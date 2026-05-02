from models.usuario import Usuario
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

def criar_usuario(nome, email, senha, tipo):
    if not nome or not email or not senha:
        raise ValueError("Nome, email e senha são obrigatórios")
    
    tipos_validos = ["professor", "secretaria", "admin"]

    if tipo not in tipos_validos:
        raise ValueError("Tipo de usuário inválido")
    
    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        raise ValueError("Já existe um usuário com esse email")
    
    senha_hash = generate_password_hash(senha)

    usuario = Usuario(
        nome=nome,
        email=email,
        senha=senha_hash,
        tipo=tipo
    )

    db.session.add(usuario)
    db.session.commit()

    return usuario

def fazer_login(email, senha):
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        raise ValueError("Usuário não encontrado")
    
    if not check_password_hash(usuario.senha, senha):
        raise ValueError("Senha incorreta")
    
    return usuario