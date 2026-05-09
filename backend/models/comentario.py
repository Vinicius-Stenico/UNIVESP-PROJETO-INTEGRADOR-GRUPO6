from database import db
from datetime import datetime
from zoneinfo import ZoneInfo


def horario_brasilia():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))


class Comentario(db.Model):
    __tablename__ = "comentarios"

    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey("chamados.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=horario_brasilia)

    usuario = db.relationship("Usuario")

    def to_dict(self):
        return {
            "id": self.id,
            "chamado_id": self.chamado_id,
            "usuario_id": self.usuario_id,
            "usuario_nome": self.usuario.nome if self.usuario else None,
            "texto": self.texto,
            "data_criacao": self.data_criacao.strftime("%d/%m/%Y %H:%M") if self.data_criacao else None,
        }
