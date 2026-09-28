"""Usuários de teste em memória.

Quando o banco de dados chegar, basta trocar o corpo das funções
`buscar_por_email` e `buscar_por_id` por consultas reais. O restante
da aplicação continua igual.
"""

from werkzeug.security import check_password_hash, generate_password_hash

# Somente para desenvolvimento. As senhas em texto puro ficam aqui apenas
# para gerar os hashes e para exibir a dica na tela de login em modo debug.
CONTAS_TESTE = [
    {"id": 1, "nome": "Ana Souza", "email": "ana@leilao.test", "senha": "ana123"},
    {"id": 2, "nome": "Bruno Lima", "email": "bruno@leilao.test", "senha": "bruno123"},
    {"id": 3, "nome": "Carla Mendes", "email": "carla@leilao.test", "senha": "carla123"},
]

# O que a aplicação realmente usa: nada de senha em texto puro, só o hash.
_POR_ID = {
    conta["id"]: {
        "id": conta["id"],
        "nome": conta["nome"],
        "email": conta["email"],
        "senha_hash": generate_password_hash(conta["senha"]),
    }
    for conta in CONTAS_TESTE
}
_POR_EMAIL = {usuario["email"]: usuario for usuario in _POR_ID.values()}

# Hash usado quando o e-mail não existe, para que o tempo de resposta
# seja parecido nos dois casos (e-mail inexistente x senha errada).
_HASH_FALSO = generate_password_hash("senha-falsa")


def buscar_por_email(email):
    return _POR_EMAIL.get(email)


def buscar_por_id(usuario_id):
    return _POR_ID.get(usuario_id)


def autenticar(email, senha):
    """Retorna o usuário se e-mail e senha conferem; senão, None."""
    usuario = buscar_por_email(email)
    if usuario is None:
        check_password_hash(_HASH_FALSO, senha)
        return None
    if check_password_hash(usuario["senha_hash"], senha):
        return usuario
    return None