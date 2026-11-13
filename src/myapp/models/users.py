import hashlib
import re
from abc import ABC, abstractmethod
from enum import Enum

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
		#firma para el issue #3
		pass

class UserManager:
	def __init__(self):
		self._users: dict[str, User] = {}

	def register(self, name: str, email: str, password: str, role: UserType) ->User:
		if not email or not email.strip():
			raise ValueError("El email no puede estar vacío")

		normalized_email = email.strip().lower()

		if normalized_email in self._users:
			raise ValueError(f"El email '{normalized_email}' ya se encuentra registrado.")

		next_id = len(self._users)+1
		new_user = User(next_id, name, normalized_email, password, role)
		self._users[normalized_email] = new_user
		return new_user

	def authenticate(self, email: str, password: str) -> User | None:
		normalized_email = email.strip().lower()
		user = self._users.get(normalized_email)

		if user and user.authenticate(password):
			return user
		return None

	@property
	def users(self) -> list[User]:
		return list(self._users.values())