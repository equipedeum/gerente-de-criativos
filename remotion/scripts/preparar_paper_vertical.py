"""Prepara pro Editor Paper um vídeo gravado na VERTICAL no celular (work/<gNN>/ vindo do work/pipeline/preparar.py).

    ./py remotion/scripts/preparar_paper_vertical.py g52b

O motor papel espera um 16:9 de 1920x1080. Aqui o quadro 16:9 é montado em volta de uma janela de 1080x980 da base
vertical (1620x2880 -> escala 2/3, largura inteira) que acompanha o rosto na vertical (mesma técnica do HyperFrames:
`recorte_vertical`), centrada no 16:9 (x 420) e a 20 px do topo; o resto é preto e nunca aparece (o motor só mostra
1080 de largura centrados em `rosto.x`). Assim o motor e o g28 aprovado ficam intactos.

Gera em remotion/public/brutos/: <gNN>-h.mp4 (1920x1080, sem áudio) e <gNN>-voz.m4a (loudnorm -16).
Imprime `rosto` (x 960, y no 16:9), `duracao` e a transcrição com tempos.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / '.claude/skills/video-dividido-hyperframes/scripts'))
import preparar  # noqa: E402  (recorte_vertical, duracao)

ALTO, POS_ROSTO = 980, 0.40   # janela 1080 x 980; centro do rosto a 40 % da altura da janela
X0, Y0 = 420, 20              # onde a janela entra no 16:9


def main(g):
    src = RAIZ / 'work' / g
    base, trilha, voz, palavras = src / 'base.mov', src / 'face_track.json', src / 'voice.wav', src / 'words_cut.json'
    for f in (base, trilha, voz, palavras):
        if not f.exists():
            sys.exit(f'falta {f} — rode antes ./py work/pipeline/preparar.py {g} <vídeo>')
    pub = RAIZ / 'remotion' / 'public' / 'brutos'
    pub.mkdir(parents=True, exist_ok=True)
    tmp = pub / f'{g}-janela.mp4'
    preparar.recorte_vertical(base, trilha, tmp, ALTO, POS_ROSTO, None, matriz='709')
    video = pub / f'{g}-h.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(tmp), '-vf', f'pad=1920:1080:{X0}:{Y0}:black', '-an', '-r', '30',
                    '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-g', '30', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video)], check=True)
    tmp.unlink()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(voz), '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k',
                    str(pub / f'{g}-voz.m4a')], check=True)
    dur = min(preparar.duracao(video), preparar.duracao(voz))
    print(f'video: brutos/{g}-h.mp4  voz: brutos/{g}-voz.m4a')
    print(f'rosto: {{x: 960, y: {int(Y0 + POS_ROSTO * ALTO)}}}')
    print(f'duracao: {int(dur * 100) / 100}')
    ws = json.load(open(palavras, encoding='utf-8'))
    print(' '.join(f"{w['w']}@{w['s']:.2f}" for w in ws))


if __name__ == '__main__':
    main(sys.argv[1])
