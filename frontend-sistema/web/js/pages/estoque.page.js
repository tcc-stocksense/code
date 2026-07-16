import { requireAuth } from '../core/auth.js';
import { apiGet, apiPatch } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { statusBadge } from '../components/statusBadge.js';
import { toast } from '../components/toast.js';
import { emptyState } from '../components/emptyState.js';
import { skeletonTable } from '../components/skeleton.js';
import { iconPencil, iconMinus, iconPlus, iconCheck, iconX, iconSearch } from '../components/icons.js';

requireAuth();
const page = renderLayout('estoque');

// State
let produtos = [];
let filtros = { busca: '', categoria: 'todas', status: 'todos', classe: 'todas' };

page.innerHTML = `
  <div class="page-header">
    <div>
      <h1 class="page-title">Estoque atual</h1>
      <p class="page-subtitle" id="subtitle"></p>
    </div>
  </div>
  <div class="filters-row">
    <div class="field" style="flex:1 1 300px; max-width:380px">
      <div style="position:relative">
        <span style="position:absolute; left:10px; top:50%; transform:translateY(-50%); color:var(--cor-texto-terc); pointer-events:none; display:flex">${iconSearch(16)}</span>
        <input class="input search" id="busca" placeholder="Buscar produto" style="padding-left:36px">
      </div>
    </div>
    <select class="select" id="filtro-cat"><option value="todas">Todas categorias</option></select>
    <select class="select" id="filtro-status">
      <option value="todos">Todos status</option>
      <option value="critico">Crítico</option>
      <option value="atencao">Atenção</option>
      <option value="ok">OK</option>
    </select>
    <select class="select" id="filtro-classe">
      <option value="todas">Todas classes</option>
      <option value="A">Classe A</option>
      <option value="B">Classe B</option>
      <option value="C">Classe C</option>
    </select>
  </div>
  <div id="tabela-container"></div>
  <div class="row-between" style="margin-top:16px">
    <span class="text-meta" id="contagem"></span>
    <div class="row" style="gap:6px; align-items:center">
      <span class="text-meta">Página 1 de 1</span>
      <button class="btn btn-tertiary btn-sm" disabled>Anterior</button>
      <button class="btn btn-tertiary btn-sm" disabled>Próxima</button>
    </div>
  </div>
`;

const tabelaContainer = document.getElementById('tabela-container');
tabelaContainer.appendChild(skeletonTable(8, 6));

// Filtros
document.getElementById('busca').addEventListener('input', (e) => { filtros.busca = e.target.value.toLowerCase(); renderTabela(); });
document.getElementById('filtro-cat').addEventListener('change', (e) => { filtros.categoria = e.target.value; renderTabela(); });
document.getElementById('filtro-status').addEventListener('change', (e) => { filtros.status = e.target.value; renderTabela(); });
document.getElementById('filtro-classe').addEventListener('change', (e) => { filtros.classe = e.target.value; renderTabela(); });

function statusClass(dias) {
  if (dias < 3) return 'critico';
  if (dias <= 7) return 'atencao';
  return 'ok';
}

function getFiltrados() {
  return produtos.filter(p => {
    if (filtros.busca && !p.nome.toLowerCase().includes(filtros.busca)) return false;
    if (filtros.categoria !== 'todas' && p.categoria !== filtros.categoria) return false;
    if (filtros.classe !== 'todas' && p.classe !== filtros.classe) return false;
    if (filtros.status !== 'todos' && statusClass(p.diasRuptura) !== filtros.status) return false;
    return true;
  }).sort((a, b) => a.diasRuptura - b.diasRuptura);
}

function classeBadge(classe) {
  const map = { A: 'badge-primary', B: 'badge-warning', C: 'badge-neutral' };
  return `<span class="badge ${map[classe] || 'badge-neutral'}">${classe}</span>`;
}

function renderTabela() {
  const filtrados = getFiltrados();
  document.getElementById('subtitle').textContent = `${filtrados.length} produtos · ordenados por urgência de reposição`;
  document.getElementById('contagem').textContent = `Mostrando ${filtrados.length} de ${produtos.length} produtos`;

  const card = document.createElement('div');
  card.className = 'card';
  card.style.padding = '0';
  card.style.overflow = 'auto';

  const table = document.createElement('table');
  table.className = 'table';
  table.innerHTML = `
    <thead><tr>
      <th style="width:80px">Status</th>
      <th>Produto</th>
      <th>Categoria</th>
      <th>Estoque</th>
      <th>Até ruptura</th>
      <th>ABC</th>
      <th></th>
    </tr></thead>
  `;

  const tbody = document.createElement('tbody');

  if (filtrados.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:40px 20px;color:var(--cor-texto-sec)">Nenhum produto encontrado.</td></tr>';
  }

  filtrados.forEach(p => {
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';
    tr.addEventListener('click', () => { window.location.href = `produto-detalhe.html?id=${p.id}`; });

    // Status
    const tdStatus = document.createElement('td');
    tdStatus.appendChild(statusBadge(p.diasRuptura));
    tr.appendChild(tdStatus);

    // Nome
    tr.innerHTML += `<td><div style="font-weight:500">${p.nome}</div></td>`;
    tr.innerHTML += `<td class="text-small text-secondary">${p.categoria}</td>`;

    // Estoque editável
    const tdEstoque = document.createElement('td');
    tdEstoque.addEventListener('click', (e) => e.stopPropagation());
    renderEstoqueCell(tdEstoque, p);
    tr.appendChild(tdEstoque);

    // Até ruptura
    const diasText = p.diasRuptura === 0 ? 'zerado' : `${p.diasRuptura} ${p.diasRuptura === 1 ? 'dia' : 'dias'}`;
    tr.innerHTML += `<td class="tabular">${diasText}</td>`;

    // ABC
    tr.innerHTML += `<td>${classeBadge(p.classe)}</td>`;

    // Ação
    tr.innerHTML += `<td><a href="produto-detalhe.html?id=${p.id}" class="btn btn-tertiary btn-sm" onclick="event.stopPropagation()">Detalhe</a></td>`;

    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  card.appendChild(table);

  tabelaContainer.innerHTML = '';
  tabelaContainer.appendChild(card);
}

function renderEstoqueCell(td, produto) {
  td.innerHTML = '';
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'estoque-cell';
  btn.innerHTML = `<span class="tabular">${produto.estoque} ${produto.unidade || 'un'}</span>${iconPencil(13)}`;
  btn.title = 'Clique para editar o estoque';
  btn.addEventListener('click', () => renderEstoqueEdit(td, produto));
  td.appendChild(btn);
}

function renderEstoqueEdit(td, produto) {
  td.innerHTML = '';
  let val = produto.estoque;

  const wrapper = document.createElement('span');
  wrapper.className = 'estoque-edit';

  const btnMinus = document.createElement('button');
  btnMinus.type = 'button';
  btnMinus.className = 'step-btn';
  btnMinus.innerHTML = iconMinus(13);
  btnMinus.addEventListener('click', () => { val = Math.max(0, val - 1); input.value = val; });

  const input = document.createElement('input');
  input.type = 'number';
  input.className = 'estoque-input';
  input.value = val;
  input.min = '0';
  input.addEventListener('input', (e) => { val = Math.max(0, Math.round(+e.target.value) || 0); });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') salvar();
    if (e.key === 'Escape') renderEstoqueCell(td, produto);
  });

  const btnPlus = document.createElement('button');
  btnPlus.type = 'button';
  btnPlus.className = 'step-btn';
  btnPlus.innerHTML = iconPlus(13);
  btnPlus.addEventListener('click', () => { val += 1; input.value = val; });

  const btnOk = document.createElement('button');
  btnOk.type = 'button';
  btnOk.className = 'confirm-btn ok';
  btnOk.innerHTML = iconCheck(14);
  btnOk.title = 'Salvar';
  btnOk.addEventListener('click', salvar);

  const btnCancel = document.createElement('button');
  btnCancel.type = 'button';
  btnCancel.className = 'confirm-btn no';
  btnCancel.innerHTML = iconX(14);
  btnCancel.title = 'Cancelar';
  btnCancel.addEventListener('click', () => renderEstoqueCell(td, produto));

  wrapper.append(btnMinus, input, btnPlus, btnOk, btnCancel);
  td.appendChild(wrapper);

  setTimeout(() => input.select(), 0);

  async function salvar() {
    try {
      const resp = await apiPatch(`/produtos/${produto.id}/estoque`, { estoque: val });
      // Atualizar dados locais com resposta do backend
      produto.estoque = resp.estoque ?? val;
      if (resp.diasRuptura != null) produto.diasRuptura = resp.diasRuptura;
      if (resp.status) produto.statusSemaforo = resp.status;
      toast.sucesso(`Estoque de "${produto.nome}" atualizado`);
      renderTabela();
    } catch (err) {
      toast.erro(err.detail || 'Erro ao atualizar estoque');
      renderEstoqueCell(td, produto);
    }
  }
}

async function carregarEstoque() {
  try {
    produtos = await apiGet('/produtos');

    // Preencher categorias no filtro
    const categorias = [...new Set(produtos.map(p => p.categoria).filter(Boolean))].sort();
    const selectCat = document.getElementById('filtro-cat');
    categorias.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      selectCat.appendChild(opt);
    });

    renderTabela();
  } catch (err) {
    tabelaContainer.innerHTML = '';
    if (err.status === 404) {
      tabelaContainer.appendChild(emptyState({
        titulo: 'Nenhum produto importado ainda',
        msg: 'Vá para Importar para carregar seus dados.',
        acao: { label: 'Importar dados', href: 'importar.html' },
      }));
    } else {
      toast.erro(err.detail || 'Erro ao carregar produtos');
    }
  }
}

carregarEstoque();
