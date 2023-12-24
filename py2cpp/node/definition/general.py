from py2cpp.lang.annotation import override
from py2cpp.node.definition.statement_simple import AnnoAssign, MoveAssign
from py2cpp.node.embed import Meta, accept_tags, expandable
from py2cpp.node.node import Node
from py2cpp.node.plugin import ModulePath


@Meta.embed(Node, accept_tags('file_input'))
class Module(Node):
	@property
	@override
	def scope_name(self) -> str:
		return self.module_path

	@property
	@override
	def namespace(self) -> str:
		return self.module_path

	@property
	@override
	def scope(self) -> str:
		return self.module_path

	@property
	@Meta.embed(Node, expandable)
	def statements(self) -> list[Node]:
		return self._children()

	@property
	def decl_vars(self) -> list[AnnoAssign | MoveAssign]:
		assigns = {node.one_of(AnnoAssign | MoveAssign): True for node in reversed(self.statements) if node.is_a(AnnoAssign, MoveAssign)}
		return list(reversed(assigns.keys()))

	@property
	def module_path(self) -> str:
		return self.plugin(ModulePath).name
