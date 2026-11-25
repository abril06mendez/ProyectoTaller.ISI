import pytest

from myapp import create_app
from myapp.extensions import db
from myapp.models.db_models import (
    AnswerModel,
    CategoryModel,
    QuestionModel,
    TagModel,
    UserModel,
)
from myapp.models.post import Category, Question, Tag
from myapp.models.users import User, UserType


class _TestDBConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret"


@pytest.fixture
def app_ctx():
    app = create_app(_TestDBConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_persist_question_with_category_tags_and_answers(app_ctx):
    user_domain = User(0, "Tomas", "tomas@mail.com", "123456", UserType.STUDENT)
    user_db = UserModel.from_domain(user_domain)

    cat_db = CategoryModel.from_domain(Category(0, "Bases de Datos"))
    tag_sql = TagModel.from_domain(Tag(0, "sqlite"))
    tag_alembic = TagModel.from_domain(Tag(0, "alembic"))

    db.session.add_all([user_db, cat_db, tag_sql, tag_alembic])
    db.session.commit()

    q_domain = Question(
        post_id=0,
        title="Duda con migraciones",
        body="¿Cómo aplico una revisión en Alembic?",
        category=cat_db.to_domain(),
        author=user_db.to_domain(),
        tags=[tag_sql.to_domain(), tag_alembic.to_domain()],
    )
    q_db = QuestionModel.from_domain(
        q_domain,
        author_id=user_db.id,
        category_id=cat_db.id,
        tags=[tag_sql, tag_alembic],
    )
    db.session.add(q_db)
    db.session.commit()

    ans_db = AnswerModel(
        body="Usá alembic upgrade head.",
        is_accepted=True,
        question_id=q_db.id,
        author_id=user_db.id,
    )
    db.session.add(ans_db)
    db.session.commit()

    loaded_q = db.session.get(QuestionModel, q_db.id).to_domain()
    assert loaded_q.title == "Duda con migraciones"
    assert loaded_q.category.name == "Bases de Datos"
    assert {t.name for t in loaded_q.tags} == {"sqlite", "alembic"}
    assert len(loaded_q.answers) == 1
    assert loaded_q.answers[0].is_accepted is True


def test_persist_ai_generated_answer(app_ctx):
    user_db = UserModel.from_domain(
        User(0, "Ana", "ana@mail.com", "123456", UserType.TEACHER)
    )
    cat_db = CategoryModel(name="Python")
    db.session.add_all([user_db, cat_db])
    db.session.commit()

    q_db = QuestionModel(
        title="Consulta IA",
        body="Explicame SQLAlchemy",
        author_id=user_db.id,
        category_id=cat_db.id,
    )
    db.session.add(q_db)
    db.session.commit()

    ai_ans_db = AnswerModel(
        body="SQLAlchemy es un ORM para Python.",
        is_ai_generated=True,
        ai_agent_name="Asistente IA",
        question_id=q_db.id,
        author_id=None,
    )
    db.session.add(ai_ans_db)
    db.session.commit()

    loaded_q = db.session.get(QuestionModel, q_db.id).to_domain()
    assert len(loaded_q.answers) == 1
    assert loaded_q.answers[0].author.name == "Asistente IA"