# Roteiros Reels - MS Tech Soluções

Gera roteiros curtos para Reels no formato **Gancho (até 3 s) + Dor + Solução MS Tech + Chamada para ação**,
com legenda pronta para o Instagram e arquivos para voz com IA e vídeo com avatar.
Também monta o **Reel pronto em MP4** (1080x1920, 40 a 55 s) com voz de IA e legenda dinâmica.
O roteiro usa só a biblioteca padrão; o vídeo usa `pillow`, `imageio-ffmpeg` e `edge-tts` (o .bat instala sozinho).

## Como usar
- Dê dois cliques em **Gerar Roteiros Reels.bat** e escolha o tema no menu.
- Ou, na pasta `D:\Free Claude Code\trabalho`:
  - `python -m roteiros_reels --listar`
  - `python -m roteiros_reels --tema filas -n 3`
  - `python -m roteiros_reels --todos --voz edge` (gera também `narracao.mp3` e acerta o tempo da legenda)
  - `python -m roteiros_reels --tema caixa_rapido --video` (roteiro + voz + `Reel-....mp4`)
  - `--formato curto` para vídeos de 20 a 30 s (o padrão é longo, 40 a 55 s)

## Voz
- Padrão: voz neural grátis da Microsoft (`voz_edge` no config). Masculina: `pt-BR-AntonioNeural`.
  Femininas: `pt-BR-FranciscaNeural`, `pt-BR-ThalitaMultilingualNeural`. Velocidade em `velocidade_voz`.
- Mais humana (paga): ElevenLabs. Preencha `elevenlabs.voice_id` no config e crie a variável de ambiente
  `ELEVENLABS_API_KEY`. Com as duas, o menu usa o ElevenLabs sozinho.
- Reserva: se a voz escolhida falhar, o app usa a voz do próprio Windows (menos natural) para o vídeo não sair mudo.
- Erro 403 na voz grátis = edge-tts desatualizado. O .bat atualiza sozinho a cada abertura.

## Vídeo
- Prints por tema (aparecem no cartão "A solução"): `dados\roteiros_reels\imagens\<tema>\*.png`.
- Música de fundo opcional: MP3 livres de direitos em `dados\roteiros_reels\musicas` (volume em `volume_musica`).
  Ou adicione a música pelo próprio Instagram na hora de postar.

Temas: filas, fechamento, seguranca, tributacao, caixa_rapido, dono_longe, balanca, estoque.

## Onde ficam os arquivos
`D:\Free Claude Code\trabalho\dados\roteiros_reels\saida\<data_hora>\<nº-tema>\`

| Arquivo | Para que serve |
|---|---|
| roteiro.txt | Roteiro com tempo de cada parte e o que mostrar na tela |
| legenda_instagram.txt | Legenda pronta: gancho, pergunta, chamada para o direct, WhatsApp e hashtags |
| voz_elevenlabs.txt | Texto com pausas para colar no ElevenLabs |
| voz_elevenlabs.json | Corpo pronto da API do ElevenLabs |
| legendas.srt | Legenda em blocos de 3 palavras (CapCut, HeyGen, Premiere) |
| legendas_destaque.ass | Legenda com a palavra falada em amarelo (ffmpeg/Aegisub) |
| cenas_avatar.json | Cenas com fala, emoção e enquadramento para vídeos com avatar |
| robo_posts_reel.json | Item no formato do `content/reels.json` do robo-posts |
| narracao.mp3 | Só com `--voz` ou `--video` |
| Reel-<pasta>.mp4 | Só com `--video` ou "S" no menu |

No lote: `lote_avatar.csv` (abre no Excel) e `lote_robo_posts.json`.
Uma cópia de cada roteiro.txt vai para `D:\Estudio MS Tech\Roteiros\Reels`.

## Configuração
`dados\roteiros_reels\config.json` (criado na 1ª vez): WhatsApp, hashtags, ritmo de fala,
pasta do estúdio e voz do ElevenLabs (`voice_id`). A chave do ElevenLabs vai na variável de
ambiente `ELEVENLABS_API_KEY`, nunca no arquivo.

O tempo da legenda sem `--voz` é uma estimativa (2,8 palavras por segundo). Com a voz, fica exato.

## Regras dos textos (temas.py)
Só fala do que já existe. Nota fiscal é sempre "em breve". Cartão no Caixa Rápido é na
maquininha da loja, com o atendente confirmando. Os testes conferem isso:
`python -m unittest discover -s roteiros_reels/tests -t .`
