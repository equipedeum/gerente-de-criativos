"""Uma folha com os formatos lado a lado (colunas) nos mesmos instantes (linhas) — conferência visual numa imagem só.
Uso: ./py work/pipeline/folha_formatos.py <saida.png> <video1.mp4> [video2.mp4 ...] [--t 1,10,25] [--h 300]
Sem --t: 6 instantes espaçados + 0,5 s antes do fim.
"""
import argparse, os, re, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FF = open(os.path.join(ROOT, "ferramentas", "ffmpeg_path.txt")).read().strip()

def info(v):
    p = subprocess.run([FF, "-hide_banner", "-i", v], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p).groups()
    w, hh = map(int, re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", p).groups())
    return int(h) * 3600 + int(m) * 60 + float(s), w, hh

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("saida"); ap.add_argument("videos", nargs="+")
    ap.add_argument("--t", default=""); ap.add_argument("--h", type=int, default=300)
    a = ap.parse_args()
    infos = [info(v) for v in a.videos]; dur = min(d for d, _, _ in infos)
    ts = [float(x) if float(x) >= 0 else dur + float(x) for x in a.t.split(",") if x.strip()] or [0.5] + [dur * k / 6 for k in range(1, 6)] + [dur - 0.5]   # negativo = a partir do fim (14/10)
    ts = [min(t, dur - 0.5) for t in ts]
    f = ImageFont.load_default(15)
    larg = [round(w * a.h / hh) for _, w, hh in infos]
    W = sum(larg) + 8 * (len(larg) + 1) + 70; H = len(ts) * (a.h + 8) + 40
    folha = Image.new("RGB", (W, H), (40, 40, 40)); d = ImageDraw.Draw(folha)
    x = 70
    for v, (du, w, hh), lw in zip(a.videos, infos, larg):
        d.text((x, 8), f"{os.path.basename(v)[:38]} {w}x{hh} {du:.2f}s", fill=(255, 255, 255), font=f); x += lw + 8
    with tempfile.TemporaryDirectory() as td:
        for i, t in enumerate(ts):
            y = 32 + i * (a.h + 8); d.text((6, y + a.h // 2), f"{t:5.1f}s", fill=(255, 255, 0), font=f); x = 70
            for j, (v, lw) in enumerate(zip(a.videos, larg)):
                p = os.path.join(td, f"{i}_{j}.png")
                subprocess.run([FF, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", v, "-frames:v", "1", p], check=True)
                folha.paste(Image.open(p).convert("RGB").resize((lw, a.h)), (x, y)); x += lw + 8
    folha.save(a.saida); print(f"{a.saida}  ({len(ts)} instantes x {len(a.videos)} vídeos)")

if __name__ == "__main__": main()
