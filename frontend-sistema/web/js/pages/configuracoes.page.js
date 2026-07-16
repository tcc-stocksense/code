import { requireAuth } from '../core/auth.js';
import { renderLayout } from '../components/layout.js';
import { toast } from '../components/toast.js';
import { iconCheck } from '../components/icons.js';

requireAuth();
const page = renderLayout('config');

page.style.maxWidth = '760px';
page.innerHTML = `
  <div class="page-header">
    <div>
      <h1 class="page-title">Configurações</h1>
      <p class="page-subtitle">Dados do estabelecimento, perfil e preferências de notificação</p>
    </div>
  </div>
  <div class="tabs" id="tabs">
    <div class="tab active" data-tab="estabelecimento">Estabelecimento</div>
    <div class="tab" data-tab="usuario">Usuário</div>
    <div class="tab" data-tab="notif">Notificações</div>
  </div>
  <form class="card" id="config-form">
    <div id="tab-content"></div>
    <div class="row" style="justify-content:flex-end; margin-top:24px; gap:10px; align-items:center">
      <span class="text-meta" id="salvo-msg" style="color:var(--status-ok); display:none">${iconCheck(14)} Salvo.</span>
      <button type="submit" class="btn btn-primary">Salvar</button>
    </div>
  </form>
`;

let tabAtual = 'estabelecimento';

// Estado local (sem backend, persiste só na sessão)
const estab = { nome: '', cnpj: '', endereco: '' };
const usuario = { nome: '', email: '' };
const notif = { critico: true, frequencia: 'diario' };

const tabContent = document.getElementById('tab-content');

function renderTab() {
  if (tabAtual === 'estabelecimento') {
    tabContent.innerHTML = `
      <div class="stack" style="gap:14px; max-width:480px">
        <div class="field">
          <label class="field-label">Nome fantasia</label>
          <input class="input" id="f-nome" value="${estab.nome}">
        </div>
        <div class="field">
          <label class="field-label">CNPJ</label>
          <input class="input" id="f-cnpj" value="${estab.cnpj}">
        </div>
        <div class="field">
          <label class="field-label">Endereço</label>
          <input class="input" id="f-endereco" value="${estab.endereco}">
        </div>
      </div>
    `;
    tabContent.querySelector('#f-nome').addEventListener('input', e => { estab.nome = e.target.value; });
    tabContent.querySelector('#f-cnpj').addEventListener('input', e => { estab.cnpj = e.target.value; });
    tabContent.querySelector('#f-endereco').addEventListener('input', e => { estab.endereco = e.target.value; });

  } else if (tabAtual === 'usuario') {
    tabContent.innerHTML = `
      <div class="stack" style="gap:14px; max-width:480px">
        <div class="field">
          <label class="field-label">Nome</label>
          <input class="input" id="f-user-nome" value="${usuario.nome}">
        </div>
        <div class="field">
          <label class="field-label">Email</label>
          <input class="input" type="email" id="f-user-email" value="${usuario.email}">
        </div>
        <div>
          <a href="#" class="text-small" id="link-senha">Alterar senha</a>
        </div>
      </div>
    `;
    tabContent.querySelector('#f-user-nome').addEventListener('input', e => { usuario.nome = e.target.value; });
    tabContent.querySelector('#f-user-email').addEventListener('input', e => { usuario.email = e.target.value; });
    tabContent.querySelector('#link-senha').addEventListener('click', e => {
      e.preventDefault();
      toast.info('Alteração de senha será implementada com o backend.');
    });

  } else if (tabAtual === 'notif') {
    tabContent.innerHTML = `
      <div class="stack" style="gap:18px; max-width:480px">
        <div class="row-between" style="padding:8px 0">
          <div>
            <div style="font-weight:500">Alerta de estoque crítico</div>
            <div class="text-meta">Notificar quando um produto passar para estado crítico.</div>
          </div>
          <div class="toggle ${notif.critico ? 'on' : ''}" id="toggle-critico"></div>
        </div>
        <div class="divider"></div>
        <div class="field">
          <label class="field-label">Resumo por email</label>
          <select class="select" id="f-frequencia">
            <option value="diario" ${notif.frequencia === 'diario' ? 'selected' : ''}>Diário, às 08:00</option>
            <option value="semanal" ${notif.frequencia === 'semanal' ? 'selected' : ''}>Semanal, segunda às 08:00</option>
            <option value="nunca" ${notif.frequencia === 'nunca' ? 'selected' : ''}>Não enviar</option>
          </select>
        </div>
      </div>
    `;
    tabContent.querySelector('#toggle-critico').addEventListener('click', () => {
      notif.critico = !notif.critico;
      tabContent.querySelector('#toggle-critico').className = `toggle ${notif.critico ? 'on' : ''}`;
    });
    tabContent.querySelector('#f-frequencia').addEventListener('change', e => { notif.frequencia = e.target.value; });
  }
}

// Tabs
document.getElementById('tabs').addEventListener('click', (e) => {
  const tab = e.target.closest('[data-tab]');
  if (!tab) return;
  tabAtual = tab.dataset.tab;
  document.querySelectorAll('#tabs .tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tabAtual));
  renderTab();
});

// Salvar
document.getElementById('config-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const msg = document.getElementById('salvo-msg');
  msg.style.display = 'inline-flex';
  toast.sucesso('Configurações salvas.');
  setTimeout(() => { msg.style.display = 'none'; }, 2000);
});

renderTab();
