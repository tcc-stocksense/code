/**
 * Wrappers Chart.js para os 3 tipos de gráfico do StockSense.
 * Chart.js é carregado via CDN no HTML: <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
 */

/**
 * Gráfico de linha com histórico + projeção (tracejada).
 * @param {HTMLCanvasElement} ctx
 * @param {Object} dados
 * @param {string[]} dados.labels
 * @param {number[]} dados.historico
 * @param {number[]} [dados.projecao]
 * @param {string} [dados.labelHist='Histórico']
 * @param {string} [dados.labelProj='Projeção']
 * @returns {Chart}
 */
export function linha(ctx, dados) {
  const { labels, historico, projecao = [], labelHist = 'Histórico', labelProj = 'Projeção' } = dados;

  const datasets = [
    {
      label: labelHist,
      data: historico,
      borderColor: '#1F4A30',
      backgroundColor: 'rgba(31,74,48,0.08)',
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.3,
      fill: true,
    },
  ];

  if (projecao.length) {
    // Projeção começa com null para alinhar com o último ponto do histórico
    const projData = new Array(historico.length - 1).fill(null);
    projData.push(historico[historico.length - 1]); // ponto de conexão
    projData.push(...projecao);

    datasets.push({
      label: labelProj,
      data: projData,
      borderColor: '#2D6644',
      borderWidth: 2,
      borderDash: [6, 4],
      pointRadius: 0,
      tension: 0.3,
      fill: false,
    });
  }

  return new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top', labels: { usePointStyle: true, boxWidth: 8 } } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, grid: { color: '#E5E5DF' } },
      },
    },
  });
}

/**
 * Gráfico Pareto (barras + linha % acumulada em eixo Y secundário + referência 80%).
 * @param {HTMLCanvasElement} ctx
 * @param {Object} dados
 * @param {string[]} dados.labels
 * @param {number[]} dados.valores - faturamento por produto
 * @param {string[]} [dados.classes] - 'A','B','C' por produto (para colorir barras)
 * @returns {Chart}
 */
export function pareto(ctx, dados) {
  const { labels, valores, classes = [] } = dados;
  const total = valores.reduce((a, v) => a + v, 0);

  // Calcular % acumulada
  let acc = 0;
  const acumulado = valores.map(v => {
    acc += v;
    return (acc / total) * 100;
  });

  const corBarra = (i) => {
    const cls = classes[i] || 'C';
    if (cls === 'A') return '#1F4A30';
    if (cls === 'B') return '#A86C16';
    return '#8B918D';
  };

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Faturamento',
          data: valores,
          backgroundColor: valores.map((_, i) => corBarra(i)),
          yAxisID: 'y',
          order: 2,
        },
        {
          label: '% Acumulada',
          data: acumulado,
          type: 'line',
          borderColor: '#2D6644',
          borderWidth: 2,
          pointRadius: 2,
          pointBackgroundColor: '#2D6644',
          fill: false,
          yAxisID: 'y1',
          order: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { usePointStyle: true, boxWidth: 8 } },
        annotation: {
          annotations: {
            line80: {
              type: 'line',
              yMin: 80, yMax: 80,
              yScaleID: 'y1',
              borderColor: '#A8332E',
              borderDash: [4, 4],
              borderWidth: 1,
              label: { content: '80%', enabled: true, position: 'end' },
            },
          },
        },
      },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, position: 'left', grid: { color: '#E5E5DF' } },
        y1: { beginAtZero: true, max: 100, position: 'right', grid: { display: false },
          ticks: { callback: (v) => v + '%' } },
      },
    },
  });
}

/**
 * Barras agrupadas (ex: Holt-Winters vs Prophet).
 * @param {HTMLCanvasElement} ctx
 * @param {Object} dados
 * @param {string[]} dados.labels - nomes dos produtos
 * @param {Array<{label: string, data: number[], cor: string}>} dados.series
 * @returns {Chart}
 */
export function barras(ctx, dados) {
  const { labels, series } = dados;

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: series.map(s => ({
        label: s.label,
        data: s.data,
        backgroundColor: s.cor,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top', labels: { usePointStyle: true, boxWidth: 8 } } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, grid: { color: '#E5E5DF' } },
      },
    },
  });
}
