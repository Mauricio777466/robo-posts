// Gera a arte (JPEG 1080x1350) de um post a partir do conteúdo em content/posts.json
const path = require('path');
const { chromium } = require('playwright');

const W = 1080, H = 1350;
const HANDLE = '@mauricio__oficialll';
const fs = require('fs');
const font = (f) => 'data:font/ttf;base64,' + fs.readFileSync(path.resolve(__dirname, '..', 'fonts', f)).toString('base64');
const FONT_BOLD = font('Poppins-Bold.ttf');
const FONT_REG = font('Poppins-Regular.ttf');

// Paletas: fundo (gradiente), destaque, texto escuro (para pílula/botão), cor secundária do brilho
const PALETTES = [
  { name: 'ciano',   bg: ['#061a33', '#02060f'], ac: '#22d3ee', dk: '#021a26', glow: '#3b5bff' },
  { name: 'roxo',    bg: ['#2a0a5e', '#0d0320'], ac: '#ff4fd8', dk: '#1a0638', glow: '#6b5bff' },
  { name: 'verde',   bg: ['#003b33', '#001210'], ac: '#2bff9a', dk: '#00281f', glow: '#0fa3a3' },
  { name: 'laranja', bg: ['#3d1300', '#110500'], ac: '#ff8a1f', dk: '#2a0d00', glow: '#ffc21f' },
  { name: 'vermelho',bg: ['#3a0610', '#0e0207'], ac: '#ff4d6d', dk: '#2a0510', glow: '#8b1e3f' },
  { name: 'amarelo', bg: ['#0b1a4a', '#040a1f'], ac: '#ffc928', dk: '#0b1a4a', glow: '#3b5bff' },
];

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
// *palavra* vira destaque na cor da paleta
const hl = (s) => esc(s).replace(/\*(.+?)\*/g, '<span class="ac">$1</span>');

function css(p) {
  return `
@font-face{font-family:P;src:url('${FONT_BOLD}');font-weight:600 900}
@font-face{font-family:P;src:url('${FONT_REG}');font-weight:100 500}
*{box-sizing:border-box;margin:0}
body{width:${W}px;height:${H}px;background:linear-gradient(160deg,${p.bg[0]} 0%,${p.bg[1]} 75%);font-family:P,Arial,"Noto Color Emoji",sans-serif;color:#fff;position:relative;overflow:hidden}
.grid{position:absolute;inset:0;background-image:linear-gradient(${p.ac}10 1px,transparent 1px),linear-gradient(90deg,${p.ac}10 1px,transparent 1px);background-size:54px 54px}
.blob{position:absolute;border-radius:50%;filter:blur(100px);opacity:.45}
.wrap{position:absolute;inset:60px 72px 56px 72px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center}
.tag{background:${p.ac};color:${p.dk};font-weight:800;font-size:24px;letter-spacing:2px;padding:12px 24px;border-radius:40px;text-transform:uppercase}
.brand{color:${p.ac};font-weight:700;font-size:22px;letter-spacing:2px}
h1{font-weight:800;font-size:76px;line-height:1.05;margin-top:56px;letter-spacing:-1px}
.ac{color:${p.ac}}
.sub{font-weight:400;font-size:32px;line-height:1.45;color:rgba(255,255,255,.86);margin-top:28px}
.body{flex:1;display:flex;flex-direction:column;justify-content:center;padding:30px 0}
.card{background:rgba(255,255,255,.06);border:1px solid ${p.ac}55;border-radius:22px;padding:26px 28px}
.li{display:flex;gap:18px;align-items:flex-start;font-size:35px;line-height:1.35;margin:13px 0}
.li i{font-style:normal;color:${p.ac};font-weight:800;min-width:40px}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.cards .e{font-size:56px;line-height:1}
.cards .t{font-weight:700;font-size:34px;margin:12px 0 6px}
.cards .d{font-size:27px;line-height:1.4;color:rgba(255,255,255,.8)}
.term{background:#00000088;border:1px solid ${p.ac}55;border-radius:22px;overflow:hidden}
.term .bar{display:flex;gap:10px;padding:16px 20px;background:#ffffff0d}
.term .bar b{width:14px;height:14px;border-radius:50%;display:block}
.term pre{font-family:"DejaVu Sans Mono",monospace;font-size:30px;line-height:1.6;padding:24px 28px;white-space:pre-wrap;color:#d8e6ff}
.term .c{color:${p.ac}}
.vs{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.vs h3{font-weight:800;font-size:36px;margin-bottom:10px}
.vs .li{font-size:30px;margin:10px 0}
.big{font-weight:800;font-size:96px;line-height:1.02;letter-spacing:-2px}
.foot{display:flex;justify-content:space-between;align-items:flex-end;gap:20px}
.foot .src{font-size:20px;color:rgba(255,255,255,.55);line-height:1.4;max-width:620px}
.foot .h{font-weight:700;font-size:26px}
`;
}

function bodyHtml(post, p) {
  const L = post.layout;
  if (L === 'list') {
    return `<div class="card">${post.items.map((t, i) => `<div class="li"><i>${post.numbered ? String(i + 1).padStart(2, '0') : '✓'}</i><div>${hl(t)}</div></div>`).join('')}</div>`;
  }
  if (L === 'cards') {
    return `<div class="cards">${post.items.map(([e, t, d]) => `<div class="card"><div class="e">${e}</div><div class="t">${hl(t)}</div><div class="d">${hl(d)}</div></div>`).join('')}</div>`;
  }
  if (L === 'terminal') {
    const lines = post.lines.map((l) => (l.startsWith('#') ? `<span class="c">${esc(l)}</span>` : esc(l))).join('\n');
    return `<div class="term"><div class="bar"><b style="background:#ff5f57"></b><b style="background:#febc2e"></b><b style="background:#28c840"></b></div><pre>${lines}</pre></div>`;
  }
  if (L === 'versus') {
    const col = (c, color) => `<div class="card" style="border-color:${color}"><h3 style="color:${color}">${esc(c.title)}</h3>${c.items.map((t) => `<div class="li"><i style="min-width:24px;color:${color}">•</i><div>${hl(t)}</div></div>`).join('')}</div>`;
    return `<div class="vs">${col(post.left, '#ffffffcc')}${col(post.right, p.ac)}</div>`;
  }
  if (L === 'big') {
    return `<div class="big">${hl(post.statement)}</div>`;
  }
  throw new Error('Layout desconhecido: ' + L);
}

function pageHtml(post, paletteIndex) {
  const p = PALETTES[paletteIndex % PALETTES.length];
  return `<!doctype html><html><head><meta charset="utf-8"><style>${css(p)}</style></head><body>
<div class="grid"></div>
<div class="blob" style="width:560px;height:560px;background:${p.ac};right:-220px;top:-140px"></div>
<div class="blob" style="width:460px;height:460px;background:${p.glow};left:-200px;bottom:-140px"></div>
<div class="wrap">
  <div class="top"><span class="tag">${esc(post.tag)}</span><span class="brand">TECH</span></div>
  ${post.layout === 'big' ? '' : `<h1>${hl(post.title)}</h1>`}
  ${post.subtitle && post.layout !== 'big' ? `<div class="sub">${hl(post.subtitle)}</div>` : ''}
  <div class="body">${bodyHtml(post, p)}${post.layout === 'big' && post.subtitle ? `<div class="sub" style="margin-top:40px">${hl(post.subtitle)}</div>` : ''}</div>
  <div class="foot"><div class="src">${post.source ? esc(post.source) : 'Salve e compartilhe com quem precisa ver isso.'}</div><div class="h">${HANDLE}</div></div>
</div></body></html>`;
}

async function render(post, paletteIndex, outFile) {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width: W, height: H } });
    await page.setContent(pageHtml(post, paletteIndex), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    // Garante que nada passou da área da arte
    const overflow = await page.evaluate(() => {
      const w = document.querySelector('.wrap');
      return w.scrollHeight > w.clientHeight + 2;
    });
    if (overflow) throw new Error(`O conteúdo do post "${post.id}" não coube na arte. Encurte o texto.`);
    await page.screenshot({ path: outFile, type: 'jpeg', quality: 90 });
  } finally {
    await browser.close();
  }
}

module.exports = { render, PALETTES };
