const fmtMoeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
const fmtMoedaCompacta = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 0, maximumFractionDigits: 0 });
const fmtData = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });

export function moedaBR(valor) {
  return fmtMoeda.format(valor);
}

export function moedaBRcompacta(valor) {
  return fmtMoedaCompacta.format(valor);
}

export function dataBR(iso) {
  if (!iso) return '';
  const [ano, mes, dia] = iso.split('-');
  return `${dia}/${mes}/${ano}`;
}

/**
 * Escapa texto que vai para `innerHTML`. Usar sempre que o conteúdo vier de
 * dado importado (nome de produto, categoria, mensagem de erro da planilha):
 * o .xlsx é entrada não confiável, mesmo vindo do próprio lojista.
 */
export function esc(valor) {
  if (valor == null) return '';
  return String(valor)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function numero(valor, casas = 0) {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  }).format(valor);
}

/** Arredondamento apenas visual: fração abaixo de 0,8 desce; a partir de 0,8 sobe.
 * Os valores originais continuam sendo usados nos cálculos e alertas.
 */
export function inteiroEstoque(valor) {
  const base = Math.floor(valor);
  return valor >= base + 0.8 ? base + 1 : base;
}

export function numeroEstoque(valor) {
  return valor == null ? '—' : numero(inteiroEstoque(valor));
}

export function diasEstoque(valor) {
  if (valor == null) return '—';
  const dias = inteiroEstoque(valor);
  return `${numero(dias)} ${dias === 1 ? 'dia' : 'dias'}`;
}
