# -*- coding: utf-8 -*-
"""Copia os formatos aprovados pra Área de Trabalho no padrão do usuário:
    Desktop/<pasta principal>/<título>/RL <título>.mp4  (IN, GL, YT idem)

    ./py .claude/skills/video-dividido-hyperframes/scripts/exportar.py \
        saidas/criativo-24-hyperframes-v1 "Se a empresa para quando você para" --pasta "Editados IA 25-09"

Sem --pasta, usa "Editados IA <dd-mm de hoje>". Copia (não move): os originais ficam em saidas/.
Só leva os formatos que existirem (<base>.mp4 = RL, <base>-YT/-IN/-GL.mp4).
"""
import argparse
import datetime
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base', help='ex.: saidas/criativo-24-hyperframes-v1')
    ap.add_argument('titulo', help='título da pasta e dos arquivos (a frase de abertura / título do Edits)')
    ap.add_argument('--pasta', help='pasta principal na Área de Trabalho')
    a = ap.parse_args()
    titulo = re.sub(r'[\\/:*?"<>|]', '', a.titulo).strip()  # nomes válidos no Windows/ExFAT
    pasta = a.pasta or f'Editados IA {datetime.date.today():%d-%m}'
    destino = Path.home() / 'Desktop' / pasta / titulo
    destino.mkdir(parents=True, exist_ok=True)
    feitos = []
    for fmt, suf in [('RL', ''), ('IN', '-IN'), ('GL', '-GL'), ('YT', '-YT')]:
        src = RAIZ / f'{a.base}{suf}.mp4'
        if src.exists():
            shutil.copy2(src, destino / f'{fmt} {titulo}.mp4')
            feitos.append(fmt)
    if not feitos:
        sys.exit(f'nenhum arquivo encontrado para {a.base}')
    print(f'{destino}: ' + ', '.join(feitos))


if __name__ == '__main__':
    main()
