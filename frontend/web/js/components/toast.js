let container = null;

function getContainer() {
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  return container;
}

function show(msg, tipo, duracao = 4000) {
  const el = document.createElement('div');
  el.className = `toast toast-${tipo}`;
  el.textContent = msg;
  getContainer().appendChild(el);
  setTimeout(() => el.remove(), duracao);
}

export const toast = {
  sucesso: (msg) => show(msg, 'sucesso'),
  erro:    (msg) => show(msg, 'erro'),
  info:    (msg) => show(msg, 'info'),
};
