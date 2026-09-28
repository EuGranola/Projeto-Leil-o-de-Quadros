"""Autenticação: middleware (before_request) e rotas de login/logout.

Toda rota exige login, exceto as listadas em ROTAS_PUBLICAS. Assim, uma
rota nova criada no futuro já nasce protegida, sem precisar de decorator.
"""

import hmac
import secrets
from urllib.parse import urlparse

from flask import (Blueprint, abort, current_app, flash, g, redirect,
                   render_template, request, session, url_for)

from app.models.usuarios import CONTAS_TESTE, autenticar, buscar_por_id

auth_bp = Blueprint("auth", __name__)

# Endpoints ("blueprint.função") que não exigem login.
ROTAS_PUBLICAS = {"auth.login", "static"}


# ---------- Rotas ----------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("usuario_id") is not None:
            return redirect(url_for("home"))
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    senha = request.form.get("senha", "")
    usuario = autenticar(email, senha)

    if usuario is None:
        flash("E-mail ou senha incorretos.", "erro")
        return render_template("login.html", email=email), 401

    # Limpa a sessão antes de logar (evita fixação de sessão).
    session.clear()
    session.permanent = True
    session["usuario_id"] = usuario["id"]

    return redirect(destino_seguro(request.args.get("next")) or url_for("home"))


@auth_bp.post("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))


# ---------- Helpers ----------

def destino_seguro(alvo):
    """Aceita apenas caminhos internos, para evitar open redirect."""
    if not alvo:
        return None
    analisado = urlparse(alvo)
    if analisado.netloc or analisado.scheme:
        return None
    if not alvo.startswith("/") or alvo.startswith("//") or "\\" in alvo:
        return None
    return alvo


def _token_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


# ---------- Middleware ----------

def init_auth(app):
    @app.before_request
    def carregar_usuario():
        """Lê a sessão e disponibiliza o usuário logado em g.usuario."""
        g.usuario = None
        usuario_id = session.get("usuario_id")
        if usuario_id is not None:
            g.usuario = buscar_por_id(usuario_id)
            if g.usuario is None:  # sessão de um usuário que não existe mais
                session.clear()

    @app.before_request
    def validar_csrf():
        """Todo POST precisa carregar o token gerado na sessão."""
        if request.method != "POST":
            return
        enviado = request.form.get("csrf_token", "")
        esperado = session.get("csrf_token", "")
        if not esperado or not hmac.compare_digest(enviado, esperado):
            abort(400, description="Token CSRF inválido. Recarregue a página e tente de novo.")

    @app.before_request
    def exigir_login():
        """Bloqueia qualquer rota não pública para quem não está logado."""
        # endpoint None = URL inexistente; deixa o Flask responder 404.
        if request.endpoint is None or request.endpoint in ROTAS_PUBLICAS:
            return
        if g.usuario is None:
            return redirect(url_for("auth.login", next=request.path))

    @app.after_request
    def nao_guardar_cache(resposta):
        """Evita que o botão 'voltar' mostre páginas privadas após o logout."""
        if g.get("usuario") is not None:
            resposta.headers["Cache-Control"] = "no-store"
        return resposta

    @app.context_processor
    def injetar_no_template():
        return {
            "csrf_token": _token_csrf,
            "usuario": g.get("usuario"),
            # A dica de contas de teste só aparece com debug ligado.
            "contas_teste": CONTAS_TESTE if current_app.debug else [],
        }