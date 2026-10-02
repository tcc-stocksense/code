/**
 * Base da API (D-09).
 *
 * Caminho RELATIVO por padrão: front e API são servidos na mesma origem nos
 * dois ambientes — em produção pelo Caddy (`handle /api/*` → backend:8080), em
 * desenvolvimento pelo nginx (frontend/nginx-dev.conf, que espelha essa rota).
 * Por isso não há URL absoluta aqui, nem detecção de ambiente: o '/api' resolve
 * para a origem de quem está servindo a página, qualquer que seja ela.
 *
 * Escape hatch: quem servir o front FORA do Docker (live server em :5500, ou
 * abrindo o .html direto) não tem o proxy e precisa apontar o host da API à mão.
 * No console do navegador, uma vez:
 *
 *     localStorage.setItem('stocksense_api_base', 'http://localhost:8080/api')
 *
 * e para voltar ao padrão:
 *
 *     localStorage.removeItem('stocksense_api_base')
 */
function baseDaApi() {
  try {
    const override = localStorage.getItem('stocksense_api_base');
    if (override) return override.replace(/\/+$/, '');
  } catch {
    // localStorage pode lançar (aba com cookies bloqueados). Cai no padrão.
  }
  return '/api';
}

export const API_BASE_URL = baseDaApi();

/**
 * Modo mock (dados fictícios, sem backend).
 *
 * Desligado por padrão: a partir da integração, ausência da chave significa
 * "falar com a API real". O botão flutuante grava explicitamente 'on'/'off'.
 */
export function mockAtivo() {
  try {
    return localStorage.getItem('stocksense_mock') === 'on';
  } catch {
    return false;
  }
}

export function setMock(ativo) {
  try {
    localStorage.setItem('stocksense_mock', ativo ? 'on' : 'off');
  } catch {
    /* sem persistência possível: o toggle vale só para esta sessão */
  }
}
