import json
import random
import re
import tempfile
import unittest
from pathlib import Path

from roteiros_reels.config import Config
from roteiros_reels.exportar import exportar_lote, gerar_srt, item_robo_posts, tempos_estimados
from roteiros_reels.legenda import montar_hashtags, montar_legenda
from roteiros_reels.script_generator import (CHAMADAS, MAX_SEGUNDOS_GANCHO, Historico, contar_palavras,
                                             estimar_segundos, gerar_roteiro)
from roteiros_reels.temas import CARTAO_REEL, FECHO_LONGO, LONGO, PERGUNTAS_ENGAJAMENTO, TEMAS
from roteiros_reels.voz import palavras_do_alinhamento

CFG = Config(copiar_para_estudio=False)


def todos_textos():
    for t in TEMAS.values():
        yield from t.ganchos + t.dores + t.solucoes
    for extra in LONGO.values():
        yield from extra["agravantes"] + extra["beneficios"]
    yield from CHAMADAS + PERGUNTAS_ENGAJAMENTO + (FECHO_LONGO,)


class TestConteudo(unittest.TestCase):
    def test_gancho_cabe_em_3_segundos(self):
        for t in TEMAS.values():
            for g in t.ganchos:
                with self.subTest(g=g):
                    self.assertLessEqual(contar_palavras(g.format(cidade="Macapá", sistema="Gestão Comercial")), 8)
                    self.assertLessEqual(estimar_segundos(g, CFG.palavras_por_segundo), MAX_SEGUNDOS_GANCHO)

    def test_nao_promete_o_que_nao_existe(self):
        proibido = re.compile(r"sis[ck]o[mn]|sys[ck]o[mn]|j[áa] emite|emite nota|nfc-?e|tef|integrad[ao] (à|a) maquininha", re.I)
        for texto in todos_textos():
            self.assertIsNone(proibido.search(texto), texto)

    def test_nota_fiscal_sempre_em_breve(self):
        for texto in todos_textos():
            if "nota fiscal" in texto.lower():
                self.assertIn("em breve", texto.lower(), texto)

    def test_todo_tema_tem_cartao_que_cabe(self):
        for k in TEMAS:
            c = CARTAO_REEL[k]
            self.assertEqual(len(c["checks"]), 6, k)
            self.assertLessEqual(len(c["titulo"]), 22, k)
            self.assertTrue(all(len(x) <= 23 for x in c["checks"]), k)


class TestGerador(unittest.TestCase):
    def test_formato_curto(self):
        r = gerar_roteiro("filas", Config(formato="curto"), random.Random(1))
        self.assertEqual([p.tipo for p in r.partes], ["gancho", "dor", "solucao", "cta"])
        self.assertNotIn("{", r.narracao)
        self.assertLess(r.duracao, 35)

    def test_formato_longo_entre_35_e_60_segundos(self):
        rng = random.Random(8)
        for k in TEMAS:
            for _ in range(5):
                r = gerar_roteiro(k, CFG, rng)
                self.assertEqual([p.tipo for p in r.partes],
                                 ["gancho", "dor", "agravante", "solucao", "beneficio", "cta"])
                self.assertGreaterEqual(r.duracao, 35, r.narracao)
                self.assertLessEqual(r.duracao, 60, r.narracao)

    def test_alinhamento_elevenlabs_vira_palavras(self):
        al = {"characters": list("Oi loja"), "character_start_times_seconds": [0, .1, .2, .3, .4, .5, .6],
              "character_end_times_seconds": [.1, .2, .3, .4, .5, .6, .7]}
        self.assertEqual(palavras_do_alinhamento(al), [{"w": "Oi", "s": 0, "e": .2}, {"w": "loja", "s": .3, "e": .7}])

    def test_historico_evita_repetir(self):
        h = Historico(None)
        rng = random.Random(3)
        combos = {tuple(gerar_roteiro("seguranca", CFG, rng, h).combinacao) for _ in range(20)}
        self.assertEqual(len(combos), 20)

    def test_mesma_semente_mesmo_roteiro(self):
        a = gerar_roteiro("estoque", CFG, random.Random(9)).narracao
        b = gerar_roteiro("estoque", CFG, random.Random(9)).narracao
        self.assertEqual(a, b)


class TestExportacao(unittest.TestCase):
    def test_legenda_hashtags(self):
        r = gerar_roteiro("tributacao", CFG, random.Random(2))
        tags = montar_hashtags(r, CFG)
        self.assertIn("#MSTechSolucoes", tags)
        self.assertIn("#Macapá", tags)
        self.assertLessEqual(len(tags), 30)
        leg = montar_legenda(r, CFG)
        self.assertLessEqual(len(leg), 2200)
        self.assertIn("direct", leg)

    def test_srt_valido(self):
        r = gerar_roteiro("balanca", CFG, random.Random(4))
        srt = gerar_srt(tempos_estimados(r), CFG)
        self.assertRegex(srt, r"^1\n00:00:00,000 --> 00:00:\d\d,\d{3}\n")
        for bloco in srt.strip().split("\n\n"):
            self.assertLessEqual(len(bloco.split("\n")[2].split()), CFG.palavras_por_bloco)

    def test_item_robo_posts_tem_campos_do_reels_json(self):
        r = gerar_roteiro("caixa_rapido", CFG, random.Random(5))
        item = item_robo_posts(r, CFG)
        campos = {"button", "caption", "checks", "code", "color", "foot", "hashtags", "id", "narration",
                  "popupBtn", "popupQ", "sub", "tag", "title", "typing"}
        self.assertEqual(set(item), campos)
        self.assertLessEqual(len(item["title"]), 22)

    def test_exporta_lote_completo(self):
        rng = random.Random(6)
        roteiros = [gerar_roteiro(k, CFG, rng) for k in TEMAS]
        with tempfile.TemporaryDirectory() as d:
            pastas = exportar_lote(roteiros, Path(d), CFG)
            esperado = {"roteiro.txt", "legenda_instagram.txt", "voz_elevenlabs.txt", "voz_elevenlabs.json",
                        "legendas.srt", "legendas_destaque.ass", "cenas_avatar.json", "robo_posts_reel.json",
                        "roteiro.json"}
            for p in pastas:
                self.assertEqual({f.name for f in p.iterdir()}, esperado)
            self.assertTrue((Path(d) / "lote_avatar.csv").exists())
            self.assertEqual(len(json.loads((Path(d) / "lote_robo_posts.json").read_text(encoding="utf-8"))), len(TEMAS))


if __name__ == "__main__":
    unittest.main()


class TestVideo(unittest.TestCase):
    def test_monta_mp4_curto(self):
        try:
            import imageio_ffmpeg  # noqa: F401
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow/imageio-ffmpeg não instalados")
        from roteiros_reels.video import duracao_audio, montar_video
        cfg = Config(formato="curto", copiar_para_estudio=False)
        r = gerar_roteiro("estoque", cfg, random.Random(1))
        with tempfile.TemporaryDirectory() as d:
            saida = montar_video(r, tempos_estimados(r), Path(d) / "t.mp4", cfg)
            self.assertGreater(saida.stat().st_size, 50_000)
            self.assertAlmostEqual(duracao_audio(saida), r.duracao + 1.9, delta=2.5)
