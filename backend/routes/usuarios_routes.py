from flask import Blueprint, jsonify, request
from controllers.usuarios_controller import (
    listar_usuarios,
    obter_usuario,
    criar_usuario,
    atualizar_usuario,
)

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    inclui_inativos = request.args.get('todos') == '1'
    return jsonify(listar_usuarios(somente_ativos=not inclui_inativos)), 200


@usuarios_bp.route('/api/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    try:
        usuario = obter_usuario(id)
        return jsonify(usuario.to_dict()), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


@usuarios_bp.route('/api/usuarios', methods=['POST'])
def post_usuario():
    dados = request.get_json() or {}
    try:
        usuario = criar_usuario(
            nome=dados.get('nome'),
            email=dados.get('email'),
            senha=dados.get('senha'),
            tipo=dados.get('tipo'),
        )
        return jsonify(usuario.to_dict()), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@usuarios_bp.route('/api/usuarios/<int:id>', methods=['PUT'])
def put_usuario(id):
    dados = request.get_json() or {}
    try:
        usuario = atualizar_usuario(
            id,
            nome=dados.get('nome'),
            email=dados.get('email'),
            tipo=dados.get('tipo'),
            senha=dados.get('senha'),
            ativo=dados.get('ativo'),
        )
        return jsonify(usuario.to_dict()), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
