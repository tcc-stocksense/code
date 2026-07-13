// App shell: sidebar, topbar, roteamento por state

function Sidebar({ tela, go }) {
  const items = [
  { key: 'home', label: 'Home', icon: <IconHome size={18} /> },
  { key: 'estoque', label: 'Estoque', icon: <IconBox size={18} /> },
  { key: 'alertas', label: 'Alertas de reposição', icon: <IconBell size={18} /> },
  { key: 'abc', label: 'Curva ABC', icon: <IconChart size={18} /> },
  { key: 'sugestao', label: 'Sugestão de compra', icon: <IconShop size={18} /> },
  { key: 'importar', label: 'Importar dados', icon: <IconUpload size={18} /> },
  { key: 'config', label: 'Configurações', icon: <IconCog size={18} /> }];


  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-mark">P</div>
        <div className="logo-text">Motor Preditivo<small>de estoque</small></div>
      </div>
      <nav className="sidebar-nav">
        <div className="nav-section-label">Operação</div>
        {items.slice(0, 5).map((it) =>
        <div key={it.key} className={`nav-item ${tela === it.key ? 'active' : ''}`} onClick={() => go(it.key)}>
            {it.icon}<span>{it.label}</span>
          </div>
        )}
        <div className="nav-section-label" style={{ marginTop: 12 }}>Sistema</div>
        {items.slice(5).map((it) =>
        <div key={it.key} className={`nav-item ${tela === it.key ? 'active' : ''}`} onClick={() => go(it.key)}>
            {it.icon}<span>{it.label}</span>
          </div>
        )}
      </nav>
      <div className="sidebar-footer">
        <div className="nav-section-label" style={{ padding: '4px 12px 4px' }}>Acesso técnico</div>
        <div className={`nav-item ${tela === 'tecnica' ? 'active' : ''}`} onClick={() => go('tecnica')}>
          <IconBeaker size={18} /><span>Comparativo de modelos</span>
        </div>
      </div>
    </aside>);

}

function Topbar({ onLogout }) {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <strong>{ESTABELECIMENTO.nome}</strong>
        <span style={{ color: 'var(--text-tertiary)' }}>·</span>
        <span>CNPJ {ESTABELECIMENTO.cnpj}</span>
      </div>
      <div className="topbar-right">
        <span className="text-meta" style={{ display: 'none' }}>{USUARIO.nome}</span>
        <div className="avatar" title={`${USUARIO.nome} — sair`} onClick={onLogout}>{USUARIO.iniciais}</div>
      </div>
    </div>);

}

const TELAS_VALIDAS = ['home', 'estoque', 'alertas', 'abc', 'sugestao', 'importar', 'config', 'detalhe', 'tecnica'];

function telaDoHash() {
  const h = (window.location.hash || '').replace('#', '').trim();
  return TELAS_VALIDAS.includes(h) ? h : null;
}

function App() {
  const hashTela = telaDoHash();
  // Deep-link: se a URL tiver #estoque, #abc etc., pula o login e abre a tela direto.
  // Isso permite importar cada tela individualmente no Figma (html.to.design) por uma URL própria.
  const [logado, setLogado] = React.useState(!!hashTela);
  const [tela, setTela] = React.useState(hashTela || 'home');
  const [produtoId, setProdutoId] = React.useState(null);

  React.useEffect(() => {
    function onHash() {
      const t = telaDoHash();
      if (t) {
        setLogado(true);
        setTela(t);
      }
    }
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  function go(t, id) {
    setTela(t);
    if (id) setProdutoId(id);
    if (TELAS_VALIDAS.includes(t)) {
      try {window.history.replaceState(null, '', '#' + t);} catch (e) {}
    }
    window.scrollTo({ top: 0 });
  }

  if (!logado) return <LoginScreen onLogin={() => setLogado(true)} />;

  let content;
  switch (tela) {
    case 'home':content = <HomeScreen go={go} />;break;
    case 'estoque':content = <EstoqueScreen go={go} />;break;
    case 'alertas':content = <AlertasScreen go={go} />;break;
    case 'abc':content = <ABCScreen />;break;
    case 'sugestao':content = <SugestaoScreen />;break;
    case 'importar':content = <ImportarScreen />;break;
    case 'config':content = <ConfigScreen />;break;
    case 'detalhe':content = <DetalheScreen produtoId={produtoId} go={go} />;break;
    case 'tecnica':content = <TecnicaScreen />;break;
    default:content = <HomeScreen go={go} />;
  }

  // Screen label para comentários
  const screenLabels = {
    home: '01 Home',
    estoque: '02 Estoque',
    alertas: '03 Alertas de reposição',
    abc: '04 Curva ABC',
    sugestao: '05 Sugestão de compra',
    importar: '06 Importar dados',
    config: '07 Configurações',
    detalhe: '08 Detalhe de produto',
    tecnica: '09 Comparativo de modelos'
  };

  return (
    <div className="app">
      <Sidebar tela={tela} go={go} />
      <main className="main" data-screen-label={screenLabels[tela] || tela}>
        <Topbar onLogout={() => setLogado(false)} />
        {content}
      </main>
    </div>);

}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);