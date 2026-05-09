from flask import Blueprint, jsonify, request
from controllers.eventos_controller import (
    listar_eventos_por_chamado,
    listar_todos_eventos,
)

eventos_bp = Blueprint('eventos', __name__)


@eventos_bp.route('/api/eventos', methods=['GET'])
def get_todos_eventos():
    limite = request.args.get('limite', default=200, type=int)
    return jsonify(listar_todos_eventos(limite=limite)), 200


@eventos_bp.route('/api/chamados/<int:chamado_id>/eventos', methods=['GET'])
def get_eventos_por_chamado(chamado_id):
    return jsonify(listar_eventos_por_chamado(chamado_id)), 200
