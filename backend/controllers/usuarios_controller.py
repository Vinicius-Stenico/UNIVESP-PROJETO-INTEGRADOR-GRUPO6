from models.usuario import Usuario
from database import db
from werkzeug.security import generate_password_hash, check_password_hash


TIPOS_VALIDOS = ["professor", "secretaria", "admin"]


def listar_usuarios(somente_ativos=True):
    q = Usuario.query
    if somente_ativos:
        q = q.filter_by(ativo=True)
    return [u.to_dict() for u in q.order_by(Usuario.nome).all()]


def obter_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        raise ValueError("Usuário não encontrado")
    return usuario


def criar_usuario(nome, email, senha, tipo):
    if not nome or not email or not senha:
        raise ValueError("Nome, email e senha são obrigatórios")

    if tipo not in TIPOS_VALIDOS:
        raise ValueError("Tipo de usuário inválido")

    if Usuario.query.filter_by(email=email).first():
        raise ValueError("Já existe um usuário com esse email")

    usuario = Usuario(
        nome=nome.strip(),
        email=email.strip(),
        senha=generate_password_hash(senha),
        tipo=tipo,
    )

    db.session.add(usuario)
    db.session.commit()

    return usuario


def atualizar_usuario(id, nome=None, email=None, tipo=None, senha=None, ativo=None):
    usuario = obter_usuario(id)

    if nome is not None:
        nome = nome.strip()
        if not nome:
            raise ValueError("Nome inválido")
        usuario.nome = nome

    if email is not None:
        email = email.strip()
        if not email:
            raise ValueError("Email inválido")
        existente = Usuario.query.filter_by(email=email).first()
        if existente and existente.id != id:
            raise ValueError("Já existe um usuário com esse email")
        usuario.email = email

    if tipo is not None:
        if tipo not in TIPOS_VALIDOS:
            raise ValueError("Tipo de usuário inválido")
        usuario.tipo = tipo

    if senha:
        usuario.senha = generate_password_hash(senha)

    if ativo is not None:
        usuario.ativo = bool(ativo)

    db.session.commit()
    return usuario


def fazer_login(email, senha):
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        raise ValueError("Usuário não encontrado")

    if not usuario.ativo:
        raise ValueError("Usuário inativo")

    if not check_password_hash(usuario.senha, senha):
        raise ValueError("Senha incorreta")

    return usuario
