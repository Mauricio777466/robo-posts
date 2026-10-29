"""Roteiros Reels - MS Tech Soluções.

Uso (na pasta D:\\Free Claude Code\\trabalho):
  python -m roteiros_reels                      menu simples
  python -m roteiros_reels --listar             mostra os temas
  python -m roteiros_reels --tema filas -n 3    3 roteiros do tema "filas"
  python -m roteiros_reels --todos              1 roteiro de cada tema
  python -m roteiros_reels --todos --voz edge   também gera o áudio (MP3) com voz grátis
  python -m roteiros_reels --tema filas --video  roteiro + voz + Reel pronto em MP4
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from . import __version__
from .config import ARQUIVO_CONFIG, Config, carregar
from .exportar import exportar_lote, gerar_ass, gerar_srt, tempos_estimados
from .script_generator import Historico, Roteiro, gerar_lote
from .temas import TEMAS
from .video import ErroVideo, ajustar_estimativa, duracao_audio, montar_video
from .voz import ErroVoz, narrar_edge, narrar_elevenlabs, narrar_windows


def copiar_para_estudio(roteiros: list[Roteiro], pastas: list[Path], cfg: Config) -> Path | None:
    """Põe uma cópia do roteiro.txt em D:\\Estudio MS Tech\\Roteiros\\Reels (se o estúdio existir)."""
    if not cfg.copiar_para_estudio or not cfg.pasta_estudio_roteiros or sys.platform != "win32":
        return None
    destino = Path(cfg.pasta_estudio_roteiros)
    if not destino.parent.exists():  # estúdio não instalado neste PC
        return None
    try:
        destino.mkdir(exist_ok=True)
        for r, p in zip(roteiros, pastas):
            shutil.copy2(p / "roteiro.txt", destino / f"Reels {r.criado_em[:10]} {p.name}.txt")
    except OSError as e:
        print(f"[aviso] Não copiei para o estúdio: {e}")
        return None
    return destino


def produzir(roteiros: list[Roteiro], pastas: list[Path], cfg: Config, motor: str | None, video: bool) -> None:
    """Gera a narração (opcional) e o vídeo pronto (opcional) de cada roteiro.

    Se a voz escolhida falhar, usa a voz do Windows como reserva para o vídeo não sair mudo.
    """
    for r, p in zip(roteiros, pastas):
        audio, palavras = None, None
        while motor:
            try:
                if motor == "edge":
                    audio = p / "narracao.mp3"
                    palavras = narrar_edge(r.narracao, audio, cfg.voz_edge, cfg.velocidade_voz)
                elif motor == "elevenlabs":
                    audio = p / "narracao.mp3"
                    palavras = narrar_elevenlabs(r.narracao, audio, cfg)
                else:
                    audio = p / "narracao.wav"
                    narrar_windows(r.narracao, audio)
                if not palavras:  # sem tempos: estica a estimativa até o tamanho do áudio
                    palavras = ajustar_estimativa(tempos_estimados(r), duracao_audio(audio) or 0)
                (p / "legendas.srt").write_text(gerar_srt(palavras, cfg), encoding="utf-8")
                (p / "legendas_destaque.ass").write_text(gerar_ass(palavras, cfg), encoding="utf-8")
                print(f"   voz pronta ({motor}): {audio.name}")
                break
            except ErroVoz as e:
                print(f"   [aviso] {e}")
                if audio:
                    audio.unlink(missing_ok=True)
                audio, palavras = None, None
                motor = "windows" if motor != "windows" and sys.platform == "win32" else None
                if motor:
                    print("   Usando a voz reserva do Windows.")
        if video:
            print(f"   montando o vídeo de {p.name} (leva 1 a 2 minutos)...")
            try:
                saida = montar_video(r, palavras or tempos_estimados(r), p / f"Reel-{p.name}.mp4", cfg,
                                     audio=audio)
                print(f"   OK vídeo pronto: {saida}")
            except ErroVideo as e:
                print(f"   [erro] {e}")
                return


def executar(temas: list[str], quantidade: int, cfg: Config, semente: int | None = None,
             voz: str | None = None, video: bool = False) -> Path:
    historico = Historico()
    roteiros = gerar_lote(temas, quantidade, cfg, semente, historico)
    pasta_lote = cfg.saida / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    pastas = exportar_lote(roteiros, pasta_lote, cfg)
    historico.salvar()
    for r, p in zip(roteiros, pastas):
        print(f" - {p.name}: {r.duracao:.0f}s | {r.parte('gancho').texto}")
    if voz or video:
        produzir(roteiros, pastas, cfg, voz, video)
    estudio = copiar_para_estudio(roteiros, pastas, cfg)
    print(f"\nPronto! {len(roteiros)} roteiro(s) em:\n  {pasta_lote}")
    if estudio:
        print(f"Cópia dos roteiros no estúdio:\n  {estudio}")
    return pasta_lote


def menu(cfg: Config) -> None:
    chaves = list(TEMAS)
    print(f"\n=== Roteiros Reels {__version__} - {cfg.empresa} ===\n")
    for i, k in enumerate(chaves, 1):
        print(f"  {i}. {TEMAS[k].titulo}")
    print(f"  {len(chaves) + 1}. Um de cada tema")
    opc = input("\nEscolha o número: ").strip()
    try:
        n = int(opc)
    except ValueError:
        print("Opção inválida.")
        return
    if n == len(chaves) + 1:
        temas = chaves
    elif 1 <= n <= len(chaves):
        temas = [chaves[n - 1]]
    else:
        print("Opção inválida.")
        return
    qtd = input("Quantos roteiros por tema? [1]: ").strip() or "1"
    video = input("Gerar o vídeo pronto com voz (precisa de internet)? S/n: ").strip().lower() != "n"
    motor = "elevenlabs" if (video and cfg.elevenlabs.voice_id and os.environ.get("ELEVENLABS_API_KEY")) else "edge"
    pasta = executar(temas, max(1, min(20, int(qtd) if qtd.isdigit() else 1)), cfg,
                     voz=motor if video else None, video=video)
    if sys.platform == "win32":
        os.startfile(pasta)  # abre a pasta no Explorer


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="roteiros_reels", description="Gera roteiros de Reels da MS Tech Soluções.")
    ap.add_argument("--listar", action="store_true", help="mostra os temas disponíveis")
    ap.add_argument("--tema", action="append", choices=list(TEMAS), help="tema (pode repetir)")
    ap.add_argument("--todos", action="store_true", help="um roteiro de cada tema")
    ap.add_argument("-n", "--quantidade", type=int, default=1, help="roteiros por tema (1 a 20)")
    ap.add_argument("--semente", type=int, help="mesma semente = mesmos roteiros (para testes)")
    ap.add_argument("--voz", choices=["edge", "elevenlabs", "windows"], help="também gera o áudio da narração")
    ap.add_argument("--video", action="store_true", help="monta o Reel pronto em MP4 (usa voz edge se --voz faltar)")
    ap.add_argument("--formato", choices=["longo", "curto"], help="longo = 40 a 60 s, curto = 20 a 30 s")
    args = ap.parse_args(argv)

    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    cfg = carregar()
    if args.formato:
        cfg.formato = args.formato
    if args.listar:
        for k, t in TEMAS.items():
            print(f"{k:14} {t.titulo}  (direct: {t.palavra_direct})")
        print(f"\nConfiguração: {ARQUIVO_CONFIG}")
        return 0
    temas = list(TEMAS) if args.todos else (args.tema or [])
    if not temas:
        menu(cfg)
        return 0
    voz = args.voz or ("edge" if args.video else None)
    executar(temas, max(1, min(20, args.quantidade)), cfg, args.semente, voz, args.video)
    return 0
