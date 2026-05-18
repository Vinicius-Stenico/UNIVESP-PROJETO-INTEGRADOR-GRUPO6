async function iniciarAdmin() {
  const erroEl = document.getElementById('erro');
  const usuario = await AppCommon.requireUsuario();

  if (!usuario) {
    return;
  }

  if (usuario.tipo !== 'admin') {
    AppCommon.showMessage(erroEl, 'Acesso restrito ao administrador.');
    window.location.href = '/dashboard';
    return;
  }

  document.getElementById('subtitulo').textContent = `Ol\u00e1, ${usuario.nome}!`;
  document.getElementById('logout').onclick = () => AppCommon.logout('/login');

  let abaAtiva = 'categorias';

  document.querySelectorAll('.tab-figma').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('.tab-figma').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      abaAtiva = b.dataset.tab;
      renderAba();
    };
  });

  async function renderAba() {
    AppCommon.showMessage(erroEl, '');

    const conteudo = document.getElementById('conteudo');
    conteudo.innerHTML = '<div class="empty-msg">Carregando...</div>';

    try {
      if (abaAtiva === 'categorias') {
        await renderCategorias(conteudo);
      } else if (abaAtiva === 'materiais') {
        await renderMateriais(conteudo);
      } else if (abaAtiva === 'eventos') {
        await renderEventos(conteudo);
      } else if (abaAtiva === 'comentarios') {
        await renderComentarios(conteudo);
      }
    } catch (e) {
      AppCommon.showMessage(erroEl, e.message);
      conteudo.innerHTML = '';
    }
  }

  async function renderCategorias(root) {
    const cats = await AppCommon.api('GET', '/api/categorias?todas=1');

    root.innerHTML = `
      <div class="card-figma">
        <h6 class="text-secondary">Nova categoria</h6>
        <form id="cat-form" class="d-flex gap-2 align-items-center flex-wrap">
          <label class="visually-hidden" for="cat-nome">Nome da categoria</label>
          <input class="form-control rounded-pill flex-grow-1" id="cat-nome" placeholder="Nome" required style="min-width:120px;">
          <button type="submit" class="btn btn-figma btn-sm">Salvar</button>
        </form>
      </div>

      <div class="card-figma">
        <h6 class="text-secondary">Categorias (${cats.length})</h6>
        ${cats.map(c => `
          <div class="d-flex align-items-center justify-content-between border-bottom py-2 small">
            <div>
              <span class="fw-bold">#${c.id}</span> ${AppCommon.escapeHtml(c.nome)}
              <span class="ms-2 ${c.ativo ? 'text-success' : 'text-muted'}">
                ${c.ativo ? 'Ativa' : 'Inativa'}
              </span>
            </div>

            <div class="acoes-vert">
              <button class="btn-link-mini" data-act="toggle" data-id="${c.id}" data-ativo="${!c.ativo}">
                ${c.ativo ? 'Desativar' : 'Reativar'}
              </button>
              <button class="btn-link-mini danger" data-act="del" data-id="${c.id}">
                Desativar
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    document.getElementById('cat-form').onsubmit = async (e) => {
      e.preventDefault();

      try {
        await AppCommon.api('POST', '/api/categorias', {
          nome: document.getElementById('cat-nome').value
        });

        renderAba();

      } catch (er) {
        AppCommon.showMessage(erroEl, er.message);
      }
    };

    root.querySelectorAll('button[data-act]').forEach(b => {
      b.onclick = async () => {
        try {
          if (b.dataset.act === 'toggle') {
            await AppCommon.api('PUT', `/api/categorias/${b.dataset.id}`, {
              ativo: b.dataset.ativo === 'true'
            });
          } else if (b.dataset.act === 'del') {
            if (!confirm('Desativar categoria?')) {
              return;
            }

            await AppCommon.api('DELETE', `/api/categorias/${b.dataset.id}`);
          }

          renderAba();

        } catch (er) {
          AppCommon.showMessage(erroEl, er.message);
        }
      };
    });
  }

  async function renderMateriais(root) {
    const [mats, cats] = await Promise.all([
      AppCommon.api('GET', '/api/materiais?todos=1'),
      AppCommon.api('GET', '/api/categorias'),
    ]);

    const opcoes = cats.map(c => `
      <option value="${c.id}">${AppCommon.escapeHtml(c.nome)}</option>
    `).join('');

    root.innerHTML = `
      <div class="card-figma">
        <h6 class="text-secondary">Novo material</h6>

        <form id="mat-form" class="d-flex flex-column gap-2">
          <label class="visually-hidden" for="mat-nome">Nome do material</label>
          <input class="form-control rounded-pill" id="mat-nome" placeholder="Nome do material" required>

          <label class="visually-hidden" for="mat-cat">Categoria do material</label>
          <select class="form-select rounded-pill" id="mat-cat">
            <option value="">Sem categoria</option>
            ${opcoes}
          </select>

          <label class="visually-hidden" for="mat-unid">Unidade do material</label>
          <input class="form-control rounded-pill" id="mat-unid" placeholder="Unidade (ex: un, cx)">

          <button type="submit" class="btn btn-figma btn-sm align-self-end">
            Salvar
          </button>
        </form>
      </div>

      <div class="card-figma">
        <h6 class="text-secondary">Materiais (${mats.length})</h6>

        ${mats.map(m => `
          <div class="d-flex align-items-center justify-content-between border-bottom py-2 small">
            <div class="me-2">
              <div>
                <span class="fw-bold">#${m.id}</span>
                ${AppCommon.escapeHtml(m.nome)}
                ${m.unidade ? `<span class="text-muted">(${AppCommon.escapeHtml(m.unidade)})</span>` : ''}
              </div>

              <div class="text-muted" style="font-size:0.78rem;">
                ${AppCommon.escapeHtml(m.categoria_nome || '-')} -
                ${m.ativo ? '<span class="text-success">Ativo</span>' : '<span class="text-muted">Inativo</span>'}
              </div>
            </div>

            <div class="acoes-vert">
              <button class="btn-link-mini" data-act="toggle" data-id="${m.id}" data-ativo="${!m.ativo}">
                ${m.ativo ? 'Desativar' : 'Reativar'}
              </button>

              <button class="btn-link-mini danger" data-act="del" data-id="${m.id}">
                Desativar
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    document.getElementById('mat-form').onsubmit = async (e) => {
      e.preventDefault();

      try {
        await AppCommon.api('POST', '/api/materiais', {
          nome: document.getElementById('mat-nome').value,
          categoria_id: parseInt(document.getElementById('mat-cat').value) || null,
          unidade: document.getElementById('mat-unid').value || null,
        });

        renderAba();

      } catch (er) {
        AppCommon.showMessage(erroEl, er.message);
      }
    };

    root.querySelectorAll('button[data-act]').forEach(b => {
      b.onclick = async () => {
        try {
          if (b.dataset.act === 'toggle') {
            await AppCommon.api('PUT', `/api/materiais/${b.dataset.id}`, {
              ativo: b.dataset.ativo === 'true'
            });
          } else if (b.dataset.act === 'del') {
            if (!confirm('Desativar material?')) {
              return;
            }

            await AppCommon.api('DELETE', `/api/materiais/${b.dataset.id}`);
          }

          renderAba();

        } catch (er) {
          AppCommon.showMessage(erroEl, er.message);
        }
      };
    });
  }

  async function renderEventos(root) {
    const eventos = await AppCommon.api('GET', '/api/eventos?limite=200');

    if (!eventos.length) {
      root.innerHTML = AppCommon.emptyState('bi-clock-history', 'Nenhum evento', 'O histórico aparecerá aqui quando houver movimentações.');
      return;
    }

    root.innerHTML = `
      <div class="card-figma">
        <h6 class="text-secondary">Eventos (${eventos.length})</h6>

        ${eventos.map(e => `
          <div class="lista-item">
            <div class="lista-meta">
              <span class="lista-tag">#${e.chamado_id}</span>
              <span class="lista-tipo">${AppCommon.escapeHtml(e.tipo)}</span>
              ${e.status_novo ? `<span class="lista-status">${AppCommon.escapeHtml(e.status_novo)}</span>` : ''}
              <span class="lista-data">${AppCommon.escapeHtml(e.data_criacao)}</span>
            </div>

            <div class="lista-corpo">
              ${AppCommon.escapeHtml(e.descricao)}
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  async function renderComentarios(root) {
    const comentarios = await AppCommon.api('GET', '/api/comentarios');

    if (!comentarios.length) {
      root.innerHTML = AppCommon.emptyState('bi-chat-dots', 'Nenhum comentário', 'Comentários das solicitações aparecerão aqui.');
      return;
    }

    root.innerHTML = `
      <div class="card-figma">
        <h6 class="text-secondary">Coment\u00e1rios (${comentarios.length})</h6>

        ${comentarios.map(c => `
          <div class="lista-item">
            <div class="lista-meta">
              <span class="lista-tag">#${c.chamado_id}</span>
              <strong>${AppCommon.escapeHtml(c.usuario_nome || '-')}</strong>
              <span class="lista-data">${AppCommon.escapeHtml(c.data_criacao)}</span>
            </div>

            <div class="lista-corpo">
              ${AppCommon.escapeHtml(c.texto)}
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  renderAba();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', iniciarAdmin);
} else {
  iniciarAdmin();
}
