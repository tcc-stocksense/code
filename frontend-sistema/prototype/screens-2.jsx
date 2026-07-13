// Screens 5-8: Alertas, Detalhe, Curva ABC, Sugestão de compra

// ---------- Tela 5: Alertas de reposição ----------
function AlertasScreen({ go }) {
  const alertas = PRODUTOS.filter((p) => p.diasRuptura <= 7).sort((a, b) => a.diasRuptura - b.diasRuptura);
  const [pedidos, setPedidos] = React.useState({});

  if (alertas.length === 0) {
    return (
      <div className="page">
        <div className="page-header"><h1 className="page-title">Produtos para pedir agora</h1></div>
        <div className="card" style={{ textAlign: 'center', padding: '48px 20px' }}>
          <p>Nenhum produto precisa ser pedido hoje. Seu estoque está em dia.</p>
        </div>
      </div>);

  }

  const proximos3 = alertas.filter((p) => p.diasRuptura <= 3).length;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Produtos para pedir agora</h1>
          <p className="page-subtitle">{proximos3} produtos precisam ser pedidos nos próximos 3 dias · {alertas.length} no total</p>
        </div>
        <button className="btn btn-primary" onClick={() => go('sugestao')}>Gerar relatório de compra</button>
      </div>

      <div className="stack-tight">
        {alertas.map((p) => {
          const sugQtd = Math.ceil(p.demandaDiaria * (p.leadTime + 7));
          const status = STATUS(p.diasRuptura);
          const isPedido = pedidos[p.id];
          return (
            <div key={p.id} className={`alert-row ${status === 'critico' ? 'critical' : 'warning'}`}>
              <div>
                <div style={{ fontWeight: 500, marginBottom: 2 }}>{p.nome}</div>
                <div className="text-meta">{p.categoria} · estoque atual {p.estoque} {p.unidade}</div>
              </div>
              <div>
                <div className="alert-strong" style={{ color: status === 'critico' ? 'var(--danger-700)' : 'var(--warning-700)' }}>
                  {p.diasRuptura === 0 ? 'Já zerou' : `Vai faltar em ${p.diasRuptura} ${p.diasRuptura === 1 ? 'dia' : 'dias'}`}
                </div>
                <div className="text-meta">lead time fornecedor: {p.leadTime} dias</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="alert-suggest">Pedir {sugQtd} {p.unidade}</div>
                <div className="text-meta">{p.fornecedor}</div>
              </div>
              <button className="btn btn-secondary btn-sm" onClick={() => go('detalhe', p.id)}>Detalhe</button>
              <button className={`btn ${isPedido ? 'btn-tertiary' : 'btn-primary'} btn-sm`} onClick={() => setPedidos({ ...pedidos, [p.id]: !isPedido })}>
                {isPedido ? <><IconCheck size={14} /> Pedido</> : 'Marcar como pedido'}
              </button>
            </div>);

        })}
      </div>
    </div>);

}

// ---------- Tela 6: Detalhe do produto ----------
function DetalheScreen({ produtoId, go }) {
  useEstoqueStore();
  const produto = PRODUTOS.find((p) => p.id === produtoId) || PRODUTOS[0];
  const { hist, proj } = React.useMemo(() => historicoProduto(produto.demandaDiaria), [produto.id]);
  const [modalOpen, setModalOpen] = React.useState(false);
  const diasRuptura = diasRupturaDe(produto);

  // KPIs
  const media = hist.reduce((a, b) => a + b, 0) / hist.length;
  const desvio = Math.sqrt(hist.reduce((a, b) => a + Math.pow(b - media, 2), 0) / hist.length);
  const cv = desvio / media;
  const inicio = hist.slice(0, 14).reduce((a, b) => a + b, 0) / 14;
  const fim = hist.slice(-14).reduce((a, b) => a + b, 0) / 14;
  const tendDelta = (fim - inicio) / inicio;
  const tend = tendDelta > 0.05 ? 'subindo' : tendDelta < -0.05 ? 'descendo' : 'estável';
  const tendIcon = tend === 'subindo' ? <IconTrend size={16} /> : tend === 'descendo' ? <IconTrendDown size={16} /> : <IconMinus size={16} />;
  const tendColor = tend === 'subindo' ? 'var(--success-600)' : tend === 'descendo' ? 'var(--danger-700)' : 'var(--text-secondary)';

  // Pontos
  const pontoReposicao = Math.ceil(media * produto.leadTime + 1.65 * desvio * Math.sqrt(produto.leadTime));
  const estoqueSeguranca = Math.ceil(1.65 * desvio * Math.sqrt(produto.leadTime));

  // Semanas
  const semanas = [];
  for (let i = 3; i >= 0; i--) {
    const slice = hist.slice(hist.length - (i + 1) * 7, hist.length - i * 7);
    semanas.push({
      label: `Semana ${4 - i}`,
      total: Math.round(slice.reduce((a, b) => a + b, 0)),
      media: (slice.reduce((a, b) => a + b, 0) / 7).toFixed(1)
    });
  }

  return (
    <div className="page">
      <button className="btn btn-tertiary btn-sm" onClick={() => go('estoque')} style={{ marginBottom: 14 }}>
        <IconArrowLeft size={14} /> Voltar para estoque
      </button>

      <div className="row-between" style={{ marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 className="page-title">{produto.nome}</h1>
          <p className="page-subtitle">{produto.categoria} · classe {produto.classe}</p>
        </div>
        <StatusPill dias={diasRuptura} />
      </div>

      <div className="detail-grid">
        <div className="stack">
          <div className="card">
            <div className="row-between" style={{ marginBottom: 6 }}>
              <h3>Demanda diária</h3>
              <span className="text-meta">últimos 90 dias + projeção 30 dias</span>
            </div>
            <LineChart hist={hist} proj={proj} height={260} formatY={(v) => v.toFixed(1)} />
          </div>

          <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: 0 }}>
            <div className="card kpi-card">
              <div className="label">Demanda média/dia</div>
              <span className="kpi-number">{media.toFixed(1)}</span>
              <div className="kpi-context">{produto.unidade}/dia</div>
            </div>
            <div className="card kpi-card">
              <div className="label">Variabilidade</div>
              <span className="kpi-number">±{desvio.toFixed(1)}</span>
              <div className="kpi-context">desvio-padrão · CV {(cv * 100).toFixed(0)}%</div>
            </div>
            <div className="card kpi-card">
              <div className="label">Tendência</div>
              <span className="kpi-number" style={{ color: tendColor, display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: 24 }}>{tendIcon} {tend}</span>
              <div className="kpi-context">{tendDelta > 0 ? '+' : ''}{(tendDelta * 100).toFixed(1)}% nas últimas 2 semanas</div>
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: 14 }}>Vendas por semana</h3>
            <table className="table">
              <thead>
                <tr><th>Semana</th><th>Total vendido</th><th>Média/dia</th></tr>
              </thead>
              <tbody>
                {semanas.map((s, i) =>
                <tr key={i}>
                    <td>{s.label}</td>
                    <td className="tabular">{s.total} {produto.unidade}</td>
                    <td className="tabular text-secondary">{s.media} {produto.unidade}/dia</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="side-panel">
          <div className="card">
            <div style={{ marginBottom: 16 }}>
              <EstoqueField produto={produto} variant="panel" />
            </div>

            <div className="side-stat">
              <span className="label">Você precisa pedir?</span>
              <span className="value" style={{ color: diasRuptura <= 7 ? 'var(--danger-700)' : 'var(--success-600)' }}>
                {diasRuptura <= 7 ? 'Sim' : 'Não'}
              </span>
            </div>
            <div className="side-stat">
              <span className="label">Ponto de reposição</span>
              <span className="value tabular">{pontoReposicao} {produto.unidade}</span>
            </div>
            <div className="side-stat">
              <span className="label">Estoque de segurança</span>
              <span className="value tabular">{estoqueSeguranca} {produto.unidade}</span>
            </div>
            <div className="side-stat">
              <span className="label">Dias até ruptura</span>
              <span className="value tabular">{diasRuptura}</span>
            </div>
            <div className="side-stat">
              <span className="label">Lead time fornecedor</span>
              <span className="value tabular">{produto.leadTime} dias</span>
            </div>
            <div className="side-stat" title="Probabilidade alvo de não faltar dentro do lead time">
              <span className="label">Nível de serviço alvo</span>
              <span className="value tabular">95%</span>
            </div>

            <div className="stack-tight" style={{ marginTop: 16 }}>
              <button className="btn btn-primary btn-block">Marcar para pedido</button>
              <button className="btn btn-secondary btn-block" onClick={() => setModalOpen(true)}>Editar parâmetros</button>
            </div>
          </div>

          <div className="card" style={{ marginTop: 16, padding: 14 }}>
            <div className="label" style={{ marginBottom: 8 }}>Fornecedor</div>
            <div style={{ fontWeight: 500 }}>{produto.fornecedor}</div>
            <div className="text-meta">Preço médio: {fmtBRL(produto.precoMedio)}/{produto.unidade}</div>
          </div>
        </div>
      </div>

      {modalOpen && <ParametrosModal produto={produto} onClose={() => setModalOpen(false)} />}
    </div>);

}

function ParametrosModal({ produto, onClose }) {
  const [ns, setNs] = React.useState(95);
  const [lt, setLt] = React.useState(produto.leadTime);
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Editar parâmetros — {produto.nome}</h3>
          <button className="icon-btn" onClick={onClose}><IconX size={16} /></button>
        </div>
        <div className="stack" style={{ gap: 14 }}>
          <div className="field">
            <label className="field-label">Lead time do fornecedor (dias)</label>
            <input type="number" className="input" value={lt} onChange={(e) => setLt(+e.target.value)} />
          </div>
          <div className="field">
            <label className="field-label">Nível de serviço alvo (%)</label>
            <input type="number" className="input" value={ns} onChange={(e) => setNs(+e.target.value)} min="50" max="99" />
            <span className="text-meta">Probabilidade de não faltar o produto dentro do lead time.</span>
          </div>
          <div className="row" style={{ justifyContent: 'flex-end', gap: 8, marginTop: 8 }}>
            <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
            <button className="btn btn-primary" onClick={onClose}>Salvar parâmetros</button>
          </div>
        </div>
      </div>
    </div>);

}

// ---------- Tela 7: Curva ABC ----------
function ABCScreen() {
  const [periodo, setPeriodo] = React.useState('30');
  const ordenados = [...PRODUTOS].sort((a, b) => b.faturamento - a.faturamento);
  const total = ordenados.reduce((a, p) => a + p.faturamento, 0);

  const top30 = ordenados.slice(0, 30);

  const grupoA = ordenados.filter((p) => p.classe === 'A');
  const grupoB = ordenados.filter((p) => p.classe === 'B');
  const grupoC = ordenados.filter((p) => p.classe === 'C');
  const pctA = grupoA.reduce((a, p) => a + p.faturamento, 0) / total * 100;
  const pctB = grupoB.reduce((a, p) => a + p.faturamento, 0) / total * 100;
  const pctC = grupoC.reduce((a, p) => a + p.faturamento, 0) / total * 100;

  let acc = 0;
  const tabelaCompleta = ordenados.map((p) => {
    acc += p.faturamento;
    return { ...p, pct: p.faturamento / total * 100, acumulada: acc / total * 100 };
  });

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Classificação ABC dos produtos</h1>
          <p className="page-subtitle">Quais produtos respondem pela maior parte do seu faturamento</p>
        </div>
        <select className="select" value={periodo} onChange={(e) => setPeriodo(e.target.value)} style={{ width: 200 }}>
          <option value="30">Últimos 30 dias</option>
          <option value="60">Últimos 60 dias</option>
          <option value="90">Últimos 90 dias</option>
          <option value="custom">Personalizado</option>
        </select>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="row-between" style={{ marginBottom: 10 }}>
          <h3>Pareto de faturamento</h3>
          <span className="text-meta">top 30 produtos · linha vermelha = 80% acumulados</span>
        </div>
        <ParetoChart data={top30} height={300} />
      </div>

      <div className="abc-cards" style={{ marginBottom: 20 }}>
        <div className="abc-card a">
          <div className="label" style={{ marginBottom: 8 }}>Classe A</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
            <span className="kpi-number">{grupoA.length}</span>
            <span className="text-secondary">produtos</span>
          </div>
          <div className="text-small" style={{ marginTop: 6 }}>{pctA.toFixed(0)}% do faturamento · prioridade máxima</div>
        </div>
        <div className="abc-card b">
          <div className="label" style={{ marginBottom: 8 }}>Classe B</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
            <span className="kpi-number">{grupoB.length}</span>
            <span className="text-secondary">produtos</span>
          </div>
          <div className="text-small" style={{ marginTop: 6 }}>{pctB.toFixed(0)}% do faturamento · monitorar</div>
        </div>
        <div className="abc-card c">
          <div className="label" style={{ marginBottom: 8 }}>Classe C</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
            <span className="kpi-number">{grupoC.length}</span>
            <span className="text-secondary">produtos</span>
          </div>
          <div className="text-small" style={{ marginTop: 6 }}>{pctC.toFixed(0)}% do faturamento · gestão por exceção</div>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ width: 80 }}>Classe</th>
              <th>Produto</th>
              <th>Faturamento</th>
              <th>% do total</th>
              <th>% acumulada</th>
            </tr>
          </thead>
          <tbody>
            {tabelaCompleta.map((p) =>
            <tr key={p.id}>
                <td><ClasseBadge classe={p.classe} /></td>
                <td>{p.nome}</td>
                <td className="tabular">{fmtBRL(p.faturamento)}</td>
                <td className="tabular text-secondary">{p.pct.toFixed(1)}%</td>
                <td className="tabular text-secondary">{p.acumulada.toFixed(1)}%</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>);

}

// ---------- Tela 8: Sugestão de compra ----------
function SugestaoScreen() {
  const sugeridos = PRODUTOS.filter((p) => p.diasRuptura <= 10);
  // group by fornecedor
  const grupos = {};
  sugeridos.forEach((p) => {
    if (!grupos[p.fornecedor]) grupos[p.fornecedor] = [];
    const qtd = Math.ceil(p.demandaDiaria * (p.leadTime + 7));
    grupos[p.fornecedor].push({ ...p, qtdSugerida: qtd, subtotal: qtd * p.precoMedio });
  });

  const [estado, setEstado] = React.useState(() => {
    const init = {};
    Object.entries(grupos).forEach(([forn, items]) => {
      items.forEach((it) => {init[it.id] = { checked: true, qtd: it.qtdSugerida };});
    });
    return init;
  });

  const totalGeral = Object.entries(grupos).reduce((acc, [, items]) => {
    return acc + items.reduce((a, it) => {
      const s = estado[it.id];if (!s.checked) return a;
      return a + s.qtd * it.precoMedio;
    }, 0);
  }, 0);
  const totalItens = Object.values(estado).filter((s) => s.checked).length;

  if (sugeridos.length === 0) {
    return (
      <div className="page">
        <div className="page-header"><h1 className="page-title">Relatório de compra sugerido</h1></div>
        <div className="card" style={{ textAlign: 'center', padding: '48px 20px' }}>
          <p>Nenhuma compra sugerida no momento.</p>
        </div>
      </div>);

  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Relatório de compra sugerido</h1>
          <p className="page-subtitle">Baseado nas previsões e nos pontos de reposição atuais</p>
        </div>
        <div className="card kpi-card" style={{ minWidth: 240, padding: 14 }}>
          <div className="label">Resumo</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: 4 }}>
            <span className="tabular" style={{ fontSize: 22, fontWeight: 500 }}>{fmtBRL(totalGeral)}</span>
            <span className="text-meta">{totalItens} itens · {Object.keys(grupos).length} fornecedores</span>
          </div>
        </div>
      </div>

      <div className="stack">
        {Object.entries(grupos).map(([forn, items]) => {
          const subtotal = items.reduce((a, it) => {
            const s = estado[it.id];if (!s.checked) return a;
            return a + s.qtd * it.precoMedio;
          }, 0);
          return (
            <div key={forn} className="card" style={{ padding: 0 }}>
              <div className="row-between" style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
                <div>
                  <div style={{ fontWeight: 500, fontSize: 16 }}>{forn}</div>
                  <div className="text-meta">{items.length} itens sugeridos · lead time {items[0].leadTime} dias</div>
                </div>
                <div className="row" style={{ gap: 8 }}>
                  <div style={{ textAlign: 'right', marginRight: 8 }}>
                    <div className="text-meta">Subtotal</div>
                    <div className="tabular" style={{ fontWeight: 500 }}>{fmtBRL(subtotal)}</div>
                  </div>
                  <button className="btn btn-secondary btn-sm"><IconDownload size={14} /> PDF</button>
                  <button className="btn btn-secondary btn-sm"><IconWhats size={14} /> WhatsApp</button>
                </div>
              </div>
              <table className="table">
                <thead>
                  <tr>
                    <th style={{ width: 36 }}></th>
                    <th>Produto</th>
                    <th>Quantidade</th>
                    <th>Preço unit.</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((it) => {
                    const s = estado[it.id];
                    return (
                      <tr key={it.id}>
                        <td><div className={`checkbox ${s.checked ? 'checked' : ''}`} onClick={() => setEstado({ ...estado, [it.id]: { ...s, checked: !s.checked } })} /></td>
                        <td>{it.nome}</td>
                        <td>
                          <input type="number" className="input" style={{ width: 90, height: 32, padding: '0 8px' }}
                          value={s.qtd} onChange={(e) => setEstado({ ...estado, [it.id]: { ...s, qtd: +e.target.value || 0 } })} />
                          <span className="text-meta" style={{ marginLeft: 6 }}>{it.unidade}</span>
                        </td>
                        <td className="tabular">{fmtBRL(it.precoMedio)}</td>
                        <td className="tabular">{fmtBRL(s.qtd * it.precoMedio)}</td>
                      </tr>);

                  })}
                </tbody>
              </table>
            </div>);

        })}
      </div>

      <div className="row" style={{ justifyContent: 'flex-end', marginTop: 20, gap: 8 }}>
        <button className="btn btn-secondary">Salvar rascunho</button>
        <button className="btn btn-primary">Confirmar pedidos</button>
      </div>
    </div>);

}

Object.assign(window, { AlertasScreen, DetalheScreen, ABCScreen, SugestaoScreen });