// SVG icons (lucide-style, portados do protótipo)
// Cada função retorna uma string SVG para inserir via innerHTML

function svg(inner, size = 18) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`;
}

export const iconHome     = (s) => svg('<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>', s);
export const iconBox      = (s) => svg('<path d="M3 7.5 12 3l9 4.5v9L12 21l-9-4.5z"/><path d="M3 7.5 12 12l9-4.5"/><path d="M12 12v9"/>', s);
export const iconBell     = (s) => svg('<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>', s);
export const iconChart    = (s) => svg('<path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-6"/>', s);
export const iconProduct  = (s) => svg('<path d="M20 7L12 3 4 7v10l8 4 8-4z"/><path d="M9 5.2v6.3L4 9"/>', s);
export const iconUpload   = (s) => svg('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5"/><path d="M12 3v12"/>', s);
export const iconSearch   = (s) => svg('<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>', s);
export const iconCog      = (s) => svg('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>', s);
export const iconBeaker   = (s) => svg('<path d="M9 3h6v6l5 9a2 2 0 0 1-1.8 3H5.8A2 2 0 0 1 4 18l5-9z"/><path d="M7 14h10"/>', s);
export const iconLogout   = (s) => svg('<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>', s);
export const iconCheck    = (s) => svg('<path d="M5 12l5 5L20 7"/>', s);
export const iconX        = (s) => svg('<path d="M6 6l12 12M18 6 6 18"/>', s);
export const iconAlert    = (s) => svg('<circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>', s);
export const iconInfo     = (s) => svg('<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>', s);
export const iconFile     = (s) => svg('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>', s);
export const iconTrend    = (s) => svg('<path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/>', s);
export const iconMinus    = (s) => svg('<path d="M5 12h14"/>', s);
export const iconPlus     = (s) => svg('<path d="M12 5v14"/><path d="M5 12h14"/>', s);
export const iconPencil   = (s) => svg('<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/>', s);
export const iconArrowLeft = (s) => svg('<path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/>', s);
export const iconDownload = (s) => svg('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>', s);
export const iconCart     = (s) => svg('<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>', s);
export const iconWhatsapp = (s) => svg('<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>', s);
