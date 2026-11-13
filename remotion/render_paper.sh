#!/usr/bin/env bash
# Render do estilo papel (Remotion), um por vez: bash remotion/render_paper.sh <composição>[:saida.mp4] ...
#   bash remotion/render_paper.sh paper-demo                     -> saidas/paper-demo.mp4
#   bash remotion/render_paper.sh paper-demo:../saidas/demo-paper-v1.mp4 paper-demo-IN:../saidas/demo-paper-v1-IN.mp4
# Sempre --color-space=bt709 (REGRA: a cor da pessoa nunca muda). Confere os tipos (tsc) antes.
cd "$(dirname "$0")" || exit 1
npx tsc --noEmit -p . || { echo "erro de tipo no TypeScript — corrija antes de renderizar"; exit 1; }
for item in "$@"; do
  comp=${item%%:*}; out=${item#*:}; [ "$out" = "$item" ] && out="../saidas/$comp.mp4"
  echo "$(date +%H:%M) render $comp"
  DO_NOT_TRACK=1 npx remotion render src/index.ts "$comp" "$out" --color-space=bt709 --log=error </dev/null 2>&1 | tail -3
  [ -s "$out" ] && echo "$(date +%H:%M) OK $comp -> $out" || { echo "$(date +%H:%M) FALHOU $comp"; exit 1; }
done
