// Mock data — produtos típicos de mercadinho brasileiro, vendas, fornecedores
// Volumes realistas: ~R$50k/mês, ~30 SKUs no protótipo

const CATEGORIAS = ['Mercearia', 'Bebidas', 'Limpeza', 'Higiene', 'Hortifruti', 'Laticínios', 'Padaria'];

const PRODUTOS = [
  // status: ok / atencao / critico  -- diasAteRuptura
  { id: 'p01', nome: 'Arroz Tipo 1 5kg Tio João',     categoria: 'Mercearia',   estoque: 12,   unidade: 'fardo',  diasRuptura: 2,  classe: 'A', precoMedio: 28.90, demandaDiaria: 6.2, leadTime: 3, fornecedor: 'Distribuidora Central', faturamento: 12480 },
  { id: 'p02', nome: 'Feijão Carioca 1kg Camil',       categoria: 'Mercearia',   estoque: 23,  unidade: 'fardo',  diasRuptura: 4,  classe: 'A', precoMedio: 7.49,  demandaDiaria: 5.8, leadTime: 3, fornecedor: 'Distribuidora Central', faturamento: 9870 },
  { id: 'p03', nome: 'Óleo de Soja 900ml Soya',        categoria: 'Mercearia',   estoque: 37,   unidade: 'cx',     diasRuptura: 9,  classe: 'A', precoMedio: 6.99,  demandaDiaria: 4.1, leadTime: 4, fornecedor: 'Distribuidora Central', faturamento: 7820 },
  { id: 'p04', nome: 'Leite Integral 1L Italac',       categoria: 'Laticínios',  estoque: 8,   unidade: 'cx',     diasRuptura: 1,  classe: 'A', precoMedio: 5.49,  demandaDiaria: 8.4, leadTime: 2, fornecedor: 'Laticínios Vale Verde', faturamento: 11200 },
  { id: 'p05', nome: 'Açúcar Refinado 1kg União',      categoria: 'Mercearia',   estoque: 55,  unidade: 'cx',     diasRuptura: 12,  classe: 'A', precoMedio: 4.79,  demandaDiaria: 4.6, leadTime: 3, fornecedor: 'Distribuidora Central', faturamento: 6680 },
  { id: 'p06', nome: 'Refrigerante 2L Coca-Cola',      categoria: 'Bebidas',     estoque: 26,  unidade: 'cx',     diasRuptura: 5,  classe: 'A', precoMedio: 9.49,  demandaDiaria: 5.2, leadTime: 2, fornecedor: 'Distribuidora Bebidas Sul', faturamento: 8740 },
  { id: 'p07', nome: 'Cerveja Pilsen 350ml Brahma',    categoria: 'Bebidas',     estoque: 66,  unidade: 'cx',     diasRuptura: 11,  classe: 'A', precoMedio: 3.49,  demandaDiaria: 6.0, leadTime: 2, fornecedor: 'Distribuidora Bebidas Sul', faturamento: 9320 },
  { id: 'p08', nome: 'Pão Francês 1kg',                 categoria: 'Padaria',     estoque: 19,   unidade: 'kg',     diasRuptura: 2,  classe: 'A', precoMedio: 14.90, demandaDiaria: 9.5, leadTime: 1, fornecedor: 'Padaria Local',          faturamento: 14200 },
  { id: 'p09', nome: 'Sabão em Pó 1kg Omo',             categoria: 'Limpeza',     estoque: 25,  unidade: 'cx',     diasRuptura: 14,  classe: 'B', precoMedio: 13.90, demandaDiaria: 1.8, leadTime: 4, fornecedor: 'Atacado Higiene & Cia',   faturamento: 4280 },
  { id: 'p10', nome: 'Detergente 500ml Ypê',            categoria: 'Limpeza',     estoque: 49,  unidade: 'cx',     diasRuptura: 13,  classe: 'B', precoMedio: 2.79,  demandaDiaria: 3.8, leadTime: 3, fornecedor: 'Atacado Higiene & Cia',   faturamento: 3120 },
  { id: 'p11', nome: 'Papel Higiênico 12un Personal',  categoria: 'Higiene',     estoque: 27,   unidade: 'cx',     diasRuptura: 16,  classe: 'B', precoMedio: 18.90, demandaDiaria: 1.7, leadTime: 4, fornecedor: 'Atacado Higiene & Cia',   faturamento: 5340 },
  { id: 'p12', nome: 'Sabonete 90g Lux',                categoria: 'Higiene',     estoque: 55,  unidade: 'cx',     diasRuptura: 12,  classe: 'B', precoMedio: 2.19,  demandaDiaria: 4.6, leadTime: 4, fornecedor: 'Atacado Higiene & Cia',   faturamento: 2840 },
  { id: 'p13', nome: 'Margarina 500g Qualy',            categoria: 'Laticínios',  estoque: 36,  unidade: 'cx',     diasRuptura: 15,  classe: 'B', precoMedio: 8.49,  demandaDiaria: 2.4, leadTime: 3, fornecedor: 'Laticínios Vale Verde',  faturamento: 3680 },
  { id: 'p14', nome: 'Queijo Mussarela 1kg',            categoria: 'Laticínios',  estoque: 11,   unidade: 'kg',     diasRuptura: 6,  classe: 'B', precoMedio: 39.90, demandaDiaria: 1.9, leadTime: 3, fornecedor: 'Laticínios Vale Verde',  faturamento: 5840 },
  { id: 'p15', nome: 'Banana Prata kg',                 categoria: 'Hortifruti',  estoque: 46,  unidade: 'kg',     diasRuptura: 8,  classe: 'B', precoMedio: 6.49,  demandaDiaria: 5.8, leadTime: 1, fornecedor: 'Hortifruti CEAGESP',      faturamento: 4920 },
  { id: 'p16', nome: 'Tomate kg',                       categoria: 'Hortifruti',  estoque: 29,   unidade: 'kg',     diasRuptura: 7,  classe: 'B', precoMedio: 8.90,  demandaDiaria: 4.1, leadTime: 1, fornecedor: 'Hortifruti CEAGESP',      faturamento: 4720 },
  { id: 'p17', nome: 'Batata kg',                       categoria: 'Hortifruti',  estoque: 57,  unidade: 'kg',     diasRuptura: 13,  classe: 'B', precoMedio: 5.49,  demandaDiaria: 4.4, leadTime: 1, fornecedor: 'Hortifruti CEAGESP',      faturamento: 3960 },
  { id: 'p18', nome: 'Cebola kg',                       categoria: 'Hortifruti',  estoque: 47,  unidade: 'kg',     diasRuptura: 18,  classe: 'C', precoMedio: 4.99,  demandaDiaria: 2.6, leadTime: 1, fornecedor: 'Hortifruti CEAGESP',      faturamento: 2180 },
  { id: 'p19', nome: 'Macarrão Espaguete 500g Adria',  categoria: 'Mercearia',   estoque: 54,  unidade: 'cx',     diasRuptura: 17, classe: 'B', precoMedio: 4.29,  demandaDiaria: 3.2, leadTime: 4, fornecedor: 'Distribuidora Central',   faturamento: 3220 },
  { id: 'p20', nome: 'Molho de Tomate 340g Quero',      categoria: 'Mercearia',   estoque: 67,  unidade: 'cx',     diasRuptura: 19, classe: 'C', precoMedio: 3.49,  demandaDiaria: 3.5, leadTime: 4, fornecedor: 'Distribuidora Central',   faturamento: 2480 },
  { id: 'p21', nome: 'Café Torrado 500g Pilão',         categoria: 'Mercearia',   estoque: 22,  unidade: 'cx',     diasRuptura: 10,  classe: 'B', precoMedio: 22.90, demandaDiaria: 2.2, leadTime: 4, fornecedor: 'Distribuidora Central',   faturamento: 6240 },
  { id: 'p22', nome: 'Suco de Laranja 1L Del Valle',    categoria: 'Bebidas',     estoque: 38,  unidade: 'cx',     diasRuptura: 16, classe: 'C', precoMedio: 8.49,  demandaDiaria: 2.4, leadTime: 2, fornecedor: 'Distribuidora Bebidas Sul', faturamento: 2680 },
  { id: 'p23', nome: 'Água Mineral 1.5L Crystal',       categoria: 'Bebidas',     estoque: 52,  unidade: 'cx',     diasRuptura: 14, classe: 'C', precoMedio: 3.49,  demandaDiaria: 3.7, leadTime: 2, fornecedor: 'Distribuidora Bebidas Sul', faturamento: 1980 },
  { id: 'p24', nome: 'Iogurte 170g Vigor',              categoria: 'Laticínios',  estoque: 42,  unidade: 'cx',     diasRuptura: 11,  classe: 'C', precoMedio: 2.99,  demandaDiaria: 3.8, leadTime: 2, fornecedor: 'Laticínios Vale Verde',  faturamento: 2240 },
  { id: 'p25', nome: 'Manteiga 200g Aviação',           categoria: 'Laticínios',  estoque: 26,  unidade: 'cx',     diasRuptura: 20, classe: 'C', precoMedio: 12.90, demandaDiaria: 1.3, leadTime: 3, fornecedor: 'Laticínios Vale Verde',  faturamento: 1840 },
  { id: 'p26', nome: 'Maçã Gala kg',                    categoria: 'Hortifruti',  estoque: 26,  unidade: 'kg',     diasRuptura: 9,  classe: 'C', precoMedio: 9.49,  demandaDiaria: 2.9, leadTime: 1, fornecedor: 'Hortifruti CEAGESP',      faturamento: 2120 },
  { id: 'p27', nome: 'Alface unidade',                  categoria: 'Hortifruti',  estoque: 61,  unidade: 'un',     diasRuptura: 12,  classe: 'C', precoMedio: 3.99,  demandaDiaria: 5.1, leadTime: 1, fornecedor: 'Hortifruti CEAGESP',      faturamento: 1620 },
  { id: 'p28', nome: 'Desinfetante 2L Pinho Sol',       categoria: 'Limpeza',     estoque: 21,  unidade: 'cx',     diasRuptura: 15,  classe: 'C', precoMedio: 14.90, demandaDiaria: 1.4, leadTime: 4, fornecedor: 'Atacado Higiene & Cia',   faturamento: 1980 },
  { id: 'p29', nome: 'Esponja Multiuso 3un',            categoria: 'Limpeza',     estoque: 49,  unidade: 'cx',     diasRuptura: 18, classe: 'C', precoMedio: 3.49,  demandaDiaria: 2.7, leadTime: 4, fornecedor: 'Atacado Higiene & Cia',   faturamento: 1280 },
  { id: 'p30', nome: 'Creme Dental 90g Colgate',        categoria: 'Higiene',     estoque: 28,  unidade: 'cx',     diasRuptura: 14, classe: 'C', precoMedio: 5.49,  demandaDiaria: 2.0, leadTime: 4, fornecedor: 'Atacado Higiene & Cia',   faturamento: 1480 },
];

const FORNECEDORES = [
  { id: 'f01', nome: 'Distribuidora Central',     contato: 'pedidos@dcentral.com.br', leadTime: 3 },
  { id: 'f02', nome: 'Laticínios Vale Verde',     contato: '(11) 4567-2200',          leadTime: 2 },
  { id: 'f03', nome: 'Distribuidora Bebidas Sul', contato: 'comercial@bebsul.com.br', leadTime: 2 },
  { id: 'f04', nome: 'Atacado Higiene & Cia',     contato: '(11) 3344-5566',          leadTime: 4 },
  { id: 'f05', nome: 'Hortifruti CEAGESP',         contato: 'pedidos@hf.com.br',       leadTime: 1 },
  { id: 'f06', nome: 'Padaria Local',              contato: '(11) 9 9888-1234',        leadTime: 1 },
];

const STATUS = (dias) => dias < 3 ? 'critico' : dias <= 7 ? 'atencao' : 'ok';

// ---------- Estoque editável (ajuste manual, persistido em localStorage) ----------
const _estoqueOverrides = (() => {
  try { return JSON.parse(localStorage.getItem('estoqueOverrides') || '{}'); } catch (e) { return {}; }
})();
const _estoqueSubs = new Set();
function _persistEstoque() {
  try { localStorage.setItem('estoqueOverrides', JSON.stringify(_estoqueOverrides)); } catch (e) {}
  _estoqueSubs.forEach((fn) => fn());
}
function getEstoque(id) {
  if (Object.prototype.hasOwnProperty.call(_estoqueOverrides, id)) return _estoqueOverrides[id];
  const p = PRODUTOS.find((x) => x.id === id);
  return p ? p.estoque : 0;
}
function isEstoqueEditado(id) {
  return Object.prototype.hasOwnProperty.call(_estoqueOverrides, id);
}
function setEstoque(id, val) {
  _estoqueOverrides[id] = Math.max(0, Math.round(Number(val) || 0));
  _persistEstoque();
}
function resetEstoque(id) {
  delete _estoqueOverrides[id];
  _persistEstoque();
}
function subscribeEstoque(fn) { _estoqueSubs.add(fn); return () => _estoqueSubs.delete(fn); }
// dias até ruptura recalculado a partir do estoque atual e da demanda diária
function diasRupturaDe(p) {
  const est = getEstoque(p.id);
  if (!p.demandaDiaria || p.demandaDiaria <= 0) return p.diasRuptura;
  return Math.max(0, Math.round(est / p.demandaDiaria));
}
// produto com estoque + dias de ruptura recalculados (para listagens reativas)
function produtoView(p) {
  return { ...p, estoque: getEstoque(p.id), diasRuptura: diasRupturaDe(p), estoqueEditado: isEstoqueEditado(p.id) };
}
// hook React: re-renderiza o componente quando qualquer estoque muda
function useEstoqueStore() {
  const [, force] = React.useReducer((x) => x + 1, 0);
  React.useEffect(() => subscribeEstoque(force), []);
}

// Histórico agregado de faturamento — últimas 8 semanas + projeção 4 semanas
function semanasHistoricoProjecao() {
  // últimas 8 semanas, valores em R$, com leve crescimento + sazonalidade
  const base = 11000;
  const hist = [];
  for (let i = 7; i >= 0; i--) {
    const sazon = Math.sin(i * 0.7) * 800;
    const ruido = (Math.random() - 0.5) * 600;
    hist.push(Math.round(base + (7 - i) * 220 + sazon + ruido));
  }
  // projeção: continua tendência
  const last = hist[hist.length - 1];
  const proj = [];
  for (let i = 1; i <= 4; i++) {
    proj.push(Math.round(last + i * 240 + (Math.random() - 0.5) * 300));
  }
  return { hist, proj };
}

// Vendas históricas (90 dias) + projeção (30 dias) para um produto
function historicoProduto(demandaMedia, variabilidade = 0.25) {
  const dias = 90;
  const hist = [];
  for (let i = 0; i < dias; i++) {
    const sazon = Math.sin(i * 0.18) * demandaMedia * 0.15;
    const tend = i * 0.012 * demandaMedia;
    const ruido = (Math.random() - 0.5) * demandaMedia * variabilidade * 2;
    hist.push(Math.max(0, demandaMedia + sazon + tend + ruido));
  }
  const proj = [];
  const last = hist[hist.length - 1];
  for (let i = 1; i <= 30; i++) {
    const tend = i * 0.012 * demandaMedia;
    const sazon = Math.sin((dias + i) * 0.18) * demandaMedia * 0.15;
    proj.push(Math.max(0, last + tend + sazon));
  }
  return { hist, proj };
}

// Top 5 alertas para home
const TOP_ALERTAS = PRODUTOS
  .filter(p => p.diasRuptura <= 5)
  .sort((a,b) => a.diasRuptura - b.diasRuptura)
  .slice(0, 5);

// Perdas mock
const PERDAS_RECENTES = [
  { id: 'l01', data: '17/05', produto: 'Banana Prata',           quantidade: 3.5, unidade: 'kg', motivo: 'Vencimento', valor: 22.72 },
  { id: 'l02', data: '15/05', produto: 'Pão Francês',            quantidade: 2.0, unidade: 'kg', motivo: 'Sobra',      valor: 29.80 },
  { id: 'l03', data: '14/05', produto: 'Iogurte 170g Vigor',     quantidade: 12,  unidade: 'un', motivo: 'Vencimento', valor: 35.88 },
  { id: 'l04', data: '12/05', produto: 'Tomate',                 quantidade: 4.2, unidade: 'kg', motivo: 'Avaria',     valor: 37.38 },
  { id: 'l05', data: '10/05', produto: 'Leite Integral 1L',      quantidade: 6,   unidade: 'un', motivo: 'Vencimento', valor: 32.94 },
  { id: 'l06', data: '08/05', produto: 'Alface',                 quantidade: 8,   unidade: 'un', motivo: 'Avaria',     valor: 31.92 },
  { id: 'l07', data: '05/05', produto: 'Queijo Mussarela',       quantidade: 0.5, unidade: 'kg', motivo: 'Avaria',     valor: 19.95 },
];

// Comparativo H-W vs Prophet — métricas por produto
const COMPARATIVO_MODELOS = PRODUTOS.slice(0, 12).map(p => {
  const hwMape = 4 + Math.random() * 8;
  const proMape = 4 + Math.random() * 8;
  const hwRmse = 1.2 + Math.random() * 2;
  const proRmse = 1.2 + Math.random() * 2;
  const hwMae  = 0.9 + Math.random() * 1.6;
  const proMae = 0.9 + Math.random() * 1.6;
  return {
    id: p.id, nome: p.nome,
    hwMape: +hwMape.toFixed(2), proMape: +proMape.toFixed(2),
    hwRmse: +hwRmse.toFixed(2), proRmse: +proRmse.toFixed(2),
    hwMae:  +hwMae.toFixed(2),  proMae:  +proMae.toFixed(2),
    recomendado: hwMape < proMape ? 'Holt-Winters' : 'Prophet',
  };
});

const MAPE_GLOBAL = { hw: 7.3, prophet: 6.8 };
const RMSE_GLOBAL = { hw: 2.14, prophet: 1.98 };
const MAE_GLOBAL  = { hw: 1.42, prophet: 1.31 };

// Estabelecimento + usuário mock
const ESTABELECIMENTO = {
  nome: 'Mercado São João',
  cnpj: '12.345.678/0001-90',
  endereco: 'Rua das Acácias, 245 — São Paulo / SP',
};
const USUARIO = {
  nome: 'Juliana Costa',
  email: 'juliana@mercadosaojoao.com.br',
  iniciais: 'JC',
};

function fmtBRL(n) {
  return 'R$ ' + n.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function fmtBRLcompact(n) {
  return 'R$ ' + Math.round(n).toLocaleString('pt-BR');
}

Object.assign(window, {
  CATEGORIAS, PRODUTOS, FORNECEDORES, STATUS,
  getEstoque, setEstoque, resetEstoque, isEstoqueEditado, subscribeEstoque, diasRupturaDe, produtoView, useEstoqueStore,
  semanasHistoricoProjecao, historicoProduto,
  TOP_ALERTAS, PERDAS_RECENTES, COMPARATIVO_MODELOS,
  MAPE_GLOBAL, RMSE_GLOBAL, MAE_GLOBAL,
  ESTABELECIMENTO, USUARIO,
  fmtBRL, fmtBRLcompact,
});
