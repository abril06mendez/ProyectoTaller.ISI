from abc import ABC
from datetime import datetime
from users import Author

class Category:
	def __init__(self, category_id: int, name: str):
		if not name or not name.strip():
			raise ValueError("El nombre de la categoria no puede estar vacío.")

		self.id = category_id
		self.name = name.strip()

class Tag:
	def __init__(self, tag_id: int, name: str):
		if not name or not name.strip():
			raise ValueError("El nombre de la etiqueta no puede estar vacío.")

		self.id = tag_id
		self.name = name.strip()

class Post(ABC):
	def __init__(self, post_id: int, body: str, author: Author):
		if not body.strip():
			raise ValueError("El cuerpo de la publicacion no puede estar en blanco.")

		if not isinstance(author,Author):
			raise ValueError("El autor debe ser una instancia válida de Author.")

		self._id = post_id
		self._body = body.strip()
		self._author = author
		self._created_at = datetime.now()

	@property
	def id(self) -> int:
		return self._id

	@property
	def body(self) -> str:
		return self._body
	
	@property
	def author(self) -> Author:
		return self._author

	@property
	def created_at(self) -> datetime:
		return self._created_at
	
class Question(Post):
	def __init__(self, post_id: int, title: str, body: str, category: Category, author: Author, tags: list[Tag] = None):
		if not title or not title.strip():
			raise ValueError("El titulo de la pregunta no puede estar vacío.")

		if not isinstance(category, Category):
			raise ValueError("La pregunta debe tener una categoria válida.")

		super().__init__(post_id, body, author)

		self._title = title.strip()
		self._category = category
		self._tags = []
		self._answers = []

		if tags:
			for tag in tags:
				self.add_tag(tag)

	@property
	def title(self) -> str:
		return self._title
	
	@property
	def category(self) -> Category:
		return self._category
	
	@property
	def tags(self) -> list[Tag]:
		return list(self._tags)

	def add_tag(self, tag: Tag):
		if not isinstance(tag, Tag):
			raise ValueError("El elemento debe ser una instancia valida de Tag")
		if tag not in self._tags:
			self._tags.append(tag)

	def has_tag(self, tag_name: str) -> bool:
		return any(tag.name.lower() == tag_name.strip().lower() for tag in self._tags)