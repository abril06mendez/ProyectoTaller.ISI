import pytest
from myapp.models.users import User, UserType
from myapp.models.post import Answer


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