/**
 * Cria um cartão de KPI.
 * @param {Object} opts
 * @param {string} opts.titulo - Label do KPI
 * @param {string|number} opts.valor - Valor principal
 * @param {string} [opts.sub] - Contexto abaixo do valor
 * @returns {HTMLElement}
 */
export function kpiCard({ titulo, valor, sub, cor }) {
  const card = document.createElement('div');
  card.className = 'card kpi-card';

  let html = `<span class="label">${titulo}</span>`;
  html += `<span class="kpi-number"${cor ? ` style="color:${cor}"` : ''}>${valor}</span>`;
  if (sub) {
    html += `<span class="kpi-context">${sub}</span>`;
  }

  card.innerHTML = html;
  return card;
}
