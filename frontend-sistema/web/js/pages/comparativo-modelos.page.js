import { requireAuth } from '../core/auth.js';
import { apiGet } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { barras } from '../components/charts.js';
import { toast } from '../components/toast.js';
import { emptyState } from '../components/emptyState.js';
import { skeletonKpiGrid, skeletonChart, skeletonTable } from '../components/skeleton.js';
import { numero } from '../core/format.js';

requireAuth();
const page = renderLayout('comparativo');

let chartInstance = null;
let metricaAtual = 'mape';
let dadosCache = null;

page.innerHTML = `
  <div style="background:var(--info-bg); border-left:3px solid var(--info); padding:10px 16px; font-size:13px; color:var(--info); margin-bottom:20px;">
    <span style="font-weight:500">Acesso técnico</span> · este painel é destinado à equipe de modelagem e à banca avaliadora.
  </div>
  <div class="page-header">
    <div>
      <h1 class="page-title">Comparativo de modelos preditivos</h1>
      <p class="page-subtitle">Holt-Winters vs Prophet · métricas agregadas e por produto</p>
    </div>
  </div>
  <div id="comp-content"></div>
`;

const content = document.getElementById('comp-content');
content.appendChild(skeletonKpiGrid(3));
content.appendChild(skeletonChart());
content.appendChild(skeletonTable(8, 8));

async function carregarComparativo() {
  try {
    const dados = await apiGet('/metricas');
    dadosCache = dados;

    if (!dados || (!dados.agregado && (!dados.porProduto || dados.porProduto.length === 0))) {
      content.innerHTML = '';
      content.appendChild(emptyState({
        titulo: 'Nenhuma métrica disponível',
        msg: 'Rode o motor de previsão para gerar métricas de comparação.',
      }));
      return;
    }

    renderConteudo(dados);

  } catch (err) {
    content.innerHTML = '';
    toast.erro(err.detail || 'Erro ao carregar métricas');
  }
}

function renderConteudo(dados) {
  content.innerHTML = '';
  const ag = dados.agregado || {};

  // KPIs agregados
  const kpiGrid = document.createElement('div');
  kpiGrid.className = 'kpi-grid';
  kpiGrid.style.gridTemplateColumns = 'repeat(3, 1fr)';

  kpiGrid.appendChild(metricCard('MAPE', ag.mapeHW, ag.mapeProphet, '%', true));
  kpiGrid.appendChild(metricCard('RMSE', ag.rmseHW, ag.rmseProphet, '', true));
  kpiGrid.appendChild(metricCard('MAE', ag.maeHW, ag.maeProphet, '', true));

  content.appendChild(kpiGrid);

  // Gráfico de barras
  if (dados.porProduto && dados.porProduto.length > 0) {
    const chartCard = document.createElement('div');
    chartCard.className = 'card';
    chartCard.style.marginBottom = '20px';
    chartCard.innerHTML = `
      <div class="row-between" style="margin-bottom:12px">
        <h3>Comparação por produto</h3>
        <select class="select" id="select-metrica" style="width:160px">
          <option value="mape">MAPE</option>
          <option value="rmse">RMSE</option>
          <option value="mae">MAE</option>
        </select>
      </div>
      <div style="height:320px"><canvas id="chart-comparativo"></canvas></div>
    `;
    content.appendChild(chartCard);

    document.getElementById('select-metrica').value = metricaAtual;
    document.getElementById('select-metrica').addEventListener('change', (e) => {
      metricaAtual = e.target.value;
      renderGrafico(dados.porProduto);
    });

    renderGrafico(dados.porProduto);

    // Log de execuções
    if (dados.execucoes && dados.execucoes.length > 0) {
      const logCard = document.createElement('div');
      logCard.className = 'card';
      logCard.style.cssText = 'padding:0; margin-bottom:20px;';
      logCard.innerHTML = `
        <div style="padding:16px 20px; border-bottom:1px solid var(--cor-borda)">
          <h3>Log de execuções</h3>
        </div>
        <pre style="padding:16px 20px; margin:0; font-size:13px; white-space:pre-wrap; font-family:monospace; line-height:1.6; max-height:260px; overflow:auto">${dados.execucoes.map(e => `[${e.data}] ${e.mensagem}`).join('\n')}</pre>
      `;
      content.appendChild(logCard);
    }

    // Tabela detalhada
    const tableCard = document.createElement('div');
    tableCard.className = 'card';
    tableCard.style.cssText = 'padding:0; overflow:auto; margin-bottom:20px;';
    tableCard.innerHTML = `
      <div style="padding:16px 20px; border-bottom:1px solid var(--cor-borda)">
        <h3>Métricas detalhadas por produto</h3>
      </div>
      <table class="table">
        <thead><tr>
          <th>Produto</th>
          <th>MAPE H-W</th><th>MAPE Prophet</th>
          <th>RMSE H-W</th><th>RMSE Prophet</th>
          <th>MAE H-W</th><th>MAE Prophet</th>
          <th>Recomendado</th>
        </tr></thead>
        <tbody>
          ${dados.porProduto.map(m => {
            const rec = m.recomendado || (m.mapeProphet < m.mapeHW ? 'Prophet' : 'Holt-Winters');
            const badgeCls = rec === 'Prophet' ? 'badge-info' : 'badge-primary';
            return `<tr>
              <td>${m.nome}</td>
              <td class="tabular">${numero(m.mapeHW, 2)}%</td>
              <td class="tabular">${numero(m.mapeProphet, 2)}%</td>
              <td class="tabular">${numero(m.rmseHW, 2)}</td>
              <td class="tabular">${numero(m.rmseProphet, 2)}</td>
              <td class="tabular">${numero(m.maeHW, 2)}</td>
              <td class="tabular">${numero(m.maeProphet, 2)}</td>
              <td><span class="badge ${badgeCls}">${rec}</span></td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>
    `;
    content.appendChild(tableCard);
  }
}

function renderGrafico(porProduto) {
  const canvas = document.getElementById('chart-comparativo');
  if (!canvas) return;

  if (chartInstance) chartInstance.destroy();

  const keyHW = metricaAtual + 'HW';
  const keyPro = metricaAtual + 'Prophet';

  chartInstance = barras(canvas, {
    labels: porProduto.map(m => m.nome.split(' ').slice(0, 2).join(' ')),
    series: [
      { label: 'Holt-Winters', data: porProduto.map(m => m[keyHW] || 0), cor: '#1F4A30' },
      { label: 'Prophet', data: porProduto.map(m => m[keyPro] || 0), cor: '#2E5A78' },
    ],
  });
}

function metricCard(label, hw, pro, unit, lowerBetter) {
  const card = document.createElement('div');
  card.className = 'card';

  const hwVal = hw != null ? numero(hw, 2) + unit : '—';
  const proVal = pro != null ? numero(pro, 2) + unit : '—';
  const winnerHW = hw != null && pro != null && (lowerBetter ? hw < pro : hw > pro);
  const diff = hw != null && pro != null ? numero(Math.abs(hw - pro), 2) + unit : '—';

  card.innerHTML = `
    <div class="label" style="margin-bottom:14px">${label} agregado</div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px">
      <div>
        <div class="text-meta" style="margin-bottom:4px">Holt-Winters ${winnerHW ? '<span class="badge badge-primary" style="margin-left:4px">melhor</span>' : ''}</div>
        <div class="tabular" style="font-size:24px; font-weight:500">${hwVal}</div>
      </div>
      <div>
        <div class="text-meta" style="margin-bottom:4px">Prophet ${!winnerHW && hw != null ? '<span class="badge badge-info" style="margin-left:4px">melhor</span>' : ''}</div>
        <div class="tabular" style="font-size:24px; font-weight:500">${proVal}</div>
      </div>
    </div>
    <div class="text-meta" style="margin-top:10px">Diferença: ${diff} ${lowerBetter ? '(quanto menor, melhor)' : ''}</div>
  `;

  return card;
}

carregarComparativo();
