"""Folha de quadros de um MP4 pra conferência visual (enquadramento, cortes, título/legenda na tela).
Uso: ./py work/pipeline/folha_quadros.py <video.mp4> <saida.png> [--n 8] [--t 1.2,5.0]
Quadros: 0,4 s, n-2 pontos espaçados e 0,5 s antes do fim (+ tempos extras de --t). Cada quadro com o tempo e a resolução real.
"""
import argparse, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FF = open(os.path.join(ROOT, "ferramentas", "ffmpeg_path.txt")).read().strip()

def duracao_res(v):
    p = subprocess.run([FF, "-hide_banner", "-i", v], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p).groups()
    w, hh = map(int, re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", p).groups())
    return int(h) * 3600 + int(m) * 60 + float(s), w, hh

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("saida"); ap.add_argument("--n", type=int, default=8); ap.add_argument("--t", default="")
    a = ap.parse_args()
    dur, W, H = duracao_res(a.video)
    ts = [0.4] + [dur * k / (a.n - 1) for k in range(1, a.n - 1)] + [max(0, dur - 0.5)]
    ts += [float(x) for x in a.t.split(",") if x.strip()]
    alvo_h = 640 if H >= W else 360
    quadros = []
    with tempfile.TemporaryDirectory() as td:
        for i, t in enumerate(sorted(ts)):
            f = os.path.join(td, f"{i}.png")
            subprocess.run([FF, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", a.video, "-frames:v", "1", f], check=True)
            im = Image.open(f).convert("RGB"); im = im.resize((round(im.width * alvo_h / im.height), alvo_h))
            d = ImageDraw.Draw(im); d.rectangle([0, 0, 120, 26], fill=(0, 0, 0)); d.text((6, 5), f"{t:6.2f} s", fill=(255, 255, 0), font=ImageFont.load_default(16))
            quadros.append(im)
    cols = 4 if H >= W else 3; rows = -(-len(quadros) // cols); qw, qh = quadros[0].size
    folha = Image.new("RGB", (cols * qw + (cols + 1) * 8, rows * qh + (rows + 1) * 8 + 30), (40, 40, 40))
    ImageDraw.Draw(folha).text((8, 6), f"{os.path.basename(a.video)}  {W}x{H}  {dur:.2f} s", fill=(255, 255, 255), font=ImageFont.load_default(18))
    for i, im in enumerate(quadros):
        folha.paste(im, (8 + (i % cols) * (qw + 8), 38 + (i // cols) * (qh + 8)))
    folha.save(a.saida); print(f"{a.saida}  ({W}x{H}, {dur:.2f} s, {len(quadros)} quadros)")

if __name__ == "__main__": main()
