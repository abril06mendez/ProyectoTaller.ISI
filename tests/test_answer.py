import pytest
from myapp.models.users import User, UserType
from myapp.models.post import Answer, Category, Question, Tag


@pytest.fixture
def user():
	return User(1, "Ana", "ana@mail.com", "123456", UserType.STUDENT)


def test_answer_starts_not_accepted(user):
	a = Answer("Usá un dict", user)
	assert a.is_accepted is False
	assert a.author is user


def test_mark_and_unmark(user):
	a = Answer("Usá un dict", user)
	a.mark_as_accepted()
	assert a.is_accepted
	a.unmark_as_accepted()
	assert not a.is_accepted


def test_ids_are_unique(user):
	a1 = Answer("uno", user)
	a2 = Answer("dos", user)
	assert a1.id != a2.id


def test_empty_body_rejected(user):
	with pytest.raises(ValueError):
		Answer("   ", user)


def test_invalid_author_rejected():
	with pytest.raises(ValueError):
		Answer("texto", "no soy un Author")

def test_user_create_answer_and_add_to_question(user):
	q = Question(1, "Duda", "Texto", Category(1, "Python"), user)
	a = user.create_answer(q, "Respuesta")
	q.add_answer(a)
	assert a in q.answers

def test_only_question_author_can_accept(user):
	other = User(2, "Beto", "beto@mail.com", "123456", UserType.STUDENT)
	q = Question(1, "Duda", "Texto", Category(1, "Python"), user)
	a = other.create_answer(q, "Respuesta")
	q.add_answer(a)
	with pytest.raises(PermissionError):
		q.accept_answer(a, other)
	q.accept_answer(a, user)
	assert a.is_accepted

def test_only_one_accepted_answer(user):
	q = Question(1, "Duda", "Texto", Category(1, "Python"), user)
	a1, a2 = user.create_answer(q, "uno"), user.create_answer(q, "dos")
	q.add_answer(a1)
	q.add_answer(a2)
	q.accept_answer(a1, user)
	q.accept_answer(a2, user)
	assert not a1.is_accepted and a2.is_accepted