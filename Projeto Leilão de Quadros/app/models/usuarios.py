"""Acesso à tabela `usuarios` com SQL puro.

REGRA DE OURO: nunca monte o SQL concatenando texto do usuário
(f"... WHERE email = '{email}'"). Isso permite SQL injection.
Use sempre os marcadores `?` e passe os valores numa tupla separada:
o SQLite trata os valores como dados, nunca como código SQL.
"""

from werkzeug.security import check_password_hash, generate_password_hash

from app.database import get_db

# Dados usados só pelo comando `init-db` (e pela dica na tela de login em debug).
CONTAS_TESTE = [
    {"nome": "Ana Souza", "email": "ana@leilao.test", "senha": "ana123"},
    {"nome": "Bruno Lima", "email": "bruno@leilao.test", "senha": "bruno123"},
    {"nome": "Carla Mendes", "email": "carla@leilao.test", "senha": "carla123"},
]

# Usado quando o e-mail não existe, para o tempo de resposta ser parecido
# nos dois casos (e-mail inexistente x senha errada).
_HASH_FALSO = generate_password_hash("senha-falsa")


def buscar_por_email(email):
    return get_db().execute(
        "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ?",
        (email,),
    ).fetchone()  # uma linha (sqlite3.Row) ou None


def buscar_por_id(usuario_id):
    return get_db().execute(
        "SELECT id, nome, email, senha_hash FROM usuarios WHERE id = ?",
        (usuario_id,),
    ).fetchone()


def criar_usuario(nome, email, senha):
    """Insere um usuário. Levanta sqlite3.IntegrityError se o e-mail já existir."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
        (nome.strip(), email.strip().lower(), generate_password_hash(senha)),
    )
    db.commit()  # sem commit, o INSERT não é gravado de verdade
    return cursor.lastrowid


def autenticar(email, senha):
    """Retorna o usuário se e-mail e senha conferem; senão, None."""
    usuario = buscar_por_email(email)
    if usuario is None:
        check_password_hash(_HASH_FALSO, senha)
        return None
    if check_password_hash(usuario["senha_hash"], senha):
        return usuario
    return None