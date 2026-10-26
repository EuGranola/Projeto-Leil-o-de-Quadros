"""Conexão com o SQLite (módulo padrão `sqlite3`, sem ORM).

Ideia central: abrimos UMA conexão por requisição e a fechamos ao final.
  - get_db()  -> devolve a conexão da requisição atual (abre se ainda não existir)
  - close_db() -> fecha a conexão quando a requisição termina
"""

import sqlite3

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        # Com Row, cada linha pode ser lida pelo nome da coluna: linha["email"]
        g.db.row_factory = sqlite3.Row
        # O SQLite não aplica chaves estrangeiras por padrão; aqui ligamos.
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(erro=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Executa o schema.sql (cria as tabelas que ainda não existem)."""
    db = get_db()
    with current_app.open_resource("schema.sql") as arquivo:
        db.executescript(arquivo.read().decode("utf-8"))


@click.command("init-db")
def init_db_command():
    """Cria as tabelas e cadastra os usuários de teste."""
    # Import aqui dentro para evitar import circular
    # (models.usuarios importa este arquivo).
    from app.models.usuarios import CONTAS_TESTE, criar_usuario

    init_db()
    click.echo("Tabelas criadas.")

    for conta in CONTAS_TESTE:
        try:
            criar_usuario(conta["nome"], conta["email"], conta["senha"])
            click.echo(f"  usuário criado: {conta['email']}")
        except sqlite3.IntegrityError:
            # Violou o UNIQUE do e-mail: o usuário já existe.
            click.echo(f"  já existe:      {conta['email']}")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)