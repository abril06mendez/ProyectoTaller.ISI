from myapp.extensions import db
from myapp.models.db_models import UserModel
from myapp.models.users import User


class UserRepository:

    def save(self, user: User) -> User:
        user_model = UserModel.from_domain(user)

        try:
            db.session.add(user_model)
            db.session.commit()
            return user_model.to_domain()

        except Exception:
            db.session.rollback()
            raise

    def find_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()

        user_model = UserModel.query.filter_by(
            email=normalized_email
        ).first()

        if user_model is None:
            return None

        return user_model.to_domain()

    def find_by_id(self, user_id: int) -> User | None:
        user_model = db.session.get(UserModel, user_id)

        if user_model is None:
            return None

        return user_model.to_domain()

    def find_all(self) -> list[User]:
        user_models = UserModel.query.order_by(UserModel.id).all()

        return [
            user_model.to_domain()
            for user_model in user_models
        ]

    def exists_by_email(self, email: str) -> bool:
        normalized_email = email.strip().lower()

        return UserModel.query.filter_by(
            email=normalized_email
        ).first() is not None