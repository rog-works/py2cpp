class DSN:
	"""AST用のドメイン名ユーティリティー。ドット区切りで要素を結合した書式を前提とする"""

	@classmethod
	def elem_counts(cls, origin: str) -> int:
		"""ドメイン名内の要素数を取得

		Args:
			origin (str): ドメイン名
		Returns:
			int: 要素数
		"""
		return len(cls.elements(origin))

	@classmethod
	def elements(cls, origin: str) -> list[str]:
		"""ドメイン名を要素に分解

		Args:
			origin (str): ドメイン名
		Returns:
			list[str]: 要素リスト
		"""
		return [elem for elem in origin.split('.') if elem]

	@classmethod
	def join(cls, *prats: str) -> str:
		"""ドメイン名の要素を結合。空の要素は除外される

		Args:
			*parts (str): 要素リスト
		Returns:
			str: ドメイン名
		"""
		return '.'.join([*[part for part in prats if part]])

	@classmethod
	def left(cls, origin: str, counts: int) -> str:
		"""左から指定の数だけ要素を切り出してドメイン名を生成

		Args:
			origin (str): ドメイン名
			counts (int): 要素数
		Returns:
			str: ドメイン名
		"""
		return cls.join(*(cls.elements(origin)[0:counts]))

	@classmethod
	def right(cls, origin: str, counts: int) -> str:
		"""右から指定の数だけ要素を切り出してドメイン名を生成

		Args:
			origin (str): ドメイン名
			counts (int): 要素数
		Returns:
			str: ドメイン名
		"""
		return cls.join(*(cls.elements(origin)[-counts:]))

	@classmethod
	def root(cls, origin: str) -> str:
		"""ルート要素を取得

		Args:
			origin (str): ドメイン名
		Returns:
			str: ルート要素
		"""
		return cls.elements(origin)[0]

	@classmethod
	def parent(cls, origin: str) -> str:
		"""親の要素を取得

		Args:
			origin (str): ドメイン名
		Returns:
			str: 親の要素
		"""
		return cls.elements(origin)[-2]
