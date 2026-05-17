from database import db
from datetime import datetime
from zoneinfo import ZoneInfo


def horario_brasilia():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))


TIPO_CRIACAO = "criacao"
TIPO_STATUS = "status"
TIPO_COMENTARIO = "comentario"
TIPO_EDICAO = "edicao"
TIPO_ANEXO = "anexo"
TIPO_CANCELAMENTO = "cancelamento"
TIPO_REABERTURA = "reabertura"
TIPO_ATRIBUICAO = "atribuicao"


class Evento(db.Model):
    __tablename__ = "eventos"

    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey("chamados.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    tipo = db.Column(db.String(30), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    status_novo = db.Column(db.String(30), nullable=True)
    data_criacao = db.Column(db.DateTime, default=horario_brasilia)

    usuario = db.relationship("Usuario")

    def to_dict(self):
        return {
            "id": self.id,
            "chamado_id": self.chamado_id,
            "usuario_id": self.usuario_id,
            "usuario_nome": self.usuario.nome if self.usuario else None,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "status_novo": self.status_novo,
            "data_criacao": self.data_criacao.strftime("%d/%m/%Y %H:%M") if self.data_criacao else None,
        }
