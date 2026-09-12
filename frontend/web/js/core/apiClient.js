import { API_BASE_URL, mockAtivo } from './config.js';
import { mockApiGet, mockApiPost, mockApiPatch, mockApiUpload } from './mock.js';

/**
 * Camada única de acesso à API. Nenhum `fetch` deve existir fora deste arquivo.
 *
 * Duas responsabilidades:
 *  1. transporte (URL base, JWT, tratamento de erro RFC 7807);
 *  2. adaptação de forma — traduz o vocabulário do backend
 *     (`produtoId`, `estoqueAtual`, `classeAbc`, `diasAteRuptura`…) para o
 *     vocabulário usado pelas telas (`id`, `estoque`, `classe`, `diasRuptura`…).
 *
 * O modo mock é uma escolha explícita do desenvolvedor (botão flutuante), nunca
 * um fallback automático: se a API responder erro, o erro sobe para a tela.
 */

// ---------------------------------------------------------------- utilidades

function num(valor) {
  if (valor == null || valor === '') return null;
  const n = Number(valor);
  return Number.isFinite(n) ? n : null;
}

/**
 * Semáforo relativo ao ponto de reposição (contrato §Alertas):
 * vermelho = estoque ≤ PR · amarelo = PR < estoque ≤ PR × 1.5 · verde = acima.
 * Retorna null quando o motor nunca rodou (PR indefinido).
 */
export function semaforoPorPR(estoque, pontoReposicao) {
  const pr = num(pontoReposicao);
  const est = num(estoque);
  if (pr == null || est == null || pr <= 0) return null;
  if (est <= pr) return 'critico';
  if (est <= pr * 1.5) return 'atencao';
  return 'ok';
}

const SEMAFORO_BACKEND = {
  VERMELHO: 'critico',
  AMARELO: 'atencao',
  VERDE: 'ok',
};

function traduzSemaforo(valor) {
  if (!valor) return null;
  return SEMAFORO_BACKEND[String(valor).toUpperCase()] ?? null;
}

// ------------------------------------------------------------- adaptação

/** GET /produtos → item da lista de estoque. */
function adaptarProduto(p) {
  const estoque = p.estoqueAtual ?? p.estoque ?? 0;
  const pontoReposicao = num(p.pontoReposicao);
  const estoqueSeguranca = num(p.estoqueSeguranca);
  return {
    id: p.produtoId ?? p.id,
    nome: p.nome,
    categoria: p.categoria ?? '',
    unidade: p.unidadeMedida ?? p.unidade ?? 'un',
    estoque,
    classe: p.classeAbc ?? p.classe ?? null,
    pontoReposicao,
    estoqueSeguranca,
    dataUltimoCalculo: p.dataUltimoCalculo ?? null,
    semaforo: semaforoPorPR(estoque, pontoReposicao),
    semCalculo: pontoReposicao == null,
  };
}

/** GET /produtos/{id}/detalhe → tela de detalhe. */
function adaptarDetalhe(p) {
  const estoque = p.estoqueAtual ?? p.estoque ?? 0;
  const pontoReposicao = num(p.pontoReposicao);
  const estoqueSeguranca = num(p.estoqueSeguranca);
  const previsoes = (p.previsoes ?? []).map(pt => ({
    data: pt.data,
    quantidade: num(pt.quantidadePrevista ?? pt.quantidade),
  }));

  const tendenciaPercentual = num(p.tendenciaPercentual);
  let tendencia = null;
  if (tendenciaPercentual != null) {
    if (tendenciaPercentual > 2) tendencia = 'crescente';
    else if (tendenciaPercentual < -2) tendencia = 'decrescente';
    else tendencia = 'estável';
  }

  // Sugestão de reposição: subir o estoque até o PR e repor o colchão de segurança.
  let qtdSugerida = null;
  if (pontoReposicao != null) {
    const alvo = pontoReposicao + (estoqueSeguranca ?? 0);
    qtdSugerida = Math.max(0, Math.ceil(alvo - estoque));
  }

  return {
    id: p.produtoId ?? p.id,
    nome: p.nome,
    categoria: p.categoria ?? '',
    unidade: p.unidadeMedida ?? p.unidade ?? 'un',
    estoque,
    classe: p.classeAbc ?? p.classe ?? null,
    demandaMedia: num(p.demandaMediaDiaria ?? p.demandaMedia),
    desvioPadrao: num(p.desvioPadraoDemanda ?? p.desvioPadrao),
    cv: num(p.coeficienteVariacao ?? p.cv),
    tendenciaPercentual,
    tendencia,
    pontoReposicao,
    estoqueSeguranca,
    diasRuptura: num(p.diasAteRuptura ?? p.diasRuptura),
    dataUltimoCalculo: p.dataUltimoCalculo ?? null,
    previsoes,
    qtdSugerida,
    semaforo: semaforoPorPR(estoque, pontoReposicao),
    semCalculo: pontoReposicao == null,
    semPrevisao: previsoes.length === 0,
  };
}

/** GET /alertas → linha da tela de alertas. */
function adaptarAlerta(a) {
  const estoque = a.estoqueAtual ?? a.estoque ?? 0;
  const pontoReposicao = num(a.pontoReposicao);
  return {
    id: a.produtoId ?? a.id,
    nome: a.nome,
    estoque,
    pontoReposicao,
    diasRuptura: num(a.diasAteRuptura ?? a.diasRuptura),
    leadTime: num(a.leadTimeMedio ?? a.leadTime),
    semaforo: traduzSemaforo(a.semaforo) ?? semaforoPorPR(estoque, pontoReposicao),
  };
}

/** GET /dashboard → KPIs da home. */
function adaptarDashboard(d) {
  const mape = num(d.mapeMedioModeloSelecionado);
  return {
    risco7Dias: num(d.riscoDeFaltar7Dias) ?? 0,
    criticoAgora: num(d.criticoAgora) ?? 0,
    acuracia: mape != null ? 100 - mape : null,
    seriesFaturamento: (d.seriesFaturamento ?? []).map(s => ({
      semana: s.semana,
      total: num(s.total) ?? 0,
    })),
  };
}

/** GET /curva-abc → ranking Pareto. */
function adaptarCurvaAbc(d) {
  const bruto = d.itens ?? d.produtos ?? [];
  return {
    abcProxy: d.abcProxy === true,
    itens: bruto.map(i => ({
      id: i.produtoId ?? i.id,
      nome: i.nome,
      classe: i.classeAbc ?? i.classe ?? 'C',
      faturamento: num(i.faturamento),
      percentualDoTotal: num(i.percentualDoTotal) ?? 0,
      percentualAcumulado: num(i.percentualAcumulado) ?? 0,
    })),
  };
}

/** GET /produtos/{id}/metricas → 2 linhas (Holt-Winters e Prophet). */
function adaptarMetricas(lista) {
  return (lista ?? []).map(m => ({
    modelo: m.modelo,
    mape: num(m.mape),
    rmse: num(m.rmse),
    mae: num(m.mae),
    selecionado: m.selecionado === true,
    executadoEm: m.executadoEm ?? null,
  }));
}

/** POST /importacao/{produtos|vendas} → resultado do upload. */
function adaptarImportacao(r) {
  return {
    totalLinhas: num(r.totalLinhas) ?? 0,
    importados: num(r.importados) ?? num(r.linhas) ?? 0,
    diasDeHistorico: num(r.diasDeHistorico),
    erros: r.erros ?? [],
    avisos: r.avisos ?? [],
  };
}

/** POST /motor/recalcular → resumo da execução síncrona. */
function adaptarMotor(r) {
  return {
    processados: num(r.produtosProcessados) ?? 0,
    falhas: num(r.produtosComFalha) ?? 0,
    classificadosAbc: num(r.produtosClassificadosAbc) ?? 0,
    abcProxy: r.abcProxy === true,
    executadoEm: r.executadoEm ?? null,
  };
}

function normalizarResposta(path, method, data) {
  if (data == null) return data;
  const rota = path.split('?')[0];

  if (method === 'GET') {
    if (rota === '/produtos' && Array.isArray(data)) return data.map(adaptarProduto);
    if (/^\/produtos\/[^/]+\/detalhe$/.test(rota)) return adaptarDetalhe(data);
    if (/^\/produtos\/[^/]+\/metricas$/.test(rota)) return adaptarMetricas(data);
    if (rota === '/alertas' && Array.isArray(data)) return data.map(adaptarAlerta);
    if (rota === '/dashboard') return adaptarDashboard(data);
    if (rota === '/curva-abc') return adaptarCurvaAbc(data);
  }

  if (method === 'PATCH' && /^\/produtos\/[^/]+\/estoque$/.test(rota)) {
    return adaptarProduto(data);
  }

  if (method === 'POST') {
    if (rota === '/importacao/produtos' || rota === '/importacao/vendas') return adaptarImportacao(data);
    if (rota === '/motor/recalcular') return adaptarMotor(data);
  }

  return data;
}

/** Corpo das requisições: traduz o vocabulário da tela para o do backend. */
function normalizarRequisicao(path, method, body) {
  if (body == null) return body;
  const rota = path.split('?')[0];

  if (method === 'PATCH' && /^\/produtos\/[^/]+\/estoque$/.test(rota)) {
    // O backend só aceita `estoqueAtual` (ProdutoEstoqueRequest).
    return { estoqueAtual: body.estoqueAtual ?? body.estoque };
  }

  return body;
}

// -------------------------------------------------------------- transporte

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
  let erros = [];
  try {
    const body = await res.json();
    // RFC 7807 ProblemDetail
    if (body.detail) detail = body.detail;
    else if (body.message) detail = body.message;
    if (Array.isArray(body.erros)) erros = body.erros;
  } catch { /* corpo não é JSON */ }

  const err = new Error(detail);
  err.status = res.status;
  err.detail = detail;
  err.erros = erros;

  // Sessão expirada ou token inválido: volta para o login em vez de
  // deixar a tela em um estado de erro que o usuário não consegue resolver.
  if (res.status === 401 || res.status === 403) {
    sessionStorage.removeItem('stocksense_token');
    if (!window.location.pathname.endsWith('login.html')) {
      window.location.replace('login.html');
    }
  }

  throw err;
}

async function requestJson(method, path, body) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: { ...getHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(normalizarRequisicao(path, method, body)),
  });
  const data = await handleResponse(res);
  return normalizarResposta(path, method, data);
}

async function requestGet(path) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: 'GET',
    headers: getHeaders(),
  });
  const data = await handleResponse(res);
  return normalizarResposta(path, 'GET', data);
}

async function requestUpload(path, formData) {
  const headers = {};
  const token = sessionStorage.getItem('stocksense_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers,
    body: formData,
  });
  const data = await handleResponse(res);
  return normalizarResposta(path, 'POST', data);
}

// ------------------------------------------------------------------ API

/**
 * O mock foi escrito antes do contrato real e ainda usa as rotas antigas.
 * Este alias mantém o modo offline utilizável sem reescrever `mock.js`.
 */
function rotaMock(path) {
  const rota = path.split('?')[0];
  if (rota === '/importacao/produtos' || rota === '/importacao/vendas') return '/importacao';
  if (/^\/produtos\/[^/]+\/metricas$/.test(rota)) return '/produtos/metricas';
  return path;
}

export async function apiGet(path) {
  if (mockAtivo()) return normalizarResposta(path, 'GET', await mockApiGet(rotaMock(path)));
  return requestGet(path);
}

export async function apiPost(path, body) {
  if (mockAtivo()) return normalizarResposta(path, 'POST', await mockApiPost(rotaMock(path), body));
  return requestJson('POST', path, body);
}

export async function apiPatch(path, body) {
  if (mockAtivo()) return normalizarResposta(path, 'PATCH', await mockApiPatch(rotaMock(path), body));
  return requestJson('PATCH', path, body);
}

export async function apiUpload(path, formData) {
  if (mockAtivo()) return normalizarResposta(path, 'POST', await mockApiUpload(rotaMock(path), formData));
  return requestUpload(path, formData);
}
