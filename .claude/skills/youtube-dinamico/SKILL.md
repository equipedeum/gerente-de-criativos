---
name: youtube-dinamico
description: "YouTube dinâmico (menu 11) — edição de vídeo de YouTube 16:9 com a pessoa falando: limpeza de tropeço/repetição/recomeço, respiros encurtados, plano aberto↔médio↔fechado trocando SÓ no começo de frase, painel de papel com o texto da marca deslizando ao lado da pessoa, selo de impacto, cartões de quebra de capítulo, cartão final com a marca, efeitos sonoros discretos e a cor da pessoa intacta. Cores, fontes e logo vêm do projeto.json. Usar quando o usuário escolher o item 11 do menu, pedir \"YouTube dinâmico\", \"edita pro YouTube\", \"vídeo longo horizontal\" ou mandar uma gravação 16:9 de fala pra virar vídeo de canal."
---

# YouTube dinâmico (menu 11)

Formato único: **YT 1920x1080** (vídeo de canal; não tem RL/IN/GL — se pedirem os verticais, oferecer os estilos 1–10
com o mesmo bruto). A pessoa fala pra câmera; a edição deixa o ritmo de vídeo de canal sem mudar o que ela disse.

## Arquitetura (o que deu certo e por quê)

1. `work/yt/montar.py <id>` — lê o cfg (`work/yt/cfg/<id>.py`), corta, monta o áudio, escolhe os planos e grava
   `remotion/public-yt/<id>/edl.json` + `mix.wav` + fontes/logo da marca. **Sem render.**
2. Remotion (`remotion/src/yt-dinamico/`, entrada própria `index.tsx`) desenha **só os grafismos**, em PNG transparente.
3. `work/yt/camera.py` faz a "câmera" (planos, punch-in, deslize junto com o painel) **direto da gravação em YUV**, sem
   passar por RGB, e o ffmpeg sobrepõe os PNG (matriz bt709) + `mix.wav` → MP4 bt709.

Por quê: o Remotion lendo 4K (OffthreadVideo) levou 5,5 min pra 5 s de vídeo e o MP4 saía com a cor em BT.601 marcada
como bt709 (rosto mais vermelho). Separando, a cor da pessoa sai idêntica à da gravação e o render é rápido.

## Passo a passo

1. **Preparo** (gravação horizontal; o ideal é 4K, que aguenta os punch-ins):
   `./py work/pipeline/preparar.py <id> brutos/<arquivo> --sem-corte --resolucao-original`
   (base_h.mov na resolução e no fps da câmera, voice.wav, words_cut.json, face_track.json). Fonte 1080p funciona, mas
   o fechado/ênfase amolecem (o relatório avisa).
2. **Ler a transcrição inteira** (`work/<id>/words_cut.json`, tempos do pré-corte) e escrever `work/yt/cfg/<id>.py` a
   partir do molde `work/yt/cfg/_modelo.py`:
   - `limpeza`: tropeço, repetição, frase recomeçada. Corte sempre dentro de pausa; fica a versão mais completa.
     Nunca tirar conteúdo só porque é longo; na dúvida, deixar e citar no relatório.
   - `capitulos`: 1 a cada ~40–70 s, só quando o assunto muda de verdade. Título curto (≤ 3–4 palavras, 1 `*destaque*`).
   - `paineis`: um por ideia forte, ~4–7 s, a cada ~10–20 s, itens entrando no tempo da palavra. Texto = o que a pessoa
     fala, enxuto (2–5 palavras por item), conferido pelo SENTIDO (não copiar erro do whisper). `risco` pra ideia negada.
   - `selos`: 1–2 por vídeo, número ou frase de impacto curta.
   - `enfase`: 2–4 frases de virada.
   - `aviso`: fala que não serve pra YouTube ("link na bio", "me chama no Direct") — não cortar sozinho, avisar o Gerente.
3. `./py work/yt/montar.py <id>` e ler `work/<id>/yt/relatorio.txt`. Tem que dar **0** em "cortes de plano com voz no
   quadro", "trocas de plano com zoom parecido" e "planos parados > 4 s". Se não der, ajustar o cfg (mexer no t0 do
   painel/selo, tirar/mover ênfase) e montar de novo.
4. **Revisão por folhas** (sem render): `bash work/yt/folha.sh <id> folha` (1 quadro a cada 4 s) e
   `bash work/yt/folha.sh <id> trans` (em volta de capítulo, painel, selo e fim) → abrir `work/<id>/yt/folha-NN.png` e
   `trans-NN.png`. Conferir: rosto inteiro e livre do painel, texto do painel dentro do papel e com margem, nada
   cortado, capítulo legível, cartão final com a marca. Trecho de até 10 s pra ver movimento/áudio:
   `bash work/yt/folha.sh <id> trecho <q0>-<q1>`. Foto de um quadro: `bash work/yt/folha.sh <id> still <quadro>`.
5. **Render** (é o Gerente que roda, pela fila, um por vez): `bash work/yt/render.sh <id> [v1]` →
   `saidas/<id>-yt-v1.mp4`. Versão nova = `v2` (nunca sobrescreve).

## Regras do estilo

- **A cor da pessoa nunca muda**: nada de filtro/LUT/grade; o camera.py só reamostra o YUV. Conferir um quadro do MP4
  contra o BRUTO (diferença média < ~2–3 níveis).
- **Troca de plano só no começo de frase** (dentro da pausa), sempre com zoom ≥ 10 % diferente do plano anterior (senão
  é pulo de imagem). Painel entrando sem emenda: a imagem só desliza, sem corte. Nada parado > 4 s (zoom leve contínuo).
- Planos: A aberto (1,00→1,045), M médio (1,18→1,23), F fechado (1,32), E ênfase (1,42), P0–P2 com painel, S selo.
  Zoom sempre ancorado no topo: a cabeça desce, nunca sai do quadro.
- Respiro > 0,85 s vira 0,52 s; a pausa do capítulo fica no tamanho do cartão (~1,3 s, com tom de sala se faltar).
- Áudio: fala em −16 LUFS (medido em estéreo, como o YouTube mede), mix final −16 LUFS e pico −1,5 dBFS. Sons só com
  evento visível: swish no painel, pop/tique nos itens, tesoura no risco, carimbo no selo, whoosh no capítulo, glock no fim.
- Painel de cor sólida da marca (`cor_papel`), texto na `cor_tinta`, destaque na `cor_destaque`. **Nunca faixa escura**
  nem sombra pesada atrás de texto. Sem legenda (vídeo de canal), sem QR/URL/"link na bio" na tela.
- Marca: `projeto.json` → `marca`, `cor_destaque`, `cor_papel`, `cor_tinta`, `cor_cinza`, `logo` (SVG/PNG, opcional:
  sem logo sai o nome da marca em serifa), `logo_simbolo` (marca-d'água no canto, opcional), `slogan` (cartão final),
  `fonte_titulo`/`fonte_titulo_bold`/`fonte_italico`/`fonte_texto`/`fonte_texto_bold` (opcionais; padrão EB Garamond,
  Instrument Serif Italic e Inter, todas OFL).

## Retorno pro Gerente (até 8 linhas)
Duração antes→depois, o que a limpeza tirou, capítulos, nº de painéis/selos, as 3 conferências do relatório (0/0/0),
folhas conferidas (caminhos), avisos de fala e `PENDENTE:`.
