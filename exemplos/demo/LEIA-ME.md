# Vídeo de demonstração

Os moldes de todos os estilos foram feitos com este roteiro (texto genérico, voz sintética), com o id `demo`:

- `roteiro.txt` — o texto falado.
- `words_cut.json` — a transcrição por palavra (o que o `work/pipeline/preparar.py` gera em `work/demo/`).

Os índices de palavra dos moldes (`work/basico/cfg/_modelo.py`, `hyperframes/exemplos/*.py`,
`remotion/src/paper/videos/demo.tsx`) apontam pra essa transcrição. Num vídeo real, troque tudo pelos índices e tempos
do `work/<id>/words_cut.json` dele.
