STATUS_ABERTO = "Aberto"
STATUS_EM_ANDAMENTO = "Em andamento"
STATUS_CONCLUIDO = "Concluído"
STATUS_CANCELADO = "Cancelado"

STATUS_VALIDOS = [
    STATUS_ABERTO,
    STATUS_EM_ANDAMENTO,
    STATUS_CONCLUIDO,
    STATUS_CANCELADO,
]


def normalizar_status(status):
    """
    Padroniza o texto do status recebido.

    Aceita variações como:
    - aberto
    - em andamento
    - resolvido
    - concluido
    - cancelado
    """

    if not status:
        raise ValueError("Status é obrigatório")
    
    status_limpo = status.strip().lower()

    mapa = {
        "aberto": STATUS_ABERTO,
        "aberta": STATUS_ABERTO,

        "em andamento": STATUS_EM_ANDAMENTO,
        "andamento": STATUS_EM_ANDAMENTO,

        "resolvido": STATUS_CONCLUIDO,
        "resolvida": STATUS_CONCLUIDO,
        "concluido": STATUS_CONCLUIDO,
        "concluida": STATUS_CONCLUIDO,
        "concluído": STATUS_CONCLUIDO,
        "concluída": STATUS_CONCLUIDO,
        
        "cancelado": STATUS_CANCELADO,
        "cancelada": STATUS_CANCELADO,
    }

    if status_limpo not in mapa:
        raise ValueError("Status inválido")
    
    return mapa[status_limpo]