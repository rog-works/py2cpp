from abc import ABCMeta, abstractmethod
import re
from typing import Callable, Generic, TypeVar

T = TypeVar('T')


class EntryProxy(Generic[T], metaclass=ABCMeta):
	"""エントリーへの要素アクセスを代替するプロクシー"""

	@abstractmethod
	def name(self, entry: T) -> str:
		"""名前を取得

		Args:
			entry (T): エントリー
		Returns:
			str: エントリーの名前
		Note:
			エントリーが空の場合を考慮すること
			@see is_empty
		"""
		raise NotImplementedError()


	@abstractmethod
	def has_child(self, entry: T) -> bool:
		"""子を持つエントリーか判定

		Args:
			entry (T): エントリー
		Returns:
			bool: True = 子を持つエントリー
		"""
		raise NotImplementedError()


	@abstractmethod
	def children(self, entry: T) -> list[T]:
		"""配下のエントリーを取得

		Args:
			entry (T): エントリー
		Returns:
			list[T]: 配下のエントリーリスト
		Raise:
			ValueError: 子を持たないエントリーで使用
		"""
		raise NotImplementedError()


	@abstractmethod
	def is_terminal(self, entry: T) -> bool:
		"""終端記号か判定

		Args:
			entry (T): エントリー
		Returns:
			bool: True = 終端記号
		"""
		raise NotImplementedError()


	@abstractmethod
	def value(self, entry: T) -> str:
		"""終端記号の値を取得

		Args:
			entry (T): エントリー
		Returns:
			str: 終端記号の値
		Raise:
			ValueError: 終端記号ではないエントリーで使用
		"""
		raise NotImplementedError()


	@abstractmethod
	def is_empty(self, entry: T) -> bool:
		"""エントリーが空か判定

		Returns:
			bool: True = 空
		Note:
			Grammarの定義上存在するが、構文解析の結果で空になったエントリー
			例えば以下の様な関数の定義の場合[parameters]が対象となり、引数がない関数の場合、エントリーとしては存在するが内容は空になる
			例) function_def: "def" name "(" [parameters] ")" "->" ":" block
		"""
		raise NotImplementedError()


	@property
	def empty_name(self) -> str:
		"""str: 空のエントリー名"""
		return '__empty__'


class ASTFinder(Generic[T]):
	"""AST探索インターフェイス"""

	def __init__(self, proxy: EntryProxy[T]) -> None:
		"""インスタンスを生成

		Args:
			proxy (EntryProxy): エントリープロクシー
		"""
		self.__proxy = proxy


	@classmethod
	def normalize_tag(cls, entry_tag: str, index: int) -> str:
		"""タグ名にインデックスを付与

		Args:
			entry_tag (str): エントリータグ名
			index (int): インデックス
		Returns:
			str: 付与後のエントリータグ名
		Note:
			書式: ${entry_tag}[${index}]
		"""
		return f'{entry_tag}[{index}]'


	@classmethod
	def denormalize_tag(cls, entry_tag: str) -> str:
		"""タグ名に付与されたインデックスを除外

		Args:
			entry_tag (str): エントリータグ名
		Returns:
			str: 元のエントリータグ名
		"""
		return cls.break_tag(entry_tag)[0]


	@classmethod
	def break_tag(cls, entry_tag: str) -> tuple[str, int]:
		"""タグ名から元のタグ名と付与されたインデックスに分解。インデックスがない場合は-1とする

		Args:
			entry_tag (str): エントリータグ名
		Returns:
			tuple[str, int]: (エントリータグ名, インデックス)
		"""
		matches = re.fullmatch(r'(\w+)\[(\d+)\]', entry_tag)
		return (matches[1], int(matches[2])) if matches else (entry_tag, -1)


	@classmethod
	def escaped_path(cls, path: str) -> str:
		"""パスを正規表現用にエスケープ

		Args:
			pash (str): パス
		Returns:
			str: エスケープ後のパス
		"""
		return re.sub(r'([.\[\]])', r'\\\1', path)


	@classmethod
	def __without_root_path(cls, full_path: str) -> str:
		"""フルパスからルート要素を除外した相対パスに変換

		Args:
			full_path (str): フルパス
		Returns:
			str: ルート要素からの相対パス
		"""
		return '.'.join(full_path.split('.')[1:])


	def has_child(self, entry: T) -> bool:
		"""子を持つエントリーか判定

		Args:
			entry (T): エントリー
		Returns:
			bool: True = 子を持つエントリー
		"""
		return self.__proxy.has_child(entry)


	def tag_by(self, entry: T) -> str:
		"""エントリーのタグ名を取得

		Args:
			entry (Entry): エントリー
		Returns:
			str: タグ名
		"""
		return self.__proxy.name(entry)


	def exists(self, root: T, full_path: str) -> bool:
		"""指定のパスに一致するエントリーが存在するか判定

		Args:
			root (Entry): ルートエントリー
			full_path (str): フルパス
		Returns:
			bool: True = 存在
		"""
		try:
			self.pluck(root, full_path)
			return True
		except ValueError:
			return False


	def pluck(self, root: T, full_path: str) -> T:
		"""指定のパスに一致するエントリーを抜き出す

		Args:
			root (Entry): ルートエントリー
			full_path (str): 抜き出すエントリーのフルパス
		Returns:
			Entry: エントリー
		Raise:
			ValueError: エントリーが存在しない
		"""
		if self.tag_by(root) == full_path:
			return root

		return self.__pluck(root, self.__without_root_path(full_path))


	def __pluck(self, entry: T, path: str) -> T:
		"""配下のエントリーから指定のパスに一致するエントリーを抜き出す

		Args:
			entry (Entry): エントリー
			path (str): 引数のエントリーからの相対パス
		Returns:
			Entry: エントリー
		Note:
			@see pluck
		Raise:
			ValueError: エントリーが存在しない
		"""
		if self.__proxy.has_child(entry) and path:
			org_tag, *remain = path.split('.')
			tag, index = self.break_tag(org_tag)
			# @see break_tag, full_pathfy
			if index != -1:
				children = self.__proxy.children(entry)
				if index >= 0 and index < len(children):
					return self.__pluck(children[index], '.'.join(remain))
			else:
				children = self.__proxy.children(entry)
				in_entries = [in_entry for in_entry in children if tag == self.tag_by(in_entry)]
				if len(in_entries):
					return self.__pluck(in_entries.pop(), '.'.join(remain))
		elif not path:
			return entry

		raise ValueError()


	def find(self, root: T, via: str, tester: Callable[[T, str], bool], depth: int = -1) -> dict[str, T]:
		"""基点のパス以下のエントリーを検索

		Args:
			root (Entry): ルートエントリー
			via (str): 探索基点のフルパス
			tester (Callable[[T, str], bool]): 検索条件
			depth (int): 探索深度(-1: 無制限)
		Returns:
			dict[str, Entry]: フルパスとエントリーのマップ
		"""
		entry = self.pluck(root, via)
		all = self.full_pathfy(entry, via, depth)
		return {in_path: in_entry for in_path, in_entry in all.items() if tester(in_entry, in_path)}


	def full_pathfy(self, entry: T, path: str = '', depth: int = -1) -> dict[str, T]:
		"""指定のエントリー以下のフルパスとマッピングを生成

		Args:
			entry (entry): エントリー
			path (str): 引数のエントリーのフルパス
			depth (int): 探索深度(-1: 無制限)
		Returns:
			dict[str, Entry]: フルパスとエントリーのマップ
		Note:
			引数のpathには必ずルート要素からのフルパスを指定すること
			相対パスを指定してこの関数を実行すると、本来のフルパスとの整合性が取れなくなる点に注意
			例)
				フルパス時: tree_a.tree_b[1].token
				相対パス時: tree_b.token ※1
				※1 相対の場合、tree_bを基点とすると、インデックスの情報が欠損するため結果が変わる
		"""
		# XXX パスが無い時点はルート要素と見做してパスを設定する
		if not len(path):
			path = self.tag_by(entry)

		in_paths = {path: entry}
		if depth == 0:
			return in_paths

		if self.__proxy.has_child(entry):
			children = self.__proxy.children(entry)
			tag_of_indexs = self.__aligned_children(children)
			for index, in_entry in enumerate(children):
				# XXX 同名の要素が並ぶか否かでパスの書式を変更
				# XXX n == 1: {path}.{tag}
				# XXX n >= 2: {path}.{tag}[{index}]
				# XXX @see normalize_tag, pluck
				entry_tag = self.tag_by(in_entry)
				indivisual = len(tag_of_indexs[entry_tag]) == 1
				in_path = f'{path}.{entry_tag}' if indivisual else f'{path}.{self.normalize_tag(entry_tag, index)}'
				in_paths = {**in_paths, **self.full_pathfy(children[index], in_path, depth - 1)}

		return in_paths


	def __aligned_children(self, children: list[T]) -> dict[str, list[int]]:
		"""子の要素を元にタグ名毎のインデックスリストに整理する

		Args:
			children (list[Entry]): 子の要素リスト
		Returns:
			dict[str, list[int]]: タグ名毎のインデックスリスト
		"""
		index_of_tags = {index: self.tag_by(in_entry) for index, in_entry in enumerate(children)}
		tag_of_indexs: dict[str, list[int]]  = {tag: [] for tag in index_of_tags.values()}
		for tag in tag_of_indexs.keys():
			tag_of_indexs[tag] = [index for index, in_tag in index_of_tags.items() if tag == in_tag]

		return tag_of_indexs