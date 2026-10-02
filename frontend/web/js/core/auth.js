import { apiPost } from './apiClient.js';

const TOKEN_KEY = 'stocksense_token';
const ESTAB_KEY = 'stocksense_estabelecimento_id';
const NOME_KEY = 'stocksense_nome_fantasia';

/**
 * POST /api/auth/login → { token, estabelecimentoId, nomeFantasia }.
 * Credencial inválida volta como erro da API (o backend não distingue
 * email de senha) — a tela mostra apenas "credenciais inválidas".
 */
export async function login(email, senha) {
  const data = await apiPost('/auth/login', { email, senha });
  if (data && data.token) {
    sessionStorage.setItem(TOKEN_KEY, data.token);
    if (data.estabelecimentoId != null) {
      sessionStorage.setItem(ESTAB_KEY, String(data.estabelecimentoId));
    }
    if (data.nomeFantasia) {
      sessionStorage.setItem(NOME_KEY, data.nomeFantasia);
    }
  }
  return data;
}

export function requireAuth() {
  if (!sessionStorage.getItem(TOKEN_KEY)) {
    window.location.replace('login.html');
  }
}

export function logout() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(ESTAB_KEY);
  sessionStorage.removeItem(NOME_KEY);
  window.location.replace('login.html');
}

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function getEstabelecimentoId() {
  const valor = sessionStorage.getItem(ESTAB_KEY);
  return valor == null ? null : Number(valor);
}

export function getNomeFantasia() {
  return sessionStorage.getItem(NOME_KEY) || 'StockSense';
}
