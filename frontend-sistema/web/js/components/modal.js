import { iconX } from './icons.js';

/**
 * Abre um modal.
 * @param {Object} opts
 * @param {string} opts.titulo
 * @param {Node|string} opts.conteudo - conteúdo do body do modal
 * @param {function} [opts.onConfirm] - callback do botão confirmar
 * @param {string} [opts.labelConfirm='Salvar']
 * @param {string} [opts.labelCancelar='Cancelar']
 * @returns {{ fechar(): void, body: HTMLElement }}
 */
export function openModal({ titulo, conteudo, onConfirm, labelConfirm = 'Salvar', labelCancelar = 'Cancelar' }) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';

  const modal = document.createElement('div');
  modal.className = 'modal';

  // Header
  const header = document.createElement('div');
  header.className = 'modal-header';
  header.innerHTML = `<h3>${titulo}</h3>`;
  const btnClose = document.createElement('button');
  btnClose.className = 'icon-btn';
  btnClose.innerHTML = iconX();
  btnClose.addEventListener('click', fechar);
  header.appendChild(btnClose);

  // Body
  const body = document.createElement('div');
  body.className = 'modal-body';
  if (typeof conteudo === 'string') {
    body.innerHTML = conteudo;
  } else if (conteudo instanceof Node) {
    body.appendChild(conteudo);
  }

  // Footer
  const footer = document.createElement('div');
  footer.className = 'row';
  footer.style.justifyContent = 'flex-end';
  footer.style.marginTop = '20px';
  footer.style.gap = '8px';

  const btnCancel = document.createElement('button');
  btnCancel.className = 'btn btn-secondary';
  btnCancel.textContent = labelCancelar;
  btnCancel.addEventListener('click', fechar);
  footer.appendChild(btnCancel);

  if (onConfirm) {
    const btnOk = document.createElement('button');
    btnOk.className = 'btn btn-primary';
    btnOk.textContent = labelConfirm;
    btnOk.addEventListener('click', () => onConfirm(fechar));
    footer.appendChild(btnOk);
  }

  modal.appendChild(header);
  modal.appendChild(body);
  modal.appendChild(footer);
  overlay.appendChild(modal);

  // Fechar ao clicar no overlay (fora do modal)
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) fechar();
  });

  document.body.appendChild(overlay);

  function fechar() {
    overlay.remove();
  }

  return { fechar, body };
}
