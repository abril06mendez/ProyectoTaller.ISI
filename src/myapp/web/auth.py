from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from myapp.extensions import db
from myapp.models.db_models import UserModel
from myapp.models.users import User, UserType

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        role_value = request.form.get("role", UserType.STUDENT.value)

        try:
            role = UserType(role_value)
            domain_user = User(
                user_id=0,
                name=name,
                email=email,
                password=password,
                role=role,
            )
        except ValueError as err:
            flash(str(err), "error")
            return render_template("auth/register.html")

        existing = db.session.scalar(
            db.select(UserModel).where(UserModel.email == domain_user.email)
        )
        if existing:
            flash(f"El email '{domain_user.email}' ya está registrado.", "error")
            return render_template("auth/register.html")

        new_user = UserModel.from_domain(domain_user)
        db.session.add(new_user)
        db.session.commit()

        flash("Cuenta creada correctamente. Ya podés iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user_record = db.session.scalar(
            db.select(UserModel).where(UserModel.email == email)
        )
        if user_record and user_record.to_domain().authenticate(password):
            session["user_id"] = user_record.id
            session["user_name"] = user_record.name
            session["user_role"] = user_record.role
            flash(f"Bienvenido, {user_record.name}.", "success")
            return redirect(url_for("users.index"))

        flash("Email o contraseña incorrectos.", "error")

    return render_template("auth/login.html")


@auth_bp.get("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("auth.login"))