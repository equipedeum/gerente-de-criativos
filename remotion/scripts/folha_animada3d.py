# -*- coding: utf-8 -*-
"""Folha de revisão do estilo "Animada 3D": junta as fotos q_*.jpg de uma pasta numa grade com o tempo de cada uma.
Uso: python remotion/scripts/folha_animada3d.py <pasta-das-fotos> <saida.png> [colunas] [largura-de-cada]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

pasta, saida = Path(sys.argv[1]), Path(sys.argv[2])
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
lw = int(sys.argv[4]) if len(sys.argv) > 4 else 320
fotos = sorted(pasta.glob('q_*.jpg'))
w0, h0 = Image.open(fotos[0]).size if fotos else (9, 16)
lh = lw * h0 // w0   # proporção da 1ª foto (12/11: IN/GL/YT além do RL)
lin = (len(fotos) + cols - 1) // cols
folha = Image.new('RGB', (cols * lw, lin * (lh + 22)), '#222')
d = ImageDraw.Draw(folha)
for i, f in enumerate(fotos):
    im = Image.open(f).convert('RGB').resize((lw, lh), Image.LANCZOS)
    x, y = (i % cols) * lw, (i // cols) * (lh + 22)
    folha.paste(im, (x, y + 22))
    d.text((x + 6, y + 5), f.stem[2:] + ' s', fill='#ffe45c')
folha.save(saida)
print(saida, len(fotos))
