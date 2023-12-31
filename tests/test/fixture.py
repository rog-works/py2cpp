import os

from py2cpp.app.app import App
from py2cpp.ast.parser import SyntaxParser
from py2cpp.ast.query import Query
from py2cpp.lang.di import ModuleDefinitions
from py2cpp.lang.locator import Locator, T_Inst
from py2cpp.module.module import Module
from py2cpp.module.types import ModulePath
from py2cpp.node.node import Node
from py2cpp.tp_lark.entry import EntryOfLark
from py2cpp.tp_lark.parser import SyntaxParserOfLark


class Fixture:
	@classmethod
	def make(cls, filepath: str) -> 'Fixture':
		rel_path = filepath.split(cls.__appdir())[1]
		without_ext = rel_path.split('.')[0]
		elems =  [elem for elem in without_ext.split(os.path.sep) if elem]
		test_module_path = '.'.join(elems)
		return cls(test_module_path)

	@classmethod
	def __appdir(cls) -> str:
		return os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

	def __init__(self, test_module_path: str) -> None:
		self.__test_module_path = test_module_path
		self.__app = App(self.__definitions())

	def __definitions(self) -> ModuleDefinitions:
		return {
			'py2cpp.module.types.ModulePath': self.__module_path,
			'py2cpp.module.types.LibraryPaths': self.__library_paths,
		}

	def __module_path(self) -> ModulePath:
		elems = self.__test_module_path.split('.')
		dirpath, filename = '.'.join(elems[:-1]), elems[-1]
		fixture_module_path = '.'.join([dirpath, 'fixtures', filename])
		return ModulePath('__main__', fixture_module_path)

	def __library_paths(self) -> list[str]:
		return ['tests.unit.py2cpp.analize.fixtures.test_db_classes']

	def get(self, symbol: type[T_Inst]) -> T_Inst:
		return self.__app.resolve(symbol)

	@property
	def main(self) -> Module:
		return self.__app.resolve(Module)

	@property
	def shared_nodes(self) -> Query[Node]:
		return self.__app.resolve(Query[Node])

	def custom_nodes(self, source_code: str) -> Query[Node]:
		def syntax_parser(locator: Locator) -> SyntaxParser:
			parser = locator.invoke(SyntaxParserOfLark)
			return lambda module_path: EntryOfLark(parser.get_lark_dirty().parse(f'{source_code}\n'))

		definitions = {**self.__definitions(), **{'py2cpp.ast.parser.SyntaxParser': syntax_parser}}
		return App(definitions).resolve(Query[Node])
