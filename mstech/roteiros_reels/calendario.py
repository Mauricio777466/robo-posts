"""Calendário de Reels: um vídeo por dia, pronto para agendar (Metricool ou robô).

Uso:
  python -m roteiros_reels.calendario --inicio 2026-10-30 --dias 14 --voz edge
Gera <saida>/<data>-<tema>.mp4 e <saida>/calendario.json (data, hora, tema, arquivo, legenda).
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

from .config import carregar
from .exportar import exportar_roteiro
from .legenda import montar_legenda
from .script_generator import Historico, gerar_roteiro
from .app import produzir

# Rodízio com peso maior para reforma tributária e novidades (pedido do mauricio, 2026-10-29).
BASE = date(2026, 10, 29)  # 1º dia do rodízio
RODIZIO = ["caixa_rapido", "tributacao", "novidades", "filas", "tributacao", "fechamento", "novidades",
           "caixa_rapido", "tributacao", "seguranca", "estoque", "tributacao", "balanca", "novidades",
           "dono_longe"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="roteiros_reels.calendario")
    ap.add_argument("--inicio", default=date.today().isoformat(), help="AAAA-MM-DD")
    ap.add_argument("--dias", type=int, default=14)
    ap.add_argument("--hora", default="19:00", help="horário sugerido de postagem")
    ap.add_argument("--voz", choices=["edge", "elevenlabs", "windows"], default="edge")
    ap.add_argument("--saida", help="pasta de saída (padrão: dados\\roteiros_reels\\calendario)")
    ap.add_argument("--exigir-voz", action="store_true", help="para com erro se algum vídeo sair sem voz")
    ap.add_argument("--semente", type=int)
    args = ap.parse_args(argv)

    cfg = carregar()
    cfg.copiar_para_estudio = False
    saida = Path(args.saida) if args.saida else cfg.saida.parent / "calendario"
    saida.mkdir(parents=True, exist_ok=True)
    arq_cal = saida / "calendario.json"
    calendario = json.loads(arq_cal.read_text(encoding="utf-8")) if arq_cal.exists() else []
    feitos = {c["data"] for c in calendario}
    rng = random.Random(args.semente)
    historico = Historico()
    inicio = date.fromisoformat(args.inicio)

    for n in range(args.dias):
        dia = inicio + timedelta(days=n)
        if dia.isoformat() in feitos:
            print(f"{dia}: já existe, pulando")
            continue
        tema = RODIZIO[(dia - BASE).days % len(RODIZIO)]
        r = gerar_roteiro(tema, cfg, rng, historico)
        pasta = exportar_roteiro(r, saida / "roteiros" / f"{dia}-{tema}", cfg)
        produzir([r], [pasta], cfg, args.voz, video=True)
        video = pasta / f"Reel-{pasta.name}.mp4"
        tem_voz = any((pasta / f"narracao.{ext}").exists() for ext in ("mp3", "wav"))
        if args.exigir_voz and not tem_voz:
            print(f"ERRO: {dia} saiu sem voz.")
            return 1
        if not video.exists():
            print(f"ERRO: o vídeo de {dia} não foi gerado.")
            return 1
        final = saida / f"{dia}-{tema}.mp4"
        video.replace(final)
        calendario.append({
            "data": dia.isoformat(), "hora": args.hora, "tema": tema, "arquivo": final.name,
            "duracao_s": r.duracao, "com_voz": tem_voz, "gancho": r.parte("gancho").texto,
            "legenda": montar_legenda(r, cfg),
        })
        calendario.sort(key=lambda c: c["data"])
        arq_cal.write_text(json.dumps(calendario, ensure_ascii=False, indent=2), encoding="utf-8")
        historico.salvar()
        print(f"{dia}: {final.name} ({'com' if tem_voz else 'SEM'} voz)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
