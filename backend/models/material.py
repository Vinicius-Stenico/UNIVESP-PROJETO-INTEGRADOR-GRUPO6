from database import db


class Material(db.Model):
    __tablename__ = "materiais"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=True)
    unidade = db.Column(db.String(20), nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    categoria = db.relationship("Categoria")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "categoria_id": self.categoria_id,
            "categoria_nome": self.categoria.nome if self.categoria else None,
            "unidade": self.unidade,
            "ativo": self.ativo,
        }
