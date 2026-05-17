from models.categoria import Categoria
from database import db


def listar_categorias(somente_ativas=True):
    q = Categoria.query
    if somente_ativas:
        q = q.filter_by(ativo=True)
    return [c.to_dict() for c in q.order_by(Categoria.nome).all()]


def criar_categoria(nome):
    if not nome or not nome.strip():
        raise ValueError("Nome é obrigatório")
    nome = nome.strip()
    if Categoria.query.filter_by(nome=nome).first():
        raise ValueError("Já existe uma categoria com esse nome")
    cat = Categoria(nome=nome)
    db.session.add(cat)
    db.session.commit()
    return cat


def atualizar_categoria(id, nome=None, ativo=None):
    cat = Categoria.query.get(id)
    if not cat:
        raise ValueError("Categoria não encontrada")
    if nome is not None:
        nome = nome.strip()
        if not nome:
            raise ValueError("Nome inválido")
        existente = Categoria.query.filter_by(nome=nome).first()
        if existente and existente.id != id:
            raise ValueError("Já existe uma categoria com esse nome")
        cat.nome = nome
    if ativo is not None:
        cat.ativo = bool(ativo)
    db.session.commit()
    return cat


def deletar_categoria(id):
    cat = Categoria.query.get(id)
    if not cat:
        raise ValueError("Categoria não encontrada")
    cat.ativo = False
    db.session.commit()
