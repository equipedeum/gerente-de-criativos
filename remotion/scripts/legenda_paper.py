"""Legenda do estilo papel: blocos curtos (unidade de sentido) com o tempo de CADA palavra (karaokê vermelho).

    ./py remotion/scripts/legenda_paper.py work/g28/words_cut.json \
        remotion/src/paper/videos/g28-blocos.txt remotion/src/paper/videos/g28-legenda.json

- blocos.txt: um bloco por linha, texto já revisado (1 a 4 palavras, nunca terminar em artigo/preposição/"que").
  `|` dentro do bloco quebra em duas linhas (só quando não há corte de sentido possível).
- O texto exibido pode corrigir o whisper ("agente" -> "agende", "faça conta" -> "faz a conta"): o alinhamento é
  por sequência (difflib); palavra corrigida herda o tempo do trecho que substituiu, repartido por igual.
- Imprime blocos curtos demais (< 0,28 s pisca) e longos demais (> 22 caracteres por linha) pra revisar.
"""
import difflib
import json
import re
import sys
import unicodedata


def norm(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s.lower())


def main(words_json, blocos_txt, saida):
    ws = [w for w in json.load(open(words_json, encoding='utf-8')) if norm(w['w'])]
    blocos = [l.strip() for l in open(blocos_txt, encoding='utf-8') if l.strip()]
    disp = []  # (bloco, linha, palavra)
    for bi, b in enumerate(blocos):
        for li, linha in enumerate(b.split('|')):
            for p in linha.split():
                disp.append((bi, li, p))
    a = [norm(p) for _, _, p in disp]
    bw = [norm(w['w']) for w in ws]
    tempos = [None] * len(disp)
    sm = difflib.SequenceMatcher(a=a, b=bw, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                tempos[i1 + k] = (ws[j1 + k]['s'], ws[j1 + k]['e'])
        elif i2 > i1:  # 'replace' (palavra corrigida) ou 'delete' (palavra exibida sem correspondente no whisper)
            if j2 > j1:
                s, e = ws[j1]['s'], ws[j2 - 1]['e']
            else:  # sem correspondente: ocupa o vão entre a palavra anterior e a seguinte
                s = ws[j1 - 1]['e'] if j1 > 0 else 0.0
                e = ws[j1]['s'] if j1 < len(ws) else s + 0.2
                if e <= s:
                    e = s + 0.05
            n = i2 - i1
            for k in range(n):
                tempos[i1 + k] = (s + (e - s) * k / n, s + (e - s) * (k + 1) / n)
    out = []
    for bi, b in enumerate(blocos):
        pal = [{'w': disp[k][2], 'l': disp[k][1], 's': round(tempos[k][0], 3), 'e': round(tempos[k][1], 3)}
               for k in range(len(disp)) if disp[k][0] == bi]
        # 15/10: palavra com duração ~0 (whisper) não acende no karaokê -> divide o tempo com a vizinha do mesmo bloco
        for k, p in enumerate(pal):
            if p['e'] - p['s'] < 0.04:
                if k + 1 < len(pal) and pal[k + 1]['e'] - p['s'] >= 0.12:
                    meio = round(p['s'] + (pal[k + 1]['e'] - p['s']) * 0.4, 3); p['e'] = meio; pal[k + 1]['s'] = meio
                elif k > 0 and p['e'] - pal[k - 1]['s'] >= 0.12:
                    meio = round(pal[k - 1]['s'] + (p['e'] - pal[k - 1]['s']) * 0.6, 3); pal[k - 1]['e'] = meio; p['s'] = meio
        out.append({'s': pal[0]['s'], 'e': pal[-1]['e'], 'txt': b, 'palavras': pal})
    for i, b in enumerate(out):
        prox = out[i + 1]['s'] if i + 1 < len(out) else b['e'] + 0.5
        tela = prox - b['s']
        maior = max(len(l) for l in b['txt'].split('|'))
        if tela < 0.28 or maior > 22:
            print(f"revisar: {b['txt']!r} tela={tela:.2f}s maior_linha={maior}", file=sys.stderr)
    json.dump(out, open(saida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(out)} blocos -> {saida}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
