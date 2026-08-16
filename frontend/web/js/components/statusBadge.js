/**
 * Semáforo de reposição.
 *
 * A régua oficial (contrato da API) é relativa ao ponto de reposição calculado
 * pelo motor — não a cortes fixos de dias. Quando o motor ainda não rodou, o
 * semáforo é `null` e a tela mostra o estado "sem cálculo" em vez de fingir OK.
 */

const MAPA = {
  critico: { css: 'badge-danger', dot: 'dot-danger', label: 'crítico' },
  atencao: { css: 'badge-warning', dot: 'dot-warning', label: 'atenção' },
  ok: { css: 'badge-success', dot: 'dot-success', label: 'ok' },
  indefinido: { css: 'badge-neutral', dot: 'dot-neutral', label: 'sem cálculo' },
};

function cfgDe(semaforo) {
  return MAPA[semaforo] || MAPA.indefinido;
}

/**
 * Badge de semáforo (dot + label).
 * @param {'critico'|'atencao'|'ok'|null} semaforo
 * @returns {HTMLElement}
 */
export function statusBadge(semaforo) {
  const cfg = cfgDe(semaforo);
  const el = document.createElement('span');
  el.className = `badge ${cfg.css}`;
  el.innerHTML = `<span class="dot ${cfg.dot}"></span>${cfg.label}`;
  if (!semaforo) el.title = 'O motor preditivo ainda não calculou o ponto de reposição deste produto.';
  return el;
}

/**
 * Apenas o dot colorido.
 * @param {'critico'|'atencao'|'ok'|null} semaforo
 * @returns {HTMLElement}
 */
export function statusDot(semaforo) {
  const cfg = cfgDe(semaforo);
  const el = document.createElement('span');
  el.className = `dot ${cfg.dot}`;
  return el;
}

/** Rótulo curto para uso em texto. */
export function statusLabel(semaforo) {
  return cfgDe(semaforo).label;
}
