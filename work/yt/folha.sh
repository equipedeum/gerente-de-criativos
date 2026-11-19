#!/bin/bash
# YouTube dinâmico (menu 11) — revisão SEM o render final:
#   bash work/yt/folha.sh <id> folha            -> work/<id>/yt/folha-NN.png (1 quadro a cada 4 s, 3x3)
#   bash work/yt/folha.sh <id> trans            -> work/<id>/yt/trans-NN.png (em volta de capítulo, painel, selo e fim)
#   bash work/yt/folha.sh <id> trecho 300-450   -> work/<id>/yt/trecho-300-450.mp4 (quadros; no máximo ~10 s)
#   bash work/yt/folha.sh <id> still 420        -> work/<id>/yt/still-420.png (foto de um quadro, 1920x1080)
set -e
id=$1; tipo=${2:-folha}; faixa=$3
R="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$R"
[ -s "remotion/public-yt/$id/edl.json" ] || { echo "falta remotion/public-yt/$id/edl.json: rode ./py work/yt/montar.py $id"; exit 1; }
D="$R/work/$id/yt"; P="$D/_png-$tipo${faixa:+-$faixa}"; B="$D/_bundle-rev"
mkdir -p "$D"
for x in "$P" "$B"; do [ -e "$x" ] && ./py -c "import sistema,sys; sistema.lixeira(sys.argv[1])" "$x" </dev/null; done
export DO_NOT_TRACK=1
cd "$R/remotion"
npx remotion bundle src/yt-dinamico/index.tsx --public-dir="public-yt/$id" --out-dir="$B" --log=error </dev/null
if [ "$tipo" = "trecho" ]; then
  a=${faixa%-*}; b=${faixa#*-}
  npx remotion render "$B" graf "$P" --sequence --image-format=png --frames="$a-$((b - 1))" --concurrency=4 --log=error </dev/null
  cd "$R"; ./py -u work/yt/camera.py "$id" trecho "$a" "$b" "$D/trecho-$faixa.mp4" "$P" </dev/null
elif [ "$tipo" = "still" ]; then
  mkdir -p "$P"
  npx remotion still "$B" graf "$P/still-$faixa.png" --frame="$faixa" --image-format=png --log=error </dev/null
  cd "$R"; ./py -u work/yt/camera.py "$id" still "$faixa" "$P/still-$faixa.png" "$D/still-$faixa.png" </dev/null
else
  npx remotion render "$B" "graf-$tipo" "$P" --sequence --image-format=png --concurrency=4 --log=error </dev/null
  cd "$R"; ./py -u work/yt/camera.py "$id" folha "$P" "$D/$tipo" "$tipo" </dev/null
fi
cd "$R"; ./py -c "import sistema,sys; [sistema.lixeira(p) for p in sys.argv[1:]]" "$P" "$B" </dev/null
echo OK
