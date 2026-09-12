import { requireAuth } from '../core/auth.js';
import { apiGet } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { toast } from '../components/toast.js';
import { emptyState } from '../components/emptyState.js';
import { skeletonTable } from '../components/skeleton.js';
import { numero } from '../core/format.js';
import { iconCheck } from '../components/icons.js';

requireAuth();
const page = renderLayout('alertas');

page.innerHTML = `
  <div class="page-header">
    <div>
      <h1 class="page-title">Produtos para pedir agora</h1>
      <p class="page-subtitle" id="subtitle"></p>
    </div>
  </div>
  <div id="alertas-container"></div>
`;

const container = document.getElementById('alertas-container');
container.appendChild(skeletonTable(6, 5));

// Estado local de "marcado como pedido" (não persiste — não há endpoint)
const pedidos = {};

const ORDEM = { critico: 0, atencao: 1, ok: 2 };

/**
 * Quanto pedir: subir o estoque até o ponto de reposição e repor o colchão de
 * segurança. O `AlertaResponse` não traz o estoque de segurança, por isso a
 * página cruza com `GET /produtos` (uma chamada, não N).
 */
function calcularSugestao(alerta, estoqueSeguranca) {
  if (alerta.pontoReposicao == null) return null;
  const alvo = alerta.pontoReposicao + (estoqueSeguranca ?? 0);
  return Math.max(0, Math.ceil(alvo - alerta.estoque));
}

async function carregarAlertas() {
  try {
    const [alertas, produtos] = await Promise.all([
      apiGet('/alertas'),
      apiGet('/produtos'),
    ]);

    container.innerHTML = '';

    if (!alertas || alertas.length === 0) {
      const semCalculo = (produtos || []).filter(p => p.semCalculo).length;
      document.getElementById('subtitle').textContent = '';
      container.appendChild(emptyState({
        titulo: semCalculo > 0 ? 'Nenhum alerta calculado' : 'Nenhum produto em risco',
        msg: semCalculo > 0
          ? `${semCalculo} produtos ainda estão sem ponto de reposição — rode o motor preditivo para gerar os alertas.`
          : 'Seu estoque está em dia. Nenhum produto precisa ser pedido agora.',
        acao: semCalculo > 0 ? { label: 'Ir para Importar', href: 'importar.html' } : undefined,
      }));
      return;
    }

    // Índice de estoque de segurança e unidade por produto
    const porId = new Map((produtos || []).map(p => [p.id, p]));

    alertas.sort((a, b) => (ORDEM[a.semaforo] ?? 3) - (ORDEM[b.semaforo] ?? 3)
      || (a.diasRuptura ?? 1e9) - (b.diasRuptura ?? 1e9));

    const criticos = alertas.filter(a => a.semaforo === 'critico').length;
    document.getElementById('subtitle').textContent =
      `${criticos} ${criticos === 1 ? 'produto está' : 'produtos estão'} no ou abaixo do ponto de reposição · ${alertas.length} no total`;

    // Produtos sem cálculo ficam fora da lista de alertas — avisar explicitamente.
    const semCalculo = (produtos || []).filter(p => p.semCalculo).length;
    if (semCalculo > 0) {
      const aviso = document.createElement('div');
      aviso.className = 'banner banner-warning';
      aviso.style.marginBottom = '16px';
      aviso.innerHTML = `
        <div class="banner-body">
          <strong>Lista incompleta.</strong>
          <small>${semCalculo} produtos ainda não têm ponto de reposição e por isso não aparecem aqui.</small>
        </div>
      `;
      container.appendChild(aviso);
    }

    const lista = document.createElement('div');
    lista.className = 'stack-tight';

    alertas.forEach(a => {
      const ref = porId.get(a.id);
      const un = ref?.unidade || 'un';
      const isCritico = a.semaforo === 'critico';
      const sugestao = calcularSugestao(a, ref?.estoqueSeguranca);

      const row = document.createElement('div');
      row.className = `alert-row ${isCritico ? 'critical' : 'warning'}`;

      // Info do produto
      const info = document.createElement('div');
      info.innerHTML = `
        <div style="font-weight:500; margin-bottom:2px">${a.nome}</div>
        <div class="text-meta">${ref?.categoria || ''}${ref?.categoria ? ' · ' : ''}estoque atual ${a.estoque} ${un} · ponto de reposição ${numero(a.pontoReposicao ?? 0, 1)} ${un}</div>
      `;

      // Urgência
      const urgencia = document.createElement('div');
      const diasText = a.diasRuptura == null
        ? 'Sem previsão de ruptura'
        : a.diasRuptura <= 0
          ? 'Já zerou'
          : `Vai faltar em ${numero(a.diasRuptura, 1)} ${a.diasRuptura === 1 ? 'dia' : 'dias'}`;
      urgencia.innerHTML = `
        <div style="font-size:18px; font-weight:500; color:${isCritico ? 'var(--status-critico)' : 'var(--status-atencao)'}">${diasText}</div>
        <div class="text-meta">lead time do fornecedor: ${a.leadTime ?? '—'} dias</div>
      `;

      // Sugestão
      const sugestaoEl = document.createElement('div');
      sugestaoEl.style.textAlign = 'right';
      sugestaoEl.innerHTML = sugestao != null
        ? `<div style="font-size:16px; font-weight:500; color:var(--cor-primaria)">Pedir ${sugestao} ${un}</div>
           <div class="text-meta">até o ponto de reposição + segurança</div>`
        : `<div class="text-meta">sem sugestão</div>`;

      // Botão detalhe
      const btnDetalhe = document.createElement('a');
      btnDetalhe.href = `produto-detalhe.html?id=${a.id}`;
      btnDetalhe.className = 'btn btn-secondary btn-sm';
      btnDetalhe.textContent = 'Detalhe';

      // Botão marcar como pedido (estado apenas visual — sem endpoint)
      const btnPedido = document.createElement('button');
      btnPedido.className = `btn ${pedidos[a.id] ? 'btn-tertiary' : 'btn-primary'} btn-sm`;
      btnPedido.innerHTML = pedidos[a.id] ? `${iconCheck(14)} Pedido` : 'Marcar como pedido';
      btnPedido.title = 'Marcação local — não é gravada no servidor';
      btnPedido.addEventListener('click', () => {
        pedidos[a.id] = !pedidos[a.id];
        btnPedido.className = `btn ${pedidos[a.id] ? 'btn-tertiary' : 'btn-primary'} btn-sm`;
        btnPedido.innerHTML = pedidos[a.id] ? `${iconCheck(14)} Pedido` : 'Marcar como pedido';
      });

      row.append(info, urgencia, sugestaoEl, btnDetalhe, btnPedido);
      lista.appendChild(row);
    });

    container.appendChild(lista);

  } catch (err) {
    container.innerHTML = '';
    toast.erro(err.detail || 'Erro ao carregar alertas');
  }
}

carregarAlertas();
