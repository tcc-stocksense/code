import { login, getToken } from '../core/auth.js';
import { toast } from '../components/toast.js';

// Já logado → dashboard
if (getToken()) {
  window.location.replace('dashboard.html');
}

const app = document.getElementById('app');
app.innerHTML = `
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <div class="logo-mark">S</div>
        <div class="logo-text">StockSense<small>Motor preditivo</small></div>
      </div>
      <h2 style="text-align:center; font-size:18px; margin-bottom:6px">Entrar no sistema</h2>
      <p class="text-meta" style="text-align:center; margin-bottom:24px">Use os dados do seu estabelecimento para acessar</p>
      <form id="login-form">
        <div class="stack" style="gap:14px">
          <div class="field">
            <label class="field-label" for="email">Email</label>
            <input class="input" id="email" type="email" required placeholder="seu@email.com" value="gestor@stocksense.com">
          </div>
          <div class="field">
            <label class="field-label" for="senha">Senha</label>
            <input class="input" id="senha" type="password" required placeholder="••••••••" value="123456">
          </div>
          <button type="submit" class="btn btn-primary btn-block" id="btn-login" style="margin-top:4px">Entrar</button>
          <a href="#" style="text-align:center; font-size:13px; color:var(--cor-texto-sec)" onclick="event.preventDefault()">Esqueci minha senha</a>
        </div>
      </form>
      <div style="text-align:center; margin-top:20px; font-size:12px; color:var(--cor-texto-terc)">
        v0.4 protótipo
      </div>
    </div>
  </div>
`;

// Toggle de mock (mesmo da layout, mas para a tela de login)
(function mockToggle() {
  const btn = document.createElement('button');
  btn.id = 'mock-toggle';
  btn.type = 'button';
  const on = localStorage.getItem('stocksense_mock') !== 'off';
  btn.textContent = on ? '🟢 Mock ON' : '⚪ Mock OFF';
  btn.title = on ? 'Clique para desativar dados fictícios' : 'Clique para ativar dados fictícios';
  btn.style.cssText = `position:fixed;bottom:16px;right:16px;z-index:9999;padding:6px 14px;border-radius:20px;border:1px solid var(--cor-borda-forte);font-size:12px;font-weight:500;cursor:pointer;background:${on?'var(--cor-primaria)':'#fff'};color:${on?'#fff':'var(--cor-texto-sec)'};box-shadow:0 2px 8px rgba(0,0,0,0.12)`;
  btn.addEventListener('click', () => {
    localStorage.setItem('stocksense_mock', on ? 'off' : 'on');
    location.reload();
  });
  document.body.appendChild(btn);
})();

const form = document.getElementById('login-form');
const btnLogin = document.getElementById('btn-login');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('email').value;
  const senha = document.getElementById('senha').value;

  btnLogin.disabled = true;
  btnLogin.innerHTML = '<span class="spinner"></span> Entrando...';

  try {
    await login(email, senha);
    window.location.replace('dashboard.html');
  } catch (err) {
    toast.erro(err.detail || 'Credenciais inválidas');
    btnLogin.disabled = false;
    btnLogin.textContent = 'Entrar';
  }
});
