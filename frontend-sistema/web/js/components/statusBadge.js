/**
 * Retorna o status semáforo baseado em dias até ruptura.
 * @param {number} diasRuptura
 * @returns {'critico'|'atencao'|'ok'}
 */
export function statusClass(diasRuptura) {
  if (diasRuptura < 3) return 'critico';
  if (diasRuptura <= 7) return 'atencao';
  return 'ok';
}

/**
 * Cria um badge de semáforo (dot + label).
 * @param {number} diasRuptura
 * @returns {HTMLElement}
 */
export function statusBadge(diasRuptura) {
  const status = statusClass(diasRuptura);
  const map = {
    critico: { css: 'badge-danger', dot: 'dot-danger', label: 'cr\u00edtico' },
    atencao: { css: 'badge-warning', dot: 'dot-warning', label: 'aten\u00e7\u00e3o' },
    ok:      { css: 'badge-success', dot: 'dot-success', label: 'ok' },
  };
  const cfg = map[status];

  const el = document.createElement('span');
  el.className = `badge ${cfg.css}`;
  el.innerHTML = `<span class="dot ${cfg.dot}"></span>${cfg.label}`;
  return el;
}

/**
 * Cria apenas o dot colorido.
 * @param {number} diasRuptura
 * @returns {HTMLElement}
 */
export function statusDot(diasRuptura) {
  const status = statusClass(diasRuptura);
  const dotMap = { critico: 'dot-danger', atencao: 'dot-warning', ok: 'dot-success' };
  const el = document.createElement('span');
  el.className = `dot ${dotMap[status]}`;
  return el;
}
