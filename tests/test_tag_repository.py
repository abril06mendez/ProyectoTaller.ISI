
import pytest

from myapp import create_app
from myapp.extensions import db
from myapp.models.post import Tag
from myapp.persistence.tag_repository import TagRepository


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

        yield TagRepository()

        db.session.remove()
        db.drop_all()


def test_save_and_find_by_name(repository):
    tag = Tag(0, "Python")

    saved_tag = repository.save(tag)

    assert saved_tag.id is not None
    assert saved_tag.name == "Python"

    found_tag = repository.find_by_name("Python")

    assert found_tag is not None
    assert found_tag.name == "Python"


def test_find_by_id(repository):
    saved_tag = repository.save(Tag(0, "SQL"))

    found_tag = repository.find_by_id(saved_tag.id)

    assert found_tag is not None
    assert found_tag.name == "SQL"


def test_find_all(repository):
    repository.save(Tag(0, "Python"))
    repository.save(Tag(0, "Java"))

    tags = repository.find_all()

    assert len(tags) == 2


def test_exists_by_name(repository):
    repository.save(Tag(0, "Python"))

    assert repository.exists_by_name("Python")
    assert not repository.exists_by_name("Java")
