"""Prepara um vídeo pro estilo papel (Editor Paper) a partir do material já cortado e transcrito em work/<id>/.

    ./py remotion/scripts/preparar_paper.py g28

Duas origens (mesmas do preparar.py da skill video-dividido-hyperframes):
- Estúdio 16:9: work/<id>/base_h.mov (1920x1080 já cortado) + voice.wav + words_cut.json.
  Gera <id>-h.mp4 (sem áudio; cópia se já for h264). No VideoPapel: `rosto` = o que este script imprime.
- Celular vertical (sem base_h.mov): work/<id>/base.mov (1620x2880, saída do work/pipeline/preparar.py) + face_track.json
  + voice.wav + words_cut.json. Gera <id>-metade.mp4 já recortado em 1080x980, janela seguindo o rosto na vertical
  (suavizada; rosto a 40 % da altura). No VideoPapel: `recortado: true`.
Sempre gera <id>-voz.m4a (loudnorm -16) em remotion/public/brutos/ e imprime a duração e a transcrição com tempos.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / '.claude/skills/video-dividido-hyperframes/scripts'))
import preparar  # noqa: E402  (detectar_rosto, duracao, recorte_vertical)


def main(g):
    src = RAIZ / 'work' / g
    voz, palavras = src / 'voice.wav', src / 'words_cut.json'
    vertical = not (src / 'base_h.mov').exists()
    base = src / ('base.mov' if vertical else 'base_h.mov')
    exigidos = (base, voz, palavras) + ((src / 'face_track.json',) if vertical else ())
    for f in exigidos:
        if not f.exists():
            sys.exit(f'falta {f} — rode antes ./py work/pipeline/preparar.py {g} <vídeo>')
    pub = RAIZ / 'remotion' / 'public' / 'brutos'
    pub.mkdir(parents=True, exist_ok=True)
    if vertical:
        saida = pub / f'{g}-metade.mp4'
        preparar.recorte_vertical(base, src / 'face_track.json', saida, 980, 0.40, None, matriz='709')
        print(f'video: brutos/{saida.name}  (recortado: true)')
        # YT/IN/GL: janela com o rosto mais alto (legenda fora do queixo); RL nos 3 modos: o vertical inteiro pra pessoa cheia
        m45 = pub / f'{g}-metade45.mp4'
        preparar.recorte_vertical(base, src / 'face_track.json', m45, 980, 0.45, None, matriz='709')
        cheio = pub / f'{g}-cheio.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(base), '-an', '-vf', 'scale=1080:1920:flags=lanczos',
                        '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30',
                        '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                        '-movflags', '+faststart', str(cheio)], check=True)
        trilha = json.load(open(src / 'face_track.json'))
        ys = sorted(p_['cy'] for p_ in trilha)
        ry = round(ys[len(ys) // 2] * 1920 / 2880) if ys else 760
        print(f"no VideoPapel: recortado: true, rosto: {{x: 540, y: 392}}, formatosVideo: {{video: 'brutos/{m45.name}', rostoY: 441}},")
        print(f"               cheioVertical: {{video: 'brutos/{cheio.name}', rostoY: {ry}}}")
    else:
        codec = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'csv=p=0', str(base)],
                               capture_output=True, text=True).stdout.strip()
        video = pub / f'{g}-h.mp4'
        v = ['-c:v', 'copy'] if codec == 'h264' else ['-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30']
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(base), '-an', *v, '-movflags', '+faststart', str(video)], check=True)
        rosto = preparar.detectar_rosto(base)
        print(f'video: brutos/{video.name}')
        print(f'rosto: {{x: {round(rosto[0]) if rosto else 960}, y: {round(rosto[1]) if rosto else 360}}}{"" if rosto else "  (NÃO DETECTADO: conferir num quadro)"}')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(voz), '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k',
                    str(pub / f'{g}-voz.m4a')], check=True)
    dur = min(preparar.duracao(base), preparar.duracao(voz))
    print(f'voz: brutos/{g}-voz.m4a')
    print(f'duracao: {int(dur * 100) / 100}')
    ws = json.load(open(palavras, encoding='utf-8'))
    print(' '.join(f"{w['w']}@{w['s']:.2f}" for w in ws))


if __name__ == '__main__':
    main(sys.argv[1])
