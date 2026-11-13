"""Entrega de uma versão: valida e copia os MP4 pra <pasta_entrega>/<código>/ (padrão ~/Desktop/CRIATIVOS/PARA REVISAR).

Uso: ./py work/pipeline/entregar.py "#CR07" <duração_s> RL=<mp4> [IN=<mp4>] [GL=<mp4>] [YT=<mp4>]

- Validação de cada arquivo: decodifica inteiro sem erro, tem vídeo e áudio, resolução certa
  (RL 1080x1920, IN 1080x1350, GL 1080x1080, YT 1920x1080) e duração ±0,3 s da informada. Falhou um -> não entrega nada.
- Nomes: "RL #CR07.mp4", "IN #CR07.mp4"... A pasta é trocada de uma vez; a versão anterior vai pra Lixeira (nunca apaga).
- Marca o código como "revisao" na fila e atualiza a _LISTA.md.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sistema  # noqa: E402

FF = sistema.FF
RES = {'RL': (1080, 1920), 'IN': (1080, 1350), 'GL': (1080, 1080), 'YT': (1920, 1080)}
RUIM = re.compile(r'Invalid NAL|missing picture|Error splitting|corrupt|Invalid data')


def checar(fmt, v, dur):
    p = subprocess.run([FF, '-hide_banner', '-i', v], capture_output=True, text=True, encoding='utf-8',
                       errors='replace').stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', p).groups()
    d = int(h) * 3600 + int(m) * 60 + float(s)
    w, hh = map(int, re.search(r'Video:.*?(\d{3,5})x(\d{3,5})', p).groups())
    erros = []
    if (w, hh) != RES[fmt]:
        erros.append(f'resolução {w}x{hh}')
    if 'Audio:' not in p:
        erros.append('sem áudio')
    if abs(d - dur) > 0.3:
        erros.append(f'duração {d:.2f}s vs {dur:.2f}s')
    dec = subprocess.run([FF, '-v', 'error', '-i', v, '-f', 'null', '-'], capture_output=True, text=True,
                         encoding='utf-8', errors='replace').stderr
    if RUIM.search(dec):
        erros.append('erro de decodificação')
    return d, w, hh, erros


def main():
    cod, dur = sys.argv[1], float(sys.argv[2])
    pares = dict(x.split('=', 1) for x in sys.argv[3:])
    if 'RL' not in pares:
        sys.exit('falta o RL')
    res, falhas = {}, []
    for fmt in ('RL', 'IN', 'GL', 'YT'):
        v = pares.get(fmt)
        if v is None:
            continue
        if not os.path.exists(v):
            falhas.append(f'{fmt}: arquivo não encontrado ({v})')
            continue
        d, w, hh, e = checar(fmt, v, dur)
        res[fmt] = (v, d, w, hh)
        if e:
            falhas.append(f'{fmt}: ' + ', '.join(e))
    if falhas:
        print('NÃO ENTREGUE:\n  ' + '\n  '.join(falhas))
        sys.exit(1)
    DEST = sistema.pasta_entrega()
    DEST.mkdir(parents=True, exist_ok=True)
    pasta, tmp = DEST / cod, DEST / f'.entrando-{cod}'
    if tmp.exists():
        shutil.rmtree(tmp)   # sobra de uma entrega interrompida (é cópia; o original está em saidas/)
    tmp.mkdir()
    for fmt, (v, d, w, hh) in res.items():
        alvo = tmp / f'{fmt} {cod}.mp4'
        shutil.copy2(v, alvo)
        print(f'{fmt} {cod}.mp4  {w}x{hh}  {d:.2f}s  {alvo.stat().st_size / 1e6:.1f} MB')
    if pasta.exists():
        if not sistema.lixeira(pasta):
            print(f'NÃO ENTREGUE: a versão anterior em {pasta} não saiu (algum vídeo aberto?). A nova ficou em {tmp}')
            sys.exit(1)
        print('versão anterior -> Lixeira')
    tmp.rename(pasta)
    print(f'ENTREGUE em {pasta}')
    subprocess.run([sys.executable, str(sistema.RAIZ / 'work/pipeline/fila.py'), 'marcar', cod, 'revisao'], check=False)


if __name__ == '__main__':
    main()
