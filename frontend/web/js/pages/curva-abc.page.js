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

// O filtro de período do protótipo foi removido: GET /api/curva-abc não aceita
// `?periodo=` — o backend classifica sobre todo o histórico importado.
page.innerHTML = `
  <div class="page-header">
    <div>
      <h1 class="page-title">Classificação ABC dos produtos</h1>
      <p class="page-subtitle">Quais produtos respondem pela maior parte do seu faturamento</p>
    </div>
  </div>
  <div id="abc-content"></div>
`;

const content = document.getElementById('abc-content');
content.appendChild(skeletonChart());
content.appendChild(skeletonKpiGrid(3));
content.appendChild(skeletonTable(10, 5));

async function carregarABC() {
  content.innerHTML = '';
  content.appendChild(skeletonChart());

  try {
    const dados = await apiGet('/curva-abc');
    const itens = dados?.itens ?? [];

    if (itens.length === 0) {
      content.innerHTML = '';
      content.appendChild(emptyState({
        titulo: 'Nenhum dado para a curva ABC',
        msg: 'Importe as vendas e execute o recálculo para gerar a classificação.',
        acao: { label: 'Importar dados', href: 'importar.html' },
      }));
      return;
    }

    content.innerHTML = '';

    // O backend já devolve `itens` ordenado, com percentual do total e acumulado prontos.
    const usaProxy = dados.abcProxy === true;

    if (usaProxy) {
      const aviso = document.createElement('div');
      aviso.className = 'banner banner-warning';
      aviso.style.marginBottom = '16px';
      aviso.innerHTML = `
        <div class="banner-body">
          <strong>Ranking por quantidade vendida.</strong>
          <small>O histórico importado não trouxe valor de venda, então a classificação usa quantidade como aproximação do faturamento.</small>
        </div>
      `;
      content.appendChild(aviso);
    }

    const rotuloValor = usaProxy ? 'Quantidade' : 'Faturamento';
    const top30 = itens.slice(0, 30);

    // Gráfico Pareto
    const chartCard = document.createElement('div');
    chartCard.className = 'card';
    chartCard.style.marginBottom = '20px';
    chartCard.innerHTML = `
      <div class="row-between" style="margin-bottom:10px">
        <h3>Pareto de ${rotuloValor.toLowerCase()}</h3>
        <span class="text-meta">top 30 produtos · linha vermelha = 80% acumulados</span>
      </div>
      <div style="height:300px"><canvas id="chart-pareto"></canvas></div>
    `;
    content.appendChild(chartCard);

    if (chartInstance) chartInstance.destroy();
    chartInstance = pareto(document.getElementById('chart-pareto'), {
      labels: top30.map(i => i.nome),
      valores: top30.map(i => i.faturamento ?? 0),
      classes: top30.map(i => i.classe),
    });

    // Cards A/B/C — participação vem do percentualDoTotal do backend
    const somaPct = (classe) => itens
      .filter(i => i.classe === classe)
      .reduce((acc, i) => acc + (i.percentualDoTotal ?? 0), 0);

    const grupos = [
      { classe: 'A', css: 'a', qtd: itens.filter(i => i.classe === 'A').length, pct: somaPct('A'), nota: 'prioridade máxima' },
      { classe: 'B', css: 'b', qtd: itens.filter(i => i.classe === 'B').length, pct: somaPct('B'), nota: 'monitorar' },
      { classe: 'C', css: 'c', qtd: itens.filter(i => i.classe === 'C').length, pct: somaPct('C'), nota: 'gestão por exceção' },
    ];

    const abcCards = document.createElement('div');
    abcCards.className = 'abc-cards';
    abcCards.style.marginBottom = '20px';
    abcCards.innerHTML = grupos.map(g => `
      <div class="abc-card ${g.css}">
        <div class="label" style="margin-bottom:8px">Classe ${g.classe}</div>
        <div style="display:flex;align-items:baseline;gap:10px">
          <span class="kpi-number">${g.qtd}</span><span class="text-secondary">produtos</span>
        </div>
        <div class="text-small" style="margin-top:6px">${numero(g.pct, 0)}% do total · ${g.nota}</div>
      </div>
    `).join('');
    content.appendChild(abcCards);

    // Tabela
    const tableCard = document.createElement('div');
    tableCard.className = 'card';
    tableCard.style.cssText = 'padding:0; overflow:auto;';

    const tableRows = itens.map(i => {
      const badgeClass = i.classe === 'A' ? 'badge-primary' : i.classe === 'B' ? 'badge-warning' : 'badge-neutral';
      const valor = i.faturamento == null
        ? '—'
        : usaProxy ? numero(i.faturamento, 0) : moedaBR(i.faturamento);
      return `<tr>
        <td><span class="badge ${badgeClass}">${i.classe}</span></td>
        <td>${i.nome}</td>
        <td class="tabular">${valor}</td>
        <td class="tabular text-secondary">${numero(i.percentualDoTotal, 1)}%</td>
        <td class="tabular text-secondary">${numero(i.percentualAcumulado, 1)}%</td>
      </tr>`;
    }).join('');

    tableCard.innerHTML = `
      <table class="table">
        <thead><tr><th style="width:80px">Classe</th><th>Produto</th><th>${rotuloValor}</th><th>% do total</th><th>% acumulada</th></tr></thead>
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
