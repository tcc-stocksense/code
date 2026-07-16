// UI primitives + icons (lucide-style outline)

const Icon = ({ d, size = 18, stroke = 2, children }) =>
<svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round">
    {children || <path d={d} />}
  </svg>;


const IconHome = (p) => <Icon {...p}><path d="M3 10.5 12 3l9 7.5" /><path d="M5 9.5V21h14V9.5" /></Icon>;
const IconBox = (p) => <Icon {...p}><path d="M3 7.5 12 3l9 4.5v9L12 21l-9-4.5z" /><path d="M3 7.5 12 12l9-4.5" /><path d="M12 12v9" /></Icon>;
const IconBell = (p) => <Icon {...p}><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" /><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" /></Icon>;
const IconChart = (p) => <Icon {...p}><path d="M3 3v18h18" /><path d="M7 14l4-4 4 4 5-6" /></Icon>;
const IconProduct = (p) => <Icon {...p}><path d="M20 7L12 3 4 7v10l8 4 8-4z" /><path d="M9 5.2v6.3L4 9" /></Icon>;
const IconShop = (p) => <Icon {...p}><path d="M3 7h18l-1 4H4z" /><path d="M5 11v9h14v-9" /><path d="M9 15h6" /></Icon>;
const IconTrash = (p) => <Icon {...p}><path d="M3 6h18" /><path d="M8 6V4h8v2" /><path d="M19 6l-1 14H6L5 6" /><path d="M10 11v6M14 11v6" /></Icon>;
const IconCog = (p) => <Icon {...p}><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" /></Icon>;
const IconBeaker = (p) => <Icon {...p}><path d="M9 3h6v6l5 9a2 2 0 0 1-1.8 3H5.8A2 2 0 0 1 4 18l5-9z" /><path d="M7 14h10" /></Icon>;
const IconUpload = (p) => <Icon {...p}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><path d="M17 8l-5-5-5 5" /><path d="M12 3v12" /></Icon>;
const IconDownload = (p) => <Icon {...p}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><path d="M7 10l5 5 5-5" /><path d="M12 15V3" /></Icon>;
const IconSearch = (p) => <Icon {...p}><circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" /></Icon>;
const IconCheck = (p) => <Icon {...p}><path d="M5 12l5 5L20 7" /></Icon>;
const IconX = (p) => <Icon {...p}><path d="M6 6l12 12M18 6 6 18" /></Icon>;
const IconChev = (p) => <Icon {...p}><path d="M9 18l6-6-6-6" /></Icon>;
const IconChevDown = (p) => <Icon {...p}><path d="M6 9l6 6 6-6" /></Icon>;
const IconArrowLeft = (p) => <Icon {...p}><path d="M19 12H5" /><path d="M12 19l-7-7 7-7" /></Icon>;
const IconAlert = (p) => <Icon {...p}><circle cx="12" cy="12" r="10" /><path d="M12 8v4" /><path d="M12 16h.01" /></Icon>;
const IconInfo = (p) => <Icon {...p}><circle cx="12" cy="12" r="10" /><path d="M12 16v-4" /><path d="M12 8h.01" /></Icon>;
const IconFile = (p) => <Icon {...p}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6" /></Icon>;
const IconTrend = (p) => <Icon {...p}><path d="M3 17l6-6 4 4 8-8" /><path d="M14 7h7v7" /></Icon>;
const IconTrendDown = (p) => <Icon {...p}><path d="M3 7l6 6 4-4 8 8" /><path d="M14 17h7v-7" /></Icon>;
const IconMinus = (p) => <Icon {...p}><path d="M5 12h14" /></Icon>;
const IconPlus = (p) => <Icon {...p}><path d="M12 5v14" /><path d="M5 12h14" /></Icon>;
const IconLock = (p) => <Icon {...p}><rect x="4" y="11" width="16" height="10" rx="2" /><path d="M8 11V7a4 4 0 0 1 8 0v4" /></Icon>;
const IconMail = (p) => <Icon {...p}><rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3 7l9 6 9-6" /></Icon>;
const IconWhats = (p) => <Icon {...p}><path d="M21 12a9 9 0 1 1-3.4-7L21 4l-1 4.5A9 9 0 0 1 21 12z" /><path d="M8 10c0 4 3 7 7 7l1-2-2.5-1-1 1c-1.5-.5-2.5-1.5-3-3l1-1L9 8z" /></Icon>;
const IconPencil = (p) => <Icon {...p}><path d="M12 20h9" /><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z" /></Icon>;

// Status pill (semáforo + label)
const StatusPill = ({ dias }) => {
  const status = STATUS(dias);
  if (status === 'critico') return <span className="badge badge-danger"><span className="dot dot-danger" />crítico</span>;
  if (status === 'atencao') return <span className="badge badge-warning"><span className="dot dot-warning" />atenção</span>;
  return <span className="badge badge-success"><span className="dot dot-success" />ok</span>;
};

const StatusDot = ({ dias }) => {
  const status = STATUS(dias);
  if (status === 'critico') return <span className="dot dot-danger" />;
  if (status === 'atencao') return <span className="dot dot-warning" />;
  return <span className="dot dot-success" />;
};

const ClasseBadge = ({ classe }) => {
  if (classe === 'A') return <span className="badge badge-primary">A</span>;
  if (classe === 'B') return <span className="badge badge-warning">B</span>;
  return <span className="badge badge-neutral">C</span>;
};

// Editor de estoque manual — variantes: 'panel' (detalhe) e 'cell' (linha da tabela)
function EstoqueField({ produto, variant = 'panel' }) {
  useEstoqueStore();
  const atual = getEstoque(produto.id);
  const editado = isEstoqueEditado(produto.id);
  const [editando, setEditando] = React.useState(false);
  const [val, setVal] = React.useState(atual);
  const inputRef = React.useRef(null);

  React.useEffect(() => {
    if (editando) {
      setVal(atual);
      const t = setTimeout(() => inputRef.current && inputRef.current.select(), 0);
      return () => clearTimeout(t);
    }
  }, [editando]);

  const dec = () => setVal((v) => Math.max(0, (parseInt(v, 10) || 0) - 1));
  const inc = () => setVal((v) => (parseInt(v, 10) || 0) + 1);
  const onChange = (e) => {
    const raw = e.target.value;
    setVal(raw === '' ? '' : Math.max(0, Math.round(+raw)));
  };
  const salvar = () => { setEstoque(produto.id, val === '' ? 0 : val); setEditando(false); };
  const cancelar = () => setEditando(false);
  const onKey = (e) => { if (e.key === 'Enter') salvar(); if (e.key === 'Escape') cancelar(); };

  // ---- variante CELL (tabela de estoque) ----
  if (variant === 'cell') {
    if (!editando) {
      return (
        <button type="button" className={`estoque-cell ${editado ? 'is-editado' : ''}`} title="Clique para editar o estoque"
          onClick={(e) => { e.stopPropagation(); setEditando(true); }}>
          <span className="tabular">{atual} {produto.unidade}</span>
          <IconPencil size={13} />
        </button>);
    }
    return (
      <span className="estoque-edit estoque-edit-cell" onClick={(e) => e.stopPropagation()}>
        <button type="button" className="step-btn" onClick={dec}><IconMinus size={13} /></button>
        <input ref={inputRef} type="number" className="estoque-input" value={val} min="0" onChange={onChange} onKeyDown={onKey} />
        <button type="button" className="step-btn" onClick={inc}><IconPlus size={13} /></button>
        <button type="button" className="confirm-btn ok" onClick={salvar} title="Salvar"><IconCheck size={14} /></button>
        <button type="button" className="confirm-btn no" onClick={cancelar} title="Cancelar"><IconX size={14} /></button>
      </span>);
  }

  // ---- variante PANEL (detalhe do produto) ----
  if (!editando) {
    return (
      <div>
        <div className="row-between" style={{ alignItems: 'flex-start' }}>
          <div className="label">Estoque atual</div>
          <button type="button" className="btn btn-tertiary btn-sm" style={{ padding: '2px 8px' }} onClick={() => setEditando(true)}>
            <IconPencil size={13} /> Editar
          </button>
        </div>
        <div style={{ fontSize: 32, fontWeight: 500, fontVariantNumeric: 'tabular-nums', lineHeight: 1.1 }}>
          {atual} <span style={{ fontSize: 16, color: 'var(--text-secondary)', fontWeight: 400 }}>{produto.unidade}</span>
        </div>
        {editado &&
          <div className="estoque-flag">
            ajustado manualmente
            <button type="button" className="estoque-undo" onClick={() => resetEstoque(produto.id)}>desfazer</button>
          </div>}
      </div>);
  }
  return (
    <div>
      <div className="label" style={{ marginBottom: 8 }}>Definir estoque atual</div>
      <div className="estoque-edit estoque-edit-panel">
        <button type="button" className="step-btn lg" onClick={dec}><IconMinus size={16} /></button>
        <input ref={inputRef} type="number" className="estoque-input lg" value={val} min="0" onChange={onChange} onKeyDown={onKey} />
        <span className="estoque-unit">{produto.unidade}</span>
        <button type="button" className="step-btn lg" onClick={inc}><IconPlus size={16} /></button>
      </div>
      <div className="row" style={{ gap: 8, marginTop: 12 }}>
        <button type="button" className="btn btn-primary btn-sm" onClick={salvar}><IconCheck size={14} /> Salvar</button>
        <button type="button" className="btn btn-secondary btn-sm" onClick={cancelar}>Cancelar</button>
      </div>
    </div>);
}

// Simple line chart in SVG
function LineChart({ hist = [], proj = [], width = 720, height = 220, formatY = (v) => v, yLabel = '' }) {
  const padL = 56,padR = 12,padT = 16,padB = 28;
  const all = [...hist, ...proj];
  if (all.length === 0) return null;
  const minY = 0;
  const maxY = Math.max(...all) * 1.1;
  const totalPts = hist.length + proj.length;
  const xStep = (width - padL - padR) / (totalPts - 1);
  const yScale = (v) => padT + (1 - (v - minY) / (maxY - minY)) * (height - padT - padB);

  const histPath = hist.map((v, i) => `${i === 0 ? 'M' : 'L'} ${padL + i * xStep} ${yScale(v)}`).join(' ');
  const projStart = hist.length - 1;
  const projPath = proj.map((v, i) => {
    const x = padL + (projStart + 1 + i) * xStep;
    return `${i === 0 ? `M ${padL + projStart * xStep} ${yScale(hist[hist.length - 1])} L` : 'L'} ${x} ${yScale(v)}`;
  }).join(' ');

  // Y ticks
  const ticks = 4;
  const yTicks = Array.from({ length: ticks + 1 }, (_, i) => minY + (maxY - minY) * (i / ticks));

  // X labels (show every Nth)
  const xLabelStep = Math.max(1, Math.floor(totalPts / 8));

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMidYMid meet">
      {/* Y grid + labels */}
      {yTicks.map((t, i) =>
      <g key={i}>
          <line x1={padL} x2={width - padR} y1={yScale(t)} y2={yScale(t)} stroke="#E5E5DF" strokeWidth="1" />
          <text x={padL - 8} y={yScale(t) + 4} fontSize="11" fill="#8B918D" textAnchor="end" fontFamily="Inter">{formatY(t)}</text>
        </g>
      )}
      {/* History line */}
      <path d={histPath} fill="none" stroke="#1F4A30" strokeWidth="1.8" />
      {/* Projection line (dashed) */}
      <path d={projPath} fill="none" stroke="#2D6644" strokeWidth="1.8" strokeDasharray="4 4" />
      {/* Divider for proj */}
      <line x1={padL + (hist.length - 1) * xStep} x2={padL + (hist.length - 1) * xStep} y1={padT} y2={height - padB} stroke="#CECEC5" strokeDasharray="2 3" />
      {/* X labels — show date indices */}
      {all.map((_, i) => i % xLabelStep === 0 &&
      <text key={i} x={padL + i * xStep} y={height - 10} fontSize="11" fill="#8B918D" textAnchor="middle" fontFamily="Inter">{xLabel(i, hist.length, totalPts)}</text>
      )}
      {/* Legend */}
      <g transform={`translate(${padL}, ${padT - 6})`}>
        <line x1="0" x2="14" y1="0" y2="0" stroke="#1F4A30" strokeWidth="1.8" />
        <text x="20" y="3" fontSize="11" fill="#5A615C" fontFamily="Inter">histórico</text>
        <line x1="80" x2="94" y1="0" y2="0" stroke="#2D6644" strokeWidth="1.8" strokeDasharray="4 4" />
        <text x="100" y="3" fontSize="11" fill="#5A615C" fontFamily="Inter">projeção</text>
      </g>
    </svg>);

}
function xLabel(i, histLen, total) {
  // Plot as semana N for aggregated, dia N for daily
  if (total <= 16) {
    // weeks
    const w = i - (histLen - 1);
    if (w === 0) return 'hoje';
    if (w < 0) return `s${w}`;
    return `s+${w}`;
  } else {
    const d = i - (histLen - 1);
    if (d === 0) return 'hoje';
    if (d % 15 !== 0 && d !== -(histLen - 1) && d !== total - histLen) return '';
    if (d < 0) return `${d}d`;
    return `+${d}d`;
  }
}

// Pareto chart
function ParetoChart({ data, width = 880, height = 280 }) {
  // data: [{nome, faturamento}], sorted desc
  const padL = 56,padR = 56,padT = 16,padB = 50;
  const maxV = Math.max(...data.map((d) => d.faturamento));
  const total = data.reduce((a, d) => a + d.faturamento, 0);
  const xStep = (width - padL - padR) / data.length;
  const yScaleL = (v) => padT + (1 - v / maxV) * (height - padT - padB);
  const yScaleR = (pct) => padT + (1 - pct) * (height - padT - padB);

  let acc = 0;
  const linePts = data.map((d, i) => {
    acc += d.faturamento;
    const pct = acc / total;
    return { x: padL + i * xStep + xStep / 2, y: yScaleR(pct), pct };
  });
  const linePath = linePts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMidYMid meet">
      {/* Y left grid */}
      {[0, 0.25, 0.5, 0.75, 1].map((t, i) =>
      <g key={i}>
          <line x1={padL} x2={width - padR} y1={yScaleL(maxV * t)} y2={yScaleL(maxV * t)} stroke="#E5E5DF" />
          <text x={padL - 8} y={yScaleL(maxV * t) + 4} fontSize="11" fill="#8B918D" textAnchor="end" fontFamily="Inter">{fmtBRLcompact(maxV * t)}</text>
          <text x={width - padR + 8} y={yScaleR(t) + 4} fontSize="11" fill="#8B918D" textAnchor="start" fontFamily="Inter">{Math.round(t * 100)}%</text>
        </g>
      )}
      {/* Bars */}
      {data.map((d, i) => {
        const barH = height - padT - padB - (yScaleL(d.faturamento) - padT);
        const fill = d.classe === 'A' ? '#1F4A30' : d.classe === 'B' ? '#A86C16' : '#8B918D';
        return <rect key={i} x={padL + i * xStep + 2} y={yScaleL(d.faturamento)} width={xStep - 4} height={barH} fill={fill} />;
      })}
      {/* Cumulative line */}
      <path d={linePath} fill="none" stroke="#2D6644" strokeWidth="2" />
      {linePts.map((p, i) => i % 3 === 0 && <circle key={i} cx={p.x} cy={p.y} r="2.5" fill="#2D6644" />)}
      {/* 80% reference */}
      <line x1={padL} x2={width - padR} y1={yScaleR(0.8)} y2={yScaleR(0.8)} stroke="#A8332E" strokeDasharray="3 3" />
      <text x={width - padR + 4} y={yScaleR(0.8) - 4} fontSize="10" fill="#A8332E" textAnchor="end" fontFamily="Inter">80%</text>
    </svg>);

}

// Bar chart (agrupadas) — para comparativo de modelos
function GroupedBars({ data, keys, colors, labels, width = 880, height = 280, formatY = (v) => v }) {
  const padL = 56,padR = 12,padT = 30,padB = 64;
  const maxV = Math.max(...data.flatMap((d) => keys.map((k) => d[k]))) * 1.1;
  const xStep = (width - padL - padR) / data.length;
  const barW = (xStep - 8) / keys.length;
  const yScale = (v) => padT + (1 - v / maxV) * (height - padT - padB);

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMidYMid meet">
      {[0, 0.25, 0.5, 0.75, 1].map((t, i) =>
      <g key={i}>
          <line x1={padL} x2={width - padR} y1={yScale(maxV * t)} y2={yScale(maxV * t)} stroke="#E5E5DF" />
          <text x={padL - 8} y={yScale(maxV * t) + 4} fontSize="11" fill="#8B918D" textAnchor="end" fontFamily="Inter">{formatY(maxV * t)}</text>
        </g>
      )}
      {data.map((d, i) =>
      <g key={i}>
          {keys.map((k, ki) => {
          const x = padL + i * xStep + 4 + ki * barW;
          const v = d[k];
          const y = yScale(v);
          const h = height - padT - padB - (y - padT);
          return <rect key={k} x={x} y={y} width={barW - 4} height={h} fill={colors[ki]} />;
        })}
          <text x={padL + i * xStep + xStep / 2} y={height - padB + 16} fontSize="10" fill="#5A615C" textAnchor="end" fontFamily="Inter" transform={`rotate(-30, ${padL + i * xStep + xStep / 2}, ${height - padB + 16})`}>{d.label}</text>
        </g>
      )}
      {/* Legend */}
      {keys.map((k, i) =>
      <g key={k} transform={`translate(${padL + i * 140}, ${10})`}>
          <rect width="12" height="12" fill={colors[i]} />
          <text x="18" y="10" fontSize="11" fill="#5A615C" fontFamily="Inter">{labels[i]}</text>
        </g>
      )}
    </svg>);

}

Object.assign(window, {
  Icon, IconHome, IconBox, IconBell, IconChart, IconProduct, IconShop, IconTrash, IconCog, IconBeaker,
  IconUpload, IconDownload, IconSearch, IconCheck, IconX, IconChev, IconChevDown, IconArrowLeft,
  IconAlert, IconInfo, IconFile, IconTrend, IconTrendDown, IconMinus, IconPlus, IconLock, IconMail, IconWhats, IconPencil,
  StatusPill, StatusDot, ClasseBadge, EstoqueField,
  LineChart, ParetoChart, GroupedBars
});