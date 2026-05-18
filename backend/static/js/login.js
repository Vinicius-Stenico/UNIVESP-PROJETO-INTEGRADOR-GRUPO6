if (AppCommon.getUsuario()) {
  window.location.href = '/dashboard';
}

const form = document.getElementById('login-form');
const btn = document.getElementById('entrar-btn');
const erro = document.getElementById('erro');

document.querySelectorAll('[data-mvp-msg]').forEach(btnMsg => {
  btnMsg.addEventListener('click', () => {
    AppCommon.showMessage(erro, 'Funcionalidade não implementada no MVP.', 'info');
  });
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  AppCommon.showMessage(erro, '');
  btn.disabled = true;
  btn.textContent = 'Entrando...';

  try {
    const data = await AppCommon.api('POST', '/api/login', {
      email: document.getElementById('email').value.trim(),
      senha: document.getElementById('senha').value,
    });

    AppCommon.setUsuario(data);
    window.location.href = '/dashboard';
  } catch (e) {
    AppCommon.showMessage(erro, e.message);
    btn.disabled = false;
    btn.textContent = 'Entrar';
  }
});
