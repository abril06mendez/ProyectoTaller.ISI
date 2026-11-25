
from myapp.extensions import db
from myapp.models.db_models import (
    AnswerModel,
    QuestionModel,
    UserModel,
)
from myapp.models.post import Answer, Question


class AnswerRepository:

    def save(
        self,
        answer: Answer,
        is_ai_generated: bool = False,
        ai_agent_name: str | None = None,
    ) -> Answer:
        from myapp.services.ai_agent import AIAgent

        try:
            question_model = db.session.get(
                QuestionModel,
                answer.question.id,
            )

            if question_model is None:
                raise ValueError(
                    "La pregunta a la que pertenece la respuesta no existe."
                )

            # Detectar automáticamente si el autor es un agente de IA.
            is_ai_generated = is_ai_generated or isinstance(
                answer.author,
                AIAgent,
            )

            author_id = None

            if is_ai_generated:
                ai_agent_name = ai_agent_name or answer.author.name
            else:
                author_model = db.session.get(
                    UserModel,
                    answer.author.id,
                )

                if author_model is None:
                    raise ValueError(
                        "El autor de la respuesta no existe en la base de datos."
                    )

                author_id = author_model.id

            answer_model = AnswerModel.from_domain(
                answer,
                question_id=question_model.id,
                author_id=author_id,
                is_ai_generated=is_ai_generated,
                ai_agent_name=ai_agent_name,
            )

            db.session.add(answer_model)
            db.session.commit()

            return answer_model.to_domain(
                question=question_model.to_domain(),
                question_author=question_model.author.to_domain(),
            )

        except Exception:
            db.session.rollback()
            raise

    def find_by_id(self, answer_id: int) -> Answer | None:
        answer_model = db.session.get(
            AnswerModel,
            answer_id,
        )

        if answer_model is None:
            return None

        return self._to_domain(answer_model)

    def find_all(self) -> list[Answer]:
        answer_models = AnswerModel.query.order_by(
            AnswerModel.id
        ).all()

        return [
            self._to_domain(answer_model)
            for answer_model in answer_models
        ]

    def find_by_question_id(self, question_id: int) -> list[Answer]:
        answer_models = AnswerModel.query.filter_by(
            question_id=question_id
        ).order_by(AnswerModel.id).all()

        return [
            self._to_domain(answer_model)
            for answer_model in answer_models
        ]

    def find_by_author_id(self, author_id: int) -> list[Answer]:
        answer_models = AnswerModel.query.filter_by(
            author_id=author_id
        ).order_by(AnswerModel.id).all()

        return [
            self._to_domain(answer_model)
            for answer_model in answer_models
        ]

    def delete(self, answer_id: int) -> bool:
        answer_model = db.session.get(
            AnswerModel,
            answer_id,
        )

        if answer_model is None:
            return False

        try:
            db.session.delete(answer_model)
            db.session.commit()
            return True

        except Exception:
            db.session.rollback()
            raise

    def _to_domain(self, answer_model: AnswerModel) -> Answer:
        question_model = answer_model.question

        question_author = question_model.author.to_domain()

        question = Question(
            post_id=question_model.id,
            title=question_model.title,
            body=question_model.body,
            category=question_model.category.to_domain(),
            author=question_author,
            tags=[
                tag.to_domain()
                for tag in question_model.tags
            ],
        )

        question._created_at = question_model.created_at

        return answer_model.to_domain(
            question=question,
            question_author=question_author,
        )
