
from myapp.extensions import db
from myapp.models.db_models import TagModel
from myapp.models.post import Tag


class TagRepository:

    def save(self, tag: Tag) -> Tag:
        tag_model = TagModel.from_domain(tag)

        try:
            db.session.add(tag_model)
            db.session.commit()
            return tag_model.to_domain()

        except Exception:
            db.session.rollback()
            raise

    def find_by_id(self, tag_id: int) -> Tag | None:
        tag_model = db.session.get(TagModel, tag_id)

        if tag_model is None:
            return None

        return tag_model.to_domain()

    def find_by_name(self, name: str) -> Tag | None:
        normalized_name = name.strip()

        tag_model = TagModel.query.filter_by(
            name=normalized_name
        ).first()

        if tag_model is None:
            return None

        return tag_model.to_domain()

    def find_all(self) -> list[Tag]:
        tag_models = TagModel.query.order_by(
            TagModel.id
        ).all()

        return [
            tag_model.to_domain()
            for tag_model in tag_models
        ]

    def exists_by_name(self, name: str) -> bool:
        normalized_name = name.strip()

        return TagModel.query.filter_by(
            name=normalized_name
        ).first() is not None
