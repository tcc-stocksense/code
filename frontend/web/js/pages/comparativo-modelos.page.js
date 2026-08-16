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

/** Chaves do ml-service: "holt_winters" e "prophet". */
const HW = 'holt_winters';
const PROPHET = 'prophet';
const ROTULO = { [HW]: 'Holt-Winters', [PROPHET]: 'Prophet' };

page.innerHTML = `
  <div style="background:var(--info-bg); border-left:3px solid var(--info); padding:10px 16px; font-size:13px; color:var(--info); margin-bottom:20px;">
    <span style="font-weight:500">Acesso técnico</span> · este painel é destinado à equipe de modelagem e à banca avaliadora.
  </div>
  <div class="page-header">
    <div>
      <h1 class="page-title">Comparativo de modelos preditivos</h1>
      <p class="page-subtitle">Holt-Winters vs Prophet · métricas por produto, agregadas nesta tela</p>
    </div>
  </div>
  <div id="comp-content"></div>
`;

const content = document.getElementById('comp-content');
content.appendChild(skeletonKpiGrid(3));
content.appendChild(skeletonChart());
content.appendChild(skeletonTable(8, 8));

/**
 * Executa `tarefas` com no máximo `limite` requisições simultâneas.
 * Não existe endpoint agregado de métricas: a visão geral é montada aqui a
 * partir de GET /api/produtos/{id}/metricas, um produto por vez.
 */
async function comLimite(itens, limite, tarefa) {
  const resultados = new Array(itens.length);
  let proximo = 0;

  async function worker() {
    while (proximo < itens.length) {
      const indice = proximo++;
      resultados[indice] = await tarefa(itens[indice], indice);
    }
  }

  await Promise.all(Array.from({ length: Math.min(limite, itens.length) }, worker));
  return resultados;
}

/** Converte a lista de MetricaResponse de um produto em uma linha da tabela. */
function montarLinha(produto, metricas) {
  if (!metricas || metricas.length === 0) return null;

  const porModelo = {};
  metricas.forEach(m => { porModelo[m.modelo] = m; });

  const hw = porModelo[HW];
  const prophet = porModelo[PROPHET];
  const vencedor = metricas.find(m => m.selecionado);

  return {
    id: produto.id,
    nome: produto.nome,
    mapeHW: hw?.mape ?? null,
    mapeProphet: prophet?.mape ?? null,
    rmseHW: hw?.rmse ?? null,
    rmseProphet: prophet?.rmse ?? null,
    maeHW: hw?.mae ?? null,
    maeProphet: prophet?.mae ?? null,
    selecionado: vencedor ? (ROTULO[vencedor.modelo] || vencedor.modelo) : null,
    executadoEm: vencedor?.executadoEm ?? metricas[0]?.executadoEm ?? null,
  };
}

/** Média simples ignorando nulos. */
function media(valores) {
  const validos = valores.filter(v => v != null);
  if (validos.length === 0) return null;
  return validos.reduce((a, v) => a + v, 0) / validos.length;
}

async function carregarComparativo() {
  try {
    const produtos = await apiGet('/produtos');

    if (!produtos || produtos.length === 0) {
      content.innerHTML = '';
      content.appendChild(emptyState({
        titulo: 'Nenhum produto importado',
        msg: 'Importe produtos e vendas antes de comparar os modelos.',
        acao: { label: 'Importar dados', href: 'importar.html' },
      }));
      return;
    }

    const brutos = await comLimite(produtos, 4, async (produto) => {
      try {
        const metricas = await apiGet(`/produtos/${produto.id}/metricas`);
        return montarLinha(produto, metricas);
      } catch {
        // Um produto sem métricas não invalida o painel inteiro.
        return null;
      }
    });

    const linhas = brutos.filter(Boolean);

    if (linhas.length === 0) {
      content.innerHTML = '';
      content.appendChild(emptyState({
        titulo: 'Nenhuma métrica disponível',
        msg: 'O motor preditivo ainda não foi executado. Rode o recálculo na tela de importação.',
        acao: { label: 'Ir para Importar', href: 'importar.html' },
      }));
      return;
    }

    renderConteudo(linhas, produtos.length);

  } catch (err) {
    content.innerHTML = '';
    toast.erro(err.detail || 'Erro ao carregar métricas');
  }
}

function renderConteudo(linhas, totalProdutos) {
  content.innerHTML = '';

  const cobertura = document.createElement('p');
  cobertura.className = 'text-meta';
  cobertura.style.marginBottom = '16px';
  cobertura.textContent = `${linhas.length} de ${totalProdutos} produtos têm métricas calculadas.`;
  content.appendChild(cobertura);

  // KPIs agregados — média das métricas por produto
  const ag = {
    mapeHW: media(linhas.map(l => l.mapeHW)),
    mapeProphet: media(linhas.map(l => l.mapeProphet)),
    rmseHW: media(linhas.map(l => l.rmseHW)),
    rmseProphet: media(linhas.map(l => l.rmseProphet)),
    maeHW: media(linhas.map(l => l.maeHW)),
    maeProphet: media(linhas.map(l => l.maeProphet)),
  };

  const kpiGrid = document.createElement('div');
  kpiGrid.className = 'kpi-grid';
  kpiGrid.style.gridTemplateColumns = 'repeat(3, 1fr)';
  kpiGrid.appendChild(metricCard('MAPE', ag.mapeHW, ag.mapeProphet, '%'));
  kpiGrid.appendChild(metricCard('RMSE', ag.rmseHW, ag.rmseProphet, ''));
  kpiGrid.appendChild(metricCard('MAE', ag.maeHW, ag.maeProphet, ''));
  content.appendChild(kpiGrid);

  // Quantos produtos cada modelo venceu
  const vitorias = linhas.reduce((acc, l) => {
    if (l.selecionado) acc[l.selecionado] = (acc[l.selecionado] || 0) + 1;
    return acc;
  }, {});
  const placar = document.createElement('div');
  placar.className = 'card';
  placar.style.marginBottom = '20px';
  placar.innerHTML = `
    <div class="label" style="margin-bottom:10px">Modelo selecionado pelo motor</div>
    <div style="display:flex; gap:24px; flex-wrap:wrap">
      ${Object.values(ROTULO).map(nome => `
        <div>
          <div class="tabular" style="font-size:24px; font-weight:500">${vitorias[nome] || 0}</div>
          <div class="text-meta">${nome}</div>
        </div>
      `).join('')}
    </div>
  `;
  content.appendChild(placar);

  // Gráfico de barras
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
    renderGrafico(linhas);
  });

  renderGrafico(linhas);

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
        <th>Selecionado</th>
      </tr></thead>
      <tbody>
        ${linhas.map(l => {
          const badgeCls = l.selecionado === 'Prophet' ? 'badge-info' : 'badge-primary';
          return `<tr>
            <td>${l.nome}</td>
            <td class="tabular">${fmt(l.mapeHW, '%')}</td>
            <td class="tabular">${fmt(l.mapeProphet, '%')}</td>
            <td class="tabular">${fmt(l.rmseHW)}</td>
            <td class="tabular">${fmt(l.rmseProphet)}</td>
            <td class="tabular">${fmt(l.maeHW)}</td>
            <td class="tabular">${fmt(l.maeProphet)}</td>
            <td>${l.selecionado ? `<span class="badge ${badgeCls}">${l.selecionado}</span>` : '—'}</td>
          </tr>`;
        }).join('')}
      </tbody>
    </table>
  `;
  content.appendChild(tableCard);
}

function fmt(valor, unidade = '') {
  return valor == null ? '—' : numero(valor, 2) + unidade;
}

function renderGrafico(linhas) {
  const canvas = document.getElementById('chart-comparativo');
  if (!canvas) return;

  if (chartInstance) chartInstance.destroy();

  const keyHW = metricaAtual + 'HW';
  const keyPro = metricaAtual + 'Prophet';

  chartInstance = barras(canvas, {
    labels: linhas.map(l => l.nome.split(' ').slice(0, 2).join(' ')),
    series: [
      { label: 'Holt-Winters', data: linhas.map(l => l[keyHW] ?? 0), cor: '#1F4A30' },
      { label: 'Prophet', data: linhas.map(l => l[keyPro] ?? 0), cor: '#2E5A78' },
    ],
  });
}

function metricCard(label, hw, pro, unidade) {
  const card = document.createElement('div');
  card.className = 'card';

  const hwVal = fmt(hw, unidade);
  const proVal = fmt(pro, unidade);
  const temAmbos = hw != null && pro != null;
  const vencedorHW = temAmbos && hw < pro;   // todas as três métricas: menor é melhor
  const diff = temAmbos ? numero(Math.abs(hw - pro), 2) + unidade : '—';

  card.innerHTML = `
    <div class="label" style="margin-bottom:14px">${label} médio</div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px">
      <div>
        <div class="text-meta" style="margin-bottom:4px">Holt-Winters ${temAmbos && vencedorHW ? '<span class="badge badge-primary" style="margin-left:4px">melhor</span>' : ''}</div>
        <div class="tabular" style="font-size:24px; font-weight:500">${hwVal}</div>
      </div>
      <div>
        <div class="text-meta" style="margin-bottom:4px">Prophet ${temAmbos && !vencedorHW ? '<span class="badge badge-info" style="margin-left:4px">melhor</span>' : ''}</div>
        <div class="tabular" style="font-size:24px; font-weight:500">${proVal}</div>
      </div>
    </div>
    <div class="text-meta" style="margin-top:10px">Diferença: ${diff} (quanto menor, melhor)</div>
  `;

  return card;
}

carregarComparativo();
