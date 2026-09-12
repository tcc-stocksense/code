import { requireAuth } from '../core/auth.js';
import { apiUpload, apiPost } from '../core/apiClient.js';
import { renderLayout } from '../components/layout.js';
import { uploadBlock } from '../components/uploadBlock.js';
import { toast } from '../components/toast.js';

requireAuth();
const page = renderLayout('importar');

/**
 * O backend expõe dois endpoints de importação, ambos multipart com o campo
 * `arquivo` e apenas `.xlsx`. A ordem importa: as vendas são casadas com os
 * produtos por SKU, então Produtos precisa entrar primeiro.
 *
 * As planilhas "desejáveis" do protótipo (estabelecimento, fornecedores,
 * produto × fornecedor) não têm endpoint e por isso não são oferecidas.
 */
const PLANILHAS = [
  {
    key: 'produtos',
    nome: 'Produtos',
    rota: '/importacao/produtos',
    campos: 'sku, nome, categoria, unidade de medida',
  },
  {
    key: 'vendas',
    nome: 'Vendas',
    rota: '/importacao/vendas',
    campos: 'data, sku, quantidade',
    dependeDe: 'produtos',
  },
];

const estados = {};
const blocos = {};
const wrappers = {};

page.style.maxWidth = '760px';
page.innerHTML = `
  <div class="page-header">
    <div>
      <h1 class="page-title">Importar dados de vendas</h1>
      <p class="page-subtitle">Envie primeiro os produtos, depois as vendas. Formato aceito: .xlsx.</p>
    </div>
  </div>
  <details class="import-help" style="margin-bottom:18px">
    <summary style="cursor:pointer; font-weight:500; font-size:14px; color:var(--cor-primaria); user-select:none">Como preparar suas planilhas</summary>
    <ul style="margin:10px 0 0; padding-left:20px; font-size:13px; color:var(--cor-texto-sec); line-height:1.8; list-style:disc">
      <li>Use a primeira linha como cabeçalho</li>
      <li>Exporte como .xlsx — .csv e .xls não são aceitos pela API</li>
      <li>Os SKUs das Vendas precisam existir na planilha de Produtos</li>
      <li>Histórico curto (menos de 90 dias) não impede a importação, mas gera aviso e piora a previsão</li>
    </ul>
  </details>
  <div id="blocos-obrigatorias"></div>
  <div id="aviso-desejaveis"></div>
  <div class="row-between" style="margin-top:24px">
    <span class="text-meta" id="status-resumo"></span>
    <button class="btn btn-primary" id="btn-processar" disabled>Processar dados</button>
  </div>
  <div id="resultado-motor" style="margin-top:16px"></div>
`;

const containerObrig = document.getElementById('blocos-obrigatorias');

const label = document.createElement('div');
label.style.cssText = 'font-size:11px; color:var(--cor-texto-terc); text-transform:uppercase; letter-spacing:0.06em; font-weight:500; margin:18px 0 10px;';
label.textContent = 'Obrigatórias';
containerObrig.appendChild(label);

PLANILHAS.forEach(pl => {
  estados[pl.key] = 'vazio';

  const bloco = uploadBlock({
    titulo: pl.nome,
    obrigatorio: true,
    accept: '.xlsx',
    campos: pl.campos,
    onFile: (file) => enviarArquivo(pl, file, bloco),
  });

  blocos[pl.key] = bloco;
  const wrapper = document.createElement('div');
  wrapper.style.marginBottom = '8px';
  wrapper.appendChild(bloco.el);
  wrappers[pl.key] = wrapper;
  containerObrig.appendChild(wrapper);
});

// Planilhas sem endpoint — explicitadas em vez de silenciosamente ignoradas
document.getElementById('aviso-desejaveis').innerHTML = `
  <div class="card" style="margin-top:18px; padding:14px">
    <div class="label" style="margin-bottom:6px">Estabelecimento, fornecedores e produto × fornecedor</div>
    <p class="text-meta" style="margin:0">
      Ainda não há endpoint de importação para essas planilhas. Lead time e dados de
      fornecedor usam os valores padrão do sistema até que a API os exponha.
    </p>
  </div>
`;

function bloquearDependentes() {
  PLANILHAS.forEach(pl => {
    if (!pl.dependeDe) return;
    const liberado = estados[pl.dependeDe] === 'sucesso';
    const wrapper = wrappers[pl.key];
    wrapper.style.opacity = liberado ? '1' : '0.5';
    wrapper.style.pointerEvents = liberado ? 'auto' : 'none';
    wrapper.title = liberado ? '' : 'Envie a planilha de Produtos primeiro.';
  });
}

function formatarErros(erros) {
  return (erros || []).slice(0, 20).map(e =>
    typeof e === 'string' ? e : `Linha ${e.linha}: ${e.mensagem}`
  );
}

async function enviarArquivo(pl, file, bloco) {
  estados[pl.key] = 'processando';
  bloco.setEstado('processando', { nome: file.name });
  atualizarResumo();

  try {
    const formData = new FormData();
    formData.append('arquivo', file);

    const r = await apiUpload(pl.rota, formData);

    estados[pl.key] = 'sucesso';
    bloco.setEstado('sucesso', { nome: file.name, linhas: r.importados });

    const partes = [`${r.importados} de ${r.totalLinhas} linhas importadas`];
    if (r.diasDeHistorico != null) partes.push(`${r.diasDeHistorico} dias de histórico`);
    toast.sucesso(`${pl.nome}: ${partes.join(' · ')}`);

    // Erros e avisos por linha não derrubam a importação — são exibidos abaixo do bloco.
    const observacoes = [...formatarErros(r.erros), ...(r.avisos || [])];
    if (observacoes.length > 0) {
      const nota = document.createElement('ul');
      nota.style.cssText = 'margin:8px 0 0; padding-left:20px; font-size:13px; color:var(--cor-texto-sec); list-style:disc';
      nota.innerHTML = observacoes.map(o => `<li>${o}</li>`).join('');
      bloco.el.appendChild(nota);
    }
  } catch (err) {
    estados[pl.key] = 'erro';
    bloco.setEstado('erro', {
      nome: file.name,
      mensagem: err.detail || 'Falha no processamento',
      erros: formatarErros(err.erros),
    });
    toast.erro(`${pl.nome}: ${err.detail || 'Erro ao importar'}`);
  }

  atualizarResumo();
}

function atualizarResumo() {
  const obrigOk = estados.produtos === 'sucesso' && estados.vendas === 'sucesso';

  document.getElementById('status-resumo').textContent = obrigOk
    ? 'Produtos e vendas importados — pronto para processar.'
    : estados.produtos === 'sucesso'
      ? 'Produtos importados. Envie a planilha de Vendas.'
      : 'Envie a planilha de Produtos para começar.';

  document.getElementById('btn-processar').disabled = !obrigOk;
  bloquearDependentes();
}

atualizarResumo();

// Processar dados — POST /api/motor/recalcular é SÍNCRONO: a resposta só volta
// quando todos os produtos foram processados. Sem retry automático.
document.getElementById('btn-processar').addEventListener('click', async () => {
  const btn = document.getElementById('btn-processar');
  const resultado = document.getElementById('resultado-motor');

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Processando...';
  resultado.innerHTML = `<p class="text-meta">O motor roda produto a produto e pode levar alguns minutos. Não feche a página.</p>`;

  try {
    const r = await apiPost('/motor/recalcular', {});

    resultado.innerHTML = `
      <div class="card" style="padding:14px">
        <div class="label" style="margin-bottom:8px">Recálculo concluído</div>
        <ul style="margin:0; padding-left:20px; font-size:13px; color:var(--cor-texto-sec); line-height:1.8; list-style:disc">
          <li>${r.processados} produtos processados${r.falhas > 0 ? ` · <strong style="color:var(--status-critico)">${r.falhas} com falha</strong>` : ''}</li>
          <li>${r.classificadosAbc} produtos classificados na curva ABC${r.abcProxy ? ' (ranking por quantidade)' : ''}</li>
        </ul>
        <div style="display:flex; gap:8px; margin-top:12px">
          <a href="dashboard.html" class="btn btn-primary btn-sm">Ver dashboard</a>
          <a href="estoque.html" class="btn btn-secondary btn-sm">Ver estoque</a>
        </div>
      </div>
    `;
    toast.sucesso('Previsões atualizadas.');
    btn.textContent = 'Processado';
  } catch (err) {
    resultado.innerHTML = '';
    toast.erro(err.detail || 'Erro ao processar dados');
    btn.disabled = false;
    btn.textContent = 'Processar dados';
  }
});
