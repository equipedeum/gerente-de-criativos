# -*- coding: utf-8 -*-
"""Infográficos, metáforas visuais e cartelas do arsenal (07/11/2026). Desenham na camada de ação (bo._amb) e devolvem ''.
Número SÓ o que ele falou. Texto de peça ≥ 48 px, a ≥ 170 px das laterais.

Infográficos: pizza, grafico_linha, contador (dígitos rolando), fluxo, mapa_rotas, mapa_mancha, funil, pictograma,
              balanca, antes_depois, grade_objetos
Metáforas:    iceberg, malabarista, domino, escada, foguete, barco_furado, engrenagens, cabo_guerra, semente, torre_blocos,
              ima, lampada, corrida, relogio_rapido, janelas, construcao
Cartelas:     pincel (sublinhado de tinta na cartela preta), nome (etiqueta de personagem com fio), selo_canto (lugar/
              hora no canto de cima), definicao (placa gravada), manchete (jornal pregado), placa_valor, numeros, carimbo
"""
import html as _html
import math
import random

import animada as an
import bonecos as bo
import motor
from bonecos import (_T, _amb, _balao, _entra_amb, _etiqueta, _fim, _pop_balao, _seed, _txt_larg, anda, corpo, gesticula,
                     muda_pose, pos, respira, vive)
from motor import q

__all__ = ['pizza', 'grafico_linha', 'contador', 'fluxo', 'mapa_rotas', 'mapa_mancha', 'funil', 'pictograma', 'balanca',
           'antes_depois', 'grade_objetos', 'iceberg', 'malabarista', 'domino', 'escada', 'foguete', 'barco_furado',
           'engrenagens', 'cabo_guerra', 'semente', 'torre_blocos', 'ima', 'lampada', 'corrida', 'relogio_rapido',
           'janelas', 'construcao', 'pincel', 'nome', 'selo_canto', 'definicao', 'manchete', 'placa_valor', 'numeros',
           'carimbo', 'citacao', 'linha_tempo', 'mao_escreve']

TINTA = '#2A1D12'


def _x(x, txt, tam=48, extra=0):
    meia = (_txt_larg(txt.upper(), tam) + extra + 40) / 2
    return min(max(x, 230 + meia), 850 - meia)   # 230 = 100 de margem + passeio do piso + zoom lento (medido no t138)


def _tag(gid, x, y, txt, cor='#FBF4E4', tinta='#1E2A3A', tam=48, rot=0, livre=False):
    """Etiqueta animável (#gid no <g> de dentro, sem transform). livre=True dentro de peça encaixada (bo.encaixa):
    a peça inteira é que vai pra caixa segura, a etiqueta fica no lugar dela."""
    return _etiqueta(x if livre else _x(x, txt, tam), y, txt, tam, cor, tinta, rot=rot, eid=gid, livre=livre)


def _pop(c, gid, t, som='pop2'):
    c.a(f"tl.fromTo('#{gid} .bp',{{opacity:0,scale:0.4,transformOrigin:'50% 50%'}},{{opacity:1,scale:1,duration:0.32,ease:'back.out(2)',transformOrigin:'50% 50%'}},{q(t)});")
    if som:
        an.som(t, som, 0.2)


def _ts(tempos, n, t, passo=0.6):
    return [_T(x) for x in tempos] if tempos else [t + 0.3 + passo * k for k in range(n)]


# ================================================================ INFOGRÁFICOS
def pizza(c, t, fatias, tempos=None, titulo='', centro=(540, 1380), r=300):
    """Pizza desenhando fatia por fatia, com o % contando no rótulo. fatias = [('Com IA', 80), ('Time', 20)] (só o
    falado; a soma é 100). Bom no 'pergaminho', 'preto', 'escritorio2'."""
    t = _T(t)
    w = an._id(c, 'pz')
    cx, cy = centro
    ts_ = _ts(tempos, len(fatias), t, 0.8)
    cores = ('#B5523B', '#2D4A63', '#C9A24A', '#5B7F6E')
    out = [f'<circle cx="{cx}" cy="{cy + 14}" r="{r}" fill="#000" opacity=".15"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="#E9DFC6"/>']
    acum = 0
    rr = r / 2
    cx0, cy0, cx1, cy1 = cx - r - 30, cy - r - (110 if titulo else 30), cx + r + 30, cy + r + 30   # caixa do que importa
    for k, (rot, val) in enumerate(fatias):
        sid = f'{w}-f{k}'
        out.append(f'<circle id="{sid}" cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{cores[k % 4]}" stroke-width="{r}" '
                   f'pathLength="100" stroke-dasharray="0 100" transform="rotate({-90 + 3.6 * acum:.1f} {cx} {cy})"/>')
        c.a(f"tl.fromTo('#{sid}',{{attr:{{'stroke-dasharray':'0 100'}}}},{{attr:{{'stroke-dasharray':'{val} 100'}},duration:0.7,ease:'power2.out'}},{q(ts_[k])});")
        meio = math.radians(-90 + 3.6 * (acum + val / 2))
        lx, ly = cx + (r + 190) * math.cos(meio), cy + (r + 150) * math.sin(meio)
        lx = _x(lx, f'{rot} {val}%', 52)
        ly = min(max(ly, 990), 1840)
        lw_ = max(_txt_larg(f'{val}%', 76), _txt_larg(rot.upper(), 48)) / 2 + 10
        cx0, cx1, cy0, cy1 = min(cx0, lx - lw_), max(cx1, lx + lw_), min(cy0, ly - 75), max(cy1, ly + 75)
        vid = f'{w}-v{k}'
        out.append(f'<g transform="translate({lx:.0f} {ly:.0f})"><g id="{vid}"><text class="tc" x="0" y="0" text-anchor="middle" font-size="76" fill="{cores[k % 4]}" id="{vid}-n">0%</text>'
                   f'<text class="tc" x="0" y="54" text-anchor="middle" font-size="48" fill="{TINTA}">{_html.escape(rot.upper())}</text></g></g>')
        c.a(f"tl.fromTo('#{vid}',{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3}},{q(ts_[k])});")
        c.a(f"conta('#{vid}-n',0,{val},{q(ts_[k])},0.7,'%');")
        an.som(ts_[k], 'marimba', 0.18)
        acum += val
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.18:.0f}" fill="#F3E6C6"/>')
    c.a(f"tl.fromTo('#{w}-g',{{rotation:-4}},{{rotation:4,duration:2,yoyo:true,repeat:{max(1, int((_fim(c) - t) / 2))},ease:'sine.inOut',svgOrigin:'{cx} {cy}'}},{q(t)});")
    if titulo:
        out.insert(0, f'<text class="tc" x="540" y="{cy - r - 60}" text-anchor="middle" font-size="56" fill="{TINTA}">{_html.escape(titulo.upper())}</text>')
    _entra_amb(c, w, t)
    # 08/11 (margem segura): pizza + rótulos + título encaixam juntos (o rótulo da fatia de baixo ia até y ~1800)
    return _amb(c, bo.encaixa(f'<g id="{w}"><g id="{w}-g">{"".join(out)}</g></g>', (cx0, cy0, cx1, cy1)))


def grafico_linha(c, t, valores=(20, 35, 30, 55, 70, 90), rotulos=(), titulo='', desce=False, t_linha=None, marcar=None):
    """Gráfico de LINHA desenhando (pergaminho ou parede clara): a linha corre, a área enche, o ponto vai na ponta;
    desce=True inverte e pinta de vermelho. valores = formato da curva (não aparece número); rotulos = embaixo (ex.:
    ('Jan', 'Jun')) só se falados; marcar=(índice, 'texto', t) põe uma bandeirinha num ponto."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'gl')
    X0, X1, Y0, Y1 = 190, 900, 1020, 1680
    vs = list(valores)
    if len(vs) < 2:   # 08/11: 1 valor só dava divisão por zero
        vs = vs * 2
    if desce:
        vs = vs[::-1]
    mx = max(vs) or 1
    P = [(X0 + 40 + (X1 - X0 - 80) * k / (len(vs) - 1), Y1 - 30 - (Y1 - Y0 - 80) * v / mx) for k, v in enumerate(vs)]
    cor = '#B03A2A' if desce else '#3F7F55'
    d = 'M' + ' '.join(f'{x:.0f} {y:.0f}' if k == 0 else f'L{x:.0f} {y:.0f}' for k, (x, y) in enumerate(P))
    out = [f'<path d="M{X0} {Y0} L{X0} {Y1} L{X1} {Y1}" stroke="{TINTA}" stroke-width="6" fill="none"/>']
    out += [f'<path d="M{X0} {y:.0f} L{X1} {y:.0f}" stroke="#8A6A3A" stroke-width="2" stroke-dasharray="6 9" opacity=".5"/>' for y in (Y0 + 100, Y0 + 260, Y0 + 420)]
    out.append(f'<path id="{w}-a" d="{d} L{P[-1][0]:.0f} {Y1} L{P[0][0]:.0f} {Y1}Z" fill="{cor}" opacity="0"/>')
    out.append(f'<path id="{w}-l" d="{d}" stroke="{cor}" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1 1"/>')
    out.append(f'<g id="{w}-p"><circle r="18" fill="{cor}"/><circle r="34" fill="{cor}" opacity=".25"/></g>')
    for k, rot in enumerate(rotulos):
        x = P[0][0] if k == 0 else P[-1][0]
        out.append(f'<text class="tc" x="{x:.0f}" y="{Y1 + 64}" text-anchor="middle" font-size="48" fill="{TINTA}">{_html.escape(rot.upper())}</text>')
    if titulo:
        out.append(f'<text class="tc" x="{X0}" y="{Y0 - 40}" font-size="56" fill="{TINTA}">{_html.escape(titulo.upper())}</text>')
    tl_ = _T(t_linha) if t_linha is not None else t + 0.3
    dur = max(0.8, min(2.6, t1 - tl_ - 0.3))
    c.a(f"tl.fromTo('#{w}-l',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{dur:.2f},ease:'power1.inOut'}},{q(tl_)});")
    c.a(f"tl.to('#{w}-a',{{opacity:0.18,duration:{dur:.2f}}},{q(tl_)});")
    c.a(f"tl.set('#{w}-p',{{x:{P[0][0]:.0f},y:{P[0][1]:.0f}}},{q(c.t0)});")
    seg = dur / (len(P) - 1)
    for k in range(1, len(P)):
        c.a(f"tl.to('#{w}-p',{{x:{P[k][0]:.0f},y:{P[k][1]:.0f},duration:{seg:.2f},ease:'none'}},{q(tl_ + seg * (k - 1))});")
    c.a(f"tl.fromTo('#{w}-p',{{scale:1}},{{scale:1.35,duration:0.3,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.3))}}},{q(c.t0)});")
    an.som(tl_, 'riser' if not desce else 'sub', 0.14)
    if marcar:
        i, txt, tm = marcar
        gid = f'{w}-m'
        x, y = P[i]
        out.append(f'<path d="M{x:.0f} {y:.0f} L{x:.0f} {y - 150:.0f}" stroke="{TINTA}" stroke-width="4"/>' + _tag(gid, _x(x, txt), y - 190, txt, '#F2B544', livre=True))
        _pop(c, gid, _T(tm))
    _entra_amb(c, w, t)
    # 08/11 (margem segura): o gráfico inteiro (eixos, rótulos, bandeirinha) encaixa abaixo do letreiro e acima do pé
    y_top = min(Y0 - (100 if titulo else 40), (P[marcar[0]][1] - 240) if marcar else 9e9)
    return _amb(c, bo.encaixa(f'<g id="{w}">{"".join(out)}</g>', (X0 - 30, y_top, X1 + 30, Y1 + (90 if rotulos else 20))))


def contador(c, t, ate, de=0, sufixo='', rotulo='', dur=1.3, y=1300, cor=None, tam=230, rolo=True):
    """Número GRANDE contando (estilo da referência: os dígitos rolam como caça-níquel e assentam), com a legenda em
    versalete embaixo e um fio de ouro abrindo. Só número falado. y = centro (cabe de 1000 a 1700)."""
    t = _T(t)
    w = an._id(c, 'cn')
    cor = cor or ('#F2B544' if not an.TEMAS.get(an.CEN.get(c.id, ('dia',))[0], (True,))[0] else '#3A2A1A')
    fmt = (lambda v: f'{int(v):,}'.replace(',', '.'))
    txt_fim = fmt(ate) + sufixo
    out = [f'<text class="tg" id="{w}-n" x="540" y="{y}" text-anchor="middle" font-size="{tam}" fill="{cor}">{_html.escape(fmt(de) + sufixo)}</text>']
    if rotulo:
        out.append(f'<rect id="{w}-f" x="390" y="{y + 165}" width="300" height="5" fill="#C9A24A"/>'
                   f'<text class="tc" id="{w}-r" x="540" y="{y + 130}" text-anchor="middle" font-size="60" fill="{cor}" letter-spacing="4">{_html.escape(rotulo.upper())}</text>')
        c.a(f"tl.fromTo('#{w}-f',{{scaleX:0}},{{scaleX:1,duration:0.4,svgOrigin:'540 {y + 167}'}},{q(t + 0.2)});")
        c.a(f"tl.fromTo('#{w}-r',{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.35}},{q(t + 0.35)});")
    c.a(f"tl.fromTo('#{w}-n',{{opacity:0,scale:1.15}},{{opacity:1,scale:1,duration:0.3,svgOrigin:'540 {y}'}},{q(t)});")
    if rolo:
        # dígitos "rolando": número aleatório trocando rápido e desacelerando até o valor
        c.a(f"(function(){{const el=document.querySelector('#{w}-n');const o={{v:0}};tl.to(o,{{v:1,duration:{dur},ease:'power3.out',onUpdate:function(){{"
            f"const p=o.v;const alvo={ate};const de={de};if(p>=0.999){{el.textContent='{txt_fim}';return;}}"
            f"const base=Math.round(de+(alvo-de)*p);const ruido=Math.round((1-p)*Math.abs(alvo-de)*0.35*Math.sin(p*97));"
            f"el.textContent=(Math.max(0,base+ruido)).toLocaleString('pt-BR')+'{sufixo}';}}}},{q(t)});}})();")
    else:
        c.a(f"conta('#{w}-n',{de},{ate},{q(t)},{dur},'{sufixo}');")
    for k in range(5):
        an.som(t + 0.12 * k, 'tique', 0.12)
    an.som(t + dur, 'impacto', 0.26)
    c.a(f"tl.fromTo('#{w}-n',{{y:0}},{{y:-8,duration:1.2,yoyo:true,repeat:{max(1, int((_fim(c) - t) / 1.2))},ease:'sine.inOut'}},{q(t + dur)});")
    _entra_amb(c, w, t)
    # 08/11 (margem segura): número + legenda encaixam juntos (a legenda ia até y+175, 18 px abaixo do pé do RL)
    lw_ = max(_txt_larg(txt_fim, tam, 'serif') * 1.15, _txt_larg(rotulo.upper(), 60) + 4 * len(rotulo) if rotulo else 0)
    return _amb(c, bo.encaixa(f'<g id="{w}">{"".join(out)}</g>', (540 - lw_ / 2, y - tam * 0.95, 540 + lw_ / 2, y + (215 if rotulo else 80))))   # + entrada em escala 1,15


def fluxo(c, t, etapas, tempos=None, vertical=True, icones=None):
    """Processo em etapas: cartões ligados por setas que se desenham, e uma bolinha dourada percorrendo o caminho
    em loop. etapas = ['Anúncio', 'IA atende', 'Reunião'] (2–4). Vertical (y 980–1840) ou horizontal (2–3 etapas)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'fx')
    n = len(etapas)
    ts_ = _ts(tempos, n, t, 0.6)
    out, pts = [], []
    if vertical:
        passo = min(260, 860 / max(1, n))
        for k, e in enumerate(etapas):
            y = 1000 + passo * k + passo / 2
            pts.append((540, y))
    else:
        for k, e in enumerate(etapas):
            pts.append((260 + 560 * k / max(1, n - 1), 1400))
    for k in range(n - 1):
        (ax, ay), (bx, by) = pts[k], pts[k + 1]
        sid = f'{w}-s{k}'
        if vertical:
            d = f'M{ax} {ay + 50} L{bx} {by - 50}'
        else:
            d = f'M{ax + 90} {ay} L{bx - 90} {by}'
        out.append(f'<path id="{sid}" d="{d}" stroke="{TINTA}" stroke-width="8" fill="none" stroke-dasharray="1 1" pathLength="1"/>'
                   f'<path d="{d}" stroke="none" fill="none"/>')
        c.a(f"tl.fromTo('#{sid}',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.4,ease:'power1.inOut'}},{q(ts_[k + 1] - 0.3)});")
    for k, e in enumerate(etapas):
        x, y = pts[k]
        tam = 52
        while _txt_larg(e.upper(), tam) > (560 if vertical else 240) and tam > 48:
            tam -= 2
        lw = max(220, _txt_larg(e.upper(), tam) + 80)
        gid = f'{w}-e{k}'
        cor = '#B5523B' if k == n - 1 else '#FBF4E4'
        tinta = '#FBF6EA' if k == n - 1 else '#1E2A3A'
        out.append(f'<g transform="translate({x:.0f} {y:.0f})"><g id="{gid}"><g class="bp"><rect x="{-lw / 2:.0f}" y="-44" width="{lw:.0f}" height="96" rx="20" fill="#000" opacity=".16"/>'
                   f'<rect x="{-lw / 2:.0f}" y="-52" width="{lw:.0f}" height="96" rx="20" fill="{cor}"/>'
                   f'<text class="tc" x="0" y="{tam * 0.36 - 4:.0f}" text-anchor="middle" font-size="{tam}" fill="{tinta}">{_html.escape(e.upper())}</text></g></g></g>')
        _pop(c, gid, ts_[k], 'pop2')
    bol = f'<g id="{w}-b" opacity="0"><circle r="16" fill="#F2B544"/><circle r="28" fill="#F2B544" opacity=".3"/></g>'
    c.a(f"tl.set('#{w}-b',{{x:{pts[0][0]},y:{pts[0][1]}}},{q(c.t0)});tl.to('#{w}-b',{{opacity:1,duration:0.2}},{q(ts_[-1])});")
    tt = ts_[-1]
    j = 0
    while tt < t1 - 0.3:
        k = j % n
        nx, ny = pts[(k + 1) % n] if k + 1 < n else pts[0]
        c.a(f"tl.to('#{w}-b',{{x:{nx:.0f},y:{ny:.0f},duration:{0.5 if k + 1 < n else 0.01},ease:'power1.inOut'}},{q(tt)});")
        tt += 0.55 if k + 1 < n else 0.05
        j += 1
    _entra_amb(c, w, t)
    # 08/11 (margem segura): os cartões encaixam juntos abaixo do letreiro e acima do pé do formato
    if vertical:
        cx_ = (540 - 340, pts[0][1] - 70, 540 + 340, pts[-1][1] + 70)
    else:
        cx_ = (130, 1330, 950, 1470)
    return _amb(c, bo.encaixa(f'<g id="{w}">{"".join(out)}{bol}</g>', cx_))


def _terra(rnd, cx, cy, rx, ry, n=22):
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        f = rnd.uniform(0.78, 1.12)
        pts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))
    d = 'M' + ' '.join(f'{(pts[k][0] + pts[(k + 1) % n][0]) / 2:.0f} {(pts[k][1] + pts[(k + 1) % n][1]) / 2:.0f} Q{pts[(k + 1) % n][0]:.0f} {pts[(k + 1) % n][1]:.0f}' for k in range(n))
    d = d.replace(' Q', ' Q', 1)
    # path com curvas suaves: M m0 Q p1 m1 Q p2 m2 ...
    seq = []
    for k in range(n):
        m = ((pts[k][0] + pts[(k + 1) % n][0]) / 2, (pts[k][1] + pts[(k + 1) % n][1]) / 2)
        seq.append((pts[(k + 1) % n], ((pts[(k + 1) % n][0] + pts[(k + 2) % n][0]) / 2, (pts[(k + 1) % n][1] + pts[(k + 2) % n][1]) / 2)))
    m0 = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
    d = f'M{m0[0]:.0f} {m0[1]:.0f} ' + ' '.join(f'Q{p[0]:.0f} {p[1]:.0f} {m[0]:.0f} {m[1]:.0f}' for p, m in seq[1:] + seq[:1]) + 'Z'
    return d


def mapa_rotas(c, t, destino, origens, tempos=None, icone='pessoa'):
    """Mapa FICTÍCIO (terra creme, mar azul, à moda da referência): várias rotas pontilhadas saindo de origens e
    CONVERGINDO no destino, com bonequinhos/moedas andando por elas. destino = ('Sua empresa', x, y); origens =
    [('Anúncio', x, y), ...] (x 170–910, y 980–1840). Cenário 'pergaminho' (ou 'preto'). Nunca lugar real."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'mr')
    rnd = random.Random(_seed(c.id) + 91)
    out = ['<rect x="-300" y="940" width="1680" height="980" fill="#7FA6B5"/>',
           f'<path d="{_terra(rnd, 540, 1400, 520, 380)}" fill="#EAD9B0" stroke="#8A6A3A" stroke-width="4"/>',
           f'<path d="{_terra(rnd, 1230, 1100, 170, 120, 14)}" fill="#EAD9B0" stroke="#8A6A3A" stroke-width="4"/>',
           f'<path d="{_terra(rnd, -150, 1750, 200, 140, 14)}" fill="#EAD9B0" stroke="#8A6A3A" stroke-width="4"/>']
    out += [f'<path d="M{rnd.uniform(120, 900):.0f} {rnd.uniform(1100, 1700):.0f} l{rnd.uniform(-60, 60):.0f} {rnd.uniform(-60, 60):.0f}" stroke="#8A6A3A" stroke-width="3" opacity=".4"/>' for _ in range(10)]
    out += [f'<path d="M{x} {y} l14 -24 l14 24Z" fill="#B9A276"/>' for x, y in ((300, 1200), (330, 1215), (700, 1600), (730, 1590), (760, 1610))]
    out += [f'<path class="ar-onda" d="M{x} {y} q20 -10 40 0 q20 10 40 0" stroke="#FFFFFF" stroke-width="3" fill="none" opacity=".5"/>' for x, y in ((-200, 1000), (980, 1500), (100, 1880), (1000, 1820))]
    dn, dx, dy = destino
    ts_ = _ts(tempos, len(origens), t, 0.55)
    for k, (nm, ox, oy) in enumerate(origens):
        rid = f'{w}-r{k}'
        mx_, my_ = (ox + dx) / 2 + rnd.uniform(-90, 90), (oy + dy) / 2 + rnd.uniform(-90, 90)
        d = f'M{ox} {oy} Q{mx_:.0f} {my_:.0f} {dx} {dy}'
        out.append(f'<path id="{rid}" d="{d}" stroke="#B5523B" stroke-width="7" fill="none" stroke-dasharray="2 14" stroke-linecap="round"/>'
                   f'<path id="{rid}m" d="{d}" stroke="#EAD9B0" stroke-width="12" fill="none" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="0"/>')
        c.a(f"tl.fromTo('#{rid}m',{{strokeDashoffset:0}},{{strokeDashoffset:-1,duration:0.7,ease:'power1.inOut'}},{q(ts_[k])});")
        pid = f'{w}-o{k}'
        out.append(f'<g id="{pid}"><circle cx="{ox}" cy="{oy}" r="16" fill="#2D4A63"/>' + _tag(pid + 't', ox, oy - 60, nm, '#FBF4E4') + '</g>')
        _pop(c, pid + 't', ts_[k], 'pop2')
        # viajante andando na rota em loop
        vid = f'{w}-v{k}'
        figura = ('<circle r="13" fill="#F2B544" stroke="#2A1D12" stroke-width="4"/>' if icone == 'moeda' else
                  '<circle cy="-18" r="9" fill="#2A1D12"/><rect x="-8" y="-8" width="16" height="22" rx="6" fill="#2A1D12"/>')
        out.append(f'<g id="{vid}" opacity="0">{figura}</g>')
        c.a(f"tl.set('#{vid}',{{x:{ox},y:{oy},opacity:1}},{q(ts_[k] + 0.6)});")
        tt = ts_[k] + 0.6
        while tt < t1 - 0.2:
            c.a(f"tl.fromTo('#{vid}',{{x:{ox},y:{oy}}},{{keyframes:{{x:[{ox},{(ox + mx_) / 2 * 0.5 + (mx_ + dx) / 2 * 0.5:.0f},{dx}],y:[{oy},{(oy + my_) / 2 * 0.5 + (my_ + dy) / 2 * 0.5:.0f},{dy}]}},duration:1.4,ease:'none',immediateRender:false}},{q(tt)});")
            tt += 1.5
    gd = f'{w}-d'
    out.append(f'<g id="{gd}"><path d="M{dx} {dy} C{dx - 36} {dy - 46} {dx - 40} {dy - 80} {dx} {dy - 106} C{dx + 40} {dy - 80} {dx + 36} {dy - 46} {dx} {dy}Z" fill="#3F7F55"/>'
               f'<circle cx="{dx}" cy="{dy - 72}" r="15" fill="#FBF6EA"/></g>' + _tag(gd + 't', dx, dy - 160, dn, '#B5523B', '#FBF6EA'))
    c.a(f"tl.fromTo('#{gd}',{{y:-140,opacity:0}},{{y:0,opacity:1,duration:0.45,ease:'bounce.out'}},{q(t)});")
    _pop(c, gd + 't', t + 0.2, '')
    c.a(f"tl.fromTo('#{gd}',{{scale:1}},{{scale:1.12,duration:0.4,yoyo:true,repeat:{max(1, int((t1 - t) / 0.4))},svgOrigin:'{dx} {dy}'}},{q(t + 0.5)});")
    an.som(t, 'papel', 0.18)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}</g>')


def mapa_mancha(c, t, origem=(540, 1400), rotulo='', t_rotulo=None, cor='#3A2A20'):
    """Mapa fictício em que uma mancha de tinta se ESPALHA a partir de um ponto (boca a boca, a marca crescendo,
    o problema se alastrando). Cenário 'pergaminho'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'mm')
    rnd = random.Random(_seed(c.id) + 92)
    ox, oy = origem
    out = ['<rect x="-300" y="940" width="1680" height="980" fill="#7FA6B5"/>',
           f'<clipPath id="{w}-cp"><path d="{_terra(rnd, 540, 1420, 560, 400)}"/></clipPath>',
           f'<path d="{_terra(random.Random(_seed(c.id) + 92), 540, 1420, 560, 400)}" fill="#EAD9B0" stroke="#8A6A3A" stroke-width="4"/>']
    blobs = ''.join(f'<circle class="{w}-bl" cx="{ox + rnd.uniform(-60, 60):.0f}" cy="{oy + rnd.uniform(-60, 60):.0f}" r="{rnd.uniform(40, 80):.0f}" fill="{cor}" opacity=".78"/>' for _ in range(9))
    out.append(f'<g clip-path="url(#{w}-cp)">{blobs}</g>')
    c.a(f"tl.fromTo('.{w}-bl',{{scale:0}},{{scale:(i)=>[7,5.5,6.5,4.8,7.5,5,6,5.8,6.8][i%9],duration:{max(1.0, t1 - t - 0.2):.2f},ease:'power1.out',stagger:0.12,"
        f"transformOrigin:'50% 50%'}},{q(t)});")
    out.append(f'<circle cx="{ox}" cy="{oy}" r="14" fill="#B5523B"/><circle id="{w}-an" cx="{ox}" cy="{oy}" r="30" fill="none" stroke="#B5523B" stroke-width="5"/>')
    c.a(f"tl.fromTo('#{w}-an',{{scale:0.6,opacity:1}},{{scale:2.2,opacity:0,duration:0.9,repeat:{max(1, int((t1 - t) / 0.9))},svgOrigin:'{ox} {oy}'}},{q(t)});")
    if rotulo:
        gid = f'{w}-t'
        out.append(_tag(gid, ox, oy - 90, rotulo, '#FBF4E4'))
        _pop(c, gid, _T(t_rotulo) if t_rotulo is not None else t + 0.3)
    an.som(t, 'whoosh_lento', 0.14)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}</g>')


def funil(c, t, topo='Leads', fundo='Clientes', t_sai=None, n=16, saem=4):
    """Funil: bolinhas caindo em cima (topo), poucas saindo embaixo como moedas douradas (fundo). Rótulos ≥ 48 px."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'fn')
    rnd = random.Random(_seed(c.id) + 93)
    ts_ = _T(t_sai) if t_sai is not None else t + 1.0
    out = ['<path d="M200 1080 L880 1080 L620 1460 L620 1640 L460 1640 L460 1460Z" fill="#2D4A63"/>'
           '<path d="M230 1094 L850 1094 L606 1450 L606 1626 L474 1626 L474 1450Z" fill="#3B5A75"/>'
           '<ellipse cx="540" cy="1080" rx="340" ry="40" fill="#22394F"/>']
    D = max(0.8, t1 - t)
    bol = ''.join(f'<circle class="{w}-b" cx="{rnd.uniform(260, 820):.0f}" cy="1010" r="18" fill="{rnd.choice(("#E9E4D8", "#B5523B", "#C9A24A", "#8FC1D4"))}"/>' for _ in range(n))
    out.append(bol)
    c.a(f"tl.fromTo('.{w}-b',{{y:-20,opacity:1}},{{y:150,opacity:0,duration:0.8,ease:'power1.in',repeat:{max(1, int(D / 0.8))},stagger:{{each:0.12,repeat:{max(1, int(D / 0.8))}}}}},{q(t)});")
    moe = ''.join(f'<g transform="translate(540 1650)"><g class="{w}-m"><circle r="22" fill="#F2B544" stroke="#9C7A2E" stroke-width="4"/></g></g>' for _ in range(saem))
    out.append(moe)
    c.a(f"tl.fromTo('.{w}-m',{{y:0,x:0,opacity:0}},{{y:110,x:(i)=>[-120,60,-40,140][i%4],opacity:1,duration:0.7,ease:'bounce.out',repeat:{max(1, int((t1 - ts_) / 1.2))},stagger:{{each:0.3,repeat:{max(1, int((t1 - ts_) / 1.2))}}}}},{q(ts_)});")
    an.som(ts_, 'glock', 0.18)
    g1, g2 = f'{w}-t1', f'{w}-t2'
    # 08/11 (margem segura): etiqueta de baixo encostada no bico (era 1760, saía embaixo do RL); a peça inteira encaixa
    out.append(_tag(g1, 540, 1000, topo, '#FBF4E4', livre=True) + _tag(g2, 770, 1560, fundo, '#B5523B', '#FBF6EA', livre=True))
    _pop(c, g1, t)
    _pop(c, g2, ts_ + 0.2)
    _entra_amb(c, w, t)
    return _amb(c, bo.encaixa(f'<g id="{w}">{"".join(out)}</g>', (200, 950, 900, 1790)))   # moedas caem até ~1782


def pictograma(c, t, n=10, destaque=8, rotulo='', tempos=None, cor='#F2B544'):
    """Grade de bonequinhos (2 fileiras) que acendem um a um até o destaque (ex.: 8 de 10 = 80%). Só o falado."""
    t = _T(t)
    w = an._id(c, 'pg')
    cols = min(5, n)
    lin = (n + cols - 1) // cols
    out = []
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.3 + 0.16 * k for k in range(destaque)]
    for k in range(n):
        x = 540 + (k % cols - (cols - 1) / 2) * 150
        y = 1180 + (k // cols) * 300
        pid = f'{w}-p{k}'
        out.append(f'<g transform="translate({x:.0f} {y})"><g id="{pid}"><circle cx="0" cy="-70" r="38" fill="#B9B2A8"/>'
                   f'<path d="M-52 80 L-52 0 Q-52 -24 -28 -24 L28 -24 Q52 -24 52 0 L52 80Z" fill="#B9B2A8"/></g></g>')
        if k < destaque:
            c.a(f"tl.to('#{pid} circle, #{pid} path',{{fill:'{cor}',duration:0.2}},{q(ts_[k])});")
            c.a(f"tl.fromTo('#{pid}',{{y:0}},{{y:-24,duration:0.15,yoyo:true,repeat:1}},{q(ts_[k])});")
            an.som(ts_[k], 'pop', 0.1)
    if rotulo:
        gid = f'{w}-r'
        out.append(_tag(gid, 540, 1180 + lin * 300 - 40, rotulo, '#2D4A63', '#FBF6EA', livre=True))
        _pop(c, gid, ts_[-1] + 0.2)
    _entra_amb(c, w, t)
    y1_ = 1180 + lin * 300 + 10 if rotulo else 1180 + (lin - 1) * 300 + 90
    return _amb(c, bo.encaixa(f'<g id="{w}">{"".join(out)}</g>', (540 - (cols - 1) * 75 - 60, 1080, 540 + (cols - 1) * 75 + 60, y1_)))


def balanca(c, t, esq='Custo', dir_='Lucro', pende='esq', t_pende=None, pesos=3):
    """Balança de dois pratos: pesos (moedas/caixas) caem num lado e o braço inclina. pende='esq'|'dir'|'equilibra'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'bz')
    tp = _T(t_pende) if t_pende is not None else t + 0.8
    ang = {'esq': -14, 'dir': 14, 'equilibra': 0}[pende]
    base = ('<path d="M440 1800 L640 1800 L580 1740 L500 1740Z" fill="#5A3E28"/><rect x="528" y="1160" width="24" height="590" fill="#8A6A45"/>'
            '<circle cx="540" cy="1160" r="26" fill="#C9A24A"/>')
    braco = (f'<g id="{w}-br"><rect x="230" y="1150" width="620" height="20" rx="10" fill="#C9A24A"/>'
             + ''.join(f'<g transform="translate({x} 1160)"><g id="{w}-pr{k}"><path d="M0 0 L-90 230 M0 0 L90 230" stroke="#5A5F66" stroke-width="4"/>'
                       f'<path d="M-130 230 L130 230 Q120 290 0 290 Q-120 290 -130 230Z" fill="#B9BFC4"/>'
                       + ''.join(f'<g class="{w}-ps{k}"><rect x="{-70 + 50 * j}" y="{180 - 0 * j}" width="44" height="44" rx="6" fill="{"#B5523B" if k == 0 else "#3F7F55"}"/></g>' for j in range(pesos))
                       + '</g></g>' for k, x in enumerate((250, 830))) + '</g>')
    lado = 0 if pende == 'esq' else 1
    c.a(f"tl.fromTo('.{w}-ps{lado}',{{y:-500,opacity:0}},{{y:0,opacity:1,duration:0.35,ease:'bounce.out',stagger:0.25}},{q(tp - 0.5)});")
    c.a(f"tl.fromTo('#{w}-br',{{rotation:0}},{{rotation:{ang},duration:0.8,ease:'elastic.out(1,0.5)',svgOrigin:'540 1160'}},{q(tp)});")
    for k in range(2):
        c.a(f"tl.fromTo('#{w}-pr{k}',{{rotation:0}},{{rotation:{-ang},duration:0.8,ease:'elastic.out(1,0.5)',svgOrigin:'0 0'}},{q(tp)});")
    an.som(tp, 'batida', 0.2)
    g1, g2 = f'{w}-e', f'{w}-d'
    tags = _tag(g1, 250, 1080, esq, '#B5523B', '#FBF6EA', livre=True) + _tag(g2, 830, 1080, dir_, '#3F7F55', '#FBF6EA', livre=True)
    _pop(c, g1, t)
    _pop(c, g2, t + 0.25)
    _entra_amb(c, w, t)
    # 08/11 (margem segura): pratos (x 120–960 ao inclinar) + etiquetas + pé encaixam juntos
    return _amb(c, bo.encaixa(f'<g id="{w}">{base}{braco}{tags}</g>', (70, 1030, 1010, 1810)))


def antes_depois(c, t, antes='Antes', depois='Depois', t_depois=None):
    """Tela dividida ANTES × DEPOIS: à esquerda mesa bagunçada (papel voando, pessoa com a mão na cabeça), à direita
    mesa limpa com a tela da IA brilhando e a pessoa tranquila tomando café. A divisória desce no meio."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'ad')
    rnd = random.Random(_seed(c.id) + 94)
    td = _T(t_depois) if t_depois is not None else t + 1.0
    out = ['<rect x="-300" y="960" width="840" height="960" fill="#D9C4A0"/><rect x="540" y="960" width="840" height="960" fill="#CFE0D3"/>']
    pa = f'{w}-a'
    g, _, _ = bo._posto(c, pa, 120, 1760, 0.85, 1, 'preocupado', rnd, xicara=False)
    out.append(g)
    vive(c, pa, t, t1)
    gesticula(c, pa, t, t1, 'j-bfa', 12, 0.2)
    out.append(bo._papeis_voando(c, f'{w}-pv', 300, 1500, t, n=4, sobe=420))
    pb = f'{w}-b'
    g2, _, _ = bo._posto(c, pb, 640, 1760, 0.85, 1, 'xicara_sent', rnd, tela='ia', xicara=False)
    out.append(f'<g id="{w}-dir">{g2}</g>')
    vive(c, pb, td, t1)
    c.a(f"tl.fromTo('#{pb}-mon .iag',{{opacity:0}},{{opacity:0.7,duration:0.4,yoyo:true,repeat:{max(1, int((t1 - td) / 0.8))}}},{q(td)});")
    c.a(f"tl.fromTo('#{w}-dir',{{opacity:0.25}},{{opacity:1,duration:0.4}},{q(td)});")
    out.append(f'<rect id="{w}-dv" x="532" y="960" width="16" height="960" fill="#FBF6EA"/>')
    c.a(f"tl.fromTo('#{w}-dv',{{scaleY:0}},{{scaleY:1,duration:0.5,ease:'power2.out',svgOrigin:'540 960'}},{q(t)});")
    g1, g2_ = f'{w}-t1', f'{w}-t2'
    out.append(_etiqueta(300, 1030, antes, 48, '#B03A2A', '#FBF6EA', rot=-2, eid=g1) + _etiqueta(780, 1030, depois, 48, '#3F7F55', '#FBF6EA', rot=2, eid=g2_))
    _pop(c, g1, t + 0.2)
    _pop(c, g2_, td)
    an.som(td, 'brilho', 0.2)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}</g>')


def grade_objetos(c, t, n=18, objeto='ferramenta', destaque=None, t_destaque=None, lupa=True, y0=980):
    """Muitos objetos iguais em grade (catálogo / prateleira de museu da referência): aparecem em onda; uma lupa passa;
    destaque=k acende um (ou risca vários: destaque=('x', [1,4,7])). objeto: ferramenta, planilha, boleto, caixa."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'go')
    cols = 4
    dy0 = y0 - 980   # letreiro de 4 linhas: desça a grade (y0=1080)
    out = [f'<rect x="150" y="{y0}" width="780" height="{1840 - y0}" rx="12" fill="#4A3422"/>']
    for k in range(n):
        x = 245 + (k % cols) * 196
        y = 1060 + dy0 + (k // cols) * 170
        if y > 1780:
            break
        oid = f'{w}-o{k}'
        if objeto == 'planilha':
            ob = '<rect x="-60" y="-50" width="120" height="100" rx="4" fill="#FBF6EA"/>' + ''.join(f'<rect x="-50" y="{-36 + 20 * j}" width="100" height="3" fill="#3F7F55"/>' for j in range(5)) + '<rect x="-14" y="-50" width="3" height="100" fill="#3F7F55"/>'
        elif objeto == 'boleto':
            ob = '<rect x="-64" y="-40" width="128" height="80" rx="4" fill="#FBF6EA"/>' + ''.join(f'<rect x="{-54 + 8 * j}" y="6" width="{(2, 4, 3)[j % 3]}" height="26" fill="#1E2A3A"/>' for j in range(13)) + '<rect x="-54" y="-28" width="70" height="8" fill="#B5523B"/>'
        elif objeto == 'caixa':
            ob = '<rect x="-56" y="-50" width="112" height="100" fill="#C49A62"/><rect x="-56" y="-50" width="112" height="16" fill="#A87F4A"/><rect x="-10" y="-50" width="20" height="100" fill="#E3CDA2" opacity=".7"/>'
        else:
            ob = ('<rect x="-56" y="-46" width="112" height="92" rx="16" fill="{0}"/><circle cx="0" cy="-4" r="22" fill="#FBF6EA" opacity=".85"/>'
                  '<rect x="-30" y="26" width="60" height="8" rx="4" fill="#FBF6EA" opacity=".6"/>').format(('#2D4A63', '#B5523B', '#5B7F6E', '#C9A24A', '#8E6A9A')[k % 5])
        out.append(f'<rect x="{x - 90}" y="{y + 56}" width="180" height="10" fill="#3A2818"/><g transform="translate({x} {y})"><g id="{oid}">{ob}</g></g>')
    c.a(f"tl.fromTo('#{w} [id^=\"{w}-o\"]',{{opacity:0,scale:0.4,transformOrigin:'50% 50%'}},{{opacity:1,scale:1,duration:0.3,ease:'back.out(2)',stagger:0.05,transformOrigin:'50% 50%'}},{q(t)});")
    an.som(t, 'pop', 0.14)
    if destaque is not None:
        td = _T(t_destaque) if t_destaque is not None else t + 1.2
        if isinstance(destaque, tuple) and destaque[0] == 'x':
            for j, k in enumerate(destaque[1]):
                x = 245 + (k % cols) * 196
                y = 1060 + dy0 + (k // cols) * 170
                out.append(f'<path id="{w}-x{j}" d="M{x - 50} {y - 44} L{x + 50} {y + 44} M{x + 50} {y - 44} L{x - 50} {y + 44}" stroke="#E0573E" stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>')
                c.a(f"tl.to('#{w}-x{j}',{{strokeDashoffset:0,duration:0.2}},{q(td + 0.2 * j)});")
                an.som(td + 0.2 * j, 'tique2', 0.16)
        else:
            c.a(f"tl.to('#{w}-o{destaque}',{{scale:1.3,duration:0.3,ease:'back.out(2)',transformOrigin:'50% 50%'}},{q(td)});")
            c.a(f"tl.fromTo('#{w} [id^=\"{w}-o\"]:not(#{w}-o{destaque})',{{opacity:1}},{{opacity:0.35,duration:0.3}},{q(td)});")
            an.som(td, 'brilho', 0.2)
    if lupa:
        out.append(f'<g id="{w}-lp"><circle r="70" fill="#FFFFFF" opacity=".15" stroke="#C9A24A" stroke-width="14"/><rect x="44" y="44" width="26" height="110" rx="10" fill="#5A3E28" transform="rotate(-45 57 57)"/></g>')
        c.a(f"tl.set('#{w}-lp',{{x:260,y:1100}},{q(c.t0)});")
        c.a(f"tl.to('#{w}-lp',{{keyframes:{{x:[260,820,300,780],y:[1100,1250,1500,1700]}},duration:{max(1.0, t1 - t - 0.2):.2f},ease:'sine.inOut'}},{q(t + 0.2)});")
    _entra_amb(c, w, t)
    # 08/11 (margem segura): o móvel inteiro encaixa abaixo do letreiro e acima do pé do formato
    return _amb(c, bo.encaixa(f'<g id="{w}">{"".join(out)}</g>', (140, y0 - 10, 940, 1930)))   # 1930: a lupa desce até ~1830 e os objetos entram em escala (back.out)


# ================================================================ METÁFORAS VISUAIS
def iceberg(c, t, topo='Salário', fundo=('Encargos', 'Ferramentas', 'Treinamento'), tempos=None):
    """Iceberg: só a ponta acima da água (o que se vê), e o bloco enorme submerso com os custos escondidos aparecendo
    um a um (tempos). O mar cobre a metade de baixo. Bom no 'porto' ou 'dia'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'ib')
    ts_ = _ts(tempos, len(fundo), t + 0.6, 0.6)
    # 08/11 (margem segura): no RL a água sobe 100 px e os custos submersos ficam mais juntos, todos acima de y 1500
    agua = 1180 if motor.FORMATO != 'RL' else 1080
    da = agua - 1180
    passo = min(170, (bo.faixa()[1] - 56 - (agua + 160)) / max(1, len(fundo) - 1))
    out = [f'<rect x="-300" y="{agua}" width="1680" height="{1980 - agua}" fill="#2D5770"/>',
           f'<rect x="-300" y="{agua}" width="1680" height="40" fill="#3E6F86"/>',
           f'<path d="M540 {980 + da} L640 {1100 + da} L700 {agua} L380 {agua} L450 {1080 + da}Z" fill="#F4F8F8"/><path d="M540 {980 + da} L640 {1100 + da} L700 {agua} L560 {agua}Z" fill="#D5E4EA"/>',
           f'<path id="{w}-sub" d="M380 {agua} L700 {agua} L860 1400 L900 1650 L760 1880 L330 1880 L170 1640 L220 1380Z" fill="#9EC3D2" opacity=".75"/>']
    out += [f'<g class="ar-onda"><rect x="{x}" y="{agua + 8 + 22 * (k % 3)}" width="120" height="5" rx="2" fill="#FFFFFF" opacity=".35"/></g>' for k, x in enumerate(range(-280, 1380, 170))]
    c.a(f"tl.fromTo('#{w}-sub',{{opacity:0.25}},{{opacity:0.8,duration:0.6}},{q(ts_[0] - 0.3)});")
    gt = f'{w}-t'
    out.append(_tag(gt, 540, 1040 + da, topo, '#FBF4E4'))
    _pop(c, gt, t)
    for k, f in enumerate(fundo):
        gid = f'{w}-f{k}'
        out.append(_tag(gid, 540, agua + 160 + passo * k, f, '#1E3A4E', '#FBF6EA'))
        _pop(c, gid, ts_[k], 'sub')
    c.a(f"tl.fromTo('#{w}-ib',{{y:0}},{{y:-10,duration:1.6,yoyo:true,repeat:{max(1, int((t1 - t) / 1.6))},ease:'sine.inOut'}},{q(t)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}"><g id="{w}-ib">{"".join(out)}</g></g>')


def malabarista(c, t, bolas=('Marketing', 'Vendas', 'Financeiro'), t_cai=None):
    """O dono sozinho fazendo malabarismo com os cartões (setores); com t_cai um deles cai e quica no chão e ele leva
    a mão à cabeça. "Tudo na mão de uma pessoa só". Qualquer interior."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'ml')
    rnd = random.Random(_seed(c.id) + 95)
    pid = f'{w}-p'
    p = pos(corpo(pid, 'toca_alto', rnd=rnd), 540, 1840, 1.1)
    vive(c, pid, t, t1)
    gesticula(c, pid, t, t1, 'j-bf', 14, 0.25)
    gesticula(c, pid, t, t1, 'j-bt', 14, 0.25)
    out = []
    n = len(bolas)
    tc = _T(t_cai) if t_cai is not None else None
    per = 1.2
    for k, b in enumerate(bolas):
        gid = f'{w}-b{k}'
        tx = b.upper()
        lw = _txt_larg(tx, 48) + 44
        out.append(f'<g id="{gid}"><rect x="{-lw / 2:.0f}" y="-40" width="{lw:.0f}" height="80" rx="16" fill="{("#B5523B", "#2D4A63", "#C9A24A", "#5B7F6E")[k % 4]}"/>'
                   f'<text class="tc" x="0" y="17" text-anchor="middle" font-size="48" fill="#FBF6EA">{_html.escape(tx)}</text></g>')
        # arco em loop: da mão esquerda (420,1300) sobe até (540, 1000) e desce na direita (660,1300) e volta por baixo
        xl, xr = 230 + lw / 2 + 10, 850 - lw / 2 - 10
        # 08/11: arco largo (dentro das laterais 170–910): no arco estreito (400–680) os cartões se amontoavam
        x0, x1 = 170 + lw / 2 + 10, 910 - lw / 2 - 10
        fim = tc if (tc is not None and k == 0) else t1
        D = max(0.5, fim - t)
        # 08/11 (folha do t68: o cartão passava na frente do ROSTO): a volta por baixo era em y 1420, na altura da cara
        # (cabeça de 1317 a 1400). Agora o arco inteiro fica acima da cabeça: mãos em 1260, topo em 990, volta por
        # dentro em 1130 (com a volta em 1240 dois cartões se encostavam na altura das mãos: 'TAREFAS' cobria 'SUPORTE').
        c.a(f"tl.fromTo('#{gid}',{{x:{x0:.0f},y:1260}},{{keyframes:{{x:[{x0:.0f},{(x0 + x1) / 2:.0f},{x1:.0f},{(x0 + x1) / 2:.0f},{x0:.0f}],y:[1260,990,1260,1130,1260]}},"
            f"duration:{per},ease:'none',repeat:{max(0, int(D / per))},immediateRender:true}},{q(t - k * per / n)});")
    if tc is not None:
        # 08/11 (margem segura): o cartão que cai vai sumindo antes de passar do pé do formato (era quicar no chão,
        # com o texto em y 1780 — embaixo da interface do Reels)
        c.a(f"tl.to('#{w}-b0',{{y:{bo.faixa()[1] - 90},x:300,rotation:-30,duration:0.5,ease:'power2.in'}},{q(tc)});")
        c.a(f"tl.to('#{w}-b0',{{opacity:0,duration:0.35,ease:'power1.in'}},{q(tc + 0.12)});")
        muda_pose(c, pid, 'toca_alto', 'coca', tc + 0.3)
        an.som(tc + 0.4, 'batida', 0.24)
    else:
        an.som(t, 'swish', 0.12)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{p}<g id="{w}-bs">{"".join(out)}</g></g>')


def domino(c, t, n=8, rotulos=(), t_cai=None):
    """Fileira de dominós caindo em cadeia (efeito dominó); rótulos opcionais no 1º e no último."""
    t = _T(t)
    w = an._id(c, 'dm')
    tc = _T(t_cai) if t_cai is not None else t + 0.6
    out = ['<rect x="-300" y="1720" width="1680" height="20" fill="#000" opacity=".12"/>']
    for k in range(n):
        x = 180 + k * (720 / max(1, n - 1))
        h = 180 + 18 * k
        did = f'{w}-d{k}'
        out.append(f'<g id="{did}"><rect x="{x - 22:.0f}" y="{1720 - h}" width="44" height="{h}" rx="6" fill="#1E2A3A"/>'
                   f'<rect x="{x - 14:.0f}" y="{1720 - h + 10}" width="28" height="{h / 2 - 14:.0f}" rx="4" fill="#FBF6EA" opacity=".9"/>'
                   f'<circle cx="{x:.0f}" cy="{1720 - h * 0.25:.0f}" r="7" fill="#FBF6EA"/></g>')
        c.a(f"tl.to('#{did}',{{rotation:{70 if k == n - 1 else 28},duration:0.22,ease:'power2.in',svgOrigin:'{x + 22:.0f} 1720'}},{q(tc + 0.14 * k)});")
        if k % 2 == 0:
            an.som(tc + 0.14 * k, 'madeira', 0.14)
    for j, r_ in enumerate(rotulos[:2]):
        gid = f'{w}-t{j}'
        x = 180 if j == 0 else 900
        out.append(_tag(gid, x, 1380 if j == 0 else 1300, r_, '#FBF4E4' if j == 0 else '#B5523B', '#1E2A3A' if j == 0 else '#FBF6EA'))
        _pop(c, gid, t if j == 0 else tc + 0.14 * n)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}</g>')


def escada(c, t, degraus=('Atende', 'Qualifica', 'Agenda'), tempos=None):
    """Escada subindo da esquerda pra direita; a pessoa sobe degrau a degrau (pulinho) e cada degrau ganha a etiqueta."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'es')
    rnd = random.Random(_seed(c.id) + 96)
    n = len(degraus)
    ts_ = _ts(tempos, n, t, 0.7)
    dw, dh = 720 / n, 600 / n
    o = 0
    out, etq = [], []
    for k in range(n):
        x = 180 + dw * k
        y = 1840 - dh * (k + 1) + o
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{dw + 2:.0f}" height="{1840 - y:.0f}" fill="{("#C9A24A", "#B5523B", "#2D4A63", "#5B7F6E")[k % 4]}"/>'
                   f'<rect x="{x:.0f}" y="{y:.0f}" width="{dw + 2:.0f}" height="14" fill="#000" opacity=".15"/>')
        gid = f'{w}-t{k}'
        etq.append(_tag(gid, _x(x + dw / 2, degraus[k]), y + 70, degraus[k], '#FBF4E4', tam=48, livre=True))   # depois dos degraus: nada cobre a etiqueta
        _pop(c, gid, ts_[k])
    out += etq
    pid = f'{w}-p'
    out.append(f'<g id="{pid}-m">{pos(corpo(pid, "anda", rnd=rnd), 180 + dw * 0.5 - 40, 1840 - dh + o, 0.55)}</g>')
    for k in range(1, n):
        c.a(f"tl.to('#{pid}-m',{{keyframes:{{x:[{dw * (k - 1):.0f},{dw * (k - 0.5):.0f},{dw * k:.0f}],y:[{-dh * (k - 1):.0f},{-dh * (k - 1) - 90:.0f},{-dh * k:.0f}]}},duration:0.4,ease:'none'}},{q(ts_[k] - 0.4)});")
        an.som(ts_[k], 'pop', 0.12)
    bo.anda(c, pid, t, 0, max(0.5, t1 - t))
    vive(c, pid, t, t1)
    _entra_amb(c, w, t)
    # 08/11 (margem segura): a escada inteira (com a pessoa no último degrau) encaixa abaixo do letreiro e acima do pé
    # do formato; se subir, fica sobre um palco (apoio) em vez de flutuar. Subir só os degraus punha a pessoa em cima
    # do letreiro; puxar só as etiquetas descolava do degrau.
    return _amb(c, bo.encaixa(f'<g id="{w}">{"".join(out)}</g>', (150, 1840 - 600 - 290, 930, 1840), apoio=True))


def foguete(c, t, t_lanca=None, rotulo=''):
    """Foguete na plataforma: fumaça, ignição (tremor) e subida até o meio da tela deixando rastro (crescimento
    rápido). Não passa por cima do letreiro (para em y ~1000). Bom em 'dia', 'campo', 'noite', 'cidade_noite'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'fg')
    tl_ = _T(t_lanca) if t_lanca is not None else t + 0.8
    fog = (f'<g id="{w}-f"><path d="M540 1380 Q600 1460 600 1600 L480 1600 Q480 1460 540 1380Z" fill="#E9E4D8"/>'
           f'<path d="M540 1380 Q570 1410 584 1450 L496 1450 Q510 1410 540 1380Z" fill="#B5523B"/>'
           f'<circle cx="540" cy="1500" r="26" fill="#8FC1D4" stroke="#5A5F66" stroke-width="6"/>'
           f'<path d="M480 1540 L440 1640 L480 1620Z M600 1540 L640 1640 L600 1620Z" fill="#B5523B"/>'
           f'<g id="{w}-fo"><path d="M500 1600 Q540 1760 580 1600Z" fill="#F2B544"/><path d="M516 1600 Q540 1700 564 1600Z" fill="#FFF1C8"/></g></g>')
    base = '<rect x="380" y="1640" width="320" height="40" fill="#5A5F66"/><rect x="420" y="1680" width="30" height="200" fill="#5A5F66"/><rect x="630" y="1680" width="30" height="200" fill="#5A5F66"/>'
    fum = ''.join(f'<circle class="{w}-fm" cx="{540 + dx}" cy="1680" r="{r}" fill="#E9E4D8" opacity=".9"/>' for dx, r in ((-160, 60), (-90, 80), (0, 90), (100, 80), (170, 60)))
    c.a(f"tl.fromTo('#{w}-fo',{{scaleY:0.2}},{{scaleY:1.2,duration:0.08,yoyo:true,repeat:{max(1, int((t1 - t) / 0.08))},svgOrigin:'540 1600'}},{q(t)});")
    c.a(f"tl.fromTo('.{w}-fm',{{scale:0.3,opacity:0}},{{scale:1.6,opacity:0.9,duration:0.8,stagger:0.08,ease:'power2.out',transformOrigin:'50% 50%'}},{q(tl_ - 0.4)});")
    c.a(f"tl.fromTo('#{w}-f',{{x:-3}},{{x:3,duration:0.04,yoyo:true,repeat:{max(1, int(0.5 / 0.04))}}},{q(tl_ - 0.5)});")
    c.a(f"tl.to('#{w}-f',{{y:-480,duration:{max(0.8, t1 - tl_):.2f},ease:'power2.in'}},{q(tl_)});")
    rastro = f'<rect id="{w}-r" x="526" y="1600" width="28" height="0" fill="#F6EBD3" opacity=".7"/>'
    c.a(f"tl.to('#{w}-r',{{attr:{{y:1120,height:480}},duration:{max(0.8, t1 - tl_):.2f},ease:'power2.in'}},{q(tl_)});")
    an.som(tl_ - 0.4, 'riser', 0.2)
    an.som(tl_, 'impacto_ar', 0.24)
    tag = ''
    if rotulo:
        tag = _tag(f'{w}-t', 780, 1560, rotulo, '#FBF4E4')
        _pop(c, f'{w}-t', t + 0.2)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{base}{rastro}{fum}{fog}{tag}</g>')


def barco_furado(c, t, furos=('Folha', 'Ferramentas'), t_balde=None):
    """Barco no mar com furos jorrando água (cada furo com etiqueta) e a pessoa tirando água com o balde sem parar.
    Dinheiro vazando / esforço que não rende."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'bf')
    rnd = random.Random(_seed(c.id) + 97)
    # 08/11 (margem segura): as etiquetas dos furos (y 1760) ficam acima do pé do formato — o mar e o barco sobem juntos
    o = min(0, bo.faixa()[1] - 60 - 1600)
    out = [f'<g transform="translate(0 {o})">', f'<rect x="-300" y="1500" width="1680" height="{460 - o}" fill="#3E6F86"/>']
    out += [f'<g class="ar-onda"><rect x="{x}" y="{1520 + 40 * (k % 4)}" width="140" height="6" rx="3" fill="#FFFFFF" opacity=".3"/></g>' for k, x in enumerate(range(-280, 1380, 150))]
    barco = (f'<g id="{w}-bc"><path d="M200 1440 L880 1440 L800 1620 L280 1620Z" fill="#8A5A2B"/><path d="M200 1440 L880 1440 L870 1470 L210 1470Z" fill="#6B3E1E"/>'
             + ''.join(f'<circle cx="{x}" cy="1560" r="16" fill="#2A1A10"/>' for x in (380, 640)) + '</g>')
    jatos = ''.join(f'<g transform="translate({x} 1560)"><g class="{w}-j"><path d="M0 0 Q{-40 if x < 540 else 40} 40 {-60 if x < 540 else 60} 120" stroke="#9FD3E6" stroke-width="16" fill="none" stroke-linecap="round"/></g></g>' for x in (380, 640))
    c.a(f"tl.fromTo('.{w}-j',{{scaleX:0.85,opacity:0.7}},{{scaleX:1.1,opacity:1,duration:0.2,yoyo:true,repeat:{max(1, int((t1 - t) / 0.2))},svgOrigin:'0 0'}},{q(t)});")
    pid = f'{w}-p'
    p = pos(corpo(pid, 'carrega', rnd=rnd), 540, 1450, 0.75)
    out.append(barco[:-4] + p + '</g>')   # a pessoa balança junto com o barco
    p = ''
    gesticula(c, pid, _T(t_balde) if t_balde is not None else t, t1, 'j-bf', 30, 0.35)
    vive(c, pid, t, t1)
    c.a(f"tl.fromTo('#{w}-bc',{{rotation:-2}},{{rotation:2,duration:1.3,yoyo:true,repeat:{max(1, int((t1 - t) / 1.3))},ease:'sine.inOut',svgOrigin:'540 1600'}},{q(t)});")
    tags = ''
    for k, f in enumerate(furos[:2]):
        gid = f'{w}-t{k}'
        tags += _tag(gid, _x((290, 790)[k], f), 1600, f, '#B5523B', '#FBF6EA', livre=True)   # no pé do casco, junto dos furos (era 1760, embaixo da tela no RL)
        _pop(c, gid, t + 0.3 + 0.4 * k)
    an.som(t, 'shimmer', 0.1)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}{p}{jatos}{tags}</g></g>')


def engrenagens(c, t, rotulos=('Marketing', 'Comercial', 'IA'), t_gira=None):
    """Três engrenagens grandes encaixadas girando juntas (a operação rodando sozinha), cada uma com a etiqueta;
    começam paradas e giram em t_gira."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'eg')
    tg = _T(t_gira) if t_gira is not None else t + 0.4
    import arsenal_fundos as af
    gs = ((330, 1300, 150, 12, '#2D4A63'), (590, 1180, 105, 9, '#B5523B'), (700, 1500, 130, 11, '#C9A24A'))
    out = []
    for k, (x, y, r, d, cor) in enumerate(gs):
        gid = f'{w}-g{k}'
        corpo_ = af._engrenagem(0, 0, r, d, cor, 0)
        out.append(f'<g transform="translate({x} {y})"><g id="{gid}">{corpo_}</g></g>')
        sent = 1 if k % 2 == 0 else -1
        vel = 60 * 150 / r
        c.a(f"tl.fromTo('#{gid}',{{rotation:0}},{{rotation:{sent * vel * max(0.5, t1 - tg):.0f},duration:{q(max(0.5, t1 - tg))},ease:'power1.in',svgOrigin:'0 0'}},{q(tg)});")
    for k, (rot, (x, y, r, _, _)) in enumerate(zip(rotulos, gs)):
        gid = f'{w}-t{k}'
        out.append(_tag(gid, _x(x, rot), y + r + 70 if k != 1 else y - r - 60, rot, '#FBF4E4', livre=True))
        _pop(c, gid, t + 0.3 * k)
    an.som(tg, 'madeira', 0.2)
    _entra_amb(c, w, t)
    # 08/11 (margem segura): as 3 engrenagens + etiquetas encaixam juntas. A caixa conta a engrenagem GIRANDO (o
    # navegador mede o retângulo do desenho girado: até raio x 1,41 a 45°)
    return _amb(c, bo.encaixa(f'<g id="{w}">{"".join(out)}</g>', (80, 930, 890, 1745)))


def cabo_guerra(c, t, esq='Você', dir_='Concorrente', vence='esq', t_puxa=None):
    """Cabo de guerra: dois de cada lado puxando a corda; a fita do meio vai pro lado de quem vence."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cg')
    rnd = random.Random(_seed(c.id) + 98)
    tp = _T(t_puxa) if t_puxa is not None else t + 0.8
    dx = -140 if vence == 'esq' else 140
    out = [f'<g id="{w}-cd"><rect x="-200" y="1560" width="1480" height="12" rx="6" fill="#C9A24A"/><rect x="530" y="1530" width="20" height="70" fill="#B03A2A"/></g>']
    pes = ''
    for k, (x, d) in enumerate(((180, -1), (330, -1), (750, 1), (900, 1))):
        pid = f'{w}-p{k}'
        pes += f'<g id="{pid}-m">' + pos(corpo(pid, 'carrega', rnd=rnd), x, 1800, 0.95, d) + '</g>'
        vive(c, pid, t, t1)
        c.a(f"tl.fromTo('#{pid} .j-cq',{{rotation:0}},{{rotation:{-12},duration:0.4,yoyo:true,repeat:{max(1, int((t1 - t) / 0.4))},svgOrigin:'0 -200'}},{q(t)});")
        c.a(f"tl.to('#{pid}-m',{{x:{dx:.0f},duration:{max(0.5, t1 - tp):.2f},ease:'power2.inOut'}},{q(tp)});")
    c.a(f"tl.to('#{w}-cd',{{x:{dx:.0f},duration:{max(0.5, t1 - tp):.2f},ease:'power2.inOut'}},{q(tp)});")
    g1, g2 = f'{w}-t1', f'{w}-t2'
    tags = _tag(g1, 260, 1180, esq, '#3F7F55' if vence == 'esq' else '#FBF4E4', '#FBF6EA' if vence == 'esq' else '#1E2A3A') + \
        _tag(g2, 820, 1180, dir_, '#3F7F55' if vence == 'dir' else '#FBF4E4', '#FBF6EA' if vence == 'dir' else '#1E2A3A')
    _pop(c, g1, t)
    _pop(c, g2, t + 0.25)
    an.som(tp, 'swish', 0.18)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}{pes}{tags}</g>')


def semente(c, t, t_cresce=None, frutos='moeda', rotulo=''):
    """Semente no vaso/terra que brota e vira árvore, os frutos são moedas douradas (crescimento que se planta)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'sm')
    tc = _T(t_cresce) if t_cresce is not None else t + 0.4
    D = max(0.8, t1 - tc - 0.2)
    out = ['<path d="M300 1820 Q540 1700 780 1820Z" fill="#6B4E31"/>',
           f'<rect id="{w}-tr" x="526" y="1760" width="28" height="0" fill="#6B4E31"/>']
    c.a(f"tl.to('#{w}-tr',{{attr:{{y:1440,height:320}},duration:{D * 0.6:.2f},ease:'power2.out'}},{q(tc)});")
    out.append(f'<g id="{w}-fr">')
    for k, (x, y, r) in enumerate(((540, 1330, 150), (440, 1400, 110), (640, 1400, 110), (540, 1230, 100))):
        cid = f'{w}-c{k}'
        out.append(f'<circle id="{cid}" cx="{x}" cy="{y}" r="{r}" fill="{("#4F7F5C", "#5B8F66", "#4F7F5C", "#6E9F72")[k]}"/>')
        c.a(f"tl.fromTo('#{cid}',{{scale:0}},{{scale:1,duration:0.6,ease:'back.out(1.6)',svgOrigin:'{x} {y + r}'}},{q(tc + D * 0.35 + 0.15 * k)});")
    for k, (x, y) in enumerate(((480, 1300), (600, 1280), (540, 1400), (430, 1420), (650, 1420), (560, 1190))):
        fid = f'{w}-m{k}'
        out.append(f'<g id="{fid}"><circle cx="{x}" cy="{y}" r="24" fill="#F2B544" stroke="#9C7A2E" stroke-width="4"/></g>')
        c.a(f"tl.fromTo('#{fid}',{{scale:0}},{{scale:1,duration:0.3,ease:'back.out(3)',svgOrigin:'{x} {y}'}},{q(tc + D * 0.7 + 0.12 * k)});")
    out.append('</g>')
    an.som(tc + D * 0.7, 'glock', 0.2)
    c.a(f"tl.fromTo('#{w}-cop',{{rotation:-1.5}},{{rotation:1.5,duration:1.4,yoyo:true,repeat:{max(1, int((t1 - t) / 1.4))},svgOrigin:'540 1760'}},{q(t)});")
    tag = ''
    if rotulo:
        tag = _tag(f'{w}-t', 540, 1880, rotulo, '#FBF4E4')
        _pop(c, f'{w}-t', t + 0.2)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}"><g id="{w}-cop">{"".join(out)}</g>{tag}</g>')


def torre_blocos(c, t, blocos=('Folha', 'Ferramenta', 'Processo', 'Gente'), tempos=None, t_cai=None):
    """Blocos com etiqueta empilhando (a estrutura inchando); a torre balança cada vez mais e, com t_cai, desaba."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'tb')
    ts_ = _ts(tempos, len(blocos), t, 0.5)
    out = []
    # 08/11 (margem segura): a torre fica de pé numa mesa quando o pé do formato é mais alto que o chão (RL: 1470)
    base = min(1840, bo.faixa()[1] - 80)   # 80: a torre que desaba gira os blocos e o canto desce além da mesa
    y = base
    for k, b in enumerate(blocos):
        tx = b.upper()
        lw = min(600, _txt_larg(tx, 48) + 80)
        h = 110
        y -= h
        bid = f'{w}-b{k}'
        out.append(f'<g id="{bid}"><rect x="{540 - lw / 2 + (k % 2) * 16 - 8:.0f}" y="{y}" width="{lw:.0f}" height="{h}" rx="8" fill="{("#B5523B", "#2D4A63", "#C9A24A", "#5B7F6E", "#8E6A9A")[k % 5]}"/>'
                   f'<text class="tc" x="{540 + (k % 2) * 16 - 8}" y="{y + 72}" text-anchor="middle" font-size="48" fill="#FBF6EA">{_html.escape(tx)}</text></g>')
        c.a(f"tl.fromTo('#{bid}',{{y:-500,opacity:0}},{{y:0,opacity:1,duration:0.4,ease:'bounce.out'}},{q(ts_[k])});")
        an.som(ts_[k] + 0.2, 'madeira', 0.16)
    c.a(f"tl.fromTo('#{w}-tr',{{rotation:-1}},{{rotation:1,duration:0.6,yoyo:true,repeat:{max(1, int((t1 - ts_[-1]) / 0.6))},ease:'sine.inOut',svgOrigin:'540 {base}'}},{q(ts_[-1])});")
    if t_cai is not None:
        tc = _T(t_cai)
        for k in range(len(blocos)):
            dx_ = max(-230, min(230, (-1) ** k * (90 + 70 * k)))
            c.a(f"tl.to('#{w}-b{k}',{{x:{dx_},y:{110 * k},rotation:{(-1) ** k * (12 + 6 * k)},duration:0.6,ease:'bounce.out',transformOrigin:'50% 100%'}},{q(tc + 0.05 * (len(blocos) - k))});")
        an.som(tc + 0.3, 'impacto', 0.3)
    _entra_amb(c, w, t)
    mesa = ''
    if base < 1840:
        mesa = (f'<rect x="200" y="{base}" width="680" height="30" rx="6" fill="#6B4E31"/><rect x="200" y="{base + 24}" width="680" height="8" fill="#000" opacity=".18"/>'
                f'<rect x="240" y="{base + 30}" width="30" height="{1960 - base}" fill="#5A3E28"/><rect x="810" y="{base + 30}" width="30" height="{1960 - base}" fill="#5A3E28"/>')
    return _amb(c, f'<g id="{w}">{mesa}<g id="{w}-tr">{"".join(out)}</g></g>')


def ima(c, t, t_atrai=None, n=6, rotulo=''):
    """Ímã grande na direita puxando bonequinhos (clientes) que vêm deslizando da esquerda."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'im')
    rnd = random.Random(_seed(c.id) + 99)
    ta = _T(t_atrai) if t_atrai is not None else t + 0.4
    mag = (f'<g id="{w}-mg"><path d="M900 1150 L760 1150 Q600 1150 600 1350 Q600 1550 760 1550 L900 1550 L900 1450 L760 1450 Q700 1450 700 1350 Q700 1250 760 1250 L900 1250Z" fill="#B03A2A"/>'
           f'<rect x="840" y="1150" width="60" height="100" fill="#D9D4CC"/><rect x="840" y="1450" width="60" height="100" fill="#D9D4CC"/></g>')
    c.a(f"tl.fromTo('#{w}-mg',{{x:0}},{{x:6,duration:0.06,yoyo:true,repeat:{max(1, int((t1 - ta) / 0.06))}}},{q(ta)});")
    lin = ''.join(f'<path class="{w}-l" d="M590 {1270 + 40 * k} Q520 {1300 + 40 * k} 470 {1260 + 40 * k}" stroke="#F2B544" stroke-width="5" fill="none" opacity="0"/>' for k in range(4))
    c.a(f"tl.fromTo('.{w}-l',{{opacity:0,x:0}},{{opacity:1,x:-30,duration:0.4,repeat:{max(1, int((t1 - ta) / 0.4))},stagger:0.1}},{q(ta)});")
    pes = ''
    for k in range(n):
        pid = f'{w}-p{k}'
        x0 = -150 - 120 * k
        pes += pos(corpo(pid, 'anda', rnd=rnd), x0, 1760 if k % 2 else 1680, 0.6 if k % 2 else 0.5)
        anda(c, pid, ta + 0.15 * k, (540 - x0) / (0.6 if k % 2 else 0.5), max(0.6, t1 - ta - 0.15 * k - 0.1))
        vive(c, pid, t, t1)
    an.som(ta, 'shimmer', 0.18)
    tag = ''
    if rotulo:
        tag = _tag(f'{w}-t', 760, 1080, rotulo, '#FBF4E4')
        _pop(c, f'{w}-t', t + 0.2)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{lin}{mag}{pes}{tag}</g>')


def lampada(c, t, t_acende=None, pessoa=True):
    """Lâmpada grande pendurada que ACENDE (raios girando, brilho) e a pessoa embaixo olhando pra cima (a ideia)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'lp')
    rnd = random.Random(_seed(c.id) + 100)
    ta = _T(t_acende) if t_acende is not None else t + 0.5
    out = [f'<path d="M540 940 L540 1060" stroke="#3A3A3A" stroke-width="6"/>',
           f'<g id="{w}-rs" opacity="0">' + ''.join(f'<rect x="-8" y="-330" width="16" height="90" rx="8" fill="#F2B544" transform="translate(540 1200) rotate({a})"/>' for a in range(0, 360, 30)) + '</g>',
           f'<circle id="{w}-gl" cx="540" cy="1200" r="230" fill="#F2B544" opacity="0"/>',
           '<rect x="490" y="1060" width="100" height="70" rx="10" fill="#8A8F96"/>',
           f'<circle id="{w}-bu" cx="540" cy="1220" r="130" fill="#E9E4D8"/>']
    c.a(f"tl.to('#{w}-bu',{{fill:'#FFE38A',duration:0.15}},{q(ta)});tl.to('#{w}-gl',{{opacity:0.25,duration:0.3}},{q(ta)});tl.to('#{w}-rs',{{opacity:1,duration:0.2}},{q(ta)});")
    c.a(f"tl.fromTo('#{w}-rs',{{rotation:0}},{{rotation:{int(40 * (t1 - ta))},duration:{q(max(0.3, t1 - ta))},ease:'none',svgOrigin:'540 1200'}},{q(ta)});")
    c.a(f"tl.fromTo('#{w}-gl',{{scale:1}},{{scale:1.12,duration:0.5,yoyo:true,repeat:{max(1, int((t1 - ta) / 0.5))},svgOrigin:'540 1200'}},{q(ta + 0.3)});")
    c.a(f"tl.fromTo('#{w}-lp',{{rotation:-3}},{{rotation:3,duration:1.6,yoyo:true,repeat:{max(1, int((t1 - t) / 1.6))},ease:'sine.inOut',svgOrigin:'540 940'}},{q(t)});")
    an.som(ta, 'brilho', 0.26)
    p = ''
    if pessoa:
        pid = f'{w}-p'
        p = pos(corpo(pid, 'coca', rnd=rnd), 360, 1880, 0.95)
        vive(c, pid, t, t1)
        muda_pose(c, pid, 'coca', 'acena', ta)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}"><g id="{w}-lp">{"".join(out)}</g>{p}</g>')


def corrida(c, t, esq='Você', dir_='Concorrente', t_passa=None):
    """Pista de corrida: dois correndo; em t_passa o primeiro (esq) ultrapassa (ou fica pra trás, se ele disser)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'co')
    rnd = random.Random(_seed(c.id) + 101)
    tp = _T(t_passa) if t_passa is not None else t + 1.0
    out = ['<rect x="-300" y="1500" width="1680" height="420" fill="#B5523B"/>'
           + ''.join(f'<rect x="-300" y="{y}" width="1680" height="6" fill="#FBF6EA" opacity=".8"/>' for y in (1500, 1640, 1780))
           + ''.join(f'<rect x="{x}" y="1500" width="6" height="420" fill="#FBF6EA" opacity=".3"/>' for x in range(-300, 1400, 200))]
    D = max(1.0, t1 - t)
    for k, (nm, y, esc) in enumerate(((dir_, 1630, 0.75), (esq, 1770, 0.85))):
        pid = f'{w}-p{k}'
        # 08/11 (margem segura): o nome anda junto com o corredor e a pista anda -120; o de trás largava em x 140 e o
        # nome saía pela esquerda — larga onde o nome inteiro cabe (≥ 170 + meia largura)
        x0 = max(300 if k == 0 else 140, 180 + _txt_larg(nm.upper(), 50) / 2 + 120 * (k == 0))
        out.append(f'<g id="{pid}-m">{pos(corpo(pid, "anda", roupa=("#2D4A63", "#E0573E")[k], manga="curta", rnd=rnd), x0, y, esc)}'
                   f'<g transform="translate({x0} {y - 475 * esc - 50:.0f})"><g id="{pid}-t"><text class="tc" x="0" y="0" text-anchor="middle" font-size="50" fill="#1E2A3A">{_html.escape(nm.upper())}</text></g></g></g>')
        anda(c, pid, t, 0, D)
        alvo = 120 if k == 0 else 560   # no fim um à frente do outro: os nomes não se sobrepõem
        c.a(f"tl.to('#{pid}-m',{{x:{alvo},duration:{D:.2f},ease:'{'power1.out' if k == 0 else 'power2.in'}'}},{q(t)});")
    c.a(f"tl.fromTo('#{w}-cam',{{x:0}},{{x:-120,duration:{D:.2f},ease:'none'}},{q(t)});")
    an.som(tp, 'swish', 0.2)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}"><g id="{w}-cam">{"".join(out)}</g></g>')


def relogio_rapido(c, t, folhas=True):
    """Relógio de parede grande com os ponteiros girando rápido e folhinhas do calendário voando (o tempo passando)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'rr')
    D = max(0.5, t1 - t)
    out = [f'<g id="{w}-rel" transform="translate(540 1330)"><circle r="300" fill="#5A3E28"/><circle r="270" fill="#FBF6EA"/>'
           + ''.join(f'<rect x="-5" y="-260" width="10" height="{36 if k % 3 == 0 else 20}" fill="#3A2A1A" transform="rotate({k * 30})"/>' for k in range(12))
           + f'<g id="{w}-h"><rect x="-9" y="-150" width="18" height="160" rx="9" fill="#1E2A3A"/></g>'
           f'<g id="{w}-m"><rect x="-6" y="-230" width="12" height="240" rx="6" fill="#1E2A3A"/></g><circle r="18" fill="#B5523B"/></g>']
    c.a(f"tl.fromTo('#{w}-m',{{rotation:0}},{{rotation:{int(720 * D)},duration:{q(D)},ease:'none',svgOrigin:'0 0'}},{q(t)});")
    c.a(f"tl.fromTo('#{w}-h',{{rotation:0}},{{rotation:{int(60 * D)},duration:{q(D)},ease:'none',svgOrigin:'0 0'}},{q(t)});")
    for k in range(int(D / 0.3)):
        an.som(t + 0.3 * k, 'tique' if k % 2 else 'tique2', 0.1)
    if folhas:
        fol = ''.join(f'<g transform="translate({rnd_x} 1000)"><g class="{w}-f"><rect x="-60" y="-70" width="120" height="140" rx="6" fill="#FBF6EA"/><rect x="-60" y="-70" width="120" height="34" rx="6" fill="#B5523B"/></g></g>'
                      for rnd_x in (230, 850, 300, 780, 260, 820))
        out.append(fol)
        c.a(f"tl.fromTo('.{w}-f',{{y:0,x:0,rotation:0,opacity:1}},{{y:900,x:(i)=>[-60,60,-90,90,-40,40][i%6],rotation:(i)=>[-200,180,-260,240,-150,170][i%6],opacity:0,duration:1.6,ease:'power1.in',stagger:{{each:0.3,repeat:{max(1, int(D / 1.6))}}}}},{q(t)});")
    _entra_amb(c, w, t)
    # 08/11 (margem segura): o relógio (1030–1630) encaixa abaixo do letreiro e acima do pé do formato
    return _amb(c, bo.encaixa(f'<g id="{w}">{"".join(out)}</g>', (230, 1020, 850, 1640)))


def janelas(c, t, n=6, apaga=None, acesa=None, t_muda=None, silhuetas=True, topo=960):
    """Fachada à noite com várias janelas acesas e uma silhueta em cada (cada um na sua casa, o time, os clientes);
    apaga=[índices] apagam em t_muda; acesa=índice acende por último (o lead acordado às 23h). Cenário 'rua_noite' ou
    'cidade_noite'. topo = y do telhado (08/11: com um número grande `an.data` na cena, use topo≈1180 pro número
    não cair em cima da fachada escura)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'jn')
    dy = topo - 960
    tm = _T(t_muda) if t_muda is not None else t + 1.0
    out = [f'<rect x="60" y="{980 + dy}" width="960" height="{max(600, 900 - dy)}" fill="#2A2236"/><rect x="40" y="{topo}" width="1000" height="30" fill="#1C1626"/>']
    cols = 3
    for k in range(n):
        x = 140 + (k % cols) * 300
        y = 1040 + dy + (k // cols) * 330
        jid = f'{w}-j{k}'
        acende_tarde = acesa is not None and k == acesa
        out.append(f'<rect x="{x}" y="{y}" width="200" height="240" fill="#1A1424"/>'
                   f'<g id="{jid}" opacity="{0 if acende_tarde else 1}"><rect x="{x + 10}" y="{y + 10}" width="180" height="220" fill="#F2B544"/>'
                   + (f'<g transform="translate({x + 100} {y + 230})"><g class="{w}-sil"><circle cy="-120" r="34" fill="#2A1A10"/><path d="M-60 0 L-50 -70 Q0 -90 50 -70 L60 0Z" fill="#2A1A10"/></g></g>' if silhuetas else '')
                   + '</g>'
                   f'<rect x="{x}" y="{y}" width="200" height="240" fill="none" stroke="#3A2E48" stroke-width="12"/><rect x="{x + 96}" y="{y}" width="8" height="240" fill="#3A2E48"/>')
        if apaga and k in apaga:
            c.a(f"tl.to('#{jid}',{{opacity:0.08,duration:0.15,ease:'steps(1)'}},{q(tm + 0.2 * list(apaga).index(k))});")
        if acende_tarde:
            c.a(f"tl.to('#{jid}',{{opacity:1,duration:0.15,ease:'steps(1)'}},{q(tm)});")
            an.som(tm, 'tique2', 0.2)
    c.a(f"tl.fromTo('.{w}-sil',{{y:0}},{{y:-6,duration:1.3,yoyo:true,repeat:{max(1, int((t1 - t) / 1.3))},stagger:0.4,ease:'sine.inOut'}},{q(t)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}</g>')


def construcao(c, t, tempos=None, rotulo=''):
    """Vista de cima de um terreno virando prédio (time-lapse da referência): terreno vazio → fundação → paredes →
    telhado pronto, com caminhõezinhos indo e vindo. Cenário 'aereo'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cs')
    ts_ = _ts(tempos, 3, t, max(0.5, (t1 - t - 0.6) / 3))
    out = ['<rect x="250" y="1020" width="580" height="680" fill="#B08A5E"/><rect x="250" y="1020" width="580" height="680" fill="none" stroke="#8A6A45" stroke-width="10" stroke-dasharray="20 14"/>',
           f'<rect id="{w}-f" x="300" y="1070" width="480" height="580" fill="#9A9A92" opacity="0"/>',
           f'<g id="{w}-p" opacity="0"><rect x="300" y="1070" width="480" height="580" fill="none" stroke="#C9C4B8" stroke-width="26"/>'
           f'<rect x="530" y="1070" width="20" height="580" fill="#C9C4B8"/><rect x="300" y="1350" width="480" height="20" fill="#C9C4B8"/></g>',
           f'<g id="{w}-t" opacity="0"><rect x="300" y="1070" width="480" height="580" fill="#B5523B"/>'
           f'<path d="M300 1070 L460 1360 L300 1650Z" fill="#9E4632"/><path d="M780 1070 L620 1360 L780 1650Z" fill="#C4614A"/>'
           f'<path d="M300 1070 L460 1360 L620 1360 L780 1070 M300 1650 L460 1360 M620 1360 L780 1650" stroke="#8E3F2C" stroke-width="8" fill="none"/>'
           f'<rect x="452" y="1352" width="176" height="16" fill="#8E3F2C"/><rect x="660" y="1150" width="40" height="70" fill="#5A3E28"/></g>']
    for k, sid in enumerate(('f', 'p', 't')):
        c.a(f"tl.fromTo('#{w}-{sid}',{{opacity:0,scale:0.9}},{{opacity:1,scale:1,duration:0.4,ease:'back.out(1.6)',svgOrigin:'540 1360'}},{q(ts_[k])});")
        an.som(ts_[k], 'madeira', 0.18)
    cam = ''.join(f'<g id="{w}-c{k}"><rect x="-34" y="-18" width="68" height="36" rx="6" fill="#E9B53A"/><rect x="14" y="-14" width="18" height="28" rx="3" fill="#1E2A3A" opacity=".6"/></g>' for k in range(2))
    c.a(f"tl.fromTo('#{w}-c0',{{x:-100,y:1760}},{{x:1180,y:1760,duration:{max(1.0, t1 - t):.2f},ease:'none'}},{q(t)});")
    c.a(f"tl.fromTo('#{w}-c1',{{x:900,y:960,rotation:90}},{{x:900,y:1900,rotation:90,duration:{max(1.0, t1 - t):.2f},ease:'none'}},{q(t)});")
    tag = ''
    if rotulo:
        tag = _tag(f'{w}-r', 540, 1360, rotulo, '#FBF4E4')
        _pop(c, f'{w}-r', ts_[-1] + 0.2)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}{cam}{tag}</g>')


# ================================================================ CARTELAS E RÓTULOS
def pincel(c, t=None, cor='#E0573E', y=930):
    """Pincelada de tinta desenhando embaixo do letreiro (cartela preta da referência) + respingos. Vale como a
    'peça' da cena de frase em tela preta (an.cenario(c, 'preto'))."""
    t = c.t0 + 0.4 if t is None else _T(t)
    w = an._id(c, 'pn')
    d = f'M250 {y} C380 {y - 18} 560 {y + 14} 830 {y - 6}'
    out = (f'<path id="{w}-p" d="{d}" stroke="{cor}" stroke-width="22" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" opacity=".9"/>'
           + ''.join(f'<circle class="{w}-s" cx="{x}" cy="{y + dy}" r="{r}" fill="{cor}" opacity=".8"/>' for x, dy, r in ((850, -20, 7), (870, 10, 4), (232, 16, 5))))
    c.a(f"tl.fromTo('#{w}-p',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.45,ease:'power2.out'}},{q(t)});")
    c.a(f"tl.fromTo('.{w}-s',{{scale:0}},{{scale:1,duration:0.2,stagger:0.05,transformOrigin:'50% 50%'}},{q(t + 0.4)});")
    an.som(t, 'swish', 0.16)
    return _amb(c, f'<g id="{w}">{out}</g>')


def nome(c, t, titulo, sub='', alvo=None, lado='dir', y=1150):
    """Etiqueta de personagem (estilo 'TÁCITO / historiador romano' da referência): nome em sans condensada, fio de ouro
    e linha de apoio em versalete; com alvo=(x, y) um fio fino aponta pra pessoa."""
    t = _T(t)
    w = an._id(c, 'nm')
    tx = titulo.upper()
    lw = max(_txt_larg(tx, 64), _txt_larg(sub.upper(), 40) if sub else 0)
    x = 850 - lw if lado == "dir" else 230
    out = (f'<g transform="translate({x:.0f} {y})"><g id="{w}-g"><text class="tc" x="0" y="0" font-size="64" fill="#FBF6EA" style="paint-order:stroke" stroke="#1E2A3A" stroke-width="6">{_html.escape(tx)}</text>'
           f'<rect id="{w}-f" x="0" y="16" width="{lw:.0f}" height="5" fill="#F2B544"/>'
           + (f'<text class="tg" x="0" y="66" font-size="40" fill="#FBF6EA" letter-spacing="3" style="paint-order:stroke" stroke="#1E2A3A" stroke-width="5">{_html.escape(sub.upper())}</text>' if sub else '')
           + '</g></g>')
    if alvo:
        ax, ay = alvo
        ox = x + (0 if lado == 'dir' else lw)
        out = f'<path id="{w}-ln" d="M{ox:.0f} {y + 10} L{ax} {ay}" stroke="#FBF6EA" stroke-width="3" pathLength="1" stroke-dasharray="1 1"/><circle cx="{ax}" cy="{ay}" r="8" fill="#F2B544"/>' + out
        c.a(f"tl.fromTo('#{w}-ln',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.35}},{q(t)});")
    c.a(f"tl.fromTo('#{w}-g',{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.35,ease:'power3.out'}},{q(t)});")
    c.a(f"tl.fromTo('#{w}-f',{{scaleX:0}},{{scaleX:1,duration:0.35,svgOrigin:'0 18'}},{q(t + 0.15)});")
    an.som(t, 'swish', 0.12)
    return _amb(c, f'<g id="{w}">{out}</g>')


def selo_canto(c, texto, t=None, sub='', y=300):
    """Selo pequeno no canto de CIMA à esquerda (lugar/ano da referência: '1338', 'Vale do Chu'): caixa escura com o
    texto (ex.: 'Segunda-feira', '8h', 'Fim do mês'). y 300 = acima do letreiro no RL e ainda visível no GL/IN."""
    t = c.t0 + 0.3 if t is None else _T(t)
    w = an._id(c, 'sc')
    tx = texto.upper()
    lw = max(_txt_larg(tx, 52), (_txt_larg(sub.upper(), 34, 'serif') + 5 * len(sub)) if sub else 0) + 60
    h = 84 + (46 if sub else 0)
    # 08/11 (margem segura): no GL/YT/IN o alto do mundo sai da tela e o letreiro ocupa o topo — o selo vai pro canto
    # de BAIXO à esquerda (dentro da caixa segura); no RL fica em cima (y ≥ 250)
    if motor.FORMATO != 'RL':
        y = bo.faixa()[1] - h
    else:
        # 12/11 (regra do usuário: texto nunca lá em cima; caixa de texto do RL começa em y 320): no topo da faixa (340)
        # o zoom do cenário (origem embaixo) subia o selo até ~275 na tela (caso real, 'MANHÃ'); 430 = logo acima do
        # letreiro (~526) e abaixo de 320 mesmo com o cenário em 1,07
        y = max(y, bo.faixa()[0], 430)
    out = (f'<g transform="translate(170 {y})"><g id="{w}-g"><rect x="0" y="0" width="{lw:.0f}" height="{h}" rx="10" fill="#0A0F1E" opacity=".72"/>'
           f'<text class="tc" x="26" y="62" font-size="52" fill="#FBF6EA">{_html.escape(tx)}</text>'
           + (f'<text class="tg" x="26" y="112" font-size="34" fill="#E9DFC9" letter-spacing="5">{_html.escape(sub.upper())}</text>' if sub else '')
           + '</g></g>')
    c.a(f"tl.fromTo('#{w}-g',{{opacity:0,y:-16}},{{opacity:1,y:0,duration:0.3,ease:'power2.out'}},{q(t)});")
    an.som(t, 'tique', 0.16)
    return _amb(c, f'<g id="{w}">{out}</g>')


def definicao(c, t, palavra, sentido='', t_sentido=None):
    """Placa de pedra com a PALAVRA gravada (letras surgindo como cinzel) e a etiqueta do sentido do lado (estilo
    'MVNVS / DEVER' da referência). Bom com 'tarde', 'campo_tarde', 'capitulo_*'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'df')
    tx = palavra.upper()
    tam = 110
    while _txt_larg(tx, tam) > 520 and tam > 56:
        tam -= 4
    out = ('<path d="M250 1860 L250 1180 L540 1040 L830 1180 L830 1860Z" fill="#D9D2C2"/><path d="M250 1180 L540 1040 L830 1180Z" fill="#C4BBA8"/>'
           '<rect x="220" y="1830" width="640" height="60" fill="#B9B09C"/><rect x="300" y="1260" width="480" height="300" fill="#C9C0AE"/>'
           f'<text class="tg" id="{w}-p" x="540" y="{1410 + tam * 0.36:.0f}" text-anchor="middle" font-size="{tam}" fill="#5A5040" letter-spacing="6">{_html.escape(tx)}</text>'
           + ''.join(f'<path class="{w}-fl" d="M{x} 1850 q8 -30 0 -50" stroke="#F2B544" stroke-width="5" fill="none" opacity=".8"/>' for x in (440, 640)))
    c.a(f"tl.fromTo('#{w}-p',{{opacity:0,letterSpacing:40}},{{opacity:1,letterSpacing:6,duration:0.6,ease:'power2.out'}},{q(t)});")
    c.a(f"tl.fromTo('.{w}-fl',{{scaleY:0.7}},{{scaleY:1.2,duration:0.2,yoyo:true,repeat:{max(1, int((t1 - t) / 0.2))},transformOrigin:'50% 100%'}},{q(t)});")
    an.som(t, 'madeira', 0.2)
    tag = ''
    if sentido:
        gid = f'{w}-s'
        tag = _tag(gid, 760, 1700, sentido, '#B5523B', '#FBF6EA', rot=-3)
        _pop(c, gid, _T(t_sentido) if t_sentido is not None else t + 0.6)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{out}{tag}</g>')


def manchete(c, t, titulo, sub='', jornal='Notícias do Dia'):
    """Jornal (fictício, desenhado) que cai pregado na tela e balança: a manchete é a frase falada (≥ 64 px), colunas de
    texto em traço. Nunca nome de jornal real."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'mc')
    tx = titulo.upper()
    tam = 88
    linhas = [tx]
    while _txt_larg(tx, tam) > 600 and tam > 64:
        tam -= 4
    if _txt_larg(tx, tam) > 600:
        p = tx.split()
        meio = len(p) // 2
        linhas = [' '.join(p[:meio]), ' '.join(p[meio:])]
        tam = 72
        while max(_txt_larg(l, tam) for l in linhas) > 600 and tam > 52:
            tam -= 4
    X, Y, W_, H_ = 210, 990, 660, 860
    out = (f'<rect x="{X + 12}" y="{Y + 16}" width="{W_}" height="{H_}" fill="#000" opacity=".2"/><rect x="{X}" y="{Y}" width="{W_}" height="{H_}" fill="#F4EEDC"/>'
           f'<text class="tg" x="{X + W_ / 2}" y="{Y + 90}" text-anchor="middle" font-size="64" fill="#1E1A16">{_html.escape(jornal)}</text>'
           f'<rect x="{X + 30}" y="{Y + 116}" width="{W_ - 60}" height="4" fill="#1E1A16"/><rect x="{X + 30}" y="{Y + 126}" width="{W_ - 60}" height="2" fill="#1E1A16"/>'
           + ''.join(f'<text class="tc" x="{X + W_ / 2}" y="{Y + 210 + (tam + 10) * k:.0f}" text-anchor="middle" font-size="{tam}" fill="#1E1A16">{_html.escape(l)}</text>' for k, l in enumerate(linhas))
           + (f'<text class="tg" x="{X + W_ / 2}" y="{Y + 230 + (tam + 10) * len(linhas):.0f}" text-anchor="middle" font-size="48" fill="#3A3228">{_html.escape(sub)}</text>' if sub else '')
           + f'<rect x="{X + 30}" y="{Y + 330 + (tam + 10) * len(linhas):.0f}" width="280" height="200" fill="#8E8778"/>'
           + ''.join(f'<rect x="{X + 340}" y="{Y + 330 + (tam + 10) * len(linhas) + 24 * j:.0f}" width="{280 - 40 * (j % 3)}" height="8" fill="#9A9282"/>' for j in range(9))
           + ''.join(f'<rect x="{X + 30}" y="{Y + 560 + (tam + 10) * len(linhas) + 24 * j:.0f}" width="{W_ - 60 - 60 * (j % 2)}" height="8" fill="#9A9282"/>' for j in range(max(0, (H_ - 600 - (tam + 10) * len(linhas)) // 24))))
    # 07/11: o jornal com scale/giro no <g> não aparecia na snapshot; agora cai pregado e balança (padrão da placa)
    c.a(f"tl.fromTo('#{w}-g',{{opacity:0,y:-160,rotation:-14}},{{opacity:1,y:0,rotation:-3,duration:0.55,ease:'back.out(1.4)',svgOrigin:'540 990'}},{q(t)});")
    c.a(f"tl.to('#{w}-g',{{rotation:-1,duration:1.6,yoyo:true,repeat:{max(1, int((t1 - t) / 1.6))},ease:'sine.inOut',svgOrigin:'540 990'}},{q(t + 0.6)});")
    an.som(t, 'swish', 0.2)
    an.som(t + 0.65, 'impacto', 0.26)
    _entra_amb(c, w, t)
    # 08/11 (margem segura): o jornal inteiro encaixa abaixo do letreiro e acima do pé do formato
    return _amb(c, bo.encaixa(f'<g id="{w}"><g id="{w}-g">{out}<circle cx="540" cy="984" r="14" fill="#B03A2A"/></g></g>', (X - 20, Y - 60, X + W_ + 30, Y + H_ + 30)))   # -60: o jornal entra caindo e fica girado -3°


def placa_valor(c, t, cabecalho, valor, x=540, y=1250, t_valor=None):
    """Cartão de papel preso com tachinha: cabeçalho pequeno e o VALOR falado grande (estilo 'PELOS PLANOS / 12 HORAS')."""
    t = _T(t)
    w = an._id(c, 'pv')
    cab, val = cabecalho.upper(), valor.upper()
    tv = 110
    while _txt_larg(val, tv) > 560 and tv > 60:
        tv -= 4
    lw = max(_txt_larg(cab, 48), _txt_larg(val, tv)) + 90
    x = min(max(x, 230 + lw / 2), 850 - lw / 2)
    out = (f'<g transform="translate({x:.0f} {y})"><g id="{w}-g"><rect x="{-lw / 2 + 10:.0f}" y="-100" width="{lw:.0f}" height="{tv + 150}" fill="#000" opacity=".18"/>'
           f'<rect x="{-lw / 2:.0f}" y="-110" width="{lw:.0f}" height="{tv + 150}" fill="#F4EEDC"/>'
           f'<text class="tc" x="0" y="-42" text-anchor="middle" font-size="48" fill="#6A5A44" letter-spacing="3">{_html.escape(cab)}</text>'
           f'<text class="tc" id="{w}-v" x="0" y="{tv * 0.8:.0f}" text-anchor="middle" font-size="{tv}" fill="#1E1A16">{_html.escape(val)}</text>'
           f'<circle cx="0" cy="-118" r="16" fill="#B03A2A"/></g></g>')
    c.a(f"tl.fromTo('#{w}-g',{{opacity:0,y:-60,rotation:-8}},{{opacity:1,y:0,rotation:-2,duration:0.45,ease:'back.out(1.6)',svgOrigin:'0 -118'}},{q(t)});")
    tv_ = _T(t_valor) if t_valor is not None else t + 0.35
    c.a(f"tl.fromTo('#{w}-v',{{opacity:0,scale:1.3}},{{opacity:1,scale:1,duration:0.25,svgOrigin:'0 {tv * 0.5:.0f}'}},{q(tv_)});")
    c.a(f"tl.to('#{w}-g',{{rotation:1,duration:1.4,yoyo:true,repeat:{max(1, int((_fim(c) - t) / 1.4))},ease:'sine.inOut',svgOrigin:'0 -118'}},{q(t + 0.5)});")
    an.som(t, 'papel', 0.2)
    an.som(tv_, 'impacto', 0.2)
    return _amb(c, f'<g id="{w}">{out}</g>')


def numeros(c, pontos, cor='#F4EEDC'):
    """Círculos numerados (1, 2, 3...) aparecendo em cima de coisas da cena: pontos = [(x, y, t), ...]."""
    w = an._id(c, 'nu')
    out = ''
    for k, (x, y, tk) in enumerate(pontos):
        nid = f'{w}-{k}'
        out += (f'<g transform="translate({x} {y})"><g id="{nid}"><circle r="40" fill="{cor}" stroke="#1E2A3A" stroke-width="5"/>'
                f'<text class="tc" x="0" y="18" text-anchor="middle" font-size="52" fill="#1E2A3A">{k + 1}</text></g></g>')
        c.a(f"tl.fromTo('#{nid}',{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:0.3,ease:'back.out(3)'}},{q(_T(tk))});")
        an.som(_T(tk), 'pop2', 0.2)
    return _amb(c, f'<g id="{w}">{out}</g>')


def carimbo(c, t, texto='Aprovado', x=540, y=1500, cor='#B03A2A', rot=-12):
    """Carimbo batendo na tela (com tremida): APROVADO, PAGO, VENDIDO, AGENDADO — só o que combina com a fala."""
    t = _T(t)
    w = an._id(c, 'cb')
    tx = texto.upper()
    tam = 96
    while _txt_larg(tx, tam) > 520 and tam > 56:
        tam -= 4
    lw = _txt_larg(tx, tam) + 70
    x = min(max(x, 230 + lw / 2), 850 - lw / 2)
    # 08/11 (margem segura): o carimbo girado (meia altura ~ tam*0,85 + lw/2*sen(rot)) fica acima do pé do formato
    y = min(y, bo.faixa()[1] - (tam * 0.85 + lw / 2 * abs(math.sin(math.radians(rot)))) * 1.1)
    out = (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot})"><g id="{w}-g"><rect x="{-lw / 2:.0f}" y="{-tam * 0.85:.0f}" width="{lw:.0f}" height="{tam * 1.6:.0f}" rx="16" fill="none" stroke="{cor}" stroke-width="12"/>'
           f'<text class="tc" x="0" y="{tam * 0.36:.0f}" text-anchor="middle" font-size="{tam}" fill="{cor}">{_html.escape(tx)}</text></g></g>')
    c.a(f"tl.fromTo('#{w}-g',{{opacity:0,scale:1.4}},{{opacity:0.92,scale:1,duration:0.2,ease:'power4.in'}},{q(t)});")   # 08/11: era 2,4 (saía da margem ao bater)
    c.a(f"tl.fromTo('#{c.id} .cenario',{{rotation:0}},{{rotation:0.8,duration:0.05,yoyo:true,repeat:5}},{q(t + 0.2)});")
    an.som(t + 0.18, 'impacto', 0.3)
    return _amb(c, f'<g id="{w}">{out}</g>')


def citacao(c, t, texto, autor='', x=540, y=1150):
    """Cartão de papel preso com a FRASE entre aspas (citação da referência: "Bastava falar com eles…") e o autor
    embaixo. Use pra uma frase marcante que ele falou (ou de cliente, se ele citou)."""
    t = _T(t)
    w = an._id(c, 'qt')
    pal = texto.split()
    linhas, cur = [], ''
    for p_ in pal:
        tst = (cur + ' ' + p_).strip()
        if _txt_larg(('“' + tst + '”').upper(), 56) > 600 and cur:
            linhas.append(cur)
            cur = p_
        else:
            cur = tst
    linhas.append(cur)
    linhas[0] = '“' + linhas[0]
    linhas[-1] = linhas[-1] + '”'
    lw = max(_txt_larg(l.upper(), 56) for l in linhas) + 80
    lw = max(lw, _txt_larg(autor.upper(), 48) + 80 if autor else 0)
    h = 70 * len(linhas) + (90 if autor else 40) + 40
    x = min(max(x, 230 + lw / 2), 850 - lw / 2)
    out = (f'<g transform="translate({x - lw / 2:.0f} {y})"><g id="{w}-g"><rect x="10" y="12" width="{lw:.0f}" height="{h}" fill="#000" opacity=".18"/>'
           f'<rect width="{lw:.0f}" height="{h}" fill="#F4EEDC"/><rect width="{lw:.0f}" height="{h}" fill="none" stroke="#C9BEA6" stroke-width="3"/>'
           + ''.join(f'<text class="tc" x="40" y="{80 + 70 * k}" font-size="56" fill="#1E1A16">{_html.escape(l.upper())}</text>' for k, l in enumerate(linhas))
           + (f'<rect x="40" y="{60 + 70 * len(linhas)}" width="60" height="4" fill="#B03A2A"/>'
              f'<text class="tg" x="40" y="{116 + 70 * len(linhas)}" font-size="48" fill="#5A4A3A">{_html.escape(autor)}</text>' if autor else '')
           + f'<circle cx="{lw / 2:.0f}" cy="-6" r="14" fill="#B03A2A"/></g></g>')
    c.a(f"tl.fromTo('#{w}-g',{{opacity:0,y:-50,rotation:-6}},{{opacity:1,y:0,rotation:-1.5,duration:0.45,ease:'back.out(1.6)',svgOrigin:'{lw / 2:.0f} -6'}},{q(t)});")
    c.a(f"tl.to('#{w}-g',{{rotation:1,duration:1.6,yoyo:true,repeat:{max(1, int((_fim(c) - t) / 1.6))},ease:'sine.inOut',svgOrigin:'{lw / 2:.0f} -6'}},{q(t + 0.5)});")
    an.som(t, 'papel', 0.22)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{out}</g>')


def linha_tempo(c, t, inicio, fim, marcos=(), t_anda=None, rotulo=''):
    """Linha do tempo em barra de madeira/latão (a da referência, 476 → 1500): as pontas com o começo e o fim FALADOS
    ('3 anos atrás' → 'Hoje'), um marcador andando por ela e marcos (texto, fração 0–1, t) aparecendo em cima."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'lt')
    X0, X1, Y = 190, 890, 1380
    out = [f'<rect x="{X0 - 30}" y="{Y - 34}" width="{X1 - X0 + 60}" height="68" rx="34" fill="#5A3E28"/>',
           f'<rect x="{X0}" y="{Y - 16}" width="{X1 - X0}" height="32" rx="16" fill="#E9DFC6"/>',
           f'<rect id="{w}-p" x="{X0}" y="{Y - 16}" width="0" height="32" rx="16" fill="#C9A24A"/>']
    out += [f'<rect x="{X0 + (X1 - X0) * k / 10:.0f}" y="{Y + 22}" width="4" height="{22 if k % 5 == 0 else 12}" fill="#5A3E28"/>' for k in range(11)]
    for k, (txt, x) in enumerate(((inicio, X0), (fim, X1))):
        gid = f'{w}-e{k}'
        out.append(_tag(gid, _x(x, txt), Y + 120 + 110 * k, txt, '#FBF4E4' if k == 0 else '#B5523B', '#1E2A3A' if k == 0 else '#FBF6EA', livre=True))   # alturas diferentes: não encostam
        _pop(c, gid, t + 0.2 * k)
    ta = _T(t_anda) if t_anda is not None else t + 0.3
    D = max(0.8, t1 - ta - 0.2)
    out.append(f'<g id="{w}-m"><path d="M0 -70 L26 -110 L-26 -110Z" fill="#B03A2A"/><circle cy="-120" r="26" fill="#B03A2A"/><circle cy="-120" r="10" fill="#FBF6EA"/></g>')
    c.a(f"tl.set('#{w}-m',{{x:{X0},y:{Y}}},{q(c.t0)});tl.to('#{w}-m',{{x:{X1},duration:{D:.2f},ease:'power1.inOut'}},{q(ta)});")
    c.a(f"tl.to('#{w}-p',{{attr:{{width:{X1 - X0}}},duration:{D:.2f},ease:'power1.inOut'}},{q(ta)});")
    for k, (txt, fr, tk) in enumerate(marcos):
        gid = f'{w}-k{k}'
        x = X0 + (X1 - X0) * fr
        out.append(f'<path d="M{x:.0f} {Y - 40} L{x:.0f} {Y - 150}" stroke="#5A3E28" stroke-width="4"/>' + _tag(gid, _x(x, txt), Y - 200, txt, '#FBF4E4', livre=True))
        _pop(c, gid, _T(tk))
    if rotulo:
        out.append(f'<text class="tc" x="540" y="{Y - 300}" text-anchor="middle" font-size="56" fill="{TINTA}">{_html.escape(rotulo.upper())}</text>')
    an.som(ta, 'whoosh_lento', 0.12)
    _entra_amb(c, w, t)
    # 08/11 (margem segura): barra + pontas + marcos encaixam juntos (as pontas iam até y 1650)
    y_top = Y - (340 if rotulo else 250 if marcos else 150)
    return _amb(c, bo.encaixa(f'<g id="{w}">{"".join(out)}</g>', (X0 - 40, y_top, X1 + 40, Y + 120 + 110 + 50)))


def mao_escreve(c, t, linhas=('Plano',), t_fim=None, cor_papel='#F4EEDC', vela=True):
    """CLOSE em primeira pessoa: a mão escrevendo com a caneta numa folha na mesa (na referência, a pena no
    pergaminho); as palavras (FALADAS, curtas) vão aparecendo como letra cursiva serifada; vela/abajur do lado."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'me')
    tf = _T(t_fim) if t_fim is not None else max(t + 0.8, t1 - 0.4)
    pele = bo._visual()[0]
    # 08/11 (margem segura): a última linha escrita fica acima do pé do formato (RL 1470): a mesa inteira sobe o necessário
    o = min(0, bo.faixa()[1] - (1180 + 140 * (len(linhas) - 1) + 50 + 25))
    out = [f'<g transform="translate(0 {o})">',
           f'<rect x="-300" y="1040" width="1680" height="{960 - o}" fill="#5A3E28"/><rect x="-300" y="1040" width="1680" height="16" fill="#4A3220"/>',
           f'<g transform="rotate(-4 540 1460)"><rect x="210" y="1120" width="660" height="760" fill="#000" opacity=".2"/>'
           f'<rect x="200" y="1100" width="660" height="760" fill="{cor_papel}"/>'
           + ''.join(f'<rect x="250" y="{1180 + 70 * k}" width="560" height="2" fill="#C9BEA6"/>' for k in range(9))]
    n = len(linhas)
    seg = (tf - t) / max(1, n)
    for k, l in enumerate(linhas):
        tam = 76
        while _txt_larg(l, tam, 'serif') > 540 and tam > 50:
            tam -= 4
        lid = f'{w}-l{k}'
        out.append(f'<clipPath id="{lid}c"><rect id="{lid}r" x="240" y="{1180 + 140 * k + 50 - tam}" width="0" height="{tam * 1.45:.0f}"/></clipPath>'
                   f'<text class="tg" x="250" y="{1180 + 140 * k + 50}" font-size="{tam}" fill="#1E2A3A" font-style="italic" clip-path="url(#{lid}c)">{_html.escape(l)}</text>')
        c.a(f"tl.to('#{lid}r',{{attr:{{width:600}},duration:{seg * 0.9:.2f},ease:'none'}},{q(t + seg * k)});")
    out.append('</g>')
    # mão com a caneta acompanhando a escrita
    mao = (f'<g id="{w}-m"><g transform="rotate(-25)"><rect x="-8" y="-150" width="16" height="150" rx="6" fill="#1E2A3A"/><path d="M-8 0 L8 0 L0 20Z" fill="#C9A24A"/></g>'
           f'<ellipse cx="30" cy="-40" rx="60" ry="44" fill="{pele}"/><rect x="40" y="-60" width="360" height="90" rx="44" fill="#2D4A63" transform="rotate(20 40 -60)"/></g>')
    out.append(mao)
    for k in range(n):
        y = 1180 + 140 * k + 40
        c.a(f"tl.fromTo('#{w}-m',{{x:260,y:{y}}},{{x:780,y:{y - 30},duration:{seg * 0.9:.2f},ease:'none'}},{q(t + seg * k)});")
        c.a(f"tl.fromTo('#{w}-m',{{rotation:-4}},{{rotation:4,duration:0.12,yoyo:true,repeat:{max(1, int(seg * 0.9 / 0.12))},svgOrigin:'0 0'}},{q(t + seg * k)});")
    an.som(t, 'papel', 0.16)
    if vela:
        out.append('<g transform="translate(980 1180)"><rect x="-22" y="-120" width="44" height="120" fill="#F4EEDC"/>'
                   '<path class="ar-pisca" d="M0 -170 Q18 -146 0 -122 Q-18 -146 0 -170Z" fill="#F2B544"/><circle cy="-146" r="60" fill="#F2B544" opacity=".15"/></g>')
    out.append('</g>')
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}</g>')
