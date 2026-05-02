from database import db
from datetime import datetime
from zoneinfo import ZoneInfo
from models.usuario import Usuario

def horario_brasilia():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))

class Chamado(db.Model):
    __tablename__ = "chamados"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Aberto")

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    atualizado_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

    usuario = db.relationship(
        "Usuario",
        foreign_keys=[usuario_id],
        back_populates="chamados"
    )

    data_criacao = db.Column(db.DateTime, default=horario_brasilia)
    data_atualizacao = db.Column(
        db.DateTime,
        default=horario_brasilia,
        onupdate=horario_brasilia
    )

    def to_dict(self):
        usuario_atualizador = Usuario.query.get(self.atualizado_por) if self.atualizado_por else None

        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "status": self.status,
            "usuario_id": self.usuario_id,
            "usuario_nome": self.usuario.nome if self.usuario else None,
            "atualizado_por": self.atualizado_por,
            "atualizado_por_nome": usuario_atualizador.nome if usuario_atualizador else None,
            "data_criacao": self.data_criacao.strftime("%d/%m/%Y %H:%M") if self.data_criacao else None,
            "data_atualizacao": self.data_atualizacao.strftime("%d/%m/%Y %H:%M") if self.data_atualizacao else None
        }