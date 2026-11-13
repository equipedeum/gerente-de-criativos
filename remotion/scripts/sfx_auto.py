"""Lê as cenas de um vídeo do estilo papel e gera remotion/src/paper/videos/<id>-auto.json com:
- `sfx`: efeitos sonoros no instante de cada animação (regra de 08/10/2026: sons baixinhos aprovados no Criativo 52);
- `pessoaGL`: trechos em que o GL (1080x1080) mostra a pessoa em tela cheia — desde 13/10/2026 cada trecho é UMA FRASE
  INTEIRA da legenda (do início ao ponto/vírgula final), 2–4 por vídeo, fora do gancho e do CTA; aceita esconder
  algumas animações do papel (escolhe as frases que escondem menos). Ver trechos_gl().

    ./py remotion/scripts/sfx_auto.py b53b

Mapa de sons: troca de seção = papel; entrada "carimbo"/Bate = carimbo no impacto (+0,13 s); "cai" = papel;
"desliza" = whoosh; Cartao/Cupom = papel baixo; pop padrão = pop; Seta/Xis = whoosh; tClique = clique; tCorte = tesoura;
tCheck/Check = tique; AoVivo = ping. Keyframe de `move` não faz som (08/11/2026).
Os NOMES são os mesmos nos dois kits; a pasta sai do PaperVideo (`KIT_SFX`: public/sfx-earshot/ desde 08/11/2026,
scripts/sfx_earshot.py; os vídeos que já existiam seguem em public/sfx/). Som só onde o papel aparece: o PaperVideo
deixa mudo a pessoa cheio do RL e os trechos pessoaGL/inserto do GL e do IN-como-GL. Sons a menos de 0,25 s um do outro: fica o mais forte; pops a menos de 0,45 s
do som anterior saem (não metralhar).
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SEM_SOM = {'papel'}   # 12/10/2026: usuário achou o farfalhar de papel "muito ruim" (caso real) — vetado em todos os vídeos
PRIO = {'carimbo': 7, 'tesoura': 6, 'clique': 5, 'papel': 4, 'tique': 3, 'whoosh': 2, 'ping': 2, 'pop': 1}


def num(expr):
    """'45.5 + i * 0.07' -> (45.5, 0.07); '12.3' -> (12.3, 0)."""
    m = re.match(r'\s*([\d.]+)\s*(?:\+\s*i\s*\*\s*([\d.]+))?', expr)
    return (float(m.group(1)), float(m.group(2) or 0)) if m else (None, 0)


GL_MIN, GL_MAX, GL_ALVO = 2.5, 7.5, 4.5   # duração de uma frase com a pessoa em tela cheia no GL (s)
GL_QTD, GL_ESPACO = 3, 6.0                 # quantos trechos (2–4 por vídeo) e folga mínima entre eles (s)
INSERTOS = []                              # (s, e) do inserto da plataforma no vídeo atual (lido do .tsx em main)


def unidades(leg):
    """Trechos de fala que podem ir pro GL: uma frase inteira (do 1º bloco até o que fecha com . ? !) ou uma sequência
    de orações dela que começa no início da frase ou logo depois de uma vírgula e termina numa vírgula ou no ponto —
    nunca começa nem termina no meio de uma oração. Devolve (índices dos blocos, é_frase_inteira)."""
    frases, ini = [], 0
    for i, b in enumerate(leg):
        if re.search(r'[.?!…]["”]?$', b['txt'].strip()) or i == len(leg) - 1:
            frases.append(list(range(ini, i + 1)))
            ini = i + 1
    out = []
    for f in frases:
        cortes = [k for k, i in enumerate(f) if leg[i]['txt'].strip().endswith(',')]
        inis = [0] + [k + 1 for k in cortes if k + 1 < len(f)]
        fins = cortes + [len(f) - 1]
        for a in inis:
            for z in fins:
                if z >= a:
                    out.append((f[a:z + 1], a == 0 and z == len(f) - 1))
    return out


def trechos_gl(leg, vis, secoes):
    """GL (13/10/2026, usuário: "pode deixar uma frase inteira"): 2–4 trechos, cada um cobrindo uma frase inteira (ou
    orações inteiras dela, até a vírgula/ponto): início do 1º bloco − 0,2 s até o fim do último + 0,15 s. Fora do gancho
    (2 primeiras seções, quando o vídeo tem ≥ 6) e do CTA (2 últimas seções). Escolhe os que escondem menos animações
    (uma animação só se perde se a seção dela acaba < 1 s depois do trecho; senão ela continua no papel quando volta),
    preferindo frase inteira e duração perto de GL_ALVO, espaçados entre si. secoes = [(s, e), ...]."""
    ss = [s for s, _ in secoes]
    de = ss[2] if len(ss) >= 6 else (ss[1] if len(ss) > 1 else 0)
    ate = ss[-2] if len(ss) >= 4 else 1e9
    cta = [b['s'] for b in leg if re.search(r'\bclica\b|^se a sua empresa|^cada mês', b['txt'].strip(), re.I)]   # 3 aberturas de CTA do lote   # 14/10: nunca em cima do "clica no link"
    if cta:
        ate = min(ate, cta[0] - 0.5)

    def fim_secao(x):
        return max([e for s, e in secoes if s <= x] or [1e9])

    cands = []
    for u, inteira in unidades(leg):
        i0, i1 = u[0], u[-1]
        s, e = leg[i0]['s'], leg[i1]['e']
        if not (GL_MIN <= e - s <= GL_MAX) or s < de - 0.3 or e > ate + 0.3:
            continue
        if any(s < b + 0.5 and e > a - 0.5 for a, b in INSERTOS):   # 14/10: nunca em cima do inserto da plataforma
            continue
        ini = max(s - 0.2, leg[i0 - 1]['e'] + 0.02 if i0 > 0 else 0)
        fim = min(e + 0.15, leg[i1 + 1]['s'] - 0.02 if i1 + 1 < len(leg) else e + 0.15)
        perdidas = sum(1 for x in vis if ini + 0.3 < x < fim - 0.3 and fim_secao(x) < fim + 1.0)
        cands.append(((perdidas, 0 if inteira else 1, abs(e - s - GL_ALVO)), round(ini, 2), round(fim, 2)))
    escolhidos = []
    for _, ini, fim in sorted(cands):
        if len(escolhidos) >= GL_QTD:
            break
        if all(fim + GL_ESPACO <= a or ini >= b + GL_ESPACO for a, b in escolhidos):
            escolhidos.append([ini, fim])
    return sorted(escolhidos)


def main(vid):
    src = (RAIZ / f'remotion/src/paper/videos/{vid}.tsx').read_text(encoding='utf-8')
    leg = json.load(open(RAIZ / f'remotion/src/paper/videos/{vid}-legenda.json', encoding='utf-8'))
    linhas = src.split('\n')
    ev = []  # (t, som, vol)
    vis = []  # instantes em que algo novo aparece no papel (pra escolher as pausas do GL)
    for i, ln in enumerate(linhas):
        prox = linhas[i + 1] if i + 1 < len(linhas) else ''
        m = re.search(r'<Secao s=\{([\d.]+)\}', ln)
        if m:
            t = float(m.group(1))
            if t > 0:
                ev.append((t, 'papel', 1.0))
            vis.append(t)
        m = re.search(r'<Peca\b.*?\bt=\{([^}]+)\}', ln)
        if m:
            t, passo = num(m.group(1))
            if t is not None:
                ent = re.search(r'entrada="(\w+)"', ln)
                ent = ent.group(1) if ent else 'pop'
                vis += [t, t + 2 * passo]
                filho = re.search(r'<(\w+)', prox)
                filho = filho.group(1) if filho else ''
                if ent == 'carimbo':
                    ev.append((t + 0.13, 'carimbo', 1.0))
                elif ent == 'cai':
                    ev.append((t, 'papel', 0.8))
                elif ent == 'desliza':
                    ev.append((t, 'whoosh', 1.0))
                elif ent in ('cresce', 'fade', 'revela'):
                    ev.append((t, 'pop', 0.45))
                elif ent == 'nada':
                    if filho == 'Cupom':
                        ev.append((t, 'papel', 0.8))
                elif filho in ('Cartao', 'Cupom'):
                    ev.append((t, 'papel', 0.7))
                elif filho == 'AoVivo':
                    ev.append((t, 'ping', 0.8))
                else:
                    ev.append((t, 'pop', 0.8))
        for pad, som, vol, mais in [(r'<Seta\b.*?\bt0=\{([\d.]+)\}', 'whoosh', 1.0, 0), (r'<Xis t0=\{([\d.]+)\}', 'whoosh', 0.9, 0),
                                    (r'tClique=\{([\d.]+)\}', 'clique', 1.0, 0), (r'tCorte=\{([\d.]+)\}', 'tesoura', 1.0, 0),
                                    (r'tCheck=\{([\d.]+)\}', 'tique', 1.0, 0), (r'<Check t0=\{([\d.]+)\}', 'tique', 1.0, 0),
                                    (r'<Bate t0=\{([\d.]+)\}', 'carimbo', 0.8, 0.13), (r'<ItemLista t=\{([\d.]+)\}', 'pop', 0.5, 0),
                                    (r'<Msg t=\{([\d.]+)\}', 'pop', 0.7, 0)]:
            for m in re.finditer(pad, ln):
                t = float(m.group(1)) + mais
                ev.append((t, som, vol))
                vis.append(float(m.group(1)))
        # itens de arrays de objetos: {t: 37.1, ...}
        for m in re.finditer(r'\{t: ([\d.]+),', ln):
            vis.append(float(m.group(1)))

    # objetos {t: ...} que viram Peca via .map: um pop pra cada. 08/11/2026: tira antes os keyframes de `move={[...]}`
    # (a peça só se mexe, nada novo aparece — o regex antigo dava pop em cada passo de move).
    sem_move = re.sub(r'move=\{\[[^\]]*\]\}', '', src)
    for m in re.finditer(r'\{t: ([\d.]+), (?:x|y|ic)\b', sem_move):
        ev.append((float(m.group(1)), 'pop', 0.7))

    ev = [e for e in ev if e[1] not in SEM_SOM]   # sons vetados pelo usuário
    ev.sort()
    final = []
    for t, som, vol in ev:
        if final and t - final[-1][0] < 0.25:
            if PRIO[som] > PRIO[final[-1][1]]:
                final[-1] = (t, som, vol)
            continue
        if som == 'pop' and final and t - final[-1][0] < 0.45:
            continue
        final.append((t, som, vol))
    sfx = [{'t': round(t, 2), 'som': s, **({'vol': v} if v != 1.0 else {})} for t, s, v in final]

    global INSERTOS
    INSERTOS = [(float(a), float(b)) for a, b in re.findall(r'inserto:\s*\{s:\s*([\d.]+),\s*e:\s*([\d.]+)', src)]
    pessoa = trechos_gl(leg, sorted(set(round(x, 2) for x in vis)), [(float(a), float(b)) for a, b in re.findall(r'<Secao s=\{([\d.]+)\} e=\{([\d.]+)\}', src)])
    out = RAIZ / f'remotion/src/paper/videos/{vid}-auto.json'
    json.dump({'sfx': sfx, 'pessoaGL': pessoa}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    dur = sum(b - a for a, b in pessoa)
    print(f'{vid}: {len(sfx)} sons; GL com a pessoa em {len(pessoa)} trechos ({dur:.1f} s) -> {out.name}')
    print('  GL:', ', '.join(f'{a:.1f}-{b:.1f}' for a, b in pessoa))


if __name__ == '__main__':
    for v in sys.argv[1:]:
        main(v)
