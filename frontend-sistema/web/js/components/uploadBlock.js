import { iconUpload, iconCheck, iconAlert, iconFile } from './icons.js';

/**
 * Bloco de upload de planilha com 4 estados: vazio, processando, sucesso, erro.
 *
 * @param {Object} opts
 * @param {string} opts.titulo - Nome da planilha (ex: "Produtos")
 * @param {boolean} [opts.obrigatorio=false]
 * @param {string} [opts.accept='.xlsx,.xls,.csv']
 * @param {function} opts.onFile - callback(file) quando um arquivo é selecionado
 * @returns {{ el: HTMLElement, setEstado(estado, info): void }}
 */
export function uploadBlock({ titulo, obrigatorio = false, accept = '.xlsx,.xls,.csv', campos, onFile }) {
  const block = document.createElement('div');
  block.className = 'import-block';

  const head = document.createElement('div');
  head.className = 'import-block-head';
  head.innerHTML = `
    <div class="import-block-title">
      ${iconFile()}
      <span class="name">${titulo}</span>
      ${obrigatorio ? '<span class="badge badge-info">obrigat\u00f3rio</span>' : ''}
    </div>
    <span class="status-label text-meta"></span>
  `;

  const body = document.createElement('div');
  body.className = 'import-block-body';

  const input = document.createElement('input');
  input.type = 'file';
  input.accept = accept;
  input.style.display = 'none';

  const dropZone = document.createElement('div');
  dropZone.className = 'drop-mini';
  dropZone.innerHTML = `${iconUpload()} Arraste ou clique para selecionar`;
  dropZone.addEventListener('click', () => input.click());
  dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--cor-primaria-clara)'; });
  dropZone.addEventListener('dragleave', () => { dropZone.style.borderColor = ''; });
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '';
    if (e.dataTransfer.files.length) onFile(e.dataTransfer.files[0]);
  });

  input.addEventListener('change', () => {
    if (input.files.length) onFile(input.files[0]);
  });

  body.appendChild(input);
  body.appendChild(dropZone);

  if (campos) {
    const note = document.createElement('div');
    note.className = 'text-meta';
    note.style.cssText = 'font-size:12px; margin-top:6px; padding:0 4px;';
    note.textContent = `Campos esperados: ${campos}`;
    body.appendChild(note);
  }

  block.appendChild(head);
  block.appendChild(body);

  const statusLabel = head.querySelector('.status-label');

  function setEstado(estado, info = {}) {
    block.classList.remove('success', 'error', 'processing');

    if (estado === 'vazio') {
      statusLabel.textContent = '';
      body.innerHTML = '';
      body.appendChild(input);
      body.appendChild(dropZone);
    } else if (estado === 'processando') {
      block.classList.add('processing');
      statusLabel.innerHTML = '<span class="spinner"></span> Processando...';
      body.innerHTML = `<div class="file-line processing">${iconFile()} <div class="file-meta"><span class="fn">${info.nome || ''}</span></div></div>`;
    } else if (estado === 'sucesso') {
      block.classList.add('success');
      statusLabel.innerHTML = `${iconCheck(14)} ${info.linhas || 0} linhas importadas`;
      statusLabel.style.color = 'var(--status-ok)';
      body.innerHTML = `
        <div class="file-line success">${iconCheck()} <div class="file-meta"><span class="fn">${info.nome || ''}</span><span class="sub">${info.linhas || 0} registros</span></div></div>
        <div style="display:flex; gap:8px; margin-top:8px">
          <button type="button" class="btn btn-tertiary btn-sm btn-substituir">Substituir</button>
          <button type="button" class="btn btn-tertiary btn-sm btn-remover" style="color:var(--status-critico)">Remover</button>
        </div>
      `;
      body.querySelector('.btn-substituir').addEventListener('click', () => input.click());
      body.querySelector('.btn-remover').addEventListener('click', () => setEstado('vazio'));
    } else if (estado === 'erro') {
      block.classList.add('error');
      statusLabel.innerHTML = `${iconAlert(14)} Erro`;
      statusLabel.style.color = 'var(--status-critico)';
      const errosHtml = (info.erros || []).map(e => `<li>${e}</li>`).join('');
      body.innerHTML = `<div class="file-line error">${iconAlert()} <div class="file-meta"><span class="fn">${info.nome || ''}</span><span class="sub">${info.mensagem || 'Falha no processamento'}</span></div></div>
        ${errosHtml ? `<ul style="margin-top:8px;padding-left:20px;font-size:13px;color:var(--status-critico);list-style:disc">${errosHtml}</ul>` : ''}`;
    }
  }

  return { el: block, setEstado };
}
