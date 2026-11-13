# -*- coding: utf-8 -*-
"""Ambientes novos do arsenal (07/11/2026). Mesmo contrato do bonecos.fundo(): devolve (camadas de trás, camada da frente),
em coordenadas de tela 1080x1920 (camadas com 300 px de sobra de cada lado). A faixa y 470–900 fica calma (é onde fica o
letreiro); ação de 950 pra baixo; o topo (120–440) tem o detalhe do lugar. Vida pelas classes ar-* (arsenal_animada).
Ambientes: campo, campo_tarde, porto, porto_tarde, fabrica, loja, cafe, transito, aereo, corte, preto, capitulo_vermelho,
capitulo_verde, tunel, casa, parque."""
import animada as an
import bonecos as bo

_c3 = bo._cam3
TINTA, CREME, OURO, FERRUGEM = an.TINTA, an.CREME, an.OURO, an.FERRUGEM

TEMAS = {   # tipo -> (claro?, cor do texto, cor do apoio, cor da chave, cor dos objetos, objeto destaque)
    'campo':             (True,  TINTA, '#2E3A30', '#9A4430', '#2D4A63', FERRUGEM),
    'campo_tarde':       (False, CREME, '#FBE9D0', OURO, CREME, OURO),
    'porto':             (True,  TINTA, '#2A3A48', '#9A4430', '#2D4A63', FERRUGEM),
    'porto_tarde':       (False, CREME, '#FBE9D0', OURO, CREME, OURO),
    'fabrica':           (True,  TINTA, '#2E3A36', '#9A4430', '#3B4E5E', FERRUGEM),
    'loja':              (True,  TINTA, '#3B3328', '#9A4430', '#3B4E5E', FERRUGEM),
    'cafe':              (False, CREME, '#E6DCC6', OURO, CREME, OURO),
    'transito':          (True,  TINTA, '#2A3A48', '#9A4430', '#2D4A63', FERRUGEM),
    'aereo':             (True,  TINTA, '#24321F', '#8E3A26', '#2D4A63', FERRUGEM),
    'corte':             (True,  TINTA, '#2A3A48', '#9A4430', '#2D4A63', FERRUGEM),
    'preto':             (False, '#F6EBD3', '#D8CFBD', '#E0573E', CREME, OURO),
    'capitulo_vermelho': (False, CREME, '#F2DCC8', OURO, CREME, OURO),
    'capitulo_verde':    (False, CREME, '#DCEBDD', OURO, CREME, OURO),
    'tunel':             (False, CREME, '#E6DCC6', OURO, CREME, OURO),
    'casa':              (True,  TINTA, '#3B3328', '#9A4430', '#3B4E5E', FERRUGEM),
    'parque':            (True,  TINTA, '#2E3A30', '#9A4430', '#2D4A63', FERRUGEM),
}


def _esc(c, f=0.82):
    return bo._esc(c, f)


def carro(x, y, cor='#B5523B', esc=1.0, dir_=1, farol=False):
    """Carrinho chapado de lado (x, y = chão no meio do carro), SEM a classe .carro (que o _vida do animada anima pelo
    índice). Ponha dentro de <g class="ar-anda" data-v="140"> pra andar."""
    teto = _esc(cor, 0.78)
    luz = '<path d="M46 -22 L150 -46 L150 4 Z" fill="#F7D98A" opacity=".25"/>' if farol else ''
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({esc * dir_:.2f} {esc:.2f})">{luz}'
            f'<ellipse cx="0" cy="2" rx="56" ry="6" fill="#000" opacity=".18"/>'
            f'<rect x="-50" y="-32" width="100" height="24" rx="7" fill="{cor}"/>'
            f'<path d="M-32 -32 L-20 -52 L20 -52 L34 -32Z" fill="{teto}"/>'
            f'<rect x="-15" y="-48" width="15" height="14" fill="#CFE3EA"/><rect x="4" y="-48" width="16" height="14" fill="#CFE3EA"/>'
            f'<circle cx="-29" cy="-8" r="10" fill="#1A1A1A"/><circle cx="29" cy="-8" r="10" fill="#1A1A1A"/>'
            f'<circle cx="-29" cy="-8" r="4" fill="#8A8A8A"/><circle cx="29" cy="-8" r="4" fill="#8A8A8A"/>'
            f'<circle cx="47" cy="-24" r="4" fill="#F7D98A"/><rect x="-50" y="-26" width="6" height="6" fill="#B03A2A"/></g>')


def caminhao(x, y, cor='#2D4A63', esc=1.0, dir_=1, texto=''):
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({esc * dir_:.2f} {esc:.2f})">'
            f'<ellipse cx="0" cy="2" rx="100" ry="7" fill="#000" opacity=".18"/>'
            f'<rect x="-100" y="-104" width="140" height="92" rx="4" fill="#EDE4D0"/><rect x="-100" y="-104" width="140" height="10" fill="{cor}"/>'
            f'<path d="M40 -76 L78 -76 L98 -44 L98 -12 L40 -12Z" fill="{cor}"/><path d="M48 -70 L74 -70 L88 -46 L48 -46Z" fill="#CFE3EA"/>'
            f'<circle cx="-66" cy="-8" r="13" fill="#1A1A1A"/><circle cx="-34" cy="-8" r="13" fill="#1A1A1A"/><circle cx="70" cy="-8" r="13" fill="#1A1A1A"/>'
            f'<circle cx="96" cy="-24" r="4" fill="#F7D98A"/></g>')


def _ceu_dia(rnd, tarde=False, n_nuv=5):
    if tarde:
        return [an._ceu('linear-gradient(#3C3F6B 0%,#B9627A 40%,#F0A35E 66%,#F7D49A 100%)',
                        '<div class="astro" style="top:300px;background:#FFE3A8;box-shadow:0 0 90px 30px #FFE3A855"></div>'),
                an._nuvens(rnd, '#F6B98C', n_nuv), an._aves(rnd, '#3A2238', 4)]
    return [an._ceu('linear-gradient(#8FC1D4 0%,#C9E0E4 52%,#EEE7D6 100%)',
                    '<div class="astro" style="top:80px;background:#FFF8E6;box-shadow:0 0 90px 30px #FFF8E655"></div>'),
            an._nuvens(rnd, '#FFFFFF', n_nuv), an._aves(rnd, '#2E3B4A', 4)]


def _gira(x, y, v, corpo):
    return f'<g class="ar-gira" data-v="{v}" data-o="{x} {y}">{corpo}</g>'


# ---------------------------------------------------------------- CAMPO
def campo(rnd, op, tarde=False):
    tarde = tarde or op.get('tarde')
    P = dict(m1='#9DB9B4', m2='#8DB07A', arv='#4F7F5C', somb='#3F6B4E', faixas=('#D5BE72', '#A9C483', '#C7AE66', '#8FB27A', '#DCC680'),
             estrada='#D9C9A2', celeiro='#B5523B') if not tarde else \
        dict(m1='#8E6A86', m2='#6E5A6A', arv='#3E4A3A', somb='#2E3A2E', faixas=('#B07A52', '#7E6E52', '#A06A48', '#6E6448', '#BC8A5A'),
             estrada='#A88A6A', celeiro='#8E3F2C')
    cam = _ceu_dia(rnd, tarde)
    A = (f'<g transform="translate(-300 960)">{an._montanhas(rnd, 1680, 300, 40, 170, 5, P["m1"])}</g>'
         f'<g transform="translate(-300 1040)">{an._montanhas(rnd, 1680, 240, 20, 90, 6, P["m2"], suave=True)}</g>')
    # campos em faixas com fileiras em perspectiva (ponto de fuga no horizonte)
    B = [f'<rect x="-300" y="1260" width="1680" height="660" fill="{P["faixas"][0]}"/>']
    ys = [1260, 1330, 1420, 1540, 1700, 1920]
    for k in range(len(ys) - 1):
        B.append(f'<rect x="-300" y="{ys[k]}" width="1680" height="{ys[k + 1] - ys[k]}" fill="{P["faixas"][k % 5]}"/>')
    for k in range(-14, 15):
        xb = 540 + k * 150
        B.append(f'<path d="M{540 + k * 26} 1262 L{xb} 1920" stroke="#000" stroke-opacity=".07" stroke-width="5"/>')
    B.append(f'<path d="M520 1262 C540 1400 380 1540 420 1920 L700 1920 C640 1560 600 1400 560 1262Z" fill="{P["estrada"]}"/>')
    # cerca
    B.append(''.join(f'<rect x="{x}" y="1440" width="12" height="80" fill="#6B4E31"/>' for x in range(-300, 1400, 70)))
    B.append('<rect x="-300" y="1456" width="1680" height="8" fill="#6B4E31"/><rect x="-300" y="1486" width="1680" height="8" fill="#6B4E31"/>')
    # celeiro + silo à esquerda, catavento à direita
    cx = 40
    B.append(f'<rect x="{cx}" y="1110" width="230" height="160" fill="{P["celeiro"]}"/><path d="M{cx - 14} 1114 L{cx + 115} 1030 L{cx + 244} 1114Z" fill="{_esc(P["celeiro"], 0.7)}"/>'
             f'<rect x="{cx + 80}" y="1170" width="70" height="100" fill="#FBF6EA"/><path d="M{cx + 80} 1170 L{cx + 150} 1270 M{cx + 150} 1170 L{cx + 80} 1270" stroke="{P["celeiro"]}" stroke-width="8"/>'
             f'<rect x="{cx + 250}" y="1060" width="60" height="210" rx="6" fill="#C8C0AF"/><path d="M{cx + 250} 1064 Q{cx + 280} 1030 {cx + 310} 1064Z" fill="#9A9282"/>')
    wx, wy = 900, 1010
    pas = ''.join(f'<path d="M0 0 L-14 -150 L14 -150Z" fill="#FBF6EA" transform="rotate({a})"/>' for a in (0, 90, 180, 270))
    B.append(f'<path d="M{wx - 30} 1290 L{wx - 6} {wy} L{wx + 6} {wy} L{wx + 30} 1290Z" fill="#8A8A8A"/>'
             f'<g transform="translate({wx} {wy})">{_gira(0, 0, 70, pas)}<circle r="12" fill="#5A5F66"/></g>')
    B.append(''.join(bo._arvore(x, y, h, P['arv'], P['somb'], rnd) for x, y, h in ((380, 1250, 200), (700, 1255, 170), (1200, 1250, 220), (-200, 1270, 240))))
    C = ''.join(f'<path d="M{x} 1930 Q{x + 10} 1850 {x - 20} 1800 Q{x + 30} 1860 {x + 30} 1930 Q{x + 50} 1840 {x + 80} 1810 Q{x + 60} 1880 {x + 70} 1930Z" '
                f'fill="{P["somb"]}"/>' for x in (-120, -40, 1080, 1160))
    return cam + [_c3(A, 10), _c3(''.join(B), 50, 'piso')], _c3(C, 85)


# ---------------------------------------------------------------- PORTO
def porto(rnd, op, tarde=False):
    tarde = tarde or op.get('tarde')
    mar, mar2 = ('#3E6F86', '#2D5770') if not tarde else ('#6A4E6E', '#4A3656')
    cam = _ceu_dia(rnd, tarde, 4)
    hor = 1180
    A = (f'<g transform="translate(-300 {hor - 260})">{an._montanhas(rnd, 1680, 260, 0, 140, 4, "#9DB4BC" if not tarde else "#7E5E7A", suave=True)}</g>'
         f'<g transform="translate(-300 {hor - 200})">{an._predios(rnd, 1680, 200, 0, 40, 150, "#8DA7B2" if not tarde else "#5E4A66", wmin=40, wmax=90)}</g>')
    B = [f'<rect x="-300" y="{hor}" width="1680" height="{1920 - hor}" fill="{mar}"/>',
         f'<rect x="-300" y="{hor + 260}" width="1680" height="{1920 - hor - 260}" fill="{mar2}"/>']
    for k in range(26):
        y = hor + 30 + (k * 29) % 700
        x = rnd.uniform(-280, 1300)
        B.append(f'<g class="ar-onda"><rect x="{x:.0f}" y="{y}" width="{rnd.uniform(60, 160):.0f}" height="5" rx="2" fill="#FFFFFF" opacity=".22"/></g>')
    # navio de carga atravessando longe
    nav = (f'<g transform="translate(-60 {hor + 70})"><path d="M0 0 L520 0 L480 46 L30 46Z" fill="#2A3340"/><rect x="20" y="-8" width="470" height="10" fill="#B5523B"/>'
           + ''.join(f'<rect x="{40 + 52 * j}" y="{-46 - 38 * (j % 2)}" width="48" height="{38 + 38 * (j % 2)}" fill="{("#C9A24A", "#B5523B", "#2D4A63", "#5B7F6E")[j % 4]}"/>' for j in range(7))
           + '<rect x="420" y="-70" width="56" height="64" fill="#EDE4D0"/><rect x="434" y="-96" width="14" height="30" fill="#2A3340"/>'
           + '<path d="M30 52 L480 52 L470 70 L40 70Z" fill="#000" opacity=".18"/></g>')
    B.append(f'<g class="ar-anda" data-v="14">{nav}</g>')
    # píer de madeira à direita com guindaste e contêineres
    B.append('<path d="M640 1480 L1400 1480 L1400 1920 L560 1920Z" fill="#8A6A45"/>'
             + ''.join(f'<path d="M{620 + k * 90} 1480 L{560 + k * 112} 1920" stroke="#6B4E31" stroke-width="4"/>' for k in range(10))
             + '<rect x="640" y="1470" width="760" height="16" fill="#6B4E31"/>'
             + ''.join(f'<rect x="{x}" y="1486" width="18" height="160" fill="#5A3E28"/>' for x in (660, 820, 980, 1140)))
    gru = ('<rect x="820" y="1040" width="22" height="440" fill="#C9A24A"/><rect x="960" y="1040" width="22" height="440" fill="#C9A24A"/>'
           '<rect x="700" y="1020" width="340" height="26" fill="#C9A24A"/>'
           + ''.join(f'<path d="M{820} {1060 + 40 * j} l22 40 M{960} {1060 + 40 * j} l22 40" stroke="#9C7A2E" stroke-width="4"/>' for j in range(10))
           + '<g class="ar-balanca" data-a="4" data-o="760 1046"><path d="M760 1046 L760 1180" stroke="#2A2A2A" stroke-width="4"/>'
             '<rect x="712" y="1180" width="96" height="56" fill="#B5523B"/><rect x="712" y="1180" width="96" height="10" fill="#8E3F2C"/></g>')
    B.append(gru)
    cont = ''
    for j, (x, y, cor) in enumerate(((870, 1416, '#2D4A63'), (990, 1416, '#5B7F6E'), (930, 1352, '#B5523B'), (1110, 1416, '#C9A24A'))):
        cont += (f'<rect x="{x}" y="{y}" width="116" height="64" fill="{cor}"/>'
                 + ''.join(f'<rect x="{x + 8 + 14 * k}" y="{y + 6}" width="4" height="52" fill="{_esc(cor, 0.8)}"/>' for k in range(8)))
    B.append(cont)
    B.append(''.join(f'<rect x="{x}" y="1452" width="22" height="22" rx="6" fill="#3A3A3A"/>' for x in (680, 1300)))
    C = ('<path d="M-300 1830 Q-100 1800 100 1840 L100 1920 L-300 1920Z" fill="#5A4A3A"/>'
         + ''.join(f'<rect x="{x}" y="1790" width="16" height="140" fill="#4A3A2C"/>' for x in (-60, 40)))
    return cam + [_c3(A, 12), _c3(''.join(B), 50, 'piso')], _c3(C, 85)


# ---------------------------------------------------------------- FÁBRICA
def _engrenagem(x, y, r, dentes, cor, v, furo='#2A2A2A'):
    d = ''.join(f'<rect x="{-r * 0.16:.0f}" y="{-r - r * 0.22:.0f}" width="{r * 0.32:.0f}" height="{r * 0.4:.0f}" rx="3" fill="{cor}" transform="rotate({360 * k / dentes:.1f})"/>'
                for k in range(dentes))
    return (f'<g transform="translate({x} {y})">' + _gira(0, 0, v, f'{d}<circle r="{r}" fill="{cor}"/><circle r="{r * 0.62:.0f}" fill="{_esc(cor, 0.85)}"/>'
            + ''.join(f'<rect x="-3" y="{-r * 0.62:.0f}" width="6" height="{r * 1.24:.0f}" fill="{_esc(cor, 0.7)}" transform="rotate({a})"/>' for a in (0, 60, 120))
            + f'<circle r="{r * 0.18:.0f}" fill="{furo}"/>') + '</g>')


def fabrica(rnd, op):
    A = ['<rect x="-300" y="0" width="1680" height="1400" fill="#CDD3C8"/>',
         '<rect x="-300" y="0" width="1680" height="470" fill="#7E8A86"/>']
    for x in range(-300, 1400, 240):   # telhado dente de serra com vidro
        A.append(f'<path d="M{x} 470 L{x} 150 L{x + 240} 330 L{x + 240} 470Z" fill="#6E7A76"/><path d="M{x + 8} 330 L{x + 8} 175 L{x + 120} 260 L{x + 120} 400Z" fill="#E8EDE6" opacity=".55"/>')
    A.append('<rect x="-300" y="440" width="1680" height="30" fill="#3E4650"/>'
             + ''.join(f'<path d="M{x} 470 L{x + 60} 440 L{x + 120} 470" stroke="#3E4650" stroke-width="6" fill="none"/>' for x in range(-300, 1400, 120)))
    A.append('<rect x="-300" y="905" width="1680" height="12" fill="#B9BFB4"/>')
    # canos na parede com vapor
    A.append('<rect x="-300" y="960" width="1680" height="22" fill="#8E3F2C"/><rect x="-300" y="1000" width="1680" height="14" fill="#5B7F6E"/>'
             + ''.join(f'<rect x="{x}" y="955" width="30" height="32" rx="4" fill="#6E2E20"/>' for x in range(-280, 1400, 260)))
    A.append(''.join(f'<circle class="ar-fuma" cx="{x}" cy="940" r="26" fill="#FFFFFF" opacity=".0"/>' for x in (120, 140, 960, 980)))
    # máquinas: prensa à esquerda, engrenagens no meio-direita
    A.append('<rect x="-120" y="1060" width="320" height="340" rx="10" fill="#3B5A6E"/><rect x="-80" y="1100" width="240" height="90" rx="6" fill="#2D4A63"/>'
             '<rect x="-40" y="1120" width="70" height="50" fill="#8FE0B0" class="ar-pisca"/><circle cx="110" cy="1145" r="16" fill="#F2B544" class="ar-pisca"/>'
             '<rect x="-120" y="1280" width="320" height="18" fill="#E9B53A"/>'
             + ''.join(f'<path d="M{-120 + 40 * k} 1280 l20 18" stroke="#2A2A2A" stroke-width="8"/>' for k in range(8)))
    A.append(_engrenagem(860, 1180, 110, 12, '#8A8F96', 40) + _engrenagem(1010, 1080, 70, 9, '#C9A24A', -63) + _engrenagem(700, 1300, 60, 8, '#B5523B', -73))
    L = ''.join(bo._pendente(x, comp, '#3A3A3A', luz=True) for x, comp in ((240, 360), (640, 360), (-120, 330), (1040, 330)))
    B = (bo._piso(1400, '#9E9E96', '#8E8E86', tabuas=False)
         + '<path d="M-300 1600 L1380 1600" stroke="#E9B53A" stroke-width="10"/><path d="M-300 1880 L1380 1880" stroke="#E9B53A" stroke-width="12"/>')
    C = ''.join(f'<g transform="translate({x} 1940)"><rect x="-90" y="-130" width="180" height="130" fill="#C49A62"/><rect x="-90" y="-130" width="180" height="16" fill="#A87F4A"/>'
                f'<path d="M-90 -130 L90 0 M90 -130 L-90 0" stroke="#A87F4A" stroke-width="8"/></g>' for x in (-70, 1150))
    return [_c3(''.join(A), 18), _c3(L, 30), _c3(B, 50, 'piso')], _c3(C, 85)


# ---------------------------------------------------------------- LOJA (por dentro)
def _produtos(rnd, x0, x1, y_prat, h0=40, h1=90):
    out, x = [], x0
    cores = ('#B5523B', '#2D4A63', '#C9A24A', '#5B7F6E', '#E9E4D8', '#8E6A9A', '#D9822B')
    while x < x1:
        w, h = rnd.uniform(26, 54), rnd.uniform(h0, h1)
        cor = rnd.choice(cores)
        if rnd.random() < 0.35:   # pote/garrafa
            out.append(f'<rect x="{x:.0f}" y="{y_prat - h:.0f}" width="{w * 0.8:.0f}" height="{h:.0f}" rx="{w * 0.3:.0f}" fill="{cor}"/>'
                       f'<rect x="{x + w * 0.15:.0f}" y="{y_prat - h * 0.6:.0f}" width="{w * 0.5:.0f}" height="{h * 0.25:.0f}" fill="#FBF6EA" opacity=".8"/>')
        else:
            out.append(f'<rect x="{x:.0f}" y="{y_prat - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{cor}"/>'
                       f'<rect x="{x + 4:.0f}" y="{y_prat - h + 8:.0f}" width="{w - 8:.0f}" height="8" fill="#FBF6EA" opacity=".6"/>')
        x += w + 3
    return ''.join(out)


def loja(rnd, op):
    A = ['<rect x="-300" y="0" width="1680" height="1400" fill="#EFE2C8"/><rect x="-300" y="0" width="1680" height="80" fill="#D9C8A6"/>']
    # topo: prateleiras altas de parede a parede com produtos e plaquinhas sem palavra
    for y in (220, 360):
        A.append(f'<rect x="-300" y="{y}" width="1680" height="14" fill="#8A6A45"/>' + _produtos(rnd, -290, 1380, y))
    A.append('<rect x="-300" y="430" width="1680" height="22" fill="#B5523B"/>'
             + ''.join(f'<rect x="{x}" y="430" width="40" height="22" fill="#FBF6EA"/>' for x in range(-300, 1400, 80)))
    # embaixo: gôndolas nas laterais
    for bx in (-300, 900):
        A.append(f'<rect x="{bx}" y="960" width="480" height="440" fill="#B79A6E"/>')
        for y in (1060, 1180, 1300, 1400):
            A.append(f'<rect x="{bx}" y="{y - 8}" width="480" height="10" fill="#6B4E31"/>' + _produtos(rnd, bx + 10, bx + 470, y - 8, 50, 90))
    A.append('<rect x="-300" y="1382" width="1680" height="18" fill="#6B5A48"/>')
    L = ''.join(bo._pendente(x, comp, '#2D4A63', luz=True) for x, comp in ((330, 360), (750, 360)))
    xadrez = ''.join(f'<rect x="{x}" y="{y}" width="120" height="{60 + (y - 1400) // 7}" fill="#C9BEA6" opacity=".7"/>'
                     for y in range(1400, 1920, 110) for x in range(-300 + (120 if (y // 110) % 2 else 0), 1400, 240))
    B = bo._piso(1400, '#E2D7C0', '#CFC3AA', tabuas=False) + xadrez
    C = bo._vaso(-40, 1960, 280, rnd)
    return [_c3(''.join(A), 18), _c3(L, 30), _c3(B, 50, 'piso')], _c3(C, 85)


# ---------------------------------------------------------------- CAFÉ / PADARIA (fim de tarde, quente)
def cafe(rnd, op):
    A = ['<rect x="-300" y="0" width="1680" height="1400" fill="#3A2A24"/><rect x="-300" y="0" width="1680" height="80" fill="#2A1E1A"/>']
    # quadros-negros do cardápio (só rabiscos, sem palavra)
    for x in (-240, 120, 480, 840, 1200):
        A.append(f'<rect x="{x}" y="140" width="300" height="250" rx="6" fill="#26332C" stroke="#6B4E31" stroke-width="12"/>'
                 + ''.join(f'<rect x="{x + 30}" y="{180 + 36 * j}" width="{rnd.uniform(100, 230):.0f}" height="8" rx="4" fill="#E9E4D8" opacity=".55"/>' for j in range(5))
                 + f'<circle cx="{x + 250}" cy="{196}" r="14" fill="#F2B544" opacity=".7"/>')
    A.append('<rect x="-300" y="440" width="1680" height="12" fill="#6B4E31"/>')
    # balcão do fundo com máquina de espresso e vitrine
    A.append('<rect x="-300" y="1080" width="1680" height="320" fill="#6B4E31"/><rect x="-300" y="1066" width="1680" height="18" fill="#8A6A45"/>'
             '<rect x="-180" y="940" width="260" height="130" rx="10" fill="#B9BFC4"/><rect x="-160" y="960" width="220" height="40" rx="6" fill="#8A8F96"/>'
             '<rect x="-120" y="1000" width="20" height="40" fill="#3A3A3A"/><rect x="0" y="1000" width="20" height="40" fill="#3A3A3A"/>'
             '<circle class="ar-fuma" cx="-110" cy="930" r="22" fill="#FFFFFF"/><circle class="ar-fuma" cx="10" cy="930" r="22" fill="#FFFFFF"/>'
             '<rect x="760" y="960" width="420" height="110" rx="8" fill="#F2E6C8" opacity=".85"/>'
             + ''.join(f'<ellipse cx="{800 + 70 * k}" cy="1040" rx="28" ry="16" fill="{("#C98B4A", "#E0B070", "#8A5A2B")[k % 3]}"/>' for k in range(6))
             + '<rect x="760" y="960" width="420" height="110" rx="8" fill="#FFFFFF" opacity=".12"/>'
             '<rect x="-300" y="1382" width="1680" height="18" fill="#2A1E1A"/>')
    L = ''.join(bo._pendente(x, comp, '#C9A24A', luz=True) for x, comp in ((150, 360), (540, 380), (930, 360)))
    B = bo._piso(1400, '#6E4E36', '#5E422E')
    C = bo._vaso(1130, 1990, 260, rnd)
    return [_c3(''.join(A), 18), _c3(L, 30), _c3(B, 50, 'piso')], _c3(C, 85)


# ---------------------------------------------------------------- TRÂNSITO (viaduto + avenida)
def transito(rnd, op):
    parado = op.get('parado', False)
    cam = _ceu_dia(rnd, op.get('tarde', False), 4)
    A = f'<g transform="translate(-300 600)">{an._predios(rnd, 1680, 600, 0, 200, 520, "#A9C2CB", janela=("#8DA7B2", "#E9DFC6"), acesas=0.15, wmin=70, wmax=150)}</g>'
    # viaduto no meio (carros pequenos) e avenida na frente (carros grandes)
    vy = 1230
    B = [f'<rect x="-300" y="{vy}" width="1680" height="40" fill="#8E8A82"/><rect x="-300" y="{vy - 14}" width="1680" height="14" fill="#B9B4A8"/>'
         + ''.join(f'<rect x="{x}" y="{vy + 40}" width="40" height="230" fill="#8E8A82"/>' for x in range(-260, 1400, 330))
         + f'<rect x="-300" y="1500" width="1680" height="420" fill="#5B616B"/><rect x="-300" y="1490" width="1680" height="14" fill="#9A9282"/>'
         + ''.join(f'<rect x="{x}" y="1690" width="80" height="10" fill="#E9DFC6" opacity=".7"/>' for x in range(-300, 1400, 160))]
    cores = ('#B5523B', '#2D4A63', '#C9A24A', '#5B7F6E', '#E9E4D8', '#8E6A9A', '#3B3B3B')
    for faixa, (y, esc, v, n) in enumerate(((vy - 4, 0.8, 120, 6), (1640, 1.7, -150, 4), (1830, 1.9, 170, 4))):
        v = v * (0.12 if parado else 1)
        xs = [-200 + k * (1700 / n) + rnd.uniform(-40, 40) for k in range(n)]
        if not parado:
            xs += [x - 1700 * (1 if v > 0 else -1) for x in xs]
        carros = ''.join((caminhao(x, y, rnd.choice(cores), esc * 0.8, 1 if v > 0 else -1) if rnd.random() < 0.2 else
                          carro(x, y, rnd.choice(cores), esc, 1 if v > 0 else -1)) for x in xs)
        B.append(f'<g class="ar-anda" data-v="{v:.0f}">{carros}</g>')
    # semáforo
    B.append('<rect x="980" y="1180" width="16" height="330" fill="#2E3640"/><rect x="956" y="1100" width="64" height="150" rx="10" fill="#2E3640"/>'
             f'<circle cx="988" cy="1130" r="18" fill="{"#E0573E" if parado else "#5A2A24"}" class="ar-pisca"/><circle cx="988" cy="1175" r="18" fill="#5A4A24"/>'
             f'<circle cx="988" cy="1220" r="18" fill="{"#2A4A34" if parado else "#4FBF7A"}"/>')
    return cam + [_c3(A, 12), _c3(''.join(B), 50, 'piso')], ''


# ---------------------------------------------------------------- VISTA AÉREA (de cima)
def aereo(rnd, op):
    A = ['<rect x="-300" y="0" width="1680" height="1920" fill="#CFC6AE"/>']
    ruas_y = (300, 960, 1380, 1760)
    ruas_x = (-120, 230, 600, 960, 1260)
    for y in ruas_y:
        A.append(f'<rect x="-300" y="{y - 34}" width="1680" height="68" fill="#6E6E6A"/>'
                 + ''.join(f'<rect x="{x}" y="{y - 3}" width="40" height="6" fill="#E9DFC6"/>' for x in range(-300, 1400, 90)))
    for x in ruas_x:
        A.append(f'<rect x="{x - 30}" y="0" width="60" height="1920" fill="#6E6E6A"/>')
    # quadras com telhados (sombra dura pra direita/baixo)
    for gy0, gy1 in ((0, 266), (994, 1346), (1414, 1726), (1794, 1920)):
        for gx0, gx1 in zip((-300,) + tuple(x + 30 for x in ruas_x), tuple(x - 30 for x in ruas_x) + (1380,)):
            if gx1 - gx0 < 60:
                continue
            x = gx0 + 14
            while x < gx1 - 40:
                w = min(gx1 - 14 - x, rnd.uniform(70, 150))
                y = gy0 + 14
                while y < gy1 - 30:
                    h = min(gy1 - 14 - y, rnd.uniform(70, 140))
                    cor = rnd.choice(('#B5523B', '#C98B6B', '#9DA6A8', '#D9C69A', '#8E8A82', '#A87F4A'))
                    if rnd.random() < 0.15:
                        A.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="#9DBF8A"/>'
                                 f'<circle cx="{x + w / 2:.0f}" cy="{y + h / 2:.0f}" r="{min(w, h) * 0.3:.0f}" fill="#5B8F66"/>')
                    else:
                        A.append(f'<rect x="{x + 8:.0f}" y="{y + 8:.0f}" width="{w:.0f}" height="{h:.0f}" fill="#000" opacity=".18"/>'
                                 f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{cor}"/>'
                                 f'<rect x="{x:.0f}" y="{y + h / 2 - 2:.0f}" width="{w:.0f}" height="4" fill="{_esc(cor, 0.8)}"/>')
                    y += h + 10
                x += w + 10
    # parque na faixa do letreiro (calma)
    A.append('<rect x="-300" y="430" width="1680" height="496" fill="#B7CF9C"/>'
             + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#7FA36A"/><circle cx="{x + 6}" cy="{y + 8}" r="{r * 0.7:.0f}" fill="#6E9459"/>'
                       for x, y, r in ((-240, 480, 46), (-170, 880, 40), (60, 470, 30), (1020, 480, 40), (1180, 870, 50), (1300, 520, 38), (110, 890, 28), (990, 890, 30)))
             + '<path d="M-300 900 C200 860 800 940 1380 880" stroke="#D9CDA8" stroke-width="22" fill="none"/>')
    B = []
    cores = ('#B5523B', '#2D4A63', '#C9A24A', '#E9E4D8', '#5B7F6E')
    for y, v in ((ruas_y[2] - 14, 160), (ruas_y[2] + 14, -140), (ruas_y[3] - 14, 130), (ruas_y[1] + 14, -150)):
        xs = [rnd.uniform(-300, 1380) for _ in range(4)]
        xs += [x - 1700 * (1 if v > 0 else -1) for x in xs]
        car = ''.join(f'<g transform="translate({x:.0f} {y})"><rect x="-26" y="-12" width="52" height="24" rx="6" fill="{rnd.choice(cores)}"/>'
                      f'<rect x="{-6 if v > 0 else -14}" y="-9" width="20" height="18" rx="3" fill="#1E2A3A" opacity=".6"/></g>' for x in xs)
        B.append(f'<g class="ar-anda" data-v="{v}">{car}</g>')
    return [_c3(''.join(A), 14), _c3(''.join(B), 50, 'piso')], ''


# ---------------------------------------------------------------- PRÉDIO EM CORTE (casa de bonecas)
ANDARES = ((1000, 1280), (1300, 1580), (1600, 1880))   # (teto, chão) de cada andar; a cena põe gente neles
# 08/11 (margem segura): no RL o térreo inteiro ficava abaixo de y 1500 (a interface do Reels cobre) — lá o prédio é um
# pouco mais baixo e sobe; embaixo dele, calçada e rua até o pé da tela
ANDARES_RL = ((900, 1125), (1145, 1370), (1390, 1615))   # telhado em ~830: abaixo do letreiro (pé ~760–800)


def andares():
    import motor
    return ANDARES_RL if motor.FORMATO == 'RL' else ANDARES


def corte(rnd, op):
    cam = _ceu_dia(rnd, False, 4)
    AND = andares()
    top, chao = AND[0][0], AND[-1][1]
    A = f'<g transform="translate(-300 {560 - (1000 - top)})">{an._predios(rnd, 1680, 420, 0, 120, 360, "#B7CCD4", wmin=70, wmax=150)}</g>'
    cores = op.get('cores', ('#E9D9BF', '#D5DDD6', '#EADCC0'))
    B = [f'<rect x="-300" y="{chao}" width="1680" height="{1920 - chao}" fill="#5B616B"/><rect x="-300" y="{chao - 8}" width="1680" height="10" fill="#9A9282"/>'
         + (f'<rect x="-300" y="{chao + 2}" width="1680" height="70" fill="#9A9282"/>'
            + ''.join(f'<rect x="{x}" y="{chao + 150}" width="90" height="10" fill="#E9DFC6" opacity=".7"/>' for x in range(-300, 1400, 170))
            if chao < 1800 else ''),
         f'<rect x="90" y="{top - 70}" width="900" height="70" fill="#4A5A66"/><rect x="70" y="{top - 80}" width="940" height="16" fill="#3A4650"/>'
         f'<rect x="760" y="{top - 140}" width="90" height="60" fill="#8E8A82"/><rect x="190" y="{top - 120}" width="12" height="40" fill="#3A4650"/>']
    for k, (y0, y1) in enumerate(AND):
        cor = cores[k % len(cores)]
        B.append(f'<rect x="110" y="{y0}" width="860" height="{y1 - y0}" fill="{cor}"/>'
                 f'<rect x="110" y="{y1 - 90}" width="860" height="90" fill="{_esc(cor, 0.9)}"/>'
                 f'<rect x="90" y="{y1}" width="900" height="20" fill="#8E8A82"/>'
                 f'<rect x="170" y="{y0 + 40}" width="150" height="110" fill="#BFDCE6"/><rect x="170" y="{y0 + 40}" width="150" height="110" fill="none" stroke="#6B5A48" stroke-width="8"/>'
                 f'<rect x="760" y="{y0 + 40}" width="110" height="80" fill="{_esc(cor, 0.75)}"/>'
                 f'<rect x="534" y="{y0}" width="4" height="40" fill="#3A3A3A"/><path d="M506 {y0 + 40} L566 {y0 + 40} L552 {y0 + 20} L520 {y0 + 20}Z" fill="#3A3A3A"/>'
                 f'<ellipse cx="536" cy="{y0 + 42}" rx="30" ry="6" fill="#F7D98A"/>')
    B.append(f'<rect x="90" y="{top - 70}" width="22" height="{chao - top + 90}" fill="#5A646C"/><rect x="968" y="{top - 70}" width="22" height="{chao - top + 90}" fill="#5A646C"/>')
    # árvores e poste na calçada
    B.append(''.join(bo._arvore(x, chao + 40 if chao < 1800 else 1880, h, '#4F7F5C', '#3F6B4E', rnd) for x, h in ((-160, 380), (1220, 360))))
    return cam + [_c3(A, 12), _c3(''.join(B), 50, 'piso')], ''


# ---------------------------------------------------------------- CARTELAS (preto, capítulos coloridos)
def preto(rnd, op):
    return [an._ceu('radial-gradient(ellipse 80% 70% at 50% 45%,#1A1714 0%,#0C0B0A 70%,#050505 100%)', '<div class="grao"></div>'),
            _c3(''.join(f'<circle cx="{rnd.uniform(-280, 1360):.0f}" cy="{rnd.uniform(950, 1900):.0f}" r="{rnd.choice((2, 3, 4))}" fill="#F2B544" opacity="{rnd.uniform(.15, .45):.2f}" class="ar-bob"/>'
                        for _ in range(24)), 6, 'piso')], ''


def _capitulo_cor(rnd, op, grad, silhueta):
    morros = an._montanhas(rnd, 1680, 360, 0, 120, 6, silhueta, suave=True)
    arvs = ''.join(f'<path d="M{x} 1920 L{x} {y} M{x} {y + 60} L{x - 40} {y + 10} M{x} {y + 90} L{x + 36} {y + 40}" stroke="{silhueta}" stroke-width="10" fill="none" stroke-linecap="round"/>'
                   for x, y in ((-140, 1500), (60, 1580), (1080, 1520), (1240, 1460)))
    cerca = ''.join(f'<rect x="{x}" y="1700" width="10" height="120" fill="{silhueta}"/>' for x in range(-300, 1400, 90)) + \
        f'<path d="M-300 1730 Q540 1700 1380 1735" stroke="{silhueta}" stroke-width="5" fill="none"/>'
    return [an._ceu(grad, '<div class="raios"></div>'), an._estrelas(rnd, 50), an._brasas(rnd, 40),
            _c3(f'<g transform="translate(-300 1560)">{morros}</g>{arvs}{cerca}', 8, 'piso')], ''


def capitulo_vermelho(rnd, op):
    return _capitulo_cor(rnd, op, 'radial-gradient(ellipse 70% 60% at 50% 42%,#A8382A 0%,#6E1E16 55%,#2E0A08 100%)', '#250806')


def capitulo_verde(rnd, op):
    return _capitulo_cor(rnd, op, 'radial-gradient(ellipse 70% 60% at 50% 42%,#3E7A5E 0%,#1F4A38 55%,#0C2018 100%)', '#0A1A12')


# ---------------------------------------------------------------- TÚNEL / CORREDOR com a porta clara no fim (contraluz)
def tunel(rnd, op):
    vx, vy = 540, 1260
    A = ['<rect x="-300" y="0" width="1680" height="1920" fill="#2A1E18"/>']
    # arcos do corredor (de longe pra perto)
    for k, s in enumerate((0.45, 0.62, 0.82, 1.08, 1.42, 1.9)):
        w, h = 300 * s, 520 * s
        x0, y0 = vx - w, vy + 260 * s - h - 140 * s
        A.append(f'<path d="M{x0 - 40 * s:.0f} 1920 L{x0 - 40 * s:.0f} {y0 + h * 0.35:.0f} Q{vx} {y0 - h * 0.35:.0f} {vx + w + 40 * s:.0f} {y0 + h * 0.35:.0f} '
                 f'L{vx + w + 40 * s:.0f} 1920 L{vx + w:.0f} 1920 L{vx + w:.0f} {y0 + h * 0.4:.0f} Q{vx} {y0 - h * 0.2:.0f} {x0:.0f} {y0 + h * 0.4:.0f} L{x0:.0f} 1920Z" '
                 f'fill="{bo._esc("#5A3E2C", 0.55 + 0.08 * k)}"/>')
    # porta iluminada
    A.append(f'<path d="M{vx - 130} 1560 L{vx - 130} 1180 Q{vx} 1050 {vx + 130} 1180 L{vx + 130} 1560Z" fill="#FFF1C8"/>'
             f'<ellipse cx="{vx}" cy="1340" rx="330" ry="420" fill="#FFE3A8" opacity=".14"/>'
             f'<ellipse cx="{vx}" cy="1340" rx="200" ry="300" fill="#FFE3A8" opacity=".18"/>')
    # tochas/luminárias nas paredes
    A.append(''.join(f'<g transform="translate({x} {y})"><rect x="-8" y="0" width="16" height="40" fill="#3A2A1E"/>'
                     f'<path class="ar-pisca" d="M0 -40 Q16 -18 0 0 Q-16 -18 0 -40Z" fill="#F2B544"/><circle cy="-16" r="40" fill="#F2B544" opacity=".12"/></g>'
                     for x, y in ((130, 1180), (950, 1180), (300, 1250), (780, 1250))))
    B = (f'<path d="M{vx - 130} 1560 L{vx + 130} 1560 L1380 1920 L-300 1920Z" fill="#3A2A20"/>'
         f'<path d="M{vx - 100} 1560 L{vx + 100} 1560 L800 1920 L280 1920Z" fill="#FFE3A8" opacity=".16"/>')
    return [_c3(''.join(A), 10), _c3(B, 50, 'piso')], ''


# ---------------------------------------------------------------- CASA de dia (sala/cozinha)
def casa(rnd, op):
    A = ['<rect x="-300" y="0" width="1680" height="1400" fill="#EAD9BF"/><rect x="-300" y="0" width="1680" height="70" fill="#D8C4A2"/>']
    # janela grande com cortina e o quintal (árvore) no topo
    A.append('<rect x="200" y="110" width="680" height="330" fill="#A9D3E2"/>'
             + f'<g transform="translate(200 250)">{an._montanhas(rnd, 680, 190, 0, 70, 3, "#8DB07A", suave=True)}</g>'
             + bo._arvore(330, 440, 300, '#4F7F5C', '#3F6B4E', rnd) + bo._arvore(760, 440, 240, '#5B8F66', '#4F7F5C', rnd)
             + '<rect x="200" y="110" width="680" height="330" fill="none" stroke="#FBF6EA" stroke-width="18"/><rect x="532" y="110" width="16" height="330" fill="#FBF6EA"/>'
             + ''.join(f'<path d="M{x} 90 Q{x + 50} 270 {x + 16} 470 L{x + 110} 470 Q{x + 120} 270 {x + 100} 90Z" fill="#C98B6B"/>' for x in (110, 870))
             + '<rect x="80" y="84" width="920" height="12" rx="6" fill="#6B4E31"/>')
    # prateleira com plantas, livros e porta-retrato (desenho, não foto)
    A.append('<rect x="-300" y="1020" width="400" height="14" fill="#8A6A45"/>' + bo._vaso(-160, 1020, 130, rnd, 'folha2')
             + ''.join(f'<rect x="{x}" y="{1020 - h}" width="22" height="{h}" fill="{c}"/>' for x, h, c in ((-60, 90, '#B5523B'), (-34, 80, '#2D4A63'), (-8, 96, '#C9A24A')))
             + '<rect x="980" y="1020" width="400" height="14" fill="#8A6A45"/>' + bo._quadro_arte(1010, 900, 120, 110, rnd, '#6B4E31')
             + bo._relogio3(1200, 940, 50))
    A.append('<rect x="-300" y="1150" width="1680" height="250" fill="#D9C4A0"/><rect x="-300" y="1146" width="1680" height="8" fill="#B79A6E"/>'
             '<rect x="-300" y="1382" width="1680" height="18" fill="#8A6A45"/>')
    B = bo._piso(1400, '#C49A6A', '#B08758') + '<ellipse cx="540" cy="1770" rx="520" ry="110" fill="#5B7F6E" opacity=".35"/>'
    C = bo._vaso(1150, 1990, 280, rnd)
    return [_c3(''.join(A), 18), _c3(B, 50, 'piso')], _c3(C, 85)


# ---------------------------------------------------------------- PARQUE / PRAÇA
def parque(rnd, op):
    tarde = op.get('tarde', False)
    cam = _ceu_dia(rnd, tarde, 5)
    A = f'<g transform="translate(-300 720)">{an._predios(rnd, 1680, 480, 0, 120, 400, "#A9C2CB" if not tarde else "#7E6A86", wmin=70, wmax=140)}</g>'
    B = [f'<rect x="-300" y="1180" width="1680" height="740" fill="{"#9DBF7A" if not tarde else "#6E7A52"}"/>',
         f'<path d="M-300 1640 C200 1560 700 1700 1380 1600 L1380 1720 C700 1820 200 1680 -300 1760Z" fill="#E2D3B0"/>']
    B.append(''.join(bo._arvore(x, y, h, '#4F7F5C' if not tarde else '#3E5A48', '#3F6B4E' if not tarde else '#2E4436', rnd)
                     for x, y, h in ((-220, 1230, 320), (80, 1210, 260), (980, 1210, 280), (1260, 1240, 330), (420, 1190, 200), (700, 1195, 220))))
    # chafariz no meio
    B.append('<ellipse cx="540" cy="1480" rx="190" ry="40" fill="#8A8F96"/><ellipse cx="540" cy="1470" rx="170" ry="32" fill="#8FC1D4"/>'
             '<rect x="526" y="1380" width="28" height="90" fill="#8A8F96"/><ellipse cx="540" cy="1380" rx="60" ry="14" fill="#8A8F96"/>'
             + ''.join(f'<circle class="ar-fuma" cx="{540 + dx}" cy="1350" r="14" fill="#CFE6EE"/>' for dx in (-20, 0, 20)))
    B.append(''.join(bo._poste(x, 1650, 420, acesa=tarde) for x in (120, 960)))
    B.append(''.join(f'<rect x="{x}" y="1560" width="180" height="16" rx="5" fill="#8A6A45"/><rect x="{x}" y="1520" width="180" height="12" rx="5" fill="#8A6A45"/>'
                     f'<rect x="{x + 14}" y="1576" width="10" height="44" fill="#3A3A3A"/><rect x="{x + 156}" y="1576" width="10" height="44" fill="#3A3A3A"/>' for x in (180, 720)))
    C = ''.join(f'<ellipse cx="{x}" cy="1930" rx="160" ry="90" fill="{"#4F7F5C" if not tarde else "#2E4436"}"/>' for x in (-120, 1180))
    return cam + [_c3(A, 12), _c3(''.join(B), 50, 'piso')], _c3(C, 85)


FUNDOS = {
    'campo': campo, 'campo_tarde': lambda r, o: campo(r, o, True), 'porto': porto, 'porto_tarde': lambda r, o: porto(r, o, True),
    'fabrica': fabrica, 'loja': loja, 'cafe': cafe, 'transito': transito, 'aereo': aereo, 'corte': corte, 'preto': preto,
    'capitulo_vermelho': capitulo_vermelho, 'capitulo_verde': capitulo_verde, 'tunel': tunel, 'casa': casa, 'parque': parque,
}
