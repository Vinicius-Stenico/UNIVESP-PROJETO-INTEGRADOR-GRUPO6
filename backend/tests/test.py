from app import app
from controllers.usuarios_controller import (
    criar_usuario,
    fazer_login
)
from controllers.chamados_controller import (
    criar_chamado,
    listar_chamados,
    atualizar_status,
    deletar_chamado,
    deletar_todos,
    listar_chamados_por_status,
    listar_chamados_por_usuario,
    listar_chamados_recentes,
    buscar_chamado_por_id,
    buscar_chamados_por_texto
)
with app.app_context():

    # Criar ou logar professor
    try:
        professor = criar_usuario("João", "joao@email.com", "123456", "professor")
    except ValueError:
        professor = fazer_login("joao@email.com", "123456")

    # Criar ou logar secretaria
    try:
        secretaria = criar_usuario("Maria", "maria@email.com", "123456", "secretaria")
    except ValueError:
        secretaria = fazer_login("maria@email.com", "123456")

    # Criar chamado com professor
    chamado = criar_chamado(
        "Computador não liga",
        "Sala 3",
        professor.id
    )

    print("Chamado criado:", chamado.titulo)
    print("Criado por:", chamado.usuario.nome)

    # Secretaria atualiza o status
    resultado = atualizar_status(
        chamado.id,
        "Em andamento",
        secretaria.id
    )

    print("Status atualizado:")
    print(resultado)
