import { requireAuth } from '../core/auth.js';
import { apiGet } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { pareto } from '../components/charts.js';
import { toast } from '../components/toast.js';
import { emptyState } from '../components/emptyState.js';
import { skeletonKpiGrid, skeletonChart, skeletonTable } from '../components/skeleton.js';
import { moedaBR, numero } from '../core/format.js';

requireAuth();
const page = renderLayout('curva-abc');

let chartInstance = null;
let periodoAtual = '30';

page.innerHTML = `
  <div class="page-header">
    <div>
      <h1 class="page-title">Classificação ABC dos produtos</h1>
      <p class="page-subtitle">Quais produtos respondem pela maior parte do seu faturamento</p>
    </div>
    <select class="select" id="filtro-periodo" style="width:200px">
      <option value="30">Últimos 30 dias</option>
      <option value="60">Últimos 60 dias</option>
      <option value="90">Últimos 90 dias</option>
    </select>
  </div>
  <div id="abc-content"></div>
`;

const content = document.getElementById('abc-content');
content.appendChild(skeletonChart());
content.appendChild(skeletonKpiGrid(3));
content.appendChild(skeletonTable(10, 5));

document.getElementById('filtro-periodo').addEventListener('change', (e) => {
  periodoAtual = e.target.value;
  carregarABC();
});

async function carregarABC() {
  content.innerHTML = '';
  content.appendChild(skeletonChart());

  try {
    const dados = await apiGet(`/curva-abc?periodo=${periodoAtual}`);

    if (!dados || !dados.produtos || dados.produtos.length === 0) {
      content.innerHTML = '';
      content.appendChild(emptyState({
        titulo: 'Nenhum dado para a curva ABC',
        msg: 'Importe dados de vendas para gerar a classificação.',
        acao: { label: 'Importar dados', href: 'importar.html' },
      }));
      return;
    }

    content.innerHTML = '';

    // Ordenar por faturamento desc
    const produtos = dados.produtos.sort((a, b) => b.faturamento - a.faturamento);
    const total = produtos.reduce((a, p) => a + p.faturamento, 0);
    const top30 = produtos.slice(0, 30);

    // Gráfico Pareto
    const chartCard = document.createElement('div');
    chartCard.className = 'card';
    chartCard.style.marginBottom = '20px';
    chartCard.innerHTML = `
      <div class="row-between" style="margin-bottom:10px">
        <h3>Pareto de faturamento</h3>
        <span class="text-meta">top 30 produtos · linha vermelha = 80% acumulados</span>
      </div>
      <div style="height:300px"><canvas id="chart-pareto"></canvas></div>
    `;
    content.appendChild(chartCard);

    if (chartInstance) chartInstance.destroy();
    chartInstance = pareto(document.getElementById('chart-pareto'), {
      labels: top30.map(p => p.nome),
      valores: top30.map(p => p.faturamento),
      classes: top30.map(p => p.classe),
    });

    // Cards A/B/C
    const grupoA = produtos.filter(p => p.classe === 'A');
    const grupoB = produtos.filter(p => p.classe === 'B');
    const grupoC = produtos.filter(p => p.classe === 'C');
    const pctA = total ? (grupoA.reduce((a, p) => a + p.faturamento, 0) / total * 100) : 0;
    const pctB = total ? (grupoB.reduce((a, p) => a + p.faturamento, 0) / total * 100) : 0;
    const pctC = total ? (grupoC.reduce((a, p) => a + p.faturamento, 0) / total * 100) : 0;

    const abcCards = document.createElement('div');
    abcCards.className = 'abc-cards';
    abcCards.style.marginBottom = '20px';
    abcCards.innerHTML = `
      <div class="abc-card a">
        <div class="label" style="margin-bottom:8px">Classe A</div>
        <div style="display:flex;align-items:baseline;gap:10px">
          <span class="kpi-number">${grupoA.length}</span><span class="text-secondary">produtos</span>
        </div>
        <div class="text-small" style="margin-top:6px">${numero(pctA, 0)}% do faturamento · prioridade máxima</div>
      </div>
      <div class="abc-card b">
        <div class="label" style="margin-bottom:8px">Classe B</div>
        <div style="display:flex;align-items:baseline;gap:10px">
          <span class="kpi-number">${grupoB.length}</span><span class="text-secondary">produtos</span>
        </div>
        <div class="text-small" style="margin-top:6px">${numero(pctB, 0)}% do faturamento · monitorar</div>
      </div>
      <div class="abc-card c">
        <div class="label" style="margin-bottom:8px">Classe C</div>
        <div style="display:flex;align-items:baseline;gap:10px">
          <span class="kpi-number">${grupoC.length}</span><span class="text-secondary">produtos</span>
        </div>
        <div class="text-small" style="margin-top:6px">${numero(pctC, 0)}% do faturamento · gestão por exceção</div>
      </div>
    `;
    content.appendChild(abcCards);

    // Tabela
    const tableCard = document.createElement('div');
    tableCard.className = 'card';
    tableCard.style.cssText = 'padding:0; overflow:auto;';

    let acc = 0;
    const tableRows = produtos.map(p => {
      acc += p.faturamento;
      const pct = total ? (p.faturamento / total * 100) : 0;
      const acumulada = total ? (acc / total * 100) : 0;
      const badgeClass = p.classe === 'A' ? 'badge-primary' : p.classe === 'B' ? 'badge-warning' : 'badge-neutral';
      return `<tr>
        <td><span class="badge ${badgeClass}">${p.classe}</span></td>
        <td>${p.nome}</td>
        <td class="tabular">${moedaBR(p.faturamento)}</td>
        <td class="tabular text-secondary">${numero(pct, 1)}%</td>
        <td class="tabular text-secondary">${numero(acumulada, 1)}%</td>
      </tr>`;
    }).join('');

    tableCard.innerHTML = `
      <table class="table">
        <thead><tr><th style="width:80px">Classe</th><th>Produto</th><th>Faturamento</th><th>% do total</th><th>% acumulada</th></tr></thead>
        <tbody>${tableRows}</tbody>
      </table>
    `;
    content.appendChild(tableCard);

  } catch (err) {
    content.innerHTML = '';
    toast.erro(err.detail || 'Erro ao carregar curva ABC');
  }
}

carregarABC();
