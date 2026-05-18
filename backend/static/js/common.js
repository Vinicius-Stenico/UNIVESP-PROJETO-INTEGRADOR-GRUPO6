window.AppCommon = (function () {
  function getUsuario() {
    try {
      return JSON.parse(sessionStorage.getItem('usuario') || 'null');
    } catch (e) {
      return null;
    }
  }

  function setUsuario(u) {
    sessionStorage.setItem('usuario', JSON.stringify(u));
  }

  async function buscarUsuarioSessao() {
    try {
      const r = await fetch('/api/me', {
        method: 'GET',
        credentials: 'same-origin'
      });

      if (!r.ok) {
        return null;
      }

      const usuario = await r.json();
      setUsuario(usuario);
      return usuario;

    } catch (e) {
      console.warn('Erro ao buscar usuário da sessão:', e);
      return null;
    }
  }

  async function logout(redirect) {
    try {
      await fetch('/api/logout', {
        method: 'POST',
        credentials: 'same-origin'
      });
    } catch (e) {
      console.warn("Erro ao encerrar sessão no backend:", e);
    }

    sessionStorage.removeItem('usuario');
    window.location.href = redirect || '/login';
  }

  async function requireUsuario(redirect) {
    let u = getUsuario();

    if (!u) {
      u = await buscarUsuarioSessao();
    }

    if (!u) {
      window.location.href = redirect || '/login';
      return null;
    }

    return u;
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[c]));
  }

  async function api(method, url, body) {
    const opt = {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'same-origin'
    };

    if (body !== undefined) {
      opt.body = JSON.stringify(body);
    }

    const r = await fetch(url, opt);

    let data = null;

    try {
      data = r.status === 204 ? null : await r.json();
    } catch (e) {
      data = null;
    }

    if (!r.ok) {
      throw new Error((data && data.erro) || ('HTTP ' + r.status));
    }

    if (url === '/api/login' && data) {
      setUsuario(data);
    }

    return data;
  }

  function fmtDataCurta(dt) {
    if (!dt) return '';
    const m = String(dt).match(/^(\d{2})\/(\d{2})\/\d{4}\s+(\d{2}:\d{2})$/);
    return m ? `${m[1]}/${m[2]} - ${m[3]}` : dt;
  }

  function fmtDataDia(dt) {
    if (!dt) return '';
    return String(dt).split(' ')[0] || dt;
  }

  function classePrioridade(prioridade) {
    if (prioridade === 'Urgente') return 'prioridade-pill prioridade-urgente';
    if (prioridade === 'Alta') return 'prioridade-pill prioridade-alta';
    if (prioridade === 'Baixa') return 'prioridade-pill prioridade-baixa';
    return 'prioridade-pill prioridade-normal';
  }

  function classeStatus(status) {
    if (status === 'Cancelado') return 'status-pill status-cancelado';
    if (status === 'Concluído') return 'status-pill status-resolvido';
    if (status === 'Em andamento') return 'status-pill status-andamento';
    return 'status-pill status-aberto';
  }

  function textoResponsavel(chamado) {
    return chamado.responsavel_nome
      ? chamado.responsavel_nome
      : 'Sem responsável';
  }

  function parseItensDescricao(desc) {
    const out = { itens: null, texto: '' };
    if (!desc) return out;

    const restante = [];

    String(desc).split('\n').forEach(linha => {
      const m = linha.match(/^Itens?:\s*(.+)$/i);

      if (m && !out.itens) {
        out.itens = m[1].trim();
      } else {
        restante.push(linha);
      }
    });

    out.texto = restante.join('\n').trim();
    return out;
  }

  function showMessage(el, message, type) {
    if (!el) return;

    el.textContent = message || '';
    el.classList.remove('success-msg', 'error-msg', 'info-msg');

    if (!message) {
      return;
    }

    if (type === 'success') {
      el.classList.add('success-msg');
    } else if (type === 'info') {
      el.classList.add('info-msg');
    } else {
      el.classList.add('error-msg');
    }
  }

  function emptyState(icon, title, text) {
    const safeIcon = escapeHtml(icon || 'bi-info-circle');
    return `
      <div class="empty-state">
        <i class="bi ${safeIcon}" aria-hidden="true"></i>
        <strong>${escapeHtml(title || '')}</strong>
        ${text ? `<span>${escapeHtml(text)}</span>` : ''}
      </div>
    `;
  }

  return {
    getUsuario,
    setUsuario,
    buscarUsuarioSessao,
    logout,
    requireUsuario,
    escapeHtml,
    api,
    fmtDataCurta,
    fmtDataDia,
    classePrioridade,
    classeStatus,
    textoResponsavel,
    parseItensDescricao,
    showMessage,
    emptyState
  };
})();
