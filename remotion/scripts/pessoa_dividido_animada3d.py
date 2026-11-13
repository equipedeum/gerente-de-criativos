# -*- coding: utf-8 -*-
"""pessoa da TELA DIVIDIDA do estilo "Animação viral" (12/11/2026), a partir do work/<gnn>/base.mov vertical (1620x2880).
Largura inteira da base, janela na proporção da faixa de baixo (ex.: 1080x1100 -> janela 1620x1650) seguindo o rosto na
VERTICAL (face_track.json, bem suavizado), com ~9 % de folga acima do cabelo e os ombros aparecendo.
SEM FILTRO DE COR: só crop + scale no próprio yuv, e as tags bt709/tv (o render do Remotion sai com --color-space=bt709).

Uso (na raiz do projeto):
  ./py remotion/scripts/pessoa_dividido_animada3d.py g22 remotion/public-animada3d/g22-pessoa-dividido.mp4 --alt 1100 </dev/null
--alt = altura da faixa da pessoa na dividida (1920 - divY do Video.tsx): 960 (padrão) ou 1100 (close, ex.: g22).
--rosto = onde fica o centro do rosto (linha dos olhos do face_track) na janela, de 0 (topo) a 1; 0,44 deixa ~9 % acima
do cabelo num close como o g22 (rosto ~900 px de largura na base).
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
FF = (RAIZ / 'ferramentas/ffmpeg_path.txt').read_text().strip()
FFPROBE = next((str(Path(FF).with_name(n)) for n in ('ffprobe.exe', 'ffprobe') if Path(FF).with_name(n).exists()), 'ffprobe')
FPS = 30

ap = argparse.ArgumentParser()
ap.add_argument('gnn')
ap.add_argument('saida')
ap.add_argument('--alt', type=int, default=960)
ap.add_argument('--rosto', type=float, default=0.44)
ap.add_argument('--suave', type=float, default=1.2, help='sigma da suavização vertical, em segundos')
a = ap.parse_args()

base = RAIZ / 'work' / a.gnn / 'base.mov'
info = json.loads(subprocess.run([FFPROBE, '-v', 'error', '-select_streams', 'v', '-show_entries',
                                  'stream=width,height,pix_fmt,color_range,color_space,nb_frames:format=duration', '-of', 'json', str(base)],
                                 capture_output=True, text=True, check=True).stdout)
st = info['streams'][0]
BW, BH = int(st['width']), int(st['height'])
print('base:', BW, BH, st.get('pix_fmt'), st.get('color_range'), st.get('color_space'))
n = int(round(float(info['format']['duration']) * FPS))
jan = int(round(BW * a.alt / 1080 / 2)) * 2           # 1100 -> 1650; 960 -> 1440
tq = np.arange(n) / FPS
trilha = json.load(open(RAIZ / 'work' / a.gnn / 'face_track.json'))
wmed = float(np.median([p['w'] for p in trilha]))
boas = [p for p in trilha if p['w'] >= 0.6 * wmed] or trilha
cy = np.interp(tq, [p['t'] for p in boas], [p['cy'] for p in boas])
m = int(0.7 * FPS) | 1                                 # mediana tira os saltos do detector
pad = np.pad(cy, m // 2, mode='edge')
cy = np.array([np.median(pad[i:i + m]) for i in range(n)])
sig = a.suave * FPS
k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2)
k /= k.sum()
cy = np.convolve(np.pad(cy, len(k) // 2, mode='edge'), k, mode='valid')[:n]
y0 = np.clip(cy - a.rosto * jan, 0, BH - jan).round().astype(int)
y0 -= y0 % 2                                           # crop em linha par (yuv420p)
print(f'janela {BW}x{jan} -> 1080x{a.alt}; y0 de {y0.min()} a {y0.max()} (mediana {int(np.median(y0))})')

saida = (RAIZ / a.saida).resolve()
# a lista de comandos do crop fica em work/<gnn>/ (o ffmpeg roda de lá, pra não escapar caminho do Windows no filtro)
cmd = RAIZ / 'work' / a.gnn / f'pessoa_dividido_{a.alt}.cmd.txt'
cmd.write_text(''.join(f'{i / FPS:.4f} crop@c y {int(y)};\n' for i, y in enumerate(y0)), encoding='utf-8')
vf = f"sendcmd=f={cmd.name},crop@c={BW}:{jan}:0:{int(y0[0])},scale=1080:{a.alt}:flags=lanczos"
subprocess.run([FF, '-v', 'error', '-y', '-i', 'base.mov', '-vf', vf, '-an', '-r', str(FPS), '-c:v', 'libx264', '-crf', '18',
                '-preset', 'medium', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p',
                '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                '-movflags', '+faststart', str(saida)], check=True, cwd=str(cmd.parent))
print('ok', saida)
