export const API_BASE_URL = 'http://localhost:8080/api';

/**
 * Modo mock (dados fictícios, sem backend).
 *
 * Desligado por padrão: a partir da integração, ausência da chave significa
 * "falar com a API real". O botão flutuante grava explicitamente 'on'/'off'.
 */
export function mockAtivo() {
  return localStorage.getItem('stocksense_mock') === 'on';
}

export function setMock(ativo) {
  localStorage.setItem('stocksense_mock', ativo ? 'on' : 'off');
}
