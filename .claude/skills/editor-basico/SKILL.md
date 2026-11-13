---
name: editor-basico
description: Editor básico (menu 1–4) — versão simples em TELA CHEIA com legenda (simples de 1 linha ou animada de 2 linhas) e, nos itens 2 e 4, título estilo Edits nos primeiros 6–9 s. Funciona com vídeo vertical de celular e horizontal 16:9. Usar quando o usuário escolher 1, 2, 3 ou 4 no menu, pedir "versão básica"/"só legenda", ou quando o gerente delegar a versão básica de um vídeo.
---

# Editor básico

Motor: `work/criativo.py` (renderiza quadro a quadro com Pillow + ffmpeg). Render: `work/basico/render.py`. Config de cada
vídeo: `work/basico/cfg/<id>.py`, a partir do molde comentado `work/basico/cfg/_modelo.py`. Entrada: `work/<id>/`
(`base.mov` vertical ou `base_h.mov` 16:9, `voice.wav`, `words_cut.json`, `face_track.json`, `cuts.json`), gerada pelo
`work/pipeline/preparar.py`. O render detecta sozinho se a fonte é vertical ou 16:9.

## Itens do menu
| item | título | legenda | no cfg |
|---|---|---|---|
| 1 | não | simples (1 linha, branca, sombra leve, SEM animação) | `sem_titulo=True`, `leg_estilo=None` |
| 2 | sim | simples | `titulo=[...]`, `legenda_desde=…`, `leg_estilo=None` |
| 3 | não | animada (frase em até 2 linhas montando palavra por palavra) | `sem_titulo=True`, `leg_estilo="serif"`, `leg_chave=False` |
| 4 | sim | animada | `titulo=[...]`, `legenda_desde=…`, `leg_estilo="serif"`, `leg_chave=False` |

A legenda simples é o padrão e **não muda de estilo sem pedido**.

## Modos

### MONTAR (sem render)
1. `./py work/basico/render.py <id> palavras` lista as palavras com índice.
2. Escrever `work/basico/cfg/<id>.py` a partir do `_modelo.py`:
   - `pasta` = título curto (vira o nome do arquivo; sem `/ \ : * ? " < > |`);
   - `titulo` (itens 2/4) = 2 linhas curtas do titulista, emoji no máximo 1 e só no FIM; `legenda_desde` = índice da
     última palavra que o título cobre, num fim de frase entre 6 e 9 s (se a frase do título passa de 9 s:
     `gancho_frases` com os blocos do resto do gancho);
   - `repl` = correções do whisper pelo SENTIDO (`{índice: (n_palavras, ["novas"])}`; `(1, [])` tira hesitação);
   - `frases` = blocos de 1–4 palavras separados por `|`, uma frase por linha;
   - `enquadro` = tela cheia (`lambda t: (1.0, 0.33)`); punch-in (1,15–1,35) só em fronteira de frase.
3. `./py work/auditar_legenda.py work/basico/cfg/<id>.py` e `./py work/basico/render.py <id> --blocos`; corrigir o que
   listar (bloco > 4 palavras só quando cortar separaria artigo/preposição do nome).
4. Stills: `./py work/basico/render.py <id> --stills 2,5,12` → `work/<id>/prev/RL-t*.png`; abrir e conferir título fora
   do rosto (no peito ou acima da cabeça, nunca no queixo), legenda na altura padrão, cabeça inteira.

### FINAL
Comandos pro Gerente (fila, um render por vez):
- RL: `./py work/basico/render.py <id>` → `saidas/basico/<pasta>/RL <pasta>.mp4`
- Depois do OK do RL: `./py work/basico/render.py <id> --formatos IN,GL,YT` (mesma pasta, `-IN`, `-GL`, `-YT`).
- Versão nova sem sobrescrever: `SUF=" v2" ./py work/basico/render.py <id>`.
Conferir: `./py work/pipeline/folha_formatos.py <png> <RL> <IN> <GL> <YT> --t 1,8,20,-1` e abrir a imagem.

### CORRIGIR
Aplicar exatamente o ajuste, stills do trecho, render de versão nova.

## Regras que valem sempre
- **TELA CHEIA SEMPRE**, do primeiro ao último quadro, em todos os formatos: nunca letterbox, faixa desfocada, quadro
  aberto ou área borrada (fonte vertical no YT = recorte 16:9 cheio em volta do rosto, `yt_zoom_cheio`). Objeto que não
  cabe fica de fora; no máximo deslocar o recorte mantendo a cabeça inteira.
- **Legenda**: blocos de 1 a 4 palavras, unidade de sentido; nunca terminar em artigo/preposição/conjunção/"que"; ponto
  e vírgula fecham o bloco; sem frase nova no meio; bloco < 0,28 s se junta ao vizinho; cortar ANTES de conector.
- **Fonte vertical no YT (1920×1080)**: sai um recorte 16:9 cheio em volta do rosto (sem blur). Em selfie bem perto o
  rosto enche o quadro e a legenda cai no queixo: confira a folha do YT e, nesse caso, pergunte ao usuário se quer o YT
  (`yt_rosto` sobe/desce o rosto no quadro; `yt_zoom_cheio` > 1 fecha mais).
- **Altura da legenda fixa** (fonte 16:9: `leg169=(66, 1260)`; o motor limita a base a 65 % da altura no RL). Não subir
  pra cima da cabeça nem descer pro peito pra desviar de objeto. Exceção automática: nos punch-ins a legenda desce pra
  fora do queixo (`leg_punch`, `leg_punch_rl=True`).
- **Título**: gancho de rede social tirado do que o vídeo diz (número/resultado, contraste/dor, cena concreta,
  curiosidade), 1ª pessoa, 2 linhas curtas; nunca descritivo/morno nem promessa que o vídeo não sustenta; no máximo
  6–9 s na tela; fora do rosto; emoji no fim.
- **Emoji**: no Mac sai a Apple Color Emoji do sistema; no Windows a Segoe UI Emoji; se existir
  `ferramentas/emoji/<codepoint>.png` (ex.: Twemoji baixado na instalação), usa o PNG.
- **Movimento**: o motor já dá planos aberto/fechado leves e câmera suave seguindo o rosto (nada parado > 4 s;
  `mov_amp=0` desliga, só se pedirem).
- **Fim do vídeo**: vai até o fim do áudio, segura o último quadro 0,4 s e faz fade preto de 0,24 s já sem voz (automático).
- **Cor da pessoa intacta**: o vídeo sai em BT.709 marcado, igual à gravação. Conferir um quadro do MP4 contra o bruto.
- Fonte fina nunca peso 100.
