// Compõe uma trilha instrumental original (estilo lo-fi / chill) e salva como WAV.
// Cada "seed" gera uma música diferente (tom, andamento, acordes e ritmo).
// Como é gerada aqui mesmo, não tem direitos autorais de terceiros.
const fs = require('fs');

const SR = 44100;

function rng(seed) {
  let s = (seed * 2654435761) >>> 0 || 1;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

const midi = (n) => 440 * Math.pow(2, (n - 69) / 12);
// progressões (graus em semitons a partir da tônica) com acordes de 7ª
const PROGS = [
  [[0, 4, 7, 11], [9, 12, 16, 19], [5, 9, 12, 16], [7, 11, 14, 17]],   // I maj7 - vi7 - IV maj7 - V7
  [[2, 5, 9, 12], [7, 11, 14, 17], [0, 4, 7, 11], [9, 12, 16, 19]],    // ii7 - V7 - I maj7 - vi7
  [[9, 12, 16, 19], [5, 9, 12, 16], [0, 4, 7, 11], [7, 11, 14, 17]],   // vi7 - IV - I - V
  [[0, 4, 7, 11], [5, 9, 12, 16], [2, 5, 9, 12], [7, 11, 14, 17]],     // I - IV - ii - V
];

function compose(seed, seconds, outFile) {
  const r = rng(seed + 7);
  const bpm = 82 + Math.floor(r() * 18);           // 82–99 BPM
  const beat = 60 / bpm;
  const key = 57 + Math.floor(r() * 7);             // tônica entre A3 e D#4
  const prog = PROGS[Math.floor(r() * PROGS.length)];
  const swing = 0.08 + r() * 0.06;
  const N = Math.floor(SR * seconds);
  const L = new Float32Array(N), R = new Float32Array(N);
  const add = (buf, i, v) => { if (i >= 0 && i < N) buf[i] += v; };

  // acordes (pad suave, 1 acorde por compasso de 4 tempos)
  const bar = beat * 4;
  for (let b = 0; b * bar < seconds; b++) {
    const chord = prog[b % prog.length];
    const t0 = b * bar;
    chord.forEach((deg, k) => {
      const f = midi(key + deg - 12 + (k === 3 ? 0 : 0));
      const start = Math.floor(t0 * SR), len = Math.floor(bar * SR);
      for (let i = 0; i < len; i++) {
        const t = i / SR;
        const env = Math.min(1, t / 0.25) * Math.exp(-t * 0.6);
        const v = (Math.sin(2 * Math.PI * f * t) + 0.3 * Math.sin(2 * Math.PI * f * 2 * t + 0.4)) * env * 0.045;
        add(L, start + i, v * (k % 2 ? 0.8 : 1)); add(R, start + i, v * (k % 2 ? 1 : 0.8));
      }
    });
    // baixo: tônica do acorde nos tempos 1 e 3
    [0, 2].forEach((bt) => {
      const f = midi(key + chord[0] - 24);
      const start = Math.floor((t0 + bt * beat) * SR), len = Math.floor(beat * 1.8 * SR);
      for (let i = 0; i < len; i++) {
        const t = i / SR, env = Math.min(1, t / 0.01) * Math.exp(-t * 2.2);
        const v = Math.sin(2 * Math.PI * f * t) * env * 0.16;
        add(L, start + i, v); add(R, start + i, v);
      }
    });
    // melodia simples (notas do acorde, uma oitava acima) em colcheias aleatórias
    for (let e = 0; e < 8; e++) {
      if (r() < 0.45) continue;
      const deg = chord[Math.floor(r() * chord.length)] + 12;
      const f = midi(key + deg);
      const st = t0 + e * beat / 2 + (e % 2 ? swing * beat / 2 : 0);
      const start = Math.floor(st * SR), len = Math.floor(beat * 0.9 * SR);
      for (let i = 0; i < len; i++) {
        const t = i / SR, env = Math.min(1, t / 0.005) * Math.exp(-t * 5);
        const v = (Math.sin(2 * Math.PI * f * t) + 0.15 * Math.sin(2 * Math.PI * f * 3 * t)) * env * 0.05;
        add(L, start + i, v * 0.9); add(R, start + i, v * 1.1);
      }
    }
  }
  // bateria: bumbo (1 e 3), caixa (2 e 4), chimbal em colcheias
  for (let k = 0; k * beat < seconds; k++) {
    const st = k * beat;
    if (k % 4 === 0 || k % 4 === 2 || (k % 4 === 3 && r() < 0.3)) {
      const start = Math.floor(st * SR);
      for (let i = 0; i < SR * 0.35; i++) {
        const t = i / SR, f = 50 + 70 * Math.exp(-t * 30);
        const v = Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 9) * 0.35;
        add(L, start + i, v); add(R, start + i, v);
      }
    }
    if (k % 4 === 1 || k % 4 === 3) {
      const start = Math.floor(st * SR); let lp = 0;
      for (let i = 0; i < SR * 0.25; i++) {
        const t = i / SR; lp += 0.35 * ((r() * 2 - 1) - lp);
        const v = (lp * 0.8 + 0.2 * Math.sin(2 * Math.PI * 190 * t)) * Math.exp(-t * 16) * 0.16;
        add(L, start + i, v); add(R, start + i, v);
      }
    }
    for (let h = 0; h < 2; h++) {
      const start = Math.floor((st + h * beat / 2 + (h ? swing * beat / 2 : 0)) * SR);
      let prev = 0;
      for (let i = 0; i < SR * 0.05; i++) {
        const n = r() * 2 - 1, hp = n - prev; prev = n;
        const v = hp * Math.exp(-i / SR * 70) * (h ? 0.03 : 0.045);
        add(L, start + i, v * 0.8); add(R, start + i, v * 1.2);
      }
    }
  }
  // "lo-fi": filtro passa-baixa leve, chiado de vinil, fade in/out, normalização
  let lpL = 0, lpR = 0, peak = 0;
  for (let i = 0; i < N; i++) {
    lpL += 0.32 * (L[i] - lpL); lpR += 0.32 * (R[i] - lpR);
    const crackle = (r() < 0.0006 ? (r() * 2 - 1) * 0.08 : 0) + (r() * 2 - 1) * 0.004;
    const t = i / SR, fade = Math.min(1, t / 0.8, (seconds - t) / 1.2);
    L[i] = (lpL + crackle) * fade; R[i] = (lpR + crackle) * fade;
    peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
  }
  const gain = 0.7 / (peak || 1);
  const buf = Buffer.alloc(44 + N * 4);
  buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write('WAVE', 8); buf.write('fmt ', 12);
  buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22); buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(N * 4, 40);
  for (let i = 0; i < N; i++) {
    buf.writeInt16LE(Math.max(-32767, Math.min(32767, Math.round(L[i] * gain * 32767))), 44 + i * 4);
    buf.writeInt16LE(Math.max(-32767, Math.min(32767, Math.round(R[i] * gain * 32767))), 46 + i * 4);
  }
  fs.writeFileSync(outFile, buf);
  return { bpm, key };
}

module.exports = { compose };
