from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from myapp.extensions import db
from myapp.models.db_models import (
    AnswerModel,
    CategoryModel,
    QuestionModel,
    TagModel,
)
from myapp.services.ai_agent import AIModelError, create_strategy

questions_bp = Blueprint("questions", __name__, url_prefix="/questions")


def _get_or_create_category(name: str) -> CategoryModel:
    clean_name = name.strip() or "General"
    category = db.session.scalar(
        db.select(CategoryModel).where(CategoryModel.name == clean_name)
    )
    if not category:
        category = CategoryModel(name=clean_name)
        db.session.add(category)
        db.session.flush()
    return category


def _get_or_create_tags(raw_tags: str) -> list[TagModel]:
    tags: list[TagModel] = []
    for item in raw_tags.split(","):
        clean = item.strip()
        if not clean:
            continue
        tag = db.session.scalar(db.select(TagModel).where(TagModel.name == clean))
        if not tag:
            tag = TagModel(name=clean)
            db.session.add(tag)
            db.session.flush()
        if tag not in tags:
            tags.append(tag)
    return tags


@questions_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_id = session.get("user_id")
        if not user_id:
            flash("Tenés que iniciar sesión para publicar una pregunta.", "error")
            return redirect(url_for("auth.login"))

        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        category_name = request.form.get("category", "General")
        raw_tags = request.form.get("tags", "")

        if not title or not body:
            flash("Completá el título y el detalle de la pregunta.", "error")
            return redirect(url_for("questions.index"))

        category = _get_or_create_category(category_name)
        tags = _get_or_create_tags(raw_tags)

        question = QuestionModel(
            title=title,
            body=body,
            author_id=user_id,
            category_id=category.id,
            tags=tags,
        )
        db.session.add(question)
        db.session.commit()

        flash("Pregunta publicada.", "success")
        return redirect(url_for("questions.detail", question_id=question.id))

    questions = db.session.scalars(
        db.select(QuestionModel).order_by(QuestionModel.created_at.desc())
    ).all()
    return render_template("questions/index.html", questions=questions)


@questions_bp.get("/<int:question_id>")
def detail(question_id: int):
    question = db.get_or_404(QuestionModel, question_id)
    return render_template("questions/detail.html", question=question)


@questions_bp.post("/<int:question_id>/answers")
def add_answer(question_id: int):
    user_id = session.get("user_id")
    if not user_id:
        flash("Tenés que iniciar sesión para responder.", "error")
        return redirect(url_for("auth.login"))

    question = db.get_or_404(QuestionModel, question_id)
    body = request.form.get("body", "").strip()
    if not body:
        flash("La respuesta no puede estar vacía.", "error")
        return redirect(url_for("questions.detail", question_id=question.id))

    answer = AnswerModel(
        body=body,
        question_id=question.id,
        author_id=user_id,
        is_ai_generated=False,
    )
    db.session.add(answer)
    db.session.commit()
    flash("Respuesta agregada.", "success")
    return redirect(url_for("questions.detail", question_id=question.id))


@questions_bp.post("/<int:question_id>/ai-answer")
def generate_ai_answer(question_id: int):
    question = db.get_or_404(QuestionModel, question_id)
    model_name = request.form.get("model_name", "gemini").strip().lower()

    try:
        strategy = create_strategy(model_name)
        domain_question = question.to_domain()
        ai_text = strategy.generate_answer(domain_question)
    except AIModelError as err:
        flash(str(err), "error")
        return redirect(url_for("questions.detail", question_id=question.id))

    answer = AnswerModel(
        body=ai_text,
        question_id=question.id,
        author_id=None,
        is_ai_generated=True,
        ai_agent_name=f"IA ({model_name.capitalize()})",
    )
    db.session.add(answer)
    db.session.commit()
    flash(f"Respuesta generada con {model_name.capitalize()}.", "success")
    return redirect(url_for("questions.detail", question_id=question.id))


@questions_bp.post("/<int:question_id>/answers/<int:answer_id>/accept")
def toggle_accept(question_id: int, answer_id: int):
    user_id = session.get("user_id")
    question = db.get_or_404(QuestionModel, question_id)
    answer = db.get_or_404(AnswerModel, answer_id)

    if user_id != question.author_id:
        flash("Solo el autor de la pregunta puede aceptar respuestas.", "error")
        return redirect(url_for("questions.detail", question_id=question.id))

    answer.is_accepted = not answer.is_accepted
    db.session.commit()
    return redirect(url_for("questions.detail", question_id=question.id))