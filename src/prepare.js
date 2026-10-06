// Passo 1: escolhe o próximo post da fila e gera a arte em docs/img/
const fs = require('fs');
const path = require('path');
const { render, PALETTES } = require('./render');

const ROOT = path.resolve(__dirname, '..');
const posts = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/posts.json'), 'utf8'));
const statePath = path.join(ROOT, 'content/state.json');
const state = fs.existsSync(statePath) ? JSON.parse(fs.readFileSync(statePath, 'utf8')) : { next: 0, published: [] };

(async () => {
  if (state.next >= posts.length) {
    console.error(`Os ${posts.length} posts do banco já foram publicados. Adicione novos posts em content/posts.json.`);
    process.exit(1);
  }
  const post = posts[state.next];
  const date = new Date().toISOString().slice(0, 10);
  const file = `docs/img/${date}-${post.id}.jpg`;
  fs.mkdirSync(path.join(ROOT, 'docs/img'), { recursive: true });
  await render(post, state.next % PALETTES.length, path.join(ROOT, file));

  const caption = `${post.caption}\n\nSiga @mauricio__oficialll para mais conteúdo de tecnologia. 💻\n\n${post.hashtags}`;
  if (caption.length > 2200) throw new Error(`Legenda do post "${post.id}" passou de 2.200 caracteres.`);
  fs.writeFileSync(path.join(ROOT, 'next.json'), JSON.stringify({ index: state.next, id: post.id, file, caption }, null, 2));
  console.log(`Post preparado: #${state.next + 1} "${post.id}" -> ${file}`);
})().catch((e) => { console.error(e.message); process.exit(1); });
