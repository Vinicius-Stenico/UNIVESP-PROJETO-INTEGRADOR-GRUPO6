window.AppCommon = (function () {
  function getUsuario() {
    try { return JSON.parse(sessionStorage.getItem('usuario') || 'null'); }
    catch (e) { return null; }
  }
  function setUsuario(u) {
    sessionStorage.setItem('usuario', JSON.stringify(u));
  }
  async function logout(redirect) {
    try {
      await fetch('/api/logout', { method: 'POST' });
    } catch (e) {
      console.warn("Erro ao encerrar sessão no backend:", e)
    }

    sessionStorage.removeItem('usuario');
    window.location.href = redirect || '/login';
  }
  function requireUsuario(redirect) {
    const u = getUsuario();
    if (!u) { window.location.href = redirect || '/login'; }
    return u;
  }
  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[c]));
  }
  async function api(method, url, body) {
    const opt = { method, headers: { 'Content-Type': 'application/json' } };
    if (body !== undefined) opt.body = JSON.stringify(body);
    const r = await fetch(url, opt);
    const data = r.status === 204 ? null : await r.json();
    if (!r.ok) throw new Error((data && data.erro) || ('HTTP ' + r.status));
    return data;
  }
  function fmtDataCurta(dt) {
    if (!dt) return '';
    const m = String(dt).match(/^(\d{2})\/(\d{2})\/\d{4}\s+(\d{2}:\d{2})$/);
    return m ? `${m[1]}/${m[2]} - ${m[3]}` : dt;
  }
  return { getUsuario, setUsuario, logout, requireUsuario, escapeHtml, api, fmtDataCurta };
})();
