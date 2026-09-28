import os
from datetime import timedelta

from flask import Flask, render_template

from app.controllers.auth import auth_bp, init_auth


def create_app():
    # Os templates Jinja2 ficam em app/views (em vez do padrão "templates").
    app = Flask(__name__, template_folder="views", static_folder="static")

    app.config.update(
        # Em produção, defina a variável de ambiente SECRET_KEY com um valor longo e aleatório.
        SECRET_KEY=os.environ.get("SECRET_KEY", "chave-apenas-para-desenvolvimento"),
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        # Ative quando servir por HTTPS:
        # SESSION_COOKIE_SECURE=True,
    )

    init_auth(app)  # middleware: sessão, CSRF e proteção das rotas
    app.register_blueprint(auth_bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app