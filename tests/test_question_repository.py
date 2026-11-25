
import pytest

from myapp import create_app
from myapp.extensions import db
from myapp.models.post import Category, Tag, Question
from myapp.models.users import User, UserType
from myapp.persistence.user_repository import UserRepository
from myapp.persistence.category_repository import CategoryRepository
from myapp.persistence.tag_repository import TagRepository
from myapp.persistence.question_repository import QuestionRepository


class TestDBConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret"


@pytest.fixture
def repository():
    app = create_app(TestDBConfig)

    with app.app_context():
        db.create_all()

        user_repository = UserRepository()
        category_repository = CategoryRepository()
        tag_repository = TagRepository()

        author = user_repository.save(
            User(0, "Ana", "ana@mail.com", "123456", UserType.STUDENT)
        )

        category = category_repository.save(
            Category(0, "Python")
        )

        tag = tag_repository.save(
            Tag(0, "Flask")
        )

        yield QuestionRepository(), author, category, tag

        db.session.remove()
        db.drop_all()


def test_save_and_find_by_id(repository):
    repo, author, category, tag = repository

    question = Question(
        0,
        "Duda con Flask",
        "Como funcionan las rutas?",
        category,
        author,
        [tag],
    )

    saved_question = repo.save(question)

    assert saved_question.id is not None
    assert saved_question.title == "Duda con Flask"
    assert saved_question.author.name == "Ana"
    assert saved_question.category.name == "Python"
    assert saved_question.has_tag("Flask")

    found_question = repo.find_by_id(saved_question.id)

    assert found_question is not None
    assert found_question.title == "Duda con Flask"


def test_find_all(repository):
    repo, author, category, tag = repository

    repo.save(
        Question(0, "Pregunta 1", "Contenido 1", category, author, [tag])
    )

    repo.save(
        Question(0, "Pregunta 2", "Contenido 2", category, author)
    )

    questions = repo.find_all()

    assert len(questions) == 2


def test_find_by_author_id(repository):
    repo, author, category, tag = repository

    repo.save(
        Question(0, "Pregunta 1", "Contenido", category, author)
    )

    questions = repo.find_by_author_id(author.id)

    assert len(questions) == 1
    assert questions[0].author.id == author.id


def test_find_by_category_id(repository):
    repo, author, category, tag = repository

    repo.save(
        Question(0, "Pregunta", "Contenido", category, author)
    )

    questions = repo.find_by_category_id(category.id)

    assert len(questions) == 1
    assert questions[0].category.id == category.id


def test_delete(repository):
    repo, author, category, tag = repository

    question = repo.save(
        Question(0, "Pregunta", "Contenido", category, author)
    )

    assert repo.delete(question.id) is True
    assert repo.find_by_id(question.id) is None


def test_delete_nonexistent_question(repository):
    repo, author, category, tag = repository

    assert repo.delete(999) is False


def test_find_by_id_nonexistent_question(repository):
    repo, author, category, tag = repository

    assert repo.find_by_id(999) is None


def test_find_all_empty(repository):
    repo, author, category, tag = repository

    assert repo.find_all() == []


def test_find_by_author_id_without_questions(repository):
    repo, author, category, tag = repository

    assert repo.find_by_author_id(author.id) == []


def test_find_by_category_id_without_questions(repository):
    repo, author, category, tag = repository

    assert repo.find_by_category_id(category.id) == []


def test_save_with_nonexistent_author(repository):
    repo, author, category, tag = repository

    nonexistent_author = User(
        999,
        "Usuario inexistente",
        "inexistente@mail.com",
        "123456",
        UserType.STUDENT,
    )

    question = Question(
        0,
        "Pregunta",
        "Contenido",
        category,
        nonexistent_author,
    )

    with pytest.raises(ValueError, match="El autor no existe"):
        repo.save(question)


def test_save_with_nonexistent_category(repository):
    repo, author, category, tag = repository

    nonexistent_category = Category(999, "Categoría inexistente")

    question = Question(
        0,
        "Pregunta",
        "Contenido",
        nonexistent_category,
        author,
    )

    with pytest.raises(ValueError, match="categoría no existe"):
        repo.save(question)


def test_save_with_nonexistent_tag(repository):
    repo, author, category, tag = repository

    nonexistent_tag = Tag(999, "Django")

    question = Question(
        0,
        "Pregunta",
        "Contenido",
        category,
        author,
        [nonexistent_tag],
    )

    with pytest.raises(ValueError, match="no existe en la base de datos"):
        repo.save(question)
