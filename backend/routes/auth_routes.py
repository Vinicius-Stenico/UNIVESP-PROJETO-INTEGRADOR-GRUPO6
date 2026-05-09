from flask import Blueprint, jsonify, request
from controllers.usuarios_controller import fazer_login, criar_usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    try:
        usuario = fazer_login(email, senha)
        return jsonify({
            "mensagem": "Login realizado!",
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "tipo": usuario.tipo
            }
        }), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 401

@auth_bp.route('/api/auth/cadastro', methods=['POST'])
def post_cadastro():
    dados = request.get_json()
    try:
        novo_usuario = criar_usuario(
            nome=dados.get('nome'),
            email=dados.get('email'),
            senha=dados.get('senha'),
            tipo=dados.get('tipo')
        )
        return jsonify({"mensagem": "Usuário cadastrado com sucesso!", "id": novo_usuario.id}), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400