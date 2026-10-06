// Passo 2: publica no Instagram pela API oficial da Meta (Instagram Graph API)
// Precisa dos segredos IG_USER_ID e IG_ACCESS_TOKEN configurados no GitHub.
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const GRAPH = 'https://graph.facebook.com/v21.0';
const { IG_USER_ID, IG_ACCESS_TOKEN, GITHUB_REPOSITORY, GITHUB_SHA_PUBLISHED, DRY_RUN } = process.env;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function call(method, url, params) {
  const body = new URLSearchParams({ ...params, access_token: IG_ACCESS_TOKEN });
  const res = method === 'GET' ? await fetch(`${url}?${body}`) : await fetch(url, { method, body });
  const json = await res.json();
  if (!res.ok || json.error) throw new Error(`Erro da API do Instagram: ${JSON.stringify(json.error || json)}`);
  return json;
}

(async () => {
  const next = JSON.parse(fs.readFileSync(path.join(ROOT, 'next.json'), 'utf8'));
  const imageUrl = `https://raw.githubusercontent.com/${GITHUB_REPOSITORY}/${GITHUB_SHA_PUBLISHED}/${next.file}`;
  console.log('Imagem:', imageUrl);

  if (DRY_RUN === 'true') {
    console.log('Modo teste: nada foi publicado.\n\nLegenda:\n' + next.caption);
    return;
  }
  if (!IG_USER_ID || !IG_ACCESS_TOKEN) throw new Error('Faltam os segredos IG_USER_ID e/ou IG_ACCESS_TOKEN no GitHub.');

  // Espera a imagem ficar disponível no link público
  for (let i = 0; i < 10; i++) {
    const r = await fetch(imageUrl, { method: 'HEAD' });
    if (r.ok) break;
    await sleep(6000);
  }

  // 1) cria o contêiner de mídia
  const { id: creationId } = await call('POST', `${GRAPH}/${IG_USER_ID}/media`, { image_url: imageUrl, caption: next.caption });
  // 2) espera o Instagram processar
  for (let i = 0; i < 20; i++) {
    const { status_code } = await call('GET', `${GRAPH}/${creationId}`, { fields: 'status_code' });
    if (status_code === 'FINISHED') break;
    if (status_code === 'ERROR' || status_code === 'EXPIRED') throw new Error('O Instagram não conseguiu processar a imagem: ' + status_code);
    await sleep(5000);
  }
  // 3) publica
  const { id: mediaId } = await call('POST', `${GRAPH}/${IG_USER_ID}/media_publish`, { creation_id: creationId });
  console.log(`Publicado! id=${mediaId}`);

  // 4) avança a fila
  const statePath = path.join(ROOT, 'content/state.json');
  const state = fs.existsSync(statePath) ? JSON.parse(fs.readFileSync(statePath, 'utf8')) : { next: 0, published: [] };
  state.next = next.index + 1;
  state.published.push({ id: next.id, mediaId, date: new Date().toISOString() });
  fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
})().catch((e) => { console.error(e.message); process.exit(1); });
