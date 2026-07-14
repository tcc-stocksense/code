/**
 * ============================================================
 *  MOCK DATA — REMOVER QUANDO O BACKEND ESTIVER PRONTO
 * ============================================================
 *
 *  Este arquivo simula todas as respostas da API para permitir
 *  testes visuais do frontend sem backend.
 *
 *  Para desativar: em apiClient.js, mude USAR_MOCK para false.
 * ============================================================
 */

// ---------- Produtos (base de tudo) ----------

const PRODUTOS = [
  { id: 1,  nome: 'Arroz Tipo 1 5kg',         categoria: 'Grãos',       estoque: 12,  unidade: 'pct', diasRuptura: 2,  classe: 'A', faturamento: 18400, demandaMedia: 5.2,  desvioPadrao: 1.3, cv: 0.25, tendencia: 'crescente',   tendenciaDelta: 0.08,  pontoReposicao: 25, estoqueSeguranca: 10, leadTime: 3, nivelServico: 95, fornecedor: 'Distribuidora Grãos do Sul', precoMedio: 22.90, qtdSugerida: 40 },
  { id: 2,  nome: 'Feijão Carioca 1kg',       categoria: 'Grãos',       estoque: 8,   unidade: 'pct', diasRuptura: 1,  classe: 'A', faturamento: 14200, demandaMedia: 6.8,  desvioPadrao: 2.1, cv: 0.31, tendencia: 'estável',     tendenciaDelta: 0.01,  pontoReposicao: 30, estoqueSeguranca: 12, leadTime: 3, nivelServico: 95, fornecedor: 'Distribuidora Grãos do Sul', precoMedio: 8.50,  qtdSugerida: 50 },
  { id: 3,  nome: 'Óleo de Soja 900ml',       categoria: 'Óleos',       estoque: 5,   unidade: 'un',  diasRuptura: 0,  classe: 'A', faturamento: 12800, demandaMedia: 4.1,  desvioPadrao: 0.9, cv: 0.22, tendencia: 'crescente',   tendenciaDelta: 0.12,  pontoReposicao: 20, estoqueSeguranca: 8,  leadTime: 2, nivelServico: 95, fornecedor: 'Cargill Alimentos',         precoMedio: 7.20,  qtdSugerida: 35 },
  { id: 4,  nome: 'Açúcar Cristal 5kg',       categoria: 'Mercearia',   estoque: 22,  unidade: 'pct', diasRuptura: 5,  classe: 'A', faturamento: 11500, demandaMedia: 3.8,  desvioPadrao: 1.0, cv: 0.26, tendencia: 'estável',     tendenciaDelta: -0.02, pontoReposicao: 18, estoqueSeguranca: 7,  leadTime: 3, nivelServico: 95, fornecedor: 'Usina Santa Helena',        precoMedio: 18.90, qtdSugerida: 20 },
  { id: 5,  nome: 'Leite Integral 1L',        categoria: 'Laticínios',  estoque: 30,  unidade: 'un',  diasRuptura: 4,  classe: 'A', faturamento: 10900, demandaMedia: 7.5,  desvioPadrao: 2.5, cv: 0.33, tendencia: 'crescente',   tendenciaDelta: 0.05,  pontoReposicao: 35, estoqueSeguranca: 15, leadTime: 1, nivelServico: 95, fornecedor: 'Laticínios Bela Vista',     precoMedio: 5.49,  qtdSugerida: 60 },
  { id: 6,  nome: 'Macarrão Espaguete 500g',  categoria: 'Massas',      estoque: 45,  unidade: 'pct', diasRuptura: 12, classe: 'B', faturamento: 7600,  demandaMedia: 3.2,  desvioPadrao: 0.8, cv: 0.25, tendencia: 'estável',     tendenciaDelta: 0.00,  pontoReposicao: 15, estoqueSeguranca: 6,  leadTime: 4, nivelServico: 90, fornecedor: 'Adria Alimentos',           precoMedio: 4.30,  qtdSugerida: 30 },
  { id: 7,  nome: 'Café Torrado 500g',        categoria: 'Bebidas',     estoque: 18,  unidade: 'pct', diasRuptura: 6,  classe: 'A', faturamento: 9800,  demandaMedia: 2.8,  desvioPadrao: 0.7, cv: 0.25, tendencia: 'decrescente', tendenciaDelta: -0.06, pontoReposicao: 14, estoqueSeguranca: 5,  leadTime: 5, nivelServico: 95, fornecedor: 'Torrefação Minas',          precoMedio: 16.90, qtdSugerida: 25 },
  { id: 8,  nome: 'Farinha de Trigo 1kg',     categoria: 'Grãos',       estoque: 35,  unidade: 'pct', diasRuptura: 10, classe: 'B', faturamento: 6200,  demandaMedia: 3.0,  desvioPadrao: 1.1, cv: 0.37, tendencia: 'estável',     tendenciaDelta: 0.01,  pontoReposicao: 12, estoqueSeguranca: 5,  leadTime: 3, nivelServico: 90, fornecedor: 'Moinho Paulista',           precoMedio: 5.80,  qtdSugerida: 20 },
  { id: 9,  nome: 'Molho de Tomate 340g',     categoria: 'Mercearia',   estoque: 60,  unidade: 'un',  diasRuptura: 18, classe: 'B', faturamento: 5400,  demandaMedia: 2.5,  desvioPadrao: 0.6, cv: 0.24, tendencia: 'estável',     tendenciaDelta: 0.03,  pontoReposicao: 10, estoqueSeguranca: 4,  leadTime: 4, nivelServico: 90, fornecedor: 'Cica Alimentos',            precoMedio: 3.90,  qtdSugerida: 0  },
  { id: 10, nome: 'Sal Refinado 1kg',         categoria: 'Mercearia',   estoque: 80,  unidade: 'pct', diasRuptura: 40, classe: 'C', faturamento: 2100,  demandaMedia: 1.2,  desvioPadrao: 0.4, cv: 0.33, tendencia: 'estável',     tendenciaDelta: 0.00,  pontoReposicao: 5,  estoqueSeguranca: 2,  leadTime: 5, nivelServico: 85, fornecedor: 'Cisne Alimentos',           precoMedio: 2.10,  qtdSugerida: 0  },
  { id: 11, nome: 'Sabão em Pó 1kg',          categoria: 'Limpeza',     estoque: 15,  unidade: 'un',  diasRuptura: 3,  classe: 'B', faturamento: 5100,  demandaMedia: 4.0,  desvioPadrao: 1.2, cv: 0.30, tendencia: 'crescente',   tendenciaDelta: 0.04,  pontoReposicao: 18, estoqueSeguranca: 7,  leadTime: 2, nivelServico: 90, fornecedor: 'P&G Brasil',                precoMedio: 12.50, qtdSugerida: 30 },
  { id: 12, nome: 'Detergente Líquido 500ml', categoria: 'Limpeza',     estoque: 25,  unidade: 'un',  diasRuptura: 8,  classe: 'C', faturamento: 3200,  demandaMedia: 2.8,  desvioPadrao: 0.5, cv: 0.18, tendencia: 'estável',     tendenciaDelta: -0.01, pontoReposicao: 10, estoqueSeguranca: 4,  leadTime: 2, nivelServico: 85, fornecedor: 'Ypê Indústria',             precoMedio: 2.90,  qtdSugerida: 0  },
  { id: 13, nome: 'Biscoito Cream Cracker',   categoria: 'Mercearia',   estoque: 40,  unidade: 'pct', diasRuptura: 14, classe: 'B', faturamento: 4800,  demandaMedia: 2.2,  desvioPadrao: 0.6, cv: 0.27, tendencia: 'estável',     tendenciaDelta: 0.02,  pontoReposicao: 8,  estoqueSeguranca: 3,  leadTime: 4, nivelServico: 90, fornecedor: 'Piraquê',                   precoMedio: 5.20,  qtdSugerida: 0  },
  { id: 14, nome: 'Margarina 500g',           categoria: 'Laticínios',  estoque: 10,  unidade: 'un',  diasRuptura: 2,  classe: 'B', faturamento: 4400,  demandaMedia: 3.5,  desvioPadrao: 0.9, cv: 0.26, tendencia: 'estável',     tendenciaDelta: 0.00,  pontoReposicao: 15, estoqueSeguranca: 6,  leadTime: 1, nivelServico: 90, fornecedor: 'Sadia',                     precoMedio: 6.80,  qtdSugerida: 25 },
  { id: 15, nome: 'Papel Higiênico 12 rolos', categoria: 'Higiene',     estoque: 20,  unidade: 'pct', diasRuptura: 7,  classe: 'B', faturamento: 5800,  demandaMedia: 2.0,  desvioPadrao: 0.5, cv: 0.25, tendencia: 'estável',     tendenciaDelta: 0.01,  pontoReposicao: 10, estoqueSeguranca: 4,  leadTime: 3, nivelServico: 90, fornecedor: 'Suzano Papel',              precoMedio: 18.90, qtdSugerida: 15 },
  { id: 16, nome: 'Cerveja Lata 350ml',       categoria: 'Bebidas',     estoque: 120, unidade: 'un',  diasRuptura: 9,  classe: 'A', faturamento: 13500, demandaMedia: 12.0, desvioPadrao: 4.0, cv: 0.33, tendencia: 'crescente',   tendenciaDelta: 0.10,  pontoReposicao: 50, estoqueSeguranca: 20, leadTime: 2, nivelServico: 95, fornecedor: 'Ambev',                     precoMedio: 3.50,  qtdSugerida: 80 },
  { id: 17, nome: 'Refrigerante 2L',          categoria: 'Bebidas',     estoque: 36,  unidade: 'un',  diasRuptura: 5,  classe: 'B', faturamento: 6800,  demandaMedia: 6.0,  desvioPadrao: 2.0, cv: 0.33, tendencia: 'estável',     tendenciaDelta: -0.03, pontoReposicao: 25, estoqueSeguranca: 10, leadTime: 2, nivelServico: 90, fornecedor: 'Coca-Cola FEMSA',           precoMedio: 8.50,  qtdSugerida: 30 },
  { id: 18, nome: 'Creme Dental 90g',         categoria: 'Higiene',     estoque: 50,  unidade: 'un',  diasRuptura: 20, classe: 'C', faturamento: 2800,  demandaMedia: 1.8,  desvioPadrao: 0.4, cv: 0.22, tendencia: 'estável',     tendenciaDelta: 0.00,  pontoReposicao: 7,  estoqueSeguranca: 3,  leadTime: 4, nivelServico: 85, fornecedor: 'Colgate-Palmolive',         precoMedio: 4.50,  qtdSugerida: 0  },
  { id: 19, nome: 'Sabonete 90g',             categoria: 'Higiene',     estoque: 70,  unidade: 'un',  diasRuptura: 30, classe: 'C', faturamento: 1900,  demandaMedia: 1.5,  desvioPadrao: 0.3, cv: 0.20, tendencia: 'estável',     tendenciaDelta: 0.00,  pontoReposicao: 5,  estoqueSeguranca: 2,  leadTime: 4, nivelServico: 85, fornecedor: 'Dove / Unilever',           precoMedio: 2.80,  qtdSugerida: 0  },
  { id: 20, nome: 'Manteiga 200g',            categoria: 'Laticínios',  estoque: 6,   unidade: 'un',  diasRuptura: 1,  classe: 'B', faturamento: 4100,  demandaMedia: 3.2,  desvioPadrao: 0.8, cv: 0.25, tendencia: 'crescente',   tendenciaDelta: 0.06,  pontoReposicao: 15, estoqueSeguranca: 6,  leadTime: 1, nivelServico: 90, fornecedor: 'Laticínios Bela Vista',     precoMedio: 12.90, qtdSugerida: 20 },
];

// ---------- Helpers ----------

function gerarGrafico(dias = 90) {
  const labels = [];
  const historico = [];
  const projecao = [];
  const hoje = new Date();
  for (let i = dias; i >= 0; i--) {
    const d = new Date(hoje);
    d.setDate(d.getDate() - i);
    labels.push(d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
    historico.push(Math.round(800 + Math.random() * 400 + (dias - i) * 2));
    projecao.push(null);
  }
  for (let i = 1; i <= 30; i++) {
    const d = new Date(hoje);
    d.setDate(d.getDate() + i);
    labels.push(d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
    historico.push(null);
    projecao.push(Math.round(1200 + Math.random() * 300 + i * 3));
  }
  return { labels, historico, projecao };
}

function gerarGraficoProduto(demandaMedia) {
  const labels = [];
  const historico = [];
  const projecao = [];
  const hoje = new Date();
  for (let i = 90; i >= 0; i--) {
    const d = new Date(hoje);
    d.setDate(d.getDate() - i);
    labels.push(d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
    historico.push(Math.max(0, Math.round(demandaMedia + (Math.random() - 0.5) * demandaMedia * 0.8)));
    projecao.push(null);
  }
  for (let i = 1; i <= 30; i++) {
    const d = new Date(hoje);
    d.setDate(d.getDate() + i);
    labels.push(d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
    historico.push(null);
    projecao.push(Math.max(0, Math.round(demandaMedia * 1.05 + (Math.random() - 0.5) * demandaMedia * 0.6)));
  }
  return { labels, historico, projecao };
}

function gerarVendasSemana(demandaMedia) {
  const semanas = [];
  const hoje = new Date();
  for (let i = 3; i >= 0; i--) {
    const inicio = new Date(hoje);
    inicio.setDate(inicio.getDate() - (i + 1) * 7);
    const fim = new Date(inicio);
    fim.setDate(fim.getDate() + 6);
    const total = Math.round(demandaMedia * 7 * (0.8 + Math.random() * 0.4));
    semanas.push({
      label: `${inicio.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })} – ${fim.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}`,
      total,
      media: +(total / 7).toFixed(1),
    });
  }
  return semanas;
}

function delay(ms = 300) {
  return new Promise(r => setTimeout(r, ms));
}

// ============================================================
//  MODELO DE ESTOQUE — a "inteligência" de reposição
//  Deriva os números a partir da estatística de demanda, do
//  lead time do fornecedor e do nível de serviço alvo, em vez
//  de valores fixos. Fórmulas clássicas de gestão de estoque:
//    estoque de segurança:  SS  = z · σ · √L
//    ponto de reposição:    ROP = μ · L + SS
//    dias até ruptura:      estoque / μ
//    precisa pedir?:        estoque ≤ ROP
//  onde μ = demanda média/dia, σ = desvio-padrão da demanda,
//  L = lead time (dias) e z = fator de segurança (normal) do
//  nível de serviço.
// ============================================================
const Z_POR_NIVEL = { 80: 0.84, 85: 1.04, 90: 1.28, 95: 1.645, 97: 1.88, 98: 2.05, 99: 2.33 };

function zDoNivel(nivel = 95) {
  const niveis = Object.keys(Z_POR_NIVEL).map(Number);
  const maisProximo = niveis.reduce((a, b) => Math.abs(b - nivel) < Math.abs(a - nivel) ? b : a);
  return Z_POR_NIVEL[maisProximo];
}

function estoqueSegurancaDe(p) {
  return Math.round(zDoNivel(p.nivelServico) * (p.desvioPadrao || 0) * Math.sqrt(Math.max(p.leadTime || 0, 0)));
}

function pontoReposicaoDe(p) {
  return Math.round((p.demandaMedia || 0) * (p.leadTime || 0) + estoqueSegurancaDe(p));
}

function diasRupturaDe(p) {
  if (!p.demandaMedia || p.demandaMedia <= 0) return 999;
  return Math.max(0, Math.round(p.estoque / p.demandaMedia));
}

function qtdSugeridaDe(p) {
  // repor até cobrir lead time + 7 dias de revisão + estoque de segurança
  const alvo = (p.demandaMedia || 0) * ((p.leadTime || 0) + 7) + estoqueSegurancaDe(p);
  return Math.max(0, Math.ceil(alvo - p.estoque));
}

// Enriquece um produto com todos os campos derivados pelo modelo.
function inteligenciaEstoque(p) {
  const estoqueSeguranca = estoqueSegurancaDe(p);
  const pontoReposicao = pontoReposicaoDe(p);
  const diasRuptura = diasRupturaDe(p);
  return {
    estoqueSeguranca,
    pontoReposicao,
    diasRuptura,
    precisaPedir: p.estoque <= pontoReposicao,
    qtdSugerida: qtdSugeridaDe(p),
    status: diasRuptura < 3 ? 'critico' : diasRuptura <= 7 ? 'atencao' : 'ok',
  };
}

// Lista de produtos já com os campos derivados (fonte única de verdade).
function produtosView() {
  return PRODUTOS.map(p => ({ ...p, ...inteligenciaEstoque(p) }));
}

// ---------- Handlers por rota ----------

const handlers = {
  // --- Dashboard ---
  'GET /dashboard': async () => {
    await delay(500);
    const view = produtosView();
    const criticos = view.filter(p => p.diasRuptura < 3);
    const emRisco = view.filter(p => p.diasRuptura <= 7);
    return {
      produtosEmRisco: emRisco.length,
      produtosCriticos: criticos.length,
      valorEmRisco: emRisco.reduce((s, p) => s + (p.faturamento * 0.07 / 4), 0),
      acuracia: 87.3,
      grafico: gerarGrafico(),
      proximosAlertas: view
        .filter(p => p.diasRuptura <= 5)
        .sort((a, b) => a.diasRuptura - b.diasRuptura)
        .slice(0, 5)
        .map(p => ({ id: p.id, nome: p.nome, diasRuptura: p.diasRuptura, qtdSugerida: p.qtdSugerida, unidade: p.unidade })),
    };
  },

  // --- Produtos (Estoque) ---
  'GET /produtos': async () => {
    await delay(400);
    return produtosView().map(p => ({
      id: p.id, nome: p.nome, categoria: p.categoria,
      estoque: p.estoque, unidade: p.unidade,
      diasRuptura: p.diasRuptura, classe: p.classe,
    }));
  },

  // --- Detalhe do produto ---
  'GET /produtos/*/detalhe': async (path) => {
    await delay(400);
    const id = parseInt(path.split('/')[2]);
    const p = PRODUTOS.find(x => x.id === id);
    if (!p) {
      const err = new Error('Produto não encontrado');
      err.status = 404;
      err.detail = 'Produto não encontrado';
      throw err;
    }
    return {
      ...p,
      ...inteligenciaEstoque(p), // sobrescreve valores estáticos pelos derivados
      grafico: gerarGraficoProduto(p.demandaMedia),
      vendasSemana: gerarVendasSemana(p.demandaMedia),
    };
  },

  // --- Atualizar estoque ---
  'PATCH /produtos/*/estoque': async (path, body) => {
    await delay(300);
    const id = parseInt(path.split('/')[2]);
    const p = PRODUTOS.find(x => x.id === id);
    if (!p) return { estoque: body.estoque, diasRuptura: 0 };
    p.estoque = Math.max(0, Math.round(Number(body.estoque) || 0));
    const intel = inteligenciaEstoque(p);
    p.diasRuptura = intel.diasRuptura; // mantém o base coerente entre telas
    return { estoque: p.estoque, ...intel };
  },

  // --- Atualizar parâmetros de reposição (lead time / nível de serviço) ---
  'PATCH /produtos/*/parametros': async (path, body) => {
    await delay(300);
    const id = parseInt(path.split('/')[2]);
    const p = PRODUTOS.find(x => x.id === id);
    if (!p) {
      const err = new Error('Produto não encontrado');
      err.status = 404;
      err.detail = 'Produto não encontrado';
      throw err;
    }
    if (body.leadTime != null) p.leadTime = Math.max(0, Math.round(Number(body.leadTime) || 0));
    if (body.nivelServico != null) p.nivelServico = Math.min(99, Math.max(50, Math.round(Number(body.nivelServico) || 95)));
    const intel = inteligenciaEstoque(p); // recomputa SS, ROP, precisaPedir, qtdSugerida
    p.diasRuptura = intel.diasRuptura;
    return { leadTime: p.leadTime, nivelServico: p.nivelServico, ...intel };
  },

  // --- Sugestão de compra ---
  'GET /sugestao-compra': async () => {
    await delay(500);
    const sugeridos = produtosView().filter(p => p.precisaPedir && p.qtdSugerida > 0);
    const grupos = {};
    sugeridos.forEach(p => {
      if (!grupos[p.fornecedor]) grupos[p.fornecedor] = [];
      grupos[p.fornecedor].push({
        id: p.id, nome: p.nome, unidade: p.unidade,
        precoMedio: p.precoMedio, leadTime: p.leadTime,
        qtdSugerida: p.qtdSugerida, subtotal: p.qtdSugerida * p.precoMedio,
      });
    });
    return { grupos };
  },

  // --- Alertas ---
  'GET /alertas': async () => {
    await delay(400);
    return produtosView()
      .filter(p => p.diasRuptura <= 7)
      .sort((a, b) => a.diasRuptura - b.diasRuptura)
      .map(p => ({
        id: p.id, nome: p.nome, categoria: p.categoria,
        estoque: p.estoque, unidade: p.unidade,
        diasRuptura: p.diasRuptura, leadTime: p.leadTime,
        qtdSugerida: p.qtdSugerida, fornecedor: p.fornecedor,
      }));
  },

  // --- Curva ABC ---
  'GET /curva-abc': async () => {
    await delay(500);
    return {
      produtos: PRODUTOS.map(p => ({
        nome: p.nome, faturamento: p.faturamento, classe: p.classe,
      })),
    };
  },

  // --- Métricas (Comparativo T10) — listagem geral por produto + agregado ---
  'GET /produtos/metricas': async () => {
    await delay(600);
    return {
      agregado: {
        mapeHW: 12.4, mapeProphet: 14.1,
        rmseHW: 8.7,  rmseProphet: 9.3,
        maeHW: 6.2,   maeProphet: 7.0,
      },
      porProduto: PRODUTOS.filter(p => p.classe === 'A' || p.classe === 'B').slice(0, 10).map(p => ({
        nome: p.nome,
        mapeHW:      +(8 + Math.random() * 12).toFixed(2),
        mapeProphet:  +(9 + Math.random() * 14).toFixed(2),
        rmseHW:      +(4 + Math.random() * 8).toFixed(2),
        rmseProphet:  +(5 + Math.random() * 9).toFixed(2),
        maeHW:       +(3 + Math.random() * 6).toFixed(2),
        maeProphet:   +(3.5 + Math.random() * 7).toFixed(2),
      })),
      execucoes: [
        { data: '2025-07-08 09:01', mensagem: 'Motor preditivo iniciado — 20 produtos carregados' },
        { data: '2025-07-08 09:01', mensagem: 'Holt-Winters: treinamento concluído (20/20 séries)' },
        { data: '2025-07-08 09:02', mensagem: 'Prophet: treinamento concluído (20/20 séries)' },
        { data: '2025-07-08 09:02', mensagem: 'Cross-validation: janela=30d, horizonte=7d' },
        { data: '2025-07-08 09:03', mensagem: 'Métricas calculadas — MAPE médio HW=12.4%, Prophet=14.1%' },
        { data: '2025-07-08 09:03', mensagem: 'Recomendação: Holt-Winters selecionado para 14 de 20 produtos' },
        { data: '2025-07-08 09:03', mensagem: 'Motor preditivo finalizado com sucesso' },
      ],
    };
  },

  // --- Importação ---
  'POST /importacao': async (_path, _body) => {
    await delay(1500);
    return { linhas: Math.floor(80 + Math.random() * 420) };
  },

  // --- Recalcular motor ---
  'POST /motor/recalcular': async () => {
    await delay(2000);
    return { status: 'ok' };
  },

  // --- Login ---
  'POST /auth/login': async () => {
    await delay(500);
    return { token: 'mock-token-stocksense-2025' };
  },
};

// ---------- Router ----------

function matchRoute(method, path) {
  const key = `${method} ${path}`;
  if (handlers[key]) return handlers[key];

  // Wildcard matching (e.g. GET /produtos/*/detalhe)
  for (const pattern of Object.keys(handlers)) {
    const [pMethod, ...pParts] = pattern.split(' ');
    const pPath = pParts.join(' ');
    if (pMethod !== method) continue;
    const regex = new RegExp('^' + pPath.replace(/\*/g, '[^/]+') + '$');
    if (regex.test(path)) return handlers[pattern];
  }
  return null;
}

// ---------- API pública ----------

export async function mockApiGet(path) {
  const cleanPath = path.split('?')[0];
  const handler = matchRoute('GET', cleanPath);
  if (!handler) {
    console.warn(`[MOCK] Rota não encontrada: GET ${path}`);
    return null;
  }
  return handler(cleanPath);
}

export async function mockApiPost(path, body) {
  const handler = matchRoute('POST', path);
  if (!handler) {
    console.warn(`[MOCK] Rota não encontrada: POST ${path}`);
    return null;
  }
  return handler(path, body);
}

export async function mockApiPatch(path, body) {
  const handler = matchRoute('PATCH', path);
  if (!handler) {
    console.warn(`[MOCK] Rota não encontrada: PATCH ${path}`);
    return null;
  }
  return handler(path, body);
}

export async function mockApiUpload(path, formData) {
  const handler = matchRoute('POST', path);
  if (!handler) {
    console.warn(`[MOCK] Rota não encontrada: POST (upload) ${path}`);
    return null;
  }
  return handler(path, formData);
}
