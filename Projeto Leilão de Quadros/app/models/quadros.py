>>> from app.models.quadros import listar_quadros
>>> [dict(q) for q in listar_quadros()]

SELECT q.id, q.titulo, q.artista, q.preco_inicial, u.nome AS dono_nome
FROM quadros q
JOIN usuarios u ON u.id = q.dono_id
ORDER BY q.criado_em DESC