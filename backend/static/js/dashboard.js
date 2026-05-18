document.addEventListener('DOMContentLoaded', async () => {
  const usuario = await AppCommon.requireUsuario();

  if (!usuario) {
    return;
  }

  const ehSecretaria = usuario.tipo === 'secretaria' || usuario.tipo === 'admin';

  const TABS_SECRETARIA = [
    { label: 'Abertas', status: 'Aberto' },
    { label: 'Em andamento', status: 'Em andamento' },
    { label: 'Conclu\u00eddas', status: 'Conclu\u00eddo' },
  ];

  const TABS_PROFESSORA = [
    { label: 'Solicita\u00e7\u00f5es', view: 'lista' },
    { label: 'Nova solicita\u00e7\u00e3o', view: 'nova' },
  ];

  const tabsEl = document.getElementById('tabs');
  const listaEl = document.getElementById('lista');
  const titulo = document.getElementById('titulo-pagina');
  const subtitulo = document.getElementById('subtitulo');
  const adminLink = document.getElementById('admin-link');
  const logoutBtn = document.getElementById('logout');

  if (ehSecretaria) {
    titulo.textContent = 'Painel da Secretaria';
    subtitulo.textContent = 'Solicita\u00e7\u00f5es';
  } else {
    titulo.textContent = 'Minhas Solicita\u00e7\u00f5es';
    subtitulo.textContent = `Ol\u00e1, ${usuario.nome}!`;
  }

  if (usuario.tipo === 'admin') {
    adminLink.style.display = '';
  }

  let tabAtiva = 0;

  function renderTabs() {
    const tabs = ehSecretaria ? TABS_SECRETARIA : TABS_PROFESSORA;

    tabsEl.innerHTML = '';

    tabs.forEach((t, i) => {
      const botao = document.createElement('button');

      botao.className = 'tab-figma' + (i === tabAtiva ? ' active' : '');
      botao.textContent = t.label;

      botao.onclick = () => {
        if (!ehSecretaria && t.view === 'nova') {
          window.location.href = '/nova-solicitacao';
          return;
        }

        tabAtiva = i;
        renderTabs();
        carregar();
      };

      tabsEl.appendChild(botao);
    });
  }

  async function carregar() {
    listaEl.innerHTML = '<div class="empty-msg">Carregando...</div>';

    try {
      let chamados = [];

      if (ehSecretaria) {
        const status = TABS_SECRETARIA[tabAtiva].status;
        const todos = await AppCommon.api('GET', '/api/chamados');

        chamados = todos.filter(c => c.status === status);
      } else {
        chamados = await AppCommon.api('GET', '/api/chamados');
      }

      if (!chamados.length) {
        const texto = ehSecretaria
          ? 'Não há solicitações nesta etapa.'
          : 'Você ainda não possui solicitações cadastradas.';
        listaEl.innerHTML = AppCommon.emptyState('bi-inbox', 'Nenhuma solicitação', texto);
        return;
      }

      listaEl.innerHTML = '';

      if (ehSecretaria) {
        const resumo = document.createElement('div');
        resumo.className = 'painel-resumo';
        resumo.innerHTML = `
          <span>${chamados.length} solicita\u00e7\u00e3o(ões)</span>
          <span>${TABS_SECRETARIA[tabAtiva].label}</span>
        `;
        listaEl.appendChild(resumo);
      }

      chamados.forEach(c => {
        listaEl.appendChild(renderCard(c));
      });

    } catch (e) {
      listaEl.innerHTML = `<div class="empty-msg">Erro: ${AppCommon.escapeHtml(e.message)}</div>`;
    }
  }

  function renderCard(c) {
    const card = document.createElement('div');
    card.className = ehSecretaria ? 'card-figma card-operacional' : 'card-figma';

    const podeEditar = !ehSecretaria && c.status === 'Aberto' && c.usuario_id === usuario.id;

    const labelBotao = (() => {
      if (ehSecretaria) {
        if (c.status === 'Aberto') return 'Atender';
        if (c.status === 'Em andamento') return 'Atualizar';
        return 'Ver';
      }

      return podeEditar ? 'Ver/Editar' : 'Ver';
    })();

    const destino = podeEditar ? `/nova-solicitacao?id=${c.id}` : `/detalhes/${c.id}`;
    const prioridade = c.prioridade || 'Normal';
    const prioridadeHtml = `<span class="${AppCommon.classePrioridade(prioridade)}">${AppCommon.escapeHtml(prioridade)}</span>`;
    const responsavelHtml = `
      <span class="responsavel-info">
        <i class="bi bi-person-badge" aria-hidden="true"></i>
        ${AppCommon.escapeHtml(AppCommon.textoResponsavel(c))}
      </span>
    `;

    const badges = [];

    if (c.tem_anexo) {
      badges.push(`
        <span class="card-badge" title="Possui anexo">
          <i class="bi bi-paperclip" aria-hidden="true"></i>
        </span>
      `);
    }

    if (c.total_comentarios > 0) {
      badges.push(`
        <span class="card-badge" title="${c.total_comentarios} coment\u00e1rio(s)">
          <i class="bi bi-chat-dots-fill" aria-hidden="true"></i> ${c.total_comentarios}
        </span>
      `);
    }

    const badgesHtml = badges.length
      ? `<span class="card-badges">${badges.join('')}</span>`
      : '';

    if (ehSecretaria) {
      card.innerHTML = `
        <div class="operacional-head">
          <span class="lista-tag">#${c.id}</span>
          <span class="operacional-title">${AppCommon.escapeHtml(c.titulo)}</span>
          ${badgesHtml}
        </div>

        <div class="operacional-grid">
          <span><strong>Solicitante</strong>${AppCommon.escapeHtml(c.usuario_nome || '-')}</span>
          <span><strong>Categoria</strong>${AppCommon.escapeHtml(c.categoria_nome || '-')}</span>
          <span><strong>Data</strong>${AppCommon.escapeHtml(AppCommon.fmtDataDia(c.data_criacao))}</span>
        </div>

        <div class="meta-chamado">
          ${prioridadeHtml}
          ${responsavelHtml}
        </div>
      `;
    } else {
      card.innerHTML = `
        <div class="d-flex align-items-baseline gap-2 mb-2">
          <span class="fw-bold">#${c.id}</span>
          <span class="fw-bold flex-grow-1">${AppCommon.escapeHtml(c.titulo)}</span>
          ${badgesHtml}
        </div>

        <div class="d-flex justify-content-between text-muted small">
          <span>${AppCommon.escapeHtml(c.categoria_nome || '-')}</span>
          <span>${AppCommon.escapeHtml(AppCommon.fmtDataDia(c.data_criacao))}</span>
        </div>

        <div class="meta-chamado justify-content-center">
          ${prioridadeHtml}
          ${responsavelHtml}
        </div>

        <div class="text-center mt-2 mb-2">
          <span class="${AppCommon.classeStatus(c.status)}">${AppCommon.escapeHtml(c.status)}</span>
        </div>
      `;
    }

    const wrap = document.createElement('div');
    wrap.className = 'd-flex justify-content-center mt-2';

    const btn = document.createElement('button');
    btn.className = 'btn btn-figma';
    btn.textContent = labelBotao;

    btn.onclick = async () => {
      if (ehSecretaria && c.status === 'Aberto' && !c.responsavel_id) {
        try {
          await AppCommon.api('PUT', `/api/chamados/${c.id}/assumir`);
          await carregar();
        } catch (e) {
          listaEl.innerHTML = `<div class="empty-msg">Erro: ${AppCommon.escapeHtml(e.message)}</div>`;
        }
        return;
      }

      window.location.href = destino;
    };

    wrap.appendChild(btn);
    card.appendChild(wrap);

    return card;
  }

  logoutBtn.onclick = () => AppCommon.logout('/login');

  renderTabs();
  carregar();
});
