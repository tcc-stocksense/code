import { logout, getNomeFantasia } from '../core/auth.js';
import { mockAtivo, setMock } from '../core/config.js';
import { iconHome, iconBox, iconBell, iconChart, iconUpload, iconBeaker, iconCog, iconLogout, iconCart } from './icons.js';

const NAV_OPERACAO = [
  { id: 'dashboard',   label: 'Home',                 icon: iconHome,   href: 'dashboard.html' },
  { id: 'estoque',     label: 'Estoque',              icon: iconBox,    href: 'estoque.html' },
  { id: 'alertas',     label: 'Alertas de reposição', icon: iconBell,   href: 'alertas.html' },
  { id: 'curva-abc',   label: 'Curva ABC',            icon: iconChart,  href: 'curva-abc.html' },
  { id: 'sugestao',    label: 'Sugestão de compra',   icon: iconCart,   href: 'sugestao-compra.html', indisponivel: true },
];

const NAV_SISTEMA = [
  { id: 'importar',    label: 'Importar dados',   icon: iconUpload, href: 'importar.html' },
  { id: 'config',      label: 'Configurações',    icon: iconCog,    href: 'configuracoes.html' },
];

function navItems(items, telaAtiva) {
  return items.map(item => `
    <a href="${item.href}" class="nav-item ${item.id === telaAtiva ? 'active' : ''}"${item.indisponivel ? ' title="Sem endpoint no backend — disponível apenas em modo mock"' : ''}>
      ${item.icon()}
      ${item.label}
      ${item.indisponivel ? '<span class="badge badge-neutral" style="margin-left:auto;font-size:10px">em breve</span>' : ''}
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

  // Topbar — o nome do estabelecimento vem do login (LoginResponse.nomeFantasia)
  const nomeFantasia = getNomeFantasia();
  const inicial = (nomeFantasia || 'U').trim().charAt(0).toUpperCase();

  const topbar = document.createElement('header');
  topbar.className = 'topbar';
  topbar.innerHTML = `
    <div class="topbar-left">
      <strong id="topbar-nome">${nomeFantasia}</strong>
      <span style="color:var(--cor-texto-terc)">·</span>
      <span id="topbar-info"></span>
    </div>
    <div class="topbar-right" style="position:relative">
      <div class="avatar" id="topbar-avatar" style="cursor:pointer" title="Menu do usuário">${inicial}</div>
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
//  fictícios. Fonte da verdade: core/config.js (padrão = API real).
// ============================================================
export function renderMockToggle() {
  if (document.getElementById('mock-toggle')) return;

  const btn = document.createElement('button');
  btn.id = 'mock-toggle';
  btn.type = 'button';

  function atualizar() {
    const on = mockAtivo();
    btn.textContent = on ? '🟠 Mock ON' : '🟢 API real';
    btn.title = on
      ? 'Exibindo dados fictícios. Clique para falar com a API real.'
      : 'Falando com a API real. Clique para usar dados fictícios (offline).';
    btn.style.cssText = `
      position:fixed; bottom:16px; right:16px; z-index:9999;
      padding:6px 14px; border-radius:20px; border:1px solid var(--cor-borda-forte);
      font-size:12px; font-weight:500; cursor:pointer;
      background:${on ? 'var(--status-atencao)' : 'var(--cor-primaria)'};
      color:#fff;
      box-shadow:0 2px 8px rgba(0,0,0,0.12);
      transition: all 0.2s;
    `;
  }

  atualizar();

  btn.addEventListener('click', () => {
    setMock(!mockAtivo());
    location.reload();
  });

  document.body.appendChild(btn);
}
