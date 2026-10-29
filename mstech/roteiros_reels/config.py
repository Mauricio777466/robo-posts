"""Configuração: dados\\roteiros_reels\\config.json (criado na 1ª vez).

Tudo fica dentro de D:\\Free Claude Code\\trabalho\\dados\\roteiros_reels,
nunca no disco C.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

PASTA_APP = Path(__file__).resolve().parent
PASTA_TRABALHO = PASTA_APP.parent
PASTA_DADOS = PASTA_TRABALHO / "dados" / "roteiros_reels"
ARQUIVO_CONFIG = PASTA_DADOS / "config.json"


@dataclass
class ConfigElevenLabs:
    # A chave NÃO fica aqui: use a variável de ambiente ELEVENLABS_API_KEY.
    voice_id: str = ""
    model_id: str = "eleven_multilingual_v2"
    stability: float = 0.45
    similarity_boost: float = 0.8
    style: float = 0.35
    use_speaker_boost: bool = True


@dataclass
class Config:
    empresa: str = "MS Tech Soluções"
    instagram: str = "@ms_tech_solucoes_"
    whatsapp: str = "(96) 98115-7991"
    sistema: str = "Gestão Comercial"
    cidades: list[str] = field(default_factory=lambda: ["Macapá", "Santana"])
    hashtags_fixas: list[str] = field(default_factory=lambda: [
        "#Macapá", "#Santana", "#Amapá", "#AutomacaoComercial",
        "#MSTechSolucoes", "#ComercioLocal", "#GestaoComercial",
    ])
    max_hashtags: int = 15
    # "longo" = 40 a 60 s (gancho, dor, prejuízo, solução, resultado, chamada); "curto" = 20 a 30 s.
    formato: str = "longo"
    # Voz grátis (edge-tts). Outras: pt-BR-FranciscaNeural, pt-BR-ThalitaMultilingualNeural.
    voz_edge: str = "pt-BR-AntonioNeural"
    velocidade_voz: str = "+4%"
    # Música de fundo opcional: coloque MP3 livres de direitos em dados\roteiros_reels\musicas.
    volume_musica: float = 0.12
    # Ritmo de fala para estimar o tempo (palavras por segundo).
    palavras_por_segundo: float = 2.8
    # Legenda dinâmica: até N palavras por bloco, em maiúsculas.
    palavras_por_bloco: int = 3
    legenda_maiusculas: bool = True
    # Cópia do roteiro para o estúdio de vídeo (subpasta Reels).
    copiar_para_estudio: bool = True
    pasta_estudio_roteiros: str = r"D:\Estudio MS Tech\Roteiros\Reels"
    pasta_saida: str = ""  # vazio = dados\roteiros_reels\saida
    elevenlabs: ConfigElevenLabs = field(default_factory=ConfigElevenLabs)

    @property
    def saida(self) -> Path:
        return Path(self.pasta_saida) if self.pasta_saida else PASTA_DADOS / "saida"


def carregar(arquivo: Path = ARQUIVO_CONFIG) -> Config:
    """Lê o config.json; campos que faltam usam o padrão. Cria o arquivo se não existir."""
    padrao = Config()
    try:
        bruto = json.loads(arquivo.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        salvar(padrao, arquivo)
        return padrao
    except (OSError, ValueError) as erro:
        print(f"[aviso] config.json com problema ({erro}); usando o padrão.")
        return padrao
    campos = {k: v for k, v in bruto.items() if k in Config.__dataclass_fields__ and k != "elevenlabs"}
    cfg = Config(**campos)
    voz = bruto.get("elevenlabs") or {}
    cfg.elevenlabs = ConfigElevenLabs(**{k: v for k, v in voz.items() if k in ConfigElevenLabs.__dataclass_fields__})
    return cfg


def salvar(cfg: Config, arquivo: Path = ARQUIVO_CONFIG) -> None:
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(asdict(cfg), ensure_ascii=False, indent=2), encoding="utf-8")
