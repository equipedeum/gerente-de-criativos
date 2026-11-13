"""Gera <pasta_entrega>/_LISTA.md: o que está em PARA REVISAR agora (a partir das pastas que existem de verdade),
com título e estilo de cada código vindos da fila. Rodar depois de cada entrega, aprovação, ajuste ou descarte.

    ./py work/pipeline/lista_revisar.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sistema  # noqa: E402


def main():
    dest = sistema.pasta_entrega()
    if not dest.exists():
        print('nada em PARA REVISAR')
        return
    est = sistema.RAIZ / 'work/pipeline/estado.json'
    vids = json.loads(est.read_text(encoding='utf-8'))['videos'] if est.exists() else {}
    linhas = []
    for p in sorted(x for x in dest.iterdir() if x.is_dir() and not x.name.startswith('.')):
        v = vids.get(p.name, {})
        fmts = ' '.join(f for f in ('RL', 'IN', 'GL', 'YT') if (p / f'{f} {p.name}.mp4').exists())
        linhas.append(f"- **{p.name}** — {v.get('titulo', '?')} [{v.get('estilo', '?')}] — {fmts}")
    txt = '# Para revisar\n\n' + ('\n'.join(linhas) if linhas else '(vazio)') + \
          '\n\nResponda com "#CRnn ok", "#CRnn: <o que mudar>" ou "#CRnn descarta".\n'
    (dest / '_LISTA.md').write_text(txt, encoding='utf-8')
    print(txt)


if __name__ == '__main__':
    main()
