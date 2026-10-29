"""Legenda pronta para o Instagram (até 2.200 caracteres e 30 hashtags)."""

from __future__ import annotations

import random

from .config import Config
from .script_generator import Roteiro
from .temas import PERGUNTAS_ENGAJAMENTO, TEMAS

LIMITE_CARACTERES = 2200
LIMITE_HASHTAGS = 30


def montar_hashtags(r: Roteiro, cfg: Config) -> list[str]:
    vistas: set[str] = set()
    tags = []
    for tag in list(cfg.hashtags_fixas) + list(TEMAS[r.tema].hashtags):
        tag = "#" + tag.strip().lstrip("#")
        if tag.lower() not in vistas:
            vistas.add(tag.lower())
            tags.append(tag)
    return tags[: min(cfg.max_hashtags, LIMITE_HASHTAGS)]


def montar_legenda(r: Roteiro, cfg: Config, rng: random.Random | None = None) -> str:
    rng = rng or random.Random(r.id)
    gancho = r.parte("gancho").texto
    pergunta = rng.choice(PERGUNTAS_ENGAJAMENTO)
    partes = [
        f"⚠️ {gancho}",
        r.parte("dor").texto,
        f"✅ {r.parte('solucao').texto}",
        *([f"🚀 {r.parte('beneficio').texto}"] if r.parte("beneficio") else []),
        pergunta,
        f"📩 Manda {r.palavra_direct} no direct que a gente te mostra funcionando na sua loja.",
        f"📲 WhatsApp: {cfg.whatsapp}\n🆓 Teste grátis de 7 dias: link na bio",
        f"{cfg.empresa} | {r.cidade} e região",
        " ".join(montar_hashtags(r, cfg)),
    ]
    legenda = "\n\n".join(partes)
    if len(legenda) > LIMITE_CARACTERES:  # nunca acontece com os textos atuais, mas por garantia
        legenda = legenda[: LIMITE_CARACTERES - 1] + "…"
    return legenda
