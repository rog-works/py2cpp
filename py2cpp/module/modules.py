from py2cpp.lang.implementation import injectable
from py2cpp.module.module import Module
from py2cpp.module.loader import ModuleLoader
from py2cpp.module.types import LibraryPaths


class Modules:
	"""モジュールマネージャー。メインモジュールを基点として関連するインポートモジュールを管理"""

	@injectable
	def __init__(self, main: Module, loader: ModuleLoader, library_paths: LibraryPaths) -> None:
		"""インスタンスを生成

		Args:
			main (Module): メインモジュール @inject
			loader (ModuleLoader): モジュールローダー @inject
			library_paths (LibraryPaths): 標準ライブラリーパスリスト @inject
		"""
		self.__modules: dict[str, Module] = {'__main__': main}
		self.__loader = loader
		self.__library_paths = library_paths

	@property
	def main(self) -> Module:
		"""Module: メインモジュール"""
		return self.__modules['__main__']

	@property
	def libralies(self) -> list[Module]:
		"""list[Module]: 標準ライブラリーモジュールリスト"""
		return [self.load(module_path) for module_path in self.__library_paths]

	def load(self, module_path: str) -> Module:
		"""モジュールをロード。ロードしたモジュールはパスとマッピングしてキャッシュ

		Args:
			module_path (str): モジュールパス
		Returns:
			Module: モジュール
		"""
		if module_path not in self.__modules:
			self.__modules[module_path] = self.__loader(module_path)

		return self.__modules[module_path]
