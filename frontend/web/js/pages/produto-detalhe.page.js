import { requireAuth } from '../core/auth.js';
import { apiGet, apiPatch } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { kpiCard } from '../components/kpiCard.js';
import { statusBadge } from '../components/statusBadge.js';
import { linha } from '../components/charts.js';
import { toast } from '../components/toast.js';
import { skeletonKpiGrid, skeletonChart } from '../components/skeleton.js';
import { numero, dataBR } from '../core/format.js';
import { iconArrowLeft, iconTrend, iconPencil, iconCheck, iconX } from '../components/icons.js';

requireAuth();
const page = renderLayout('estoque');

const params = new URLSearchParams(window.location.search);
const produtoId = params.get('id');

if (!produtoId) {
  window.location.replace('estoque.html');
}

// Loading
page.innerHTML = '';
page.appendChild(skeletonKpiGrid(3));
page.appendChild(skeletonChart());

async function carregarDetalhe() {
  try {
    const p = await apiGet(`/produtos/${produtoId}/detalhe`);

    page.innerHTML = '';

    // Voltar
    const btnVoltar = document.createElement('a');
    btnVoltar.href = 'estoque.html';
    btnVoltar.className = 'btn btn-tertiary btn-sm';
    btnVoltar.style.marginBottom = '14px';
    btnVoltar.innerHTML = `${iconArrowLeft(14)} Voltar para estoque`;
    page.appendChild(btnVoltar);

    // Header
    const header = document.createElement('div');
    header.className = 'row-between';
    header.style.cssText = 'margin-bottom:24px; flex-wrap:wrap; gap:12px;';
    const headerLeft = document.createElement('div');
    headerLeft.innerHTML = `
      <h1 class="page-title">${p.nome}</h1>
      <p class="page-subtitle">${p.categoria || 'sem categoria'}${p.classe ? ` · classe ${p.classe}` : ''}</p>
    `;
    header.appendChild(headerLeft);
    let headerBadge = statusBadge(p.semaforo);
    header.appendChild(headerBadge);
    page.appendChild(header);

    // Banner quando o motor ainda não rodou para este produto
    if (p.semCalculo || p.semPrevisao) {
      const banner = document.createElement('div');
      banner.className = 'banner banner-warning';
      banner.style.marginBottom = '20px';
      banner.innerHTML = `
        <div class="banner-body">
          <strong>Sem previsão para este produto.</strong>
          <small>O motor preditivo ainda não gerou estatísticas de demanda — importe vendas com histórico suficiente e execute o recálculo.</small>
        </div>
        <a href="importar.html" class="btn btn-secondary btn-sm">Ir para Importar</a>
      `;
      page.appendChild(banner);
    }

    // Grid: conteúdo principal + side panel
    const grid = document.createElement('div');
    grid.className = 'detail-grid';

    // === Coluna principal ===
    const mainCol = document.createElement('div');
    mainCol.className = 'stack';

    // Gráfico — o backend devolve apenas a série prevista (até 30 pontos)
    if (p.previsoes.length > 0) {
      const chartCard = document.createElement('div');
      chartCard.className = 'card';
      chartCard.innerHTML = `
        <div class="row-between" style="margin-bottom:6px">
          <h3>Demanda prevista</h3>
          <span class="text-meta">${p.previsoes.length} dias · modelo selecionado pelo motor</span>
        </div>
        <div style="height:260px"><canvas id="chart-demanda"></canvas></div>
      `;
      mainCol.appendChild(chartCard);
    }

    // KPIs
    const kpiGrid = document.createElement('div');
    kpiGrid.className = 'kpi-grid';
    kpiGrid.style.gridTemplateColumns = 'repeat(3, 1fr)';
    kpiGrid.style.marginBottom = '0';

    kpiGrid.appendChild(kpiCard({
      titulo: 'Demanda média/dia',
      valor: p.demandaMedia != null ? numero(p.demandaMedia, 1) : '—',
      sub: `${p.unidade}/dia`,
    }));

    kpiGrid.appendChild(kpiCard({
      titulo: 'Variabilidade',
      valor: p.desvioPadrao != null ? `±${numero(p.desvioPadrao, 1)}` : '—',
      sub: p.cv != null ? `desvio-padrão · CV ${numero(p.cv * 100, 0)}%` : 'desvio-padrão da demanda',
    }));

    const tendLabel = p.tendencia || '—';
    const tendCor = p.tendencia === 'crescente' ? 'var(--status-ok)'
      : p.tendencia === 'decrescente' ? 'var(--status-critico)' : null;
    const trendIcon = p.tendencia === 'decrescente'
      ? `<span style="display:inline-flex;transform:rotate(180deg)">${iconTrend(16)}</span>`
      : p.tendencia === 'crescente' ? iconTrend(16) : '';
    kpiGrid.appendChild(kpiCard({
      titulo: 'Tendência',
      valor: `${trendIcon} ${tendLabel}`,
      sub: p.tendenciaPercentual != null
        ? `${p.tendenciaPercentual > 0 ? '+' : ''}${numero(p.tendenciaPercentual, 1)}% (primeiros vs. últimos 14 dias)`
        : 'sem cálculo',
      cor: tendCor,
    }));

    mainCol.appendChild(kpiGrid);

    // Tabela da série prevista
    if (p.previsoes.length > 0) {
      const serieCard = document.createElement('div');
      serieCard.className = 'card';
      serieCard.innerHTML = `<h3 style="margin-bottom:14px">Série prevista</h3>`;
      const table = document.createElement('table');
      table.className = 'table';
      table.innerHTML = `
        <thead><tr><th>Data</th><th>Quantidade prevista</th></tr></thead>
        <tbody>
          ${p.previsoes.map(pt => `
            <tr>
              <td>${dataBR(pt.data)}</td>
              <td class="tabular">${pt.quantidade != null ? numero(pt.quantidade, 2) : '—'} ${p.unidade}</td>
            </tr>
          `).join('')}
        </tbody>
      `;
      serieCard.appendChild(table);
      mainCol.appendChild(serieCard);
    }

    grid.appendChild(mainCol);

    // === Side panel ===
    const side = document.createElement('div');
    side.className = 'side-panel';

    const sideCard = document.createElement('div');
    sideCard.className = 'card';

    // Estoque atual (editável)
    const estoqueBlock = document.createElement('div');
    estoqueBlock.style.marginBottom = '16px';
    const estoqueOriginal = p.estoque;
    let foiAjustado = false;

    function renderEstoqueDisplay() {
      estoqueBlock.innerHTML = `
        <div class="label">Estoque atual</div>
        <div style="display:flex; align-items:center; gap:8px; margin-top:8px">
          <span style="font-size:32px; font-weight:500; font-variant-numeric:tabular-nums; line-height:1.1">
            ${p.estoque} <span style="font-size:16px; color:var(--cor-texto-sec); font-weight:400">${p.unidade}</span>
          </span>
          <button type="button" class="btn btn-tertiary btn-sm" id="btn-edit-estoque" title="Editar estoque" style="padding:4px">${iconPencil(14)}</button>
        </div>
        ${foiAjustado ? `<div style="margin-top:6px; display:flex; align-items:center; gap:8px">
          <span class="badge badge-warning" style="font-size:11px">ajustado manualmente</span>
          <a href="#" id="btn-desfazer-estoque" style="font-size:12px; color:var(--cor-primaria)">desfazer</a>
        </div>` : ''}
      `;
      estoqueBlock.querySelector('#btn-edit-estoque').addEventListener('click', renderEstoqueEdit);
      if (foiAjustado) {
        estoqueBlock.querySelector('#btn-desfazer-estoque').addEventListener('click', async (e) => {
          e.preventDefault();
          await salvarEstoque(estoqueOriginal, 'Estoque revertido ao valor original');
        });
      }
    }

    function renderEstoqueEdit() {
      let val = p.estoque;
      estoqueBlock.innerHTML = `
        <div class="label">Estoque atual</div>
        <div style="display:flex; align-items:center; gap:6px; margin-top:8px">
          <input type="number" class="input" id="edit-estoque-input" value="${val}" min="0" style="width:100px; font-size:18px; padding:6px 10px">
          <button type="button" class="btn btn-primary btn-sm" id="btn-save-estoque" style="padding:4px 8px">${iconCheck(14)}</button>
          <button type="button" class="btn btn-tertiary btn-sm" id="btn-cancel-estoque" style="padding:4px 8px">${iconX(14)}</button>
        </div>
      `;
      const input = estoqueBlock.querySelector('#edit-estoque-input');
      input.select();
      input.addEventListener('input', (e) => { val = Math.max(0, Math.round(+e.target.value) || 0); });
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') salvarEstoque(val);
        if (e.key === 'Escape') renderEstoqueDisplay();
      });
      estoqueBlock.querySelector('#btn-cancel-estoque').addEventListener('click', renderEstoqueDisplay);
      estoqueBlock.querySelector('#btn-save-estoque').addEventListener('click', () => salvarEstoque(val));
    }

    /** PATCH /api/produtos/{id}/estoque → body { estoqueAtual } (traduzido no apiClient). */
    async function salvarEstoque(valor, mensagem) {
      try {
        const resp = await apiPatch(`/produtos/${produtoId}/estoque`, { estoqueAtual: valor });
        p.estoque = resp.estoque ?? valor;
        p.pontoReposicao = resp.pontoReposicao ?? p.pontoReposicao;
        p.estoqueSeguranca = resp.estoqueSeguranca ?? p.estoqueSeguranca;
        p.semaforo = resp.semaforo;
        p.qtdSugerida = p.pontoReposicao != null
          ? Math.max(0, Math.ceil(p.pontoReposicao + (p.estoqueSeguranca ?? 0) - p.estoque))
          : null;
        foiAjustado = (p.estoque !== estoqueOriginal);
        toast.sucesso(mensagem || `Estoque atualizado para ${p.estoque}`);
        renderEstoqueDisplay();
        renderStats();
        const novo = statusBadge(p.semaforo);
        headerBadge.replaceWith(novo);
        headerBadge = novo;
      } catch (err) {
        toast.erro(err.detail || 'Erro ao atualizar estoque');
        renderEstoqueDisplay();
      }
    }

    renderEstoqueDisplay();
    sideCard.appendChild(estoqueBlock);

    // Stats de reposição — todos vêm do motor; null = ainda não calculado
    const statsWrap = document.createElement('div');
    sideCard.appendChild(statsWrap);

    function renderStats() {
      const un = p.unidade;
      const precisaPedir = p.pontoReposicao != null ? p.estoque <= p.pontoReposicao : null;
      const diasTxt = p.diasRuptura == null ? '—'
        : p.diasRuptura <= 0 ? 'zerado'
        : `${numero(p.diasRuptura, 1)} dias`;

      const stats = [
        {
          label: 'Você precisa pedir?',
          value: precisaPedir == null ? '—' : (precisaPedir ? 'Sim' : 'Não'),
          color: precisaPedir == null ? null : (precisaPedir ? 'var(--status-critico)' : 'var(--status-ok)'),
        },
      ];
      if (precisaPedir && p.qtdSugerida) {
        stats.push({ label: 'Quanto pedir (sugerido)', value: `${p.qtdSugerida} ${un}`, color: 'var(--cor-primaria)' });
      }
      stats.push(
        { label: 'Ponto de reposição', value: p.pontoReposicao != null ? `${numero(p.pontoReposicao, 1)} ${un}` : '—' },
        { label: 'Estoque de segurança', value: p.estoqueSeguranca != null ? `${numero(p.estoqueSeguranca, 1)} ${un}` : '—' },
        { label: 'Dias até ruptura', value: diasTxt },
        { label: 'Último cálculo', value: p.dataUltimoCalculo ? dataBR(String(p.dataUltimoCalculo).slice(0, 10)) : '—' },
      );

      statsWrap.innerHTML = stats.map(s =>
        `<div class="side-stat"><span class="label">${s.label}</span><span class="value tabular" ${s.color ? `style="color:${s.color}"` : ''}>${s.value}</span></div>`
      ).join('');
    }

    renderStats();

    // Botões.
    // "Editar parâmetros" fica desabilitado: PATCH /api/produtos/{id}/parametros
    // ainda não existe no backend (pendência P-01 do backlog de integração).
    const btns = document.createElement('div');
    btns.className = 'stack-tight';
    btns.style.marginTop = '16px';
    btns.innerHTML = `
      <button class="btn btn-primary btn-block" id="btn-marcar-pedido">Marcar para pedido</button>
      <button class="btn btn-secondary btn-block" id="btn-editar-params" disabled
        title="Indisponível: o backend ainda não expõe endpoint para editar lead time e nível de serviço.">
        Editar parâmetros
      </button>
      <span class="text-meta" style="text-align:center; display:block">Lead time e nível de serviço ainda não são editáveis.</span>
    `;
    sideCard.appendChild(btns);

    side.appendChild(sideCard);
    grid.appendChild(side);
    page.appendChild(grid);

    // Renderizar gráfico da série prevista
    if (p.previsoes.length > 0) {
      linha(document.getElementById('chart-demanda'), {
        labels: p.previsoes.map(pt => dataBR(pt.data)),
        historico: p.previsoes.map(pt => pt.quantidade ?? 0),
        labelHist: 'Demanda prevista',
      });
    }

    // Marcar para pedido (estado local — não há endpoint de pedidos)
    const btnPedido = document.getElementById('btn-marcar-pedido');
    btnPedido.title = 'Marcação local — não é gravada no servidor';
    let marcado = false;
    btnPedido.addEventListener('click', () => {
      marcado = !marcado;
      btnPedido.className = `btn ${marcado ? 'btn-tertiary' : 'btn-primary'} btn-block`;
      btnPedido.innerHTML = marcado ? `${iconCheck(14)} Pedido marcado` : 'Marcar para pedido';
    });

  } catch (err) {
    page.innerHTML = '';
    if (err.status === 404) {
      page.innerHTML = `<div class="empty-state"><div class="empty-state-title">Produto não encontrado</div><a href="estoque.html" class="btn btn-primary" style="margin-top:16px">Voltar ao estoque</a></div>`;
    } else {
      toast.erro(err.detail || 'Erro ao carregar produto');
    }
  }
}

carregarDetalhe();
