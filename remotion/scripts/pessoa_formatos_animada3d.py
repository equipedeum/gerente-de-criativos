# -*- coding: utf-8 -*-
"""pessoa dos formatos IN / GL / YT do estilo "Animação viral" (12/11/2026), a partir do work/<gnn>/base_h.mov (16:9).
Gera em remotion/public-animada3d/:
  <gnn>-pessoa-IN-cheio.mp4 1080x1350 (janela 864x1080)   <gnn>-pessoa-IN-dividido.mp4 1080x648 (slot da dividida)
  <gnn>-pessoa-GL-cheio.mp4 1080x1080 (janela 1080x1080)  <gnn>-pessoa-GL-dividido.mp4 1080x520
  <gnn>-pessoa-YT-cheio.mp4 1920x1080 (quadro inteiro)    <gnn>-pessoa-YT-dividido.mp4 750x1080 (coluna da direita)
Tamanhos = FMT do remotion/src/animada3d/motor/Viral.tsx (geometria do Editor Extremo). As janelas seguem o rosto
(face_track.json, suavizado). Na dividida o rosto fica com ~250 px (IN) / 230 (GL) / o máximo que a altura deixa (YT).
SEM FILTRO DE COR (regra do usuário, 12/11): só crop + scale no próprio yuv, sem marca de cor (igual à base, igual ao
RL aprovado). Uso: ./py remotion/scripts/pessoa_formatos_animada3d.py t96 </dev/null
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
FF = (RAIZ / 'ferramentas/ffmpeg_path.txt').read_text().strip()
FPS = 30
PUB = RAIZ / 'remotion' / 'public-animada3d'
# nome: (saída w, h, rosto alvo em px (None = janela fixa), centro do rosto na altura da janela, janela fixa w, h)
ALVOS = {
    'IN-cheio': (1080, 1350, None, None, 864, 1080),
    'GL-cheio': (1080, 1080, None, None, 1080, 1080),
    'YT-cheio': (1920, 1080, None, None, 1920, 1080),
    'IN-dividido': (1080, 648, 250, 0.40, None, None),
    'GL-dividido': (1080, 520, 230, 0.40, None, None),
    'YT-dividido': (750, 1080, 330, 0.40, None, None),
}


def suave(v, sig_s, n, med=0.5):
    m = int(med * FPS) | 1
    pad = np.pad(v, m // 2, mode='edge')
    v = np.array([np.median(pad[i:i + m]) for i in range(n)])
    sig = sig_s * FPS
    k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2)
    k /= k.sum()
    return np.convolve(np.pad(v, len(k) // 2, mode='edge'), k, mode='valid')[:n]


# Fonte de CELULAR vertical (work/<gnn>/base.mov 1620x2880, sem base_h.mov; 12/11, caso real = b53b): o rosto ocupa ~52 % da
# largura, então só saem os recortes que cabem sem close: IN e GL cheios (janela da largura inteira) e a coluna da
# dividida do YT (750x1080). A faixa baixa da dividida do IN/GL viraria close e o YT cheio cortaria a cabeça — no Video.tsx
# esses modos trocam (formatos.IN/GL.trocar {D: "A"}; formatos.YT.trocar {T: "L"}). Topo do cabelo a ~10 % da janela.
ALVOS_V = {'IN-cheio': (1080, 1350), 'GL-cheio': (1080, 1080), 'YT-dividido': (750, 1080)}
K_CAB = 0.62   # topo do cabelo = cy - 0,62 x largura do rosto (o mesmo K_CAB_V do Editor Extremo)


def main_vertical(gnn, so=None):
    base = RAIZ / 'work' / gnn / 'base.mov'
    import av
    with av.open(str(base)) as c:
        vs = c.streams.video[0]
        BW, BH = vs.codec_context.width, vs.codec_context.height
        n = vs.frames or int(round(float(vs.duration * vs.time_base) * FPS))
    tq = np.arange(n) / FPS
    trilha = json.load(open(RAIZ / 'work' / gnn / 'face_track.json'))
    wmed = float(np.median([p['w'] for p in trilha]))
    boas = [p for p in trilha if 0.6 * wmed <= p['w'] <= 1.5 * wmed] or trilha
    cab = np.interp(tq, [p['t'] for p in boas], [p['cy'] - K_CAB * p['w'] for p in boas])
    m = int(0.6 * FPS)                       # a janela sobe ANTES dele subir: mínimo em ±0,6 s, depois suaviza
    pad = np.pad(cab, m, mode='edge')
    cab = suave(np.array([pad[i:i + 2 * m + 1].min() for i in range(n)]), 1.2, n, 0.7)
    for nome, (W, H) in ALVOS_V.items():
        if so and nome not in so:
            continue
        s = max(W / BW, H / BH)                # largura inteira (nunca coluna estreita)
        jw, jh = min(BW, int(round(W / s / 2)) * 2), min(BH, int(round(H / s / 2)) * 2)
        x0 = (BW - jw) // 2
        y0 = np.clip(cab - 0.10 * jh, 0, BH - jh).round().astype(int)
        y0 -= y0 % 2
        saida = PUB / f'{gnn}-pessoa-{nome}.mp4'
        cmd = RAIZ / 'work' / gnn / f'pessoa_{nome}.cmd.txt'
        cmd.write_text(''.join(f'{i / FPS:.4f} crop@c y {int(y)};\n' for i, y in enumerate(y0)), encoding='utf-8')
        vf = f"sendcmd=f={cmd.name},crop@c={jw}:{jh}:{x0}:{int(y0[0])},scale={W}:{H}:flags=lanczos"
        subprocess.run([FF, '-v', 'error', '-y', '-i', 'base.mov', '-vf', vf, '-an', '-r', str(FPS), '-c:v', 'libx264',
                        '-crf', '18', '-preset', 'medium', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p',
                        '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                        '-movflags', '+faststart', str(saida)], check=True, cwd=str(cmd.parent))
        cmd.unlink()
        print(f'{saida.name}: janela {jw}x{jh} -> {W}x{H} (rosto ~{wmed * s:.0f} px); y {y0.min()}-{y0.max()}')


def main(gnn, so=None):
    if not (RAIZ / 'work' / gnn / 'base_h.mov').exists() and (RAIZ / 'work' / gnn / 'base.mov').exists():
        return main_vertical(gnn, so)
    base = RAIZ / 'work' / gnn / 'base_h.mov'
    import av
    with av.open(str(base)) as c:
        vs = c.streams.video[0]
        BW, BH = vs.codec_context.width, vs.codec_context.height
        n = vs.frames or int(round(float(vs.duration * vs.time_base) * FPS))
    assert (BW, BH) == (1920, 1080), (BW, BH)
    tq = np.arange(n) / FPS
    trilha = json.load(open(RAIZ / 'work' / gnn / 'face_track.json'))
    wmed = float(np.median([p['w'] for p in trilha]))
    boas = [p for p in trilha if p['w'] >= 0.6 * wmed] or trilha
    cx = suave(np.interp(tq, [p['t'] for p in boas], [p['cx'] for p in boas]), 0.8, n)
    cy = suave(np.interp(tq, [p['t'] for p in boas], [p['cy'] for p in boas]), 1.2, n, 0.7)
    for nome, (W, H, rosto, frac, jw, jh) in ALVOS.items():
        if so and nome not in so:
            continue
        if rosto:
            s = max(rosto / wmed, W / BW, H / BH)
            jw, jh = int(round(W / s / 2)) * 2, int(round(H / s / 2)) * 2
            jw, jh = min(jw, BW), min(jh, BH)
        x0 = np.clip(cx - jw / 2, 0, BW - jw).round().astype(int)
        y0 = np.clip(cy - (frac or 0.5) * jh, 0, BH - jh).round().astype(int) if jh < BH else np.zeros(n, int)
        x0 -= x0 % 2
        y0 -= y0 % 2
        saida = PUB / f'{gnn}-pessoa-{nome}.mp4'
        cmd = RAIZ / 'work' / gnn / f'pessoa_{nome}.cmd.txt'
        cmd.write_text(''.join(f'{i / FPS:.4f} crop@c x {int(x)};\n{i / FPS:.4f} crop@c y {int(y)};\n'
                               for i, (x, y) in enumerate(zip(x0, y0))), encoding='utf-8')
        vf = f"sendcmd=f={cmd.name},crop@c={jw}:{jh}:{int(x0[0])}:{int(y0[0])},scale={W}:{H}:flags=lanczos"
        subprocess.run([FF, '-v', 'error', '-y', '-i', 'base_h.mov', '-vf', vf, '-an', '-r', str(FPS), '-c:v', 'libx264',
                        '-crf', '18', '-preset', 'medium', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p',
                        '-movflags', '+faststart', str(saida)], check=True, cwd=str(cmd.parent))
        cmd.unlink()
        print(f'{saida.name}: janela {jw}x{jh} -> {W}x{H}; x {x0.min()}-{x0.max()}, y {y0.min()}-{y0.max()}')


if __name__ == '__main__':
    main(sys.argv[1], set(sys.argv[2:]) or None)
