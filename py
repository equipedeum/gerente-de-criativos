#!/usr/bin/env bash
# Roda o Python do projeto (ferramentas/venv) já com PYTHONUTF8=1 e PYTHONPATH=work — no Mac e no Windows (Git Bash).
#   ./py work/pipeline/preparar.py demo brutos/meu-video.mov
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -x "$RAIZ/ferramentas/venv/bin/python" ]; then PY="$RAIZ/ferramentas/venv/bin/python"          # Mac / Linux
elif [ -f "$RAIZ/ferramentas/venv/Scripts/python.exe" ]; then PY="$RAIZ/ferramentas/venv/Scripts/python.exe"   # Windows
else echo "Não achei o Python do projeto (ferramentas/venv). Peça ao Claude: \"instala\"." >&2; exit 1; fi
SEP=":"; W="$RAIZ/work"
if command -v cygpath >/dev/null 2>&1; then SEP=";"; W="$(cygpath -w "$RAIZ/work")"; fi   # Git Bash no Windows
# o código lê o caminho do ffmpeg em ferramentas/ffmpeg_path.txt; se faltar, grava o que estiver no PATH
if [ ! -s "$RAIZ/ferramentas/ffmpeg_path.txt" ]; then
  FF="$(command -v ffmpeg)" || { echo "ffmpeg não encontrado. Peça ao Claude: \"instala\"." >&2; exit 1; }
  command -v cygpath >/dev/null 2>&1 && FF="$(cygpath -m "$FF")"
  printf '%s\n' "$FF" > "$RAIZ/ferramentas/ffmpeg_path.txt"
fi
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONPATH="$W${PYTHONPATH:+$SEP$PYTHONPATH}" DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1
exec "$PY" "$@"
