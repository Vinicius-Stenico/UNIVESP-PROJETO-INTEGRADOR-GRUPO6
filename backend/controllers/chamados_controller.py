from models.chamado import Chamado
from models.usuario import Usuario
from database import db

def validar_status(status):
    status = status.strip().lower()    

    mapa = {
        "aberto": "Aberto",
        "em andamento": "Em andamento",
        "resolvido": "Resolvido",
        "cancelado": "Cancelado"
    }

    if status not in mapa:
        raise ValueError("Status inválido")
    
    return mapa[status]

def criar_chamado(titulo, descricao, usuario_id=None):
    if usuario_id:
        usuario = Usuario.query.get(usuario_id)

    if not usuario:
        raise ValueError("Usuário não encontrado")
    
    chamado = Chamado(
        titulo=titulo,
        descricao=descricao,
        usuario_id=usuario_id

    )


    db.session.add(chamado)
    db.session.commit()

    return chamado

def atualizar_status(id, novo_status, usuario_id):
    novo_status = validar_status(novo_status)

    chamado = Chamado.query.get(id)
    usuario = Usuario.query.get(usuario_id)

    if not chamado:
        raise ValueError("Chamado não encontrado")
    
    if not usuario:
        raise ValueError("Usuário não encontrado")
    
    if usuario.tipo not in ["admin", "secretaria"]:
        raise ValueError("Você não tem permissão para alterar o status")

    if chamado.status == novo_status:
        raise ValueError("Chamado já está com esse status")

    chamado.status = novo_status
    chamado.atualizado_por = usuario_id
    
    db.session.commit()
    
    return chamado.to_dict()

def deletar_chamado(id):
    chamado = Chamado.query.get(id)

    if not chamado:
        raise ValueError("Chamado não encontrado")
    
    db.session.delete(chamado)
    db.session.commit()

def listar_chamados():
    return Chamado.query.all()      

def deletar_todos():
    Chamado.query.delete()
    db.session.commit()

def listar_chamados_recentes():
    chamados = Chamado.query.order_by(Chamado.data_criacao.desc()).all()
    return [c.to_dict() for c in chamados]

def listar_chamados_por_status(status):
    chamados = Chamado.query.filter_by(status=status).all()
    return [c.to_dict() for c in chamados]

def listar_chamados_por_usuario(usuario_id):
    chamados = Chamado.query.filter_by(usuario_id=usuario_id).all()
    return [c.to_dict() for c in chamados]

def buscar_chamados_por_texto(texto):
    chamados = Chamado.query.filter(
        Chamado.titulo.ilike(f"%{texto}%") |
        Chamado.descricao.ilike(f"%{texto}%")
    ).all()

    return [c.to_dict() for c in chamados]

def buscar_chamado_por_id(id):
    chamado = Chamado.query.get(id)

    if not chamado:
        raise ValueError("Chamado não encontrado")
    
    return chamado.to_dict()