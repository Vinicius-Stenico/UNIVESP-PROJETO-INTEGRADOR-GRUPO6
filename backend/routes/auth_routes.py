from flask import Blueprint, jsonify, request, session
from controllers.usuarios_controller import fazer_login, criar_usuario
from utils.auth import login_required, usuario_logado

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json() or {}

    email = dados.get('email')
    senha = dados.get('senha')

    try:
        usuario = fazer_login(email, senha)
        
        session["usuario_id"] = usuario.id

        return jsonify(usuario.to_dict()), 200
    
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensagem": "Logout realizado com sucesso"}), 200


@auth_bp.route("/api/me", methods=["GET"])
@login_required
def me():
    usuario = usuario_logado()
    return jsonify(usuario.to_dict()), 200


@auth_bp.route("/api/usuarios", methods=["POST"])
def post_usuario():
    dados = request.get_json() or {}

    try:
        usuario = criar_usuario(
            nome=dados.get("nome"),
            email=dados.get("email"),
            senha=dados.get("senha"),
            tipo=dados.get("tipo"),
        )
        return jsonify(usuario.to_dict()), 201
    
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
