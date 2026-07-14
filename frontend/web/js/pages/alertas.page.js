import { requireAuth } from '../core/auth.js';
import { apiGet } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { toast } from '../components/toast.js';
import { emptyState } from '../components/emptyState.js';
import { skeletonTable } from '../components/skeleton.js';
import { iconCheck } from '../components/icons.js';

requireAuth();
const page = renderLayout('alertas');

page.innerHTML = `
  <div class="page-header">
    <div>
      <h1 class="page-title">Produtos para pedir agora</h1>
      <p class="page-subtitle" id="subtitle"></p>
    </div>
    <a href="sugestao-compra.html" class="btn btn-primary">Gerar relatório de compra</a>
  </div>
  <div id="alertas-container"></div>
`;

const container = document.getElementById('alertas-container');
container.appendChild(skeletonTable(6, 5));

// Estado local de "marcado como pedido"
const pedidos = {};

async function carregarAlertas() {
  try {
    const alertas = await apiGet('/alertas');

    container.innerHTML = '';

    if (!alertas || alertas.length === 0) {
      document.getElementById('subtitle').textContent = '';
      container.appendChild(emptyState({
        titulo: 'Nenhum produto em risco',
        msg: 'Seu estoque está em dia. Nenhum produto precisa ser pedido agora.',
      }));
      return;
    }

    // Ordenar por urgência
    alertas.sort((a, b) => a.diasRuptura - b.diasRuptura);
    const proximos3 = alertas.filter(p => p.diasRuptura <= 3).length;
    document.getElementById('subtitle').textContent =
      `${proximos3} produtos precisam ser pedidos nos próximos 3 dias · ${alertas.length} no total`;

    const lista = document.createElement('div');
    lista.className = 'stack-tight';

    alertas.forEach(p => {
      const isCritico = p.diasRuptura < 3;
      const row = document.createElement('div');
      row.className = `alert-row ${isCritico ? 'critical' : 'warning'}`;

      // Info do produto
      const info = document.createElement('div');
      info.innerHTML = `
        <div style="font-weight:500; margin-bottom:2px">${p.nome}</div>
        <div class="text-meta">${p.categoria || ''} · estoque atual ${p.estoque} ${p.unidade || 'un'}</div>
      `;

      // Urgência
      const urgencia = document.createElement('div');
      const diasText = p.diasRuptura === 0 ? 'Já zerou' : `Vai faltar em ${p.diasRuptura} ${p.diasRuptura === 1 ? 'dia' : 'dias'}`;
      urgencia.innerHTML = `
        <div style="font-size:18px; font-weight:500; color:${isCritico ? 'var(--status-critico)' : 'var(--status-atencao)'}">${diasText}</div>
        <div class="text-meta">lead time fornecedor: ${p.leadTime || '—'} dias</div>
      `;

      // Sugestão
      const sugestao = document.createElement('div');
      sugestao.style.textAlign = 'right';
      sugestao.innerHTML = `
        <div style="font-size:16px; font-weight:500; color:var(--cor-primaria)">Pedir ${p.qtdSugerida || '—'} ${p.unidade || 'un'}</div>
        <div class="text-meta">${p.fornecedor || ''}</div>
      `;

      // Botão detalhe
      const btnDetalhe = document.createElement('a');
      btnDetalhe.href = `produto-detalhe.html?id=${p.id}`;
      btnDetalhe.className = 'btn btn-secondary btn-sm';
      btnDetalhe.textContent = 'Detalhe';

      // Botão marcar como pedido
      const btnPedido = document.createElement('button');
      btnPedido.className = `btn ${pedidos[p.id] ? 'btn-tertiary' : 'btn-primary'} btn-sm`;
      btnPedido.innerHTML = pedidos[p.id] ? `${iconCheck(14)} Pedido` : 'Marcar como pedido';
      btnPedido.addEventListener('click', () => {
        pedidos[p.id] = !pedidos[p.id];
        btnPedido.className = `btn ${pedidos[p.id] ? 'btn-tertiary' : 'btn-primary'} btn-sm`;
        btnPedido.innerHTML = pedidos[p.id] ? `${iconCheck(14)} Pedido` : 'Marcar como pedido';
      });

      row.append(info, urgencia, sugestao, btnDetalhe, btnPedido);
      lista.appendChild(row);
    });

    container.appendChild(lista);

  } catch (err) {
    container.innerHTML = '';
    toast.erro(err.detail || 'Erro ao carregar alertas');
  }
}

carregarAlertas();
