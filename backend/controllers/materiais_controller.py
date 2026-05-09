from models.material import Material
from models.categoria import Categoria
from database import db


def listar_materiais(somente_ativos=True, categoria_id=None):
    q = Material.query
    if somente_ativos:
        q = q.filter_by(ativo=True)
    if categoria_id:
        q = q.filter_by(categoria_id=categoria_id)
    return [m.to_dict() for m in q.order_by(Material.nome).all()]


def criar_material(nome, categoria_id=None, unidade=None):
    if not nome or not nome.strip():
        raise ValueError("Nome é obrigatório")
    nome = nome.strip()
    if categoria_id and not Categoria.query.get(categoria_id):
        raise ValueError("Categoria não encontrada")
    mat = Material(nome=nome, categoria_id=categoria_id, unidade=(unidade or None))
    db.session.add(mat)
    db.session.commit()
    return mat


def atualizar_material(id, nome=None, categoria_id=None, unidade=None, ativo=None):
    mat = Material.query.get(id)
    if not mat:
        raise ValueError("Material não encontrado")
    if nome is not None:
        nome = nome.strip()
        if not nome:
            raise ValueError("Nome inválido")
        mat.nome = nome
    if categoria_id is not None:
        if categoria_id and not Categoria.query.get(categoria_id):
            raise ValueError("Categoria não encontrada")
        mat.categoria_id = categoria_id or None
    if unidade is not None:
        mat.unidade = unidade or None
    if ativo is not None:
        mat.ativo = bool(ativo)
    db.session.commit()
    return mat


def deletar_material(id):
    mat = Material.query.get(id)
    if not mat:
        raise ValueError("Material não encontrado")
    db.session.delete(mat)
    db.session.commit()
