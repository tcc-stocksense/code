import { iconBox } from './icons.js';

/**
 * Estado vazio reutilizável.
 * @param {Object} opts
 * @param {string} opts.titulo
 * @param {string} [opts.msg]
 * @param {Object} [opts.acao] - { label, href } para botão de ação
 * @returns {HTMLElement}
 */
export function emptyState({ titulo, msg, acao }) {
  const el = document.createElement('div');
  el.className = 'empty-state';

  let html = iconBox(48);
  html += `<div class="empty-state-title">${titulo}</div>`;
  if (msg) html += `<div class="empty-state-msg">${msg}</div>`;
  if (acao) html += `<a href="${acao.href}" class="btn btn-primary">${acao.label}</a>`;

  el.innerHTML = html;
  return el;
}
