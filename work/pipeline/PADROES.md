# Padrões aprovados (leia isto primeiro; a skill do estilo só se algo aqui não resolver)

Python sempre `./py` (raiz do projeto). Preparo de cada vídeo em `work/<id>/` (`base.mov` vertical 1620x2880 ou
`base_h.mov` 16:9, `voice.wav`, `words_cut.json`, `face_track.json`, `cuts.json`). **Um render por vez** (fila do
Gerente). Nunca sobrescrever saída (versão nova no nome). Nunca mexer em `brutos/`.

## Legenda (todos os estilos)
- Blocos de 1–4 palavras por unidade de sentido; nunca terminar em artigo/preposição/conjunção/"que"; ponto/vírgula
  fecham o bloco; nada < 0,28 s. Paper: a 1ª linha de um bloco quebrado (`|`) também não termina em artigo/preposição.
- Texto pelo SENTIDO (do/no, a/há, e/é), crase certa ("desde às 8", "à noite"), nomes do `projeto.json`.
- Legenda simples = 1 linha, branca, sombra leve, sem animação, altura FIXA do formato. A animada (2 linhas montando
  palavra por palavra) só quando escolhida no menu (3/4).
- Fim do vídeo: vai até o fim do áudio, segura o último quadro ~0,4 s, fade curto já sem voz.

## Zona segura e movimento (todos)
- Texto só na altura do peito: nunca lá em cima (o Instagram tampa), nunca baixo demais (RL: acima de 65 % da altura),
  nunca no rosto. Texto e enfeites a ≥ 90–100 px das laterais.
- Corte, troca de modo e zoom só em início/fim de frase. Imagem nunca parada > 4 s.
- 3 modos nos estilos com animação (pessoa cheia / animação cheia / dividida) e a pessoa aparece em TODO formato numa
  frase inteira a cada ~10 s. Nada de pessoa num quadrinho/cartão: na dividida ela ocupa a faixa inteira.
- Sem área desfocada/letterbox em nenhum formato.
- A cor da pessoa nunca muda (sem filtro; HF converte pra BT.601 sozinho; Remotion com `--color-space=bt709` e quadros
  PNG; básico sai em BT.709 marcado). Conferir um quadro do MP4 contra o bruto.
- Nada de QR, URL, "link na bio" ou Direct escrito na tela. A palavra "link" falada pode (fica na legenda do básico).

## Básico (menu 1–4)
- Molde `work/basico/cfg/_modelo.py`. Render `./py work/basico/render.py <id> [--formatos IN,GL,YT] [--blocos] [--stills t,t]`,
  `SUF=" v2"` pra versão nova.
- TELA CHEIA SEMPRE (recorte 9:16 no rosto). Fonte 16:9: legenda `leg169=(66, 1260)`; título no peito, nunca no rosto.
- Título (2/4): gancho de rede social, 2 linhas curtas, no máximo 6–9 s, emoji no máx. 1 e só no fim.

## Hyperframe (menu 5)
- Molde `hyperframes/exemplos/hyperframe_gerar.py`; preparar → gerar → revisar → render (skill video-dividido-hyperframes).
- Sem legenda e sem título; uma cena por frase; lettering + metáfora literal; `pessoa_gl` a cada ~10 s.

## Paper (menu 6)
- Molde `remotion/src/paper/videos/demo.tsx`; scripts `preparar_paper.py`, `legenda_paper.py`, `sfx_auto.py`,
  `trilha_cheio.py` (16:9); render `bash remotion/render_paper.sh paper-<id>:../saidas/<id>-paper-v1.mp4`.
- Sem som "papel"; sem etiqueta de seção; sem título; destaque verde `#059669`; número ruim/perda em vermelho; dinheiro
  verde. Papel nunca vazio > ~0,5 s; conteúdo do papel de y ~330 a 860; cabeça nunca sob o rasgo.
- GL: trechos `pessoaGL` = frase INTEIRA, a cada ~10 s.

## VOX (menu 7)
- Molde `hyperframes/exemplos/vox_gerar.py` (termina com `vox.aplicar()`); peça documento a cada 3–4 cenas, cena escura a
  cada 4–6; letra nunca se mexe; tudo estilo papel.

## Extremo (menu 8)
- Molde `hyperframes/exemplos/extremo_gerar.py`; D/G/T por cena; legenda só no T; frase com "link" numa cena G; fonte
  vertical: `modos={'IN': 'T', 'GL': 'T'}` pra a pessoa aparecer no IN/GL; `X.ZOOM_D = False`.

## Edição animada (menu 9)
- Molde `hyperframes/exemplos/animada_gerar.py` (termina com `an.aplicar()`); animação em tela cheia, pessoa cheia a
  cada ~10–15 s; NÃO REPETIR plano/peça/ambiente; MARGEM 0 no `checar_margem.py` antes do render.

## Animação viral (menu 10)
- Molde `remotion/src/animada3d/exemplo/`; T/D/A a cada 3–5 s; legenda só no T; `camD` em toda tomada D; render
  `bash remotion/render_a3d.sh <id>-animada3d:../saidas/<id>-animada3d-v1.mp4`.

## Autoconferência obrigatória (quem renderizou confere)
`./py work/pipeline/folha_formatos.py <saida.png> <RL.mp4> [<IN.mp4> <GL.mp4> <YT.mp4>] --t 1,10,25,40,-1` → abrir a
imagem e checar: cabeça inteira, nada cortado, texto na zona segura e fora do rosto, margens, a pessoa em todo formato.
Corrigir sozinho antes de entregar.
