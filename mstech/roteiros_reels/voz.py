"""Gera o áudio da narração (opcional).

- "edge": voz neural grátis da Microsoft (pacote edge-tts, a mesma do robo-posts).
  Devolve o tempo de cada palavra, então a legenda fica sincronizada de verdade.
- "elevenlabs": API paga do ElevenLabs. A chave vem da variável de ambiente
  ELEVENLABS_API_KEY (nunca salvar a chave em arquivo). Usa só a biblioteca padrão.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from .config import PASTA_DADOS, Config

VOZ_EDGE_PADRAO = "pt-BR-AntonioNeural"  # feminina: pt-BR-FranciscaNeural
TICKS = 10_000_000  # edge-tts devolve tempos em unidades de 100 ns


class ErroVoz(RuntimeError):
    pass


def narrar_edge(texto: str, mp3: Path, voz: str = VOZ_EDGE_PADRAO, velocidade: str = "+4%") -> list[dict]:
    try:
        import edge_tts  # dependência opcional
    except ImportError as e:
        raise ErroVoz("Falta o pacote edge-tts. Rode: python -m pip install edge-tts") from e

    async def _rodar() -> list[dict]:
        try:
            com = edge_tts.Communicate(texto, voz, rate=velocidade, boundary="WordBoundary")
        except TypeError:  # versões antigas
            com = edge_tts.Communicate(texto, voz, rate=velocidade)
        palavras = []
        with open(mp3, "wb") as f:
            async for parte in com.stream():
                if parte["type"] == "audio":
                    f.write(parte["data"])
                elif parte["type"] == "WordBoundary":
                    s = parte["offset"] / TICKS
                    palavras.append({"w": parte["text"], "s": round(s, 3), "e": round(s + parte["duration"] / TICKS, 3)})
        return palavras

    try:
        palavras = asyncio.run(_rodar())
    except Exception as e:  # rede caiu, serviço fora, versão velha do edge-tts etc.
        msg = str(e)
        if "403" in msg:
            raise ErroVoz("A voz grátis recusou o pedido (403). Normalmente é o edge-tts desatualizado: "
                          "rode  python -m pip install -U edge-tts  (o .bat já faz isso).") from e
        raise ErroVoz(f"Não deu para gerar a voz agora ({msg[:160]}). Confira a internet.") from e
    if not palavras:
        raise ErroVoz("A voz não devolveu os tempos das palavras.")
    return palavras


PS_WINDOWS = r"""
param([string]$txt, [string]$wav)
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$v = $s.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Culture.Name -eq 'pt-BR' } | Select-Object -First 1
if ($v) { $s.SelectVoice($v.VoiceInfo.Name) }
$s.Rate = 1
$s.SetOutputToWaveFile($wav)
$s.Speak([IO.File]::ReadAllText($txt, [Text.Encoding]::UTF8))
$s.Dispose()
"""


def narrar_windows(texto: str, wav: Path, timeout: int = 180) -> None:
    """Voz reserva: a voz do próprio Windows (sem internet). Menos natural, mas o vídeo não sai mudo."""
    if sys.platform != "win32":
        raise ErroVoz("A voz do Windows só funciona no Windows.")
    temp = PASTA_DADOS.parent / "temp"
    temp.mkdir(parents=True, exist_ok=True)
    ps1, txt = temp / "voz_windows.ps1", temp / "voz_windows.txt"
    ps1.write_text(PS_WINDOWS, encoding="utf-8-sig")
    txt.write_text(texto, encoding="utf-8")
    try:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1), str(txt), str(wav)],
                       check=True, capture_output=True, timeout=timeout,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.SubprocessError) as e:
        raise ErroVoz(f"A voz do Windows também falhou ({e}).") from e
    if not wav.exists() or wav.stat().st_size < 1000:
        raise ErroVoz("A voz do Windows não gerou o áudio.")


def palavras_do_alinhamento(alinhamento: dict) -> list[dict]:
    """Converte o alinhamento por letra do ElevenLabs em tempos por palavra."""
    letras = alinhamento.get("characters") or []
    inicios = alinhamento.get("character_start_times_seconds") or []
    fins = alinhamento.get("character_end_times_seconds") or []
    palavras, atual, s0, e0 = [], "", 0.0, 0.0
    for c, s, e in zip(letras, inicios, fins):
        if c.isspace():
            if atual:
                palavras.append({"w": atual, "s": round(s0, 3), "e": round(e0, 3)})
            atual = ""
            continue
        if not atual:
            s0 = s
        atual += c
        e0 = e
    if atual:
        palavras.append({"w": atual, "s": round(s0, 3), "e": round(e0, 3)})
    return palavras


def narrar_elevenlabs(texto: str, mp3: Path, cfg: Config, timeout: int = 120) -> list[dict]:
    """Voz mais humana (paga). Usa a rota with-timestamps para a legenda sair sincronizada."""
    chave = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    v = cfg.elevenlabs
    if not chave:
        raise ErroVoz("Defina a variável de ambiente ELEVENLABS_API_KEY com a sua chave do ElevenLabs.")
    if not v.voice_id:
        raise ErroVoz('Preencha "elevenlabs" > "voice_id" no config.json.')
    corpo = {
        "text": texto, "model_id": v.model_id,
        "voice_settings": {"stability": v.stability, "similarity_boost": v.similarity_boost,
                           "style": v.style, "use_speaker_boost": v.use_speaker_boost},
    }
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{v.voice_id}/with-timestamps?output_format=mp3_44100_128",
        data=json.dumps(corpo).encode("utf-8"), method="POST",
        headers={"xi-api-key": chave, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ErroVoz(f"ElevenLabs recusou o pedido (HTTP {e.code}): {e.read()[:300]!r}") from e
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise ErroVoz(f"Sem resposta válida do ElevenLabs ({e}).") from e
    if not dados.get("audio_base64"):
        raise ErroVoz("O ElevenLabs não devolveu o áudio.")
    mp3.write_bytes(base64.b64decode(dados["audio_base64"]))
    return palavras_do_alinhamento(dados.get("alignment") or {})
