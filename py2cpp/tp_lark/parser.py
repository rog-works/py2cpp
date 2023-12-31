import os
import json
from typing import IO, cast

from lark import Lark, Tree
from lark.indenter import PythonIndenter

from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import ParserSetting
from py2cpp.lang.cache import CacheProvider
from py2cpp.lang.implementation import implements, injectable
from py2cpp.lang.io import FileLoader
from py2cpp.tp_lark.entry import EntryOfLark, Serialization


class SyntaxParserOfLark:
	"""シンタックスパーサー(Lark版)"""

	@injectable
	def __init__(self, loader: FileLoader, setting: ParserSetting, cache: CacheProvider) -> None:
		"""インスタンスを生成

		Args:
			loader (FileLoader): ファイルローダー @inject
			setting (ParserSetting): パーサー設定データ @inject
			cache (CacheProvider): キャッシュプロバイダー @inject
		"""
		self.__loader = loader
		self.__setting = setting
		self.__cache = cache

	@implements
	def __call__(self, module_path: str) -> Entry:
		"""モジュールを解析してシンタックスツリーを生成

		Args:
			module_path (str): モジュールパス
		Returns:
			Entry: シンタックスツリーのルートエントリー
		"""
		parser = self.__load_parser()
		return self.__load_entry(parser, module_path)

	def __load_parser(self) -> Lark:
		"""シンタックスパーサーをロード

		Returns:
			Lark: シンタックスパーサー
		"""
		def identity() -> dict[str, str]:
			return {
				'mtime': str(os.path.getmtime(self.__setting.grammar)),
				'grammar': self.__setting.grammar,
				'start': self.__setting.start,
				'algorithem': self.__setting.algorithem,
			}

		@self.__cache.get('parser.cache', identity=identity())
		def instantiate() -> LarkStored:
			return LarkStored(Lark(
				self.__loader(self.__setting.grammar),
				start=self.__setting.start,
				parser=self.__setting.algorithem,
				postlex=PythonIndenter()
			))

		return instantiate().lark

	def __load_entry(self, parser: Lark, module_path: str) -> Entry:
		"""シンタックスツリーをロード

		Args:
			parser (Lark): シンタックスパーサー
			module_path (str): モジュールパス
		Returns:
			Entry: シンタックスツリーのルートエントリー
		"""
		basepath = module_path.replace('.', '/')

		def source_path() -> str:
			return f'{basepath}.py'

		def identity() -> dict[str, str]:
			return {'mtime': str(os.path.getmtime(source_path()))}

		def load_source() -> str:
			return self.__loader(source_path())

		@self.__cache.get(basepath, identity=identity(), format='json')
		def instantiate() -> EntryStored:
			return EntryStored(EntryOfLark(parser.parse(load_source())))

		return instantiate().entry

	def get_lark_dirty(self) -> Lark:
		"""Larkインスタンスを取得(デバッグ用)

		Returns:
			Lark: Larkインスタンス
		Note:
			デバッグ用途のため、基本的に使用しないことを推奨
		"""
		return self.__load_parser()


class LarkStored:
	"""ストア(Lark版)"""

	def __init__(self, lark: Lark) -> None:
		""""インスタンスを生成

		Args:
			lark (Lark): Larkインスタンス
		"""
		self.lark = lark

	@classmethod
	def load(cls, stream: IO) -> 'LarkStored':
		""""インスタンスを復元

		Args:
			stream (IO): IO
		Returns:
			LarkStored: インスタンス
		"""
		return LarkStored(Lark.load(stream))

	def save(self, stream: IO) -> None:
		""""インスタンスを保存

		Args:
			stream (IO): IO
		"""
		self.lark.save(stream)


class EntryStored:
	"""ストア(シンタックスツリー版)"""

	def __init__(self, entry: Entry) -> None:
		""""インスタンスを生成

		Args:
			lark (Lark): Larkインスタンス
		"""
		self.entry = entry

	@classmethod
	def load(cls, stream: IO) -> 'EntryStored':
		""""インスタンスを復元

		Args:
			stream (IO): IO
		Returns:
			EntryStored: インスタンス
		"""
		data = json.load(stream)
		tree = cast(Tree, Serialization.loads(data))
		return EntryStored(EntryOfLark(tree))

	def save(self, stream: IO) -> None:
		""""インスタンスを保存

		Args:
			stream (IO): IO
		"""
		data = Serialization.dumps(cast(Tree, self.entry.source))
		stream.write(json.dumps(data).encode('utf-8'))
