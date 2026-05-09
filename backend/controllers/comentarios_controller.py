from models.comentario import Comentario
from models.chamado import Chamado
from models.usuario import Usuario
from models.evento import Evento, TIPO_COMENTARIO
from database import db


def listar_comentarios(chamado_id):
    comentarios = (Comentario.query
                   .filter_by(chamado_id=chamado_id)
                   .order_by(Comentario.data_criacao.asc())
                   .all())
    return [c.to_dict() for c in comentarios]


def listar_todos_comentarios():
    comentarios = Comentario.query.order_by(Comentario.data_criacao.desc()).all()
    return [c.to_dict() for c in comentarios]


def criar_comentario(chamado_id, usuario_id, texto):
    if not texto or not texto.strip():
        raise ValueError("Comentário não pode ser vazio")
    chamado = Chamado.query.get(chamado_id)
    if not chamado:
        raise ValueError("Chamado não encontrado")
    if chamado.status in ("Cancelado", "Resolvido"):
        raise ValueError("Solicitação encerrada — não aceita mais comentários")
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        raise ValueError("Usuário não encontrado")

    coment = Comentario(chamado_id=chamado_id, usuario_id=usuario_id, texto=texto.strip())
    db.session.add(coment)

    evento = Evento(
        chamado_id=chamado_id,
        usuario_id=usuario_id,
        tipo=TIPO_COMENTARIO,
        descricao=f"{usuario.nome} adicionou um comentário",
    )
    db.session.add(evento)
    db.session.commit()
    return coment
