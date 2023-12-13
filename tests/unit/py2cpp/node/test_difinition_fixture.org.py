from py2cpp.cpp.enum import *

@deco(A, A.B)
class Hoge:
	class Values(CEnum):
		A = 0
		B = 1

	def func1(self, value: int) -> Values:
		if value == 0:
			return Hoge.Values.A
		else:
			return Hoge.Values.B

	@deco_func('hoge')
	def func2(self, text: str) -> None:
		if False:
			b

def func3(ok: bool) -> None:
	pass