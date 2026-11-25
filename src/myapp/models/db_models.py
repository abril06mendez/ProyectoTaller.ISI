from myapp.extensions import db
from myapp.models.users import User, UserType


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __repr__(self) -> str:
        return f"<UserModel {self.email}>"

    @classmethod
    def from_domain(cls, user: User) -> UserModel:
        return cls(
            name=user.name,
            email=user.email,
            password_hash=user._password_hash,
            role=user.role.value,
        )

    def to_domain(self) -> User:
        domain_user = User(
            user_id=self.id,
            name=self.name,
            email=self.email,
            password="placeholder_password",
            role=UserType(self.role),
        )
        domain_user._password_hash = self.password_hash
        return domain_user