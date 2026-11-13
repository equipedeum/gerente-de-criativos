# -*- coding: utf-8 -*-
"""Checagem de MARGEM SEGURA da Edição animada (08/11/2026).

Regra do usuário: "o que é animação importante ou escrita na tela tem que estar dentro da margem". Caixa segura:
  RL 1080x1920: x 100–980, y 220–1500 (a interface do Reels/TikTok cobre o alto e o pé);
  IN 1080x1350: x 100–980, y 80–1270;   GL 1080x1080 e YT (painel 1080x1080 à esquerda): x 100–980, y 80–1000.
12/11/2026 (regra do usuário: texto nunca lá em cima — o Instagram tampa —, nunca baixo demais, nunca no rosto): TEXTO
tem caixa própria — RL y 320–1500, IN y 225–1270, GL/YT y 180–1000 (CAIXA_TEXTO no .mjs).
Vale pra TODO texto visível (letreiro, capítulo, data, rótulo, balão, etiqueta, placa, manchete, número) e pra toda peça
marcada `data-imp` (o objeto que carrega a ideia: celular, carteira, gráfico, infográfico...). Cenário de fundo pode
sangrar (decoração). Mede no navegador, com câmera/zoom/paralaxe e o pico das entradas, a cada 0,1 s de cada cena.

    ./py hyperframes/checar_margem.py t68-animada RL,IN,GL,YT [--passo 0.1]
    (sem formato = os 4; `--sem-gerar` usa o index.html que já está em public/)

Saída: uma linha por elemento fora (cena, texto/peça, quanto passou e de que lado, de quando a quando) e o total.
Amostras em que o TEMA inteiro está mexido por uma transição (chicote, zoom, empurrão de entrada) contam à parte
("em transição") — só o resto é erro. Também usado pelo revisar.py nos projetos *-animada.
"""
import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MJS = RAIZ / 'hyperframes/checar_margem.mjs'
ENV = dict(os.environ, DO_NOT_TRACK='1', HYPERFRAMES_NO_TELEMETRY='1', PYTHONUTF8='1')


_RUNNER = r"""
import os, runpy, sys
alt = os.environ['MARGEM_MOTOR']
class L(list):
    def insert(self, i, x):
        if os.path.basename(os.path.normpath(str(x))) == 'hyperframes':
            return super().insert(1, x)
        return super().insert(i, x)
sys.path = L([alt] + sys.path)
g = sys.argv[1]
sys.argv = [g] + sys.argv[2:]
runpy.run_path(g, run_name='__main__')
"""


def gerar(pasta, fmt):
    """Gera o index.html do formato. MARGEM_MOTOR=<pasta irmã de hyperframes/ com cópia dos .py do motor> usa essa
    cópia (pra medir o 'antes' enquanto o motor é editado)."""
    if os.environ.get('MARGEM_MOTOR'):
        cmd = [sys.executable, '-c', _RUNNER, str(pasta / 'gerar.py'), 'phosphor', fmt]
    else:
        cmd = [sys.executable, str(pasta / 'gerar.py'), 'phosphor', fmt]
    subprocess.run(cmd, check=True, env=ENV, stdout=subprocess.DEVNULL)


def medir(pasta, fmt, passo=0.1):
    saida = pasta / f'margem-{fmt}.json'
    r = subprocess.run(['node', str(MJS), str(pasta / 'public'), fmt, str(saida), str(passo)],
                       capture_output=True, text=True, encoding='utf-8', env=ENV)
    if r.returncode != 0:
        raise RuntimeError(f'checar_margem.mjs falhou ({fmt}):\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}')
    return json.loads(saida.read_text(encoding='utf-8'))


def resumo(j):
    """Agrupa as amostras por (cena, elemento): pior estouro, intervalo de tempo. Devolve (erros, em_transicao)."""
    g = defaultdict(lambda: {'n': 0, 't0': 99e9, 't1': -1, 'fora': {}, 'trans': True, 'rots': []})
    for a in j['achados']:
        # um ELEMENTO = a peça/etiqueta com id (os textos de dentro dela — dias da agenda, palavras — contam juntos)
        k = (a['cena'], 'peca' if a['tipo'] == 'peca' else 'texto', a['el'] or a['rot'], '')
        x = g[k]
        if a['rot'] not in x['rots']:
            x['rots'].append(a['rot'])
        x['n'] += 1
        x['t0'], x['t1'] = min(x['t0'], a['t']), max(x['t1'], a['t'])
        x['trans'] = x['trans'] and a['trans']
        if not a['trans'] or x['trans']:
            for lado, v in a['fora'].items():
                x['fora'][lado] = max(x['fora'].get(lado, 0), v)
    erros = {k: v for k, v in g.items() if not v['trans']}
    trans = {k: v for k, v in g.items() if v['trans']}
    return erros, trans


def imprime(fmt, j, detalhe=True):
    erros, trans = resumo(j)
    # 12/11 (regra do usuário): texto tem caixa própria, mais longe do topo (CAIXA_TEXTO do checar_margem.mjs)
    print(f'MARGEM {fmt}: {len(erros)} elemento(s) fora da caixa segura {j["caixa"]}'
          + (f' / texto {j["caixa_texto"]}' if j.get('caixa_texto') else '')
          + (f' (+{len(trans)} só durante transição)' if trans else ''))
    if detalhe:
        for (cena, tipo, el, _), v in sorted(erros.items()):
            rot = ' '.join(v['rots'])[:44]
            lados = ', '.join(f'{k} {v_}px' for k, v_ in v['fora'].items())
            print(f'  {cena} {tipo:5s} {rot!r:44s} [{el}] {lados}  ({v["t0"]:.2f}–{v["t1"]:.2f}s, {v["n"]} amostras)')
    return len(erros), len(trans)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nome')
    ap.add_argument('formatos', nargs='?', default='RL,IN,GL,YT')
    ap.add_argument('--passo', type=float, default=0.1)
    ap.add_argument('--sem-gerar', action='store_true')
    ap.add_argument('--trans', action='store_true', help='lista também o que só sai durante transição')
    a = ap.parse_args()
    pasta = RAIZ / 'hyperframes' / a.nome
    tot = {}
    for fmt in a.formatos.split(','):
        if not a.sem_gerar:
            gerar(pasta, fmt)
        j = medir(pasta, fmt, a.passo)
        tot[fmt] = imprime(fmt, j)
        if a.trans:
            for (cena, tipo, el, _), v in sorted(resumo(j)[1].items()):
                print(f'    (trans) {cena} {el} {v["rots"][:3]!r} {v["fora"]} {v["t0"]:.2f}–{v["t1"]:.2f}')
    print('TOTAL ' + ' '.join(f'{f}={e}' for f, (e, _) in tot.items()))


if __name__ == '__main__':
    main()
