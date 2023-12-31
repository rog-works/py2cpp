from typing import Callable

from py2cpp.ast.resolver import Resolver, SymbolMapping
from py2cpp.lang.locator import Currying
from py2cpp.node.node import Node


class NodeResolver:
	"""ノードリゾルバー。解決したノードとパスをマッピングして管理"""

	def __init__(self, currying: Currying, settings: SymbolMapping) -> None:
		"""インスタンスを生成

		Args:
			currying (Currying): カリー化関数
			settings (Settings): マッピング設定データ
		"""
		self.__currying = currying
		self.__resolver = Resolver[Node].load(settings)
		self.__insts: dict[str, Node] = {}

	def can_resolve(self, symbol: str) -> bool:
		"""解決出来るか確認

		Args:
			symbol (str): シンボル名
		Returns:
			bool: True = 解決できる
		"""
		return self.__resolver.can_resolve(symbol)

	def resolve(self, symbol: str, full_path: str) -> Node:
		"""ノードのインスタンスを解決

		Args:
			symbol (str): シンボル
			full_path (str): エントリーのフルパス
		Returns:
			Node: 解決したノード
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		if full_path in self.__insts:
			return self.__insts[full_path]

		ctor = self.__resolver.resolve(symbol)
		factory = self.__currying(ctor, Callable[[str], ctor])
		self.__insts[full_path] = factory(full_path).actualize()
		return self.__insts[full_path]

	def clear(self) -> None:
		"""インスタンスのマッピング情報を削除"""
		self.__insts = {}
