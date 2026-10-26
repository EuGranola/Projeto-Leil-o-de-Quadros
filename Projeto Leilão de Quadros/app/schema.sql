-- Estrutura do banco. É executado pelo comando:  flask --app run init-db
-- O "IF NOT EXISTS" permite rodar o comando várias vezes sem apagar dados.

CREATE TABLE IF NOT EXISTS usuarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,   -- UNIQUE: não permite dois cadastros com o mesmo e-mail
    senha_hash  TEXT    NOT NULL,          -- nunca a senha em texto puro
    criado_em   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS quadros (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo          TEXT    NOT NULL,
    artista         TEXT,
    descricao       TEXT,
    preco_inicial   INTEGER NOT NULL,  -- em centavos
    dono_id         INTEGER NOT NULL REFERENCES usuarios(id),
    criado_em       TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);