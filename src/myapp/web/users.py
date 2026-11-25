from flask import Blueprint, render_template

from myapp.extensions import db
from myapp.models.db_models import UserModel

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.get("/")
def index():
    users = db.session.scalars(db.select(UserModel)).all()
    return render_template("users/index.html", users=users)


@users_bp.get("/<int:user_id>")
def detail(user_id: int):
    user = db.get_or_404(UserModel, user_id)
    return render_template("users/detail.html", user=user)