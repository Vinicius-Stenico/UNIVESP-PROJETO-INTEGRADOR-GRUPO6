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

PRIORIDADE_BAIXA = "Baixa"
PRIORIDADE_NORMAL = "Normal"
PRIORIDADE_ALTA = "Alta"
PRIORIDADE_URGENTE = "Urgente"

PRIORIDADES_VALIDAS = [
    PRIORIDADE_BAIXA,
    PRIORIDADE_NORMAL,
    PRIORIDADE_ALTA,
    PRIORIDADE_URGENTE,
]

def normalizar_prioridade(prioridade):
    """
    Padroniza a prioridade recebida.
    Se nada for enviado, usa Normal.
    """

    if not prioridade:
        return PRIORIDADE_NORMAL
    
    prioridade_limpa = prioridade.strip().lower()

    mapa = {
        "baixa": PRIORIDADE_BAIXA,
        "normal": PRIORIDADE_NORMAL,
        "media": PRIORIDADE_NORMAL,
        "média": PRIORIDADE_NORMAL,
        "alta": PRIORIDADE_ALTA,
        "urgente": PRIORIDADE_URGENTE,
    }

    if prioridade_limpa not in mapa:
        raise ValueError("Prioridade inválida")
    
    return mapa[prioridade_limpa]