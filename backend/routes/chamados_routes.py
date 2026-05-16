from flask import Blueprint, jsonify, request, send_from_directory, current_app, abort
from utils.auth import login_required, usuario_logado, pode_ver_chamado
from utils.arquivos import salvar_anexo, excluir_anexo
from controllers.chamados_controller import (
    listar_chamados_recentes,
    criar_chamado,
    editar_chamado,
    atualizar_status,
    buscar_chamado_por_id,
    deletar_chamado,
    listar_chamados_por_status,
    listar_chamados_por_usuario,
    buscar_chamados_por_texto,
)
from models.chamado import Chamado

chamados_bp = Blueprint('chamados', __name__)

ALLOWED_EXT = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'txt'}


def _ler_payload():
    """Aceita JSON ou multipart/form-data. Retorna (dados_dict, arquivo_storage_ou_none)."""
    if request.content_type and request.content_type.startswith('multipart/'):
        dados = {k: v for k, v in request.form.items()}
        for chave_int in ('usuario_id', 'categoria_id'):
            if chave_int in dados and dados[chave_int] != '':
                try:
                    dados[chave_int] = int(dados[chave_int])
                except ValueError:
                    pass
            elif chave_int in dados and dados[chave_int] == '':
                dados[chave_int] = None
        arquivo = request.files.get('anexo')
        return dados, arquivo
    return request.get_json() or {}, None


@chamados_bp.route('/api/chamados', methods=['GET'])
@login_required
def get_chamados():
    usuario = usuario_logado()

    if usuario.tipo in ("admin", "secretaria"):
        return jsonify(listar_chamados_recentes()), 200

    return jsonify(listar_chamados_por_usuario(usuario.id)), 200


@chamados_bp.route('/api/chamados', methods=['POST'])
@login_required
def post_chamado():
    anexo_path = None
    anexo_nome = None

    try:
        usuario = usuario_logado()
        dados, arquivo = _ler_payload()

        if arquivo:
            anexo_path, anexo_nome = salvar_anexo(arquivo)

        novo = criar_chamado(
            dados.get('titulo'),
            dados.get('descricao'),
            usuario.id,
            categoria_id=dados.get('categoria_id'),
            anexo_path=anexo_path,
            anexo_nome=anexo_nome,
        )

        return jsonify({
            "mensagem": "Chamado criado com sucesso!",
            "id": novo.id
        }), 201
    
    except ValueError as e:
        excluir_anexo(anexo_path)
        return jsonify({"erro": str(e)}), 400
    
    except Exception as e:
        excluir_anexo(anexo_path)
        return jsonify({"erro": str(e)}), 400

@chamados_bp.route('/api/chamados/<int:id>', methods=['GET'])
@login_required
def get_chamado_id(id):
    try:
        usuario = usuario_logado()
        chamado = Chamado.query.get(id)

        if not chamado:
            return jsonify({"erro": "Chamado não encontrado"}), 404

        if not pode_ver_chamado(usuario, chamado):
            return jsonify({"erro": "Você não tem permissão para visualizar este chamado"}), 403

        return jsonify(buscar_chamado_por_id(id)), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


@chamados_bp.route('/api/chamados/<int:id>', methods=['PUT'])
@login_required
def put_chamado(id):
    novo_anexo_path = None
    novo_anexo_nome = None

    try:
        usuario = usuario_logado()
        dados, arquivo = _ler_payload()

        chamado_atual = Chamado.query.get(id)

        if not chamado_atual:
            return jsonify({"erro": "Chamado não encontrado"}), 404
        
        anexo_antigo = chamado_atual.anexo_path

        if arquivo:
            novo_anexo_path, novo_anexo_nome = salvar_anexo(arquivo)

        chamado = editar_chamado(
            id,
            usuario_id=usuario.id,
            titulo=dados.get('titulo'),
            descricao=dados.get('descricao'),
            categoria_id=dados.get('categoria_id'),
            anexo_path=novo_anexo_path,
            anexo_nome=novo_anexo_nome,
        )

        # Se enviou anexo novo e havia anexo antigo, remove o antigo.
        if novo_anexo_path and anexo_antigo and anexo_antigo != novo_anexo_path:
            excluir_anexo(anexo_antigo)
        
        return jsonify(chamado.to_dict()), 200
    
    except ValueError as e:
        excluir_anexo(novo_anexo_path)
        return jsonify({"erro": str(e)}), 400
    
    except Exception as e:
        excluir_anexo(novo_anexo_path)
        return jsonify({"erro": str(e)}), 400   


@chamados_bp.route('/api/chamados/<int:id>/status', methods=['PUT'])
@login_required
def put_status(id):
    dados = request.get_json() or {}

    try:
        usuario = usuario_logado()

        chamado = atualizar_status(
            id,
            dados.get('status'),
            usuario.id
        )

        return jsonify(chamado), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400


@chamados_bp.route('/api/chamados/<int:id>', methods=['DELETE'])
def delete_chamado(id):
    try:
        deletar_chamado(id)
        return jsonify({"mensagem": "Chamado excluído!"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 404


@chamados_bp.route('/api/chamados/usuario/<int:usuario_id>', methods=['GET'])
def get_por_usuario(usuario_id):
    return jsonify(listar_chamados_por_usuario(usuario_id)), 200


@chamados_bp.route('/api/chamados/busca', methods=['GET'])
def get_busca():
    texto = request.args.get('q', '')
    return jsonify(buscar_chamados_por_texto(texto)), 200


@chamados_bp.route('/api/chamados/<int:id>/anexo', methods=['GET'])
@login_required
def get_anexo(id):
    usuario = usuario_logado()
    chamado = Chamado.query.get(id)

    if not chamado or not chamado.anexo_path:
        abort(404)

    if not pode_ver_chamado(usuario, chamado):
        return jsonify({"erro": "Você não tem permissão para acessar este anexo"}), 403
    
    upload_dir = current_app.config['UPLOAD_FOLDER']

    baixar = request.args.get("download") == "1"

    return send_from_directory(
        upload_dir,
        chamado.anexo_path,
        as_attachment=baixar,
        download_name=chamado.anexo_nome or chamado.anexo_path,
    )