from abc import ABC
from datetime import datetime
from myapp.models.post import Answer
from myapp.models.users import Author
from itertools import count

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

	@property
	def answers(self) -> list:
		return list(self._answers)

	def add_answer(self, answer: Answer) -> None:
		if not isinstance(answer, Answer):
			raise ValueError("El elemento debe ser una instancia válida de Answer")

		if answer.question is not self:
			raise ValueError("La respuesta pertenece a otra pregunta.")

		if answer not in self._answers:
			self._answers.append(answer)

class Answer(Post):
    _id_counter = count(1)  # compartido por todas las respuestas

    def __init__(self, body: str, author: Author, question: Question):
        super().__init__(next(Answer._id_counter), body, author)
        self._question = question
        self._is_accepted = False

    @property
    def question(self) -> Question:
        return self._question

    @property
    def is_accepted(self) -> bool:
        return self._is_accepted

    def mark_as_accepted(self) -> None:
        self._is_accepted = True

    def unmark_as_accepted(self) -> None:
        self._is_accepted = False

    def __repr__(self) -> str:
        status = "accepted" if self._is_accepted else "pending"
        return f"Answer(id={self.id}, author={self.author.name}, {status})"