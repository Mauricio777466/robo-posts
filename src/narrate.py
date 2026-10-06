"""Gera a narração (MP3) de um texto com voz neural pt-BR e os tempos de cada palavra (JSON).

Uso: python3 src/narrate.py "<texto>" saida.mp3 saida.json [voz]
Voz padrão: pt-BR-AntonioNeural (masculina). Feminina: pt-BR-FranciscaNeural.
Também dá para trocar pela variável de ambiente TTS_VOICE.
"""
import asyncio
import json
import os
import sys

import edge_tts

TICKS = 10_000_000  # a API devolve tempos em unidades de 100 nanossegundos


async def main(text, mp3, js, voice):
    try:
        comm = edge_tts.Communicate(text, voice, rate="+6%", boundary="WordBoundary")
    except TypeError:  # versões antigas não têm o parâmetro boundary
        comm = edge_tts.Communicate(text, voice, rate="+6%")
    words = []
    with open(mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / TICKS
                words.append({"w": chunk["text"], "s": round(start, 3), "e": round(start + chunk["duration"] / TICKS, 3)})
    if not words:
        raise SystemExit("A voz não devolveu os tempos das palavras.")
    with open(js, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False)
    print(f"Narração: {len(words)} palavras, {words[-1]['e']:.1f}s, voz {voice}")


if __name__ == "__main__":
    voice = sys.argv[4] if len(sys.argv) > 4 else os.environ.get("TTS_VOICE") or "pt-BR-AntonioNeural"
    asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3], voice))
