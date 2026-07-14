/**
 * Componentes de loading skeleton reutilizáveis.
 */

export function skeletonKpiGrid(qtd = 4) {
  const grid = document.createElement('div');
  grid.className = 'kpi-grid';
  for (let i = 0; i < qtd; i++) {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="skeleton skeleton-text" style="width:40%"></div>
      <div class="skeleton skeleton-title" style="width:60%"></div>
      <div class="skeleton skeleton-text" style="width:50%"></div>
    `;
    grid.appendChild(card);
  }
  return grid;
}

export function skeletonChart() {
  const el = document.createElement('div');
  el.className = 'card';
  el.innerHTML = '<div class="skeleton skeleton-chart"></div>';
  return el;
}

export function skeletonTable(linhas = 5, colunas = 4) {
  const card = document.createElement('div');
  card.className = 'card';
  card.style.padding = '0';
  let html = '<table class="table"><thead><tr>';
  for (let c = 0; c < colunas; c++) {
    html += '<th><div class="skeleton skeleton-text" style="width:60%"></div></th>';
  }
  html += '</tr></thead><tbody>';
  for (let r = 0; r < linhas; r++) {
    html += '<tr>';
    for (let c = 0; c < colunas; c++) {
      html += `<td><div class="skeleton skeleton-text" style="width:${50 + Math.random() * 30}%"></div></td>`;
    }
    html += '</tr>';
  }
  html += '</tbody></table>';
  card.innerHTML = html;
  return card;
}
