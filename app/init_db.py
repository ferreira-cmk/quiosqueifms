import sqlite3

conn = sqlite3.connect('conteudos.db')

conn.execute('''
CREATE TABLE IF NOT EXISTS conteudos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    imagem TEXT NOT NULL,
    grupo TEXT NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT 1
)
''')

conn.close()
print("Banco de dados 'conteudos.db' criado com sucesso.")
