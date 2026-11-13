#!/usr/bin/env bash
# Fila única de render: UM render por vez no computador. Cada linha de work/pipeline/fila_render.txt é um comando
# completo, rodado da raiz do projeto, por exemplo:
#   ./py work/basico/render.py demo --formatos IN,GL,YT
#   ./py .claude/skills/video-dividido-hyperframes/scripts/renderizar.py demo-extremo saidas/demo-extremo-v1 RL
#   bash remotion/render_paper.sh paper-demo saidas/demo-paper-v1.mp4
# Dá pra acrescentar/reordenar linhas com a fila rodando (ela lê a 1ª linha a cada volta). Alteração pedida pelo
# usuário vai no TOPO; vídeo novo no fim. Rodar em segundo plano: bash work/pipeline/fila_render.sh
# Portável (Mac bash 3.2 e Git Bash): sem sed -i, sem mapfile, sem flags GNU.
cd "$(dirname "$0")/../.." || exit 1
F=work/pipeline/fila_render.txt; A=work/pipeline/fila_render_atual.txt; L=work/pipeline/.fila_render.lock
LOG=work/pipeline/fila_render.log; ERR=work/pipeline/fila_render_erros.txt
mkdir "$L" 2>/dev/null || { echo "a fila já está rodando (se não estiver, apague a pasta $L)"; exit 1; }
trap 'rmdir "$L"' EXIT
if [ -s "$A" ]; then   # item interrompido (PC desligou no meio) volta pro topo
  echo "item interrompido volta pro topo: $(cat "$A")"; { cat "$A"; cat "$F" 2>/dev/null; } > "$F.tmp"; mv "$F.tmp" "$F"; rm -f "$A"
fi
ocupado() { ps -ef 2>/dev/null | grep -E "[r]enderizar\.py|work/basico/[r]ender\.py|[r]emotion render|[h]yperframes(@[0-9.]+)? render" | grep -vq "fila_render"; }
while [ -s "$F" ]; do
  while ocupado; do sleep 20; done
  IFS= read -r cmd < "$F"; cmd=${cmd%$'\r'}
  tail -n +2 "$F" > "$F.tmp"; mv "$F.tmp" "$F"
  [ -z "$cmd" ] && continue
  case "$cmd" in \#*) continue ;; esac
  echo "$cmd" > "$A"
  echo "== $(date '+%d/%m %H:%M') $cmd" | tee -a "$LOG"
  if bash -c "$cmd" >> "$LOG" 2>&1 </dev/null; then echo "   ok $(date +%H:%M)" | tee -a "$LOG"
  else echo "   ERRO $(date +%H:%M) (ver $LOG)" | tee -a "$LOG"; echo "$(date '+%d/%m %H:%M') $cmd" >> "$ERR"; fi
  rm -f "$A"
done
echo "FIM fila_render $(date +%H:%M)"
