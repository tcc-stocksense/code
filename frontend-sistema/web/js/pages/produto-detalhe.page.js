import { requireAuth } from '../core/auth.js';
import { apiGet, apiPatch } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { kpiCard } from '../components/kpiCard.js';
import { statusBadge } from '../components/statusBadge.js';
import { linha } from '../components/charts.js';
import { toast } from '../components/toast.js';
import { openModal } from '../components/modal.js';
import { skeletonKpiGrid, skeletonChart } from '../components/skeleton.js';
import { numero } from '../core/format.js';
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
      <p class="page-subtitle">${p.categoria || ''} · classe ${p.classe || ''}</p>
    `;
    header.appendChild(headerLeft);
    let headerBadge = statusBadge(p.diasRuptura);
    header.appendChild(headerBadge);
    page.appendChild(header);

    // Grid: conteúdo principal + side panel
    const grid = document.createElement('div');
    grid.className = 'detail-grid';

    // === Coluna principal ===
    const mainCol = document.createElement('div');
    mainCol.className = 'stack';

    // Gráfico
    if (p.grafico) {
      const chartCard = document.createElement('div');
      chartCard.className = 'card';
      chartCard.innerHTML = `
        <div class="row-between" style="margin-bottom:6px">
          <h3>Demanda diária</h3>
          <span class="text-meta">últimos 90 dias + projeção 30 dias</span>
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
      sub: `${p.unidade || 'un'}/dia`,
    }));

    kpiGrid.appendChild(kpiCard({
      titulo: 'Variabilidade',
      valor: p.desvioPadrao != null ? `±${numero(p.desvioPadrao, 1)}` : '—',
      sub: p.cv != null ? `desvio-padrão · CV ${numero(p.cv * 100, 0)}%` : '',
    }));

    const tendLabel = p.tendencia || 'estável';
    const tendCor = p.tendencia === 'crescente' ? 'var(--status-ok)' : p.tendencia === 'decrescente' ? 'var(--status-critico)' : null;
    const trendIcon = p.tendencia === 'decrescente'
      ? `<span style="display:inline-flex;transform:rotate(180deg)">${iconTrend(16)}</span>`
      : p.tendencia === 'crescente' ? iconTrend(16) : '';
    kpiGrid.appendChild(kpiCard({
      titulo: 'Tendência',
      valor: `${trendIcon} ${tendLabel}`,
      sub: p.tendenciaDelta != null ? `${p.tendenciaDelta > 0 ? '+' : ''}${numero(p.tendenciaDelta * 100, 1)}% nas últimas 2 semanas` : '',
      cor: tendCor,
    }));

    mainCol.appendChild(kpiGrid);

    // Vendas por semana (se disponível)
    if (p.vendasSemana && p.vendasSemana.length > 0) {
      const semanasCard = document.createElement('div');
      semanasCard.className = 'card';
      semanasCard.innerHTML = `<h3 style="margin-bottom:14px">Vendas por semana</h3>`;
      const table = document.createElement('table');
      table.className = 'table';
      table.innerHTML = `
        <thead><tr><th>Semana</th><th>Total vendido</th><th>Média/dia</th></tr></thead>
        <tbody>
          ${p.vendasSemana.map(s => `
            <tr>
              <td>${s.label}</td>
              <td class="tabular">${s.total} ${p.unidade || 'un'}</td>
              <td class="tabular text-secondary">${numero(s.media, 1)} ${p.unidade || 'un'}/dia</td>
            </tr>
          `).join('')}
        </tbody>
      `;
      semanasCard.appendChild(table);
      mainCol.appendChild(semanasCard);
    }

    grid.appendChild(mainCol);

    // === Side panel ===
    const side = document.createElement('div');
    side.className = 'side-panel';

    const sideCard = document.createElement('div');
    sideCard.className = 'card';

    // Estoque atual (editável, com tag "ajustado manualmente" + desfazer)
    const estoqueBlock = document.createElement('div');
    estoqueBlock.style.marginBottom = '16px';
    const estoqueOriginal = p.estoque;
    let foiAjustado = false;

    function renderEstoqueDisplay() {
      estoqueBlock.innerHTML = `
        <div class="label">Estoque atual</div>
        <div style="display:flex; align-items:center; gap:8px; margin-top:8px">
          <span style="font-size:32px; font-weight:500; font-variant-numeric:tabular-nums; line-height:1.1">
            ${p.estoque} <span style="font-size:16px; color:var(--cor-texto-sec); font-weight:400">${p.unidade || 'un'}</span>
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
          try {
            const resp = await apiPatch(`/produtos/${produtoId}/estoque`, { estoque: estoqueOriginal });
            p.estoque = resp.estoque ?? estoqueOriginal;
            aplicarIntel(resp);
            foiAjustado = false;
            toast.sucesso('Estoque revertido ao valor original');
            renderEstoqueDisplay();
            refreshIntel();
          } catch (err) {
            toast.erro(err.detail || 'Erro ao reverter estoque');
          }
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
        if (e.key === 'Enter') salvar();
        if (e.key === 'Escape') renderEstoqueDisplay();
      });
      estoqueBlock.querySelector('#btn-cancel-estoque').addEventListener('click', renderEstoqueDisplay);
      estoqueBlock.querySelector('#btn-save-estoque').addEventListener('click', salvar);

      async function salvar() {
        try {
          const resp = await apiPatch(`/produtos/${produtoId}/estoque`, { estoque: val });
          p.estoque = resp.estoque ?? val;
          aplicarIntel(resp);
          foiAjustado = (p.estoque !== estoqueOriginal);
          toast.sucesso(`Estoque atualizado para ${p.estoque}`);
          renderEstoqueDisplay();
          refreshIntel();
        } catch (err) {
          toast.erro(err.detail || 'Erro ao atualizar estoque');
        }
      }
    }

    renderEstoqueDisplay();
    sideCard.appendChild(estoqueBlock);

    // Stats — derivados pela inteligência de reposição; reagem a mudanças de estoque
    const statsWrap = document.createElement('div');
    sideCard.appendChild(statsWrap);

    function precisaPedir() {
      if (p.precisaPedir != null) return p.precisaPedir;
      if (p.pontoReposicao != null) return p.estoque <= p.pontoReposicao;
      return p.diasRuptura <= 7;
    }

    function renderStats() {
      const un = p.unidade || 'un';
      const pedir = precisaPedir();
      const diasTxt = p.diasRuptura == null ? '—'
        : p.diasRuptura === 0 ? 'zerado'
        : `${p.diasRuptura} ${p.diasRuptura === 1 ? 'dia' : 'dias'}`;

      const stats = [
        { label: 'Você precisa pedir?', value: pedir ? 'Sim' : 'Não', color: pedir ? 'var(--status-critico)' : 'var(--status-ok)' },
      ];
      if (pedir && p.qtdSugerida > 0) {
        stats.push({ label: 'Quanto pedir (sugerido)', value: `${p.qtdSugerida} ${un}`, color: 'var(--cor-primaria)' });
      }
      stats.push(
        { label: 'Ponto de reposição', value: `${p.pontoReposicao ?? '—'} ${un}` },
        { label: 'Estoque de segurança', value: `${p.estoqueSeguranca ?? '—'} ${un}` },
        { label: 'Dias até ruptura', value: diasTxt },
        { label: 'Lead time fornecedor', value: `${p.leadTime ?? '—'} dias` },
        { label: 'Nível de serviço alvo', value: `${p.nivelServico ?? 95}%` },
      );

      statsWrap.innerHTML = stats.map(s =>
        `<div class="side-stat"><span class="label">${s.label}</span><span class="value tabular" ${s.color ? `style="color:${s.color}"` : ''}>${s.value}</span></div>`
      ).join('');
    }

    // Recalcula painel + badge do header após o estoque mudar
    function refreshIntel() {
      renderStats();
      const novo = statusBadge(p.diasRuptura);
      headerBadge.replaceWith(novo);
      headerBadge = novo;
    }

    // Propaga os campos derivados devolvidos pelo backend/mock ao editar o estoque
    function aplicarIntel(resp) {
      if (resp.diasRuptura != null) p.diasRuptura = resp.diasRuptura;
      if (resp.pontoReposicao != null) p.pontoReposicao = resp.pontoReposicao;
      if (resp.estoqueSeguranca != null) p.estoqueSeguranca = resp.estoqueSeguranca;
      if (resp.precisaPedir != null) p.precisaPedir = resp.precisaPedir;
      if (resp.qtdSugerida != null) p.qtdSugerida = resp.qtdSugerida;
    }

    renderStats();

    // Botões
    const btns = document.createElement('div');
    btns.className = 'stack-tight';
    btns.style.marginTop = '16px';
    btns.innerHTML = `
      <button class="btn btn-primary btn-block" id="btn-marcar-pedido">Marcar para pedido</button>
      <button class="btn btn-secondary btn-block" id="btn-editar-params">Editar parâmetros</button>
    `;
    sideCard.appendChild(btns);

    side.appendChild(sideCard);

    // Card fornecedor
    if (p.fornecedor) {
      const fornCard = document.createElement('div');
      fornCard.className = 'card';
      fornCard.style.cssText = 'margin-top:16px; padding:14px;';
      fornCard.innerHTML = `
        <div class="label" style="margin-bottom:8px">Fornecedor</div>
        <div style="font-weight:500">${p.fornecedor}</div>
        ${p.precoMedio != null ? `<div class="text-meta">Preço médio: R$ ${numero(p.precoMedio, 2)}/${p.unidade || 'un'}</div>` : ''}
      `;
      side.appendChild(fornCard);
    }

    grid.appendChild(side);
    page.appendChild(grid);

    // Renderizar gráfico
    if (p.grafico) {
      linha(document.getElementById('chart-demanda'), {
        labels: p.grafico.labels,
        historico: p.grafico.historico,
        projecao: p.grafico.projecao || [],
        labelHist: 'Histórico',
        labelProj: 'Projeção',
      });
    }

    // Marcar para pedido toggle
    const btnPedido = document.getElementById('btn-marcar-pedido');
    let marcado = false;
    btnPedido.addEventListener('click', () => {
      marcado = !marcado;
      btnPedido.className = `btn ${marcado ? 'btn-tertiary' : 'btn-primary'} btn-block`;
      btnPedido.innerHTML = marcado ? `${iconCheck(14)} Pedido marcado` : 'Marcar para pedido';
    });

    // Modal editar parâmetros (read-only se sem endpoint)
    document.getElementById('btn-editar-params').addEventListener('click', () => {
      const form = document.createElement('div');
      form.className = 'stack';
      form.style.gap = '14px';
      form.innerHTML = `
        <div class="field">
          <label class="field-label">Lead time do fornecedor (dias)</label>
          <input type="number" class="input" id="param-lt" value="${p.leadTime || 0}">
        </div>
        <div class="field">
          <label class="field-label">Nível de serviço alvo (%)</label>
          <input type="number" class="input" id="param-ns" value="${p.nivelServico || 95}" min="50" max="99">
          <span class="text-meta">Probabilidade de não faltar o produto dentro do lead time.</span>
        </div>
      `;

      let salvando = false;
      openModal({
        titulo: `Editar parâmetros — ${p.nome}`,
        conteudo: form,
        labelConfirm: 'Salvar parâmetros',
        onConfirm: async (fechar) => {
          if (salvando) return;
          salvando = true;
          const lt = Math.max(0, Math.round(+document.getElementById('param-lt').value) || 0);
          const ns = Math.min(99, Math.max(50, Math.round(+document.getElementById('param-ns').value) || 95));
          try {
            const resp = await apiPatch(`/produtos/${produtoId}/parametros`, { leadTime: lt, nivelServico: ns });
            if (resp.leadTime != null) p.leadTime = resp.leadTime;
            if (resp.nivelServico != null) p.nivelServico = resp.nivelServico;
            aplicarIntel(resp);
            refreshIntel();
            toast.sucesso('Parâmetros atualizados — reposição recalculada');
            fechar();
          } catch (err) {
            salvando = false;
            toast.erro(err.detail || 'Erro ao salvar parâmetros');
          }
        },
      });
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
