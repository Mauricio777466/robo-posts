"""Monta o Reel pronto (MP4 1080x1920) a partir do roteiro e da narração.

Visual MS Tech: fundo azul-escuro, logo no topo, um cartão por parte do
roteiro (gancho, problema, prejuízo, solução, resultado, chamada) e a
legenda dinâmica embaixo, com a palavra falada em amarelo.

Precisa de Pillow e imageio-ffmpeg (o ffmpeg vem dentro do pacote, nada
é instalado no disco C). Prints das telas por tema são opcionais:
dados\\roteiros_reels\\imagens\\<tema>\\*.png
"""

from __future__ import annotations

import random
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import PASTA_DADOS, Config
from .script_generator import Roteiro
from .temas import CARTAO_REEL

W, H, FPS = 1080, 1920, 30
ATRASO_VOZ = 0.3  # segundos de respiro antes da primeira palavra
SOBRA_FINAL = 1.6  # cartão da chamada parado no fim
TRANSICAO = 0.28  # entrada de cada cartão
PASTA_ASSETS = Path(__file__).resolve().parent / "assets"
PASTA_IMAGENS = PASTA_DADOS / "imagens"
PASTA_MUSICAS = PASTA_DADOS / "musicas"

FUNDO = (11, 18, 32)
CARTAO = (19, 29, 50)
BRANCO = (255, 255, 255)
CINZA = (148, 163, 184)
AMARELO = (250, 204, 21)
CIANO = (34, 211, 238)
ROTULOS = {
    "gancho": ("", CIANO),
    "dor": ("O PROBLEMA", (239, 68, 68)),
    "agravante": ("O PREJUÍZO", (249, 115, 22)),
    "solucao": ("A SOLUÇÃO", (37, 99, 235)),
    "beneficio": ("O RESULTADO", (16, 185, 129)),
    "cta": ("FALA COM A GENTE", AMARELO),
}

CX, CY, CW, CH = 60, 330, 960, 1000  # área do cartão


class ErroVideo(RuntimeError):
    pass


def _pil():
    try:
        from PIL import Image, ImageDraw, ImageFilter, ImageFont
    except ImportError as e:
        raise ErroVideo("Falta o pacote Pillow. Rode: python -m pip install pillow") from e
    return Image, ImageDraw, ImageFilter, ImageFont


def caminho_ffmpeg() -> str:
    try:
        import imageio_ffmpeg
    except ImportError as e:
        raise ErroVideo("Falta o pacote imageio-ffmpeg. Rode: python -m pip install imageio-ffmpeg") from e
    return imageio_ffmpeg.get_ffmpeg_exe()


class Fontes:
    def __init__(self):
        _, _, _, ImageFont = _pil()
        self._cache = {}
        self._ImageFont = ImageFont

    def __call__(self, tamanho: int, negrito: bool = True):
        chave = (tamanho, negrito)
        if chave not in self._cache:
            arq = PASTA_ASSETS / ("Poppins-Bold.ttf" if negrito else "Poppins-Regular.ttf")
            try:
                self._cache[chave] = self._ImageFont.truetype(str(arq), tamanho)
            except OSError:
                self._cache[chave] = self._ImageFont.load_default(tamanho)
        return self._cache[chave]


def quebrar(texto: str, fonte, largura: int) -> list[str]:
    linhas, atual = [], ""
    for p in texto.split():
        teste = f"{atual} {p}".strip()
        if fonte.getlength(teste) <= largura or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def texto_que_cabe(draw, texto: str, fontes: Fontes, largura: int, altura: int, maior: int, menor: int = 40):
    """Escolhe o maior tamanho de fonte em que o texto cabe na caixa."""
    for tam in range(maior, menor - 1, -4):
        f = fontes(tam)
        linhas = quebrar(texto, f, largura)
        alt = len(linhas) * int(tam * 1.18)
        if alt <= altura and max(f.getlength(ln) for ln in linhas) <= largura:
            return f, linhas, int(tam * 1.18)
    f = fontes(menor)
    return f, quebrar(texto, f, largura), int(menor * 1.18)


def marcar(d, x: int, y: int, tam: int, cor=BRANCO) -> None:
    """Desenha um ✓ com linhas (a fonte não tem esse símbolo)."""
    d.line([(x - tam * 0.45, y), (x - tam * 0.12, y + tam * 0.33), (x + tam * 0.45, y - tam * 0.33)],
           fill=cor, width=max(3, tam // 7), joint="curve")


def primeira_frase(texto: str) -> str:
    for sep in (". ", "? ", "! ", ": "):
        if sep in texto:
            return texto.split(sep)[0] + sep.strip()
    return texto


def imagem_do_tema(tema: str, rng: random.Random):
    pasta = PASTA_IMAGENS / tema
    if not pasta.is_dir():
        return None
    arquivos = sorted(p for p in pasta.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"))
    return rng.choice(arquivos) if arquivos else None


# ---------- desenho ----------

@dataclass
class Quadro:
    inicio: float
    imagem: object  # PIL.Image RGBA do cartão


def fundo_base(cfg: Config):
    Image, ImageDraw, ImageFilter, _ = _pil()
    img = Image.new("RGB", (W, H), FUNDO)
    brilho = Image.new("L", (W, H), 0)
    ImageDraw.Draw(brilho).ellipse((-200, 500, W + 200, 1500), fill=70)
    brilho = brilho.filter(ImageFilter.GaussianBlur(160))
    img.paste(Image.new("RGB", (W, H), (37, 99, 235)), (0, 0), brilho)
    logo = PASTA_ASSETS / "logo.png"
    if logo.exists():
        lg = Image.open(logo).convert("RGB")
        img.paste(lg, ((W - lg.width) // 2, 95))
    d = ImageDraw.Draw(img)
    f = Fontes()(30, negrito=False)
    rodape = f"{cfg.instagram}  ·  {' e '.join(cfg.cidades)}"
    d.text((W // 2, H - 70), rodape, font=f, fill=CINZA, anchor="mm")
    return img


def cartao(r: Roteiro, tipo: str, cfg: Config, fontes: Fontes, rng: random.Random, checks_visiveis: int = 6):
    Image, ImageDraw, _, _ = _pil()
    img = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rotulo, cor = ROTULOS[tipo]
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), radius=48, fill=CARTAO + (240,), outline=cor, width=4)
    y = 60
    if rotulo:
        f = fontes(34)
        larg = int(f.getlength(rotulo)) + 56
        d.rounded_rectangle((60, y, 60 + larg, y + 64), radius=32, fill=cor)
        d.text((60 + larg // 2, y + 32), rotulo, font=f, fill=FUNDO if cor == AMARELO else BRANCO, anchor="mm")
        y += 110
    caixa_l = CW - 120
    parte = r.parte(tipo)
    c = CARTAO_REEL[r.tema]

    if tipo == "gancho":
        f = fontes(34)
        d.text((60, y), r.titulo_tema.upper(), font=f, fill=CIANO)
        fonte, linhas, passo = texto_que_cabe(d, parte.texto, fontes, caixa_l, CH - y - 160, 100)
        y0 = y + (CH - y - len(linhas) * passo) // 2
        for i, ln in enumerate(linhas):
            d.text((60, y0 + i * passo), ln, font=fonte, fill=BRANCO if i < len(linhas) - 1 else AMARELO)
    elif tipo in ("dor", "agravante"):
        fonte, linhas, passo = texto_que_cabe(d, primeira_frase(parte.texto), fontes, caixa_l, CH - y - 80, 76)
        y0 = y + (CH - y - 40 - len(linhas) * passo) // 2
        for i, ln in enumerate(linhas):
            d.text((60, y0 + i * passo), ln, font=fonte, fill=BRANCO)
    elif tipo == "solucao":
        d.text((60, y), c["titulo"], font=fontes(78), fill=BRANCO)
        y += 120
        foto = imagem_do_tema(r.tema, rng)
        if foto:
            im = Image.open(foto).convert("RGB")
            im.thumbnail((caixa_l, CH - y - 60))
            mask = Image.new("L", im.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=24, fill=255)
            img.paste(im, (60 + (caixa_l - im.width) // 2, y + 20), mask)
        else:
            for i, item in enumerate(c["checks"][:4]):
                yy = y + 40 + i * 120
                d.ellipse((60, yy, 120, yy + 60), fill=cor)
                marcar(d, 90, yy + 30, 34)
                d.text((150, yy + 30), item, font=fontes(52), fill=BRANCO, anchor="lm")
    elif tipo == "beneficio":
        for i, item in enumerate(c["checks"]):
            yy = y + 20 + i * 125
            feito = i < checks_visiveis
            d.ellipse((60, yy, 124, yy + 64), fill=cor if feito else None, outline=cor, width=4)
            if feito:
                marcar(d, 92, yy + 32, 36)
            d.text((156, yy + 32), item, font=fontes(52), fill=BRANCO if feito else CINZA, anchor="lm")
    elif tipo == "cta":
        d.text((CW // 2, y + 40), "Manda", font=fontes(64), fill=BRANCO, anchor="mm")
        fonte, _, _ = texto_que_cabe(d, r.palavra_direct, fontes, caixa_l, 200, 170)
        d.text((CW // 2, y + 190), r.palavra_direct, font=fonte, fill=AMARELO, anchor="mm")
        d.text((CW // 2, y + 340), "no direct", font=fontes(64), fill=BRANCO, anchor="mm")
        d.line((160, y + 440, CW - 160, y + 440), fill=CINZA, width=2)
        d.text((CW // 2, y + 520), cfg.instagram, font=fontes(52), fill=CIANO, anchor="mm")
        d.text((CW // 2, y + 600), f"WhatsApp {cfg.whatsapp}", font=fontes(44, negrito=False), fill=BRANCO, anchor="mm")
        d.text((CW // 2, y + 680), "Teste grátis de 7 dias: link na bio", font=fontes(40, negrito=False),
               fill=CINZA, anchor="mm")
    return img


def desenhar_legenda(img, palavras: list[dict], atual: int, fontes: Fontes, pop: float):
    _, ImageDraw, _, _ = _pil()
    d = ImageDraw.Draw(img, "RGBA")
    f = fontes(int(76 * (0.94 + 0.06 * pop)))
    textos = [w["w"].upper() for w in palavras]
    espaco = f.getlength(" ")
    larguras = [f.getlength(t) for t in textos]
    # até 2 linhas, cada uma com no máximo 900 px
    linhas, linha, larg = [], [], 0.0
    for i, lw in enumerate(larguras):
        extra = lw + (espaco if linha else 0)
        if linha and larg + extra > 900:
            linhas.append((linha, larg))
            linha, larg = [], 0.0
            extra = lw
        linha.append(i)
        larg += extra
    linhas.append((linha, larg))
    alt_linha = 100
    topo = 1440
    caixa_w = max(lw for _, lw in linhas) + 70
    d.rounded_rectangle(((W - caixa_w) / 2, topo - 20, (W + caixa_w) / 2, topo + len(linhas) * alt_linha + 10),
                        radius=30, fill=(0, 0, 0, 200))
    for n, (idx, lw) in enumerate(linhas):
        x = (W - lw) / 2
        for i in idx:
            cor = AMARELO if i == atual else BRANCO
            d.text((x, topo + n * alt_linha), textos[i], font=f, fill=cor, stroke_width=3, stroke_fill=(0, 0, 0))
            x += larguras[i] + espaco


# ---------- tempos ----------

def blocos_legenda(palavras: list[dict], por_bloco: int = 3) -> list[list[dict]]:
    saida, atual = [], []
    for w in palavras:
        atual.append(w)
        texto = " ".join(x["w"] for x in atual)
        if len(atual) >= por_bloco or len(texto) > 22 or w["w"][-1:] in ".,!?;:":
            saida.append(atual)
            atual = []
    if atual:
        saida.append(atual)
    return saida


def inicio_das_partes(r: Roteiro, palavras: list[dict]) -> list[float]:
    """Hora em que cada parte começa, dividindo as palavras da voz na proporção do roteiro."""
    contagens = [len(p.texto.split()) for p in r.partes]
    total = sum(contagens)
    inicios, acumulado = [], 0
    for c in contagens:
        idx = min(len(palavras) - 1, round(acumulado * len(palavras) / total))
        inicios.append(0.0 if not inicios else palavras[idx]["s"])
        acumulado += c
    return inicios


# ---------- render ----------

def montar_video(r: Roteiro, palavras: list[dict], saida: Path, cfg: Config, audio: Path | None = None,
                 musica: Path | None = None, semente: int | None = None) -> Path:
    """Gera o MP4. palavras = [{w, s, e}] (da voz ou estimadas)."""
    if not palavras:
        raise ErroVideo("Sem palavras para a legenda.")
    Image, _, _, _ = _pil()
    ffmpeg = caminho_ffmpeg()
    rng = random.Random(semente if semente is not None else r.id)
    fontes = Fontes()
    palavras = [{**w, "s": w["s"] + ATRASO_VOZ, "e": w["e"] + ATRASO_VOZ} for w in palavras]
    duracao = palavras[-1]["e"] + SOBRA_FINAL
    total_quadros = int(duracao * FPS)

    base = fundo_base(cfg)
    inicios = inicio_das_partes(r, palavras)
    cartoes = {}
    for p in r.partes:
        if p.tipo == "beneficio":
            cartoes[p.tipo] = [cartao(r, p.tipo, cfg, fontes, rng, n) for n in range(7)]
        else:
            cartoes[p.tipo] = [cartao(r, p.tipo, cfg, fontes, rng)]
    grupos = blocos_legenda(palavras, cfg.palavras_por_bloco)

    if musica is None and PASTA_MUSICAS.is_dir():
        opcoes = sorted(p for p in PASTA_MUSICAS.iterdir() if p.suffix.lower() in (".mp3", ".m4a", ".wav", ".ogg"))
        musica = rng.choice(opcoes) if opcoes else None

    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    filtros, mapa_audio = [], []
    if audio:
        cmd += ["-i", str(audio)]
        atraso = int(ATRASO_VOZ * 1000)
        filtros.append(f"[1:a]adelay={atraso}|{atraso},volume=1.1[voz]")
    if musica:
        cmd += ["-stream_loop", "-1", "-i", str(musica)]
        n = 2 if audio else 1
        filtros.append(f"[{n}:a]volume={cfg.volume_musica},afade=t=in:d=0.6,"
                       f"afade=t=out:st={max(0, duracao - 1.2):.2f}:d=1.2[mus]")
    if audio and musica:
        filtros.append("[voz][mus]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
        mapa_audio = ["-map", "[a]"]
    elif audio:
        mapa_audio = ["-map", "[voz]"]
    elif musica:
        mapa_audio = ["-map", "[mus]"]
    if filtros:
        cmd += ["-filter_complex", ";".join(filtros), "-map", "0:v", *mapa_audio, "-c:a", "aac", "-b:a", "160k"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-t", f"{duracao:.2f}", "-movflags", "+faststart", str(saida)]

    saida.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    cache: dict[tuple, object] = {}
    try:
        for q in range(total_quadros):
            t = q / FPS
            n = max(i for i, s in enumerate(inicios) if s <= t or i == 0)
            parte = r.partes[n]
            dur_parte = (inicios[n + 1] if n + 1 < len(inicios) else duracao - SOBRA_FINAL) - inicios[n]
            estado = 0
            if parte.tipo == "beneficio":
                estado = min(6, int((t - inicios[n]) / max(0.1, dur_parte * 0.8) * 6) + 1)
            k = min(1.0, (t - inicios[n]) / TRANSICAO) if n else 1.0
            k = 1 - (1 - k) ** 3
            chave = (n, estado)
            if k >= 1 and chave in cache:
                quadro = cache[chave].copy()
            else:
                quadro = base.copy()
                img_cartao = cartoes[parte.tipo][estado]
                if k < 1:
                    alfa = img_cartao.getchannel("A").point(lambda v, k=k: int(v * k))
                    quadro.paste(img_cartao, (CX, CY + int(60 * (1 - k))), alfa)
                else:
                    quadro.paste(img_cartao, (CX, CY), img_cartao)
                    cache[chave] = quadro.copy()
            # barra de progresso
            if q:
                quadro.paste(CIANO, (0, 0, max(1, int(W * t / duracao)), 10))
            g = next((g for i, g in enumerate(grupos)
                      if g[0]["s"] <= t < (grupos[i + 1][0]["s"] if i + 1 < len(grupos) else g[-1]["e"] + 0.5)), None)
            if g:
                atual = next((i for i, w in enumerate(g) if w["s"] <= t < w["e"] + 0.05), -1)
                desenhar_legenda(quadro, g, atual, fontes, min(1.0, (t - g[0]["s"]) / 0.12))
            proc.stdin.write(quadro.tobytes())
        proc.stdin.close()
    except BrokenPipeError:
        pass
    erro = proc.stderr.read().decode("utf-8", "ignore")
    if proc.wait() != 0:
        raise ErroVideo(f"O ffmpeg falhou: {erro[-600:]}")
    return saida


def duracao_audio(arquivo: Path) -> float | None:
    """Lê a duração pelo próprio ffmpeg (sem ffprobe)."""
    try:
        out = subprocess.run([caminho_ffmpeg(), "-i", str(arquivo)], capture_output=True, text=True,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stderr
    except (OSError, ErroVideo):
        return None
    for linha in out.splitlines():
        if "Duration:" in linha:
            h, m, s = linha.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return None


def ajustar_estimativa(palavras: list[dict], duracao_real: float) -> list[dict]:
    """Quando a voz não dá o tempo das palavras, estica a estimativa até a duração real do áudio."""
    if not palavras or not duracao_real:
        return palavras
    fator = duracao_real / palavras[-1]["e"]
    return [{**w, "s": round(w["s"] * fator, 3), "e": round(w["e"] * fator, 3)} for w in palavras]
