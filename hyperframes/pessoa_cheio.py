# -*- coding: utf-8 -*-
"""Recorte da pessoa em TELA CHEIA vertical (1080x1920) pro RL da tela dividida (26/10/2026, regra do usuário: alternar
tela cheia na pessoa / tela cheia na animação / tela dividida). Janela 9:16 do 16:9 (608x1080 de base_h.mov) seguindo o
rosto na horizontal (face_track.json, suavizado), escalada pra 1080x1920 — o mesmo recorte "A" do básico.
Gera hyperframes/<pasta>/public/pessoa-cheio.mp4 (sem áudio). Uso: python hyperframes/pessoa_cheio.py t83 t83-hf
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cor_pessoa  # noqa: E402   (12/11: REGRA do usuário — a cor da pessoa nunca muda)

RAIZ = Path(__file__).resolve().parents[1]
FF = (RAIZ / 'ferramentas/ffmpeg_path.txt').read_text().strip()
FPS = 30


def video_ok(p):
    """True se o mp4 abre e tem duração (um arquivo cortado no meio não tem o índice 'moov' e falha aqui)."""
    try:
        import av
        with av.open(str(p)) as c:
            return bool(c.streams.video) and (c.duration or 0) > 0
    except Exception:
        return False


_CQ = {}


def cortes_quadros(gnn):
    """12/11/2026 (caso real): quadro EXATO (a 30 fps, o relógio da composição e dos recortes) em que o take novo de cada
    corte seco do tratado aparece. O cortes_visuais.json é aproximado (no t32 dava 20,633 / 54,033: índice da fonte
    29,97 dividido por 30) e o take novo só aparece em 20,667 / 54,100 — usar o .json deixava a pessoa entrar 3 quadros
    no take ANTERIOR e pular pro novo no começo da frase. Aqui acha o pulo de imagem na fonte (±0,6 s em volta de cada
    corte do .json) e devolve round(pts do 1º quadro novo × 30), que é o quadro em que o ffmpeg (-r 30 / fps=30) põe ele."""
    if gnn in _CQ:
        return _CQ[gnn]
    w = RAIZ / 'work' / gnn
    cv = w / 'cortes_visuais.json'
    cortes = sorted(float(c) for c in json.loads(cv.read_text())) if cv.exists() else []
    base = w / 'base_h.mov' if (w / 'base_h.mov').exists() else w / 'base.mov'
    out = []
    for c in cortes:
        n = int(round(c * FPS))
        if base.exists():
            try:
                import av
                with av.open(str(base)) as ct:
                    vs = ct.streams.video[0]
                    ct.seek(int(max(0.0, c - 0.6) / vs.time_base), stream=vs)
                    ant, melhor = None, (0.0, None)
                    for fr in ct.decode(vs):
                        t = float(fr.pts * vs.time_base)
                        if t > c + 0.6:
                            break
                        a = fr.to_ndarray(format='gray')[::8, ::8].astype(np.float32)
                        if ant is not None and t >= c - 0.6:
                            d = float(np.abs(a - ant).mean())
                            if d > melhor[0]:
                                melhor = (d, t)
                        ant = a
                    if melhor[1] is not None and melhor[0] >= 8:
                        n = int(round(melhor[1] * FPS))
            except Exception as e:   # sem a fonte legível: fica o quadro do .json
                print(f'AVISO cortes_quadros({gnn}): {e}')
        out.append(n)
    _CQ[gnn] = out
    return out


def gerar(gnn, pasta, larg=608, saida_wh=(1080, 1920), nome='pessoa-cheio.mp4'):
    """larg: largura da janela no 16:9 (608 = 9:16; 864 = 4:5 pra IN em tela cheia, 27/10)."""
    base = RAIZ / 'work' / gnn / 'base_h.mov'
    pub = RAIZ / 'hyperframes' / pasta / 'public'
    saida = pub / nome
    if saida.exists() and video_ok(saida):
        if not cor_pessoa.ok(saida):   # 12/11: recorte antigo em BT.709 (o render do HF amarelava a pele)
            cor_pessoa.converter(saida)
        return saida
    if saida.exists():   # 09/11 (varredura): recorte pela metade (render interrompido em 07/11) era reaproveitado e o render quebrava
        print(f'AVISO: {saida.name} estava corrompido (gerado pela metade); refazendo')
        saida.unlink()
    if not base.exists() and (RAIZ / 'work' / gnn / 'base.mov').exists():
        return _gerar_vertical(gnn, pub, saida, saida_wh)   # 07/11: fonte de celular vertical (sem base_h.mov)
    trilha = json.load(open(RAIZ / 'work' / gnn / 'face_track.json'))
    dur = float(subprocess.run([FF, '-hide_banner', '-i', str(base)], capture_output=True, text=True).stderr
                .split('Duration: ')[1].split(',')[0].split(':')[2]) + 60 * int(
        subprocess.run([FF, '-hide_banner', '-i', str(base)], capture_output=True, text=True).stderr
        .split('Duration: ')[1].split(':')[1])
    n = int(round(dur * FPS))
    tq = np.arange(n) / FPS
    wmed = float(np.median([p['w'] for p in trilha]))
    boas = [p for p in trilha if p['w'] >= 0.6 * wmed] or trilha
    sig = 0.8 * FPS
    k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2)
    k /= k.sum()
    # 12/11/2026 (caso real, "erro de corte"): a média andava ATRAVÉS do corte seco do tratado — o take novo começava com
    # a janela ainda no lugar do take anterior e ia corrigindo devagar (panorâmica lenta logo depois do corte). Agora a
    # trilha é suavizada POR TAKE (work/<id>/cortes_visuais.json): no corte a janela pula junto com a imagem (escondido
    # pelo próprio corte) e cada take tem a sua câmera. Recortes já gerados não mudam (apague o .mp4 pra refazer).
    lim = [0] + [f for f in cortes_quadros(gnn) if 0 < f < n] + [n]
    cx = np.empty(n)
    for a, b in zip(lim, lim[1:]):
        if b <= a:
            continue
        ps = [p for p in boas if a / FPS <= p['t'] < b / FPS] or boas
        seg = np.interp(tq[a:b], [p['t'] for p in ps], [p['cx'] for p in ps])
        cx[a:b] = np.convolve(np.pad(seg, len(k) // 2, mode='edge'), k, mode='valid')[:b - a]
    x0 = np.clip(cx - larg / 2, 0, 1920 - larg).round().astype(int)
    cmd = saida.with_suffix('.cmd.txt')
    cmd.write_text(''.join(f'{i / FPS:.4f} crop@c x {int(x)};\n' for i, x in enumerate(x0)), encoding='utf-8')
    # 12/11 (REGRA: a cor da pessoa nunca muda): matriz BT.601 pro render do HyperFrames não amarelar a pele (cor_pessoa.py)
    vf = (f"sendcmd=f={cmd.name},crop@c={larg}:1080:{int(x0[0])}:0,scale={saida_wh[0]}:{saida_wh[1]}:flags=lanczos"
          + cor_pessoa.vf(base))
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(base), '-vf', vf, '-an', '-r', str(FPS), '-c:v', 'libx264',
                    '-crf', '18', '-preset', 'medium', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p',
                    *cor_pessoa.ARGS, '-movflags', '+faststart', saida.name], check=True, cwd=str(pub))
    cmd.unlink()
    return saida


def _gerar_vertical(gnn, pub, saida, saida_wh, pos_rosto=None):
    """07/11/2026 (opt-in automático: só quando work/<gnn> não tem base_h.mov e tem base.mov 1620x2880 do
    work/pipeline/preparar.py): largura inteira do vertical, janela na proporção da saída seguindo o rosto na VERTICAL (face_track
    em coordenadas da base, suavizado). 9:16 = quadro inteiro; 4:5 = 1620x2025; 16:9 = 1620x912 (close)."""
    import av
    W, H = saida_wh
    base = RAIZ / 'work' / gnn / 'base.mov'
    jan = min(2880, int(round(1620 * H / W / 2)) * 2)
    if pos_rosto is None:
        # 07/11 (YT da fonte vertical cortava a testa: o rosto ocupa quase toda a janela 16:9): no 16:9 o centro do rosto
        # fica mais embaixo, sobra a testa e o topo da cabeça
        pos_rosto = 0.53 if W > H else 0.38
    c = av.open(str(base))
    vs = c.streams.video[0]
    n = vs.frames or int(round(float(vs.duration * vs.time_base) * FPS))
    c.close()
    tq = np.arange(n) / FPS
    trilha = json.load(open(RAIZ / 'work' / gnn / 'face_track.json'))
    if trilha and jan < 2880:
        wmed = float(np.median([p['w'] for p in trilha]))
        boas = [p for p in trilha if p['w'] >= 0.6 * wmed] or trilha
        cy = np.interp(tq, [p['t'] for p in boas], [p['cy'] for p in boas])
        m = int(0.5 * FPS) | 1
        pad = np.pad(cy, m // 2, mode='edge')
        cy = np.array([np.median(pad[i:i + m]) for i in range(n)])
        sig = 0.8 * FPS
        k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2)
        k /= k.sum()
        cy = np.convolve(np.pad(cy, len(k) // 2, mode='edge'), k, mode='valid')[:n]
    else:
        cy = np.full(n, 2880 * 0.30)
    y0 = np.clip(cy - pos_rosto * jan, 0, 2880 - jan).round().astype(int)
    cmd = saida.with_suffix('.cmd.txt')
    cmd.write_text(''.join(f'{i / FPS:.4f} crop@c y {int(y)};\n' for i, y in enumerate(y0)), encoding='utf-8')
    vf = f"sendcmd=f={cmd.name},crop@c=1620:{jan}:0:{int(y0[0])},scale={W}:{H}:flags=lanczos" + cor_pessoa.vf(base)
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(base), '-vf', vf, '-an', '-r', str(FPS), '-c:v', 'libx264',
                    '-crf', '18', '-preset', 'medium', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p',
                    *cor_pessoa.ARGS, '-movflags', '+faststart', saida.name], check=True, cwd=str(pub))
    cmd.unlink()
    print(f'{saida.name}: vertical 1620x{jan} -> {W}x{H} (y na base {y0.min()}-{y0.max()})')
    return saida


if __name__ == '__main__':
    print(gerar(sys.argv[1], sys.argv[2]))
