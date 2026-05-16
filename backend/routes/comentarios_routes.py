from flask import Blueprint, jsonify, request
from utils.auth import login_required, usuario_logado, pode_ver_chamado, secretaria_ou_admin_required
from models.chamado import Chamado
from controllers.comentarios_controller import (
    listar_comentarios,
    listar_todos_comentarios,
    criar_comentario,
)

comentarios_bp = Blueprint('comentarios', __name__)


@comentarios_bp.route('/api/comentarios', methods=['GET'])
@secretaria_ou_admin_required
def get_todos_comentarios():
    return jsonify(listar_todos_comentarios()), 200


@comentarios_bp.route('/api/chamados/<int:chamado_id>/comentarios', methods=['GET'])
@login_required
def get_comentarios_por_chamado(chamado_id):
    usuario = usuario_logado()
    chamado = Chamado.query.get(chamado_id)

    if not chamado:
        return jsonify({"erro": "Chamado não encontrado"}), 404

    if not pode_ver_chamado(usuario, chamado):
        return jsonify({"erro": "Você não tem permissão para visualizar comentários deste chamado"}), 403

    return jsonify(listar_comentarios(chamado_id)), 200

@comentarios_bp.route('/api/chamados/<int:chamado_id>/comentarios', methods=['POST'])
@login_required
def post_comentario(chamado_id):
    dados = request.get_json() or {}

    try:
        usuario = usuario_logado()
        chamado = Chamado.query.get(chamado_id)

        if not chamado:
            return jsonify({"erro": "Chamado não encontrado"}), 404

        if not pode_ver_chamado(usuario, chamado):
            return jsonify({"erro": "Você não tem permissão para comentar neste chamado"}), 403

        coment = criar_comentario(
            chamado_id=chamado_id,
            usuario_id=usuario.id,
            texto=dados.get('texto'),
        )

        return jsonify(coment.to_dict()), 201

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
