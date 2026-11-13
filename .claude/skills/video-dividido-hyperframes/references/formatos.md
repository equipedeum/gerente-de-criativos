# Formatos — RL, YT, IN, GL

Todos saem do mesmo `gerar.py` (`gerar.py phosphor RL|YT|IN|GL`); o motor (`hyperframes/motor.py`, dicionário
`FORMATOS`) decide onde ficam os dois "quadrados" do RL. As cenas são desenhadas uma vez, num quadro de 1080x960, e
cada formato só posiciona/escala esse quadro. Ordem de entrega: **RL primeiro, os outros três só depois do OK**.

| | quadro | painel (animações) | pessoa | título | recorte da pessoa |
|---|---|---|---|---|---|
| **RL** | 1080x1920 | em cima, 1080x960, escala 1 | embaixo, 1080x960 | na divisória (y 960) | `pessoa.mp4` = crop 1080x960 escala 1:1 |
| **YT** | 1920x1080 | à esquerda, 960x853 (escala 0,889) | à direita, 960x853 | sobre a pessoa, altura do microfone (~79 % do quadrado dele) | `pessoa.mp4` (o mesmo do RL) |
| **IN** | 1080x1350 | em cima, 1080x675; faixa útil do RL (y 229–856) → y ~150–633 (escala 0,77, desloc. −26) | embaixo, 1080x675 | na divisória (y 675) | `pessoa-IN.mp4` = crop 1536x960, escala 1080x676 (70 %, mais largo, sem cortar) |
| **GL** | 1080x1080 | tela cheia, escala 1 (cena 1080x1080 com fundo preto) | tela cheia nas cenas de `pessoa_gl` | sobre a pessoa, y 800 | `pessoa-GL.mp4` = crop 1080x1080 escala 1:1 |

## Por que cada um é assim

- **YT** — "mantenha os tamanhos dos quadrados, apenas ao invés de ser vertical, colocar um ao lado do outro".
  Os dois quadrados são idênticos ao RL por dentro; pra caber 2×960 de largura ficam 960x853, com faixa preta em
  cima e embaixo. Título: "apenas deixe nessa região" (marcou a altura do microfone no quadrado da pessoa).
  Nas cenas sob o título o painel não precisa desviar dele (`sob-titulo` volta ao padding normal).
- **IN** — "consegue fazer no mesmo estilo Reels, ou vai cortar?" → dá, sem cortar: divisória no meio (675), as
  duas metades em largura total. A pessoa mostra o mesmo enquadramento do RL (cabeça ao microfone) reduzido,
  aparecendo mais estúdio nas laterais. O painel perde o topo vazio, não o conteúdo, e continua baixo.
- **GL** — sugestão dele: "frase 1 com pessoa no vídeo, frase 2 e 3 animadas, frase 4 com pessoa, 5 e 6 animadas…".
  Sem divisória: o quadrado inteiro é da pessoa (rosto do tamanho do RL) ou da animação (tamanho do RL). Ritmo 1:2
  ajustado pelo conteúdo: a frase-chave com animação forte fica animada; perguntas retóricas e "Fechado?" com o
  rosto. Com título na tela, as cenas animadas mantêm o conteúdo entre y 180 e 700.

## Nomes de arquivo
- `saidas/<nome>-hyperframes-vN.mp4` (RL) e `...-vN-YT.mp4`, `-IN.mp4`, `-GL.mp4`.
- Área de Trabalho: `Editados IA <dd-mm>/<título>/RL <título>.mp4`, `IN …`, `GL …`, `YT …`.
