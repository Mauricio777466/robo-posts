# Vídeos da MS Tech Soluções (@ms_tech_solucoes_)

Área separada do robô do @mauricio__oficialll. Não mexe em `content/` nem em `docs/img/`.

- `roteiros_reels/`: o mesmo app de roteiros do PC (D:\Free Claude Code\trabalho\roteiros_reels).
- `.github/workflows/mstech-videos.yml`: a cada push nesta branch (pasta `mstech/`), gera os Reels
  do calendário com voz neural grátis (edge-tts) e salva em `docs/mstech/` com o `calendario.json`.
- Os vídeos ficam em link público (raw.githubusercontent.com) para o Metricool baixar e agendar.

Rodar à mão: aba Actions → "Vídeos MS Tech" → Run workflow (informe início e dias).
