import { login, getToken } from '../core/auth.js';
import { renderMockToggle } from '../components/layout.js';
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
            <input class="input" id="email" type="email" required placeholder="seu@email.com" value="admin@stocksense.local">
          </div>
          <div class="field">
            <label class="field-label" for="senha">Senha</label>
            <input class="input" id="senha" type="password" required placeholder="••••••••" value="admin123">
          </div>
          <button type="submit" class="btn btn-primary btn-block" id="btn-login" style="margin-top:4px">Entrar</button>
          <a href="#" style="text-align:center; font-size:13px; color:var(--cor-texto-sec)" onclick="event.preventDefault()">Esqueci minha senha</a>
        </div>
      </form>
      <div style="text-align:center; margin-top:20px; font-size:12px; color:var(--cor-texto-terc)">
        v0.5 · integrado à API
      </div>
    </div>
  </div>
`;

// Mesmo toggle da área logada — uma única implementação.
renderMockToggle();

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
    // O backend devolve 404 para credencial inválida (não distingue email de senha).
    toast.erro(err.status === 404 ? 'Credenciais inválidas' : (err.detail || 'Não foi possível entrar'));
    btnLogin.disabled = false;
    btnLogin.textContent = 'Entrar';
  }
});
