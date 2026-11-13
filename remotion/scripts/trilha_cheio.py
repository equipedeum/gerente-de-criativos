# -*- coding: utf-8 -*-
"""Trilha horizontal do rosto pro modo "pessoa em TELA CHEIA" do RL no estilo papel (26/10/2026, regra do usuário:
alternar tela dividida / pessoa cheia / papel cheio). Lê work/<id>/face_track.json (mesmo relógio do <id>-h.mp4),
descarta detecções pequenas, suaviza (gaussiana 0,8 s, igual ao hyperframes/pessoa_cheio.py) e grava
src/paper/videos/<id>-cheio.json = {"dt": 0.2, "cx": [...]} (cx no 16:9 1920x1080).
No <id>.tsx: `import cheio from './<id>-cheio.json'` e `rostoCheio: cheio`. Uso: python scripts/trilha_cheio.py t36 [t37 ...]
"""
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
DT = 0.2


def gerar(vid):
    trilha = json.load(open(RAIZ / 'work' / vid / 'face_track.json'))
    wmed = float(np.median([p['w'] for p in trilha]))
    boas = [p for p in trilha if p['w'] >= 0.6 * wmed] or trilha
    fim = max(p['t'] for p in trilha) + 1
    tq = np.arange(0, fim, 1 / 30)
    cx = np.interp(tq, [p['t'] for p in boas], [p['cx'] for p in boas])
    sig = 0.8 * 30
    k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2)
    k /= k.sum()
    cx = np.convolve(np.pad(cx, len(k) // 2, mode='edge'), k, mode='valid')[:len(tq)]
    amostra = [round(float(x), 1) for x in cx[::int(DT * 30)]]
    out = RAIZ / 'remotion/src/paper/videos' / f'{vid}-cheio.json'
    json.dump({'dt': DT, 'cx': amostra}, open(out, 'w', encoding='utf-8'))
    print(out, len(amostra), 'amostras')


if __name__ == '__main__':
    for v in sys.argv[1:]:
        gerar(v)
