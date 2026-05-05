from flask import Blueprint, jsonify, request
from backend.controllers.chamados_controller import (
    listar_chamados_recentes,
    criar_chamado,
    atualizar_status,
    buscar_chamado_por_id,
    deletar_chamado,
    listar_chamados_por_status,
    listar_chamados_por_usuario,
    buscar_chamados_por_texto
)

chamados_bp = Blueprint('chamados', __name__)

@chamados_bp.route('/api/chamados', methods=['GET'])
def get_chamados():
    return jsonify(listar_chamados_recentes()), 200

@chamados_bp.route('/api/chamados', methods=['POST'])
def post_chamado():
    dados = request.get_json()
    try:
        novo = criar_chamado(dados.get('titulo'), dados.get('descricao'), dados.get('usuario_id'))
        return jsonify({"mensagem": "Chamado criado com sucesso!"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@chamados_bp.route('/api/chamados/<int:id>', methods=['GET'])
def get_chamado_id(id):
    try:
        return jsonify(buscar_chamado_por_id(id)), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404

@chamados_bp.route('/api/chamados/<int:id>/status', methods=['PUT'])
def put_status(id):
    dados = request.get_json()
    try:
        resultado = atualizar_status(id, dados.get('status'), dados.get('usuario_id'))
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

@chamados_bp.route('/api/chamados/<int:id>', methods=['DELETE'])
def delete_chamado(id):
    try:
        deletar_chamado(id)
        return jsonify({"mensagem": "Chamado excluído!"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404

@chamados_bp.route('/api/chamados/usuario/<int:usuario_id>', methods=['GET'])
def get_por_usuario(usuario_id):
    return jsonify(listar_chamados_por_usuario(usuario_id)), 200

@chamados_bp.route('/api/chamados/busca', methods=['GET'])
def get_busca():
    texto = request.args.get('q', '')
    return jsonify(buscar_chamados_por_texto(texto)), 200