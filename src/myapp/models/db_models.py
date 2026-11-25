from __future__ import annotations

from datetime import datetime

from myapp.extensions import db
from myapp.models.post import Answer, Category, Question, Tag
from myapp.models.users import User, UserType

question_tags = db.Table(
    "question_tags",
    db.Column(
        "question_id",
        db.Integer,
        db.ForeignKey("questions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


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


class CategoryModel(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<CategoryModel {self.name}>"

    @classmethod
    def from_domain(cls, category: Category) -> CategoryModel:
        return cls(name=category.name)

    def to_domain(self) -> Category:
        return Category(category_id=self.id, name=self.name)


class TagModel(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<TagModel {self.name}>"

    @classmethod
    def from_domain(cls, tag: Tag) -> TagModel:
        return cls(name=tag.name)

    def to_domain(self) -> Tag:
        return Tag(tag_id=self.id, name=self.name)


class QuestionModel(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    author = db.relationship("UserModel", backref=db.backref("questions", lazy=True))
    category = db.relationship("CategoryModel", backref=db.backref("questions", lazy=True))
    tags = db.relationship(
        "TagModel",
        secondary=question_tags,
        backref=db.backref("questions", lazy=True),
    )
    answers = db.relationship(
        "AnswerModel",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="AnswerModel.created_at",
    )

    def __repr__(self) -> str:
        return f"<QuestionModel {self.id}: {self.title}>"

    @classmethod
    def from_domain(
        cls,
        question: Question,
        author_id: int,
        category_id: int,
        tags: list[TagModel] | None = None,
    ) -> QuestionModel:
        return cls(
            title=question.title,
            body=question.body,
            created_at=question.created_at,
            author_id=author_id,
            category_id=category_id,
            tags=tags or [],
        )

    def to_domain(self) -> Question:
        author_domain = self.author.to_domain()
        category_domain = self.category.to_domain()
        tags_domain = [tag.to_domain() for tag in self.tags]

        question_domain = Question(
            post_id=self.id,
            title=self.title,
            body=self.body,
            category=category_domain,
            author=author_domain,
            tags=tags_domain,
        )
        question_domain._created_at = self.created_at

        for ans_model in self.answers:
            ans_domain = ans_model.to_domain(
                question=question_domain,
                question_author=author_domain,
            )
            question_domain.add_answer(ans_domain)

        return question_domain


class AnswerModel(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_accepted = db.Column(db.Boolean, nullable=False, default=False)
    is_ai_generated = db.Column(db.Boolean, nullable=False, default=False)
    ai_agent_name = db.Column(db.String(100), nullable=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    question = db.relationship("QuestionModel", back_populates="answers")
    author = db.relationship("UserModel", backref=db.backref("answers", lazy=True))

    def __repr__(self) -> str:
        return f"<AnswerModel {self.id} (question={self.question_id})>"

    @classmethod
    def from_domain(
        cls,
        answer: Answer,
        question_id: int,
        author_id: int | None = None,
        is_ai_generated: bool = False,
        ai_agent_name: str | None = None,
    ) -> AnswerModel:
        return cls(
            body=answer.body,
            created_at=answer.created_at,
            is_accepted=answer.is_accepted,
            is_ai_generated=is_ai_generated,
            ai_agent_name=ai_agent_name,
            question_id=question_id,
            author_id=author_id,
        )

    def to_domain(
        self,
        question: Question,
        question_author: User | None = None,
    ) -> Answer:
        if self.is_ai_generated:
            from myapp.services.ai_agent import AIAgent, AIStrategy

            class _PersistedStrategy(AIStrategy):
                def generate_answer(self, q: Question) -> str:
                    return ""

            author_domain = AIAgent(
                agent_id=0,
                name=self.ai_agent_name or "Asistente IA",
                strategy=_PersistedStrategy(),
            )
        elif question_author is not None and self.author_id == question_author.id:
            author_domain = question_author
        else:
            author_domain = self.author.to_domain()

        answer_domain = Answer(
            body=self.body,
            author=author_domain,
            question=question,
        )
        answer_domain._id = self.id
        answer_domain._created_at = self.created_at
        if self.is_accepted:
            answer_domain.mark_as_accepted()

        return answer_domain