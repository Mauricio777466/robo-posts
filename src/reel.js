// Gera um Reel (MP4 1080x1920, 15s) no estilo "cartão com câmera em movimento":
// linha -> cartão cresce -> zoom no título -> balão com cursor -> texto digitado -> checklist -> zoom out -> giro 3D.
// Cada quadro é desenhado no navegador (Playwright) e o ffmpeg junta tudo em vídeo.
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');
const os = require('os');
const { compose } = require('./music');

const W = 1080, H = 1920, FPS = 30, DURATION = 15;
const HANDLE = '@mauricio__oficialll';
const font = (f) => 'data:font/ttf;base64,' + fs.readFileSync(path.resolve(__dirname, '..', 'fonts', f)).toString('base64');

function pageHtml(reel) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:P;src:url('${font('Poppins-Bold.ttf')}');font-weight:600 900}
@font-face{font-family:P;src:url('${font('Poppins-Regular.ttf')}');font-weight:100 500}
*{box-sizing:border-box;margin:0}
:root{--ac:${reel.color || '#111'}}
body{width:${W}px;height:${H}px;overflow:hidden;font-family:P,Arial,"Noto Color Emoji",sans-serif;
  background:radial-gradient(ellipse at 50% 40%,#fbfbfb 0%,#ececec 60%,#dedede 100%);color:#111}
#cam{position:absolute;left:0;top:0;width:${W}px;height:${H}px;transform-origin:0 0}
#persp{position:absolute;left:90px;top:300px;width:900px;height:1320px;perspective:2600px}
#card{position:absolute;inset:0;transform-origin:50% 50%}
#base{position:absolute;inset:0;background:linear-gradient(160deg,#2a2a2a,#0b0b0b 55%);border-radius:58px;box-shadow:0 60px 120px #0005}
#panel{position:absolute;left:16px;right:16px;top:16px;height:780px;background:#fff;border-radius:44px;overflow:hidden;padding:64px 60px}
.tag{font-size:26px;font-weight:600;color:#222;display:flex;gap:16px;align-items:center}
.handle{position:absolute;right:44px;top:44px;font-size:22px;font-weight:600;color:#555;background:#f1f1f1;border-radius:30px;padding:10px 20px}
#title{font-weight:800;font-size:92px;line-height:1.02;letter-spacing:-2px;margin-top:22px}
#title span{display:inline-block}
#sub{font-size:46px;color:#9a9a9a;margin-top:14px;font-weight:500}
#sub .k{color:#111;font-weight:700;position:relative;display:inline-block}
#sub .k i{position:absolute;left:0;bottom:-6px;height:7px;border-radius:6px;background:var(--ac);width:0}
#row{display:flex;gap:30px;margin-top:40px;align-items:flex-start}
#left{flex:1;min-width:0}
#typing{font-size:40px;font-weight:600;min-height:56px;white-space:nowrap}
#typing.mono{font-family:"DejaVu Sans Mono",monospace;font-size:34px;font-weight:700;color:#111}
#typing.mono .p{color:var(--ac)}
#typing .car{display:inline-block;width:3px;height:44px;background:#111;vertical-align:-8px;margin-left:3px}
#btn{display:inline-block;margin-top:22px;background:#111;color:#fff;font-weight:700;font-size:28px;padding:20px 34px;border-radius:40px}
#foot{margin-top:30px;font-size:24px;color:#888}
#popup{width:330px;background:linear-gradient(180deg,#f4f4f4,#e7e7e7);border-radius:30px;padding:26px 24px;box-shadow:0 20px 40px #0001}
#popup .q{display:flex;gap:16px;font-weight:700;font-size:30px;line-height:1.15}
#popup .q b{flex:none;width:44px;height:44px;border-radius:50%;background:#111;color:#fff;display:flex;align-items:center;justify-content:center;font-size:28px}
#pbtn{margin-top:20px;background:#fff;border-radius:22px;padding:16px 18px;font-size:24px;font-weight:600;white-space:nowrap}
#checks{position:absolute;left:70px;right:60px;top:860px;display:grid;grid-template-columns:1fr 1fr;gap:26px 30px}
#checks div{color:#e8e8e8;font-size:30px;display:flex;gap:14px;align-items:center}
#checks div em{flex:none;width:34px;height:34px;border-radius:50%;border:2px solid #bbb;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:20px}
#ig{position:absolute;left:70px;bottom:60px;color:#bbb;font-size:22px;font-weight:600;letter-spacing:1px}
#cursor{position:absolute;width:44px;height:44px;opacity:0}
</style></head><body>
<div id="cam"><div id="persp"><div id="card">
  <div id="base"></div>
  <div id="panel">
    <div class="tag" id="tag"><span style="color:var(--ac)">+</span><span id="tagt"></span><span style="color:var(--ac)">+</span></div>
    <div class="handle" id="handle">${HANDLE}</div>
    <div id="title"></div>
    <div id="sub"></div>
    <div id="row">
      <div id="left"><div id="typing"></div><div id="btn"></div><div id="foot"></div></div>
      <div id="popup"><div class="q"><b>!</b><span id="pq"></span></div><div id="pbtn"></div></div>
    </div>
  </div>
  <div id="checks"></div>
  <div id="ig">${HANDLE.toUpperCase()}</div>
  <svg id="cursor" viewBox="0 0 24 24"><path d="M4 2l16 11-7 1.5L9.5 21z" fill="#111" stroke="#fff" stroke-width="1.5"/></svg>
</div></div></div>
<script>
const R=${JSON.stringify(reel).replace(/<\//g, '<\\/')};
const $=id=>document.getElementById(id);
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
$('tagt').textContent=R.tag;
$('title').innerHTML=R.title.split(' ').map(w=>'<span>'+esc(w)+'&nbsp;</span>').join('');
$('sub').innerHTML=esc(R.sub).replace(/\\*(.+?)\\*/,'<span class="k">$1<i></i></span>');
if(R.code)$('typing').classList.add('mono');
$('btn').textContent=R.button; $('foot').textContent=R.foot||'';
$('pq').textContent=R.popupQ; $('pbtn').innerHTML=esc(R.popupBtn)+' &rarr;';
$('checks').innerHTML=R.checks.map(c=>'<div><em></em><span>'+esc(c)+'</span></div>').join('');

// posições (sem transformações) usadas pela câmera
const card=$('persp').getBoundingClientRect();
const ctr=el=>{const r=el.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];};
const P={card:[card.left+card.width/2,card.top+card.height/2],
  title:[card.left+card.width*0.42,($('tag').getBoundingClientRect().top+$('sub').getBoundingClientRect().bottom)/2],
  popup:ctr($('popup')),left:ctr($('left')),checks:ctr($('checks'))};
const pb=$('pbtn').getBoundingClientRect();
const btnPt=[pb.left+pb.width*0.7-card.left,pb.top+pb.height*0.6-card.top];
window.__overflow=$('pbtn').scrollWidth>$('pbtn').clientWidth+2||$('panel').scrollHeight>$('panel').clientHeight+2||$('typing').scrollWidth>$('left').clientWidth+2||$('checks').getBoundingClientRect().bottom>card.bottom-110;

const cl=x=>Math.max(0,Math.min(1,x)), ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2, out=t=>1-Math.pow(1-t,3);
const seg=(t,a,b)=>cl((t-a)/(b-a));
const CAM=[[0,'card',1],[1.6,'card',1],[2.4,'title',1.55],[4.4,'title',1.55],[5.1,'popup',1.75],[6.9,'popup',1.75],[7.6,'left',1.6],[8.8,'left',1.6],[9.5,'checks',1.35],[10.9,'checks',1.35],[11.6,'card',0.86],[15,'card',0.86]];
function cam(t){let i=0;while(i<CAM.length-2&&t>=CAM[i+1][0])i++;const [t0,a,s0]=CAM[i],[t1,b,s1]=CAM[i+1];
  const k=ease(cl((t-t0)/(t1-t0)));return [P[a][0]+(P[b][0]-P[a][0])*k,P[a][1]+(P[b][1]-P[a][1])*k,s0+(s1-s0)*k];}
const fade=(el,v,dy=24,blur=0)=>{el.style.opacity=v;el.style.transform='translateY('+(dy*(1-v))+'px)';el.style.filter=blur?'blur('+(blur*(1-v))+'px)':'none';};

window.setT=t=>{
  const [x,y,s]=cam(t); $('cam').style.transform='translate('+(${W}/2-x*s)+'px,'+(${H}/2-y*s)+'px) scale('+s+')';
  // linha -> cartão
  const g1=out(seg(t,0,0.8)), g2=ease(seg(t,0.8,1.6)), c=$('card'), h=24+(1320-24)*g2;
  c.style.clipPath='inset('+((1320-h)/2)+'px '+(450*(1-g1))+'px '+((1320-h)/2)+'px '+(450*(1-g1))+'px round 58px)';
  // giro 3D no final
  const r=ease(seg(t,11.7,13.2))*(1-ease(seg(t,13.9,14.8)));
  c.style.transform='rotateX('+(50*r)+'deg) rotateZ('+(-30*r)+'deg) translateY('+(-40*r)+'px)';
  $('base').style.boxShadow='0 '+(60+80*r)+'px '+(120+60*r)+'px #0005';
  // conteúdo
  fade($('tag'),out(seg(t,1.9,2.4))); fade($('handle'),out(seg(t,2.0,2.5)),0);
  [...$('title').children].forEach((w,i,a)=>fade(w,out(seg(t,2.2+i/a.length,2.6+i/a.length)),30,10));
  fade($('sub'),out(seg(t,3.3,3.8)),20,8); const u=document.querySelector('#sub i'); if(u)u.style.width=(100*out(seg(t,3.8,4.3)))+'%';
  fade($('popup'),out(seg(t,4.8,5.4)),30,14); fade($('pbtn'),out(seg(t,5.4,5.8)),16);
  const cu=$('cursor'), cin=out(seg(t,5.7,6.3)); cu.style.opacity=seg(t,5.6,5.8)*(1-seg(t,7.0,7.3));
  cu.style.left=(btnPt[0]+120*(1-cin))+'px'; cu.style.top=(btnPt[1]+160*(1-cin))+'px';
  const clk=seg(t,6.35,6.55); $('pbtn').style.transform='scale('+(1-0.06*Math.sin(Math.PI*clk))+')'; $('pbtn').style.background=clk>0&&clk<1?'#f0f0f0':'#fff';
  const n=Math.floor(R.typing.length*seg(t,7.4,8.4)), blink=t<8.4||Math.floor(t*2.5)%2===0;
  $('typing').innerHTML=esc(R.typing.slice(0,n))+(t>7.2&&t<10?'<span class="car" style="opacity:'+(blink?1:0)+'"></span>':'');
  fade($('btn'),out(seg(t,8.4,8.8)),16); fade($('foot'),out(seg(t,8.7,9.1)),12);
  [...$('checks').children].forEach((d,i)=>{fade(d,out(seg(t,9.4+i*0.22,9.7+i*0.22)),14,6);const e=d.firstChild,done=seg(t,9.6+i*0.22,9.8+i*0.22)>=1;
    e.textContent=done?'✓':'';e.style.borderColor=done?'var(--ac)':'#777';e.style.background=done?'var(--ac)':'transparent';e.style.color=done?'#fff':'#fff';});
  $('ig').style.opacity=seg(t,9.2,9.6);
};
</script></body></html>`;
}

// Trilha: se existir alguma música sua (livre de direitos) na pasta music/, usa uma delas;
// senão, compõe uma batida lo-fi original para este vídeo.
function pickMusic(index) {
  const dir = path.resolve(__dirname, '..', 'music');
  const own = fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => /\.(mp3|m4a|wav|aac|ogg)$/i.test(f)).sort() : [];
  if (own.length) return path.join(dir, own[index % own.length]);
  const f = path.join(os.tmpdir(), `trilha-${index}.wav`);
  compose(index * 31 + 5, DURATION, f);
  return f;
}

async function renderReel(reel, index, outFile, opts = {}) {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width: W, height: H } });
    await page.setContent(pageHtml(reel), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    if (await page.evaluate(() => window.__overflow)) throw new Error(`O texto do reel "${reel.id}" não coube no cartão. Encurte.`);
    if (opts.stills) { // só quadros de conferência
      for (const t of opts.stills) { await page.evaluate((x) => window.setT(x), t); await page.screenshot({ path: outFile.replace('.mp4', `-${t}.jpg`), type: 'jpeg', quality: 80 }); }
      return;
    }
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-stream_loop', '-1', '-i', pickMusic(index || 0),
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', String(FPS), '-b:v', '3500k', '-maxrate', '4500k', '-bufsize', '9M',
      '-af', `afade=t=in:d=0.5,afade=t=out:st=${DURATION - 1.2}:d=1.2,volume=0.9`, '-c:a', 'aac', '-b:a', '160k', '-t', String(DURATION), '-movflags', '+faststart', outFile]);
    let err = '';
    ff.stderr.on('data', (d) => (err += d));
    const done = new Promise((res, rej) => ff.on('close', (code) => (code === 0 ? res() : rej(new Error('ffmpeg: ' + err)))));
    for (let i = 0; i < FPS * DURATION; i++) {
      await page.evaluate((t) => window.setT(t), i / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 88 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    await done;
  } finally {
    await browser.close();
  }
}

module.exports = { renderReel };
