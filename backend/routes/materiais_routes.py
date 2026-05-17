from flask import Blueprint, jsonify, request
from utils.auth import login_required, admin_required
from controllers.materiais_controller import (
    listar_materiais,
    criar_material,
    atualizar_material,
    deletar_material,
)

materiais_bp = Blueprint('materiais', __name__)


@materiais_bp.route('/api/materiais', methods=['GET'])
@login_required
def get_materiais():
    inclui_inativos = request.args.get('todos') == '1'
    cat = request.args.get('categoria_id', type=int)
    return jsonify(listar_materiais(somente_ativos=not inclui_inativos, categoria_id=cat)), 200


@materiais_bp.route('/api/materiais', methods=['POST'])
@admin_required
def post_material():
    dados = request.get_json() or {}
    try:
        mat = criar_material(
            nome=dados.get('nome'),
            categoria_id=dados.get('categoria_id'),
            unidade=dados.get('unidade'),
        )
        return jsonify(mat.to_dict()), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@materiais_bp.route('/api/materiais/<int:id>', methods=['PUT'])
@admin_required
def put_material(id):
    dados = request.get_json() or {}
    try:
        mat = atualizar_material(
            id,
            nome=dados.get('nome'),
            categoria_id=dados.get('categoria_id'),
            unidade=dados.get('unidade'),
            ativo=dados.get('ativo'),
        )
        return jsonify(mat.to_dict()), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@materiais_bp.route('/api/materiais/<int:id>', methods=['DELETE'])
@admin_required
def delete_material(id):
    try:
        deletar_material(id)
        return jsonify({"mensagem": "Material excluído"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404
