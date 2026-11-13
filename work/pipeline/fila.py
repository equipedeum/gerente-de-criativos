"""Fila e códigos dos criativos (sem planilha): cada versão entregue ganha um código #CRnn (prefixo em projeto.json).
Estado em work/pipeline/estado.json — a fila é a verdade, não a memória (depois de compactar o contexto: `status`).

Uso: ./py work/pipeline/fila.py <comando> ...
    novo <id> <estilo> "<título>"     reserva o próximo código pra uma versão (estilo: basico, hyperframe, paper, vox,
                                     extremo, animada, viral...) e imprime o código
    status                           tudo, por status
    ver <código>                     detalhes de um código
    marcar <código> <etapa> [nota]   etapa: montagem | revisao_legenda | render | conferencia | revisao (entregue) | ajuste
    nota <código> "texto"            guarda uma observação
    ajuste <código> "o que mudar"    o usuário pediu alteração: tira a versão de PARA REVISAR (vai pra Lixeira) e marca ajuste
    aprovar <código>                 OK do usuário: move a pasta de PARA REVISAR pra APROVADOS
    descartar <código>               descartado: pasta pra Lixeira (nunca apaga de vez) e marca descartado
"""
import datetime
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sistema  # noqa: E402

EST = sistema.RAIZ / 'work/pipeline/estado.json'


def carregar():
    if EST.exists():
        return json.loads(EST.read_text(encoding='utf-8'))
    return {'proximo': 1, 'videos': {}}


def salvar(e):
    tmp = EST.with_suffix('.tmp')
    tmp.write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding='utf-8')
    tmp.replace(EST)


def agora():
    return datetime.datetime.now().strftime('%d/%m %H:%M')


def norm(c):
    pre = sistema.projeto()['prefixo_codigo']
    c = c.strip()
    if c.isdigit():
        return f'#{pre}{int(c):02d}'
    return c if c.startswith('#') else '#' + c


def hist(v, txt):
    v.setdefault('historico', []).append(f'{agora()} {txt}')


def lista_revisar():
    import subprocess
    subprocess.run([sys.executable, str(sistema.RAIZ / 'work/pipeline/lista_revisar.py')], check=False)


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    e = carregar()
    cmd = a[0]
    if cmd == 'novo':
        id_, estilo, titulo = a[1], a[2], ' '.join(a[3:])
        cod = f"#{sistema.projeto()['prefixo_codigo']}{e['proximo']:02d}"
        e['proximo'] += 1
        e['videos'][cod] = {'id': id_, 'estilo': estilo, 'titulo': titulo, 'status': 'montagem'}
        hist(e['videos'][cod], 'reservado')
        salvar(e)
        print(cod)
    elif cmd == 'status':
        por = {}
        for cod, v in e['videos'].items():
            por.setdefault(v['status'], []).append(f"{cod} {v['titulo']} [{v['estilo']}] ({v['id']})")
        for st in ('montagem', 'revisao_legenda', 'render', 'conferencia', 'ajuste', 'revisao', 'aprovado', 'descartado'):
            if st in por:
                print(f'== {st} ({len(por[st])})')
                print('\n'.join('  ' + x for x in por.pop(st)))
        for st, xs in por.items():
            print(f'== {st} ({len(xs)})')
            print('\n'.join('  ' + x for x in xs))
        if not e['videos']:
            print('fila vazia')
    elif cmd == 'ver':
        print(json.dumps(e['videos'].get(norm(a[1]), {}), ensure_ascii=False, indent=1))
    elif cmd in ('marcar', 'nota', 'ajuste', 'aprovar', 'descartar'):
        cod = norm(a[1])
        v = e['videos'].get(cod)
        if not v:
            sys.exit(f'{cod} não existe na fila')
        pasta = sistema.pasta_entrega() / cod
        if cmd == 'marcar':
            v['status'] = a[2]
            hist(v, a[2] + (' — ' + ' '.join(a[3:]) if a[3:] else ''))
        elif cmd == 'nota':
            v.setdefault('notas', []).append(' '.join(a[2:]))
            hist(v, 'nota')
        elif cmd == 'ajuste':
            # REGRA: pediu alteração = a versão antiga sai de PARA REVISAR na hora (lá só fica o que dá pra revisar)
            if pasta.exists() and not sistema.lixeira(pasta):
                sys.exit(f'não consegui mandar {pasta} pra Lixeira (vídeo aberto?)')
            v['status'] = 'ajuste'
            v.setdefault('ajustes', []).append(' '.join(a[2:]))
            hist(v, 'ajuste pedido: ' + ' '.join(a[2:]))
        elif cmd == 'aprovar':
            dest = pasta.parent.parent / 'APROVADOS' / cod
            if pasta.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    sistema.lixeira(dest)
                shutil.move(str(pasta), str(dest))
                print(f'-> {dest}')
            v['status'] = 'aprovado'
            hist(v, 'aprovado')
        elif cmd == 'descartar':
            if pasta.exists() and not sistema.lixeira(pasta):
                sys.exit(f'não consegui mandar {pasta} pra Lixeira (vídeo aberto?)')
            v['status'] = 'descartado'
            hist(v, 'descartado')
        salvar(e)
        print(f"{cod} {v['status']}")
        if cmd in ('ajuste', 'aprovar', 'descartar') or (cmd == 'marcar' and a[2] == 'revisao'):
            lista_revisar()
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
