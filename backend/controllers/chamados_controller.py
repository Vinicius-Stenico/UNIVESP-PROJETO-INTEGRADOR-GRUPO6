from models.chamado import Chamado
from models.usuario import Usuario
from models.categoria import Categoria
from models.evento import Evento, TIPO_CRIACAO, TIPO_STATUS
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

def criar_chamado(titulo, descricao, usuario_id=None, categoria_id=None,
                  anexo_path=None, anexo_nome=None):
    usuario = Usuario.query.get(usuario_id) if usuario_id else None

    if not usuario:
        raise ValueError("Usuário não encontrado")

    if categoria_id and not Categoria.query.get(categoria_id):
        raise ValueError("Categoria não encontrada")

    chamado = Chamado(
        titulo=titulo,
        descricao=descricao,
        usuario_id=usuario_id,
        categoria_id=categoria_id,
        anexo_path=anexo_path,
        anexo_nome=anexo_nome,
    )

    db.session.add(chamado)
    db.session.flush()

    evento = Evento(
        chamado_id=chamado.id,
        usuario_id=usuario_id,
        tipo=TIPO_CRIACAO,
        descricao=f"{usuario.nome} criou a solicitação",
        status_novo="Aberto",
    )
    db.session.add(evento)
    db.session.commit()

    return chamado


def editar_chamado(id, usuario_id, titulo=None, descricao=None,
                   categoria_id=None, anexo_path=None, anexo_nome=None):
    chamado = Chamado.query.get(id)
    if not chamado:
        raise ValueError("Chamado não encontrado")

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        raise ValueError("Usuário não encontrado")

    if chamado.status in ("Cancelado", "Resolvido"):
        raise ValueError("Solicitação encerrada — não pode mais ser editada")

    eh_dono_aberto = (chamado.usuario_id == usuario.id and chamado.status == "Aberto")
    eh_admin_secretaria = usuario.tipo in ("admin", "secretaria")
    if not (eh_dono_aberto or eh_admin_secretaria):
        raise ValueError("Você não tem permissão para editar essa solicitação")

    if categoria_id is not None:
        if categoria_id and not Categoria.query.get(categoria_id):
            raise ValueError("Categoria não encontrada")
        chamado.categoria_id = categoria_id or None

    if titulo is not None:
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("Título não pode ser vazio")
        chamado.titulo = titulo

    if descricao is not None:
        chamado.descricao = descricao

    if anexo_path is not None:
        chamado.anexo_path = anexo_path
        chamado.anexo_nome = anexo_nome

    chamado.atualizado_por = usuario_id

    evento = Evento(
        chamado_id=chamado.id,
        usuario_id=usuario_id,
        tipo="edicao",
        descricao=f"{usuario.nome} editou a solicitação",
    )
    db.session.add(evento)
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
    
    eh_dono_cancelando = (
        novo_status == "Cancelado"
        and chamado.usuario_id == usuario.id
        and chamado.status in ("Aberto", "Em andamento")
    )
    if usuario.tipo not in ["admin", "secretaria"] and not eh_dono_cancelando:
        raise ValueError("Você não tem permissão para alterar o status")

    if chamado.status == novo_status:
        raise ValueError("Chamado já está com esse status")

    chamado.status = novo_status
    chamado.atualizado_por = usuario_id

    evento = Evento(
        chamado_id=chamado.id,
        usuario_id=usuario_id,
        tipo=TIPO_STATUS,
        descricao=f"{usuario.nome} alterou o status para {novo_status}",
        status_novo=novo_status,
    )
    db.session.add(evento)
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