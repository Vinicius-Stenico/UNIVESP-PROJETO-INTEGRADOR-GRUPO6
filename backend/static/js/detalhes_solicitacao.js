(async function () {
  const usuario = await AppCommon.requireUsuario();
  if (!usuario) return;

  const ehSecretaria = usuario.tipo === 'secretaria' || usuario.tipo === 'admin';
  const id = document.getElementById('detalhes-root').dataset.chamadoId;

  let chamado = null;

  async function carregar() {
    try {
      chamado = await AppCommon.api('GET', `/api/chamados/${id}`);
      renderChamado();

      const [eventos, comentarios] = await Promise.all([
        AppCommon.api('GET', `/api/chamados/${id}/eventos`),
        AppCommon.api('GET', `/api/chamados/${id}/comentarios`),
      ]);

      renderHistorico(eventos);
      renderComentarios(comentarios);
      montarAcoes();

      const eFinalizado = chamado.status === 'Cancelado' || chamado.status === 'Conclu\u00eddo';
      document.getElementById('d-comentario-wrap').style.display = eFinalizado ? 'none' : '';
    } catch (e) {
      AppCommon.showMessage(document.getElementById('d-erro'), e.message);
    }
  }

  function renderChamado() {
    document.getElementById('d-id').textContent = chamado.id;
    document.getElementById('d-titulo').textContent = chamado.titulo;
    document.getElementById('d-data').innerHTML = `<strong>Data:</strong> ${AppCommon.escapeHtml(AppCommon.fmtDataDia(chamado.data_criacao))}`;

    if (chamado.categoria_nome) {
      document.getElementById('d-categoria').innerHTML = `<strong>Categoria:</strong> ${AppCommon.escapeHtml(chamado.categoria_nome)}`;
    }

    const prioridade = chamado.prioridade || 'Normal';
    document.getElementById('d-prioridade').innerHTML =
      `<strong>Prioridade:</strong> <span class="${AppCommon.classePrioridade(prioridade)}">${AppCommon.escapeHtml(prioridade)}</span>`;

    document.getElementById('d-responsavel').innerHTML =
      `<strong>Respons\u00e1vel:</strong> ${AppCommon.escapeHtml(chamado.responsavel_nome || 'Ainda n\u00e3o assumido')}`;
    document.getElementById('d-status').innerHTML = `<strong>Status:</strong> <span class="tag-status">${AppCommon.escapeHtml(chamado.status)}</span>`;

    if (ehSecretaria) {
      document.getElementById('d-solicitante').innerHTML = `<strong>Solicitante:</strong> ${AppCommon.escapeHtml(chamado.usuario_nome || '-')}`;
    }

    const parsed = AppCommon.parseItensDescricao(chamado.descricao);

    if (parsed.itens) {
      document.getElementById('d-itens-bloco').style.display = '';
      document.getElementById('d-itens-conteudo').textContent = parsed.itens;
    }

    document.getElementById('d-descricao').textContent =
      parsed.texto || (parsed.itens ? '(sem descri\u00e7\u00e3o adicional)' : (chamado.descricao || '(sem descri\u00e7\u00e3o)'));

    if (chamado.tem_anexo) {
      document.getElementById('d-anexo-bloco').style.display = '';

      const linkVisualizar = document.getElementById('d-anexo-link');
      const linkDownload = document.getElementById('d-anexo-download');

      linkVisualizar.href = `/api/chamados/${chamado.id}/anexo`;
      linkDownload.href = `/api/chamados/${chamado.id}/anexo?download=1`;

      document.getElementById('d-anexo-nome').textContent = chamado.anexo_nome || 'arquivo anexado';
    }
  }

  function iconeEvento(tipo) {
    const mapa = {
      criacao: 'bi-pencil-square',
      status: 'bi-arrow-repeat',
      comentario: 'bi-chat-dots',
      edicao: 'bi-pencil',
      anexo: 'bi-paperclip',
      cancelamento: 'bi-x-circle',
      reabertura: 'bi-arrow-counterclockwise',
      atribuicao: 'bi-person-check',
    };

    return mapa[tipo] || 'bi-dot';
  }

  function renderHistorico(eventos) {
    const el = document.getElementById('d-historico');

    if (!eventos.length) {
      el.innerHTML = AppCommon.emptyState('bi-clock-history', 'Sem eventos', 'As movimentações da solicitação aparecerão aqui.');
      return;
    }

    el.innerHTML = eventos.map(e => {
      const tag = e.status_novo
        ? ` <span class="tag-status">${AppCommon.escapeHtml(e.status_novo)}</span>`
        : '';

      return `
        <div class="hist-line">
          <strong><i class="bi ${iconeEvento(e.tipo)}" aria-hidden="true"></i> ${AppCommon.escapeHtml(AppCommon.fmtDataCurta(e.data_criacao))}</strong><br>
          ${AppCommon.escapeHtml(e.descricao)}${tag}
        </div>
      `;
    }).join('');
  }

  function renderComentarios(comentarios) {
    const el = document.getElementById('d-comentarios');

    if (!comentarios.length) {
      el.innerHTML = AppCommon.emptyState('bi-chat-dots', 'Não há comentários', 'Use o campo abaixo para registrar uma observação.');
      return;
    }

    el.innerHTML = comentarios.map(c =>
      `<div class="hist-line"><strong>${AppCommon.escapeHtml(c.usuario_nome || '-')}</strong> - ${AppCommon.escapeHtml(AppCommon.fmtDataCurta(c.data_criacao))}<br>${AppCommon.escapeHtml(c.texto)}</div>`
    ).join('');
  }

  function montarAcoes() {
    const acoes = document.getElementById('d-acoes');
    const info = document.getElementById('d-acoes-info');
    const btnPri = document.getElementById('d-btn-primario');
    const btnCanc = document.getElementById('d-btn-cancelar');

    acoes.style.display = 'none';
    info.textContent = '';
    btnPri.style.display = 'none';
    btnCanc.style.display = 'none';
    btnPri.onclick = null;
    btnCanc.onclick = null;

    const eAtivo = chamado.status === 'Aberto' || chamado.status === 'Em andamento';
    if (!eAtivo) {
      info.textContent = 'Solicitação encerrada. As ações ficam disponíveis apenas enquanto ela está ativa.';
      return;
    }

    const eDono = chamado.usuario_id === usuario.id;

    if (ehSecretaria) {
      if (chamado.status === 'Aberto' && !chamado.responsavel_id) {
        btnPri.textContent = 'Assumir';
        btnPri.onclick = () => assumirChamado();
        btnPri.style.display = '';

      } else if (chamado.status === 'Aberto') {
        btnPri.textContent = 'Iniciar atendimento';
        btnPri.onclick = () => mudarStatus('Em andamento');
        btnPri.style.display = '';

      } else if (chamado.status === 'Em andamento') {
        btnPri.textContent = 'Concluir';
        btnPri.onclick = () => mudarStatus('Conclu\u00eddo');
        btnPri.style.display = '';
      }

      btnCanc.textContent = 'Cancelar solicita\u00e7\u00e3o';
      btnCanc.onclick = () => mudarStatus('Cancelado');
      btnCanc.style.display = '';

      acoes.style.display = '';
    } else if (eDono) {
      btnCanc.textContent = 'Cancelar solicita\u00e7\u00e3o';
      btnCanc.onclick = () => mudarStatus('Cancelado');
      btnCanc.style.display = '';
    } else {
      info.textContent = 'Você pode acompanhar esta solicitação, mas não há ações disponíveis para o seu perfil.';
    }

    if (btnPri.style.display !== 'none' || btnCanc.style.display !== 'none') {
      acoes.style.display = 'flex';
    }
  }

  async function assumirChamado() {
    AppCommon.showMessage(document.getElementById('d-erro'), '');

    try {
      chamado = await AppCommon.api('PUT', `/api/chamados/${id}/assumir`);

      renderChamado();
      montarAcoes();

      const [eventos, comentarios] = await Promise.all([
        AppCommon.api('GET', `/api/chamados/${id}/eventos`),
        AppCommon.api('GET', `/api/chamados/${id}/comentarios`),
      ]);

      renderHistorico(eventos);
      renderComentarios(comentarios);

    } catch (e) {
      AppCommon.showMessage(document.getElementById('d-erro'), e.message);
    }
  }

  async function mudarStatus(novo) {
    AppCommon.showMessage(document.getElementById('d-erro'), '');

    const confirmacoes = {
      'Cancelado': 'Cancelar esta solicita\u00e7\u00e3o? Essa a\u00e7\u00e3o n\u00e3o pode ser desfeita.',
      'Conclu\u00eddo': 'Concluir esta solicita\u00e7\u00e3o?',
    };

    if (confirmacoes[novo] && !confirm(confirmacoes[novo])) return;

    const sucessos = {
      'Cancelado': 'Solicita\u00e7\u00e3o cancelada.',
      'Conclu\u00eddo': 'Solicita\u00e7\u00e3o conclu\u00edda.',
      'Em andamento': 'Solicita\u00e7\u00e3o atualizada para Em andamento.',
    };

    try {
      await AppCommon.api('PUT', `/api/chamados/${id}/status`, { status: novo, usuario_id: usuario.id });
      AppCommon.showMessage(document.getElementById('d-erro'), sucessos[novo] || 'Status atualizado.', 'success');
      window.location.href = '/dashboard';
    } catch (e) {
      AppCommon.showMessage(document.getElementById('d-erro'), e.message);
    }
  }

  document.getElementById('d-add-coment').onclick = async () => {
    AppCommon.showMessage(document.getElementById('d-erro'), '');
    const input = document.getElementById('d-comentario');
    const texto = input.value.trim();
    if (!texto) return;

    try {
      await AppCommon.api('POST', `/api/chamados/${id}/comentarios`, { usuario_id: usuario.id, texto });
      input.value = '';
      carregar();
    } catch (e) {
      AppCommon.showMessage(document.getElementById('d-erro'), e.message);
    }
  };

  document.getElementById('logout').onclick = () => AppCommon.logout('/login');
  document.getElementById('d-btn-voltar').onclick = () => { window.location.href = '/dashboard'; };

  carregar();
})();
