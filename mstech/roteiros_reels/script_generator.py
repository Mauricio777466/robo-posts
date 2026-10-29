"""Gerador de roteiros: Gancho forte (até 3 s) + Dor + Solução MS Tech + Chamada.

Sorteia uma combinação de frases do tema e evita repetir combinações já
usadas (histórico em dados\\roteiros_reels\\historico.json).
"""

from __future__ import annotations

import json
import random
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from .config import PASTA_DADOS, Config
from .temas import CHAMADAS, FECHO_LONGO, LONGO, TEMAS, Tema

ARQUIVO_HISTORICO = PASTA_DADOS / "historico.json"
MAX_SEGUNDOS_GANCHO = 3.0
PAUSA_ENTRE_PARTES = 0.4  # segundos de respiro entre uma parte e outra

ORDEM_CURTO = ("gancho", "dor", "solucao", "cta")  # 20 a 30 s
ORDEM_LONGO = ("gancho", "dor", "agravante", "solucao", "beneficio", "cta")  # 40 a 60 s
NOMES = {"gancho": "GANCHO", "dor": "DOR", "agravante": "O PREJUÍZO", "solucao": "SOLUÇÃO MS TECH",
         "beneficio": "O RESULTADO", "cta": "CHAMADA PARA AÇÃO"}
EMOCAO = {"gancho": "surpresa", "dor": "preocupação", "agravante": "seriedade", "solucao": "confiança",
          "beneficio": "alegria", "cta": "animação"}
VISUAL_DE = {"agravante": "dor", "beneficio": "solucao"}


@dataclass
class Parte:
    tipo: str
    texto: str
    segundos: float
    visual: str = ""
    emocao: str = ""


@dataclass
class Roteiro:
    id: str
    tema: str
    titulo_tema: str
    palavra_direct: str
    cidade: str
    partes: list[Parte]
    combinacao: list[int] = field(default_factory=list)
    criado_em: str = ""

    @property
    def narracao(self) -> str:
        return " ".join(p.texto for p in self.partes)

    @property
    def duracao(self) -> float:
        return round(sum(p.segundos for p in self.partes) + PAUSA_ENTRE_PARTES * (len(self.partes) - 1), 1)

    def parte(self, tipo: str) -> Parte | None:
        return next((p for p in self.partes if p.tipo == tipo), None)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["narracao"] = self.narracao
        d["duracao_estimada_s"] = self.duracao
        return d


def contar_palavras(texto: str) -> int:
    return len(re.findall(r"[\wÀ-ÿ@#]+", texto))


def estimar_segundos(texto: str, palavras_por_segundo: float) -> float:
    return round(max(0.8, contar_palavras(texto) / palavras_por_segundo), 1)


def slug(texto: str) -> str:
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def preencher(texto: str, cfg: Config, tema: Tema, cidade: str) -> str:
    return texto.format(
        cidade=cidade, empresa=cfg.empresa, sistema=cfg.sistema, whatsapp=cfg.whatsapp,
        instagram=cfg.instagram, palavra=tema.palavra_direct,
    )


class Historico:
    """Combinações já usadas por tema, para não repetir o mesmo vídeo."""

    def __init__(self, arquivo: Path | None = ARQUIVO_HISTORICO):
        self.arquivo = arquivo
        self.usadas: dict[str, list[str]] = {}
        if arquivo and arquivo.exists():
            try:
                self.usadas = json.loads(arquivo.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                self.usadas = {}

    def ja_usada(self, tema: str, chave: str) -> bool:
        return chave in self.usadas.get(tema, [])

    def marcar(self, tema: str, chave: str) -> None:
        self.usadas.setdefault(tema, []).append(chave)

    def salvar(self) -> None:
        if not self.arquivo:
            return
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        self.arquivo.write_text(json.dumps(self.usadas, ensure_ascii=False, indent=1), encoding="utf-8")


def gerar_roteiro(tema_chave: str, cfg: Config | None = None, rng: random.Random | None = None,
                  historico: Historico | None = None) -> Roteiro:
    """Gera um roteiro do tema. Levanta KeyError se o tema não existir."""
    cfg = cfg or Config()
    rng = rng or random.Random()
    tema = TEMAS[tema_chave]
    ordem = ORDEM_LONGO if cfg.formato == "longo" else ORDEM_CURTO
    fontes = {"gancho": tema.ganchos, "dor": tema.dores, "solucao": tema.solucoes, "cta": CHAMADAS,
              "agravante": LONGO[tema.chave]["agravantes"], "beneficio": LONGO[tema.chave]["beneficios"]}
    listas = tuple(fontes[t] for t in ordem)

    escolha: list[int] = []
    for _ in range(60):  # tenta achar uma combinação inédita
        escolha = [rng.randrange(len(lista)) for lista in listas]
        if not historico or not historico.ja_usada(tema.chave, cfg.formato + ":" + "-".join(map(str, escolha))):
            break
    if historico:
        historico.marcar(tema.chave, cfg.formato + ":" + "-".join(map(str, escolha)))

    cidade = rng.choice(cfg.cidades)
    partes = []
    for tipo, lista, i in zip(ordem, listas, escolha):
        texto = preencher(lista[i], cfg, tema, cidade)
        if tipo == "beneficio":  # no longo entram os dois resultados, o sorteado primeiro
            outros = [preencher(x, cfg, tema, cidade) for j, x in enumerate(lista) if j != i]
            texto = " ".join([texto] + outros)
        if tipo == "cta" and cfg.formato == "longo":
            texto += " " + preencher(FECHO_LONGO, cfg, tema, cidade)
        partes.append(Parte(tipo, texto, estimar_segundos(texto, cfg.palavras_por_segundo),
                            tema.visuais.get(VISUAL_DE.get(tipo, tipo), ""), EMOCAO[tipo]))

    agora = datetime.now()
    return Roteiro(
        id=f"{agora:%Y%m%d-%H%M%S}-{tema.chave}-{''.join(map(str, escolha))}",
        tema=tema.chave, titulo_tema=tema.titulo, palavra_direct=tema.palavra_direct,
        cidade=cidade, partes=partes, combinacao=escolha, criado_em=agora.isoformat(timespec="seconds"),
    )


def gerar_lote(temas: list[str], quantidade: int = 1, cfg: Config | None = None,
               semente: int | None = None, historico: Historico | None = None) -> list[Roteiro]:
    rng = random.Random(semente)
    return [gerar_roteiro(t, cfg, rng, historico) for t in temas for _ in range(quantidade)]


def roteiro_texto(r: Roteiro) -> str:
    """Roteiro legível para gravar (você, o avatar ou a voz de IA)."""
    linhas = [
        f"ROTEIRO REELS - {r.titulo_tema.upper()}",
        f"Duração estimada: {r.duracao:.0f} segundos | Palavra do direct: {r.palavra_direct}",
        "=" * 60, "",
    ]
    t = 0.0
    for p in r.partes:
        linhas += [f"[{t:04.1f}s - {t + p.segundos:04.1f}s] {NOMES[p.tipo]}  (tom: {p.emocao})",
                   f"FALA: {p.texto}"]
        if p.visual:
            linhas.append(f"TELA: {p.visual}")
        linhas.append("")
        t += p.segundos + PAUSA_ENTRE_PARTES
    linhas += ["-" * 60, "TEXTO CORRIDO (para colar na voz de IA):", r.narracao, ""]
    return "\n".join(linhas)
