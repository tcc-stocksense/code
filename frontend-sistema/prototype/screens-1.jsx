// Screens 1-4: Login, Home, Importar, Estoque

// ---------- Tela 1: Login ----------
function LoginScreen({ onLogin }) {
  const [email, setEmail] = React.useState('juliana@mercadosaojoao.com.br');
  const [senha, setSenha] = React.useState('••••••••');
  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <div className="logo-mark">P</div>
          <div className="logo-text">Motor Preditivo<small>de estoque</small></div>
        </div>
        <h2 style={{textAlign:'center', fontSize:18, marginBottom:6}}>Entrar no sistema</h2>
        <p className="text-meta" style={{textAlign:'center', marginBottom:24}}>Use os dados do seu estabelecimento para acessar</p>
        <form onSubmit={(e)=>{e.preventDefault(); onLogin();}}>
          <div className="stack" style={{gap:14}}>
            <div className="field">
              <label className="field-label">Email</label>
              <input className="input" value={email} onChange={(e)=>setEmail(e.target.value)} type="email"/>
            </div>
            <div className="field">
              <label className="field-label">Senha</label>
              <input className="input" value={senha} onChange={(e)=>setSenha(e.target.value)} type="password"/>
            </div>
            <button type="submit" className="btn btn-primary btn-block" style={{marginTop:4}}>Entrar</button>
            <a href="#" style={{textAlign:'center', fontSize:13, color:'var(--text-secondary)'}} onClick={e=>e.preventDefault()}>Esqueci minha senha</a>
          </div>
        </form>
        <div className="login-footer">
          Motor Preditivo de Estoque — v0.4 protótipo
        </div>
      </div>
    </div>
  );
}

// ---------- Tela 2: Home ----------
function HomeScreen({ go }) {
  const { hist, proj } = React.useMemo(() => semanasHistoricoProjecao(), []);
  const produtosEmRisco7d = PRODUTOS.filter(p => p.diasRuptura <= 7).length;
  const produtosCriticos = PRODUTOS.filter(p => p.diasRuptura < 3).length;
  const valorRisco = PRODUTOS.filter(p => p.diasRuptura <= 7).reduce((acc, p) => acc + p.faturamento * 0.07 / 4, 0);
  const acuracia = 100 - MAPE_GLOBAL.prophet;

  return (
    <div className="page">
      <div className="stack-tight" style={{marginBottom:24}}>
        <h1 className="page-title">Bom dia, Juliana.</h1>
        <p className="page-subtitle">Hoje, 18 de maio.</p>
      </div>

      <div className="banner banner-warning">
        <IconAlert/>
        <div className="banner-body">
          <strong>Você tem 7 produtos que precisam ser pedidos hoje.</strong>
          <small>3 estão em estado crítico (menos de 3 dias).</small>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={()=>go('alertas')}>Ver lista</button>
      </div>

      <div className="kpi-grid">
        <div className="card kpi-card">
          <div className="label">Risco de faltar</div>
          <span className="kpi-number">{produtosEmRisco7d}</span>
          <div className="kpi-context">nos próximos 7 dias</div>
        </div>
        <div className="card kpi-card">
          <div className="label">Crítico agora</div>
          <span className="kpi-number" style={{color:'var(--danger-700)'}}>{produtosCriticos}</span>
          <div className="kpi-context">menos de 3 dias até zerar</div>
        </div>
        <div className="card kpi-card">
          <div className="label">Valor em risco</div>
          <span className="kpi-number">{fmtBRLcompact(valorRisco)}</span>
          <div className="kpi-context">venda perdida estimada (coef. ABRAS)</div>
        </div>
        <div className="card kpi-card">
          <div className="label">Acurácia do modelo</div>
          <span className="kpi-number">{acuracia.toFixed(1)}%</span>
          <div className="kpi-context">MAPE médio últimas 4 semanas</div>
        </div>
      </div>

      <div className="card" style={{marginBottom:24}}>
        <div className="row-between" style={{marginBottom:6}}>
          <h3>Previsão de faturamento</h3>
          <span className="text-meta">últimas 8 semanas + projeção 4 semanas</span>
        </div>
        <LineChart hist={hist} proj={proj} height={260} formatY={(v)=>fmtBRLcompact(v)}/>
      </div>

      <div className="card">
        <div className="row-between" style={{marginBottom:14}}>
          <h3>Próximos alertas de reposição</h3>
          <button className="btn btn-tertiary btn-sm" onClick={()=>go('alertas')}>Ver todos <IconChev size={14}/></button>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th style={{width:24}}></th>
              <th>Produto</th>
              <th>Até ruptura</th>
              <th>Sugestão</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {TOP_ALERTAS.map(p => (
              <tr key={p.id} style={{cursor:'pointer'}} onClick={()=>go('detalhe', p.id)}>
                <td><StatusDot dias={p.diasRuptura}/></td>
                <td>{p.nome}</td>
                <td className="tabular">{p.diasRuptura === 0 ? 'zerado' : `${p.diasRuptura} ${p.diasRuptura===1?'dia':'dias'}`}</td>
                <td className="tabular">{Math.round(p.demandaDiaria * (p.leadTime + 7))} {p.unidade}</td>
                <td><button className="btn btn-tertiary btn-sm">Detalhe <IconChev size={14}/></button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------- Tela 3: Importar dados ----------
// Cada planilha é um bloco independente com sua própria área de upload.
// O gestor sobe só os "temas" que precisar — não é obrigatório enviar tudo.
const PLANILHAS_IMPORT = [
  { key: 'produtos',        nome: 'Produtos',             tipo: 'obrigatória', grupo: 'Obrigatórias', campos: 'sku, nome, categoria, preço, unidade',  linhasMock: 312,   arq: 'produtos.xlsx' },
  { key: 'vendas',          nome: 'Vendas',               tipo: 'obrigatória', grupo: 'Obrigatórias', campos: 'data, sku, quantidade, valor_total',     linhasMock: 28430, arq: 'vendas_2024.csv' },
  { key: 'estabelecimento', nome: 'Estabelecimento',      tipo: 'desejável',   grupo: 'Desejáveis',   campos: 'nome, cnpj, endereço',                   linhasMock: 1,     arq: 'estabelecimento.xlsx' },
  { key: 'fornecedores',    nome: 'Fornecedores',         tipo: 'desejável',   grupo: 'Desejáveis',   campos: 'id, nome, contato, lead_time_dias',      linhasMock: 6,     arq: 'fornecedores.xlsx' },
  { key: 'prodForn',        nome: 'Produto × Fornecedor', tipo: 'desejável',   grupo: 'Desejáveis',   campos: 'sku, id_fornecedor, preco_compra',       linhasMock: 1234,  arq: 'prod_fornecedor.csv' },
];

function ImportarScreen() {
  const [arquivos, setArquivos] = React.useState({
    produtos:        { status: 'sucesso', linhas: 312,   nome: 'produtos.xlsx' },
    vendas:          { status: 'sucesso', linhas: 28430, nome: 'vendas_2024.csv' },
    estabelecimento: { status: 'vazio' },
    fornecedores:    { status: 'erro', erro: 'Linha 45: data fora do formato. Use AAAA-MM-DD.', nome: 'fornecedores.xlsx' },
    prodForn:        { status: 'vazio' },
  });
  const [open, setOpen] = React.useState(false);

  function enviar(pl) {
    // Simula validação e processamento do arquivo daquele tema
    setArquivos(a => ({ ...a, [pl.key]: { status: 'processing', linhas: pl.linhasMock, nome: pl.arq } }));
    setTimeout(() => {
      setArquivos(a => ({ ...a, [pl.key]: { status: 'sucesso', linhas: pl.linhasMock, nome: pl.arq } }));
    }, 1600);
  }
  function remover(pl) {
    setArquivos(a => ({ ...a, [pl.key]: { status: 'vazio' } }));
  }

  const obrigOk = arquivos.produtos.status === 'sucesso' && arquivos.vendas.status === 'sucesso';
  const enviadas = PLANILHAS_IMPORT.filter(pl => arquivos[pl.key].status === 'sucesso').length;

  const grupos = ['Obrigatórias', 'Desejáveis'];

  return (
    <div className="page" style={{maxWidth:760}}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Importar dados de vendas</h1>
          <p className="page-subtitle">Envie cada planilha no seu próprio bloco. Você pode subir só o que precisar — não é obrigatório enviar tudo.</p>
        </div>
      </div>

      <div className="card" style={{marginBottom:20, padding:0}}>
        <button className="row-between" style={{width:'100%', background:'none', border:'none', padding:'16px 20px', cursor:'pointer', textAlign:'left'}} onClick={()=>setOpen(!open)}>
          <span style={{fontWeight:500}}>Como preparar suas planilhas</span>
          <IconChevDown size={16} style={{transform: open ? 'rotate(180deg)' : 'none'}}/>
        </button>
        {open && (
          <div style={{padding:'0 20px 20px', borderTop:'1px solid var(--border)', paddingTop:16}}>
            <p className="text-small text-secondary" style={{marginBottom:10}}>
              Os campos esperados de cada planilha aparecem dentro de cada bloco abaixo. Formatos aceitos: .xlsx, .xls e .csv até 20MB.
            </p>
            <a href="#" onClick={e=>e.preventDefault()} style={{display:'inline-block', marginTop:4, fontSize:14}}>Baixar modelos de planilha</a>
          </div>
        )}
      </div>

      {grupos.map(grupo => {
        const doGrupo = PLANILHAS_IMPORT.filter(pl => pl.grupo === grupo);
        if (doGrupo.length === 0) return null;
        return (
          <div key={grupo}>
            <div className="import-tema-label">{grupo}</div>
            <div className="stack-tight" style={{marginBottom:4}}>
              {doGrupo.map(pl => (
                <ImportBlock key={pl.key} pl={pl} f={arquivos[pl.key]} onEnviar={()=>enviar(pl)} onRemover={()=>remover(pl)}/>
              ))}
            </div>
          </div>
        );
      })}

      <div className="row-between" style={{marginTop:24}}>
        <span className="text-meta">
          {enviadas} {enviadas===1?'planilha enviada':'planilhas enviadas'} · {obrigOk ? 'obrigatórias OK, pronto para processar.' : 'envie Produtos e Vendas para gerar previsões.'}
        </span>
        <button className="btn btn-primary" disabled={!obrigOk}>Processar dados</button>
      </div>
    </div>
  );
}

function ImportBlock({ pl, f, onEnviar, onRemover }) {
  const status = f.status === 'sucesso' ? 'success' : f.status === 'erro' ? 'error' : f.status === 'processing' ? 'processing' : '';
  const badgeClass = pl.tipo === 'obrigatória' ? 'badge-primary' : pl.tipo === 'opcional' ? 'badge-neutral' : 'badge-warning';

  return (
    <div className={`import-block ${status}`}>
      <div className="import-block-head">
        <div className="import-block-title">
          <IconFile size={18} style={{color:'var(--text-tertiary)'}}/>
          <span className="name">{pl.nome}</span>
          <span className={`badge ${badgeClass}`}>{pl.tipo}</span>
        </div>
        {f.status === 'sucesso' && <span className="badge badge-success"><IconCheck size={13}/> enviada</span>}
        {f.status === 'erro' && <span className="badge badge-danger"><IconAlert size={13}/> com erro</span>}
        {f.status === 'processing' && <span className="badge badge-info"><span className="spinner"/> validando</span>}
      </div>

      <div className="import-block-body">
        {f.status === 'vazio' && (
          <div className="drop-mini" onClick={onEnviar}>
            <IconUpload size={20}/>
            <div style={{textAlign:'left'}}>
              <div>Arraste a planilha de <strong style={{fontWeight:500, color:'var(--text-primary)'}}>{pl.nome}</strong> aqui ou clique para escolher</div>
              <div className="text-meta">Campos esperados: {pl.campos}</div>
            </div>
          </div>
        )}

        {f.status === 'processing' && (
          <div className="file-line processing">
            <span className="spinner"/>
            <div className="file-meta">
              <div className="fn">{f.nome}</div>
              <div className="sub">Validando {f.linhas.toLocaleString('pt-BR')} linhas…</div>
            </div>
          </div>
        )}

        {f.status === 'sucesso' && (
          <div className="file-line success">
            <IconCheck size={18}/>
            <div className="file-meta">
              <div className="fn">{f.nome}</div>
              <div className="sub">{f.linhas.toLocaleString('pt-BR')} linhas processadas</div>
            </div>
            <button className="btn btn-tertiary btn-sm" onClick={onEnviar}>Substituir</button>
            <button className="btn btn-tertiary btn-sm" onClick={onRemover}>Remover</button>
          </div>
        )}

        {f.status === 'erro' && (
          <div className="stack-tight">
            <div className="file-line error">
              <IconAlert size={18}/>
              <div className="file-meta">
                <div className="fn">{f.nome}</div>
                <div className="sub">{f.erro}</div>
              </div>
            </div>
            <div className="drop-mini" onClick={onEnviar} style={{marginTop:8}}>
              <IconUpload size={18}/>
              <span>Corrija a planilha e reenvie</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------- Tela 4: Estoque ----------
function EstoqueScreen({ go }) {
  useEstoqueStore();
  const [busca, setBusca] = React.useState('');
  const [cat, setCat] = React.useState('todas');
  const [status, setStatus] = React.useState('todos');
  const [classe, setClasse] = React.useState('todas');

  const filtrados = PRODUTOS.map(produtoView).filter(p => {
    if (busca && !p.nome.toLowerCase().includes(busca.toLowerCase())) return false;
    if (cat !== 'todas' && p.categoria !== cat) return false;
    if (classe !== 'todas' && p.classe !== classe) return false;
    if (status !== 'todos' && STATUS(p.diasRuptura) !== status) return false;
    return true;
  }).sort((a,b) => a.diasRuptura - b.diasRuptura);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Estoque atual</h1>
          <p className="page-subtitle">{filtrados.length} produtos · ordenados por urgência de reposição</p>
        </div>
      </div>

      <div className="filters-row">
        <div className="field" style={{flex:'1 1 300px', maxWidth:380}}>
          <div style={{position:'relative'}}>
            <input className="input search" placeholder="Buscar produto" value={busca} onChange={e=>setBusca(e.target.value)} style={{paddingLeft:38}}/>
            <span style={{position:'absolute', left:12, top:11, color:'var(--text-tertiary)'}}><IconSearch size={16}/></span>
          </div>
        </div>
        <select className="select" value={cat} onChange={e=>setCat(e.target.value)}>
          <option value="todas">Todas categorias</option>
          {CATEGORIAS.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select className="select" value={status} onChange={e=>setStatus(e.target.value)}>
          <option value="todos">Todos status</option>
          <option value="critico">Crítico</option>
          <option value="atencao">Atenção</option>
          <option value="ok">OK</option>
        </select>
        <select className="select" value={classe} onChange={e=>setClasse(e.target.value)}>
          <option value="todas">Todas classes</option>
          <option value="A">Classe A</option>
          <option value="B">Classe B</option>
          <option value="C">Classe C</option>
        </select>
      </div>

      <div className="card" style={{padding:0, overflow:'hidden'}}>
        <table className="table">
          <thead>
            <tr>
              <th style={{width:60}}>Status</th>
              <th>Produto</th>
              <th>Categoria</th>
              <th>Estoque</th>
              <th>Até ruptura</th>
              <th>ABC</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtrados.map(p => (
              <tr key={p.id} style={{cursor:'pointer'}} onClick={()=>go('detalhe', p.id)}>
                <td><StatusPill dias={p.diasRuptura}/></td>
                <td><div style={{fontWeight:500}}>{p.nome}</div></td>
                <td className="text-small text-secondary">{p.categoria}</td>
                <td onClick={(e)=>e.stopPropagation()}><EstoqueField produto={p} variant="cell"/></td>
                <td className="tabular">{p.diasRuptura === 0 ? 'zerado' : `${p.diasRuptura} ${p.diasRuptura===1?'dia':'dias'}`}</td>
                <td><ClasseBadge classe={p.classe}/></td>
                <td><button className="btn btn-tertiary btn-sm" onClick={(e)=>{e.stopPropagation(); go('detalhe', p.id);}}>Detalhe <IconChev size={14}/></button></td>
              </tr>
            ))}
            {filtrados.length === 0 && (
              <tr><td colSpan="7" style={{textAlign:'center', padding:'40px 20px', color:'var(--text-secondary)'}}>Nenhum produto bate com os filtros.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="row-between" style={{marginTop:16}}>
        <span className="text-meta">Mostrando {filtrados.length} de {PRODUTOS.length} produtos</span>
        <div className="row">
          <button className="btn btn-secondary btn-sm" disabled>Anterior</button>
          <span className="text-meta">Página 1 de 1</span>
          <button className="btn btn-secondary btn-sm" disabled>Próxima</button>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { LoginScreen, HomeScreen, ImportarScreen, EstoqueScreen });
