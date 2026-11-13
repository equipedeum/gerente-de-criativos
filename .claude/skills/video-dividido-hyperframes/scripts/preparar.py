# -*- coding: utf-8 -*-
"""Prepara hyperframes/<nome>/public/ a partir do material já cortado e transcrito em work/<gNN>/.

    ./py .claude/skills/video-dividido-hyperframes/scripts/preparar.py g24 criativo-24
    ... --formatos        # depois do OK do RL: gera também os recortes da pessoa pra IN e GL
    ... --rosto-x 1000    # força o centro do rosto (px no 16:9) se a detecção errar

Duas origens:
- Estúdio (16:9): work/<gNN>/base_h.mov (1920x1080 já cortado, alinhado ao áudio) + voice.wav + words_cut.json.
  Recorte fixo centrado no rosto, escala 1:1.
- Celular vertical (sem base_h.mov): work/<gNN>/base.mov (1620x2880, saída do work/pipeline/preparar.py) +
  face_track.json + voice.wav + words_cut.json. Largura inteira (escala 2/3 -> 1080) e uma janela que acompanha o
  rosto na vertical, suavizada (o celular balança e ele anda).
Gera: fontes, gsap, voz.m4a (loudnorm), pessoa.mp4 (RL: 1080x960) e, com --formatos, pessoa-IN.mp4 e pessoa-GL.mp4.
REGRA DO USUÁRIO (12/11/2026): a cor da pessoa NUNCA muda. Os recortes saem com a cor da fonte, só na matriz BT.601
(hyperframes/cor_pessoa.py: o render do HyperFrames extrai os quadros em JPG e lê o YUV como 601 — em 709 a pele
amarelava). --contraste/--saturacao (um realce antigo) estão DESATIVADOS: param com erro.
Imprime a duração pra configurar() e a transcrição numerada (os índices são os que letreiro()/ts() usam).
"""
import argparse
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
FPS = 30
sys.path.insert(0, str(RAIZ / 'hyperframes'))
import cor_pessoa  # noqa: E402   (12/11: REGRA do usuário — a cor da pessoa nunca muda)


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def duracao(arq):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(arq)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def detectar_rosto(video):
    """Centro mediano do rosto (x, y) no 16:9, por Haar em ~15 quadros. None se não achar."""
    try:
        import cv2
    except ImportError:
        return None
    cap = cv2.VideoCapture(str(video))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    xs, ys = [], []
    for k in range(15):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * (k + 0.5) / 15))
        ok, fr = cap.read()
        if not ok:
            continue
        cinza = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        faces = casc.detectMultiScale(cinza, 1.1, 6, minSize=(120, 120))
        if len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            xs.append(x + w / 2)
            ys.append(y + h / 2)
    cap.release()
    if len(xs) < 5:
        return None
    return statistics.median(xs), statistics.median(ys)


def recorte_vertical(base, face_json, saida, alto, pos_rosto, vf_cor, matriz='601'):
    """Janela 1080 x alto da base vertical (1620x2880 -> escala 2/3), acompanhando o rosto na vertical.
    O centro do rosto fica a pos_rosto da altura da janela; trajetória suavizada (gaussiana de 0,6 s).
    matriz='601' pro HyperFrames (cor_pessoa: o render dele lê o YUV como 601); matriz='709' pro Remotion (o
    OffthreadVideo lê o YUV como 709 — com 601 a pele saía ~5 níveis mais vermelha, medido no Paper vertical)."""
    import av
    import numpy as np
    esc = 1080 / 1620
    trilha = json.load(open(face_json))
    # o detector também pega rosto pequeno (gente ao fundo, falso positivo): o da pessoa, com o celular na mão, é
    # sempre grande. Fica só o que tem pelo menos 60 % da largura mediana; depois tira picos com mediana de 0,5 s.
    if trilha:
        wmed = float(np.median([p['w'] for p in trilha]))
        boas = [p for p in trilha if p['w'] >= 0.6 * wmed] or trilha
    else:
        boas = []
    c = av.open(str(base))
    vs = c.streams.video[0]
    n = vs.frames or int(round(float(vs.duration * vs.time_base) * FPS))
    tq = np.arange(n) / FPS
    if boas:
        cy = np.interp(tq, [p['t'] for p in boas], [p['cy'] for p in boas])
        m = int(0.5 * FPS) | 1
        pad = np.pad(cy, m // 2, mode='edge')
        cy = np.array([np.median(pad[i:i + m]) for i in range(n)])
    else:
        cy = np.full(n, 2880 * 0.30)
    sig = 0.6 * FPS
    k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2)
    k /= k.sum()
    cy = np.convolve(np.pad(cy, len(k) // 2, mode='edge'), k, mode='valid')[:n]
    janela = alto / esc  # altura da janela na base
    y0 = np.clip(cy - pos_rosto * janela, 0, 2880 - janela).round().astype(int)
    c.close()
    # o ffmpeg faz tudo (decodifica, recorta, escala, cor); a posição do recorte muda quadro a quadro por sendcmd
    # (bem mais rápido que passar os quadros pelo Python: ~1 min em vez de ~7 por vídeo)
    cmds = Path(saida).with_suffix('.cmd.txt')
    cmds.write_text(''.join(f'{i / FPS:.4f} crop@c y {int(y)};\n' for i, y in enumerate(y0)), encoding='utf-8')
    jan = int(round(janela / 2)) * 2
    rel = str(cmds.name)  # caminho relativo (o filtro do ffmpeg não gosta do "C:" no caminho)
    vf = (f"sendcmd=f={rel},crop@c=1620:{jan}:0:{int(y0[0])},scale=1080:{alto}:flags=lanczos"
          + (f',{vf_cor}' if vf_cor else '') + (cor_pessoa.vf(base) if matriz == '601' else ''))
    tags = cor_pessoa.ARGS if matriz == '601' else ['-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv']
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(Path(base).resolve()), '-vf', vf, '-an', '-r', str(FPS),
                    '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-g', '30', '-keyint_min', '30',
                    '-pix_fmt', 'yuv420p', *tags, '-movflags', '+faststart', str(Path(saida).name)],
                   check=True, cwd=str(Path(saida).parent))
    cmds.unlink()
    print(f'{Path(saida).name}: janela 1080x{alto} seguindo o rosto (y na base {y0.min()}-{y0.max()})')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('gnn', help='pasta em work/ (ex.: g24)')
    ap.add_argument('nome', help='pasta em hyperframes/ (ex.: criativo-24)')
    ap.add_argument('--formatos', action='store_true', help='gera também pessoa-IN.mp4 e pessoa-GL.mp4')
    ap.add_argument('--rosto-x', type=float)
    ap.add_argument('--rosto-y', type=float)
    ap.add_argument('--contraste', type=float, default=1.0)
    ap.add_argument('--saturacao', type=float, default=1.0)
    a = ap.parse_args()

    src = RAIZ / 'work' / a.gnn
    base_h, voz, palavras = src / 'base_h.mov', src / 'voice.wav', src / 'words_cut.json'
    vertical = not base_h.exists()
    exigidos = (src / 'base.mov', src / 'face_track.json', voz, palavras) if vertical else (base_h, voz, palavras)
    for f in exigidos:
        if not f.exists():
            sys.exit(f'falta {f} — cortar/transcrever antes (ver SKILL.md, passo 1)')
    if (a.contraste, a.saturacao) != (1.0, 1.0):
        sys.exit('REGRA DO USUÁRIO (12/11/2026): a cor da pessoa nunca muda — --contraste/--saturacao estão desativados.')
    vf_cor = ''
    pub = RAIZ / 'hyperframes' / a.nome / 'public'
    (pub / 'fonts').mkdir(parents=True, exist_ok=True)
    (pub / 'vendor').mkdir(exist_ok=True)

    # fontes (todas OFL, em ferramentas/fontes): Inter (bold = linhas grandes), Montserrat (Light pra linha fina,
    # Regular quando ela fica pequena) e TikTok Sans (título, só se pedirem)
    for nome in ('Inter-Regular.ttf', 'Inter-Bold.ttf', 'Montserrat-Light.ttf', 'Montserrat-Regular.ttf',
                 'TikTokSans-Variable.ttf'):
        if not (pub / 'fonts' / nome).exists():
            shutil.copy2(RAIZ / 'ferramentas/fontes' / nome, pub / 'fonts' / nome)
    gsap = RAIZ / '.claude/skills/talking-head-recut/assets/vendor/gsap.min.js'
    if not (pub / 'vendor/gsap.min.js').exists():
        shutil.copy2(gsap, pub / 'vendor/gsap.min.js')

    comum = ['-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-g', '30', '-keyint_min', '30',
             '-pix_fmt', 'yuv420p', *cor_pessoa.ARGS, '-movflags', '+faststart', '-an']
    if not (pub / 'voz.m4a').exists():
        ffmpeg('-i', str(voz), '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k',
               str(pub / 'voz.m4a'))
    if vertical:
        base, trilha = src / 'base.mov', src / 'face_track.json'
        if not (a.formatos and (pub / 'pessoa.mp4').exists()):  # com --formatos, o recorte do RL aprovado fica
            recorte_vertical(base, trilha, pub / 'pessoa.mp4', 960, 0.38, vf_cor)
        if a.formatos:
            recorte_vertical(base, trilha, pub / 'pessoa-GL.mp4', 1080, 0.36, vf_cor)
            recorte_vertical(base, trilha, pub / 'pessoa-IN.mp4', 676, 0.42, vf_cor)
        transcricao(base, voz, palavras)
        return

    # rosto
    if a.rosto_x is None:
        r = detectar_rosto(base_h)
        if r is None:
            print('  aviso: rosto não detectado; usando x=1000, y=340 (enquadramento do estúdio). Conferir o recorte.')
            r = (1000, 340)
        fx, fy = r
    else:
        fx, fy = a.rosto_x, (a.rosto_y or 340)
    print(f'rosto em x={fx:.0f} y={fy:.0f} (no 16:9)')
    x_rl = int(min(max(fx - 540, 0), 840))
    y_rl = int(min(max(fy - 0.32 * 960, 0), 120))  # rosto a ~1/3 do quadrado (calibrado no Criativo 22 aprovado: y 40)

    cor = (f',{vf_cor}' if vf_cor else '') + cor_pessoa.vf(base_h)   # 12/11: só a matriz BT.601 (mesma cor)
    ffmpeg('-i', str(base_h), '-vf', f'crop=1080:960:{x_rl}:{y_rl},fps={FPS}{cor}', *comum, str(pub / 'pessoa.mp4'))
    print(f'pessoa.mp4: crop=1080:960:{x_rl}:{y_rl}')
    if a.formatos:
        x_in = int(min(max(fx - 768, 0), 384))
        ffmpeg('-i', str(base_h), '-vf', f'crop=1536:960:{x_in}:{y_rl},scale=1080:676:flags=lanczos,fps={FPS}{cor}',
               *comum, str(pub / 'pessoa-IN.mp4'))
        ffmpeg('-i', str(base_h), '-vf', f'crop=1080:1080:{x_rl}:0,fps={FPS}{cor}', *comum, str(pub / 'pessoa-GL.mp4'))
        print(f'pessoa-IN.mp4: crop=1536:960:{x_in}:{y_rl} -> 1080x676 | pessoa-GL.mp4: crop=1080:1080:{x_rl}:0')

    transcricao(base_h, voz, palavras)


def transcricao(video, voz, palavras):
    dur = math.floor(min(duracao(video), duracao(voz)) * 100) / 100  # pra baixo: nunca passa do vídeo
    print(f'\nduracao={dur:.2f}  (configurar(duracao=...))')
    w = json.load(open(palavras, encoding='utf-8'))
    print(f'palavras={len(w)}; transcrição numerada (índice:palavra@início):\n')
    linha = []
    for i, p in enumerate(w):
        linha.append(f"{i}:{p['w']}@{p['s']:.2f}")
        if p['w'].rstrip().endswith(('.', '?', '!')):
            print(' '.join(linha))
            linha = []
    if linha:
        print(' '.join(linha))


if __name__ == '__main__':
    main()
