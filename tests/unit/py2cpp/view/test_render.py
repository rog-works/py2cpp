import os
from typing import Any
from unittest import TestCase

from py2cpp.view.render import Renderer
from tests.test.helper import data_provider

class Fixture:
	@classmethod
	def appdir(cls) -> str:
		return os.path.join(os.path.dirname(__file__), '../../../..')

	@classmethod
	def renderer(cls) -> Renderer:
		return Renderer(os.path.join(cls.appdir(), 'example/template'))


class TestRenderer(TestCase):
	@data_provider([
		('move_assign.j2', 0, {'symbol': 'hoge', 'value': '1234'}, 'hoge = 1234;'),
		('move_assign.j2', 2, {'symbol': 'hoge', 'value': '1234'}, '\t\thoge = 1234;'),
		('class.j2', 0, {
			'class_name': 'Hoge',
			'decorators': [
				{'symbol': 'deco', 'arguments': [{'value': 'A'}, {'value': 'A.B'}]}
			],
			'parents': ['Base', 'Interface'],
			'variables': [
				{'access': 'private', 'symbol': '__value', 'variable_type': 'int'},
				{'access': 'private', 'symbol': '__text', 'variable_type': 'string'},
			],
			'block': '\n'.join([
				'public: Hoge() {',
				'	int hoge = 1234;',
				'	int fuga = 2345;',
				'}',
			]),
		},
		'\n'.join([
			'deco(A, A.B)',
			'class Hoge : public Base, Interface {',
			'	private: int __value;',
			'	private: string __text;',
			'',
			'	public: Hoge() {',
			'		int hoge = 1234;',
			'		int fuga = 2345;',
			'	}',
			'};',
		])),
	])
	def test_render(self, template: str, indent: int, vars: dict[str, Any], expected: str) -> None:
		renderer = Fixture.renderer()
		actual = renderer.render(template, indent=indent, vars=vars)
		self.assertEqual(actual, expected)
