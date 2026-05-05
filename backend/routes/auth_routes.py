from flask import Blueprint, jsonify, request
from backend.controllers.usuarios_controller import fazer_login

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