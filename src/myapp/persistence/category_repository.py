
from myapp.extensions import db
from myapp.models.db_models import CategoryModel
from myapp.models.post import Category


class CategoryRepository:

    def save(self, category: Category) -> Category:
        category_model = CategoryModel.from_domain(category)

        try:
            db.session.add(category_model)
            db.session.commit()
            return category_model.to_domain()

        except Exception:
            db.session.rollback()
            raise

    def find_by_id(self, category_id: int) -> Category | None:
        category_model = db.session.get(CategoryModel, category_id)

        if category_model is None:
            return None

        return category_model.to_domain()

    def find_by_name(self, name: str) -> Category | None:
        normalized_name = name.strip()

        category_model = CategoryModel.query.filter_by(
            name=normalized_name
        ).first()

        if category_model is None:
            return None

        return category_model.to_domain()

    def find_all(self) -> list[Category]:
        category_models = CategoryModel.query.order_by(
            CategoryModel.id
        ).all()

        return [
            category_model.to_domain()
            for category_model in category_models
        ]

    def exists_by_name(self, name: str) -> bool:
        normalized_name = name.strip()

        return CategoryModel.query.filter_by(
            name=normalized_name
        ).first() is not None
