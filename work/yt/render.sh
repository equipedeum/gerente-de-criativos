#!/bin/bash
# YouTube dinâmico (menu 11) — RENDER FINAL de um vídeo. UM render por vez no computador (o Gerente põe na fila).
#   bash work/yt/render.sh <id> [v1]        -> saidas/<id>-yt-v1.mp4 (nunca sobrescreve; versão nova = v2, v3…)
# 1) Remotion: grafismos em PNG transparente (painéis, selos, capítulos, cartão final) -> work/<id>/yt/graf
# 2) work/yt/camera.py: a pessoa direto da gravação em YUV (planos/punch-in, cor intacta) + overlay dos PNG em bt709 + mix.wav
# Os PNG vão pra Lixeira depois que o MP4 sai.
set -e
id=$1; v=${2:-v1}
[ -n "$id" ] || { echo "uso: bash work/yt/render.sh <id> [v1]"; exit 1; }
R="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$R"
[ -s "remotion/public-yt/$id/edl.json" ] || { echo "falta remotion/public-yt/$id/edl.json: rode ./py work/yt/montar.py $id"; exit 1; }
mkdir -p saidas
out="$R/saidas/$id-yt-$v.mp4"
[ -e "$out" ] && { echo "já existe: $out (não sobrescrevo; use a próxima versão)"; exit 1; }
G="$R/work/$id/yt/graf"
[ -e "$G" ] && ./py -c "import sistema,sys; sistema.lixeira(sys.argv[1])" "$G" </dev/null
B="$R/work/$id/yt/_bundle"
[ -e "$B" ] && ./py -c "import sistema,sys; sistema.lixeira(sys.argv[1])" "$B" </dev/null
export DO_NOT_TRACK=1
cd "$R/remotion"
echo "$(date +%H:%M) 1/2 grafismos $id"
npx remotion bundle src/yt-dinamico/index.tsx --public-dir="public-yt/$id" --out-dir="$B" --log=error </dev/null
npx remotion render "$B" graf "$G" --sequence --image-format=png --concurrency=4 --log=error </dev/null
cd "$R"
echo "$(date +%H:%M) 2/2 câmera + overlay + áudio -> $out"
./py -u work/yt/camera.py "$id" final "$out" "$G" </dev/null
[ -s "$out" ] || { echo "$(date +%H:%M) FALHOU $id"; exit 1; }
./py -c "import sistema,sys; [sistema.lixeira(p) for p in sys.argv[1:]]" "$G" "$B" </dev/null
echo "$(date +%H:%M) OK $out"
