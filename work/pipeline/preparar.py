"""Preparo de um vídeo bruto para todos os editores (vertical de celular ou horizontal 16:9).

Uso:
    ./py work/pipeline/preparar.py <id> <vídeo> [--sem-corte] [--mao] [--sem-tratar-audio]

    <id>                nome curto, sem espaço (ex.: v01, aula3, demo) — vira a pasta work/<id>/
    --sem-corte         o vídeo já veio editado: não corta as pausas
    --mao               gravação na mão/selfie: só corta pausas longas e para antes da última pausa (quando a pessoa
                        estica o braço pra parar a gravação)
    --sem-tratar-audio  não passa o filtro de voz (o áudio já veio tratado)

Gera em work/<id>/:
    base.mov            vertical 1620x2880 (celular)    OU    base_h.mov  horizontal 1920x1080
    voice.wav           voz 48 kHz mono (tratada: filtro de ruído leve + compressor + loudnorm -16 LUFS)
    voice16k.wav        16 kHz mono (transcrição)
    words_cut.json      palavras com tempo [{w, s, e, p}] (faster-whisper small, local)
    cuts.json           {"segs": [[ini, fim], ...], "total": dur, "sil": [...], "dur": dur_do_bruto}
    face_track.json     [{t, cx, cy, w}] rosto em pixels do base (1 a cada 3 quadros)

Regras que valem aqui:
- A COR DA PESSOA NUNCA MUDA: o vídeo é só cortado/redimensionado, sem filtro de cor.
- Corte só dentro de silêncio de verdade (cortar_silencios.py), nunca em cima da fala.
- Nunca mexe no arquivo original (brutos/ é só leitura).
Imprime a duração, a largura do rosto, a transcrição e os "BURACO COM VOZ" (trecho que o whisper pulou).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ / 'work'))
import sistema  # noqa: E402
from cortar_silencios import conferir, detectar_silencios_relativo, montar_segmentos  # noqa: E402

FF = sistema.FF


def ff(*a):
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', *a], check=True)


def sonda(arq):
    out = subprocess.run([sistema.FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=width,height,color_transfer:stream_side_data=rotation:format=duration', '-of', 'json', str(arq)],
                         capture_output=True, text=True, encoding='utf-8').stdout
    j = json.loads(out or '{}')
    s = (j.get('streams') or [{}])[0]
    w, h = int(s.get('width', 0)), int(s.get('height', 0))
    rot = 0
    for sd in s.get('side_data_list', []) or []:
        if 'rotation' in sd:
            rot = int(float(sd['rotation']))
    if abs(rot) in (90, 270):   # celular grava deitado e marca rotação: o ffmpeg já gira ao decodificar
        w, h = h, w
    hdr = s.get('color_transfer', '') in ('arib-std-b67', 'smpte2084')   # iPhone grava HDR (HLG/Dolby Vision) por padrão
    return w, h, float(j.get('format', {}).get('duration', 0)), hdr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('id')
    ap.add_argument('video')
    ap.add_argument('--sem-corte', action='store_true')
    ap.add_argument('--mao', action='store_true')
    ap.add_argument('--sem-tratar-audio', action='store_true')
    a = ap.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', a.id):
        sys.exit('id só com letras, números, - e _ (sem espaço)')
    SRC = str(Path(a.video).resolve())
    D = RAIZ / 'work' / a.id
    D.mkdir(parents=True, exist_ok=True)
    W0, H0, DUR, HDR = sonda(SRC)
    vertical = H0 > W0
    print(f'{a.id}: {W0}x{H0} ({"vertical" if vertical else "horizontal"}), {DUR:.2f} s')

    # 1. pausas (relativas ao piso de ruído da gravação; corte só dentro do silêncio)
    ff('-i', SRC, '-vn', '-ac', '1', '-ar', '16000', str(D / 'voz16k_bruto.wav'))
    sil = detectar_silencios_relativo(str(D / 'voz16k_bruto.wav'), dur_min=0.20, fator=0.42)
    if a.sem_corte:
        segs, total = [[0.0, DUR]], DUR
    else:
        ini = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
        fim = sil[-1][0] if sil and sil[-1][1] > DUR - 0.1 else DUR
        if a.mao:
            longas = [x for x in sil if x[1] - x[0] >= 0.8 and x[1] > DUR - 4.0]
            if longas:
                fim = min(fim, longas[0][0])
            segs, total = montar_segmentos(sil, DUR, ini, fim, margem=0.10, pausa_alvo=0.40, min_remover=0.50,
                                           entrada=0.20, saida=0.20)
        else:
            segs, total = montar_segmentos(sil, DUR, ini, fim, margem=0.07, pausa_alvo=0.12, min_remover=0.10,
                                           entrada=0.20, saida=0.45)
        ruins = conferir(segs, sil)
        assert not ruins, ruins
    json.dump({'segs': segs, 'total': total, 'sil': sil, 'dur': DUR}, open(D / 'cuts.json', 'w'))
    print(f'{a.id}: {DUR:.2f} s -> {total:.2f} s ({len(segs)} trechos, tirou {DUR - total:.1f} s de pausa)')

    # 2. base cortada, SEM filtro de cor (a cor da pessoa nunca muda)
    if vertical:
        Wb, Hb, nome = 1620, 2880, 'base.mov'      # 1620x2880 deixa dar zoom 1,3–1,5 sem perder nitidez
    else:
        Wb, Hb, nome = 1920, 1080, 'base_h.mov'
    # HDR (iPhone com 'HDR' ligado na câmera): converte pra SDR BT.709 com tone mapping, senão a pele fica lavada/cinza.
    # Não é "mexer na cor": é mostrar a gravação como ela aparece no celular. Sem o zscale no ffmpeg, avisa.
    tm = ''
    if HDR:
        filtros = subprocess.run([FF, '-hide_banner', '-filters'], capture_output=True, text=True).stdout
        if ' zscale ' in filtros and ' tonemap ' in filtros:
            tm = ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,'
                  'zscale=t=bt709:m=bt709:r=tv,')
            print('vídeo HDR: convertendo pra SDR (BT.709) com tone mapping')
        else:
            print('ATENÇÃO: vídeo HDR e o ffmpeg não tem zscale — a cor pode sair lavada. No iPhone: Ajustes > Câmera > '
                  'Gravar Vídeo > desligue "Vídeo HDR" (ou instale um ffmpeg com zimg).')
    n = len(segs)
    vf = ''.join(f'[0:v]trim=start={x}:end={y},setpts=PTS-STARTPTS[v{i}];' for i, (x, y) in enumerate(segs))
    af = ''.join(f'[0:a]atrim=start={x}:end={y},asetpts=PTS-STARTPTS,afade=t=in:d=0.010,'
                 f'afade=t=out:st={max(0, y - x - 0.010)}:d=0.010[a{i}];' for i, (x, y) in enumerate(segs))
    cat = (''.join(f'[v{i}][a{i}]' for i in range(n)) + f'concat=n={n}:v=1:a=1[vc][a];'
           f'[vc]{tm}scale={Wb}:{Hb}:force_original_aspect_ratio=increase,crop={Wb}:{Hb},setsar=1,format=yuv420p[v]')
    for velho in ('base.mov', 'base_h.mov'):
        if (D / velho).exists():
            (D / velho).unlink()   # intermediário refeito (o original está em brutos/)
    ff('-i', SRC, '-filter_complex', vf + af + cat, '-map', '[v]', '-map', '[a]', '-r', '30',
       '-c:v', 'libx264', '-preset', 'fast', '-crf', '14', '-pix_fmt', 'yuv420p',
       '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
       '-c:a', 'pcm_s16le', str(D / nome))
    filtro = [] if a.sem_tratar_audio else [
        '-af', 'highpass=f=90,afftdn=nr=10:nf=-34,lowpass=f=12000,'
               'acompressor=threshold=-20dB:ratio=2.5:attack=8:release=140:makeup=3,loudnorm=I=-16:TP=-1.5:LRA=9']
    ff('-i', str(D / nome), '-vn', '-ac', '1', '-ar', '48000', *filtro, str(D / 'voice.wav'))
    ff('-i', str(D / 'voice.wav'), '-ac', '1', '-ar', '16000', str(D / 'voice16k.wav'))
    (D / 'voz16k_bruto.wav').unlink()

    # 3. transcrição do áudio já cortado (tempos na linha do tempo final)
    from faster_whisper import WhisperModel
    pj = sistema.projeto()
    dica = '. '.join(x for x in (pj.get('nome_pessoa'), pj.get('marca'), pj.get('termos_transcricao')) if x)
    mdl = WhisperModel('small', device='cpu', compute_type='int8', download_root=str(RAIZ / 'models'),
                       local_files_only=True)
    segw, _ = mdl.transcribe(str(D / 'voice16k.wav'), language='pt', word_timestamps=True, beam_size=5,
                             vad_filter=False, initial_prompt=os.environ.get('PREP_PROMPT') or dica or None)
    W = [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3), 'p': round(w.probability, 2)}
         for sg in segw for w in sg.words]
    json.dump(W, open(D / 'words_cut.json', 'w', encoding='utf-8'), ensure_ascii=False)

    # 4. rosto (Haar do OpenCV, 1 a cada 3 quadros)
    import av
    import cv2
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    c = av.open(str(D / nome))
    vs = c.streams.video[0]
    vs.thread_type = 'AUTO'
    pw, ph = (405, 720) if vertical else (960, 540)
    sx, sy = Wb / pw, Hb / ph
    out, last, k = [], None, 0
    for fr in c.decode(vs):
        if k % 3 == 0:
            t = float(fr.pts * vs.time_base)
            sm = cv2.resize(fr.to_ndarray(format='gray'), (pw, ph))
            f = casc.detectMultiScale(sm, 1.1, 4, minSize=(40, 40))
            if len(f):
                x, y, w, hh = max(f, key=lambda r: r[2] * r[3])
                last = (int((x + w / 2) * sx), int((y + hh / 2) * sy), int(w * sx))
            if last:
                out.append({'t': round(t, 3), 'cx': last[0], 'cy': last[1], 'w': last[2]})
        k += 1
    c.close()
    if not out:
        print('ATENÇÃO: nenhum rosto achado; usando o centro do quadro (ajustar o enquadramento no cfg)')
        out = [{'t': 0.0, 'cx': Wb // 2, 'cy': int(Hb * 0.4), 'w': Hb // 6}]
    json.dump(out, open(D / 'face_track.json', 'w'))
    ws = [o['w'] for o in out]
    print(f'{a.id}: {total:.2f} s | {len(W)} palavras | rosto: largura mediana {int(np.median(ws))} de {Wb}')
    print(' '.join(w['w'] for w in W))

    # 5. buracos: > 1,2 s sem palavra mas com voz (o whisper às vezes pula uma frase inteira)
    au = wave.open(str(D / 'voice16k.wav'))
    sr = au.getframerate()
    amos = np.frombuffer(au.readframes(au.getnframes()), np.int16).astype(np.float32)
    lim = [(0.0, W[0]['s'])] if W else []
    lim += [(x['e'], y['s']) for x, y in zip(W, W[1:])] + ([(W[-1]['e'], total)] if W else [])
    ref = np.sqrt(np.mean(amos ** 2)) or 1
    for x, y in lim:
        if y - x > 1.2:
            seg = amos[int((x + 0.15) * sr):int((y - 0.15) * sr)]
            if len(seg) and np.sqrt(np.mean(seg ** 2)) > 0.35 * ref:
                print(f'BURACO COM VOZ: {x:.2f}–{y:.2f} s (retranscrever esse trecho)')


if __name__ == '__main__':
    main()
