import hashlib
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from myapp.persistence.user_repository import UserRepository

class UserType(Enum):
	STUDENT = "estudiante"
	TEACHER = "docente"

class Author(ABC):
	def __init__(self, author_id: int, name: str):
		if not name or not name.strip():
			raise ValueError("El nombre del autor no puede estar vacio.")

		self._id = author_id
		self._name = name.strip()

	@property
	def id(self)->int:
		return self._id

	@property
	def name(self) -> str:
		return self._name

	@abstractmethod
	def create_answer(self, question, text: str):
		pass

class User(Author):
	def  __init__(self, user_id: int, name:str, email: str, password: str, role: UserType):
		super().__init__(user_id, name)

		if not self._is_valid_email(email):
				raise ValueError("El formato del mail no es valido")

		if not password or len(password)<6:
				raise ValueError("La contraseña debe tener al menos 6 caracteres")

		if not isinstance(role,UserType):
				raise ValueError("El rol debe ser una instancia valida de UserType")

		self._email = email.strip().lower()
		self._password_hash = self._hash_password(password)
		self._role = role
		
	@property
	def email(self) -> str:
		return self._email
		
	@property
	def role(self) -> UserType:
		return self._role
		
	def _is_valid_email(self, email: str) -> bool:
		pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
		return re.match(pattern, email.strip()) is not None

	def _hash_password(self, password: str) -> str:
		return hashlib.sha256(password.encode("utf-8")).hexdigest()

	def authenticate(self, password: str) -> bool:
		return self._password_hash == self._hash_password(password)

	def create_answer(self, question, text: str):
		from myapp.models.post import Answer
		return Answer(text, self, question)


class UserManager:
    def __init__(self, user_repository=None):
        if user_repository is None:
            from myapp.persistence.user_repository import UserRepository
            user_repository = UserRepository()

        self._user_repository = user_repository

    def register(
        self,
        name: str,
        email: str,
        password: str,
        role: UserType
    ) -> User:
        if not email or not email.strip():
            raise ValueError("El email no puede estar vacío")

        normalized_email = email.strip().lower()

        if self._user_repository.exists_by_email(normalized_email):
            raise ValueError(
                f"El email '{normalized_email}' ya se encuentra registrado."
            )

        new_user = User(0, name, normalized_email, password, role)

        return self._user_repository.save(new_user)

    def authenticate(self, email: str, password: str) -> User | None:
        if not email or not email.strip():
            return None

        normalized_email = email.strip().lower()
        user = self._user_repository.find_by_email(normalized_email)

        if user and user.authenticate(password):
            return user

        return None

    @property
    def users(self) -> list[User]:
        return self._user_repository.find_all()
