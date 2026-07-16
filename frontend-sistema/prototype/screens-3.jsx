// Screens: Configurações, Comparativo de modelos (técnica)

// ---------- Tela 9: Configurações ----------
function ConfigScreen() {
  const [tab, setTab] = React.useState('estabelecimento');
  const [estab, setEstab] = React.useState({ ...ESTABELECIMENTO });
  const [user, setUser] = React.useState({ nome: USUARIO.nome, email: USUARIO.email });
  const [notif, setNotif] = React.useState({ critico: true, frequencia: 'diario' });
  const [salvo, setSalvo] = React.useState(false);

  function salvar(e) { e.preventDefault(); setSalvo(true); setTimeout(()=>setSalvo(false), 2000); }

  return (
    <div className="page" style={{maxWidth:760}}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Configurações</h1>
          <p className="page-subtitle">Dados do estabelecimento, perfil e preferências de notificação</p>
        </div>
      </div>

      <div className="tabs">
        <div className={`tab ${tab==='estabelecimento'?'active':''}`} onClick={()=>setTab('estabelecimento')}>Estabelecimento</div>
        <div className={`tab ${tab==='usuario'?'active':''}`} onClick={()=>setTab('usuario')}>Usuário</div>
        <div className={`tab ${tab==='notif'?'active':''}`} onClick={()=>setTab('notif')}>Notificações</div>
      </div>

      <form onSubmit={salvar} className="card">
        {tab === 'estabelecimento' && (
          <div className="stack" style={{gap:14, maxWidth:480}}>
            <div className="field">
              <label className="field-label">Nome fantasia</label>
              <input className="input" value={estab.nome} onChange={e=>setEstab({...estab, nome: e.target.value})}/>
            </div>
            <div className="field">
              <label className="field-label">CNPJ</label>
              <input className="input" value={estab.cnpj} onChange={e=>setEstab({...estab, cnpj: e.target.value})}/>
            </div>
            <div className="field">
              <label className="field-label">Endereço</label>
              <input className="input" value={estab.endereco} onChange={e=>setEstab({...estab, endereco: e.target.value})}/>
            </div>
          </div>
        )}

        {tab === 'usuario' && (
          <div className="stack" style={{gap:14, maxWidth:480}}>
            <div className="field">
              <label className="field-label">Nome</label>
              <input className="input" value={user.nome} onChange={e=>setUser({...user, nome: e.target.value})}/>
            </div>
            <div className="field">
              <label className="field-label">Email</label>
              <input className="input" type="email" value={user.email} onChange={e=>setUser({...user, email: e.target.value})}/>
            </div>
            <div>
              <a href="#" onClick={e=>e.preventDefault()} className="text-small">Alterar senha</a>
            </div>
          </div>
        )}

        {tab === 'notif' && (
          <div className="stack" style={{gap:18, maxWidth:480}}>
            <div className="row-between" style={{padding:'8px 0'}}>
              <div>
                <div style={{fontWeight:500}}>Alerta de estoque crítico</div>
                <div className="text-meta">Notificar quando um produto passar para estado crítico.</div>
              </div>
              <div className={`toggle ${notif.critico ? 'on' : ''}`} onClick={()=>setNotif({...notif, critico: !notif.critico})}/>
            </div>
            <div className="divider"/>
            <div className="field">
              <label className="field-label">Resumo por email</label>
              <select className="select" value={notif.frequencia} onChange={e=>setNotif({...notif, frequencia: e.target.value})}>
                <option value="diario">Diário, às 08:00</option>
                <option value="semanal">Semanal, segunda às 08:00</option>
                <option value="nunca">Não enviar</option>
              </select>
            </div>
          </div>
        )}

        <div className="row" style={{justifyContent:'flex-end', marginTop:24, gap:10, alignItems:'center'}}>
          {salvo && <span className="text-meta" style={{color:'var(--success-600)'}}><IconCheck size={14}/> Salvo.</span>}
          <button type="submit" className="btn btn-primary">Salvar</button>
        </div>
      </form>
    </div>
  );
}

// ---------- Tela 10: Comparativo de modelos (técnica) ----------
function TecnicaScreen() {
  const [metrica, setMetrica] = React.useState('MAPE');

  const data = COMPARATIVO_MODELOS.map(m => ({
    label: m.nome.split(' ').slice(0,2).join(' '),
    hw: m['hw' + metrica.charAt(0) + metrica.slice(1).toLowerCase()],
    pro: m['pro' + metrica.charAt(0) + metrica.slice(1).toLowerCase()],
  }));

  const formatMetric = (v) => metrica === 'MAPE' ? v.toFixed(1) + '%' : v.toFixed(2);

  return (
    <div className="page">
      <div className="tech-banner" style={{marginBottom:20}}>
        <span style={{fontWeight:500}}>Acesso técnico</span> · este painel é destinado à equipe de modelagem e à banca avaliadora. Não tem efeito no fluxo do gestor.
      </div>

      <div className="page-header">
        <div>
          <h1 className="page-title">Comparativo de modelos preditivos</h1>
          <p className="page-subtitle">Holt-Winters vs Prophet · métricas agregadas e por produto</p>
        </div>
      </div>

      <div className="kpi-grid" style={{gridTemplateColumns:'repeat(3, 1fr)'}}>
        <MetricCard label="MAPE" hw={MAPE_GLOBAL.hw} pro={MAPE_GLOBAL.prophet} unit="%" lowerBetter/>
        <MetricCard label="RMSE" hw={RMSE_GLOBAL.hw} pro={RMSE_GLOBAL.prophet} lowerBetter/>
        <MetricCard label="MAE"  hw={MAE_GLOBAL.hw} pro={MAE_GLOBAL.prophet} lowerBetter/>
      </div>

      <div className="card" style={{marginBottom:20}}>
        <div className="row-between" style={{marginBottom:12}}>
          <h3>Comparação por produto</h3>
          <select className="select" value={metrica} onChange={e=>setMetrica(e.target.value)} style={{width:160}}>
            <option value="MAPE">MAPE</option>
            <option value="RMSE">RMSE</option>
            <option value="MAE">MAE</option>
          </select>
        </div>
        <GroupedBars
          data={data}
          keys={['hw','pro']}
          colors={['#1F4A30','#2E5A78']}
          labels={['Holt-Winters', 'Prophet']}
          height={320}
          formatY={formatMetric}
        />
      </div>

      <div className="card" style={{padding:0, overflow:'hidden', marginBottom:20}}>
        <div style={{padding:'16px 20px', borderBottom:'1px solid var(--border)'}}>
          <h3>Métricas detalhadas por produto</h3>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>Produto</th>
              <th>MAPE H-W</th>
              <th>MAPE Prophet</th>
              <th>RMSE H-W</th>
              <th>RMSE Prophet</th>
              <th>MAE H-W</th>
              <th>MAE Prophet</th>
              <th>Recomendado</th>
            </tr>
          </thead>
          <tbody>
            {COMPARATIVO_MODELOS.map(m => (
              <tr key={m.id}>
                <td>{m.nome}</td>
                <td className="tabular">{m.hwMape.toFixed(2)}%</td>
                <td className="tabular">{m.proMape.toFixed(2)}%</td>
                <td className="tabular">{m.hwRmse.toFixed(2)}</td>
                <td className="tabular">{m.proRmse.toFixed(2)}</td>
                <td className="tabular">{m.hwMae.toFixed(2)}</td>
                <td className="tabular">{m.proMae.toFixed(2)}</td>
                <td><span className={`badge ${m.recomendado === 'Prophet' ? 'badge-info' : 'badge-primary'}`}>{m.recomendado}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3 style={{marginBottom:12}}>Execuções</h3>
        <div style={{fontFamily:'ui-monospace, SFMono-Regular, Menlo, monospace', fontSize:13, color:'var(--text-secondary)', lineHeight:1.8}}>
          <div>[2026-05-18 03:00:14] retraining iniciado · 312 SKUs</div>
          <div>[2026-05-18 03:02:47] holt-winters: ok · 312/312 séries · MAPE agregado 7.32%</div>
          <div>[2026-05-18 03:08:21] prophet: ok · 312/312 séries · MAPE agregado 6.78%</div>
          <div>[2026-05-18 03:08:24] persistência: postgresql/forecasts · 9.840 linhas inseridas</div>
          <div>[2026-05-18 03:08:25] <span style={{color:'var(--success-600)'}}>concluído</span> · próximo agendamento: 2026-05-19 03:00</div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, hw, pro, unit = '', lowerBetter }) {
  const winnerHW = lowerBetter ? hw < pro : hw > pro;
  const fmt = (v) => v.toFixed(2) + unit;
  return (
    <div className="card">
      <div className="label" style={{marginBottom:14}}>{label} agregado</div>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12}}>
        <div>
          <div className="text-meta" style={{marginBottom:4}}>Holt-Winters {winnerHW && <span className="badge badge-primary" style={{marginLeft:4}}>melhor</span>}</div>
          <div className="tabular" style={{fontSize:24, fontWeight:500}}>{fmt(hw)}</div>
        </div>
        <div>
          <div className="text-meta" style={{marginBottom:4}}>Prophet {!winnerHW && <span className="badge badge-info" style={{marginLeft:4}}>melhor</span>}</div>
          <div className="tabular" style={{fontSize:24, fontWeight:500}}>{fmt(pro)}</div>
        </div>
      </div>
      <div className="text-meta" style={{marginTop:10}}>
        Diferença: {Math.abs(hw - pro).toFixed(2)}{unit} {lowerBetter ? '(quanto menor, melhor)' : ''}
      </div>
    </div>
  );
}

Object.assign(window, { ConfigScreen, TecnicaScreen });
