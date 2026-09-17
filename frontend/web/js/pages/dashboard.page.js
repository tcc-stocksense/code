import { requireAuth } from '../core/auth.js';
import { apiGet } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { kpiCard } from '../components/kpiCard.js';
import { statusDot } from '../components/statusBadge.js';
import { linha } from '../components/charts.js';
import { toast } from '../components/toast.js';
import { emptyState } from '../components/emptyState.js';
import { skeletonKpiGrid, skeletonChart, skeletonTable } from '../components/skeleton.js';
import { moedaBRcompacta, dataBR, numero } from '../core/format.js';
import { iconAlert } from '../components/icons.js';

requireAuth();
const page = renderLayout('dashboard');

// Loading state
page.innerHTML = '';
page.appendChild(skeletonKpiGrid(3));
page.appendChild(skeletonChart());
page.appendChild(skeletonTable(5, 4));

async function carregarDashboard() {
  try {
    // A tabela "próximos alertas" sai da mesma fonte da tela de Alertas.
    const [dados, alertas] = await Promise.all([
      apiGet('/dashboard'),
      apiGet('/alertas').catch(() => []),
    ]);

    page.innerHTML = '';

    // Saudação personalizada
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

    // Banner de alerta
    if (dados.risco7Dias > 0) {
      const banner = document.createElement('div');
      banner.className = 'banner banner-warning';
      banner.innerHTML = `
        ${iconAlert()}
        <div class="banner-body">
          <strong>Você tem ${dados.risco7Dias} ${dados.risco7Dias === 1 ? 'produto que precisa' : 'produtos que precisam'} ser ${dados.risco7Dias === 1 ? 'pedido' : 'pedidos'}.</strong>
          <small>${dados.criticoAgora} ${dados.criticoAgora === 1 ? 'rompe' : 'rompem'} em menos de 3 dias.</small>
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
      valor: dados.risco7Dias ?? 0,
      sub: 'nos próximos 7 dias',
    }));
    kpiGrid.appendChild(kpiCard({
      titulo: 'Crítico agora',
      valor: dados.criticoAgora ?? 0,
      // O backend conta `diasAteRuptura < 3` (DashboardService.LIMITE_CRITICO_DIAS),
      // não estoque ≤ ponto de reposição — esse é o critério da tela de Alertas.
      sub: 'produtos que rompem em menos de 3 dias',
      cor: 'var(--status-critico)',
    }));
    // Valor em risco — o backend ainda não expõe esse número e a regra de cálculo
    // (coef. ABRAS) não foi definida; o card fica no lugar, em estado "sem dado".
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
      valor: dados.acuracia != null ? numero(dados.acuracia, 1) + '%' : '—',
      sub: dados.acuracia != null
        ? '100 − MAPE do modelo selecionado'
        : 'motor ainda não executado',
    }));
    page.appendChild(kpiGrid);

    // Gráfico de faturamento — apenas histórico semanal (o backend não projeta faturamento)
    const serie = dados.seriesFaturamento || [];
    if (serie.length > 0) {
      const chartCard = document.createElement('div');
      chartCard.className = 'card';
      chartCard.style.marginBottom = '24px';
      chartCard.innerHTML = `
        <div class="row-between" style="margin-bottom:6px">
          <h3>Faturamento semanal</h3>
          <span class="text-meta">histórico · ${serie.length} semanas</span>
        </div>
        <div style="height:260px"><canvas id="chart-faturamento"></canvas></div>
      `;
      page.appendChild(chartCard);

      // A projeção volta a ser desenhada assim que o backend enviar a série;
      // hoje `projecao` chega vazia e o gráfico mostra só o histórico.
      linha(document.getElementById('chart-faturamento'), {
        labels: serie.map(s => dataBR(s.semana)),
        historico: serie.map(s => s.total),
        projecao: dados.projecao || [],
        labelHist: 'Histórico',
        labelProj: 'Projeção',
      });
    } else {
      const vazio = document.createElement('div');
      vazio.className = 'card';
      vazio.style.marginBottom = '24px';
      vazio.innerHTML = `
        <h3 style="margin-bottom:8px">Faturamento semanal</h3>
        <p class="text-meta">Sem histórico de vendas importado.</p>
      `;
      page.appendChild(vazio);
    }

    // Tabela próximos alertas (top 5)
    const ORDEM = { critico: 0, atencao: 1, ok: 2 };
    const proximos = (alertas || [])
      .filter(a => a.semaforo !== 'ok')   // mesma regra da tela de Alertas (B-02)
      .sort((a, b) => (ORDEM[a.semaforo] ?? 3) - (ORDEM[b.semaforo] ?? 3)
        || (a.diasRuptura ?? 1e9) - (b.diasRuptura ?? 1e9))
      .slice(0, 5);

    if (proximos.length > 0) {
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
            <th>Estoque</th>
            <th>Ponto de reposição</th>
            <th>Até ruptura</th>
            <th></th>
          </tr>
        </thead>
      `;
      const tbody = document.createElement('tbody');
      proximos.forEach(p => {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        tr.addEventListener('click', () => { window.location.href = `produto-detalhe.html?id=${p.id}`; });

        const tdDot = document.createElement('td');
        tdDot.appendChild(statusDot(p.semaforo));
        tr.appendChild(tdDot);

        const diasTxt = p.diasRuptura == null ? '—'
          : p.diasRuptura <= 0 ? 'zerado'
          : `${numero(p.diasRuptura, 1)} dias`;

        // Mesmo motivo do B-01: nada de `innerHTML +=` depois de um appendChild.
        const celula = (texto, className) => {
          const td = document.createElement('td');
          if (className) td.className = className;
          td.textContent = texto;
          return td;
        };
        tr.appendChild(celula(p.nome));
        tr.appendChild(celula(p.estoque, 'tabular'));
        tr.appendChild(celula(p.pontoReposicao != null ? numero(p.pontoReposicao, 1) : '—', 'tabular'));
        tr.appendChild(celula(diasTxt, 'tabular'));

        const tdAcao = document.createElement('td');
        const link = document.createElement('a');
        link.href = `produto-detalhe.html?id=${p.id}`;
        link.className = 'btn btn-tertiary btn-sm';
        link.textContent = 'Detalhe';
        tdAcao.appendChild(link);
        tr.appendChild(tdAcao);

        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      alertCard.appendChild(table);
      page.appendChild(alertCard);
    }

  } catch (err) {
    page.innerHTML = '';
    page.appendChild(emptyState({
      titulo: 'Não foi possível carregar o dashboard',
      msg: err.detail || 'Verifique se o backend está no ar e se há dados importados.',
      acao: { label: 'Ir para Importar', href: 'importar.html' },
    }));
    toast.erro(err.detail || 'Erro ao carregar o dashboard');
  }
}

carregarDashboard();
