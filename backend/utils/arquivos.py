from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename

EXTENSOES_PERMITIDAS = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "txt",
}

def obter_pasta_uploads():
    """
    Retorna a pasta de uploads configurada no Flask.
    Cria a pasta se ela ainda não existir.
    """
    pasta = Path(current_app.config["UPLOAD_FOLDER"])
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta

def extensao_permitida(nome_arquivo):
    """
    Verifica se o arquivo possui uma extensão permitida.
    """
    if not nome_arquivo or "." not in nome_arquivo:
        return False
    
    extensao = nome_arquivo.rsplit(".", 1)[1].lower()
    return extensao in EXTENSOES_PERMITIDAS

def salvar_anexo(file_storage):
    """
    Salva um anexo com nome interno seguro.

    Retorna:
    - Nome salvo no servidor
    - Nome original do arquivo
    """
    if not file_storage or not file_storage.filename:
        return None, None
    
    nome_original = file_storage.filename

    if not extensao_permitida(nome_original):
        extensoes = ", ".join(sorted(EXTENSOES_PERMITIDAS))
        raise ValueError(f"Tipo de arquivo não permitido. Aceitos: {extensoes}")
    
    nome_seguro = secure_filename(nome_original)

    if not nome_seguro:
        raise ValueError("Nome de arquivo inválido")
    
    extensao = nome_seguro.rsplit(".", 1)[1].lower()
    
    # Nome interno aleatório, para evitar conflito e proteger o nome real no servidor.
    nome_salvo = f"{uuid4().hex}.{extensao}"

    caminho = obter_pasta_uploads() / nome_salvo
    file_storage.save(caminho)

    return nome_salvo, nome_original

def excluir_anexo(nome_salvo):
    """
    Remove um arquivo salvo, caso exista.

    Usado para evitar arquivos orfãos quando:
    - criação do chamado dá erro depois do upload;
    - usuário substitui um anexo antigo por outro.
    """
    if not nome_salvo:
        return
    
    caminho = obter_pasta_uploads() / nome_salvo

    try:
        caminho.unlink(missing_ok=True)
    except OSError:
        pass