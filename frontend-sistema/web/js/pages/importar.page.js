import { requireAuth } from '../core/auth.js';
import { apiUpload, apiPost } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { uploadBlock } from '../components/uploadBlock.js';
import { toast } from '../components/toast.js';

requireAuth();
const page = renderLayout('importar');

const PLANILHAS = [
  { key: 'produtos',        nome: 'Produtos',             tipo: 'obrigatória', grupo: 'Obrigatórias', campos: 'sku, nome, categoria, preço, unidade' },
  { key: 'vendas',          nome: 'Vendas',               tipo: 'obrigatória', grupo: 'Obrigatórias', campos: 'data, sku, quantidade, valor_total' },
  { key: 'estabelecimento', nome: 'Estabelecimento',      tipo: 'desejável',   grupo: 'Desejáveis',   campos: 'nome, cnpj, endereço' },
  { key: 'fornecedores',    nome: 'Fornecedores',         tipo: 'desejável',   grupo: 'Desejáveis',   campos: 'id, nome, contato, lead_time_dias' },
  { key: 'prodForn',        nome: 'Produto × Fornecedor', tipo: 'desejável',   grupo: 'Desejáveis',   campos: 'sku, id_fornecedor, preco_compra' },
];

// Estado dos uploads
const estados = {};
const blocos = {};

page.style.maxWidth = '760px';
page.innerHTML = `
  <div class="page-header">
    <div>
      <h1 class="page-title">Importar dados de vendas</h1>
      <p class="page-subtitle">Envie cada planilha no seu próprio bloco. Formatos aceitos: .xlsx, .xls e .csv.</p>
    </div>
  </div>
  <details class="import-help" style="margin-bottom:18px">
    <summary style="cursor:pointer; font-weight:500; font-size:14px; color:var(--cor-primaria); user-select:none">Como preparar suas planilhas</summary>
    <ul style="margin:10px 0 0; padding-left:20px; font-size:13px; color:var(--cor-texto-sec); line-height:1.8; list-style:disc">
      <li>Use a primeira linha como cabeçalho</li>
      <li>Exporte como .xlsx, .xls ou .csv (UTF-8)</li>
      <li>A planilha de Vendas deve conter ao menos 30 dias de histórico para previsões confiáveis</li>
      <li>SKUs devem coincidir entre Produtos e Vendas</li>
    </ul>
    <a href="#" onclick="event.preventDefault()" style="font-size:13px; color:var(--cor-primaria); margin-top:8px; display:inline-block">Baixar modelos de planilha</a>
  </details>
  <div id="blocos-obrigatorias"></div>
  <div id="blocos-desejaveis"></div>
  <div class="row-between" style="margin-top:24px">
    <span class="text-meta" id="status-resumo"></span>
    <button class="btn btn-primary" id="btn-processar" disabled>Processar dados</button>
  </div>
`;

const containerObrig = document.getElementById('blocos-obrigatorias');
const containerDesej = document.getElementById('blocos-desejaveis');

// Label de seção
function addSectionLabel(container, text) {
  const label = document.createElement('div');
  label.style.cssText = 'font-size:11px; color:var(--cor-texto-terc); text-transform:uppercase; letter-spacing:0.06em; font-weight:500; margin:18px 0 10px;';
  label.textContent = text;
  container.appendChild(label);
}

addSectionLabel(containerObrig, 'Obrigatórias');
addSectionLabel(containerDesej, 'Desejáveis');

PLANILHAS.forEach(pl => {
  estados[pl.key] = 'vazio';

  const bloco = uploadBlock({
    titulo: pl.nome,
    obrigatorio: pl.tipo === 'obrigatória',
    campos: pl.campos,
    onFile: (file) => enviarArquivo(pl, file, bloco),
  });

  blocos[pl.key] = bloco;
  const container = pl.grupo === 'Obrigatórias' ? containerObrig : containerDesej;
  const wrapper = document.createElement('div');
  wrapper.style.marginBottom = '8px';
  wrapper.appendChild(bloco.el);
  container.appendChild(wrapper);
});

async function enviarArquivo(pl, file, bloco) {
  estados[pl.key] = 'processando';
  bloco.setEstado('processando', { nome: file.name });
  atualizarResumo();

  try {
    const formData = new FormData();
    formData.append('arquivo', file);
    formData.append('tipo', pl.key);

    const resultado = await apiUpload('/importacao', formData);

    estados[pl.key] = 'sucesso';
    bloco.setEstado('sucesso', { nome: file.name, linhas: resultado.linhas || 0 });
    toast.sucesso(`${pl.nome}: ${resultado.linhas || 0} linhas importadas`);
  } catch (err) {
    estados[pl.key] = 'erro';
    bloco.setEstado('erro', {
      nome: file.name,
      mensagem: err.detail || 'Falha no processamento',
      erros: err.erros || [],
    });
    toast.erro(`${pl.nome}: ${err.detail || 'Erro ao importar'}`);
  }

  atualizarResumo();
}

function atualizarResumo() {
  const enviadas = Object.values(estados).filter(s => s === 'sucesso').length;
  const obrigOk = estados.produtos === 'sucesso' && estados.vendas === 'sucesso';

  document.getElementById('status-resumo').textContent =
    `${enviadas} planilha${enviadas !== 1 ? 's' : ''} enviada${enviadas !== 1 ? 's' : ''} · ` +
    (obrigOk ? 'obrigatórias OK, pronto para processar.' : 'envie Produtos e Vendas para gerar previsões.');

  document.getElementById('btn-processar').disabled = !obrigOk;
}

atualizarResumo();

// Processar dados
document.getElementById('btn-processar').addEventListener('click', async () => {
  const btn = document.getElementById('btn-processar');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Processando...';

  try {
    await apiPost('/motor/recalcular', {});
    toast.sucesso('Dados processados com sucesso! Previsões atualizadas.');
    btn.textContent = 'Processado';
  } catch (err) {
    toast.erro(err.detail || 'Erro ao processar dados');
    btn.disabled = false;
    btn.textContent = 'Processar dados';
  }
});
