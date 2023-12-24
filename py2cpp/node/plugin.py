from dataclasses import dataclass
from typing import TypeVar, cast

from py2cpp.ast.parser import SyntaxParser
from py2cpp.ast.provider import Query
from py2cpp.lang.di import DI
from py2cpp.lang.locator import Locator
from py2cpp.node.base import Plugin
from py2cpp.node.node import Node
from py2cpp.tp_lark.types import Entry

T = TypeVar('T', bound=Node)

@dataclass
class ModulePath(Plugin):
	name: str

	@classmethod
	def entrypoint(cls) -> 'ModulePath':
		return cls('__main__')


class ModuleLoader(Plugin):
	def __init__(self, locator: Locator, parser: SyntaxParser):
		self.__locator = locator
		self.__parser = parser

	def load(self, module_path: str, expect: type[T]) -> T:
		root = self.__parser.parse(module_path)

		di = cast(DI, self.__locator).clone()
		di.unregister(Entry)
		di.unregister(ModulePath)
		di.register(Entry, lambda: root)
		di.register(ModulePath, lambda: ModulePath(module_path))

		nodes = di.resolve(Query[Node])
		return cast(expect, nodes.by('file_input'))  # XXX ダウンキャストと見做されて警告されるのでcastで対処
