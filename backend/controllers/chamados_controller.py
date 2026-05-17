from models.chamado import Chamado
from models.usuario import Usuario
from models.categoria import Categoria
from controllers.eventos_controller import criar_evento
from database import db
from utils.constants import (
    STATUS_ABERTO,
    STATUS_EM_ANDAMENTO,
    STATUS_CONCLUIDO,
    STATUS_CANCELADO,
    normalizar_status,
)
from models.evento import (
    TIPO_CRIACAO,
    TIPO_STATUS,
    TIPO_EDICAO,
    TIPO_ANEXO,
    TIPO_CANCELAMENTO,
    TIPO_REABERTURA,
    TIPO_ATRIBUICAO,
)
from utils.constants import (
    STATUS_ABERTO,
    STATUS_EM_ANDAMENTO,
    STATUS_CONCLUIDO,
    STATUS_CANCELADO,
    normalizar_prioridade,
)

def validar_status(status):
    return normalizar_status(status)

def criar_chamado(titulo, descricao, usuario_id=None, categoria_id=None,
                  anexo_path=None, anexo_nome=None, prioridade=None):
    usuario = Usuario.query.get(usuario_id) if usuario_id else None

    if not usuario:
        raise ValueError("Usuário não encontrado")

    if categoria_id and not Categoria.query.get(categoria_id):
        raise ValueError("Categoria não encontrada")

    prioridade = normalizar_prioridade(prioridade)

    chamado = Chamado(
        titulo=titulo,
        descricao=descricao,
        usuario_id=usuario_id,
        categoria_id=categoria_id,
        anexo_path=anexo_path,
        anexo_nome=anexo_nome,
        prioridade = prioridade,
        status=STATUS_ABERTO,
    )

    db.session.add(chamado)
    db.session.flush()

    criar_evento(
        chamado_id=chamado.id,
        usuario_id=usuario_id,
        tipo=TIPO_CRIACAO,
        descricao=f"{usuario.nome} criou a solicitação com prioridade {prioridade}",
        status_novo=STATUS_ABERTO,
    )

    if anexo_nome:
        criar_evento(
            chamado_id=chamado.id,
            usuario_id=usuario_id,
            tipo=TIPO_ANEXO,
            descricao=f"{usuario.nome} anexou o arquivo: {anexo_nome}",
        )

    db.session.commit()

    return chamado


def editar_chamado(id, usuario_id, titulo=None, descricao=None,
                   categoria_id=None, anexo_path=None, anexo_nome=None, prioridade=None):
    alteracoes = []
    
    chamado = Chamado.query.get(id)
    if not chamado:
        raise ValueError("Chamado não encontrado")

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        raise ValueError("Usuário não encontrado")

    if chamado.status in (STATUS_CANCELADO, STATUS_CONCLUIDO):
        raise ValueError("Solicitação encerrada — não pode mais ser editada")

    eh_dono_aberto = (chamado.usuario_id == usuario.id and chamado.status == "Aberto")
    eh_admin_secretaria = usuario.tipo in ("admin", "secretaria")
    if not (eh_dono_aberto or eh_admin_secretaria):
        raise ValueError("Você não tem permissão para editar essa solicitação")

    if categoria_id is not None:
        categoria_antiga = chamado.categoria.nome if chamado.categoria else "sem categoria"

        if categoria_id:
            nova_categoria = Categoria.query.get(categoria_id)

            if not nova_categoria:
                raise ValueError("Categoria não encontrada")
            
            categoria_nova = nova_categoria.nome
        else:
            categoria_nova = "Sem categoria"

        if chamado.categoria_id != categoria_id:
            alteracoes.append(f"Categoria alterada de '{categoria_antiga}' para '{categoria_nova}'")
            chamado.categoria_id = categoria_id or None

    if titulo is not None:
        titulo = titulo.strip()

        if not titulo:
            raise ValueError("Título não pode ser vazio")
        
        if chamado.titulo != titulo:
            alteracoes.append(f"Título alterado de '{chamado.titulo}' para '{titulo}'")
            chamado.titulo = titulo

    if descricao is not None:
        if chamado.descricao != descricao:
            alteracoes.append("Descrição alterada")
            chamado.descricao = descricao

    if prioridade is not None:
        nova_prioridade = normalizar_prioridade(prioridade)
        
        if chamado.prioridade != nova_prioridade:
            alteracoes.append(
                f"Prioridade alterada de '{chamado.prioridade}' para '{nova_prioridade}'"
            )
            chamado.prioridade = nova_prioridade

    if anexo_path is not None:
        chamado.anexo_path = anexo_path
        chamado.anexo_nome = anexo_nome

        if anexo_nome:
            alteracoes.append(f"Novo anexo enviado: {anexo_nome}")

    chamado.atualizado_por = usuario_id

    if alteracoes:
        descricao_evento = f"{usuario.nome} editou a solicitação: " + "; ".join(alteracoes)
    else:
        descricao_evento = f"{usuario.nome} acessou a edição, mas não alterou informações"

    criar_evento(
        chamado_id=chamado.id,
        usuario_id=usuario_id,
        tipo=TIPO_EDICAO,
        descricao=descricao_evento,
    )
    db.session.commit()

    return chamado

def assumir_chamado(id, usuario_id):
    chamado = Chamado.query.get(id)

    if not chamado:
        raise ValueError("Chamado não encontrado")
    
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        raise ValueError("Usuário não encontrado")
    
    if usuario.tipo not in ("admin", "secretaria"):
        raise ValueError("Apenas secretaria ou admin podem assumir chamados")
    
    if chamado.status in (STATUS_CANCELADO, STATUS_CONCLUIDO):
        raise ValueError("Solicitação encerrada - não pode ser assumida")
    
    responsavel_anterior = chamado.responsavel.nome if chamado.responsavel else None

    chamado.responsavel_id = usuario.id
    chamado.atualizado_por = usuario.id

    if responsavel_anterior:
        descricao = (
            f"{usuario.nome} assumiu o chamado. "
            f"Responsável anterior: {responsavel_anterior}"
        )
    else:
        descricao = f"{usuario.nome} assumiu o chamado"

    criar_evento(
        chamado_id=chamado.id,
        usuario_id=usuario.id,
        tipo=TIPO_ATRIBUICAO,
        descricao=descricao,
    )

    if chamado.status == STATUS_ABERTO:
        status_anterior = chamado.status
        chamado.status = STATUS_EM_ANDAMENTO

        criar_evento(
            chamado_id=chamado.id,
            usuario_id=usuario.id,
            tipo=TIPO_STATUS,
            descricao=f"{usuario.nome} alterou o status de '{status_anterior}' para '{STATUS_EM_ANDAMENTO}'",
            status_novo=STATUS_EM_ANDAMENTO,
        )

    db.session.commit()

    return chamado.to_dict()

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
        and chamado.status in (STATUS_ABERTO, STATUS_EM_ANDAMENTO)
    )
    if usuario.tipo not in ["admin", "secretaria"] and not eh_dono_cancelando:
        raise ValueError("Você não tem permissão para alterar o status")

    if chamado.status == novo_status:
        raise ValueError("Chamado já está com esse status")

    status_anterior = chamado.status

    chamado.status = novo_status
    chamado.atualizado_por = usuario_id

    tipo_evento = TIPO_STATUS

    if novo_status == STATUS_CANCELADO:
        tipo_evento = TIPO_CANCELAMENTO

    elif status_anterior == STATUS_CONCLUIDO and novo_status != STATUS_CONCLUIDO:
        tipo_evento = TIPO_REABERTURA

    criar_evento(
        chamado_id=chamado.id,
        usuario_id=usuario_id,
        tipo=tipo_evento,
        descricao=f"{usuario.nome} alterou o status de '{status_anterior}' para '{novo_status}'",
        status_novo=novo_status,
    )

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