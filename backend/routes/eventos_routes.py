from flask import Blueprint, jsonify, request
from utils.auth import login_required, admin_required, usuario_logado, pode_ver_chamado
from models.chamado import Chamado
from controllers.eventos_controller import (
    listar_eventos_por_chamado,
    listar_todos_eventos,
)

eventos_bp = Blueprint('eventos', __name__)


@eventos_bp.route('/api/eventos', methods=['GET'])
@admin_required
def get_todos_eventos():
    limite = request.args.get('limite', default=200, type=int)
    return jsonify(listar_todos_eventos(limite=limite)), 200

@eventos_bp.route('/api/chamados/<int:chamado_id>/eventos', methods=['GET'])
@login_required
def get_eventos_por_chamado(chamado_id):
    usuario = usuario_logado()
    chamado = Chamado.query.get(chamado_id)

    if not chamado:
        return jsonify({"erro": "Chamado não encontrado"}), 404

    if not pode_ver_chamado(usuario, chamado):
        return jsonify({"erro": "Você não tem permissão para visualizar o histórico deste chamado"}), 403

    return jsonify(listar_eventos_por_chamado(chamado_id)), 200