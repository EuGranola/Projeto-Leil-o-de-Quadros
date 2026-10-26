import os
from datetime import timedelta

from flask import Flask, render_template

from app import database
from app.controllers.auth import auth_bp, init_auth


def create_app(config=None):
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
        # O arquivo do banco fica na pasta "instance/", na raiz do projeto.
        DATABASE=os.path.join(app.instance_path, "leilao.db"),
    )
    if config:  # permite sobrescrever (útil em testes)
        app.config.update(config)

    os.makedirs(app.instance_path, exist_ok=True)

    database.init_app(app)  # fecha a conexão ao fim da requisição + comando init-db
    init_auth(app)          # middleware: sessão, CSRF e proteção das rotas
    app.register_blueprint(auth_bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app