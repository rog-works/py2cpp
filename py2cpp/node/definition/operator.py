from py2cpp.lang.annotation import override
from py2cpp.node.embed import Meta, actualized
from py2cpp.node.node import Node
from py2cpp.node.definition.expression import Expression
from py2cpp.node.definition.terminal import Terminal


@Meta.embed(Node, actualized(via=Expression))
class UnaryOperator(Node):
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		if via._at(0).to_string() not in ['+', '-', '~']:
			return False

		return len(via._children()) == 2

	@property
	def operator(self) -> Terminal:
		return self._at(0).as_a(Terminal)

	@property
	def value(self) -> Node:
		return self._at(1).as_a(Expression).actualize()


# @Meta.embed(Node, accept_tags('group_expr'), actualized(via=Expression))
class Group(Node):  # FIXME impl トランスパイルの性質上必要だが、あると色々と邪魔になる
	@classmethod
	@override
	def match_feature(cls, via: Node) -> bool:
		return False