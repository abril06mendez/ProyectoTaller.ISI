from flask import Flask, redirect, url_for

from myapp.config import Config
from myapp.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)

    from myapp.api.health import health_bp
    from myapp.web.auth import auth_bp
    from myapp.web.users import users_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    @app.get("/")
    def root():
        return redirect(url_for("users.index"))

    return app