"""
Migration: adiciona a coluna `ativo` na tabela `usuarios`.

Idempotente: detecta se a coluna já existe e não faz nada nesse caso.
Roda direto via `python migrations/add_usuario_ativo.py` (dentro de backend/, com venv ativo).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from app import app, db


def main():
    with app.app_context():
        inspector = inspect(db.engine)
        colunas = [c["name"] for c in inspector.get_columns("usuarios")]
        if "ativo" in colunas:
            print("Coluna 'ativo' já existe — nada a fazer.")
            return

        with db.engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE usuarios ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1"
            ))
        print("Coluna 'ativo' adicionada à tabela 'usuarios' (default 1).")


if __name__ == "__main__":
    main()
