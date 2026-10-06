// Gera TODAS as artes na pasta preview/ para você conferir antes (não publica nada).
// Uso: node src/preview.js
const fs = require('fs');
const path = require('path');
const { render, PALETTES } = require('./render');

const ROOT = path.resolve(__dirname, '..');
const posts = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/posts.json'), 'utf8'));

(async () => {
  fs.mkdirSync(path.join(ROOT, 'preview'), { recursive: true });
  for (const [i, post] of posts.entries()) {
    const out = path.join(ROOT, 'preview', `${String(i + 1).padStart(2, '0')}-${post.id}.jpg`);
    await render(post, i % PALETTES.length, out);
    console.log('ok', out);
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
