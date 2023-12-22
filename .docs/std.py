from typing import Any, Iterator, TypeAlias, TypeVar

T_Num = TypeVar('T_Num', int, float)
T_Iter: TypeAlias = Iterator
T_Any: TypeAlias = Any


@alias('int')
class Integer:
	def __init__(self, number: T_Num) -> None: ...


@alias('float')
class Float:
	def __init__(self, number: T_Num) -> None: ...


@alias('str')
class String:
	def split(self, delimiter: 'String') -> list['String']: ...
	def join(self, iterable: T_Iter) -> 'String': ...
	def replace(self, subject: 'String', replaced: 'String') -> 'String': ...
	def find(self, subject: 'String') -> Integer: ...


@alias('bool')
class Boolean: ...


@alias('tuple')
class Tuple: ...


@alias('list')
class List:
	def __init__(self, iterable: T_Iter) -> None: ...
	def append(self, elem: T_Any) -> None: ...
	def insert(self, index: Integer, elem: T_Any) -> None: ...
	def pop(self, index: Integer = Integer(-1)) -> T_Any: ...
	def reverse(self) -> None: ...


@alias('dict')
class Dict:
	def __init__(self, iterable: T_Iter) -> None: ...
	def keys(self) -> List: ...
	def values(self) -> List: ...
	def items(self) -> List: ...


@alias('None')
class Null: ...
