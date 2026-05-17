from functools import wraps
from flask import session, jsonify
from models.usuario import Usuario

def usuario_logado():
    """
    Retorna o usuário atualmente logado com base na sessão.
    """
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return None
    
    return Usuario.query.get(usuario_id)


def login_required(func):
    """
    Bloqueia acesso se não houver usuário logado.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        usuario = usuario_logado()

        if not usuario:
            return jsonify({"erro": "Usuário não autenticado"}), 401
        
        return func(*args, **kwargs)
    
    return wrapper

def admin_required(func):
    """
    Permite acesso apenas para usuário admin.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        usuario = usuario_logado()

        if not usuario:
            return jsonify({"erro": "Usuário não autenticado"}), 401
        
        if usuario.tipo != "admin":
            return jsonify({"erro": "Acesso restrito ao administrador"}), 403
        
        return func(*args, **kwargs)
    
    return wrapper

def secretaria_ou_admin_required(func):
    """
    Permite acesso apenas para secretaria ou admin
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        usuario = usuario_logado()

        if not usuario:
            return jsonify({"erro": "Usuário não autenticado"}), 401
        
        if usuario.tipo not in ("secretaria", "admin"):
            return jsonify({"erro": "Acesso restrito à secretaria/admin"}), 403
        
        return func(*args, **kwargs)
    
    return wrapper

def pode_ver_chamado(usuario, chamado):
    """
    Regra para visualizar chamado:
    - admin vê tudo
    - secretaria vê tudo
    - professor vê apenas os próprios chamados
    """
    if not usuario or not chamado:
        return False
    
    if usuario.tipo in ("admin", "secretaria"):
        return True
    
    return chamado.usuario_id == usuario.id