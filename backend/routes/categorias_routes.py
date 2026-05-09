from flask import Blueprint, jsonify, request
from controllers.categorias_controller import (
    listar_categorias,
    criar_categoria,
    atualizar_categoria,
    deletar_categoria,
)

categorias_bp = Blueprint('categorias', __name__)


@categorias_bp.route('/api/categorias', methods=['GET'])
def get_categorias():
    inclui_inativas = request.args.get('todas') == '1'
    return jsonify(listar_categorias(somente_ativas=not inclui_inativas)), 200


@categorias_bp.route('/api/categorias', methods=['POST'])
def post_categoria():
    dados = request.get_json() or {}
    try:
        cat = criar_categoria(dados.get('nome'))
        return jsonify(cat.to_dict()), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@categorias_bp.route('/api/categorias/<int:id>', methods=['PUT'])
def put_categoria(id):
    dados = request.get_json() or {}
    try:
        cat = atualizar_categoria(id, nome=dados.get('nome'), ativo=dados.get('ativo'))
        return jsonify(cat.to_dict()), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@categorias_bp.route('/api/categorias/<int:id>', methods=['DELETE'])
def delete_categoria(id):
    try:
        deletar_categoria(id)
        return jsonify({"mensagem": "Categoria excluída"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
