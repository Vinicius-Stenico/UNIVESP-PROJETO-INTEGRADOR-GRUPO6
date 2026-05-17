from app import app
from database import db
from sqlalchemy import text


with app.app_context():
    with db.engine.connect() as conn:
        colunas = conn.execute(text("PRAGMA table_info(chamados)")).fetchall()
        nomes_colunas = [coluna[1] for coluna in colunas]

        if "prioridade" not in nomes_colunas:
            conn.execute(
                text(
                    "ALTER TABLE chamados "
                    "ADD COLUMN prioridade VARCHAR(20) NOT NULL DEFAULT 'Normal'"
                )
            )
            print("Coluna prioridade criada.")

        if "responsavel_id" not in nomes_colunas:
            conn.execute(
                text(
                    "ALTER TABLE chamados "
                    "ADD COLUMN responsavel_id INTEGER"
                )
            )
            print("Coluna responsavel_id criada.")

        conn.commit()

    print("Migração finalizada.")