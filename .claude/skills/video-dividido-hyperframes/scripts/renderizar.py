# -*- coding: utf-8 -*-
"""Renderiza um ou mais formatos e confere o arquivo.

    ./py .claude/skills/video-dividido-hyperframes/scripts/renderizar.py \
        criativo-24 saidas/criativo-24-hyperframes-v1 RL
    ... YT,IN,GL     # só depois do OK do usuário no RL

Saídas: <base>.mp4 (RL) e <base>-YT.mp4 / -IN.mp4 / -GL.mp4. Nunca sobrescreve um arquivo já entregue: use outra
versão na base (v2, v3…). Confere: tamanho do quadro, duração, áudio; no GL, que cada troca pessoa ↔ animação
cai no quadro exato do corte (brilho muda no quadro certo).
"""
import argparse
import json
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
QUADRO = {'RL': (1080, 1920), 'YT': (1920, 1080), 'IN': (1080, 1350), 'GL': (1080, 1080)}
sys.path.insert(0, str(RAIZ / 'hyperframes'))
import cor_pessoa  # noqa: E402   (12/11: REGRA do usuário — a cor da pessoa nunca muda)


def sonda(arq):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height:format=duration',
                          '-of', 'json', str(arq)], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    v = next(s for s in j['streams'] if s['codec_type'] == 'video')
    return v['width'], v['height'], float(j['format']['duration']), any(s['codec_type'] == 'audio' for s in j['streams'])


def conferir_gl(pasta, arq):
    import av
    html = (pasta / 'public/index.html').read_text(encoding='utf-8')
    m = re.findall(r'// (c\d+) \[([\d.]+)–([\d.]+)\]( pessoa)?', html)
    pessoa = {x[0] for x in m if x[3]}
    trocas = [(round(float(m[k][1]) * 30), m[k][0] in pessoa) for k in range(1, len(m))
              if (m[k - 1][0] in pessoa) != (m[k][0] in pessoa)]
    quero = {f for f, _ in trocas} | {f - 1 for f, _ in trocas}
    if not trocas:   # 08/11: GL sem troca pessoa/animação quebrava em max([])
        return 0, []
    fim = max(quero)
    brilho = {}
    c = av.open(str(arq))
    for i, fr in enumerate(c.decode(c.streams.video[0])):
        if i in quero:
            brilho[i] = fr.to_ndarray(format='gray')[100:980].mean()
        if i > fim:
            break
    ruins = [f for f, pra_pessoa in trocas
             if not ((brilho[f] > brilho[f - 1] + 15) if pra_pessoa else (brilho[f] < brilho[f - 1] - 15))]
    return len(trocas), ruins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nome')
    ap.add_argument('base', help='caminho de saída sem extensão, ex.: saidas/criativo-24-hyperframes-v1')
    ap.add_argument('formatos', nargs='?', default='RL')
    ap.add_argument('--icones', default='phosphor')
    ap.add_argument('--sobrescrever', action='store_true')
    ap.add_argument('--crf', type=int, help='compressão (padrão do --quality delivery); 20 pra gravação de celular (~10 Mbps)')
    a = ap.parse_args()
    pasta = RAIZ / 'hyperframes' / a.nome
    # 13/11/2026 (varredura): os recortes da pessoa (public/pessoa*.mp4) são intermediários e podem ir pra Lixeira depois
    # da entrega (regra "sem duplicado"). O pessoa.mp4/-IN/-GL vêm do preparar.py e NENHUM gerar.py recria — sem ele o
    # check acusava missing_local_asset e a fila parava (caso real). Agora, se faltar, o preparar.py roda antes (o
    # gnn sai do configurar(...) do gerar.py; o Extremo gera os dele sozinho e não usa o pessoa.mp4).
    if not (pasta / 'public' / 'pessoa.mp4').exists():
        g = re.search(r"work/([^/'\"]+)/words_cut\.json", (pasta / 'gerar.py').read_text(encoding='utf-8'))
        if g and 'import extremo' not in (pasta / 'gerar.py').read_text(encoding='utf-8'):
            print(f'recortes da pessoa faltando em {a.nome}/public — rodando o preparar.py {g.group(1)} --formatos')
            subprocess.run([PY, str(Path(__file__).with_name('preparar.py')), g.group(1), a.nome, '--formatos'],
                           check=True, env=ENV, stdin=subprocess.DEVNULL)
    for fmt in a.formatos.split(','):
        saida = RAIZ / (f'{a.base}.mp4' if fmt == 'RL' else f'{a.base}-{fmt}.mp4')
        if saida.exists() and not a.sobrescrever:
            sys.exit(f'{saida} já existe — use outra versão (vN+1) ou --sobrescrever se ainda não foi entregue')
        subprocess.run([PY, str(pasta / 'gerar.py'), a.icones, fmt], check=True, env=ENV)
        # 12/11/2026 (REGRA DO USUÁRIO: a cor da pessoa nunca muda): o render do HF extrai os quadros do <video> em JPG e
        # lê o YUV como BT.601 — vídeo em BT.709 saía com a pele amarelada. Converte pra 601 (mesma cor) o que faltar.
        cor_pessoa.garantir(pasta / 'public')
        chk =subprocess.run([NPX, '-y', HF, 'check', 'public'], cwd=pasta, env=ENV, capture_output=True, text=True)
        txt = re.sub(r'\x1b\[[0-9;]*m', '', chk.stdout + chk.stderr)
        if chk.returncode != 0 and not re.search(r'\d+ error\(s\)', txt):   # 08/11: check travou/npx falhou sem relatório
            sys.exit(f'{fmt}: hyperframes check não rodou (código {chk.returncode}): ' + txt.strip()[-300:])
        erros = sum(int(e) for e in re.findall(r'(\d+) error\(s\)', txt))
        # 08/11: na Edição animada, contador girando / calendário virando dá content_overlap durante a animação
        # (falso positivo). Com HF_SOBREPOSICAO_OK=1 esse tipo vira só aviso; a folha de revisão é que confere.
        if os.environ.get('HF_SOBREPOSICAO_OK') == '1':
            sob = len(re.findall(r'content_overlap', txt))
            if sob:
                print(f'{fmt}: {sob} aviso(s) de sobreposição durante animação ignorado(s)')
            erros -= sob
        if erros > 0:
            sys.exit(f'{fmt}: hyperframes check com erro — rode revisar.py e corrija antes de renderizar')
        r = subprocess.run([NPX, '-y', HF, 'render', 'public', '--skill=talking-head-recut', '-o', str(saida),
                            '--fps', '30', '--quality', 'delivery'] + (['--crf', str(a.crf)] if a.crf else []),
                           cwd=pasta, env=ENV, capture_output=True, text=True)
        if r.returncode != 0 or not saida.exists():
            print(re.sub(r'\x1b\[[0-9;]*m', '', r.stdout[-2000:] + r.stderr[-2000:]))
            sys.exit(f'{fmt}: render falhou')
        w, h, dur, audio = sonda(saida)
        ok = (w, h) == QUADRO[fmt] and audio
        print(f'{fmt}: {saida.relative_to(RAIZ)}  {w}x{h}  {dur:.2f}s  áudio={"sim" if audio else "NÃO"}'
              f'  {"ok" if ok else "VERIFICAR"}')
        if fmt == 'GL':
            n, ruins = conferir_gl(pasta, saida)
            print(f'   GL: {n} trocas pessoa/animação, fora do quadro do corte: {ruins or "nenhuma"}')


if __name__ == '__main__':
    main()
