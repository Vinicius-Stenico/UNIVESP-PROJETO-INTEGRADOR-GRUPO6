from models.comentario import Comentario
from models.chamado import Chamado
from models.usuario import Usuario
from models.evento import TIPO_COMENTARIO
from controllers.eventos_controller import criar_evento
from utils.constants import STATUS_CANCELADO, STATUS_CONCLUIDO
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
    if chamado.status in (STATUS_CANCELADO, STATUS_CONCLUIDO):
        raise ValueError("Solicitação encerrada — não aceita mais comentários")
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        raise ValueError("Usuário não encontrado")

    coment = Comentario(chamado_id=chamado_id, usuario_id=usuario_id, texto=texto.strip())
    db.session.add(coment)

    texto_resumo = texto.strip()

    if len(texto_resumo) > 80:
        texto_resumo = texto_resumo[:80] + "..."

    criar_evento(
        chamado_id=chamado_id,
        usuario_id=usuario_id,
        tipo=TIPO_COMENTARIO,
        descricao=f"{usuario.nome} comentou: {texto_resumo}",
    )

    db.session.commit()
    return coment
