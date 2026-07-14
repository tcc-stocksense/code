import { API_BASE_URL } from './config.js';
import { mockApiGet, mockApiPost, mockApiPatch, mockApiUpload } from './mock.js';

// ============================================================
//  MOCK: controlado pelo botão flutuante (localStorage)
//  Para desativar definitivamente, mude para false.
// ============================================================
const USAR_MOCK = localStorage.getItem('stocksense_mock') !== 'off';

function getHeaders() {
  const headers = { 'Accept': 'application/json' };
  const token = sessionStorage.getItem('stocksense_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse(res) {
  if (res.ok) {
    const text = await res.text();
    return text ? JSON.parse(text) : null;
  }

  let detail = `Erro ${res.status}`;
  try {
    const body = await res.json();
    // RFC 7807 ProblemDetail
    if (body.detail) detail = body.detail;
    else if (body.message) detail = body.message;
  } catch { /* corpo não é JSON */ }

  const err = new Error(detail);
  err.status = res.status;
  err.detail = detail;
  throw err;
}

export async function apiGet(path) {
  if (USAR_MOCK) return mockApiGet(path);
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: 'GET',
    headers: getHeaders(),
  });
  return handleResponse(res);
}

export async function apiPost(path, body) {
  if (USAR_MOCK) return mockApiPost(path, body);
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { ...getHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

export async function apiPatch(path, body) {
  if (USAR_MOCK) return mockApiPatch(path, body);
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: 'PATCH',
    headers: { ...getHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

export async function apiUpload(path, formData) {
  if (USAR_MOCK) return mockApiUpload(path, formData);
  const headers = {};
  const token = sessionStorage.getItem('stocksense_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  // Não define Content-Type — o browser seta o boundary do multipart
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers,
    body: formData,
  });
  return handleResponse(res);
}
