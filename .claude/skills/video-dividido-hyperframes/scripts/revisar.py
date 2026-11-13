# -*- coding: utf-8 -*-
"""Revisão antes de renderizar: gera o formato, roda o `hyperframes check`, fotografa o fim de cada cena,
mede onde o conteúdo do painel começa/termina e monta uma folha de contato pra olhar.

    ./py .claude/skills/video-dividido-hyperframes/scripts/revisar.py criativo-24 [RL|YT|IN|GL] [--em 3.2,9.9]

Saída: hyperframes/<nome>/revisao-<FMT>.png e uma linha por cena "cNN topo-base". No RL o topo do conteúdo
deve ficar em ~y 229 ou mais (regra "nada no alto"; só cena muito alta sobe um pouco) e a base acima da divisória.
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
PY = sys.executable
ENV = dict(os.environ, DO_NOT_TRACK='1', HYPERFRAMES_NO_TELEMETRY='1', PYTHONUTF8='1')
NPX = shutil.which('npx') or 'npx'
HF = 'hyperframes@0.8.76'
# região do painel em cada formato (y0, y1) e limite de baixo quando o título está na tela
PAINEL = {'RL': (0, 955), 'IN': (0, 672), 'GL': (0, 1080), 'YT': (113, 967)}
TITULO_Y = {'RL': 960, 'IN': 675, 'GL': 800}  # centro do título Edits (quando há); no YT ele fica sobre a pessoa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nome')
    ap.add_argument('formato', nargs='?', default='RL')
    ap.add_argument('--icones', default='phosphor')
    ap.add_argument('--em', help='tempos extras (s), separados por vírgula')
    ap.add_argument('--antes', type=float, default=0.08, help='quanto antes do fim da cena fotografar (s); 0.4 pula as transições do arsenal')
    ap.add_argument('--sem-margem', action='store_true', help='Edição animada: pula a checagem de margem segura')
    a = ap.parse_args()
    pasta = RAIZ / 'hyperframes' / a.nome
    subprocess.run([PY, str(pasta / 'gerar.py'), a.icones, a.formato], check=True, env=ENV)
    # 12/11 (REGRA: a cor da pessoa nunca muda): vídeo em BT.709 sai amarelado no render do HF (extração JPG lê 601) e
    # a folha (snapshot, decodificada pelo Chrome) não mostra — converte já aqui (ver hyperframes/cor_pessoa.py)
    sys.path.insert(0, str(RAIZ / 'hyperframes'))
    import cor_pessoa
    cor_pessoa.garantir(pasta / 'public')
    chk =subprocess.run([NPX, '-y', HF, 'check', 'public'], cwd=pasta, env=ENV, capture_output=True, text=True)
    txt = re.sub(r'\x1b\[[0-9;]*m', '', chk.stdout + chk.stderr)
    for l in txt.splitlines():
        if re.search(r'error\(s\)|✗|Check (passed|failed)|⚠ (gsap|font|media|video)', l):
            print('check:', l.strip())

    html = (pasta / 'public/index.html').read_text(encoding='utf-8')
    marcas = re.findall(r'// (c\d+) \[([\d.]+)–([\d.]+)\]( pessoa)?', html)
    tempos = [f'{max(float(ini) + 0.05, float(fim) - a.antes):.2f}' for _, ini, fim, _ in marcas]
    if a.em:
        tempos += a.em.split(',')
    snap = pasta / 'snapshots'
    shutil.rmtree(snap, ignore_errors=True)
    subprocess.run([NPX, '-y', HF, 'snapshot', 'public', '--no-end', '--describe', 'false', '-o', 'snapshots',
                    '--at', ','.join(tempos)], cwd=pasta, env=ENV, capture_output=True, check=True)

    import numpy as np
    from PIL import Image, ImageDraw
    fs = sorted(glob.glob(str(snap / 'frame-*.png')), key=lambda f: int(re.search(r'frame-(\d+)', f).group(1)))
    y0, y1 = PAINEL.get(a.formato, (0, 955))
    m_tit = re.search(r'id="titulo" class="clip" data-start="0" data-duration="([\d.]+)"', html)
    fim_tit = float(m_tit.group(1)) if m_tit else 0.0  # sem título (o padrão desde 29/09)
    medidas = []
    for k, f in enumerate(fs[:len(marcas)]):
        cid, _, _, pessoa = marcas[k]
        if pessoa:
            medidas.append(f'{cid} pessoa')
            continue
        img = np.asarray(Image.open(f).convert('L'))
        x0, x1 = (0, 960) if a.formato == 'YT' else (0, img.shape[1])
        teto = y1 if float(marcas[k][1]) >= fim_tit or a.formato not in TITULO_Y else TITULO_Y[a.formato] - 95
        reg = img[y0:teto, x0:x1]
        linhas = np.where((reg > 60).any(axis=1))[0]
        medidas.append(f'{cid} {linhas.min() + y0}-{linhas.max() + y0}' if len(linhas) else f'{cid} vazio')
    print('conteúdo do painel (y topo-base) no fim de cada cena:')
    print('  ' + ' | '.join(medidas))

    ims = [Image.open(f) for f in fs]
    larg = 300
    alt = int(larg * ims[0].height / ims[0].width)
    cols = 9
    lin = (len(ims) + cols - 1) // cols
    folha = Image.new('RGB', (cols * (larg + 4), lin * (alt + 22)), (40, 40, 40))
    d = ImageDraw.Draw(folha)
    for i, (im, f) in enumerate(zip(ims, fs)):
        x, y = (i % cols) * (larg + 4), (i // cols) * (alt + 22)
        folha.paste(im.resize((larg, alt)), (x, y + 20))
        rot = marcas[i][0] if i < len(marcas) else 'extra'
        d.text((x + 4, y + 4), f"{rot} {re.search(r'at-(.*)s', f).group(1)}s", fill='yellow')
    saida = pasta / f'revisao-{a.formato}.png'
    folha.save(saida)
    print('folha de contato:', saida)
    if a.nome.endswith('-animada') and not a.sem_margem:
        # 08/11 (Edição animada, regra do usuário): texto e peça importante dentro da caixa segura do formato, medido
        # no navegador a cada 0,1 s (câmera, zoom, paralaxe, pico das entradas). Ver hyperframes/checar_margem.py.
        sys.path.insert(0, str(RAIZ / 'hyperframes'))
        import checar_margem
        checar_margem.imprime(a.formato, checar_margem.medir(pasta, a.formato))


if __name__ == '__main__':
    main()
