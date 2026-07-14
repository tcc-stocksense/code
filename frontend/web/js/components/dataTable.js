/**
 * Tabela genérica com busca, ordenação, filtros e renderizador de célula por coluna.
 *
 * @param {HTMLElement} container - onde injetar a tabela
 * @param {Object} opts
 * @param {Array<{chave: string, titulo: string, render?: (linha) => Node|string, ordenavel?: boolean}>} opts.colunas
 * @param {Array<Object>} opts.linhas
 * @param {boolean} [opts.busca=false] - exibir campo de busca
 * @param {string} [opts.buscaPlaceholder='Buscar...']
 * @param {Array<{chave: string, titulo: string, opcoes: Array<{valor: string, label: string}>}>} [opts.filtros]
 * @param {function} [opts.onClickLinha] - callback ao clicar numa linha (recebe a linha)
 * @returns {{ atualizar(linhas: Array): void }}
 */
export function dataTable(container, opts) {
  const { colunas, busca = false, buscaPlaceholder = 'Buscar...', filtros = [], onClickLinha } = opts;
  let linhas = [...opts.linhas];
  let termoBusca = '';
  let ordenacao = { chave: null, dir: 'asc' };
  const filtrosSelecionados = {};

  // Wrapper
  const wrapper = document.createElement('div');

  // Barra de filtros
  const barraFiltros = document.createElement('div');
  barraFiltros.className = 'filters-row';

  if (busca) {
    const inputBusca = document.createElement('input');
    inputBusca.type = 'text';
    inputBusca.className = 'input search';
    inputBusca.placeholder = buscaPlaceholder;
    inputBusca.addEventListener('input', (e) => {
      termoBusca = e.target.value.toLowerCase();
      renderTabela();
    });
    barraFiltros.appendChild(inputBusca);
  }

  filtros.forEach(f => {
    const select = document.createElement('select');
    select.className = 'select';
    select.innerHTML = `<option value="">${f.titulo}</option>` +
      f.opcoes.map(o => `<option value="${o.valor}">${o.label}</option>`).join('');
    select.addEventListener('change', (e) => {
      filtrosSelecionados[f.chave] = e.target.value;
      renderTabela();
    });
    barraFiltros.appendChild(select);
  });

  if (busca || filtros.length) wrapper.appendChild(barraFiltros);

  // Tabela
  const tableCard = document.createElement('div');
  tableCard.className = 'card';
  tableCard.style.padding = '0';
  tableCard.style.overflow = 'auto';

  const table = document.createElement('table');
  table.className = 'table';
  tableCard.appendChild(table);
  wrapper.appendChild(tableCard);
  container.appendChild(wrapper);

  function getLinhasFiltradas() {
    let resultado = linhas;

    // Busca textual
    if (termoBusca) {
      resultado = resultado.filter(l =>
        colunas.some(c => {
          const val = l[c.chave];
          return val != null && String(val).toLowerCase().includes(termoBusca);
        })
      );
    }

    // Filtros por select
    for (const [chave, valor] of Object.entries(filtrosSelecionados)) {
      if (valor) {
        resultado = resultado.filter(l => String(l[chave]) === valor);
      }
    }

    // Ordenação
    if (ordenacao.chave) {
      resultado = [...resultado].sort((a, b) => {
        const va = a[ordenacao.chave];
        const vb = b[ordenacao.chave];
        if (va == null) return 1;
        if (vb == null) return -1;
        const cmp = typeof va === 'number' ? va - vb : String(va).localeCompare(String(vb), 'pt-BR');
        return ordenacao.dir === 'asc' ? cmp : -cmp;
      });
    }

    return resultado;
  }

  function renderTabela() {
    const dados = getLinhasFiltradas();

    // Header
    const thead = document.createElement('thead');
    const trHead = document.createElement('tr');
    colunas.forEach(col => {
      const th = document.createElement('th');
      th.textContent = col.titulo;
      if (col.ordenavel !== false) {
        th.style.cursor = 'pointer';
        if (ordenacao.chave === col.chave) {
          th.textContent += ordenacao.dir === 'asc' ? ' \u25B2' : ' \u25BC';
        }
        th.addEventListener('click', () => {
          if (ordenacao.chave === col.chave) {
            ordenacao.dir = ordenacao.dir === 'asc' ? 'desc' : 'asc';
          } else {
            ordenacao = { chave: col.chave, dir: 'asc' };
          }
          renderTabela();
        });
      }
      trHead.appendChild(th);
    });
    thead.appendChild(trHead);

    // Body
    const tbody = document.createElement('tbody');
    dados.forEach(linha => {
      const tr = document.createElement('tr');
      if (onClickLinha) {
        tr.style.cursor = 'pointer';
        tr.addEventListener('click', () => onClickLinha(linha));
      }
      colunas.forEach(col => {
        const td = document.createElement('td');
        if (col.render) {
          const conteudo = col.render(linha);
          if (typeof conteudo === 'string') {
            td.innerHTML = conteudo;
          } else if (conteudo instanceof Node) {
            td.appendChild(conteudo);
          }
        } else {
          td.textContent = linha[col.chave] != null ? linha[col.chave] : '';
        }
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });

    table.innerHTML = '';
    table.appendChild(thead);
    table.appendChild(tbody);
  }

  renderTabela();

  return {
    atualizar(novasLinhas) {
      linhas = [...novasLinhas];
      renderTabela();
    }
  };
}
