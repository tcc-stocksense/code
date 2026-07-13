import { requireAuth } from '../core/auth.js';
import { apiGet } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { kpiCard } from '../components/kpiCard.js';
import { statusDot } from '../components/statusBadge.js';
import { linha } from '../components/charts.js';
import { toast } from '../components/toast.js';
import { emptyState } from '../components/emptyState.js';
import { skeletonKpiGrid, skeletonChart, skeletonTable } from '../components/skeleton.js';
import { moedaBRcompacta } from '../core/format.js';
import { iconAlert } from '../components/icons.js';

requireAuth();
const page = renderLayout('dashboard');

// Loading state
page.innerHTML = '';
page.appendChild(skeletonKpiGrid(4));
page.appendChild(skeletonChart());
page.appendChild(skeletonTable(5, 4));

async function carregarDashboard() {
  try {
    const dados = await apiGet('/dashboard');

    page.innerHTML = '';

    // Saudação personalizada (como no protótipo)
    const header = document.createElement('div');
    header.className = 'stack-tight';
    header.style.marginBottom = '24px';
    const hora = new Date().getHours();
    const saudacao = hora < 12 ? 'Bom dia' : hora < 18 ? 'Boa tarde' : 'Boa noite';
    const dataExtenso = new Date().toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    header.innerHTML = `
      <h1 class="page-title">${saudacao}.</h1>
      <p class="page-subtitle">${dataExtenso}</p>
    `;
    page.appendChild(header);

    // Banner de alerta (só se há produtos em risco)
    if (dados.produtosEmRisco > 0) {
      const banner = document.createElement('div');
      banner.className = 'banner banner-warning';
      banner.innerHTML = `
        ${iconAlert()}
        <div class="banner-body">
          <strong>Você tem ${dados.produtosEmRisco} produtos que precisam ser pedidos.</strong>
          <small>${dados.produtosCriticos || 0} estão em estado crítico (menos de 3 dias).</small>
        </div>
        <a href="alertas.html" class="btn btn-secondary btn-sm">Ver lista</a>
      `;
      page.appendChild(banner);
    }

    // KPIs
    const kpiGrid = document.createElement('div');
    kpiGrid.className = 'kpi-grid';
    kpiGrid.appendChild(kpiCard({
      titulo: 'Risco de faltar',
      valor: dados.produtosEmRisco ?? 0,
      sub: 'nos próximos 7 dias',
    }));
    kpiGrid.appendChild(kpiCard({
      titulo: 'Crítico agora',
      valor: dados.produtosCriticos ?? 0,
      sub: 'menos de 3 dias até zerar',
      cor: 'var(--status-critico)',
    }));
    // Valor em risco — só exibe se confirmado pelo backend
    if (dados.valorEmRisco != null) {
      kpiGrid.appendChild(kpiCard({
        titulo: 'Valor em risco',
        valor: moedaBRcompacta(dados.valorEmRisco),
        sub: 'venda perdida estimada (coef. ABRAS)',
      }));
    } else {
      kpiGrid.appendChild(kpiCard({
        titulo: 'Valor em risco',
        valor: '—',
        sub: 'aguardando confirmação da regra',
      }));
    }
    kpiGrid.appendChild(kpiCard({
      titulo: 'Acurácia do modelo',
      valor: dados.acuracia != null ? dados.acuracia.toFixed(1) + '%' : '—',
      sub: 'MAPE médio últimas 4 semanas',
    }));
    page.appendChild(kpiGrid);

    // Gráfico de faturamento
    if (dados.grafico) {
      const chartCard = document.createElement('div');
      chartCard.className = 'card';
      chartCard.style.marginBottom = '24px';
      chartCard.innerHTML = `
        <div class="row-between" style="margin-bottom:6px">
          <h3>Previsão de faturamento</h3>
          <span class="text-meta">histórico + projeção</span>
        </div>
        <div style="height:260px"><canvas id="chart-faturamento"></canvas></div>
      `;
      page.appendChild(chartCard);

      linha(document.getElementById('chart-faturamento'), {
        labels: dados.grafico.labels,
        historico: dados.grafico.historico,
        projecao: dados.grafico.projecao || [],
        labelHist: 'Histórico',
        labelProj: 'Projeção',
      });
    }

    // Tabela próximos alertas
    if (dados.proximosAlertas && dados.proximosAlertas.length > 0) {
      const alertCard = document.createElement('div');
      alertCard.className = 'card';
      alertCard.innerHTML = `
        <div class="row-between" style="margin-bottom:14px">
          <h3>Próximos alertas de reposição</h3>
          <a href="alertas.html" class="btn btn-tertiary btn-sm">Ver todos</a>
        </div>
      `;
      const table = document.createElement('table');
      table.className = 'table';
      table.innerHTML = `
        <thead>
          <tr>
            <th style="width:24px"></th>
            <th>Produto</th>
            <th>Até ruptura</th>
            <th>Sugestão</th>
            <th></th>
          </tr>
        </thead>
      `;
      const tbody = document.createElement('tbody');
      dados.proximosAlertas.forEach(p => {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        tr.addEventListener('click', () => { window.location.href = `produto-detalhe.html?id=${p.id}`; });

        const tdDot = document.createElement('td');
        tdDot.appendChild(statusDot(p.diasRuptura));
        tr.appendChild(tdDot);

        tr.innerHTML += `
          <td>${p.nome}</td>
          <td class="tabular">${p.diasRuptura === 0 ? 'zerado' : p.diasRuptura + (p.diasRuptura === 1 ? ' dia' : ' dias')}</td>
          <td class="tabular">${p.qtdSugerida != null ? p.qtdSugerida + ' ' + (p.unidade || 'un') : '—'}</td>
          <td><a href="produto-detalhe.html?id=${p.id}" class="btn btn-tertiary btn-sm">Detalhe</a></td>
        `;
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      alertCard.appendChild(table);
      page.appendChild(alertCard);
    }

  } catch (err) {
    page.innerHTML = '';
    if (err.status === 404 || err.detail?.includes('import')) {
      page.appendChild(emptyState({
        titulo: 'Nenhum dado encontrado',
        msg: 'Importe dados para ver o dashboard.',
        acao: { label: 'Ir para Importar', href: 'importar.html' },
      }));
    } else {
      toast.erro(err.detail || 'Erro ao carregar o dashboard');
    }
  }
}

carregarDashboard();
