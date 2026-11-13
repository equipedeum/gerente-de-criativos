"""Junta os quadros de uma pasta (q_*.jpg do fotos.mjs) numa folha de revisão com o tempo em cima.
    ./py remotion/scripts/folha.py <pasta> [colunas] [largura]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

pasta = Path(sys.argv[1]); cols = int(sys.argv[2]) if len(sys.argv) > 2 else 6; lw = int(sys.argv[3]) if len(sys.argv) > 3 else 360
arqs = sorted(pasta.glob('q_*.jpg'), key=lambda p: float(p.stem[2:]))
lh = lw * 16 // 9
linhas = (len(arqs) + cols - 1) // cols
folha = Image.new('RGB', (cols * lw, linhas * (lh + 26)), 'white')
d = ImageDraw.Draw(folha)
for i, a in enumerate(arqs):
    x, y = (i % cols) * lw, (i // cols) * (lh + 26)
    folha.paste(Image.open(a).resize((lw, lh)), (x, y + 26))
    d.text((x + 6, y + 6), f'{float(a.stem[2:]):.2f}s', fill='black')
folha.save(pasta / 'folha.jpg', quality=88)
print(pasta / 'folha.jpg')
