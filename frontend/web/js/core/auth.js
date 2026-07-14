import { apiPost } from './apiClient.js';

const TOKEN_KEY = 'stocksense_token';

export async function login(email, senha) {
  const data = await apiPost('/auth/login', { email, senha });
  if (data && data.token) {
    sessionStorage.setItem(TOKEN_KEY, data.token);
  }
  return data;
}

export function requireAuth() {
  // TODO: reativar quando o backend estiver pronto
  // if (!sessionStorage.getItem(TOKEN_KEY)) {
  //   window.location.replace('../pages/login.html');
  // }
}

export function logout() {
  sessionStorage.removeItem(TOKEN_KEY);
  window.location.replace('../pages/login.html');
}

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}
