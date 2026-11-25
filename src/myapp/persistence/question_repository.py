
from myapp.extensions import db
from myapp.models.db_models import (
    QuestionModel,
    UserModel,
    CategoryModel,
    TagModel,
)
from myapp.models.post import Question


class QuestionRepository:

    def save(self, question: Question) -> Question:
        try:
            author_model = db.session.get(
                UserModel,
                question.author.id
            )

            if author_model is None:
                raise ValueError("El autor no existe en la base de datos.")

            category_model = db.session.get(
                CategoryModel,
                question.category.id
            )

            if category_model is None:
                raise ValueError("La categoría no existe en la base de datos.")

            tag_models = []

            for tag in question.tags:
                tag_model = db.session.get(TagModel, tag.id)

                if tag_model is None:
                    raise ValueError(
                        f"La etiqueta '{tag.name}' no existe en la base de datos."
                    )

                tag_models.append(tag_model)

            question_model = QuestionModel.from_domain(
                question,
                author_id=author_model.id,
                category_id=category_model.id,
                tags=tag_models,
            )

            db.session.add(question_model)
            db.session.commit()

            return question_model.to_domain()

        except Exception:
            db.session.rollback()
            raise

    def find_by_id(self, question_id: int) -> Question | None:
        question_model = db.session.get(
            QuestionModel,
            question_id
        )

        if question_model is None:
            return None

        return question_model.to_domain()

    def find_all(self) -> list[Question]:
        question_models = QuestionModel.query.order_by(
            QuestionModel.id
        ).all()

        return [
            question_model.to_domain()
            for question_model in question_models
        ]

    def find_by_author_id(self, author_id: int) -> list[Question]:
        question_models = QuestionModel.query.filter_by(
            author_id=author_id
        ).order_by(QuestionModel.id).all()

        return [
            question_model.to_domain()
            for question_model in question_models
        ]

    def find_by_category_id(self, category_id: int) -> list[Question]:
        question_models = QuestionModel.query.filter_by(
            category_id=category_id
        ).order_by(QuestionModel.id).all()

        return [
            question_model.to_domain()
            for question_model in question_models
        ]

    def delete(self, question_id: int) -> bool:
        question_model = db.session.get(
            QuestionModel,
            question_id
        )

        if question_model is None:
            return False

        try:
            db.session.delete(question_model)
            db.session.commit()
            return True

        except Exception:
            db.session.rollback()
            raise
