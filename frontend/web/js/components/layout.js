import { logout } from '../core/auth.js';
import { iconHome, iconBox, iconBell, iconChart, iconUpload, iconBeaker, iconCog, iconLogout, iconCart } from './icons.js';

const NAV_OPERACAO = [
  { id: 'dashboard',   label: 'Home',                 icon: iconHome,   href: 'dashboard.html' },
  { id: 'estoque',     label: 'Estoque',              icon: iconBox,    href: 'estoque.html' },
  { id: 'alertas',     label: 'Alertas de reposição', icon: iconBell,   href: 'alertas.html' },
  { id: 'curva-abc',   label: 'Curva ABC',            icon: iconChart,  href: 'curva-abc.html' },
  { id: 'sugestao',   label: 'Sugestão de compra',   icon: iconCart,   href: 'sugestao-compra.html' },
];

const NAV_SISTEMA = [
  { id: 'importar',    label: 'Importar dados',   icon: iconUpload, href: 'importar.html' },
  { id: 'config',      label: 'Configurações',    icon: iconCog,    href: 'configuracoes.html' },
];

function navItems(items, telaAtiva) {
  return items.map(item => `
    <a href="${item.href}" class="nav-item ${item.id === telaAtiva ? 'active' : ''}">
      ${item.icon()}
      ${item.label}
    </a>
  `).join('');
}

export function renderLayout(telaAtiva) {
  const app = document.getElementById('app');
  if (!app) return;

  // Sidebar
  const sidebar = document.createElement('aside');
  sidebar.className = 'sidebar';
  sidebar.innerHTML = `
    <div class="sidebar-logo">
      <div class="logo-mark">S</div>
      <div class="logo-text">StockSense<small>Motor preditivo</small></div>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-section-label">Operação</div>
      ${navItems(NAV_OPERACAO, telaAtiva)}
      <div class="nav-section-label" style="margin-top:12px">Sistema</div>
      ${navItems(NAV_SISTEMA, telaAtiva)}
    </nav>
    <div class="sidebar-footer">
      <div class="nav-section-label" style="padding:4px 12px 4px">Acesso técnico</div>
      <a href="comparativo-modelos.html" class="nav-item ${telaAtiva === 'comparativo' ? 'active' : ''}">
        ${iconBeaker()}
        Comparativo de modelos
      </a>
      <button type="button" class="nav-item" id="btn-logout">
        ${iconLogout()}
        Sair
      </button>
    </div>
  `;

  // Main wrapper
  const main = document.createElement('div');
  main.className = 'main';

  // Topbar
  const topbar = document.createElement('header');
  topbar.className = 'topbar';
  topbar.innerHTML = `
    <div class="topbar-left">
      <strong id="topbar-nome">StockSense</strong>
      <span style="color:var(--cor-texto-terc)">·</span>
      <span id="topbar-info"></span>
    </div>
    <div class="topbar-right" style="position:relative">
      <div class="avatar" id="topbar-avatar" style="cursor:pointer" title="Menu do usuário">U</div>
      <div class="avatar-menu" id="avatar-menu">
        <a href="configuracoes.html" class="avatar-menu-item">
          ${iconCog(16)}
          Configurações
        </a>
        <button type="button" class="avatar-menu-item" id="menu-logout">
          ${iconLogout(16)}
          Sair
        </button>
      </div>
    </div>
  `;

  // Page content container
  const page = document.createElement('div');
  page.className = 'page';
  page.id = 'page-content';

  main.appendChild(topbar);
  main.appendChild(page);

  app.classList.add('app');
  app.appendChild(sidebar);
  app.appendChild(main);

  // Sidebar logout
  sidebar.querySelector('#btn-logout').addEventListener('click', () => logout());

  // Avatar dropdown menu
  const avatar = topbar.querySelector('#topbar-avatar');
  const menu = topbar.querySelector('#avatar-menu');

  avatar.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('open');
  });

  menu.querySelector('#menu-logout').addEventListener('click', () => logout());

  // Fechar menu ao clicar fora
  document.addEventListener('click', () => menu.classList.remove('open'));
  menu.addEventListener('click', (e) => e.stopPropagation());

  // Toggle de mock data
  renderMockToggle();

  return page;
}

// ============================================================
//  MOCK TOGGLE — botão flutuante para ativar/desativar dados
// ============================================================
function renderMockToggle() {
  if (document.getElementById('mock-toggle')) return;

  const btn = document.createElement('button');
  btn.id = 'mock-toggle';
  btn.type = 'button';

  const ativo = localStorage.getItem('stocksense_mock') !== 'off';

  function atualizar() {
    const on = localStorage.getItem('stocksense_mock') !== 'off';
    btn.textContent = on ? '🟢 Mock ON' : '⚪ Mock OFF';
    btn.title = on ? 'Clique para desativar dados fictícios' : 'Clique para ativar dados fictícios';
    btn.style.cssText = `
      position:fixed; bottom:16px; right:16px; z-index:9999;
      padding:6px 14px; border-radius:20px; border:1px solid var(--cor-borda-forte);
      font-size:12px; font-weight:500; cursor:pointer;
      background:${on ? 'var(--cor-primaria)' : '#fff'};
      color:${on ? '#fff' : 'var(--cor-texto-sec)'};
      box-shadow:0 2px 8px rgba(0,0,0,0.12);
      transition: all 0.2s;
    `;
  }

  atualizar();

  btn.addEventListener('click', () => {
    const on = localStorage.getItem('stocksense_mock') !== 'off';
    localStorage.setItem('stocksense_mock', on ? 'off' : 'on');
    location.reload();
  });

  document.body.appendChild(btn);
}
