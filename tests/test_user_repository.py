
import pytest

from myapp import create_app
from myapp.extensions import db
from myapp.models.users import User, UserType
from myapp.persistence.user_repository import UserRepository


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

        yield UserRepository()

        db.session.remove()
        db.drop_all()


def test_save_and_find_by_email(repository):
    user = User(
        0, "Ana", "ANA@mail.com", "123456", UserType.STUDENT
    )

    saved_user = repository.save(user)

    assert saved_user.id is not None
    assert saved_user.email == "ana@mail.com"

    found_user = repository.find_by_email("ANA@mail.com")

    assert found_user is not None
    assert found_user.name == "Ana"
    assert found_user.email == "ana@mail.com"
    assert found_user.authenticate("123456")


def test_find_by_id(repository):
    user = User(0, "Juan", "juan@mail.com", "123456", UserType.TEACHER)

    saved_user = repository.save(user)

    found_user = repository.find_by_id(saved_user.id)

    assert found_user is not None
    assert found_user.name == "Juan"


def test_find_all(repository):
    repository.save(User(0, "Ana", "ana@mail.com", "123456", UserType.STUDENT))
    repository.save(User(0, "Juan", "juan@mail.com", "123456", UserType.TEACHER))

    users = repository.find_all()

    assert len(users) == 2


def test_exists_by_email(repository):
    repository.save(User(0, "Ana", "ana@mail.com", "123456", UserType.STUDENT))

    assert repository.exists_by_email("ANA@mail.com")
    assert not repository.exists_by_email("otro@mail.com")
