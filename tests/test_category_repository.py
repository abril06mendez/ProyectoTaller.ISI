
import pytest

from myapp import create_app
from myapp.extensions import db
from myapp.models.post import Category
from myapp.persistence.category_repository import CategoryRepository


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

        yield CategoryRepository()

        db.session.remove()
        db.drop_all()


def test_save_and_find_by_name(repository):
    category = Category(0, "Bases de Datos")

    saved_category = repository.save(category)

    assert saved_category.id is not None
    assert saved_category.name == "Bases de Datos"

    found_category = repository.find_by_name("Bases de Datos")

    assert found_category is not None
    assert found_category.name == "Bases de Datos"


def test_find_by_id(repository):
    saved_category = repository.save(Category(0, "Python"))

    found_category = repository.find_by_id(saved_category.id)

    assert found_category is not None
    assert found_category.name == "Python"


def test_find_all(repository):
    repository.save(Category(0, "Python"))
    repository.save(Category(0, "Java"))

    categories = repository.find_all()

    assert len(categories) == 2


def test_exists_by_name(repository):
    repository.save(Category(0, "Bases de Datos"))

    assert repository.exists_by_name("Bases de Datos")
    assert not repository.exists_by_name("Matemática")
