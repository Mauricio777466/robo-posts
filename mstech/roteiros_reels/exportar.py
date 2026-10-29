"""Exporta cada roteiro em arquivos prontos para voz com IA e vídeo com avatar.

Por roteiro (uma pasta):
  roteiro.txt               roteiro com tempos e o que mostrar na tela
  legenda_instagram.txt     legenda pronta para colar no post
  voz_elevenlabs.txt        texto com pausas <break> para o ElevenLabs
  voz_elevenlabs.json       corpo pronto da chamada da API do ElevenLabs
  legendas.srt              legenda dinâmica (blocos curtos) para CapCut/HeyGen
  legendas_destaque.ass     legenda com palavra em destaque (karaokê), para ffmpeg/Aegisub
  cenas_avatar.json         cenas para criadores de vídeo com avatar falando
  robo_posts_reel.json      item no formato do content/reels.json do robo-posts
Por lote: lote_avatar.csv e lote_robo_posts.json.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from .config import Config
from .legenda import montar_hashtags, montar_legenda
from .script_generator import NOMES, PAUSA_ENTRE_PARTES, Roteiro, roteiro_texto
from .temas import CARTAO_REEL

PAUSA_SSML = '<break time="0.4s" />'


# ---------- tempos das palavras ----------

def tempos_estimados(r: Roteiro) -> list[dict]:
    """Tempo de cada palavra pela estimativa de ritmo (w = palavra, s = início, e = fim)."""
    palavras, t = [], 0.0
    for p in r.partes:
        ws = p.texto.split()
        passo = p.segundos / max(1, len(ws))
        for w in ws:
            palavras.append({"w": w, "s": round(t, 3), "e": round(t + passo, 3)})
            t += passo
        t += PAUSA_ENTRE_PARTES
    return palavras


def blocos(palavras: list[dict], por_bloco: int) -> list[list[dict]]:
    """Agrupa em blocos curtos, quebrando também na pontuação (estilo legenda viral)."""
    saida, atual = [], []
    for w in palavras:
        atual.append(w)
        if len(atual) >= por_bloco or re.search(r"[.,!?;:]$", w["w"]):
            saida.append(atual)
            atual = []
    if atual:
        saida.append(atual)
    return saida


def _ts_srt(s: float) -> str:
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def _ts_ass(s: float) -> str:
    cs = int(round(s * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def _limpa(w: str, maiusculas: bool) -> str:
    return w.upper() if maiusculas else w


def gerar_srt(palavras: list[dict], cfg: Config) -> str:
    linhas = []
    for i, b in enumerate(blocos(palavras, cfg.palavras_por_bloco), 1):
        texto = " ".join(_limpa(w["w"], cfg.legenda_maiusculas) for w in b)
        linhas += [str(i), f"{_ts_srt(b[0]['s'])} --> {_ts_srt(b[-1]['e'])}", texto, ""]
    return "\n".join(linhas)


def gerar_ass(palavras: list[dict], cfg: Config) -> str:
    """Legenda 1080x1920, texto branco com a palavra falada em amarelo (#FACC15)."""
    cab = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        # Primary = destaque (amarelo), Secondary = antes de falar (branco). Cores em &HAABBGGRR.
        "Style: Viral,Arial Black,88,&H0015CCFA,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,6,3,"
        "2,60,60,520,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    eventos = []
    for b in blocos(palavras, cfg.palavras_por_bloco):
        texto = " ".join(
            f"{{\\k{max(1, int(round((w['e'] - w['s']) * 100)))}}}{_limpa(w['w'], cfg.legenda_maiusculas)}" for w in b
        )
        eventos.append(f"Dialogue: 0,{_ts_ass(b[0]['s'])},{_ts_ass(b[-1]['e'] + 0.05)},Viral,,0,0,0,,{texto}")
    return cab + "\n".join(eventos) + "\n"


# ---------- voz e avatar ----------

def texto_elevenlabs(r: Roteiro) -> str:
    return f" {PAUSA_SSML} ".join(p.texto for p in r.partes)


def corpo_elevenlabs(r: Roteiro, cfg: Config) -> dict:
    v = cfg.elevenlabs
    return {
        "text": texto_elevenlabs(r),
        "model_id": v.model_id,
        "voice_settings": {"stability": v.stability, "similarity_boost": v.similarity_boost,
                           "style": v.style, "use_speaker_boost": v.use_speaker_boost},
        "_voice_id": v.voice_id or "PREENCHA_NO_CONFIG",
        "_endpoint": "POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    }


def cenas_avatar(r: Roteiro, cfg: Config) -> dict:
    cenas, t = [], 0.0
    for i, p in enumerate(r.partes, 1):
        cenas.append({
            "cena": i, "parte": NOMES[p.tipo], "inicio_s": round(t, 1), "duracao_s": p.segundos,
            "fala": p.texto, "emocao": p.emocao, "enquadramento": "close" if p.tipo in ("gancho", "cta") else "médio",
            "texto_na_tela": p.texto.split(".")[0][:60], "fundo_sugerido": p.visual,
        })
        t += p.segundos + PAUSA_ENTRE_PARTES
    return {
        "titulo": f"{r.titulo_tema} - {r.cidade}", "formato": "9:16 (1080x1920)",
        "duracao_estimada_s": r.duracao, "idioma": "pt-BR", "marca": cfg.empresa, "instagram": cfg.instagram,
        "estilo_legenda": "blocos de até 3 palavras, maiúsculas, palavra falada em amarelo #FACC15",
        "narracao_completa": r.narracao, "cenas": cenas,
    }


def item_robo_posts(r: Roteiro, cfg: Config) -> dict:
    """Mesmo formato dos itens de content/reels.json do robo-posts."""
    c = CARTAO_REEL[r.tema]
    return {
        "id": r.id, "tag": "MS Tech Soluções", "color": c["cor"], "code": False,
        "title": c["titulo"], "sub": c["sub"], "typing": c["typing"],
        "button": f"Direct: {r.palavra_direct}", "foot": f"{cfg.empresa} · {r.cidade}",
        "popupQ": "Isso acontece na sua loja?", "popupBtn": "Comenta aí",
        "checks": c["checks"],
        "caption": montar_legenda(r, cfg).rsplit("\n\n", 1)[0],
        "hashtags": " ".join(montar_hashtags(r, cfg)),
        "narration": r.narracao,
    }


# ---------- gravação ----------

def exportar_roteiro(r: Roteiro, pasta: Path, cfg: Config, palavras: list[dict] | None = None) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    palavras = palavras or tempos_estimados(r)
    arquivos = {
        "roteiro.txt": roteiro_texto(r),
        "legenda_instagram.txt": montar_legenda(r, cfg),
        "voz_elevenlabs.txt": texto_elevenlabs(r),
        "voz_elevenlabs.json": json.dumps(corpo_elevenlabs(r, cfg), ensure_ascii=False, indent=2),
        "legendas.srt": gerar_srt(palavras, cfg),
        "legendas_destaque.ass": gerar_ass(palavras, cfg),
        "cenas_avatar.json": json.dumps(cenas_avatar(r, cfg), ensure_ascii=False, indent=2),
        "robo_posts_reel.json": json.dumps(item_robo_posts(r, cfg), ensure_ascii=False, indent=2),
        "roteiro.json": json.dumps(r.to_dict(), ensure_ascii=False, indent=2),
    }
    for nome, conteudo in arquivos.items():
        (pasta / nome).write_text(conteudo, encoding="utf-8")
    return pasta


def exportar_lote(roteiros: list[Roteiro], pasta_lote: Path, cfg: Config) -> list[Path]:
    pasta_lote.mkdir(parents=True, exist_ok=True)
    pastas = [exportar_roteiro(r, pasta_lote / f"{i:02d}-{r.tema}", cfg) for i, r in enumerate(roteiros, 1)]
    # utf-8-sig para o Excel abrir com acentos
    with open(pasta_lote / "lote_avatar.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["pasta", "tema", "cidade", "duracao_s", "titulo", "roteiro", "legenda_arquivo"])
        for p, r in zip(pastas, roteiros):
            w.writerow([p.name, r.tema, r.cidade, r.duracao, r.parte("gancho").texto, r.narracao,
                        str(p / "legenda_instagram.txt")])
    (pasta_lote / "lote_robo_posts.json").write_text(
        json.dumps([item_robo_posts(r, cfg) for r in roteiros], ensure_ascii=False, indent=2), encoding="utf-8")
    return pastas
