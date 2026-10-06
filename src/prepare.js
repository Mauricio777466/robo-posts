// Passo 1: escolhe o próximo conteúdo e gera o arquivo em docs/img/
// Segunda, quarta e sexta: Reel em vídeo com música (MP4). Terça e quinta: post com arte (JPG).
// Para forçar um Reel em outro dia, use a variável FORCE_REEL=true.
const fs = require('fs');
const path = require('path');
const { render, PALETTES } = require('./render');

const ROOT = path.resolve(__dirname, '..');
const read = (f) => JSON.parse(fs.readFileSync(path.join(ROOT, f), 'utf8'));
const statePath = path.join(ROOT, 'content/state.json');
const state = fs.existsSync(statePath) ? read('content/state.json') : {};
state.next = state.next || 0;
state.nextReel = state.nextReel || 0;

// dia da semana no horário de Brasília
const weekday = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Sao_Paulo', weekday: 'short' }).format(new Date());
const isReel = process.env.FORCE_REEL === 'true' || !['Tue', 'Thu'].includes(weekday);
const date = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date());
const SIGN = '\n\nSiga @mauricio__oficialll para mais conteúdo de tecnologia. 💻\n\n';

(async () => {
  fs.mkdirSync(path.join(ROOT, 'docs/img'), { recursive: true });
  let out;
  if (isReel) {
    const reels = read('content/reels.json');
    if (state.nextReel >= reels.length) throw new Error(`Os ${reels.length} Reels já foram publicados. Adicione novos em content/reels.json.`);
    const reel = reels[state.nextReel];
    const file = `docs/img/${date}-${reel.id}.mp4`;
    const { renderReel } = require('./reel');
    await renderReel(reel, state.nextReel, path.join(ROOT, file));
    out = { type: 'reel', index: state.nextReel, id: reel.id, file, caption: reel.caption + SIGN + reel.hashtags };
  } else {
    const posts = read('content/posts.json');
    if (state.next >= posts.length) throw new Error(`Os ${posts.length} posts do banco já foram publicados. Adicione novos posts em content/posts.json.`);
    const post = posts[state.next];
    const file = `docs/img/${date}-${post.id}.jpg`;
    await render(post, state.next % PALETTES.length, path.join(ROOT, file));
    out = { type: 'post', index: state.next, id: post.id, file, caption: post.caption + SIGN + post.hashtags };
  }
  if (out.caption.length > 2200) throw new Error(`Legenda de "${out.id}" passou de 2.200 caracteres.`);
  fs.writeFileSync(path.join(ROOT, 'next.json'), JSON.stringify(out, null, 2));
  console.log(`Preparado (${out.type}): "${out.id}" -> ${out.file}`);
})().catch((e) => { console.error(e.message); process.exit(1); });
