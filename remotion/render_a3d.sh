#!/bin/bash
# Fila de render da Animação viral (um por vez): bash remotion/render_a3d.sh <composição>[:saida.mp4] ...
# saída padrão ../saidas/<composição>.mp4 ; imprime OK/FALHOU por item e FIM
cd "$(dirname "$0")" || exit 1
for item in "$@"; do
  comp=${item%%:*}; out=${item#*:}; [ "$out" = "$item" ] && out="../saidas/$comp.mp4"
  echo "$(date +%H:%M) render $comp"
  DO_NOT_TRACK=1 npx remotion render src/animada3d/index.tsx $comp "$out" --public-dir=public-animada3d --gl=${GL_REMOTION:-angle} --concurrency=3 --crf=18 --color-space=bt709 --log=error </dev/null 2>&1 | grep -vE "texto-fora|mundo.ts" | tail -3
  [ -s "$out" ] && echo "$(date +%H:%M) OK $comp" || echo "$(date +%H:%M) FALHOU $comp"
done
echo "$(date +%H:%M) FIM"
