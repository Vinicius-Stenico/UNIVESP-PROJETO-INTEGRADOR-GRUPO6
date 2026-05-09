from flask import Blueprint, jsonify, request
from controllers.comentarios_controller import (
    listar_comentarios,
    listar_todos_comentarios,
    criar_comentario,
)

comentarios_bp = Blueprint('comentarios', __name__)


@comentarios_bp.route('/api/comentarios', methods=['GET'])
def get_todos_comentarios():
    return jsonify(listar_todos_comentarios()), 200


@comentarios_bp.route('/api/chamados/<int:chamado_id>/comentarios', methods=['GET'])
def get_comentarios_por_chamado(chamado_id):
    return jsonify(listar_comentarios(chamado_id)), 200


@comentarios_bp.route('/api/chamados/<int:chamado_id>/comentarios', methods=['POST'])
def post_comentario(chamado_id):
    dados = request.get_json() or {}
    try:
        coment = criar_comentario(
            chamado_id=chamado_id,
            usuario_id=dados.get('usuario_id'),
            texto=dados.get('texto'),
        )
        return jsonify(coment.to_dict()), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
