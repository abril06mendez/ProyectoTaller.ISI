
import pytest

from myapp import create_app
from myapp.extensions import db
from myapp.models.post import Answer, Category, Question
from myapp.models.users import User, UserType
from myapp.persistence.user_repository import UserRepository
from myapp.persistence.category_repository import CategoryRepository
from myapp.persistence.question_repository import QuestionRepository
from myapp.persistence.answer_repository import AnswerRepository
from myapp.models.db_models import AnswerModel
from myapp.services.ai_agent import AIAgent, AIStrategy

class DummyAIStrategy(AIStrategy):

    def generate_answer(self, question: Question) -> str:
        return "Respuesta generada por IA."


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
        question_repository = QuestionRepository()

        question_author = user_repository.save(
            User(0, "Ana", "ana@mail.com", "123456", UserType.STUDENT)
        )

        answer_author = user_repository.save(
            User(0, "Beto", "beto@mail.com", "123456", UserType.STUDENT)
        )

        category = category_repository.save(
            Category(0, "Python")
        )

        question = question_repository.save(
            Question(
                0,
                "Duda con Python",
                "Como funcionan las listas?",
                category,
                question_author,
            )
        )

        yield (
            AnswerRepository(),
            question,
            question_author,
            answer_author,
        )

        db.session.remove()
        db.drop_all()


def test_save_and_find_by_id(repository):
    repo, question, question_author, answer_author = repository

    answer = Answer(
        "Las listas almacenan elementos.",
        answer_author,
        question,
    )

    saved_answer = repo.save(answer)

    assert saved_answer.id is not None
    assert saved_answer.body == "Las listas almacenan elementos."
    assert saved_answer.author.id == answer_author.id
    assert saved_answer.question.id == question.id

    found_answer = repo.find_by_id(saved_answer.id)

    assert found_answer is not None
    assert found_answer.body == saved_answer.body
    assert found_answer.author.id == answer_author.id
    assert found_answer.question.id == question.id


def test_find_all(repository):
    repo, question, question_author, answer_author = repository

    repo.save(Answer("Respuesta 1", answer_author, question))
    repo.save(Answer("Respuesta 2", answer_author, question))

    answers = repo.find_all()

    assert len(answers) == 2


def test_find_by_question_id(repository):
    repo, question, question_author, answer_author = repository

    repo.save(Answer("Respuesta 1", answer_author, question))
    repo.save(Answer("Respuesta 2", answer_author, question))

    answers = repo.find_by_question_id(question.id)

    assert len(answers) == 2
    assert all(a.question.id == question.id for a in answers)


def test_find_by_author_id(repository):
    repo, question, question_author, answer_author = repository

    repo.save(Answer("Respuesta de Beto", answer_author, question))

    answers = repo.find_by_author_id(answer_author.id)

    assert len(answers) == 1
    assert answers[0].author.id == answer_author.id


def test_delete(repository):
    repo, question, question_author, answer_author = repository

    answer = repo.save(
        Answer("Respuesta para eliminar", answer_author, question)
    )

    assert repo.delete(answer.id) is True
    assert repo.find_by_id(answer.id) is None


def test_delete_nonexistent_answer(repository):
    repo, question, question_author, answer_author = repository

    assert repo.delete(999) is False


def test_save_preserves_accepted_status(repository):
    repo, question, question_author, answer_author = repository

    answer = Answer("Respuesta aceptada", answer_author, question)
    answer.mark_as_accepted()

    saved_answer = repo.save(answer)

    assert saved_answer.is_accepted is True

    found_answer = repo.find_by_id(saved_answer.id)

    assert found_answer.is_accepted is True


def test_save_rejects_nonexistent_question(repository):
    repo, question, question_author, answer_author = repository

    nonexistent_question = Question(
        999,
        "Pregunta inexistente",
        "Contenido",
        question.category,
        question_author,
    )

    answer = Answer(
        "Respuesta",
        answer_author,
        nonexistent_question,
    )

    with pytest.raises(ValueError):
        repo.save(answer)


def test_save_rejects_nonexistent_author(repository):
    repo, question, question_author, answer_author = repository

    nonexistent_author = User(
        999,
        "Carlos",
        "carlos@mail.com",
        "123456",
        UserType.STUDENT,
    )

    answer = Answer(
        "Respuesta",
        nonexistent_author,
        question,
    )

    with pytest.raises(ValueError):
        repo.save(answer)


def test_find_by_id_returns_none_when_missing(repository):
    repo, question, question_author, answer_author = repository

    assert repo.find_by_id(999) is None

def test_save_ai_generated_answer(repository):
    repo, question, question_author, answer_author = repository

    agent = AIAgent(
        agent_id=0,
        name="Asistente IA",
        strategy=DummyAIStrategy(),
    )

    answer = agent.create_answer(
        question,
        "Respuesta generada por IA.",
    )

    saved_answer = repo.save(answer)

    assert saved_answer.id is not None
    assert saved_answer.body == "Respuesta generada por IA."
    assert isinstance(saved_answer.author, AIAgent)
    assert saved_answer.author.name == "Asistente IA"

    answer_model = db.session.get(
        AnswerModel,
        saved_answer.id,
    )

    assert answer_model.is_ai_generated is True
    assert answer_model.ai_agent_name == "Asistente IA"
    assert answer_model.author_id is None

