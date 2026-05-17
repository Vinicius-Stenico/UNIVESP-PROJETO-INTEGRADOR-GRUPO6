from models.evento import Evento
from database import db

def criar_evento(chamado_id, usuario_id, tipo, descricao, status_novo=None):
    evento = Evento(
        chamado_id=chamado_id,
        usuario_id=usuario_id,
        tipo=tipo,
        descricao=descricao,
        status_novo=status_novo,
    )
    
    db.session.add(evento)
    return evento


def listar_eventos_por_chamado(chamado_id):
    eventos = (
        Evento.query
        .filter_by(chamado_id=chamado_id)
        .order_by(Evento.data_criacao.asc())
        .all()
    )

    return [e.to_dict() for e in eventos]


def listar_todos_eventos(limite=200):
    eventos = (
        Evento.query
        .order_by(Evento.data_criacao.desc())
        .limit(limite)
        .all()
    )

    return [e.to_dict() for e in eventos]
