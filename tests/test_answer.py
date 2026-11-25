import pytest
from myapp.models.users import User, UserType
from myapp.models.post import Answer, Category, Question, Tag


@pytest.fixture
def user():
    return User(1, "Ana", "ana@mail.com", "123456", UserType.STUDENT)


@pytest.fixture
def question(user):
    return Question(1, "Duda", "Texto", Category(1, "Python"), user)


def test_answer_starts_not_accepted(user, question):
    a = Answer("Usá un dict", user, question)
    assert a.is_accepted is False
    assert a.author is user
    assert a.question is question


def test_mark_and_unmark(user, question):
    a = Answer("Usá un dict", user, question)
    a.mark_as_accepted()
    assert a.is_accepted
    a.unmark_as_accepted()
    assert not a.is_accepted


def test_ids_are_unique(user, question):
    a1 = Answer("uno", user, question)
    a2 = Answer("dos", user, question)
    assert a1.id != a2.id


def test_empty_body_rejected(user, question):
    with pytest.raises(ValueError):
        Answer("   ", user, question)


def test_invalid_author_rejected(question):
    with pytest.raises(ValueError):
        Answer("texto", "no soy un Author", question)


def test_user_create_answer_and_add_to_question(user, question):
    a = user.create_answer(question, "Respuesta")
    question.add_answer(a)
    assert a in question.answers


def test_only_question_author_can_accept(user):
    other = User(2, "Beto", "beto@mail.com", "123456", UserType.STUDENT)
    q = Question(1, "Duda", "Texto", Category(1, "Python"), user)
    a = other.create_answer(q, "Respuesta")
    q.add_answer(a)

    with pytest.raises(PermissionError):
        q.accept_answer(a, other)

    q.accept_answer(a, user)
    assert a.is_accepted


def test_multiple_answers_can_be_accepted(user, question):
    a1 = user.create_answer(question, "uno")
    a2 = user.create_answer(question, "dos")
    question.add_answer(a1)
    question.add_answer(a2)
    question.accept_answer(a1, user)
    question.accept_answer(a2, user)
    assert a1.is_accepted
    assert a2.is_accepted

def test_question_author_can_unaccept_answer(user, question):
    a = user.create_answer(question, "Respuesta")
    question.add_answer(a)

    question.accept_answer(a, user)
    question.unaccept_answer(a, user)

    assert a.is_accepted is False
