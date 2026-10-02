import { requireAuth } from '../core/auth.js';
import { apiGet } from '../core/apiClient.js';
import { mockAtivo } from '../core/config.js';
import { renderLayout } from '../components/layout.js';
import { toast } from '../components/toast.js';
import { emptyState } from '../components/emptyState.js';
import { skeletonTable } from '../components/skeleton.js';
import { moedaBR } from '../core/format.js';
import { iconDownload, iconWhatsapp } from '../components/icons.js';

requireAuth();
const page = renderLayout('sugestao');

page.innerHTML = `
  <div class="page-header" id="header-area">
    <div>
      <h1 class="page-title">Relatório de compra sugerido</h1>
      <p class="page-subtitle">Baseado nas previsões e nos pontos de reposição atuais</p>
    </div>
  </div>
  <div id="sugestao-content"></div>
`;

const content = document.getElementById('sugestao-content');
content.appendChild(skeletonTable(8, 5));

// Estado local: checked e qtd por produto
const estado = {};

async function carregarSugestao() {
  // GET /api/sugestao-compra nao existe no backend. Enquanto o endpoint nao for
  // criado, esta tela so funciona em modo mock - e diz isso, em vez de exibir
  // dados ficticios como se fossem reais.
  if (!mockAtivo()) {
    content.innerHTML = '';
    content.appendChild(emptyState({
      titulo: 'Relat\u00f3rio de compra ainda n\u00e3o dispon\u00edvel',
      msg: 'O backend ainda n\u00e3o exp\u00f5e o endpoint de sugest\u00e3o de compra. Enquanto isso, a tela de Alertas mostra o que precisa ser pedido e quanto.',
      acao: { label: 'Ir para Alertas', href: 'alertas.html' },
    }));
    return;
  }
  try {
    const dados = await apiGet('/sugestao-compra');

    content.innerHTML = '';

    if (!dados || !dados.grupos || Object.keys(dados.grupos).length === 0) {
      content.appendChild(emptyState({
        titulo: 'Nenhuma compra sugerida no momento',
        msg: 'Seu estoque está em dia. Nenhum produto precisa ser pedido agora.',
      }));
      return;
    }

    const grupos = dados.grupos;

    // Inicializar estado (checked=true, qtd=qtdSugerida vinda do backend)
    Object.entries(grupos).forEach(([, items]) => {
      items.forEach(it => {
        if (!(it.id in estado)) {
          estado[it.id] = { checked: true, qtd: it.qtdSugerida };
        }
      });
    });

    renderConteudo(grupos);

  } catch (err) {
    content.innerHTML = '';
    toast.erro(err.detail || 'Erro ao carregar sugestão de compra');
  }
}

// Calcula totais apenas dos itens marcados
function calcTotais(grupos) {
  let totalGeral = 0;
  let totalItens = 0;
  Object.values(grupos).forEach(items => {
    items.forEach(it => {
      const s = estado[it.id];
      if (s && s.checked) {
        totalGeral += s.qtd * it.precoMedio;
        totalItens++;
      }
    });
  });
  return { totalGeral, totalItens, totalFornecedores: Object.keys(grupos).length };
}

// Atualiza apenas os valores numéricos sem re-renderizar tudo (evita perder foco do input)
function atualizarTotais(grupos) {
  const { totalGeral, totalItens, totalFornecedores } = calcTotais(grupos);

  // Resumo geral
  const resumoCard = document.getElementById('resumo-card');
  if (resumoCard) {
    resumoCard.querySelector('.tabular').textContent = moedaBR(totalGeral);
    resumoCard.querySelector('.text-meta').textContent = `${totalItens} itens · ${totalFornecedores} fornecedores`;
  }

  // Subtotais por fornecedor
  document.querySelectorAll('[data-forn]').forEach(el => {
    const forn = el.dataset.forn;
    const items = grupos[forn];
    if (!items) return;
    const sub = items.reduce((a, it) => {
      const s = estado[it.id];
      return a + (s && s.checked ? s.qtd * it.precoMedio : 0);
    }, 0);
    el.textContent = moedaBR(sub);
  });

  // Subtotais por linha
  document.querySelectorAll('[data-item-sub]').forEach(el => {
    const id = +el.dataset.itemSub;
    const it = findItem(grupos, id);
    if (!it) return;
    const s = estado[id];
    el.textContent = moedaBR(s.qtd * it.precoMedio);
    el.style.opacity = s.checked ? '1' : '0.35';
  });
}

function findItem(grupos, id) {
  for (const items of Object.values(grupos)) {
    const found = items.find(it => it.id === id);
    if (found) return found;
  }
  return null;
}

function renderConteudo(grupos) {
  content.innerHTML = '';

  const { totalGeral, totalItens, totalFornecedores } = calcTotais(grupos);

  // Card de resumo no header
  const headerArea = document.getElementById('header-area');
  let resumoCard = document.getElementById('resumo-card');
  if (!resumoCard) {
    resumoCard = document.createElement('div');
    resumoCard.id = 'resumo-card';
    resumoCard.className = 'card kpi-card';
    resumoCard.style.cssText = 'min-width:240px; padding:14px;';
    headerArea.appendChild(resumoCard);
  }
  resumoCard.innerHTML = `
    <div class="label">Resumo</div>
    <div style="display:flex; justify-content:space-between; align-items:baseline; margin-top:4px; gap:16px">
      <span class="tabular" style="font-size:22px; font-weight:500">${moedaBR(totalGeral)}</span>
      <span class="text-meta">${totalItens} itens · ${totalFornecedores} fornecedores</span>
    </div>
  `;

  // Um card por fornecedor
  const stack = document.createElement('div');
  stack.className = 'stack';

  Object.entries(grupos).forEach(([forn, items]) => {
    const subtotal = items.reduce((a, it) => {
      const s = estado[it.id];
      return a + (s && s.checked ? s.qtd * it.precoMedio : 0);
    }, 0);

    const card = document.createElement('div');
    card.className = 'card';
    card.style.padding = '0';

    // Cabeçalho do grupo
    const cardHeader = document.createElement('div');
    cardHeader.className = 'row-between';
    cardHeader.style.cssText = 'padding:16px 20px; border-bottom:1px solid var(--cor-borda); flex-wrap:wrap; gap:12px;';
    cardHeader.innerHTML = `
      <div>
        <div style="font-weight:500; font-size:16px">${forn}</div>
        <div class="text-meta">${items.length} itens sugeridos · lead time ${items[0].leadTime} dias</div>
      </div>
      <div class="row" style="gap:8px; align-items:center">
        <div style="text-align:right; margin-right:8px">
          <div class="text-meta">Subtotal</div>
          <div class="tabular" style="font-weight:500" data-forn="${forn}">${moedaBR(subtotal)}</div>
        </div>
        <button class="btn btn-secondary btn-sm btn-pdf" title="Exportar PDF">${iconDownload(14)} PDF</button>
        <button class="btn btn-secondary btn-sm btn-whats" title="Enviar via WhatsApp">${iconWhatsapp(14)} WhatsApp</button>
      </div>
    `;

    // Handlers PDF / WhatsApp (sem endpoint ainda)
    cardHeader.querySelector('.btn-pdf').addEventListener('click', () => {
      toast.info(`Exportação PDF para "${forn}" — aguardando endpoint do backend.`);
    });
    cardHeader.querySelector('.btn-whats').addEventListener('click', () => {
      toast.info(`Envio WhatsApp para "${forn}" — aguardando endpoint do backend.`);
    });

    // Tabela do grupo
    const table = document.createElement('table');
    table.className = 'table';
    table.innerHTML = `
      <thead><tr>
        <th style="width:36px"></th>
        <th>Produto</th>
        <th>Quantidade</th>
        <th>Preço unit.</th>
        <th>Subtotal</th>
      </tr></thead>
    `;

    const tbody = document.createElement('tbody');
    items.forEach(it => {
      const s = estado[it.id];
      const tr = document.createElement('tr');
      tr.style.opacity = s.checked ? '1' : '0.5';
      tr.style.transition = 'opacity 0.15s';

      // Checkbox
      const tdCheck = document.createElement('td');
      const checkbox = document.createElement('div');
      checkbox.className = `checkbox ${s.checked ? 'checked' : ''}`;
      checkbox.addEventListener('click', () => {
        s.checked = !s.checked;
        checkbox.className = `checkbox ${s.checked ? 'checked' : ''}`;
        tr.style.opacity = s.checked ? '1' : '0.5';
        atualizarTotais(grupos);
      });
      tdCheck.appendChild(checkbox);
      tr.appendChild(tdCheck);

      // Nome
      const tdNome = document.createElement('td');
      tdNome.textContent = it.nome;
      tr.appendChild(tdNome);

      // Quantidade editável
      const tdQtd = document.createElement('td');
      const inputQtd = document.createElement('input');
      inputQtd.type = 'number';
      inputQtd.className = 'input';
      inputQtd.style.cssText = 'width:90px; height:32px; padding:0 8px; display:inline-block;';
      inputQtd.value = s.qtd;
      inputQtd.min = '0';
      inputQtd.addEventListener('input', (e) => {
        s.qtd = Math.max(0, Math.round(+e.target.value) || 0);
        atualizarTotais(grupos);
      });
      tdQtd.appendChild(inputQtd);
      const spanUn = document.createElement('span');
      spanUn.className = 'text-meta';
      spanUn.style.marginLeft = '6px';
      spanUn.textContent = it.unidade;
      tdQtd.appendChild(spanUn);
      tr.appendChild(tdQtd);

      // Preço unitário
      const tdPreco = document.createElement('td');
      tdPreco.className = 'tabular';
      tdPreco.textContent = moedaBR(it.precoMedio);
      tr.appendChild(tdPreco);

      // Subtotal do item
      const tdSub = document.createElement('td');
      tdSub.className = 'tabular';
      tdSub.setAttribute('data-item-sub', it.id);
      tdSub.textContent = moedaBR(s.qtd * it.precoMedio);
      tdSub.style.opacity = s.checked ? '1' : '0.35';
      tr.appendChild(tdSub);

      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    card.appendChild(cardHeader);
    card.appendChild(table);
    stack.appendChild(card);
  });

  content.appendChild(stack);

  // Rodapé com ações
  const actions = document.createElement('div');
  actions.className = 'row';
  actions.style.cssText = 'justify-content:flex-end; margin-top:20px; gap:8px;';
  actions.innerHTML = `
    <button class="btn btn-secondary" id="btn-rascunho">Salvar rascunho</button>
    <button class="btn btn-primary" id="btn-confirmar">Confirmar pedidos</button>
  `;
  content.appendChild(actions);

  document.getElementById('btn-rascunho').addEventListener('click', () => {
    toast.info('Rascunho salvo localmente — aguardando endpoint do backend.');
  });
  document.getElementById('btn-confirmar').addEventListener('click', () => {
    const { totalGeral: tg, totalItens: ti } = calcTotais(grupos);
    toast.sucesso(`Pedidos confirmados — ${ti} itens, ${moedaBR(tg)}`);
  });
}

carregarSugestao();
