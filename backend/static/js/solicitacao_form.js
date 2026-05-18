document.addEventListener('DOMContentLoaded', async () => {
  const usuario = await AppCommon.requireUsuario();

  if (!usuario) {
    return;
  }

  document.getElementById('ola').textContent = `Ol\u00e1, ${usuario.nome}!`;

  const editandoId = new URLSearchParams(window.location.search).get('id');

  const tabForm = document.getElementById('tab-form');
  const tabLista = document.getElementById('tab-lista');
  const btnCancelar = document.getElementById('cancelar');
  const btnLogout = document.getElementById('logout');
  const arquivoInput = document.getElementById('arquivo');
  const nomeArquivo = document.getElementById('nome-arquivo');
  const selCategoria = document.getElementById('categoria');
  const selItens = document.getElementById('itens');
  const form = document.getElementById('form-nova');
  const erro = document.getElementById('erro');
  const enviar = document.getElementById('enviar');
  const tituloInput = document.getElementById('titulo');
  const descricaoInput = document.getElementById('descricao');
  const prioridadeSelect = document.getElementById('prioridade');
  const previewTitulo = document.getElementById('preview-titulo');
  const previewMeta = document.getElementById('preview-meta');
  const previewItem = document.getElementById('preview-item');

  tabForm.textContent = editandoId ? 'Editar solicita\u00e7\u00e3o' : 'Nova solicita\u00e7\u00e3o';

  tabLista.onclick = () => {
    window.location.href = '/dashboard';
  };

  btnCancelar.onclick = () => {
    window.location.href = '/dashboard';
  };

  btnLogout.onclick = () => AppCommon.logout('/login');

  arquivoInput.addEventListener('change', (e) => {
    const f = e.target.files[0];
    nomeArquivo.textContent = f ? f.name : 'Nenhum arquivo';
  });

  function itemSelecionadoTexto() {
    const itemOpt = selItens.selectedOptions[0];

    if (!itemOpt || !itemOpt.value) {
      return '';
    }

    return itemOpt.dataset.nome + (itemOpt.dataset.unidade ? ` (${itemOpt.dataset.unidade})` : '');
  }

  function atualizarPreview() {
    const titulo = tituloInput.value.trim();
    const categoria = selCategoria.selectedOptions[0]?.textContent || '';
    const item = itemSelecionadoTexto();
    const prioridade = prioridadeSelect.value || 'Normal';

    previewTitulo.textContent = titulo || 'Título ainda não informado';
    previewMeta.textContent = `${categoria && selCategoria.value ? categoria : 'Sem categoria'} - Prioridade ${prioridade}`;
    previewItem.textContent = item ? `Item: ${item}` : 'Nenhum item selecionado';
  }

  async function carregarCategorias() {
    try {
      const cats = await AppCommon.api('GET', '/api/categorias');

      cats.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.nome;
        selCategoria.appendChild(opt);
      });

    } catch (e) {
      console.error('Erro ao carregar categorias:', e);
    }
  }

  async function carregarMateriais(catId) {
    selItens.innerHTML = '<option value="">Selecione o(s) item(ns)</option>';

    const url = catId ? `/api/materiais?categoria_id=${catId}` : '/api/materiais';

    try {
      const mats = await AppCommon.api('GET', url);

      mats.forEach(m => {
        const opt = document.createElement('option');

        opt.value = m.id;
        opt.textContent = m.unidade ? `${m.nome} (${m.unidade})` : m.nome;
        opt.dataset.nome = m.nome;
        opt.dataset.unidade = m.unidade || '';

        selItens.appendChild(opt);
      });

    } catch (e) {
      console.error('Erro ao carregar materiais:', e);
    }
  }

  selCategoria.addEventListener('change', () => {
    carregarMateriais(selCategoria.value || null);
    atualizarPreview();
  });

  tituloInput.addEventListener('input', atualizarPreview);
  selItens.addEventListener('change', atualizarPreview);
  prioridadeSelect.addEventListener('change', atualizarPreview);
  descricaoInput.addEventListener('input', atualizarPreview);

  async function carregarChamadoExistente() {
    if (!editandoId) {
      return;
    }

    try {
      const c = await AppCommon.api('GET', `/api/chamados/${editandoId}`);

      const ehDono = c.usuario_id === usuario.id;
      const ehSecretariaOuAdmin = usuario.tipo === 'admin' || usuario.tipo === 'secretaria';

      if (!ehDono && !ehSecretariaOuAdmin) {
        AppCommon.showMessage(erro, 'Você não pode editar essa solicitação.');
        window.location.href = '/dashboard';
        return;
      }

      if (c.status !== 'Aberto' && !ehSecretariaOuAdmin) {
        AppCommon.showMessage(erro, 'Esta solicitação não pode mais ser editada.');
        window.location.href = `/detalhes/${editandoId}`;
        return;
      }

      document.getElementById('titulo').value = c.titulo;

      if (c.categoria_id) {
        selCategoria.value = String(c.categoria_id);
        await carregarMateriais(c.categoria_id);
      } else {
        await carregarMateriais(null);
      }

      document.getElementById('prioridade').value = c.prioridade || 'Normal';

      const parsed = AppCommon.parseItensDescricao(c.descricao);

      document.getElementById('descricao').value = parsed.texto;

      if (parsed.itens) {
        Array.from(selItens.options).forEach(opt => {
          const txt = opt.dataset.nome
            ? (opt.dataset.unidade ? `${opt.dataset.nome} (${opt.dataset.unidade})` : opt.dataset.nome)
            : '';

          if (txt === parsed.itens) {
            selItens.value = opt.value;
          }
        });
      }

      atualizarPreview();

      if (c.tem_anexo) {
        document.getElementById('anexo-atual').style.display = '';

        const link = document.getElementById('anexo-link');
        link.href = `/api/chamados/${c.id}/anexo`;
        link.textContent = c.anexo_nome || 'baixar anexo';
      }

      const ativo = c.status === 'Aberto' || c.status === 'Em andamento';
      const cancelarSolBtn = document.getElementById('cancelar-sol');

      if (ativo) {
        cancelarSolBtn.style.display = '';

        cancelarSolBtn.onclick = async () => {
          if (!confirm('Cancelar esta solicita\u00e7\u00e3o? Essa a\u00e7\u00e3o n\u00e3o pode ser desfeita.')) {
            return;
          }

          try {
            await AppCommon.api('PUT', `/api/chamados/${c.id}/status`, {
              status: 'Cancelado'
            });

            AppCommon.showMessage(erro, 'Solicitação cancelada.', 'success');
            window.location.href = '/dashboard';

          } catch (e) {
            AppCommon.showMessage(erro, e.message);
          }
        };
      }

    } catch (e) {
      AppCommon.showMessage(erro, e.message);
    }
  }

  async function init() {
    await carregarCategorias();

    if (!editandoId) {
      await carregarMateriais(null);
    }

    await carregarChamadoExistente();
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    AppCommon.showMessage(erro, '');
    enviar.disabled = true;

    const titulo = document.getElementById('titulo').value.trim();
    const categoriaId = parseInt(selCategoria.value) || '';
    const itemNome = itemSelecionadoTexto();
    const descBase = document.getElementById('descricao').value.trim();

    const partes = [];

    if (itemNome) {
      partes.push(`Item: ${itemNome}`);
    }

    if (descBase) {
      partes.push(descBase);
    }

    const descricao = partes.join('\n') || '(sem descri\u00e7\u00e3o)';

    const fd = new FormData();

    fd.append('titulo', titulo);
    fd.append('descricao', descricao);
    fd.append('categoria_id', selCategoria.value || '');
    fd.append('prioridade', document.getElementById('prioridade').value || 'Normal');
    
    if (categoriaId) {
      fd.append('categoria_id', categoriaId);
    }

    const arquivo = arquivoInput.files[0];

    if (arquivo) {
      fd.append('anexo', arquivo);
    }

    try {
      const url = editandoId ? `/api/chamados/${editandoId}` : '/api/chamados';
      const method = editandoId ? 'PUT' : 'POST';

      const r = await fetch(url, {
        method,
        body: fd,
        credentials: 'same-origin'
      });

      const data = await r.json();

      if (!r.ok) {
        throw new Error(data.erro || 'Erro');
      }

      window.location.href = editandoId ? `/detalhes/${editandoId}` : '/dashboard';

    } catch (e) {
      AppCommon.showMessage(erro, e.message);
      enviar.disabled = false;
    }
  });

  init();
  atualizarPreview();
});
