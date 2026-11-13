# -*- coding: utf-8 -*-
"""Bonecos e cenas do dia a dia pra Edição animada (06/11/2026).

Usuário, depois do 1º teste: "quero mais bonecos, mais objetos… mais dia a dia e não só cenário de cidade no fundo".
Na referência (documentário ilustrado) a cena quase sempre tem
GENTE fazendo alguma coisa: atrás da mesa assinando papel, reunião em mesa comprida, família no sofá com rádio, fila
na padaria, operários, gente no metrô; e OBJETOS: papéis empilhados, lista com X vermelho, telegrama, cartaz, gráfico
de barras no pergaminho com os valores, xícara, abajur, relógio. Tudo em vetor chapado, de frente, sem contorno.

Cenas prontas (cada uma devolve HTML pro monta(); tempos em índice de palavra (int) ou s (float)):
  mesa(c, t, ...)          pessoa na mesa digitando no notebook, xícara com vapor, abajur, papéis; cartão ao lado opcional
  reuniao(c, t, ...)       3–4 pessoas atrás da mesa comprida (pano verde); uma assina o contrato (assinatura desenhando)
  celular(c, t, ...)       pessoa com o celular na mão e notificações pipocando
  loja(c, t, ...)          balcão com toldo listrado, vendedor, caixa registradora e fila de clientes entrando
  multidao(c, t, n, rot)   bonequinhos aparecendo em fileiras + número grande (ex.: '40 leads')
  documento(c, t, titulo, itens)  papel com itens que ganham ✓ (verde) ou ✗ (vermelho) + carimbo opcional
  casa_noite(c, t, ...)    casa à noite com a janela acesa e alguém no notebook lá dentro
  grafico(c, t, titulo, barras)   gráfico de barras no pergaminho, barras subindo uma a uma com o valor e linha pontilhada
Tudo se mexe sem parar: piscar, falar, digitar, vapor, andar, notificação, caneta.
"""
import html as _html
import random
import re

import animada as an
import motor
from motor import q

PELES = ('#F1C9A5', '#E3AE84', '#C68A5E', '#8D5B3D')
CABELOS = ('#2B1D14', '#4A3222', '#7A5230', '#1A1A1A', '#B9B2A8')
TERNOS = ('#2D3A4F', '#3B3B3B', '#4A3A2C', '#2F4A3E')
CAMISAS = ('#E9E4D8', '#8FB3C9', '#B5523B', '#5B7F6E', '#C9A24A', '#6E5A8A')


def _esc(cor, f=0.82):
    cor = cor.lstrip('#')
    r, g, b = (int(cor[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02X%02X%02X' % (int(r * f), int(g * f), int(b * f))


def _T(x):
    return motor.ts(x) if isinstance(x, int) else float(x)


# ================================================================ BONECO (busto de frente, viewBox 200x260)
_CAB = {
    'curto': 'M61 88 Q56 44 100 40 Q146 44 139 88 Q136 66 118 60 Q100 70 76 62 Q64 70 61 88Z',
    'lateral': 'M60 92 Q54 40 106 39 Q148 46 140 92 Q138 62 124 55 Q100 66 72 57 Q63 70 60 92Z',
    'calvo': 'M60 104 Q57 76 64 64 L70 100Z M140 104 Q143 76 136 64 L130 100Z',
    'longo': 'M62 94 Q58 42 100 40 Q142 42 138 94 Q132 58 100 56 Q76 60 62 94Z',
    'coque': 'M61 90 Q58 44 100 42 Q142 44 139 90 Q132 60 100 58 Q72 62 61 90Z',
}


def busto(bid, pele=None, cabelo=None, estilo='curto', roupa=None, terno=True, gravata='#B5523B', oculos=False,
          bigode=False, rnd=None):
    """SVG <g> de um boneco de frente (cabeça, ombros). Partes animáveis: .cabeca .olhos .boca."""
    rnd = rnd or random.Random(_seed(bid))
    pele = pele or rnd.choice(PELES)
    cabelo = cabelo or rnd.choice(CABELOS)
    roupa = roupa or (rnd.choice(TERNOS) if terno else rnd.choice(CAMISAS))
    ps = _esc(pele, 0.86)
    atras = ''
    if estilo in ('longo',):
        atras = f'<path d="M58 95 Q54 40 100 38 Q146 40 142 95 L152 178 Q100 194 48 178Z" fill="{cabelo}"/>'
    corpo = f'<path d="M14 262 L16 206 Q20 162 64 150 L136 150 Q180 162 184 206 L186 262Z" fill="{roupa}"/>'
    if terno:
        corpo += (f'<path d="M84 150 L100 198 L116 150Z" fill="#F4EFE6"/>'
                  f'<path d="M95 156 L105 156 L109 200 L100 212 L91 200Z" fill="{gravata}"/>'
                  f'<path d="M64 150 L95 214 L82 150Z" fill="{_esc(roupa, 0.8)}"/><path d="M136 150 L105 214 L118 150Z" fill="{_esc(roupa, 0.8)}"/>')
    else:
        corpo += f'<path d="M82 150 L100 174 L118 150Z" fill="{ps}"/>'
    rosto = (f'<rect x="88" y="118" width="24" height="40" fill="{ps}"/>'
             f'<ellipse cx="62" cy="96" rx="7" ry="10" fill="{pele}"/><ellipse cx="138" cy="96" rx="7" ry="10" fill="{pele}"/>'
             f'<ellipse cx="100" cy="92" rx="38" ry="45" fill="{pele}"/>'
             f'<path d="{_CAB[estilo]}" fill="{cabelo}"/>'
             + (f'<circle cx="100" cy="36" r="16" fill="{cabelo}"/>' if estilo == 'coque' else '')
             + f'<path d="M78 84 Q86 79 94 83" stroke="{_esc(cabelo, 0.9)}" stroke-width="3.6" fill="none" stroke-linecap="round"/>'
               f'<path d="M106 83 Q114 79 122 84" stroke="{_esc(cabelo, 0.9)}" stroke-width="3.6" fill="none" stroke-linecap="round"/>'
               f'<g class="olhos"><ellipse cx="86" cy="97" rx="3.6" ry="4.4" fill="#1E1A16"/><ellipse cx="114" cy="97" rx="3.6" ry="4.4" fill="#1E1A16"/></g>'
               f'<path d="M100 99 Q105 110 98 113" stroke="{ps}" stroke-width="3" fill="none" stroke-linecap="round"/>'
               f'<ellipse cx="78" cy="112" rx="7" ry="4" fill="#E58A7A" opacity=".25"/><ellipse cx="122" cy="112" rx="7" ry="4" fill="#E58A7A" opacity=".25"/>'
               f'<path class="boca" d="M90 123 Q100 129 110 123" stroke="#8A3B2A" stroke-width="3.6" fill="none" stroke-linecap="round"/>'
             + (f'<path d="M86 117 Q100 109 114 117 Q100 121 86 117Z" fill="{cabelo}"/>' if bigode else '')
             + ('<g fill="none" stroke="#2A2A2A" stroke-width="3"><circle cx="86" cy="97" r="11"/><circle cx="114" cy="97" r="11"/>'
                '<path d="M97 97 L103 97"/></g>' if oculos else ''))
    return f'<g id="{bid}" class="boneco">{atras}{corpo}<g class="cabeca">{rosto}</g></g>'


def _vivo(c, bid, t0, t1, fala=False, cabeca=True):
    """Piscar (sempre), falar (opcional) e balançar a cabeça de leve, de t0 até o fim da cena."""
    D = max(0.4, t1 - t0)
    per = 2.6 + (_seed(bid) % 7) * 0.13   # 08/11: _seed (hash() mudava a cada processo/formato)
    c.a(f"tl.to('#{bid} .olhos',{{keyframes:{{'0%':{{scaleY:1}},'90%':{{scaleY:1}},'95%':{{scaleY:0.1}},'100%':{{scaleY:1}}}},"
        f"duration:{per:.2f},repeat:{max(0, int(D / per))},ease:'none',svgOrigin:'100 97'}},{q(t0)});")
    if fala:
        c.a(f"tl.to('#{bid} .boca',{{scaleY:2.4,duration:0.13,yoyo:true,repeat:{max(1, int(D / 0.13))},ease:'sine.inOut',svgOrigin:'100 125'}},{q(t0)});")
    if cabeca:
        c.a(f"tl.to('#{bid} .cabeca',{{rotation:{2.5 if _seed(bid) % 2 else -2.5},duration:1.5,yoyo:true,repeat:{max(1, int(D / 1.5))},"
            f"ease:'sine.inOut',svgOrigin:'100 150'}},{q(t0)});")


def _fim(c):
    """Fim da cena. As peças são chamadas dentro do monta(), ANTES de a cena seguinte existir: aí o fim vem da palavra
    seguinte (mesma regra do motor: a próxima cena entra 0,20 s antes dela). Antes de 06/11 isso devolvia o fim do vídeo
    e toda animação 'até o fim da cena' ficava esticada (gente levando 30 s pra atravessar a tela)."""
    k = motor.CENAS.index(c)
    if k + 1 < len(motor.CENAS):
        return motor.CENAS[k + 1].t0
    i = c.i1 + 1
    return min(motor.DUR, q(motor.ts(i) - 0.20)) if i < len(motor.W) else motor.DUR


def _entra(c, sel, t, dy=60):
    c.a(f"tl.fromTo('{sel}',{{opacity:0,y:{dy}}},{{opacity:1,y:0,duration:0.5,ease:'power3.out'}},{q(t)});")


# ================================================================ PESSOA de corpo inteiro (viewBox 60x160)
def pessoa(pid, x, y, esc=1.0, roupa=None, pele=None, cabelo=None, calca='#2A2F3A', rnd=None):
    rnd = rnd or random.Random(_seed(pid))
    roupa, pele, cabelo = roupa or rnd.choice(CAMISAS + TERNOS), pele or rnd.choice(PELES), cabelo or rnd.choice(CABELOS)
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({esc:.2f})"><g id="{pid}" class="pessoa">'
            f'<g class="perna1"><rect x="17" y="88" width="11" height="60" rx="4" fill="{calca}"/><rect x="14" y="144" width="16" height="8" rx="3" fill="#1A1A1A"/></g>'
            f'<g class="perna2"><rect x="32" y="88" width="11" height="60" rx="4" fill="{_esc(calca, 0.85)}"/><rect x="31" y="144" width="16" height="8" rx="3" fill="#1A1A1A"/></g>'
            f'<rect x="8" y="40" width="9" height="44" rx="4.5" fill="{_esc(roupa, 0.85)}"/><rect x="43" y="40" width="9" height="44" rx="4.5" fill="{_esc(roupa, 0.85)}"/>'
            f'<circle cx="12.5" cy="86" r="5" fill="{pele}"/><circle cx="47.5" cy="86" r="5" fill="{pele}"/>'
            f'<rect x="14" y="34" width="32" height="58" rx="9" fill="{roupa}"/>'
            f'<rect x="25" y="26" width="10" height="10" fill="{_esc(pele, 0.86)}"/>'
            f'<circle cx="30" cy="18" r="14" fill="{pele}"/><path d="M16 17 Q16 2 30 3 Q45 2 44 17 Q40 9 30 10 Q20 9 16 17Z" fill="{cabelo}"/>'
            f'<circle cx="25" cy="19" r="1.8" fill="#1E1A16"/><circle cx="35" cy="19" r="1.8" fill="#1E1A16"/></g></g>')


def _anda(c, pid, t, dx, dur, parar=True):
    """Anda dx px em dur s (pernas alternando, corpo quicando)."""
    passos = max(1, int(dur / 0.22))
    c.a(f"tl.fromTo('#{pid}',{{x:0}},{{x:{dx:.0f},duration:{dur:.2f},ease:'none'}},{q(t)});")
    c.a(f"tl.fromTo('#{pid} .perna1',{{rotation:-16}},{{rotation:16,duration:0.22,yoyo:true,repeat:{passos},ease:'sine.inOut',svgOrigin:'22 90'}},{q(t)});")
    c.a(f"tl.fromTo('#{pid} .perna2',{{rotation:16}},{{rotation:-16,duration:0.22,yoyo:true,repeat:{passos},ease:'sine.inOut',svgOrigin:'37 90'}},{q(t)});")


# ================================================================ OBJETOS
def _xicara(x, y, vid):
    return (f'<g transform="translate({x} {y})"><g class="vapor" id="{vid}" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity=".7">'
            '<path d="M-8 -14 Q-14 -26 -8 -38 Q-2 -50 -8 -62"/><path d="M8 -14 Q2 -26 8 -38 Q14 -50 8 -62"/></g>'
            '<path d="M-20 -10 L20 -10 L16 26 L-16 26Z" fill="#F4EFE6"/><rect x="-20" y="-12" width="40" height="6" rx="3" fill="#E0D6C4"/>'
            '<path d="M20 -2 Q34 -2 32 10 Q30 18 18 16" fill="none" stroke="#F4EFE6" stroke-width="5"/>'
            '<rect x="-16" y="0" width="32" height="6" fill="#B5523B"/></g>')


def _vapor(c, vid, t0, t1):
    D = max(0.5, t1 - t0)
    c.a(f"tl.fromTo('#{vid} path',{{y:10,opacity:0}},{{y:-14,opacity:0.8,duration:1.6,ease:'sine.out',repeat:{max(1, int(D / 1.6))},"
        f"stagger:{{each:0.8,repeat:0}}}},{q(t0)});")


def _papeis(x, y, n=3):
    return ''.join(f'<rect x="{x + k * 4}" y="{y - k * 5}" width="110" height="20" rx="2" fill="{"#FBF6EA" if k % 2 else "#EFE6D2"}" '
                   f'transform="rotate({(-3 + 2 * k)} {x + 55} {y})"/>' for k in range(n))


def _abajur(x, y, cor='#2F5A47'):
    return (f'<g transform="translate({x} {y})"><path d="M-46 -150 L46 -150 L32 -190 L-32 -190Z" fill="{cor}"/>'
            f'<ellipse cx="0" cy="-148" rx="46" ry="7" fill="#F7D98A" opacity=".85"/>'
            f'<rect x="-3" y="-150" width="6" height="140" fill="#C9A24A"/><ellipse cx="0" cy="-6" rx="34" ry="8" fill="#C9A24A"/></g>')


def _mesa_frente(x, y, w, cor='#8A6A45', pano=None):
    topo = pano or cor
    return (f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="4" fill="{_esc(topo, 1.08) if pano else cor}"/>'
            f'<rect x="{x + 8}" y="{y + 22}" width="{w - 16}" height="200" fill="{_esc(topo, 0.82)}"/>'
            + (f'<rect x="{x + 8}" y="{y + 22}" width="{w - 16}" height="10" fill="{_esc(topo, 0.7)}"/>' if pano else ''))


def _notebook(x, y, vid=''):
    """Notebook visto por trás (tampa com logo) — a pessoa olha pra tela."""
    return (f'<g transform="translate({x} {y})"><rect x="-120" y="-150" width="240" height="150" rx="10" fill="#C9CDD2"/>'
            f'<rect x="-120" y="-150" width="240" height="150" rx="10" fill="none" stroke="#AEB4BB" stroke-width="4"/>'
            f'<circle cx="0" cy="-76" r="12" fill="#AEB4BB"/><rect x="-140" y="-4" width="280" height="12" rx="5" fill="#9CA3AB"/></g>')


# ================================================================ CENAS
def mesa(c, t, oculos=False, estilo='curto', terno=False, cartao='', t_cartao=None, xicara=True, larg=860):
    """Pessoa na mesa digitando no notebook (mãos batendo), xícara com vapor, abajur, papéis.
    cartao = texto curto de um cartão creme que entra ao lado (ex.: 'Lead novo!'), em t_cartao."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'm')
    b = f'{w}-b'
    vid = f'{w}-v'
    svg = (f'<svg class="quadro" id="{w}" width="{larg}" height="{larg * 0.72:.0f}" viewBox="0 0 900 650">'
           f'<ellipse cx="450" cy="640" rx="430" ry="18" fill="#000" opacity=".12"/>'
           + _abajur(150, 440) +
           f'<g transform="translate(330 160) scale(1.2)">{busto(b, estilo=estilo, terno=terno, oculos=oculos)}</g>'
           + _mesa_frente(40, 430, 820) + _notebook(450, 430) + _papeis(640, 424)
           + (_xicara(760, 404, vid) if xicara else '') +
           f'<g class="maos"><ellipse class="m1" cx="380" cy="436" rx="20" ry="13" fill="#E3AE84"/>'
           f'<ellipse class="m2" cx="520" cy="436" rx="20" ry="13" fill="#E3AE84"/></g></svg>')
    _entra(c, f'#{w}', t)
    _vivo(c, b, t, t1)
    D = max(0.4, t1 - t)
    c.a(f"tl.to('#{w} .m1',{{y:-8,duration:0.11,yoyo:true,repeat:{max(1, int(D / 0.11))},ease:'sine.inOut'}},{q(t + 0.3)});")
    c.a(f"tl.to('#{w} .m2',{{y:-8,duration:0.13,yoyo:true,repeat:{max(1, int(D / 0.13))},ease:'sine.inOut'}},{q(t + 0.36)});")
    if xicara:
        _vapor(c, vid, t, t1)
    an.som(t + 0.3, 'digitando', 0.10)
    extra = ''
    if cartao:
        tc = _T(t_cartao) if t_cartao is not None else t + 0.8
        extra = f'<div class="cartao-f" id="{w}-c">{_html.escape(cartao)}</div>'
        c.a(f"tl.fromTo('#{w}-c',{{opacity:0,scale:0.6,rotation:-8}},{{opacity:1,scale:1,rotation:-3,duration:0.4,ease:'back.out(2)'}},{q(tc)});")
        an.som(tc, 'pop2', 0.25)
    return f'<div class="quadro-w">{svg}{extra}</div>'


def reuniao(c, t, n=4, t_assina=None, larg=880):
    """Pessoas atrás da mesa comprida com pano verde, papéis na frente; a do meio assina (assinatura desenhando)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'r')
    rnd = random.Random(len(motor.CENAS) * 7 + n)
    xs = [450 + (k - (n - 1) / 2) * (760 / n) for k in range(n)]
    bon = []
    estilos = ['curto', 'longo', 'calvo', 'lateral', 'coque']
    for k, x in enumerate(xs):
        bid = f'{w}-b{k}'
        bon.append((bid, f'<g transform="translate({x - 95:.0f} {170 + rnd.uniform(-8, 8):.0f}) scale(0.95)">'
                         f'{busto(bid, estilo=estilos[(k + rnd.randint(0, 3)) % 5], terno=k % 2 == 0, oculos=rnd.random() < 0.3, bigode=rnd.random() < 0.2, rnd=rnd)}</g>'))
    meio = n // 2
    papeis = ''.join(f'<g transform="translate({x - 50:.0f} 404) rotate({rnd.uniform(-4, 4):.1f})"><rect width="100" height="70" rx="3" fill="#FBF6EA"/>'
                     + ''.join(f'<rect x="12" y="{12 + 11 * j}" width="{rnd.uniform(40, 76):.0f}" height="4" fill="#C8BFAE"/>' for j in range(4))
                     + (f'<path class="ass" d="M14 58 Q24 44 32 56 T52 54 Q60 46 70 58 T88 52" fill="none" stroke="#1E2A3A" stroke-width="3" '
                        f'stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>' if i == meio else '')
                     + '</g>' for i, x in enumerate(xs))
    caneta = (f'<g transform="translate({xs[meio] + 10:.0f} 380)"><g class="caneta"><rect x="-4" y="0" width="8" height="70" rx="3" fill="#1E2A3A" '
              f'transform="rotate(28)"/><circle cx="0" cy="0" r="7" fill="#E3AE84"/></g></g>')
    svg = (f'<svg class="quadro" id="{w}" width="{larg}" height="{larg * 0.72:.0f}" viewBox="0 0 900 650">'
           f'<ellipse cx="450" cy="640" rx="430" ry="18" fill="#000" opacity=".12"/>'
           + ''.join(h for _, h in bon) + _mesa_frente(20, 400, 860, pano='#2F5A47') + papeis + caneta + '</svg>')
    _entra(c, f'#{w}', t)
    for k, (bid, _) in enumerate(bon):
        _vivo(c, bid, t, t1, fala=(k == (meio + 1) % n))
    ta = _T(t_assina) if t_assina is not None else t + 0.9
    c.a(f"tl.fromTo('#{w} .ass',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:1.0,ease:'power1.inOut'}},{q(ta)});")
    c.a(f"tl.fromTo('#{w} .caneta',{{opacity:0}},{{opacity:1,duration:0.15}},{q(max(t, ta - 0.25))});")   # 06/11: o traço solto aparecia antes
    c.a(f"tl.fromTo('#{w} .caneta',{{x:0,y:0}},{{x:70,y:12,duration:1.0,ease:'sine.inOut'}},{q(ta)});")
    an.som(ta, 'papel', 0.25)
    return svg


def celular(c, t, notificacoes=('Lead novo', 'Lead novo', 'Reunião marcada'), tempos=None, estilo='lateral', terno=False, larg=820):
    """Pessoa segurando o celular perto do rosto; notificações (cartõezinhos) pipocam ao lado, com som."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'p')
    b = f'{w}-b'
    svg = (f'<svg class="quadro" id="{w}" width="{larg}" height="{larg * 0.8:.0f}" viewBox="0 0 820 656">'
           f'<g transform="translate(110 120) scale(1.9)">{busto(b, estilo=estilo, terno=terno)}</g>'
           f'<g class="fone" transform="translate(470 330)"><rect x="-6" y="-10" width="96" height="176" rx="16" fill="#1E2A3A"/>'
           f'<rect x="4" y="6" width="76" height="140" rx="6" fill="#8FC1D4"/><rect x="4" y="6" width="76" height="140" rx="6" fill="#fff" opacity=".25" class="brilho"/>'
           f'<ellipse cx="-4" cy="120" rx="26" ry="36" fill="#E3AE84"/></g></svg>')
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.6 + 0.7 * k for k in range(len(notificacoes))]
    notes = ''.join(f'<div class="notif" id="{w}-n{k}"><i></i>{_html.escape(n)}</div>' for k, n in enumerate(notificacoes))
    _entra(c, f'#{w}', t)
    _vivo(c, b, t, t1)
    c.a(f"tl.to('#{w} .fone',{{rotation:-3,duration:0.9,yoyo:true,repeat:{max(1, int((t1 - t) / 0.9))},ease:'sine.inOut',svgOrigin:'510 420'}},{q(t)});")
    for k, tk in enumerate(ts_):
        c.a(f"tl.fromTo('#{w}-n{k}',{{opacity:0,x:-40,scale:0.7}},{{opacity:1,x:0,scale:1,duration:0.35,ease:'back.out(2)'}},{q(tk)});")
        an.som(tk, 'pop2', 0.22)
    return f'<div class="quadro-w cel-w">{svg}<div class="notifs">{notes}</div></div>'


def loja(c, t, clientes=4, larg=880):
    """Fachada de loja (toldo listrado), vendedor atrás do balcão com caixa registradora; clientes chegam andando."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'l')
    b = f'{w}-b'
    rnd = random.Random(31 + len(motor.CENAS))
    listras = ''.join(f'<path d="M{60 + k * 60} 60 L{120 + k * 60} 60 L{120 + k * 60} 120 Q{90 + k * 60} 140 {60 + k * 60} 120Z" '
                      f'fill="{"#B5523B" if k % 2 == 0 else "#FBF6EA"}"/>' for k in range(13))
    fila = ''
    for k in range(clientes):
        fila += pessoa(f'{w}-p{k}', 40 + k * 70, 470, 1.25, rnd=rnd)
    svg = (f'<svg class="quadro" id="{w}" width="{larg}" height="{larg * 0.74:.0f}" viewBox="0 0 900 666">'
           f'<rect x="40" y="40" width="820" height="470" fill="#E9DFC6"/><rect x="40" y="40" width="820" height="24" fill="#6B4E31"/>'
           + listras +
           f'<rect x="520" y="170" width="260" height="190" fill="#A9CFDD"/><rect x="520" y="170" width="260" height="190" fill="none" stroke="#6B4E31" stroke-width="10"/>'
           f'<rect x="552" y="210" width="40" height="40" fill="#C9A24A"/><rect x="606" y="196" width="40" height="54" fill="#B5523B"/><rect x="660" y="214" width="40" height="36" fill="#5B7F6E"/>'
           f'<g transform="translate(250 150) scale(0.95)">{busto(b, estilo="coque", terno=False, roupa="#5B7F6E")}</g>'
           f'<rect x="150" y="360" width="440" height="160" fill="#8A6A45"/><rect x="140" y="350" width="460" height="18" rx="4" fill="#A88B60"/>'
           f'<g transform="translate(430 300)"><rect x="0" y="0" width="110" height="52" rx="6" fill="#3B4E5E"/><rect x="12" y="-30" width="80" height="34" rx="4" fill="#2D3A4F"/>'
           f'<rect x="20" y="-24" width="64" height="20" fill="#8FE0B0" class="visor"/><rect x="10" y="52" width="90" height="8" fill="#2D3A4F"/></g>'
           f'<rect x="0" y="636" width="900" height="30" fill="#000" opacity=".1"/>' + fila + '</svg>')
    _entra(c, f'#{w}', t)
    _vivo(c, b, t, t1, fala=True)
    for k in range(clientes):
        _anda(c, f'{w}-p{k}', t + 0.3 + 0.25 * k, 120, 1.3)
    c.a(f"tl.fromTo('#{w} .visor',{{opacity:1}},{{opacity:0.35,duration:0.3,ease:'steps(1)',yoyo:true,repeat:{max(1, int((t1 - t) / 0.3))}}},{q(t + 1)});")
    an.som(t + 1.6, 'madeira', 0.2)
    return svg


def multidao(c, t, n=40, rotulo='', cols=10, t_fim=None, larg=860, numero=True):
    """Bonequinhos aparecendo em fileiras (um a um) + número grande contando até n e rótulo (ex.: 'LEADS POR DIA')."""
    t = _T(t)
    w = an._id(c, 'u')
    rnd = random.Random(n * 3 + len(motor.CENAS))
    lin = (n + cols - 1) // cols
    esc = min(1.0, 800 / (cols * 66))
    pes = ''.join(pessoa(f'{w}-p{k}', 30 + (k % cols) * 66 * esc + (lin - 1 - k // cols) * 8, 20 + (k // cols) * 120 * esc, esc * 0.85, rnd=rnd)
                  for k in range(n))
    alt = 40 + lin * 120 * esc
    tf = _T(t_fim) if t_fim is not None else t + 1.6
    c.a(f"tl.fromTo('#{w} .pessoa',{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.25,ease:'back.out(2)',stagger:{max(0.015, (tf - t) / n):.3f}}},{q(t)});")
    if numero:
        c.a(f"conta('#{w}-num',0,{n},{q(t)},{q(max(0.4, tf - t))},'');")
    an.som(t, 'floreio', 0.22)
    an.som(tf, 'impacto_ar', 0.25)
    rot = f'<div class="mrot">{_html.escape(rotulo)}</div>' if rotulo else ''
    return (f'<div class="multi" id="{w}"><svg width="{larg}" height="{alt:.0f}" viewBox="0 0 {cols * 66 * esc + 60:.0f} {alt:.0f}">{pes}</svg>'
            + (f'<div class="mnum"><span id="{w}-num">0</span>{rot}</div>' if numero or rot else '') + '</div>')


def documento(c, t, titulo, itens, marcas=None, tempos=None, carimbo='', larg=640):
    """Papel com título e itens; cada item ganha ✓ (marca 'v') ou ✗ ('x') no seu tempo; carimbo opcional no fim."""
    t = _T(t)
    w = an._id(c, 'd')
    marcas = marcas or ['v'] * len(itens)
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.5 + 0.45 * k for k in range(len(itens))]
    lis = []
    for k, (txt, m) in enumerate(zip(itens, marcas)):
        simb = ('<path class="mk" d="M6 22 L16 32 L34 8" pathLength="1"/>' if m == 'v'
                else '<path class="mk" d="M8 8 L32 32 M32 8 L8 32" pathLength="1"/>')
        lis.append(f'<li id="{w}-{k}" class="{m}"><svg viewBox="0 0 40 40">{simb}</svg><span>{_html.escape(txt)}</span></li>')
        tk = ts_[k]
        c.a(f"tl.fromTo('#{w}-{k}',{{opacity:0,x:-20}},{{opacity:1,x:0,duration:0.25,ease:'power2.out'}},{q(tk)});")
        c.a(f"tl.fromTo('#{w}-{k} .mk',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.25,ease:'power1.out'}},{q(tk + 0.15)});")
        an.som(tk + 0.15, 'tique2' if m == 'v' else 'batida', 0.25)
    _entra(c, f'#{w}', t, 40)
    an.som(t, 'papel', 0.22)
    car = ''
    if carimbo:
        tc = ts_[-1] + 0.5
        car = f'<div class="carimbo-a" id="{w}-k">{_html.escape(carimbo)}</div>'
        c.a(f"tl.fromTo('#{w}-k',{{opacity:0,scale:2.2,rotation:-20}},{{opacity:0.9,scale:1,rotation:-12,duration:0.18,ease:'power4.in'}},{q(tc)});")
        an.som(tc + 0.15, 'impacto', 0.3)
    return (f'<div class="doc" id="{w}" style="width:{larg}px"><div class="dt">{_html.escape(titulo)}</div>'
            f'<ul>{"".join(lis)}</ul>{car}</div>')


def casa_noite(c, t, larg=860):
    """Casa à noite: janela acesa e alguém no notebook lá dentro (brilho da tela piscando), fumaça na chaminé."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'h')
    b = f'{w}-b'
    svg = (f'<svg class="quadro" id="{w}" width="{larg}" height="{larg * 0.8:.0f}" viewBox="0 0 900 720">'
           f'<g class="fumo" fill="#8E9AB8" opacity=".5"><circle cx="660" cy="90" r="22"/><circle cx="680" cy="60" r="26"/><circle cx="700" cy="24" r="30"/></g>'
           f'<rect x="630" y="110" width="50" height="120" fill="#4A2E2A"/>'
           f'<path d="M130 290 L450 110 L770 290Z" fill="#3A2A36"/><rect x="170" y="280" width="560" height="420" fill="#6B3E34"/>'
           + ''.join(f'<rect x="170" y="{y}" width="560" height="3" fill="#5A332B"/>' for y in range(300, 700, 34)) +
           f'<rect x="250" y="360" width="400" height="260" fill="#F2C46B" class="luz"/>'
           f'<g transform="translate(380 420) scale(0.75)">{busto(b, estilo="lateral", terno=False)}</g>'
           f'<rect x="300" y="560" width="300" height="70" fill="#7A5B38"/><g transform="translate(450 560)"><rect x="-90" y="-80" width="180" height="80" rx="8" fill="#C9CDD2"/></g>'
           f'<rect x="250" y="360" width="400" height="260" fill="none" stroke="#2B1A16" stroke-width="16"/>'
           f'<rect x="442" y="360" width="16" height="260" fill="#2B1A16"/><rect x="250" y="482" width="400" height="14" fill="#2B1A16"/>'
           f'<rect x="230" y="616" width="440" height="18" fill="#2B1A16"/></svg>')
    _entra(c, f'#{w}', t)
    _vivo(c, b, t, t1)
    D = max(0.5, t1 - t)
    c.a(f"tl.fromTo('#{w} .luz',{{fill:'#F2C46B'}},{{fill:'#F7D98A',duration:0.6,ease:'steps(2)',yoyo:true,repeat:{max(1, int(D / 0.6))}}},{q(t)});")
    c.a(f"tl.fromTo('#{w} .fumo circle',{{y:20,opacity:0}},{{y:-30,opacity:0.6,duration:1.8,ease:'sine.out',repeat:{max(1, int(D / 1.8))},stagger:{{each:0.6,repeat:0}}}},{q(t)});")
    return svg


def grafico(c, t, titulo, barras, sub='', tempos=None, larg=860):
    """Gráfico de barras no pergaminho (ref. 'VOTOS DO PARTIDO'): barras sobem uma a uma, valor contando em cima,
    linha pontilhada ligando os topos. barras = [('2024', 30, '30 mil'), ...] (rótulo, altura 0–100, valor escrito)."""
    t = _T(t)
    w = an._id(c, 'g')
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.4 + 0.6 * k for k in range(len(barras))]
    n = len(barras)
    bw, gap, H = 110, 60, 360
    x0 = (larg - (n * bw + (n - 1) * gap)) / 2
    cols, pts = [], []
    for k, (rot, h, val) in enumerate(barras):
        x = x0 + k * (bw + gap)
        hh = H * h / 100
        destaque = k == n - 1
        cols.append(f'<div class="gb" style="left:{x:.0f}px;width:{bw}px"><div class="gv" id="{w}-v{k}">{_html.escape(val)}</div>'
                    f'<div class="gbar{" dest" if destaque else ""}" id="{w}-b{k}" style="height:{hh:.0f}px"></div>'
                    f'<div class="gr">{_html.escape(rot)}</div></div>')
        pts.append((x + bw / 2, H + 100 - 58 - hh))
        c.a(f"tl.fromTo('#{w}-b{k}',{{scaleY:0}},{{scaleY:1,duration:0.5,ease:'power3.out',transformOrigin:'50% 100%'}},{q(ts_[k])});")
        c.a(f"tl.fromTo('#{w}-v{k}',{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3}},{q(ts_[k] + 0.35)});")
        an.som(ts_[k], 'marimba', 0.2)
    linha = 'M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in pts)
    c.a(f"tl.fromTo('#{w}-l',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{q(max(0.4, ts_[-1] - ts_[0]))},ease:'none'}},{q(ts_[0] + 0.4)});")
    _entra(c, f'#{w}', t, 30)
    return (f'<div class="graf" id="{w}" style="width:{larg}px"><div class="gt">{_html.escape(titulo)}</div>'
            + (f'<div class="gs">{_html.escape(sub)}</div>' if sub else '') +
            f'<div class="garea" style="height:{H + 100}px"><div class="geixo"></div>{"".join(cols)}'
            f'<svg class="glinha" width="{larg}" height="{H + 100}"><path id="{w}-l" d="{linha}" pathLength="1" stroke-dasharray="0.012 0.012"/></svg></div></div>')


def equipe(c, t, n=5, larg=860):
    """O time chegando: pessoas entrando pela esquerda, uma atrás da outra, e parando lado a lado."""
    t = _T(t)
    w = an._id(c, 'e')
    rnd = random.Random(77 + n)
    pes = ''.join(pessoa(f'{w}-p{k}', 40 + k * 150 - 320, 40, 1.6, rnd=rnd) for k in range(n))
    for k in range(n):
        _anda(c, f'{w}-p{k}', t + 0.15 * k, 320, 1.6 - 0.05 * k)
    an.som(t + 0.2, 'swish', 0.15)
    return f'<svg class="quadro" id="{w}" width="{larg}" height="300" viewBox="0 0 860 300" style="overflow:hidden">{pes}<rect x="0" y="282" width="860" height="8" rx="4" fill="#000" opacity=".12"/></svg>'



# ================================================================ v3 (06/11, revisão independente nota 4/10)
# "personagens 3–4x maiores, de CORPO INTEIRO e fazendo algo", "dado vira CENA, não cartão creme", "4–5 ambientes com
# piso em perspectiva, mesa com pés no chão e o fundo atrás", "metade de cima preenchida", "dia a dia".
# Corpo de PERFIL (olha pra direita; olha=-1 espelha), ~475 unidades de altura em esc=1, articulado: ombro/cotovelo,
# quadril/joelho e pescoço (cada junta tem o pivô na origem do seu <g>, então o GSAP gira com svgOrigin '0 0').
# As cenas novas desenham na CAMADA DE AÇÃO (1080x1920, coordenadas de tela) que o animada.aplicar() põe dentro do
# cenário e anda junto com o piso (sem patinar); a função devolve '' pro monta(). Ambientes (an.cenario): 'escritorio',
# 'escritorio_noite', 'reuniao', 'sala_noite', 'rua', 'rua_tarde', 'celular', 'celular_dia' — desenhados por fundo().
import math

AMB = {}   # id da cena -> [svg da camada de ação]
CALCAS = ('#2A2F3A', '#3B4A5E', '#4A3A2C', '#55606C', '#2F3B30', '#6B5A48')
SAPATOS = ('#1A1A1A', '#3A2A1E', '#5A3A26')
CHAO = 1730          # linha do chão das mesas (pés) na camada de ação
PAREDE_FIM = 1400    # onde a parede encontra o piso


# 08/11 (margem segura): o objeto que carrega a ideia leva data-imp e a checagem (hyperframes/checar_margem.py) exige
# que ele fique inteiro dentro da caixa segura de cada formato. prefixo do id da peça -> (subgrupo marcado, lados
# conferidos; '' = os 4). Peças largas de cenário (escritório aberto, prédio em corte, fábrica...) não entram: o texto
# delas já é conferido (todo texto visível é).
IMP = {'cm': ('-cel', 'esq dir topo'), 'ca': ('-c', ''), 'cx': ('-cx', ''), 'ag': ('-cal', ''),
       'cr': ('-r', 'esq dir topo'), 'pz': ('-g', ''), 'gl': ('', ''), 'cn': ('', ''), 'fx': ('', ''), 'fn': ('', ''),
       'pg': ('', ''), 'bz': ('', ''), 'go': ('', ''), 'ml': ('-bs', ''),
       'eg': ('', ''), 'sm': ('-fr', ''), 'tb': ('-tr', ''), 'lp': ('-bu', ''), 'rr': ('-rel', ''),
       'pv': ('', ''), 'mc': ('-g', ''), 'cb': ('', ''), 'qt': ('', ''), 'lt': ('', '')}


# Caixa segura de cada formato, em coordenadas da CAMADA DE AÇÃO (o mundo 1080x1920). No RL o mundo é a tela; no
# GL/YT/IN ele encolhe (an._css_mundo: mostra do y 280/260 até o chão), então a mesma caixa da tela vira outra faixa
# no mundo. Já desconta o passeio da câmera (piso ±60 px, zoom lento de 5 %, push/pan do arsenal).
#   RL tela x 100–980, y 220–1500  |  GL/YT tela y 80–1000 (mundo 401–1798)  |  IN tela y 80–1270 (mundo 358–1822)
# 12/11/2026 (REGRA DO USUÁRIO: texto nunca lá em cima — RL ≥ 320, IN ≥ 200, GL/YT ≥ 160): o mundo do GL/YT/IN agora
# mostra do y 240 (an.TOPO_MUNDO, escala 0,643/0,804) e o topo da faixa desceu: RL 340; GL/YT 530 = tela ~186;
# IN 500 = tela ~209. A base continua: GL/YT 1770 = tela ~984, IN 1790 = tela ~1246.
FAIXA = {'RL': (340, 1470), 'GL': (530, 1770), 'YT': (530, 1770), 'IN': (500, 1790)}
X_LAT = (170, 910)   # bordas de texto/peça na camada de ação: 100 de margem + passeio do piso (±60) + zoom lento


def faixa(fmt=None):
    """(y_min, y_max) do mundo onde texto e peça importante ficam inteiros na tela em qualquer formato atual."""
    return FAIXA.get(fmt or motor.FORMATO, FAIXA['RL'])


def cabe_y(y0, y1, fmt=None):
    """Deslocamento dy que leva o intervalo [y0, y1] do mundo pra dentro da faixa segura do formato (0 = já cabe).
    Se não couber inteiro, alinha pelo topo da faixa (o resto passa embaixo) — reveja a peça."""
    a, b = faixa(fmt)
    if y1 - y0 > b - a:
        return a - y0
    return min(0, b - y1) + max(0, a - y0)


def encaixa(svg, caixa, apoio=False):
    """Encaixa uma peça inteira (svg do mundo) na caixa segura do formato SEM mexer no desenho dela. caixa = (x0, y0,
    x1, y1) do que importa (texto + objeto) no mundo. A conta é feita no an.aplicar(), quando o tamanho do letreiro da
    cena já é conhecido: a peça fica ABAIXO do letreiro e acima do limite de baixo do formato (RL 1470), encolhendo
    (âncora no pé) só se não couber e subindo o mínimo. apoio=True: se a peça subiu, desenha um suporte chapado
    (mesa/pedestal) do pé novo até o chão antigo, pra nada flutuar. As animações de dentro continuam iguais."""
    x0, y0, x1, y1 = caixa
    return f'<g data-enc="{x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f},{1 if apoio else 0}">{svg}</g>'


def resolve_encaixe(amb, topo_min, fmt=None, lat=(170, 910)):
    """Troca cada <g data-enc> do svg da camada de ação pelo transform que põe a peça entre topo_min (pé do letreiro,
    no mundo) e o fim da faixa segura do formato. Chamado pelo an.aplicar()."""
    def troca(m):
        x0, y0, x1, y1, apoio = (float(v) for v in m.group(1).split(','))
        a, b = faixa(fmt)
        a = max(a, topo_min)
        if b - a < 260:   # letreiro muito alto: usa a faixa inteira (a revisão aponta se cobrir texto)
            a = faixa(fmt)[0]
        s_ = min(1.0, (b - a) / max(1, y1 - y0), (lat[1] - lat[0]) / max(1, x1 - x0))
        ny0, ny1 = y1 - s_ * (y1 - y0), y1
        nx0, nx1 = 540 + s_ * (x0 - 540), 540 + s_ * (x1 - 540)
        if ny1 - ny0 > b - a + 0.5:
            dy = a - ny0
        else:
            dy = min(0.0, b - ny1) + max(0.0, a - ny0)
        dx = max(0.0, lat[0] - nx0) - max(0.0, nx1 - lat[1])
        if abs(s_ - 1) < 1e-3 and abs(dx) < 0.5 and abs(dy) < 0.5:
            return '<g>'
        tx, ty = dx + 540 * (1 - s_), dy + y1 * (1 - s_)
        sup = ''
        if apoio and dy < -10:
            topo, chao = ny1 + dy, y1 + 80
            L0, L1 = nx0 + dx - 30, nx1 + dx + 30
            sup = (f'<rect x="{L0:.0f}" y="{topo:.0f}" width="{L1 - L0:.0f}" height="26" rx="6" fill="#6B4E31"/>'
                   f'<rect x="{L0:.0f}" y="{topo + 20:.0f}" width="{L1 - L0:.0f}" height="8" fill="#000" opacity=".18"/>'
                   f'<rect x="{L0 + 30:.0f}" y="{topo + 26:.0f}" width="26" height="{max(0, chao - topo - 26):.0f}" fill="#5A3E28"/>'
                   f'<rect x="{L1 - 56:.0f}" y="{topo + 26:.0f}" width="26" height="{max(0, chao - topo - 26):.0f}" fill="#5A3E28"/>')
        return f'{sup}<g transform="translate({tx:.1f} {ty:.1f}) scale({s_:.4f})">'
    return re.sub(r'<g data-enc="([-\d.,]+)">', troca, amb)


def _marca_imp(svg):
    m = re.search(r'<g id="(c\d+-([a-z]+)\d+)">', svg)
    if not m or m.group(2) not in IMP:
        return svg
    sub, lados = IMP[m.group(2)]
    alvo = f'<g id="{m.group(1)}{sub}"'
    if alvo not in svg:
        return svg
    attr = f' data-imp="{m.group(2)}"' + (f' data-lados="{lados}"' if lados else '')
    return svg.replace(alvo, alvo + attr, 1)


def _amb(c, svg):
    AMB.setdefault(c.id, []).append(_marca_imp(svg))
    return ''


def semente_video():
    """Semente do vídeo (crc32 do nome da composição): muda as pessoas e os detalhes de cenário de um criativo pro outro."""
    import zlib
    return zlib.crc32(str(getattr(motor, 'COMPOSICAO', '') or '').encode('utf-8')) % 100003


def variante(ideia, opcoes, base=None):
    """Escolhe, pela semente do vídeo, qual cena usar pra uma ideia (sempre fiel à fala): ex.
    bo.variante('qualifica', ('mapa', 'agenda'), base='mapa'). base = a cena que o molde (vídeo de onde o gerar.py foi
    copiado) usou: ela sai do sorteio, então dois vídeos do mesmo meio não repetem a cena."""
    import zlib
    ops = [o for o in opcoes if o != base] or list(opcoes)
    return ops[random.Random(semente_video() * 13 + zlib.crc32(ideia.encode('utf-8'))).randrange(len(ops))]


def _seed(s):
    return sum(ord(ch) * (k + 1) for k, ch in enumerate(s)) + semente_video()


_BARALHO = {'cartas': None, 'i': 0}


def _visual():
    """Próximo visual do baralho do vídeo (pele, cabelo, penteado, roupa). Embaralhado pela semente do vídeo e tirado em
    ordem: dentro do mesmo vídeo a mesma pessoa só volta depois de dezenas de outras (o careca de tablet, o barbudo e o
    homem de camisa vermelha não aparecem em 3–4 cenas)."""
    if _BARALHO['cartas'] is None:
        import itertools
        cartas = list(itertools.product(range(len(PELES)), range(len(CABELOS)), range(6), range(len(CAMISAS))))
        random.Random(semente_video() * 7 + 3).shuffle(cartas)
        # afasta cartas parecidas: mesmo penteado ou mesma roupa nunca em sequência
        ord_, resto = [cartas[0]], cartas[1:]
        while resto:
            j = next((k for k, cc in enumerate(resto[:40]) if cc[2] != ord_[-1][2] and cc[3] != ord_[-1][3]), 0)
            ord_.append(resto.pop(j))
        _BARALHO['cartas'] = ord_
    c_ = _BARALHO['cartas'][_BARALHO['i'] % len(_BARALHO['cartas'])]
    _BARALHO['i'] += 1
    return (PELES[c_[0]], CABELOS[c_[1]], ('curto', 'lateral', 'longo', 'coque', 'calvo', 'cacheado')[c_[2]], CAMISAS[c_[3]])


def _txt_larg(txt, tam, fonte='cond'):
    f = an._fonte('TikTokSans-Variable.ttf', tam, 75, 800) if fonte == 'cond' else an._fonte('EBGaramond-400.woff2', tam)
    return f.getlength(txt)


# ---------------------------------------------------------------- corpo articulado
def _ik(dx, dy, l1=92, l2=88):
    """Ângulos (ombro, cotovelo relativo) pra mão chegar em (dx, dy) a partir do ombro. Ângulo 0 = braço pra baixo;
    negativo = pra frente. Escolhe o cotovelo mais baixo (natural)."""
    d = max(abs(l1 - l2) + 2, min(l1 + l2 - 2, math.hypot(dx, dy)))
    phi = math.degrees(math.atan2(-dx, dy))
    a = math.degrees(math.acos(max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))))
    melhor = None
    for s in (1, -1):
        t1 = phi + s * a
        ex, ey = -l1 * math.sin(math.radians(t1)), l1 * math.cos(math.radians(t1))
        t2 = math.degrees(math.atan2(-(dx - ex), dy - ey))
        rel = (t2 - t1 + 180) % 360 - 180
        cand = (round(ey, 1), -ex, t1, rel)
        if melhor is None or cand > melhor:
            melhor = cand
    return melhor[2], melhor[3]


# mão de trás (t) e da frente (f): alvo (dx, dy) a partir do ombro, ou ('a', ombro, cotovelo) em graus
POSES = {
    'em_pe':      dict(t=('a', 6, -8), f=('a', -6, -10)),
    'anda':       dict(t=('a', 0, -14), f=('a', 0, -14)),
    'digita':     dict(sent=1, t=(116, 44), f=(136, 40)),
    'headset':    dict(sent=1, t=(116, 44), f=(136, 40)),
    'telefone':   dict(t=('a', 6, -10), f=(12, -72)),
    'tel_sent':   dict(sent=1, t=(116, 44), f=(12, -72)),
    'cafe':       dict(t=('a', 4, -10), f=(70, 92)),
    'carrega':    dict(t=(96, 60), f=(108, 56)),
    'pasta':      dict(t=('a', 4, -10), f=('a', -4, -6)),
    'aperta':     dict(t=('a', 6, -8), f=(150, 112)),
    'aponta':     dict(t=('a', 6, -8), f=('a', -128, -8)),
    'acena':      dict(t=('a', 6, -8), f=(50, -146)),
    'acena_sent': dict(sent=1, t=(116, 44), f=(50, -146)),
    'preocupado': dict(sent=1, t=(116, 44), f=(0, -116), cab=12),
    'coca':       dict(t=('a', 6, -8), f=(0, -116), cab=8),          # em pé coçando a cabeça
    'mostra':     dict(t=('a', 6, -8), f=(104, 18)),                 # mão pra frente mostrando algo (carteira vazia, papel)
    'toca_alto':  dict(t=('a', 6, -8), f=(82, -118)),                # mão alta pra frente (high five)
    'celular':    dict(t=('a', 6, -8), f=(78, -36), cab=12),
    'cel_sent':   dict(sent=1, t=(60, 84), f=(78, -36), cab=12),
    'sentado':    dict(sent=1, t=(64, 92), f=(86, 88)),
    'xicara_sent': dict(sent=1, t=(64, 92), f=(84, 30)),
    'come_sent':  dict(sent=1, t=(70, 66), f=(96, 36)),     # 08/11: sentado à mesa, mãos em cima do tampo (tampo ~200 do chão)
    'come_ponta': dict(sent=1, t=(112, 40), f=(140, 24)),   # 08/11: na PONTA da mesa (alcança o prato)
}


def _perna(cls, a1, a2, calca, sapato):
    return (f'<g transform="rotate({a1:.1f})"><g class="{cls}">'
            f'<rect x="-17" y="-10" width="34" height="122" rx="16" fill="{calca}"/>'
            f'<g transform="translate(0 104) rotate({a2:.1f})"><g class="{cls}s">'
            f'<rect x="-15" y="-10" width="30" height="114" rx="14" fill="{calca}"/>'
            f'<path d="M-16 96 L18 96 Q40 98 40 110 L40 114 L-16 114Z" fill="{sapato}"/></g></g></g></g>')


_ITENS = {
    'celular': ('<rect x="-8" y="-38" width="32" height="58" rx="7" fill="#1E2A3A"/>'
                '<rect x="-4" y="-33" width="24" height="46" rx="3" fill="#8FC1D4" class="telac"/>'),
    'cafe': ('<g class="vapor-i" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity=".75">'
             '<path d="M8 -54 Q2 -66 8 -78 Q14 -90 8 -100"/><path d="M22 -54 Q16 -66 22 -78 Q28 -90 22 -100"/></g>'
             '<path d="M-2 -44 L32 -44 L27 8 L3 8Z" fill="#F4EFE6"/><rect x="1" y="-28" width="29" height="15" fill="#8A5A2B"/>'
             '<rect x="-5" y="-50" width="40" height="9" rx="3" fill="#D8CBB4"/>'),
    'caixa': ('<rect x="-40" y="-78" width="132" height="104" rx="4" fill="#C49A62"/><rect x="-40" y="-78" width="132" height="16" fill="#A87F4A"/>'
              '<rect x="18" y="-78" width="18" height="104" fill="#E3CDA2" opacity=".7"/>'),
    'papel': ('<g transform="rotate(-8)"><rect x="-6" y="-60" width="64" height="84" rx="3" fill="#FBF6EA"/>'
              + ''.join(f'<rect x="4" y="{-50 + 12 * k}" width="{40 - 6 * (k % 2)}" height="4" fill="#B7AC98"/>' for k in range(5)) + '</g>'),
    'pasta': ('<path d="M-10 12 L-10 2 L14 2 L14 12" stroke="#4A2E1E" stroke-width="6" fill="none"/>'
              '<rect x="-32" y="12" width="68" height="52" rx="7" fill="#5A3A26"/><rect x="-32" y="30" width="68" height="5" fill="#4A2E1E"/>'),
    'garfo': ('<rect x="-2" y="-40" width="5" height="44" rx="2" fill="#9AA3AD"/>'
              '<path d="M-6 -54 L-6 -38 M0 -54 L0 -38 M6 -54 L6 -38 M-7 -38 L7 -38" stroke="#9AA3AD" stroke-width="3"/>'),
    'caneta': '<rect x="-3" y="-40" width="7" height="46" rx="3" fill="#1E2A3A" transform="rotate(30)"/>',
    'tablet': '<rect x="-10" y="-70" width="74" height="96" rx="8" fill="#1E2A3A"/><rect x="-4" y="-63" width="62" height="82" rx="3" fill="#BFD9E2"/>',
    'carteira': ('<g class="it-cart" opacity="0"><rect x="-6" y="-30" width="74" height="50" rx="8" fill="#6B3E1E"/>'
                 '<rect x="2" y="-24" width="58" height="38" rx="4" fill="#3A2210"/><path d="M8 -6 l10 -8 l10 8 l10 -8 l10 8" stroke="#8A5A30" stroke-width="3" fill="none"/></g>'),
}


def _braco(cls, a1, a2, manga, pele, curta, item='', item_rot=0.0):
    if curta:
        sup = (f'<rect x="-12" y="-6" width="24" height="100" rx="12" fill="{pele}"/>'
               f'<rect x="-15" y="-14" width="30" height="58" rx="14" fill="{manga}"/>')
    else:
        sup = f'<rect x="-14" y="-12" width="28" height="108" rx="14" fill="{manga}"/>'
    ante = (f'<rect x="-12" y="-8" width="24" height="94" rx="12" fill="{pele if curta else manga}"/>'
            f'<circle cx="0" cy="90" r="15" fill="{pele}"/>')
    it = f'<g class="it" transform="translate(0 90) rotate({-(a1 + a2) + item_rot:.1f})">{_ITENS[item]}</g>' if item else ''
    return (f'<g transform="rotate({a1:.1f})"><g class="{cls}">{sup}'
            f'<g transform="translate(0 92) rotate({a2:.1f})"><g class="{cls}a">{ante}{it}</g></g></g></g>')


_CAB3 = {
    'curto': 'M-40 -38 Q-50 -98 6 -98 Q48 -98 50 -62 Q36 -76 16 -74 Q0 -72 -8 -60 Q-14 -50 -12 -36 Q-26 -24 -40 -38Z',
    'lateral': 'M-40 -40 Q-50 -100 8 -100 Q52 -98 52 -70 Q44 -60 30 -74 Q10 -80 -4 -64 Q-12 -52 -12 -36 Q-26 -24 -40 -40Z',
    'longo': 'M-40 -38 Q-50 -100 6 -100 Q50 -98 52 -60 Q38 -78 14 -76 Q-2 -72 -10 -58 Q-16 -46 -14 -30 Q-28 -22 -40 -38Z',
    'coque': 'M-40 -40 Q-48 -96 6 -96 Q46 -96 50 -64 Q34 -76 14 -74 Q-2 -70 -10 -58 Q-14 -48 -14 -34 Q-28 -26 -40 -40Z',
    'calvo': 'M-42 -36 Q-48 -62 -34 -78 Q-26 -62 -20 -50 Q-22 -36 -30 -26Z',
    'cacheado': '',
}


def _cabeca3(pele, cabelo, estilo, oculos, barba, headset):
    ps = _esc(pele, 0.86)
    atras = ''
    if estilo == 'longo':
        atras = f'<path d="M-42 -70 Q-62 6 -34 46 L4 40 Q-14 0 -6 -52Z" fill="{cabelo}"/>'
    elif estilo == 'coque':
        atras = f'<circle cx="-36" cy="-92" r="19" fill="{cabelo}"/>'
    if estilo == 'cacheado':
        cab = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{cabelo}"/>' for x, y, r in
                      ((-34, -72, 20), (-16, -90, 20), (8, -96, 20), (32, -86, 17), (-42, -46, 17), (44, -70, 12)))
    else:
        cab = f'<path d="{_CAB3[estilo]}" fill="{cabelo}"/>'
    return (atras + f'<rect x="-12" y="-20" width="26" height="30" fill="{ps}"/>'
            f'<circle cx="4" cy="-50" r="44" fill="{pele}"/><circle cx="46" cy="-44" r="9" fill="{pele}"/>'
            + cab +
            f'<ellipse cx="-6" cy="-46" rx="8" ry="11" fill="{ps}"/>'
            f'<path d="M16 -72 Q27 -78 38 -71" stroke="{_esc(cabelo, 0.85)}" stroke-width="5" fill="none" stroke-linecap="round"/>'
            f'<g class="j-olho"><ellipse cx="28" cy="-56" rx="4.6" ry="5.8" fill="#1E1A16"/></g>'
            f'<ellipse cx="26" cy="-34" rx="8" ry="4.5" fill="#E58A7A" opacity=".28"/>'
            f'<path class="j-boca" d="M26 -24 Q34 -19 41 -26" stroke="#8A3B2A" stroke-width="4" fill="none" stroke-linecap="round"/>'
            + (f'<path d="M-10 -40 Q-8 -4 22 -4 Q44 -6 48 -30 Q38 -20 28 -21 Q16 -23 10 -32 Q2 -42 -10 -40Z" fill="{cabelo}"/>' if barba else '')
            + ('<circle cx="29" cy="-56" r="12" fill="#FFFFFF" fill-opacity=".18" stroke="#2A2A2A" stroke-width="3.6"/>'
               '<path d="M17 -58 L-4 -52" stroke="#2A2A2A" stroke-width="3.6"/>' if oculos else '')
            + ('<path d="M-8 -48 Q-16 -110 18 -102" stroke="#2A2A2A" stroke-width="8" fill="none" stroke-linecap="round"/>'
               '<circle cx="-6" cy="-46" r="15" fill="#2A2A2A"/><path d="M-2 -36 Q8 -10 36 -16" stroke="#2A2A2A" stroke-width="4.5" fill="none"/>'
               '<circle cx="38" cy="-16" r="6" fill="#2A2A2A"/>' if headset else ''))


def corpo(pid, pose='em_pe', pele=None, cabelo=None, estilo=None, roupa=None, calca=None, blazer=None, gravata=None,
          oculos=None, barba=None, headset=False, cracha=False, item=None, manga=None, rnd=None, item_rot=0.0):
    """Pessoa de CORPO INTEIRO, de perfil olhando pra direita. Origem = chão entre os pés (y pra cima negativo),
    ~475 de altura. Posicione com pos(). Partes animáveis (classes): j-cq (corpo todo), j-cab, j-olho, j-boca,
    j-bt/j-bta (braço de trás/antebraço), j-bf/j-bfa (braço da frente), j-pt/j-pts, j-pf/j-pfs (pernas).
    pose: ver POSES. item na mão da frente: celular, cafe, caixa, papel, pasta, caneta, tablet."""
    rnd = random.Random(_seed(pid))   # rodada 7: o rnd da cena não decide mais a cara (vinha igual em todo vídeo)
    v_pele, v_cab, v_est, v_roupa = _visual()
    pele = pele or v_pele
    cabelo = cabelo or v_cab
    estilo = estilo or v_est
    roupa = roupa or v_roupa
    calca = calca or rnd.choice(CALCAS)
    sapato = rnd.choice(SAPATOS)
    oculos = rnd.random() < 0.22 if oculos is None else oculos
    barba = (estilo in ('curto', 'calvo', 'lateral') and rnd.random() < 0.25) if barba is None else barba
    manga = manga or ('longa' if blazer or rnd.random() < 0.6 else 'curta')
    P = POSES[pose]
    sent = P.get('sent', 0)
    dy = 104 if sent else 0
    hip = -218 + dy
    sh = (2, -350 + dy)

    def ang(spec):
        return (spec[1], spec[2]) if spec[0] == 'a' else _ik(spec[0], spec[1])

    at1, at2 = ang(P['t'])
    af1, af2 = ang(P['f'])
    pt, pf = ((-88, 90), (-92, 92)) if sent else ((5, 0), (-5, 0))
    manga_cor = blazer or roupa
    curta = manga == 'curta' and not blazer
    tronco = (f'<rect x="-32" y="{hip - 26}" width="66" height="44" rx="16" fill="{calca}"/>'
              f'<rect x="-34" y="{-382 + dy}" width="72" height="{170}" rx="30" fill="{roupa}"/>')
    if blazer:
        tronco += (f'<path d="M-34 {-350 + dy} Q-34 {-382 + dy} -4 {-382 + dy} L16 {-382 + dy} L26 {-300 + dy} L32 {-214 + dy} '
                   f'L-34 {-214 + dy}Z" fill="{blazer}"/>')
        if gravata:
            tronco += f'<path d="M24 {-372 + dy} L34 {-372 + dy} L36 {-300 + dy} L29 {-288 + dy} L22 {-300 + dy}Z" fill="{gravata}"/>'
    if cracha:
        tronco += (f'<path d="M6 {-378 + dy} L24 {-300 + dy}" stroke="#B5523B" stroke-width="4"/>'
                   f'<rect x="14" y="{-304 + dy}" width="22" height="30" rx="3" fill="#FBF6EA"/>'
                   f'<rect x="14" y="{-304 + dy}" width="22" height="8" fill="#2D4A63"/>')
    calca_t = _esc(calca, 0.8)
    s = (f'<g id="{pid}" class="corpo"><path d="M-30 0 L40 0 L210 -16 L150 -26 Z" fill="#000" opacity=".16"/><g class="j-cq">'
         f'<g transform="translate({sh[0] - 4} {sh[1]})">{_braco("j-bt", at1, at2, _esc(manga_cor, 0.8), _esc(pele, 0.88), curta)}</g>'
         f'<g transform="translate(-6 {hip})">{_perna("j-pt", pt[0], pt[1], calca_t, _esc(sapato, 0.8))}</g>'
         f'<g transform="translate(2 {hip})">{_perna("j-pf", pf[0], pf[1], calca, sapato)}</g>'
         + tronco +
         f'<g transform="translate(2 {-378 + dy}) rotate({P.get("cab", 0)})"><g class="j-cab">'
         f'{_cabeca3(pele, cabelo, estilo, oculos, barba, headset)}</g></g>'
         f'<g transform="translate({sh[0] + 4} {sh[1]})">{_braco("j-bf", af1, af2, manga_cor, pele, curta, item or "", item_rot)}</g>'
         '</g></g>')
    return s


def pos(svg, x, y, esc=1.0, olha=1):
    """Põe um corpo/objeto em (x, y) da tela (y = chão), com escala e direção (olha=-1 vira pra esquerda)."""
    return f'<g transform="translate({x:.0f} {y:.0f}) scale({esc * olha:.3f} {esc:.3f})">{svg}</g>'


# ---------------------------------------------------------------- animação do corpo
def vive(c, pid, t, t1=None, fala=False, cabeca=True):
    """Piscar sempre, falar (boca) e cabeça balançando de leve, de t até o fim da cena."""
    t1 = _fim(c) if t1 is None else t1
    D = max(0.4, t1 - t)
    per = 2.3 + (_seed(pid) % 7) * 0.15
    c.a(f"tl.to('#{pid} .j-olho',{{keyframes:{{'0%':{{scaleY:1}},'88%':{{scaleY:1}},'94%':{{scaleY:0.1}},'100%':{{scaleY:1}}}},"
        f"duration:{per:.2f},repeat:{max(0, int(D / per))},ease:'none',svgOrigin:'28 -56'}},{q(t)});")
    if fala:
        c.a(f"tl.to('#{pid} .j-boca',{{scaleY:2.2,duration:0.13,yoyo:true,repeat:{max(1, int(D / 0.13))},ease:'sine.inOut',svgOrigin:'33 -23'}},{q(t)});")
    if cabeca:
        c.a(f"tl.to('#{pid} .j-cab',{{rotation:{3 if _seed(pid) % 2 else -3},duration:1.4,yoyo:true,repeat:{max(1, int(D / 1.4))},"
            f"ease:'sine.inOut',svgOrigin:'0 0'}},{q(t)});")


def anda(c, pid, t, dx, dur, bracos=True, some=False):
    """Anda dx unidades pra frente em dur s (pernas e braços alternando, corpo quicando) e para."""
    passo = 0.27
    n = max(1, int(round(dur / passo)))
    rep = n - 1 if n % 2 else n   # termina de volta no começo
    c.a(f"tl.fromTo('#{pid}',{{x:0}},{{x:{dx:.0f},duration:{dur:.2f},ease:'none'}},{q(t)});")
    c.a(f"tl.fromTo('#{pid} .j-pt',{{rotation:-24}},{{rotation:24,duration:{passo},yoyo:true,repeat:{rep},ease:'sine.inOut',svgOrigin:'0 0'}},{q(t)});")
    c.a(f"tl.fromTo('#{pid} .j-pf',{{rotation:24}},{{rotation:-24,duration:{passo},yoyo:true,repeat:{rep},ease:'sine.inOut',svgOrigin:'0 0'}},{q(t)});")
    c.a(f"tl.fromTo('#{pid} .j-pts, #{pid} .j-pfs',{{rotation:0}},{{rotation:22,duration:{passo / 2:.3f},yoyo:true,repeat:{2 * rep + 1},ease:'sine.inOut',svgOrigin:'0 0'}},{q(t)});")
    c.a(f"tl.fromTo('#{pid} .j-cq',{{y:0}},{{y:-9,duration:{passo / 2:.3f},yoyo:true,repeat:{2 * rep + 1},ease:'sine.inOut'}},{q(t)});")
    if bracos:
        c.a(f"tl.fromTo('#{pid} .j-bt',{{rotation:18}},{{rotation:-18,duration:{passo},yoyo:true,repeat:{rep},ease:'sine.inOut',svgOrigin:'0 0'}},{q(t)});")
        c.a(f"tl.fromTo('#{pid} .j-bf',{{rotation:-18}},{{rotation:18,duration:{passo},yoyo:true,repeat:{rep},ease:'sine.inOut',svgOrigin:'0 0'}},{q(t)});")
    else:
        c.a(f"tl.fromTo('#{pid} .j-bt',{{rotation:14}},{{rotation:-14,duration:{passo},yoyo:true,repeat:{rep},ease:'sine.inOut',svgOrigin:'0 0'}},{q(t)});")
    fim = t + dur
    c.a(f"tl.to('#{pid} .j-pt, #{pid} .j-pf, #{pid} .j-pts, #{pid} .j-pfs, #{pid} .j-bt, #{pid} .j-bf',{{rotation:0,duration:0.2,ease:'power1.out',svgOrigin:'0 0'}},{q(fim)});")
    if some:
        c.a(f"tl.to('#{pid}',{{opacity:0,duration:0.25}},{q(fim - 0.1)});")


def _angs(pose, lado):
    spec = POSES[pose][lado]
    return (spec[1], spec[2]) if spec[0] == 'a' else _ik(spec[0], spec[1])


def muda_pose(c, pid, de, para, t, dur=0.45, lados=('f',)):
    """Troca a pose dos braços no meio da cena (mesma postura sentada/em pé): gira ombro e cotovelo pela diferença
    entre as duas poses. Ex.: muda_pose(c, pid, 'coca', 'mostra', t) = tira a mão da cabeça e mostra a carteira."""
    for lado in lados:
        (a0, b0), (a1, b1) = _angs(de, lado), _angs(para, lado)
        cl = 'j-bt' if lado == 't' else 'j-bf'
        c.a(f"tl.to('#{pid} .{cl}',{{rotation:{a1 - a0:.1f},duration:{dur},ease:'power2.inOut',svgOrigin:'0 0'}},{q(t)});")
        c.a(f"tl.to('#{pid} .{cl}a',{{rotation:{b1 - b0:.1f},duration:{dur},ease:'power2.inOut',svgOrigin:'0 0'}},{q(t)});")


def digita(c, pid, t, t1=None):
    t1 = _fim(c) if t1 is None else t1
    D = max(0.3, t1 - t)
    c.a(f"tl.fromTo('#{pid} .j-bfa',{{rotation:-7}},{{rotation:7,duration:0.11,yoyo:true,repeat:{max(1, int(D / 0.11))},ease:'sine.inOut',svgOrigin:'0 0'}},{q(t)});")
    c.a(f"tl.fromTo('#{pid} .j-bta',{{rotation:6}},{{rotation:-6,duration:0.13,yoyo:true,repeat:{max(1, int(D / 0.13))},ease:'sine.inOut',svgOrigin:'0 0'}},{q(t + 0.05)});")


def gesticula(c, pid, t, t1=None, parte='j-bfa', amp=10, per=0.4):
    """Balança uma parte (antebraço acenando, mão coçando a cabeça, braço apontando) de t até t1."""
    t1 = _fim(c) if t1 is None else t1
    D = max(0.3, t1 - t)
    c.a(f"tl.fromTo('#{pid} .{parte}',{{rotation:{-amp}}},{{rotation:{amp},duration:{per},yoyo:true,repeat:{max(1, int(D / per))},ease:'sine.inOut',svgOrigin:'0 0'}},{q(t)});")


def respira(c, pid, t, t1=None):
    t1 = _fim(c) if t1 is None else t1
    D = max(0.4, t1 - t)
    c.a(f"tl.fromTo('#{pid} .j-cq',{{y:0}},{{y:-4,duration:1.1,yoyo:true,repeat:{max(1, int(D / 1.1))},ease:'sine.inOut'}},{q(t)});")


# ---------------------------------------------------------------- objetos e móveis (coordenadas de tela; y = chão)
def _mesa_lado(x, y, w, cor='#8A6A45'):
    """Mesa de lado (tampo + pés no chão + gaveteiro): tampo em y-200."""
    e = _esc(cor, 0.78)
    return (f'<ellipse cx="{x + w / 2:.0f}" cy="{y + 4}" rx="{w / 2 + 20:.0f}" ry="10" fill="#000" opacity=".13"/>'
            f'<rect x="{x + 10}" y="{y - 186}" width="16" height="186" fill="{e}"/>'
            f'<rect x="{x + w - 120}" y="{y - 186}" width="104" height="168" rx="4" fill="{_esc(cor, 0.9)}"/>'
            f'<rect x="{x + w - 110}" y="{y - 170}" width="84" height="6" rx="3" fill="{e}"/>'
            f'<rect x="{x + w - 110}" y="{y - 110}" width="84" height="6" rx="3" fill="{e}"/>'
            f'<rect x="{x + w - 30}" y="{y - 186}" width="16" height="186" fill="{e}"/>'
            f'<rect x="{x}" y="{y - 204}" width="{w}" height="20" rx="5" fill="{cor}"/>'
            f'<rect x="{x}" y="{y - 186}" width="{w}" height="5" fill="{e}" opacity=".6"/>')


def _cadeira(x, y, olha=1, cor='#2D3A4F'):
    e = _esc(cor, 0.8)
    return (f'<g transform="translate({x} {y}) scale({olha} 1)">'
            f'<rect x="-74" y="-352" width="22" height="236" rx="11" fill="{e}"/>'
            f'<rect x="-62" y="-122" width="128" height="20" rx="9" fill="{cor}"/>'
            f'<rect x="-6" y="-104" width="12" height="70" fill="#5A5F66"/>'
            f'<rect x="-56" y="-38" width="112" height="9" rx="4" fill="#5A5F66"/>'
            f'<circle cx="-50" cy="-12" r="11" fill="#2A2A2A"/><circle cx="50" cy="-12" r="11" fill="#2A2A2A"/></g>')


def _tela(tipo, w, h, rnd, gid=''):
    """Conteúdo da tela de um monitor (caixa 0..w x 0..h)."""
    if tipo == 'grafico':
        bars = ''.join(f'<rect class="tb" x="{w * (0.14 + 0.19 * k):.0f}" y="{h * (0.82 - 0.16 * (k + 1)):.0f}" width="{w * 0.12:.0f}" '
                       f'height="{h * 0.16 * (k + 1):.0f}" fill="{"#B5523B" if k == 3 else "#2D4A63"}"/>' for k in range(4))
        return f'<rect width="{w}" height="{h}" fill="#F3EEDF"/>{bars}<rect x="{w * .1:.0f}" y="{h * .82:.0f}" width="{w * .8:.0f}" height="3" fill="#2A2A2A"/>'
    if tipo == 'ia':
        return (f'<rect width="{w}" height="{h}" fill="#2A2416"/><rect class="iag" width="{w}" height="{h}" fill="#F2B544" opacity=".0"/>'
                f'<g transform="translate({w / 2:.0f} {h / 2:.0f})"><path class="iast" d="M0 -26 L7 -7 L26 0 L7 7 L0 26 L-7 7 L-26 0 L-7 -7Z" fill="#F2B544"/></g>')
    linhas = ''.join(f'<rect class="tl{k % 3}" x="{w * 0.1:.0f}" y="{h * 0.16 + k * h * 0.13:.0f}" width="{w * rnd.uniform(0.35, 0.78):.0f}" height="{max(4, h * 0.06):.0f}" rx="2" '
                     f'fill="{rnd.choice(("#2D4A63", "#5B7F6E", "#B5523B", "#C9A24A"))}"/>' for k in range(6))
    return f'<rect width="{w}" height="{h}" fill="#EAF2F2"/>{linhas}'


def _monitor(x, y_mesa, w=176, h=118, tela='linhas', rnd=None, mid=''):
    """Monitor de frente sobre a mesa (pé em y_mesa), centro x."""
    rnd = rnd or random.Random(int(x))
    ida = f' id="{mid}"' if mid else ''
    return (f'<g{ida} transform="translate({x - w / 2:.0f} {y_mesa - h - 34:.0f})">'
            f'<rect x="{w / 2 - 8:.0f}" y="{h}" width="16" height="30" fill="#4A4F57"/><rect x="{w / 2 - 40:.0f}" y="{h + 26}" width="80" height="9" rx="4" fill="#4A4F57"/>'
            f'<rect x="-8" y="-8" width="{w + 16}" height="{h + 16}" rx="8" fill="#1E2A3A"/>'
            f'<svg width="{w}" height="{h}" class="scr">{_tela(tela, w, h, rnd)}</svg></g>')


def _xic(x, y, vid):
    return f'<g transform="translate({x} {y}) scale(0.8)">{_xicara(0, 0, vid)}</g>'


def _vaso(x, y, h=200, rnd=None, cls='folha'):
    rnd = rnd or random.Random(int(x))
    folhas = ''.join(f'<path d="M0 0 C{-40 + 18 * k} {-h * 0.3:.0f} {-30 + 14 * k} {-h * 0.75:.0f} {-48 + 24 * k} {-h:.0f} '
                     f'C{-8 + 8 * k} {-h * 0.7:.0f} {8 + 3 * k} {-h * 0.3:.0f} 0 0Z" fill="{c}"/>'
                     for k, c in enumerate(('#3F6B4E', '#4F7F5C', '#5B8F66', '#3F6B4E', '#4F7F5C')))
    return (f'<g transform="translate({x} {y - 70})"><g class="{cls}">{folhas}</g></g>'
            f'<path d="M{x - 42} {y - 76} L{x + 42} {y - 76} L{x + 32} {y} L{x - 32} {y}Z" fill="#B5523B"/>'
            f'<rect x="{x - 46}" y="{y - 84}" width="92" height="14" rx="5" fill="#8E3F2C"/>')


def _seguro(x, y, w, h_cima, h_baixo, livre=False):
    """08/11 (margem segura): centro (x, y) de um texto de peça no MUNDO puxado pra dentro da caixa segura do formato
    (bo.faixa + laterais 170–910, que já descontam o passeio da câmera). livre=True = coordenada local de um grupo
    transformado (não mexe)."""
    if livre:
        return x, y
    a, b = faixa()
    y = min(max(y, a + h_cima), b - h_baixo)
    x = min(max(x, X_LAT[0] + w / 2), X_LAT[1] - w / 2)
    return x, y


def _balao(bid, x, y, texto, cor='#FBF4E4', tinta='#1E2A3A', tam=40, cauda='baixo', icone='', livre=False):
    """Balão/cartão de texto em SVG centrado em (x, y). icone: 'ok' (✓ verde), 'ponto' (bolinha vermelha), 'ia'."""
    tam = max(tam, 48)   # rodada 6: texto de peça ≥ 48 px (o revisor mediu ~25 px de letra nos balões de 36–38)
    tx = texto.upper()
    lw = _txt_larg(tx, tam) + (50 if icone else 0)
    w, h = lw + 56, tam + 34
    x, y = _seguro(x, y, w * 1.08, h / 2 + 30, h / 2 + 22, livre)   # 1,08 = pico do back.out; 30 = sobe ao entrar/flutuar
    ic = ''
    if icone == 'ok':
        ic = f'<circle cx="{-w / 2 + 40:.0f}" cy="0" r="16" fill="#3F7F55"/><path d="M{-w / 2 + 32:.0f} 0 l6 6 l11 -12" stroke="#fff" stroke-width="4" fill="none"/>'
    elif icone == 'ponto':
        ic = f'<circle cx="{-w / 2 + 38:.0f}" cy="0" r="11" fill="#B5523B"/>'
    elif icone == 'ia':
        ic = f'<path transform="translate({-w / 2 + 40:.0f} 0)" d="M0 -16 L4 -4 L16 0 L4 4 L0 16 L-4 4 L-16 0 L-4 -4Z" fill="#F2B544"/>'
    rabo = (f'<path d="M-14 {h / 2 - 2:.0f} L0 {h / 2 + 20:.0f} L14 {h / 2 - 2:.0f}Z" fill="{cor}"/>' if cauda == 'baixo' else '')
    off = 25 if icone else 0
    return (f'<g transform="translate({x:.0f} {y:.0f})"><g id="{bid}" class="balao"><g class="bp">'
            f'<rect x="{-w / 2:.0f}" y="{-h / 2 + 8:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{h / 2:.0f}" fill="#000" opacity=".16"/>'
            f'<rect x="{-w / 2:.0f}" y="{-h / 2:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{h / 2:.0f}" fill="{cor}"/>{rabo}{ic}'
            f'<text class="tc" x="{off}" y="{tam * 0.36:.0f}" text-anchor="middle" font-size="{tam}" fill="{tinta}">{_html.escape(tx)}</text></g></g></g>')


def _pop_balao(c, bid, t, som='pop2'):
    # escala/opacidade SÓ no grupo de dentro (.bp); o de fora só anda em y (flutua) — nunca os dois no mesmo <g>
    c.a(f"tl.fromTo('#{bid} .bp',{{opacity:0,scale:0.4,transformOrigin:'50% 100%'}},{{opacity:1,scale:1,duration:0.38,ease:'back.out(2.2)',transformOrigin:'50% 100%'}},{q(t)});")
    c.a(f"tl.fromTo('#{bid}',{{y:30}},{{y:0,duration:0.38,ease:'power2.out'}},{q(t)});")
    c.a(f"tl.to('#{bid}',{{y:-8,duration:1.0,yoyo:true,repeat:{max(1, int((_fim(c) - t - 0.5) / 1.0))},ease:'sine.inOut'}},{q(t + 0.5)});")
    if som:
        an.som(t, som, 0.22)


def _etiqueta(x, y, texto, tam=34, cor='#FBF4E4', tinta='#1E2A3A', rot=-3, eid='', livre=False):
    tam = max(tam, 48)
    tx = texto.upper()
    w = _txt_larg(tx, tam) + 40
    x, y = _seguro(x, y, w * 1.1, tam * 0.75 + 20, tam * 0.75 + 20, livre)
    ida = f' id="{eid}"' if eid else ''
    return (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot})"><g{ida}><g class="bp">'
            f'<rect x="{-w / 2:.0f}" y="{-tam * 0.75:.0f}" width="{w:.0f}" height="{tam * 1.5:.0f}" rx="6" fill="{cor}"/>'
            f'<rect x="{-w / 2:.0f}" y="{tam * 0.75 - 6:.0f}" width="{w:.0f}" height="6" fill="#000" opacity=".12"/>'
            f'<text class="tc" x="0" y="{tam * 0.36:.0f}" text-anchor="middle" font-size="{tam}" fill="{tinta}">{_html.escape(tx)}</text></g></g></g>')


def _papeis_voando(c, gid, x, y, t, n=3, sobe=520, cor='#FBF6EA'):
    """Folhas soltas voando (sobem girando e somem), em loop até o fim da cena."""
    t1 = _fim(c)
    fol = ''.join(f'<g transform="translate({x + 30 * k} {y})"><g class="pv"><rect x="-28" y="-36" width="56" height="72" rx="3" fill="{cor}"/>'
                  + ''.join(f'<rect x="-18" y="{-24 + 12 * j}" width="34" height="4" fill="#B7AC98"/>' for j in range(4)) + '</g></g>'
                  for k in range(n))
    D = max(0.8, t1 - t)
    per = 1.9
    c.a(f"tl.fromTo('#{gid} .pv',{{opacity:0,x:0,y:0,rotation:0}},{{opacity:1,x:(i)=>[-220,160,-90,250,-170,60][i%6],y:{-sobe},rotation:(i)=>[-190,140,-60,200,-120,90][i%6],"
        f"duration:{per},ease:'power1.out',repeat:{max(0, int(D / per))},stagger:{{each:0.55,repeat:{max(0, int(D / per))}}}}},{q(t)});")
    an.som(t, 'papel', 0.2)
    return f'<g id="{gid}">{fol}</g>'


def _relogio3(x, y, r=52, hora=None, rid=''):
    """Relógio de parede; hora=(h, m) fixa os ponteiros; o dos segundos anda (classe seg)."""
    h, m = hora or (10, 10)
    ah, am = (h % 12) * 30 + m * 0.5, m * 6
    return (f'<g transform="translate({x} {y})"><circle r="{r + 7}" fill="#5A3E28"/><circle r="{r}" fill="#FBF6EA"/>'
            + ''.join(f'<rect x="-1.6" y="{-r + 5}" width="3.2" height="{10 if k % 3 == 0 else 5}" fill="#3A2A1A" transform="rotate({k * 30})"/>' for k in range(12))
            + f'<rect x="-3" y="{-r * 0.52:.0f}" width="6" height="{r * 0.52:.0f}" rx="3" fill="#1E2A3A" transform="rotate({ah:.0f})"/>'
              f'<rect x="-2" y="{-r * 0.78:.0f}" width="4" height="{r * 0.78:.0f}" rx="2" fill="#1E2A3A" transform="rotate({am:.0f})"/>'
              f'<g class="seg"><rect x="-1" y="{-r * 0.85:.0f}" width="2" height="{r * 0.95:.0f}" fill="#B5523B"/></g><circle r="5" fill="#1E2A3A"/></g>')


def _moedas_caindo(c, gid, x0, y0, x1, y1, t, n=6, per=0.9, arco=False):
    """Moedas caindo de (x0,y0) até (x1,y1) em loop (arco=True faz parábola pro lado)."""
    t1 = _fim(c)
    D = max(0.6, t1 - t)
    mo = ''.join(f'<g transform="translate({x0} {y0})"><g class="mo"><circle r="17" fill="#C9A24A"/><circle r="12" fill="#F2B544"/>'
                 f'<rect x="-3" y="-7" width="6" height="14" rx="2" fill="#C9A24A"/></g></g>' for _ in range(n))
    rep = max(0, int(D / per))
    st = per / n
    c.a(f"tl.fromTo('#{gid} .mo',{{x:0,opacity:1}},{{x:{x1 - x0},duration:{per},ease:'{'power1.out' if arco else 'none'}',repeat:{rep},stagger:{{each:{st:.3f},repeat:{rep}}}}},{q(t)});")
    c.a(f"tl.fromTo('#{gid} .mo',{{y:{'-30' if arco else 0}}},{{y:{y1 - y0},duration:{per},ease:'power2.in',repeat:{rep},stagger:{{each:{st:.3f},repeat:{rep}}}}},{q(t)});")
    c.a(f"tl.fromTo('#{gid}',{{opacity:0}},{{opacity:1,duration:0.2}},{q(t)});")
    return f'<g id="{gid}">{mo}</g>'


# ---------------------------------------------------------------- AMBIENTES (fundo em camadas, coordenadas de tela)
def _cam3(corpo, vel, cls=''):
    return (f'<div class="cam sala {cls}" data-vel="{vel}" style="height:1920px"><svg width="1680" height="1920" '
            f'viewBox="-300 0 1680 1920" overflow="visible">{corpo}</svg></div>')


def _piso(y0, cor, linha, vp=(540, 720), tabuas=True):
    out = [f'<rect x="-300" y="{y0}" width="1680" height="{1920 - y0}" fill="{cor}"/>']
    if tabuas:
        for k in range(-16, 17):
            xt = 540 + k * 96
            xb = vp[0] + (xt - vp[0]) * (1920 - vp[1]) / (y0 - vp[1])
            out.append(f'<path d="M{xt} {y0} L{xb:.0f} 1920" stroke="{linha}" stroke-width="3"/>')
    for i in range(1, 8):
        yy = y0 + (1920 - y0) * (i / 7) ** 1.7
        out.append(f'<rect x="-300" y="{yy:.0f}" width="1680" height="2" fill="{linha}" opacity=".55"/>')
    out.append(f'<rect x="-300" y="{y0}" width="1680" height="26" fill="#000" opacity=".10"/>')
    return ''.join(out)


def _janelao(y0, y1, noite, rnd, caixilho, ceu):
    alt = y1 - y0
    gid = 'jn' if noite else 'jd'
    cid = f'jc{gid}{y0}'
    pred1 = an._predios(rnd, 1680, alt, 0, alt * 0.25, alt * 0.7, '#22305A' if noite else '#B9D0D8', wmin=60, wmax=130)
    pred2 = an._predios(rnd, 1680, alt, 0, alt * 0.12, alt * 0.45, '#16213F' if noite else '#8DAFBD',
                        janela=('#1F2C52', '#F2C46B') if noite else ('#7A9DAC', '#EEF3EF'), acesas=0.4 if noite else 0.2, wmin=90, wmax=170)
    nuv = '' if noite else ''.join(an._nuvem(rnd.uniform(-200, 1300), y0 + rnd.uniform(40, alt * 0.4), rnd.uniform(0.5, 0.8), '#FFFFFF') for _ in range(5))
    est = ''.join(f'<circle cx="{rnd.uniform(-300, 1380):.0f}" cy="{y0 + rnd.uniform(10, alt * 0.5):.0f}" r="{rnd.choice((1.5, 2.2))}" fill="#fff" opacity=".8"/>' for _ in range(40)) if noite else ''
    mull = ''.join(f'<rect x="{x}" y="{y0}" width="14" height="{alt}" fill="{caixilho}"/>' for x in range(-300, 1400, 176))
    return (f'<defs><linearGradient id="{cid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ceu[0]}"/><stop offset="1" stop-color="{ceu[1]}"/></linearGradient></defs>'
            f'<rect x="-300" y="{y0}" width="1680" height="{alt}" fill="url(#{cid})"/>{est}{nuv}'
            f'<g transform="translate(-300 {y0})">{pred1}{pred2}</g>'
            f'<rect x="-300" y="{y0}" width="1680" height="{alt}" fill="#FFFFFF" opacity="{0.03 if noite else 0.12}"/>'
            f'{mull}<rect x="-300" y="{y0 - 14}" width="1680" height="16" fill="{caixilho}"/>'
            f'<rect x="-300" y="{y0 + alt * 0.62:.0f}" width="1680" height="10" fill="{caixilho}"/>'
            f'<rect x="-300" y="{y1}" width="1680" height="20" fill="{_esc(caixilho, 1.25)}"/>')


def _quadro_arte(x, y, w, h, rnd, moldura='#5A3E28'):
    ceu = rnd.choice(('#A9CFDD', '#F0C38E', '#CFE0D0'))
    mt = rnd.choice(('#6F9AA8', '#B5523B', '#5B7F6E'))
    return (f'<rect x="{x - 8}" y="{y - 8}" width="{w + 16}" height="{h + 16}" fill="{moldura}"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{ceu}"/>'
            f'<path d="M{x} {y + h} L{x + w * 0.35:.0f} {y + h * 0.4:.0f} L{x + w * 0.6:.0f} {y + h * 0.75:.0f} L{x + w * 0.8:.0f} {y + h * 0.5:.0f} L{x + w} {y + h}Z" fill="{mt}"/>'
            f'<circle cx="{x + w * 0.75:.0f}" cy="{y + h * 0.25:.0f}" r="{min(w, h) * 0.1:.0f}" fill="#FBF6EA"/>')


def _pendente(x, comp, cor, luz=False):
    glow = (f'<path d="M-40 {comp + 52} L40 {comp + 52} L90 {comp + 170} L-90 {comp + 170}Z" fill="#F7D98A" opacity=".10"/>' if luz else '')
    return (f'<g transform="translate({x} 0)"><g class="pend">{glow}<rect x="-2" y="0" width="4" height="{comp}" fill="#3A3A3A"/>'
            f'<path d="M-50 {comp + 54} L50 {comp + 54} L26 {comp} L-26 {comp}Z" fill="{cor}"/>'
            f'<ellipse cx="0" cy="{comp + 54}" rx="50" ry="9" fill="#F7D98A" opacity="{0.95 if luz else 0.7}"/></g></g>')


def _arvore(x, y, h, cor, sombra, rnd):
    r = h * 0.32
    copa = ''.join(f'<circle cx="{x + dx * r:.0f}" cy="{y - h * 0.62 + dy * r:.0f}" r="{r * rr:.0f}" fill="{cor}"/>'
                   for dx, dy, rr in ((0, 0, 1), (-0.7, 0.3, 0.75), (0.7, 0.3, 0.75), (0, -0.55, 0.75), (-0.4, -0.35, 0.6), (0.45, -0.3, 0.6)))
    somb = ''.join(f'<circle cx="{x + dx * r + r * 0.25:.0f}" cy="{y - h * 0.62 + dy * r + r * 0.1:.0f}" r="{r * rr * 0.8:.0f}" fill="{sombra}"/>'
                   for dx, dy, rr in ((0.35, 0.2, 0.9), (0.75, 0.35, 0.6)))
    return (f'<ellipse cx="{x + h * 0.18:.0f}" cy="{y}" rx="{h * 0.3:.0f}" ry="12" fill="#000" opacity=".18"/>'
            f'<rect x="{x - h * 0.035:.0f}" y="{y - h * 0.55:.0f}" width="{h * 0.07:.0f}" height="{h * 0.55:.0f}" fill="#6B4E31"/>'
            f'<rect x="{x:.0f}" y="{y - h * 0.55:.0f}" width="{h * 0.035:.0f}" height="{h * 0.55:.0f}" fill="#4F3822"/>'
            f'<g class="copa">{copa}{somb}</g>')


def _poste(x, y, h=470, cor='#2E3640', acesa=False):
    luz = '<circle cx="0" cy="0" r="60" fill="#F7D98A" opacity=".25"/>' if acesa else ''
    return (f'<rect x="{x - 7}" y="{y - h}" width="14" height="{h}" fill="{cor}"/><rect x="{x - 16}" y="{y - 24}" width="32" height="24" fill="{cor}"/>'
            f'<path d="M{x} {y - h} Q{x} {y - h - 40} {x + 50} {y - h - 40}" stroke="{cor}" stroke-width="10" fill="none"/>'
            f'<g transform="translate({x + 60} {y - h - 28})">{luz}<path d="M-26 -14 L26 -14 L16 6 L-16 6Z" fill="{cor}"/>'
            f'<rect x="-14" y="4" width="28" height="7" fill="{"#F7D98A" if acesa else "#E9DFC6"}"/></g>')


def _fachadas(rnd, y_chao, tarde=False):
    cores = (('#C98B6B', '#B5523B'), ('#E2D3B0', '#C9A24A'), ('#9DB3A0', '#5B7F6E'), ('#D9B98C', '#8E3F2C'),
             ('#A9BCC8', '#2D4A63'), ('#E8C9A0', '#B5523B'))
    nomes = ('CAFÉ', 'PADARIA', 'LIVROS', 'FLORES', 'MERCADO', 'ÓTICA', 'FARMÁCIA')
    out, x, k = [], -300, 0
    while x < 1400:
        w = rnd.uniform(230, 330)
        topo = y_chao - rnd.uniform(560, 760)
        cor, tolda = cores[(k + rnd.randint(0, 5)) % len(cores)]
        if tarde:
            cor, tolda = _esc(cor, 0.62), _esc(tolda, 0.7)
        sombra = _esc(cor, 0.78)
        out.append(f'<rect x="{x:.0f}" y="{topo:.0f}" width="{w:.0f}" height="{y_chao - topo:.0f}" fill="{cor}"/>'
                   f'<rect x="{x + w - 26:.0f}" y="{topo:.0f}" width="26" height="{y_chao - topo:.0f}" fill="{sombra}"/>'
                   f'<rect x="{x - 6:.0f}" y="{topo - 14:.0f}" width="{w + 12:.0f}" height="18" fill="{_esc(cor, 0.7)}"/>')
        for jy in range(int(topo + 50), int(y_chao - 300), 120):
            for jx in range(int(x + 34), int(x + w - 70), 84):
                acesa = tarde and rnd.random() < 0.45
                out.append(f'<rect x="{jx}" y="{jy}" width="46" height="70" fill="{"#F2C46B" if acesa else ("#2A3550" if tarde else "#6F95A5")}"/>'
                           f'<rect x="{jx - 4}" y="{jy + 70}" width="54" height="7" fill="{sombra}"/>')
        # térreo: toldo listrado, vitrine, porta e letreiro
        ty = y_chao - 230
        n_l = int(w // 40)
        out.append(''.join(f'<path d="M{x + 10 + j * 40:.0f} {ty} L{x + 50 + j * 40:.0f} {ty} L{x + 50 + j * 40:.0f} {ty + 50} '
                           f'Q{x + 30 + j * 40:.0f} {ty + 64} {x + 10 + j * 40:.0f} {ty + 50}Z" fill="{tolda if j % 2 == 0 else "#FBF6EA"}"/>' for j in range(n_l)))
        out.append(f'<rect x="{x + 20:.0f}" y="{ty + 70}" width="{w * 0.55:.0f}" height="150" fill="{"#F2C46B" if tarde else "#BFDCE6"}" opacity=".9"/>'
                   f'<rect x="{x + w * 0.66:.0f}" y="{ty + 50}" width="{w * 0.24:.0f}" height="180" fill="{_esc(cor, 0.55)}"/>'
                   f'<rect x="{x + 20:.0f}" y="{ty - 70}" width="{w - 60:.0f}" height="56" rx="4" fill="{_esc(tolda, 0.85)}"/>'
                   f'<rect x="{x + 20 + (w - 60) * 0.2:.0f}" y="{ty - 48}" width="{(w - 60) * 0.6:.0f}" height="12" rx="6" fill="#FBF6EA" opacity=".85"/>')   # letreiro sem palavra (cortava na borda)
        x += w + rnd.uniform(0, 10)
        k += 1
    return ''.join(out)


def fundo(tipo, seed, op=None):
    """Camadas do ambiente: (lista de camadas de trás, camada da frente). Chamado pelo animada._cenario_html."""
    rnd = random.Random(seed)
    op = op or {}
    if tipo in ('escritorio', 'escritorio_noite', 'reuniao', 'escritorio2'):
        noite = tipo == 'escritorio_noite'
        pal = {
            'escritorio': dict(parede='#EADFC8', teto='#D6C6A8', painel='#C6A97C', painel_l='#B0925F', rodape='#6B4E31',
                               piso='#B68E5F', piso_l='#A47D50', caix='#4F5B63', ceu=('#A9D3E2', '#E4EEE9'), lum='#2F5A47'),
            'escritorio_noite': dict(parede='#2F3A58', teto='#222B44', painel='#3A4567', painel_l='#323C5C', rodape='#1C2440',
                                     piso='#2B3352', piso_l='#232A45', caix='#161D33', ceu=('#0B1530', '#2A3B6B'), lum='#C9A24A'),
            'escritorio2': dict(parede='#E2D6BE', teto='#3A3A3A', painel='#B5935F', painel_l='#9C7A4A', rodape='#5A3E28',
                                piso='#A9825A', piso_l='#977249', caix='#4F5B63', ceu=('#A9D3E2', '#E4EEE9'), lum='#2A2A2A'),
            'reuniao': dict(parede='#D5DDD6', teto='#BCC7C0', painel='#7A5A3C', painel_l='#6A4C30', rodape='#4A3422',
                            piso='#6E7A80', piso_l='#626D73', caix='#3F4A50', ceu=('#B8DCE6', '#EAF0EA'), lum='#B5523B'),
        }[tipo]
        A = [f'<rect x="-300" y="0" width="1680" height="{PAREDE_FIM}" fill="{pal["parede"]}"/>',
             f'<rect x="-300" y="0" width="1680" height="80" fill="{pal["teto"]}"/>',
             ''.join(f'<rect x="{x}" y="22" width="150" height="16" rx="4" fill="{"#F7E7B5" if not noite else "#3A4466"}"/>' for x in range(-260, 1380, 330)),
             (_topo_ripas() if tipo == 'reuniao' else _topo_tijolo(rnd, op.get('topo', 'relogio')) if tipo == 'escritorio2' else _janelao(130, 470, noite, rnd, pal['caix'], pal['ceu'])),
             f'<rect x="-300" y="1170" width="1680" height="{PAREDE_FIM - 1170}" fill="{pal["painel"]}"/>',
             ''.join(f'<rect x="{x}" y="1170" width="6" height="{PAREDE_FIM - 1170}" fill="{pal["painel_l"]}"/>' for x in range(-300, 1400, 130)),
             f'<rect x="-300" y="1160" width="1680" height="14" fill="{pal["painel_l"]}"/>',
             f'<rect x="-300" y="{PAREDE_FIM - 18}" width="1680" height="18" fill="{pal["rodape"]}"/>',
             _quadro_arte(-180, 880, 200, 150, rnd), _quadro_arte(1150, 860, 180, 220, rnd),
             _quadro_arte(112, 1010, 116, 110, rnd), _quadro_arte(852, 990, 116, 130, rnd)]
        L = ''.join(_pendente(x, comp, pal['lum'], luz=noite) for x, comp in ((150, 300), (930, 300), (-160, 260), (1240, 260)))
        if tipo == 'escritorio2':   # trilho de spots no lugar das luminárias penduradas
            L = ('<rect x="-300" y="96" width="1680" height="12" fill="#2A2A2A"/>'
                 + ''.join(f'<g transform="translate({x} 108) rotate({(-1) ** (x // 180) * 18})"><rect x="-14" y="0" width="28" height="44" rx="6" fill="#2A2A2A"/>'
                           f'<path d="M-14 44 L14 44 L60 300 L-60 300Z" fill="#FFF1C8" opacity=".09"/></g>' for x in range(-240, 1400, 180)))
        B = _piso(PAREDE_FIM, pal['piso'], pal['piso_l'], tabuas=tipo != 'reuniao')
        if tipo == 'reuniao':
            B += f'<ellipse cx="540" cy="1720" rx="620" ry="140" fill="#000" opacity=".08"/>'
        C = _vaso(-40, 1960, 300, rnd) + _vaso(1130, 1990, 260, rnd)
        return [_cam3(''.join(A), 18), _cam3(L, 30), _cam3(B, 50, 'piso')], _cam3(C, 85)
    if tipo == 'quarto_noite':
        # quarto à noite: parede azul-petróleo, janela com cortina e lua, quadro, prateleira; luz baixa do abajur
        A = ('<rect x="-300" y="0" width="1680" height="1400" fill="#24324A"/><rect x="-300" y="1180" width="1680" height="220" fill="#1F2B40"/>'
             '<rect x="-300" y="1176" width="1680" height="8" fill="#18223A"/>'
             '<rect x="40" y="130" width="380" height="330" fill="#0E1834"/>'
             + f'<g transform="translate(40 260)">{an._predios(rnd, 380, 200, 0, 70, 180, "#16213F", janela=("#1F2C52", "#F2C46B"), acesas=0.4, wmin=50, wmax=90)}</g>'
             + '<circle cx="330" cy="200" r="30" fill="#F3EBCF"/><rect x="40" y="130" width="380" height="330" fill="none" stroke="#18223A" stroke-width="16"/>'
             '<rect x="222" y="130" width="14" height="330" fill="#18223A"/>'
             + ''.join(f'<path d="M{x} 100 Q{x + 40} 300 {x + 10} 500 L{x + 80} 500 Q{x + 100} 300 {x + 80} 100Z" fill="#5B4A7A"/>' for x in (-30, 410))
             + _quadro_arte(640, 170, 300, 220, rnd, '#18223A')
             + '<rect x="-300" y="1382" width="1680" height="18" fill="#141C30"/>')
        L = ('<g transform="translate(-40 0)"><path d="M-70 1300 L70 1300 L50 1230 L-50 1230Z" fill="#C9A24A"/>'
             '<path d="M-70 1300 L70 1300 L260 1740 L-260 1740Z" fill="#F7D98A" opacity=".08"/></g>')
        B = _piso(1400, '#2E2A3A', '#262230') + '<ellipse cx="480" cy="1770" rx="520" ry="110" fill="#5B4A7A" opacity=".45"/>'
        C = _vaso(1160, 1990, 260, rnd)
        return [_cam3(A, 18), _cam3(L, 30), _cam3(B, 50, 'piso')], _cam3(C, 85)
    if tipo == 'sala_noite':
        A = ('<rect x="-300" y="0" width="1680" height="1400" fill="#3B3352"/>'
             '<rect x="-300" y="1150" width="1680" height="250" fill="#332B47"/><rect x="-300" y="1146" width="1680" height="10" fill="#2A2340"/>'
             + '<rect x="560" y="130" width="460" height="350" fill="#0E1834"/>'
             + f'<g transform="translate(560 250)">{an._predios(rnd, 460, 230, 0, 80, 200, "#16213F", janela=("#1F2C52", "#F2C46B"), acesas=0.45, wmin=50, wmax=100)}</g>'
             + '<circle cx="880" cy="200" r="34" fill="#F3EBCF"/><circle cx="880" cy="200" r="64" fill="#F3EBCF" opacity=".12"/>'
             + '<rect x="560" y="130" width="460" height="350" fill="none" stroke="#2A2236" stroke-width="18"/><rect x="782" y="130" width="16" height="350" fill="#2A2236"/>'
             + ''.join(f'<path d="M{x} 100 Q{x + 40} 300 {x + 10} 520 L{x + 90} 520 Q{x + 110} 300 {x + 90} 100Z" fill="#7E3526"/>' for x in (470, 1010))
             + _quadro_arte(90, 190, 300, 210, rnd, '#2A1E16')
             + _quadro_arte(-150, 880, 220, 160, rnd, '#2A1E16') + _quadro_arte(1110, 900, 170, 130, rnd, '#2A1E16')
             + '<rect x="-300" y="1382" width="1680" height="18" fill="#221C33"/>')
        L = ('<g transform="translate(-120 0)"><rect x="-4" y="1080" width="8" height="660" fill="#2A2A2A"/>'
             '<path d="M-60 1080 L60 1080 L40 1000 L-40 1000Z" fill="#C9A24A"/><path d="M-60 1080 L60 1080 L240 1700 L-240 1700Z" fill="#F7D98A" opacity=".07"/>'
             '<ellipse cx="0" cy="1742" rx="50" ry="10" fill="#2A2A2A"/></g>')
        B = _piso(1400, '#3A2D3E', '#30253A') + '<ellipse cx="560" cy="1760" rx="560" ry="120" fill="#7E3526" opacity=".45"/>'
        C = _vaso(1180, 1980, 300, rnd)
        return [_cam3(A, 16), _cam3(L, 30), _cam3(B, 50, 'piso')], _cam3(C, 85)
    if tipo in ('rua', 'rua_tarde', 'rua_noite'):
        tarde = tipo in ('rua_tarde', 'rua_noite')
        noite_ = tipo == 'rua_noite'
        lon = an._predios(rnd, 1680, 600, 0, 140, 380, '#1C2748' if noite_ else ('#7E6A86' if tarde else '#B7CCD4'), wmin=70, wmax=150,
                          janela=('#1F2C52', '#F2C46B') if noite_ else None, acesas=0.3)
        A = f'<g transform="translate(-300 {1180 - 600})">{lon}</g>'
        y_ch = 1560
        B = (_fachadas(rnd, y_ch, tarde)
             + f'<rect x="-300" y="{y_ch}" width="1680" height="130" fill="{"#8C7F86" if tarde else "#D3C8B2"}"/>'
             + ''.join(f'<rect x="{x}" y="{y_ch}" width="3" height="130" fill="#000" opacity=".08"/>' for x in range(-300, 1400, 90))
             + f'<rect x="-300" y="1690" width="1680" height="14" fill="{"#6E6470" if tarde else "#9A9282"}"/>'
             + f'<rect x="-300" y="1704" width="1680" height="216" fill="{"#3E3846" if tarde else "#5B616B"}"/>'
             + ''.join(f'<rect x="{x}" y="1812" width="70" height="8" fill="#E9DFC6" opacity=".7"/>' for x in range(-300, 1400, 150))
             + ''.join(_arvore(x, 1620, 360, '#4F7F5C' if not tarde else '#3E5A48', '#3F6B4E' if not tarde else '#2E4436', rnd) for x in (-200, 360, 900, 1290))
             + ''.join(_poste(x, 1630, 470, acesa=tarde) for x in (90, 640, 1200)))
        C = ''.join(f'<ellipse cx="{x}" cy="1930" rx="150" ry="90" fill="{"#3F6B4E" if not tarde else "#2E4436"}"/>' for x in (-120, 1180))
        return [_cam3(A, 16), _cam3(B, 50, 'piso')], _cam3(C, 85)
    if tipo in ('celular', 'celular_dia'):
        noite = tipo == 'celular'
        base = '#141C33' if noite else '#E7D7B9'
        bok = ''.join(f'<circle cx="{rnd.uniform(-300, 1380):.0f}" cy="{rnd.uniform(0, 1920):.0f}" r="{rnd.uniform(40, 140):.0f}" '
                      f'fill="{rnd.choice(("#F2C46B", "#B5523B", "#8FC1D4")) if noite else rnd.choice(("#FFFFFF", "#F2C46B", "#C6A97C"))}" '
                      f'opacity="{rnd.uniform(0.06, 0.18):.2f}"/>' for _ in range(26))
        return [_cam3(f'<rect x="-300" y="0" width="1680" height="1920" fill="{base}"/>', 6), _cam3(bok, 24, 'piso')], ''
    if tipo == 'recepcao':
        # recepção / entrada: porta de vidro grande à esquerda (rua lá fora), parede de ripas atrás do balcão, piso de placas
        A = ('<rect x="-300" y="0" width="1680" height="1400" fill="#E4DED0"/><rect x="-300" y="0" width="1680" height="80" fill="#CFC7B4"/>'
             + ''.join(f'<rect x="{x}" y="24" width="180" height="14" rx="4" fill="#F7E7B5"/>' for x in range(-260, 1380, 320))
             + ''.join(f'<rect x="{x}" y="80" width="40" height="60" fill="{("#B08A5E", "#9C7A50")[(x // 48) % 2]}"/>' for x in range(-300, 1400, 48))
             + '<path d="M540 140 L540 230" stroke="#3A3A3A" stroke-width="4"/>'
             '<ellipse cx="540" cy="270" rx="320" ry="50" fill="none" stroke="#C9A24A" stroke-width="16"/>'
             '<ellipse cx="540" cy="270" rx="320" ry="50" fill="none" stroke="#FFF1C8" stroke-width="5"/>'
             + ''.join(f'<path d="M{x} 140 L{x} 300" stroke="#3A3A3A" stroke-width="3"/><path d="M{x - 40} 300 L{x + 40} 300 L{x + 30} 350 L{x - 30} 350Z" fill="#B5523B"/>'
                       + ''.join(f'<path d="M{x - 30 + 15 * j} 345 Q{x - 40 + 20 * j} 420 {x - 30 + 18 * j} 470" stroke="#4F7F5C" stroke-width="9" fill="none" stroke-linecap="round"/>' for j in range(5))
                       for x in (60, 1020))
             + ''.join(f'<rect x="{x}" y="880" width="22" height="520" fill="{"#B08A5E" if (x // 30) % 2 else "#9C7A50"}"/>' for x in range(600, 1400, 30))
             + '<rect x="-300" y="900" width="560" height="500" fill="#3F4A50"/>'   # porta de vidro abaixo do letreiro
             '<rect x="-280" y="920" width="520" height="460" fill="#BFDCE6"/>'
             + f'<g transform="translate(-280 1100)">{an._predios(rnd, 520, 280, 0, 120, 260, "#8DAFBD", wmin=60, wmax=120)}</g>'
             '<rect x="-280" y="1300" width="520" height="80" fill="#C8BBA0"/>'
             '<rect x="-30" y="920" width="16" height="460" fill="#3F4A50"/><rect x="-280" y="920" width="520" height="460" fill="#FFFFFF" opacity=".12"/>'
             '<rect x="-300" y="1382" width="1680" height="18" fill="#6B5A48"/>')
        L = ''.join(_pendente(x, comp, '#2D4A63') for x, comp in ((150, 300), (930, 300), (1240, 260)))
        B = (_piso(1400, '#D3CAB8', '#BEB39E', tabuas=False)
             + ''.join(f'<path d="M{540 + k * 160} 1400 L{540 + (540 + k * 160 - 540) * 1.9:.0f} 1920" stroke="#BEB39E" stroke-width="3"/>' for k in range(-9, 10)))
        C = _vaso(-40, 1960, 300, rnd) + _vaso(1130, 1990, 260, rnd)
        return [_cam3(A, 18), _cam3(L, 30), _cam3(B, 50, 'piso')], _cam3(C, 85)
    if tipo == 'deposito':
        # depósito / expedição: parede de chapa, clarabóias, treliça, estantes de palete com caixas
        caixas = ''
        for x0 in range(-260, 1380, 260):
            for prat in (1010, 1190, 1370):
                caixas += f'<rect x="{x0}" y="{prat}" width="230" height="12" fill="#D9822B"/>'
                xx = x0 + 8
                while xx < x0 + 210:
                    w_ = rnd.uniform(46, 80)
                    h_ = rnd.uniform(60, 150)
                    caixas += (f'<rect x="{xx:.0f}" y="{prat - h_:.0f}" width="{w_:.0f}" height="{h_:.0f}" fill="{rnd.choice(("#C49A62", "#B58A52", "#D3AE76"))}"/>'
                               f'<rect x="{xx + w_ * 0.4:.0f}" y="{prat - h_:.0f}" width="{w_ * 0.2:.0f}" height="{h_:.0f}" fill="#E3CDA2" opacity=".6"/>')
                    xx += w_ + 4
            caixas += f'<rect x="{x0}" y="840" width="12" height="560" fill="#2D4A63"/><rect x="{x0 + 220}" y="840" width="12" height="560" fill="#2D4A63"/>'
        A = ('<rect x="-300" y="0" width="1680" height="1400" fill="#D3CBBB"/>'
             + ''.join(f'<rect x="{x}" y="0" width="6" height="1400" fill="#C8C0AF"/>' for x in range(-300, 1400, 40))
             + '<rect x="-300" y="0" width="1680" height="470" fill="#8E8A82"/>'
             + ''.join(f'<rect x="{x}" y="0" width="10" height="470" fill="#7E7A72"/>' for x in range(-300, 1400, 28))   # telha ondulada
             + ''.join(f'<rect x="{x}" y="40" width="150" height="330" fill="#E8EDE6" opacity=".55"/>' for x in range(-250, 1400, 420))   # telha translúcida
             + '<rect x="-300" y="60" width="1680" height="18" fill="#3E4650"/><rect x="-300" y="420" width="1680" height="18" fill="#3E4650"/>'
             + ''.join(f'<path d="M{x} 78 L{x + 90} 420 L{x + 180} 78" stroke="#3E4650" stroke-width="10" fill="none"/>' for x in range(-300, 1400, 180))
             + '<rect x="-300" y="438" width="1680" height="40" fill="#000" opacity=".12"/>'
             + caixas + '<rect x="-300" y="1382" width="1680" height="18" fill="#5A646C"/>')
        L = ''.join(_pendente(x, comp, '#3A3A3A', luz=True) for x, comp in ((150, 330), (930, 330), (-160, 300), (1240, 300)))
        B = (_piso(1400, '#A3A39C', '#93938C', tabuas=False)
             + '<path d="M-300 1640 L1380 1640" stroke="#E9B53A" stroke-width="10"/><path d="M-300 1890 L1380 1890" stroke="#E9B53A" stroke-width="12"/>')
        C = ''.join(f'<g transform="translate({x} 1930)"><rect x="-90" y="-120" width="180" height="120" fill="#C49A62"/><rect x="-90" y="-120" width="180" height="16" fill="#A87F4A"/></g>' for x in (-60, 1160))
        return [_cam3(A, 18), _cam3(L, 30), _cam3(B, 50, 'piso')], _cam3(C, 85)
    if tipo == 'copa':
        # copa / cozinha: parede menta em cima, azulejo branco embaixo, armários altos, janela
        az = ''.join(f'<rect x="-300" y="{y}" width="1680" height="2" fill="#D6D0C2"/>' for y in range(960, 1400, 34))
        az += ''.join(f'<rect x="{x + (17 if ((y - 960) // 34) % 2 else 0)}" y="{y}" width="2" height="34" fill="#D6D0C2"/>'
                      for y in range(960, 1400, 34) for x in range(-300, 1400, 68))
        arm = ''.join(f'<rect x="{x}" y="880" width="160" height="150" rx="6" fill="#5B7F6E"/><rect x="{x + 70}" y="980" width="20" height="8" rx="4" fill="#C9A24A"/>'
                      for x in range(-280, -40, 170)) + ''.join(f'<rect x="{x}" y="880" width="160" height="150" rx="6" fill="#5B7F6E"/><rect x="{x + 70}" y="980" width="20" height="8" rx="4" fill="#C9A24A"/>' for x in range(1140, 1400, 170))
        A = ('<rect x="-300" y="0" width="1680" height="1400" fill="#CFE0D3"/><rect x="-300" y="0" width="1680" height="80" fill="#B9CDBF"/>'
             + ''.join(f'<rect x="{x}" y="130" width="160" height="300" rx="6" fill="#5B7F6E"/><rect x="{x + 8}" y="138" width="144" height="284" rx="4" fill="none" stroke="#4A6A5B" stroke-width="4"/>'
                       f'<rect x="{x + 70}" y="400" width="20" height="9" rx="4" fill="#C9A24A"/>' for x in list(range(-300, 340, 170)) + list(range(760, 1400, 170)))
             + ''.join(f'<rect x="360" y="{y}" width="360" height="14" rx="3" fill="#8A6A45"/>' for y in (250, 400))
             + ''.join(f'<path d="M{x} {y - 50} L{x + 38} {y - 50} L{x + 34} {y} L{x + 4} {y}Z" fill="{cor}"/><path d="M{x + 38} {y - 40} q16 0 14 14 q-2 10 -14 10" stroke="{cor}" stroke-width="6" fill="none"/>'
                       for (x, y, cor) in ((390, 250, '#B5523B'), (450, 250, '#F4EFE6'), (510, 250, '#2D4A63'), (570, 250, '#C9A24A'), (630, 250, '#5B7F6E'),
                                           (400, 400, '#F4EFE6'), (470, 400, '#B5523B'), (540, 400, '#F4EFE6')))
             + '<rect x="600" y="330" width="44" height="70" rx="6" fill="#C49A62"/><rect x="654" y="350" width="44" height="50" rx="6" fill="#8A5A2B"/>'
             + '<rect x="-300" y="950" width="1680" height="450" fill="#F1EEE6"/>' + az + arm
             + '<rect x="-300" y="1382" width="1680" height="18" fill="#7A8A80"/>')
        L = ''.join(_pendente(x, comp, '#B5523B') for x, comp in ((150, 300), (930, 300), (-160, 260), (1240, 260)))
        B = _piso(1400, '#D8CFC0', '#C4B9A6', tabuas=False) + ''.join(
            f'<rect x="{x}" y="{y}" width="80" height="{40 + (y - 1400) // 9}" fill="#C4B9A6" opacity=".55"/>'
            for y in range(1400, 1920, 104) for x in range(-300 + (80 if (y // 104) % 2 else 0), 1400, 160))
        C = _vaso(-40, 1960, 300, rnd) + _vaso(1130, 1990, 260, rnd)
        return [_cam3(A, 18), _cam3(L, 30), _cam3(B, 50, 'piso')], _cam3(C, 85)
    if tipo == 'sala_dono':
        # sala do dono: parede verde escura, lambri de madeira, janelão, estantes de livro nas laterais, tapete
        est = ''
        for bx in (-280, 1110):
            est += f'<rect x="{bx}" y="560" width="250" height="840" fill="#4A3422"/>'
            for prat in range(700, 1400, 150):
                xx = bx + 14
                while xx < bx + 230:
                    w_, h_ = rnd.uniform(16, 28), rnd.uniform(70, 120)
                    est += f'<rect x="{xx:.0f}" y="{prat - h_:.0f}" width="{w_:.0f}" height="{h_:.0f}" fill="{rnd.choice(("#B5523B", "#2D4A63", "#C9A24A", "#5B7F6E", "#7E3526", "#E9E4D8"))}"/>'
                    xx += w_ + 2
                est += f'<rect x="{bx}" y="{prat}" width="250" height="12" fill="#3A2818"/>'
        A = ('<rect x="-300" y="0" width="1680" height="1400" fill="#2F4A3E"/><rect x="-300" y="0" width="1680" height="80" fill="#26392F"/>'
             + ''.join(f'<path d="M{x} 470 L{x} 230 Q{x + 150} 110 {x + 300} 230 L{x + 300} 470Z" fill="#F0C38E"/>'
                       f'<g transform="translate({x} 300)">{an._predios(rnd, 300, 170, 0, 60, 150, "#C98B6B", wmin=40, wmax=80)}</g>'
                       f'<path d="M{x} 470 L{x} 230 Q{x + 150} 110 {x + 300} 230 L{x + 300} 470Z" fill="none" stroke="#3A2818" stroke-width="16"/>'
                       f'<rect x="{x + 144}" y="150" width="12" height="320" fill="#3A2818"/>'
                       f'<path d="M{x - 40} 120 Q{x + 10} 300 {x - 20} 500 L{x + 40} 500 Q{x + 50} 300 {x + 30} 120Z" fill="#7E3526"/>'
                       f'<path d="M{x + 340} 120 Q{x + 290} 300 {x + 320} 500 L{x + 260} 500 Q{x + 250} 300 {x + 270} 120Z" fill="#7E3526"/>' for x in (-120, 900))
             + '<rect x="372" y="150" width="336" height="250" fill="#C9A24A"/>' + _quadro_arte(390, 168, 300, 214, rnd, '#8E6B22')
             + '<rect x="-300" y="1100" width="1680" height="300" fill="#6B4E31"/>'
             + ''.join(f'<rect x="{x}" y="1120" width="110" height="250" rx="4" fill="none" stroke="#5A3E28" stroke-width="6"/>' for x in range(-280, 1400, 140))
             + '<rect x="-300" y="1088" width="1680" height="14" fill="#5A3E28"/>' + est
             + '<rect x="-300" y="1382" width="1680" height="18" fill="#3A2818"/>')
        L = ''.join(_pendente(x, comp, '#C9A24A', luz=True) for x, comp in ((540 - 390, 300), (540 + 390, 300)))
        B = _piso(1400, '#7A5638', '#6A4A30') + '<ellipse cx="540" cy="1760" rx="520" ry="120" fill="#7E3526" opacity=".55"/>'
        C = _vaso(1130, 1990, 280, rnd)
        return [_cam3(A, 18), _cam3(L, 30), _cam3(B, 50, 'piso')], _cam3(C, 85)
    raise ValueError(tipo)


SALAS = ('escritorio', 'escritorio_noite', 'reuniao', 'sala_noite', 'rua', 'rua_tarde', 'rua_noite', 'celular', 'celular_dia',
         'recepcao', 'deposito', 'copa', 'sala_dono', 'quarto_noite', 'escritorio2')


def _topo_tijolo(rnd, variante='relogio'):
    """Topo do escritório 2: parede de tijolo aparente (sem a faixa de janelas) com um relógio grande, uma fileira de
    quadros ou uma prateleira com plantas e livros (variante; use an.cenario(c, 'escritorio2', topo='quadros'))."""
    out = ['<rect x="-300" y="80" width="1680" height="410" fill="#A8553C"/>']
    for r, y in enumerate(range(80, 490, 34)):
        off = 0 if r % 2 else 40
        out.append(''.join(f'<rect x="{x}" y="{y + 3}" width="74" height="28" rx="2" fill="{rnd.choice(("#B5603F", "#9E4E35", "#B86A48", "#A85A3E"))}"/>'
                           for x in range(-300 + off, 1400, 80)))
    out.append('<rect x="-300" y="488" width="1680" height="12" fill="#5A3E28"/>')
    if variante == 'quadros':
        out.append(''.join(_quadro_arte(x, 170, 210, 150, rnd, '#2A1E16') for x in (-140, 160, 460, 760, 1060)))
    elif variante == 'prateleira':
        out.append('<rect x="-300" y="380" width="1680" height="16" fill="#5A3E28"/>')
        x = -280
        while x < 1360:
            if rnd.random() < 0.4:
                out.append(_vaso(x + 40, 380, 150, rnd, 'folha2'))
                x += 110
            else:
                for _ in range(rnd.randint(4, 8)):
                    w_, h_ = rnd.uniform(16, 26), rnd.uniform(70, 110)
                    out.append(f'<rect x="{x:.0f}" y="{380 - h_:.0f}" width="{w_:.0f}" height="{h_:.0f}" fill="{rnd.choice(("#B5523B", "#2D4A63", "#C9A24A", "#5B7F6E", "#E9E4D8"))}"/>')
                    x += w_ + 2
                x += 50
    else:
        out.append(_relogio3(540, 300, 110, (10, 10)))
    return ''.join(out)


def _topo_ripas():
    """Topo da sala de reunião: ripas de madeira + spots (cada interior com um topo diferente, não a mesma faixa)."""
    return (''.join(f'<rect x="{x}" y="100" width="26" height="380" fill="{("#8A6A45", "#7A5A3C")[(x // 34) % 2]}"/>' for x in range(-300, 1400, 34))
            + '<rect x="-300" y="476" width="1680" height="14" fill="#5A3E28"/>'
            + ''.join(f'<circle cx="{x}" cy="88" r="12" fill="#FFF1C8"/><path d="M{x - 12} 92 L{x - 60} 300 L{x + 60} 300 L{x + 12} 92Z" fill="#FFF1C8" opacity=".10"/>' for x in range(-200, 1380, 200)))


# ---------------------------------------------------------------- CENAS de ação (camada em tela cheia)
def _posto(c, pid, x, y, esc, olha, pose, rnd, tela='linhas', xicara=True, monitor=True, **kw):
    """Mesa + cadeira + pessoa sentada (de lado) + monitor de frente. x = quadril da pessoa."""
    d = olha
    mx = x + d * (60 + 104) * esc        # começo da mesa (depois dos joelhos)
    w = 300 * esc
    mesa = f'<g transform="translate({x:.0f} {y}) scale({esc * d:.3f} {esc:.3f})">{_mesa_lado(60, 0, 300)}</g>'
    cad = f'<g transform="translate({x:.0f} {y}) scale({esc:.3f})">{_cadeira(0, 0, d)}</g>'
    pes = pos(corpo(pid, pose, rnd=rnd, **kw), x, y, esc, d)
    mon_x = x + d * (60 + 230) * esc
    mon = _monitor(mon_x, y - 204 * esc, 180 * esc, 122 * esc, tela, rnd, mid=f'{pid}-mon') if monitor else ''
    vid = f'{pid}-v'
    xi = _xic(x + d * (60 + 120) * esc, y - 204 * esc, vid) if xicara else ''
    if xicara:
        _vapor(c, vid, c.t0, _fim(c))
    return cad + mesa + mon + pes + xi, mx, mon_x


def escritorio(c, t, acoes=('digita', 'telefone', 'cafe'), quadro=None, t_quadro=None, pilha=None, cartoes=(), baloes=(),
               ia=None, papeis=None, placas=(), noite=False):
    """Escritório com GENTE fazendo coisas (corpo inteiro, ~3x maior que a v2). Use com an.cenario(c, 'escritorio')
    (ou 'escritorio_noite'). acoes (até 4, nesta ordem de lugar): sentadas — 'digita', 'headset', 'preocupado',
    'tel_sent', 'acena_sent' (mesa da esquerda, depois da direita); em pé no meio — 'telefone', 'aponta', 'celular';
    andando na frente — 'cafe', 'caixa', 'pasta', 'chega' (entra pela esquerda e para), 'papel'.
    quadro='grafico' = quadro na parede com barras subindo (sem número) em t_quadro.
    pilha=('Folha', t) = pilha de papel crescendo na mesa da esquerda com etiqueta.
    cartoes=[('Ferramenta', t), ...] = faturas empilhando em cima do monitor da direita.
    baloes=[(lugar, 'texto', t, icone)] = balão sobre a pessoa do lugar 0/1/2 (icone 'ok'/'ponto'/'ia'/'').
    ia=t = brilho de IA pulando de monitor em monitor (as telas acendem douradas). papeis=t = folhas voando.
    placas=('Marketing', 'Comercial') = placas penduradas sobre as duas mesas."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'x')
    rnd = random.Random(_seed(c.id) + 5)
    sentadas = [a for a in acoes if a in ('digita', 'headset', 'preocupado', 'tel_sent', 'acena_sent')]
    em_pe = [a for a in acoes if a in ('telefone', 'aponta', 'celular', 'coca')]
    andando = [a for a in acoes if a in ('cafe', 'caixa', 'pasta', 'chega', 'papel')]
    partes, quem, monitores = [], {}, []
    lugares = [(150, 1), (930, -1)]
    for k, a in enumerate(sentadas[:2]):
        x, d = lugares[k]
        pid = f'{w}-s{k}'
        tela = 'ia' if ia is not None else ('grafico' if a == 'headset' and k else 'linhas')
        g, mx, mon_x = _posto(c, pid, x, CHAO, 1.0, d, a, rnd, tela=tela, headset=a == 'headset',
                              blazer=rnd.choice((None, '#2D3A4F', '#4A3A2C')) if a == 'preocupado' else None)
        partes.append(g)
        quem[k] = (x + d * 30, CHAO - 520)
        monitores.append((mon_x, CHAO - 204 - 61, pid))
        vive(c, pid, t, t1, fala=a in ('headset', 'tel_sent'))
        if a in ('digita', 'headset'):
            digita(c, pid, t + 0.2, t1)
            an.som(t + 0.3, 'digitando', 0.08)
        elif a == 'preocupado':
            gesticula(c, pid, t, t1, 'j-bfa', 12, 0.2)
        elif a == 'acena_sent':
            gesticula(c, pid, t, t1, 'j-bfa', 22, 0.28)
    for k, a in enumerate(em_pe[:1]):
        pid = f'{w}-e{k}'
        x = 540 if len(sentadas) == 2 else (760 if sentadas else 420)
        partes.insert(0, pos(corpo(pid, a, item='celular' if a in ('telefone', 'celular') else None, rnd=rnd), x, 1560, 0.9,
                             -1 if x > 600 else 1))
        quem[2] = (x, 1560 - 470)
        vive(c, pid, t, t1, fala=a == 'telefone')
        respira(c, pid, t, t1)
        if a == 'telefone':
            gesticula(c, pid, t, t1, 'j-bt', 8, 0.6)
        elif a == 'aponta':
            gesticula(c, pid, t, t1, 'j-bf', 4, 0.5)
        elif a == 'coca':
            gesticula(c, pid, t, t1, 'j-bfa', 12, 0.2)
    for k, a in enumerate(andando[:3]):
        pid = f'{w}-a{k}'
        item = {'cafe': 'cafe', 'caixa': 'caixa', 'pasta': 'pasta', 'papel': 'papel', 'chega': rnd.choice(('cafe', 'pasta', None))}[a]
        pose = {'cafe': 'cafe', 'caixa': 'carrega', 'pasta': 'pasta', 'papel': 'cafe', 'chega': 'cafe' if item == 'cafe' else 'anda'}[a]
        if item == 'pasta':
            pose = 'pasta'
        D = max(1.0, t1 - t)
        if a == 'chega':
            alvo = (300, 540, 780)[k % 3]
            x0 = -160 - 150 * k
            esc = 1.12
            yb = 1860
            partes.append(pos(corpo(pid, pose, item=item, cracha=True, rnd=rnd), x0, yb, esc))
            dur = min(D - 0.2, 1.3 + 0.25 * k)
            anda(c, pid, t + 0.25 * k, (alvo - x0) / esc, dur, bracos=item is None)
            vive(c, pid, t, t1)
        else:
            x0 = -180 - 300 * k
            esc = 1.12
            yb = 1860
            partes.append(pos(corpo(pid, pose, item=item, rnd=rnd), x0, yb, esc))
            anda(c, pid, t + 0.1 + 0.4 * k, (1400 - x0) / esc * min(1.0, D / 4.2), D - 0.1, bracos=False)
            vive(c, pid, t, t1)
    extra = []
    if quadro:
        tq = _T(t_quadro) if t_quadro is not None else t + 0.6
        gq = f'{w}-q'
        bars = ''.join(f'<rect id="{gq}-b{k}" x="{430 + k * 60}" y="{1110 - 34 * (k + 1)}" width="40" height="{34 * (k + 1)}" '
                       f'fill="{"#B5523B" if k == 3 else "#2D4A63"}"/>' for k in range(4))
        extra.append(f'<g id="{gq}"><rect x="384" y="878" width="312" height="262" fill="#5A3E28"/><rect x="396" y="890" width="288" height="238" fill="#F3EEDF"/>'
                     f'{bars}<rect x="414" y="1110" width="252" height="4" fill="#2A2A2A"/>'
                     f'<path id="{gq}-l" d="M450 1060 L510 1030 L570 990 L630 950" stroke="#2A2A2A" stroke-width="4" fill="none" stroke-dasharray="1 1" pathLength="1"/></g>')
        for k in range(4):
            c.a(f"tl.fromTo('#{gq}-b{k}',{{scaleY:0}},{{scaleY:1,duration:0.45,ease:'power3.out',transformOrigin:'50% 100%'}},{q(tq + 0.3 * k)});")
            an.som(tq + 0.3 * k, 'marimba', 0.16)
        c.a(f"tl.fromTo('#{gq}-l',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:1.1,ease:'none'}},{q(tq + 0.2)});")
    if pilha:
        rot, tp = pilha
        tp = _T(tp)
        gp = f'{w}-p'
        # mesinha própria do lado direito (as mesas de trabalho já estão cheias: mãos, monitor, xícara)
        px = 760 if len(sentadas) < 2 else 540
        mesinha = (f'<rect x="{px - 130}" y="{CHAO - 150}" width="260" height="18" rx="5" fill="#8A6A45"/>'
                   f'<rect x="{px - 116}" y="{CHAO - 132}" width="14" height="132" fill="#6B4E31"/><rect x="{px + 102}" y="{CHAO - 132}" width="14" height="132" fill="#6B4E31"/>')
        fol = ''.join(f'<rect class="fl" x="{px - 70 + (k % 2) * 5}" y="{CHAO - 166 - 15 * k}" width="140" height="14" rx="2" fill="{"#FBF6EA" if k % 2 else "#E9E0CC"}"/>'
                      for k in range(14))
        extra.append(f'<g id="{gp}">{mesinha}{fol}{_etiqueta(px, CHAO - 410, rot, 40, eid=gp + "-e")}</g>')
        c.a(f"tl.fromTo('#{gp} .fl',{{opacity:0,y:-60}},{{opacity:1,y:0,duration:0.22,ease:'power2.out',stagger:0.08}},{q(tp)});")
        _pop_balao(c, f'{gp}-e', tp + 0.3, 'papel')
    for k, (rot, tc) in enumerate(cartoes):
        tc = _T(tc)
        cid = f'{w}-f{k}'
        mx = monitores[-1][0] if monitores else 760
        extra.append(f'<g transform="translate({mx - 130 + 10 * k:.0f} {CHAO - 480 - 70 * k}) rotate({-4 + 3 * k})"><g id="{cid}">'
                     f'<rect width="270" height="88" rx="6" fill="#FBF6EA"/><rect width="270" height="20" rx="6" fill="#B5523B"/>'
                     f'<text class="tc" x="135" y="68" text-anchor="middle" font-size="44" fill="#1E2A3A">{_html.escape(rot.upper())}</text></g></g>')
        c.a(f"tl.fromTo('#{cid}',{{opacity:0,y:-80,rotation:-10}},{{opacity:1,y:0,rotation:0,duration:0.35,ease:'back.out(1.8)'}},{q(tc)});")
        an.som(tc, 'pop2', 0.2)
    for k, (lugar, txt, tb, icone) in enumerate(baloes):
        bx, by = quem.get(lugar, (540, 1200))
        # 06/11 (t80): meia largura REAL do balão (o _balao desenha com ≥ 48 px + ícone + 56 de borda); com 40 px o balão
        # da mesa da esquerda saía a ~20–60 px da lateral. 170 = 100 px de margem + passeio da câmera.
        meia = (_txt_larg(txt.upper(), 48) + (50 if icone else 0) + 56) / 2
        bx = min(max(bx, 170 + meia), 910 - meia)
        bid = f'{w}-bl{k}'
        extra.append(_balao(bid, bx, by - 30 - 0 * k, txt, icone=icone))
        _pop_balao(c, bid, _T(tb))
    if ia is not None and monitores:
        ti = _T(ia)
        gi = f'{w}-ia'
        extra.append(f'<g id="{gi}"><circle r="40" fill="#F2B544" opacity=".25"/><path d="M0 -28 L8 -8 L28 0 L8 8 L0 28 L-8 8 L-28 0 L-8 -8Z" fill="#F2B544"/></g>')
        pts = [(mx, my - 90) for mx, my, _ in monitores] + [(540, 1180)]
        seq = (pts * 4)[:max(2, int((t1 - ti) / 0.7) + 1)]
        c.a(f"tl.set('#{gi}',{{x:{pts[-1][0]},y:{pts[-1][1]},opacity:0}},{q(c.t0)});")
        c.a(f"tl.to('#{gi}',{{opacity:1,duration:0.3}},{q(ti)});")
        for j, (px, py) in enumerate(seq):
            c.a(f"tl.to('#{gi}',{{x:{px:.0f},y:{py:.0f},duration:0.6,ease:'power2.inOut'}},{q(ti + 0.7 * j)});")
        c.a(f"tl.to('#{gi}',{{rotation:360,duration:1.6,repeat:{max(1, int((t1 - ti) / 1.6))},ease:'none'}},{q(ti)});")
        for mx, my, pid in monitores:
            c.a(f"tl.fromTo('#{pid}-mon .iag',{{opacity:0}},{{opacity:0.75,duration:0.35,yoyo:true,repeat:{max(1, int((t1 - ti) / 0.7))},ease:'sine.inOut'}},{q(ti + 0.4)});")
        an.som(ti, 'shimmer', 0.2)
    if papeis is not None:
        extra.append(_papeis_voando(c, f'{w}-pv', 330, CHAO - 240, _T(papeis)))
    for k, pl in enumerate(placas[:2]):
        x = (330, 750)[k]
        extra.append(f'<path d="M{x - 60} 960 L{x} 900 L{x + 60} 960" stroke="#3A3A3A" stroke-width="3" fill="none"/>' + _etiqueta(x, 1000, pl, 40, '#2D4A63', '#FBF6EA', rot=0))
    # tela dos monitores tremeluz (alguém trabalhando)
    c.a(f"tl.fromTo('#{w} .tl0, #{w} .tl2',{{scaleX:0.4}},{{scaleX:1,duration:0.5,ease:'steps(3)',yoyo:true,repeat:{max(1, int((t1 - t) / 0.5))},stagger:0.1}},{q(t)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(partes)}{"".join(extra)}</g>')


def _entra_amb(c, w, t):
    """A ação aparece num dissolve curto (corte suave dentro do mesmo lugar); no 1º quadro do vídeo já está lá."""
    if c.t0 < 0.05:
        return
    c.a(f"tl.fromTo('#{w}',{{opacity:0.0}},{{opacity:1,duration:0.25,ease:'power1.out'}},{q(max(c.t0, t - 0.25))});")


def crescimento_predio(c, t, rotulo='', andares=3, t_andares=None):
    """Rua com o prédio da empresa crescendo andar por andar (gente na calçada, carro passando). Cenário 'rua'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cp')
    rnd = random.Random(_seed(c.id))
    x0, x1, ch = 330, 750, 1560
    base = (f'<rect x="{x0}" y="{ch - 300}" width="{x1 - x0}" height="300" fill="#2D4A63"/>'
            f'<rect x="{x1 - 34}" y="{ch - 300}" width="34" height="300" fill="#22394F"/>'
            f'<rect x="{x0 + 150}" y="{ch - 190}" width="120" height="190" fill="#BFDCE6"/><rect x="{x0 + 208}" y="{ch - 190}" width="4" height="190" fill="#22394F"/>'
            + ''.join(f'<rect x="{x0 + 30 + 300 * j}" y="{ch - 220}" width="80" height="100" fill="#BFDCE6"/>' for j in range(2)))
    if rotulo:   # 08/11: a placa vai NA fachada do térreo (antes ficava solta entre o térreo e os andares novos, que flutuavam)
        base += _etiqueta(540, ch - 262, rotulo, 40, '#B5523B', '#FBF6EA', rot=0, eid=f'{w}-r')
    andar = ''
    ta = [(_T(x) if x is not None else None) for x in (t_andares or [])] or [t + 0.25 + 0.35 * k for k in range(andares)]
    for k in range(andares):
        ha = min(200, int(250 / andares))     # 06/11: o prédio para em y ~900 (o letreiro fica em cima, limpo)
        y = ch - 300 - ha * (k + 1)   # 08/11: andar encostado no de baixo (sem vão)
        andar += (f'<g id="{w}-a{k}"><rect x="{x0 + 10}" y="{y}" width="{x1 - x0 - 20}" height="{ha}" fill="{("#3B5A75", "#34536D")[k % 2]}"/>'
                  f'<rect x="{x1 - 44}" y="{y}" width="34" height="{ha}" fill="#2A445C"/>'
                  + ''.join(f'<rect class="jp" x="{x0 + 40 + 92 * j}" y="{y + ha * 0.22:.0f}" width="56" height="{ha * 0.55:.0f}" fill="{"#F2E6C8" if (j + k) % 3 else "#BFDCE6"}"/>' for j in range(4))
                  + f'<rect x="{x0}" y="{y + ha - 10}" width="{x1 - x0}" height="12" fill="#22394F"/></g>')
        c.a(f"tl.fromTo('#{w}-a{k}',{{scaleY:0,opacity:0}},{{scaleY:1,opacity:1,duration:0.32,ease:'back.out(1.6)',transformOrigin:'50% 100%'}},{q(ta[k])});")
        an.som(ta[k], 'pop', 0.16)
    gt = ch - 600
    gru = (f'<g id="{w}-g"><rect x="{x1 + 40}" y="{gt}" width="18" height="600" fill="#C9A24A"/>'
           + ''.join(f'<path d="M{x1 + 40} {gt + 30 * j} l18 30" stroke="#9C7A2E" stroke-width="3"/>' for j in range(20))
           + f'<rect x="{x0 - 60}" y="{gt}" width="{x1 - x0 + 170}" height="16" fill="#C9A24A"/>'
           f'<path d="M{x0 + 30} {gt + 16} L{x0 + 30} {gt + 90}" stroke="#2A2A2A" stroke-width="3"/><rect x="{x0 + 4}" y="{gt + 90}" width="52" height="30" fill="#B5523B"/></g>')
    c.a(f"tl.fromTo('#{w}-g',{{rotation:-2}},{{rotation:2,duration:1.2,yoyo:true,repeat:2,ease:'sine.inOut',svgOrigin:'{x1 + 49} {ch}'}},{q(c.t0)});")
    pes = ''
    for k in range(3):
        pid = f'{w}-p{k}'
        x = (-120, 980, -380)[k]
        d = -1 if x > 540 else 1
        pes += pos(corpo(pid, ('cafe', 'pasta', 'celular')[k], item=('cafe', 'pasta', 'celular')[k], rnd=rnd), x, 1690, 0.92, d)
        anda(c, pid, t + 0.1 * k, 380, max(1.0, t1 - t), bracos=False)
        vive(c, pid, t, t1)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{gru}{base}{andar}{pes}</g>')


def fachada(c, t, letreiro='LOJA', fila=5, notas=True, t_fila=None):
    """Fachada de loja na calçada: vendedor no balcão com a caixa registradora, FILA DE CLIENTES chegando e crescendo,
    notas de dinheiro saindo da caixa (faturamento subindo, sem número). Cenário 'rua' ou 'rua_tarde'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'fc')
    rnd = random.Random(_seed(c.id) + 2)
    ch = 1560
    x0, x1 = 150, 930
    listras = ''.join(f'<path d="M{x0 + j * 60} {ch - 430} L{x0 + 60 + j * 60} {ch - 430} L{x0 + 60 + j * 60} {ch - 360} '
                      f'Q{x0 + 30 + j * 60} {ch - 340} {x0 + j * 60} {ch - 360}Z" fill="{"#B5523B" if j % 2 == 0 else "#FBF6EA"}"/>' for j in range(13))
    vend = f'{w}-v'
    loja = (f'<rect x="{x0}" y="{ch - 620}" width="{x1 - x0}" height="620" fill="#E2D3B0"/><rect x="{x1 - 30}" y="{ch - 620}" width="30" height="620" fill="#C9B690"/>'
            f'<rect x="{x0 + 70}" y="{ch - 600}" width="{x1 - x0 - 140}" height="120" rx="8" fill="#2D4A63"/>'
            f'<text class="tc" x="{(x0 + x1) / 2:.0f}" y="{ch - 515}" text-anchor="middle" font-size="84" fill="#FBF6EA">{_html.escape(letreiro.upper())}</text>'
            + listras +
            f'<rect x="{x0 + 40}" y="{ch - 330}" width="460" height="300" fill="#F6E7C4"/>'
            + pos(corpo(vend, 'digita', roupa='#5B7F6E', estilo='coque', rnd=rnd), x0 + 200, ch - 40, 0.62)
            + f'<rect x="{x0 + 40}" y="{ch - 150}" width="460" height="120" fill="#8A6A45"/><rect x="{x0 + 30}" y="{ch - 160}" width="480" height="16" fill="#A88B60"/>'
            f'<g id="{w}-cx" transform="translate({x0 + 330} {ch - 214})"><rect x="0" y="0" width="120" height="56" rx="6" fill="#3B4E5E"/><rect x="14" y="-34" width="88" height="38" rx="4" fill="#2D3A4F"/>'
            f'<rect x="22" y="-27" width="72" height="22" fill="#8FE0B0" class="visor"/><rect x="10" y="56" width="100" height="8" fill="#2D3A4F"/></g>'
            f'<rect x="{x0 + 40}" y="{ch - 330}" width="460" height="300" fill="#FFFFFF" opacity=".16"/>'
            f'<rect x="{x0 + 40}" y="{ch - 330}" width="460" height="300" fill="none" stroke="#6B4E31" stroke-width="12"/>'
            f'<rect x="{x0 + 560}" y="{ch - 330}" width="170" height="330" fill="#5A3E28"/><rect x="{x0 + 576}" y="{ch - 314}" width="138" height="160" fill="#BFDCE6"/>'
            f'<g transform="translate({x0 + 645} {ch - 200}) rotate(-4)"><rect x="-74" y="-28" width="148" height="56" rx="5" fill="#FBF6EA"/>'
            f'<text class="tc" x="0" y="16" text-anchor="middle" font-size="42" fill="#3F7F55">ABERTO</text></g>')
    vive(c, vend, t, t1, fala=True)
    digita(c, vend, t + 0.4, t1)
    c.a(f"tl.fromTo('#{w} .visor',{{opacity:1}},{{opacity:0.35,duration:0.3,ease:'steps(1)',yoyo:true,repeat:{max(1, int((t1 - t) / 0.3))}}},{q(t + 0.5)});")
    tf = _T(t_fila) if t_fila is not None else t + 0.2
    clientes = ''
    alvos = [640, 520, 400, 280, 160, 40][:fila]
    for k, alvo in enumerate(alvos):
        pid = f'{w}-c{k}'
        x0c = -150 - 130 * k
        item = rnd.choice(('celular', 'pasta', None, 'papel'))
        clientes += pos(corpo(pid, 'anda' if item is None else ('pasta' if item == 'pasta' else 'cafe' if item == 'papel' else 'celular'),
                              item=item, rnd=rnd), x0c, 1680, 0.95)
        dur = min(max(0.8, t1 - tf - 0.3 * k - 0.2), 1.1 + 0.18 * k)
        anda(c, pid, tf + 0.3 * k, (alvo - x0c) / 0.95, dur, bracos=item is None)
        vive(c, pid, tf, t1)
    notas_g = ''
    if notas:
        gn = f'{w}-n'
        notas_g = (f'<g id="{gn}">' + ''.join(
            f'<g transform="translate({x0 + 390} {ch - 230})"><g class="nt"><rect x="-38" y="-20" width="76" height="40" rx="4" fill="#7FB08A"/>'
            f'<rect x="-30" y="-13" width="60" height="26" rx="3" fill="none" stroke="#3F7F55" stroke-width="3"/><circle r="8" fill="#3F7F55"/></g></g>'
            for _ in range(7)) + '</g>')
        D = max(0.8, t1 - t - 0.4)
        rep = max(0, int(D / 1.4))
        # 08/11 (folha do t83): as notas subiam até 620 px e passavam por cima do letreiro; agora param abaixo dele
        c.a(f"tl.fromTo('#{gn} .nt',{{x:0,y:0,opacity:0,rotation:0,scale:0.6}},{{x:(i)=>[-240,180,-60,300,-180,90,240][i%7],y:(i)=>[-400,-300,-360,-330,-280,-390,-340][i%7],opacity:1,rotation:(i)=>[-150,120,-40,160,-110,60,-80][i%7],scale:1.1,"
            f"duration:1.4,ease:'power2.out',repeat:{rep},stagger:{{each:0.2,repeat:{rep}}}}},{q(t + 0.4)});")
        an.som(t + 0.45, 'glock', 0.16)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{loja}{notas_g}{clientes}</g>')


def pote(c, t, rotulo='Lucro', entrada='Vendas', saidas=('Folha', 'Ferramentas'), dono=True):
    """Dado virando cena: pote de vidro do LUCRO enchendo por cima (moedas das vendas caindo do cano) e VAZANDO por
    baixo pra dois baldes (saídas); o nível não sobe. Dono do lado coçando a cabeça. Cenário 'escritorio'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'pt')
    rnd = random.Random(_seed(c.id) + 3)
    yb = 1700
    jx0, jx1, jy0 = 420, 700, 1150
    nivel = 1430
    pote_svg = (f'<ellipse cx="560" cy="{yb + 4}" rx="190" ry="14" fill="#000" opacity=".15"/><g id="{w}-nvb">'
                f'<path d="M{jx0} {jy0 + 40} Q{jx0} {jy0} {jx0 + 40} {jy0} L{jx1 - 40} {jy0} Q{jx1} {jy0} {jx1} {jy0 + 40} L{jx1} {yb - 40} '
                f'Q{jx1} {yb} {jx1 - 40} {yb} L{jx0 + 40} {yb} Q{jx0} {yb} {jx0} {yb - 40}Z" fill="#DCEFF2" opacity=".55"/>'
                f'<g id="{w}-nv"><rect x="{jx0 + 14}" y="{nivel}" width="{jx1 - jx0 - 28}" height="{yb - nivel - 14}" rx="20" fill="#E0B048"/>'
                + ''.join(f'<circle cx="{rnd.uniform(jx0 + 40, jx1 - 40):.0f}" cy="{rnd.uniform(nivel + 20, yb - 30):.0f}" r="15" fill="#F2C664" stroke="#C9A24A" stroke-width="3"/>' for _ in range(16))
                + f'<rect x="{jx0 + 14}" y="{nivel - 6}" width="{jx1 - jx0 - 28}" height="14" rx="7" fill="#F2C664"/></g></g>'
                f'<path d="M{jx0} {jy0 + 40} Q{jx0} {jy0} {jx0 + 40} {jy0} L{jx1 - 40} {jy0} Q{jx1} {jy0} {jx1} {jy0 + 40} L{jx1} {yb - 40} '
                f'Q{jx1} {yb} {jx1 - 40} {yb} L{jx0 + 40} {yb} Q{jx0} {yb} {jx0} {yb - 40}Z" fill="none" stroke="#9BBFC8" stroke-width="8"/>'
                f'<rect x="{jx0 + 30}" y="{jy0 + 40}" width="22" height="{yb - jy0 - 120}" rx="11" fill="#FFFFFF" opacity=".45"/>'
                + ''.join(f'<rect x="{jx1 - 50}" y="{1250 + 60 * k}" width="34" height="5" fill="#7FA4B1"/>' for k in range(6))
                + f'<path d="M{jx1 + 10} {nivel} l26 -16 v32z" fill="#B5523B" id="{w}-mk"/>'
                + _etiqueta(560, jy0 + 120, rotulo, 46, '#FBF6EA', '#1E2A3A', rot=-2))
    cano = (f'<rect x="530" y="820" width="60" height="230" fill="#7A8A94"/><rect x="520" y="1040" width="80" height="26" rx="6" fill="#5F6E78"/>'
            f'<rect x="530" y="820" width="14" height="230" fill="#93A3AC"/>' + _etiqueta(700, 930, entrada, 36, '#2D4A63', '#FBF6EA', rot=3))
    jorro = _moedas_caindo(c, f'{w}-in', 560, 1070, 560, nivel - 10, t + 0.2, n=6, per=0.75)
    vaz = ''
    for k, s in enumerate(saidas[:2]):
        bx = (300, 785)[k]
        sx = (jx0 + 8, jx1 - 8)[k]
        vaz += (f'<rect x="{sx - (24 if k == 0 else 0)}" y="{yb - 70}" width="24" height="18" fill="#7A8A94"/>'
                + _moedas_caindo(c, f'{w}-o{k}', sx + (-30 if k == 0 else 30), yb - 60, bx, yb - 40, t + 0.5 + 0.2 * k, n=4, per=0.8, arco=True)
                + f'<path d="M{bx - 66} {yb - 90} L{bx + 66} {yb - 90} L{bx + 52} {yb} L{bx - 52} {yb}Z" fill="#8A6A45"/>'
                  f'<rect x="{bx - 72}" y="{yb - 100}" width="144" height="16" rx="6" fill="#6B4E31"/>'
                + _etiqueta(bx, yb + 60, s, 32, '#FBF6EA', '#B5523B', rot=(-3, 3)[k]))
    c.a(f"tl.fromTo('#{w}-nv',{{y:0}},{{y:-10,duration:0.5,yoyo:true,repeat:{max(1, int((t1 - t) / 0.5))},ease:'sine.inOut'}},{q(t)});")
    c.a(f"tl.fromTo('#{w}-mk',{{x:0}},{{x:10,duration:0.4,yoyo:true,repeat:{max(1, int((t1 - t) / 0.4))},ease:'sine.inOut'}},{q(t)});")
    an.som(t + 0.25, 'glock', 0.18)
    pes = ''
    if dono:   # rodada 6: entra andando coçando a cabeça; quando o nível BAIXA, tira a carteira vazia e balança a cabeça
        pid = f'{w}-d'
        (a0, b0), (a1, b1) = _angs('coca', 'f'), _angs('mostra', 'f')
        pes = pos(corpo(pid, 'coca', blazer='#2D3A4F', gravata='#B5523B', roupa='#E9E4D8', item='carteira',
                        item_rot=-((a1 - a0) + (b1 - b0)), rnd=rnd), -40, 1780, 1.0)
        anda(c, pid, t, 190, min(1.2, max(0.6, t1 - t - 0.5)), bracos=False)
        vive(c, pid, t, t1, cabeca=False)
        tm = t + max(1.4, min(2.2, (t1 - t) * 0.45))   # momento da carteira
        gesticula(c, pid, t + 0.6, tm, 'j-bfa', 14, 0.22)
        muda_pose(c, pid, 'coca', 'mostra', tm, 0.4)
        c.a(f"tl.to('#{pid} .it-cart',{{opacity:1,duration:0.15}},{q(tm + 0.2)});")
        c.a(f"tl.fromTo('#{pid} .j-cab',{{rotation:-8}},{{rotation:8,duration:0.3,yoyo:true,repeat:{max(1, int((t1 - tm - 0.5) / 0.3))},ease:'sine.inOut',svgOrigin:'0 0'}},{q(tm + 0.5)});")
        an.som(tm + 0.2, 'papel', 0.2)
    c.a(f"tl.fromTo('#{w}-nvb',{{y:0}},{{y:70,duration:{max(0.8, (t1 - t) * 0.5):.2f},ease:'power1.inOut'}},{q(t + 1.0)});")   # o lucro escoa
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{cano}{jorro}{pote_svg}{pes}{vaz}</g>')


def sala_noite(c, t, notif='Lead novo', t_notif=None, hora=(11, 0), gato=False, baloes=(), cachorro=True, tv=True, mao=True):
    """Sala de casa à noite: o dono no sofá com o CELULAR NA MÃO (tela acesa), relógio na hora falada, cachorro no
    tapete, luz da TV piscando; o celular vibra e apita (notif em t_notif) e a conversa sai dele em balões:
    baloes=[('Oi! Vi o anúncio', t, 'ponto'), ('IA: já te ajudo', t, 'ia'), ('Reunião marcada', t, 'ok')].
    Cenário 'sala_noite'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'sn')
    rnd = random.Random(_seed(c.id) + 4)
    yb = 1740
    dx = 330   # rodada 6: tudo pra direita — o canto de baixo à esquerda é do rótulo com relógio
    sofa = (f'<ellipse cx="{400 + dx}" cy="{yb + 4}" rx="300" ry="16" fill="#000" opacity=".2"/>'
            f'<rect x="{120 + dx}" y="{yb - 330}" width="90" height="300" rx="30" fill="#4A6A7A"/>'
            f'<rect x="{130 + dx}" y="{yb - 150}" width="520" height="110" rx="26" fill="#557A8B"/>'
            f'<rect x="{600 + dx}" y="{yb - 220}" width="80" height="180" rx="30" fill="#4A6A7A"/>'
            f'<rect x="{150 + dx}" y="{yb - 40}" width="20" height="40" fill="#2A2A2A"/><rect x="{630 + dx}" y="{yb - 40}" width="20" height="40" fill="#2A2A2A"/>')
    pid = f'{w}-d'
    pessoa_ = pos(corpo(pid, 'cel_sent' if mao else 'xicara_sent', roupa='#8E6A9A', calca='#3B4A5E',
                        item='celular' if mao else 'cafe', rnd=rnd), 290 + dx, yb - 26, 1.0)
    tn = _T(t_notif) if t_notif is not None else t + 0.6
    extra = ''
    if tv:   # TV de lado na direita: só a luz azulada piscando no chão e na parede
        extra += (f'<rect x="1010" y="1330" width="22" height="200" fill="#11161F"/><rect x="990" y="1530" width="70" height="210" fill="#5A3E28"/>'
                  f'<path id="{w}-tvl" d="M1010 1330 L1010 1530 L560 {yb} L560 1150Z" fill="#8FC1D4" opacity=".10"/>')
        c.a(f"tl.fromTo('#{w}-tvl',{{opacity:0.05}},{{opacity:0.16,duration:0.33,ease:'steps(2)',yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.33))}}},{q(c.t0)});")
    if cachorro:
        extra += (f'<g transform="translate(720 {yb + 70}) scale(0.9)"><ellipse cx="0" cy="-34" rx="92" ry="38" fill="#B07A4A"/>'
                  f'<g id="{w}-cab"><circle cx="86" cy="-60" r="34" fill="#B07A4A"/><ellipse cx="118" cy="-52" rx="20" ry="14" fill="#C9935F"/>'
                  f'<circle cx="134" cy="-56" r="6" fill="#2A2A2A"/><circle cx="92" cy="-70" r="4.5" fill="#1E1A16"/>'
                  f'<path d="M66 -84 Q52 -60 70 -40 Q82 -62 80 -84Z" fill="#8A5A30"/></g>'
                  f'<g id="{w}-rabo"><path d="M-88 -40 Q-130 -60 -126 -96" stroke="#B07A4A" stroke-width="14" fill="none" stroke-linecap="round"/></g>'
                  f'<rect x="-70" y="-14" width="44" height="14" rx="7" fill="#9A6A3E"/><rect x="40" y="-14" width="44" height="14" rx="7" fill="#9A6A3E"/></g>')
        c.a(f"tl.fromTo('#{w}-rabo',{{rotation:-14}},{{rotation:16,duration:0.28,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.28))},ease:'sine.inOut',svgOrigin:'-88 -40'}},{q(c.t0)});")
        c.a(f"tl.fromTo('#{w}-cab',{{rotation:10,y:14}},{{rotation:0,y:0,duration:0.3,ease:'back.out(2)',svgOrigin:'60 -40'}},{q(tn + 0.1)});")
    if gato:
        extra += (f'<g transform="translate(615 {yb - 222})"><ellipse cx="0" cy="0" rx="50" ry="26" fill="#2A2A2A"/><circle cx="36" cy="-16" r="20" fill="#2A2A2A"/></g>')
    # celular vibrando na mão: ondas na mão e a tela pulsando
    ox, oy = 372 + dx, yb - 26 - 350 + 104 - 30
    extra += (f'<g transform="translate({ox} {oy})"><g id="{w}-ond" fill="none" stroke="#F2C46B" stroke-width="5" stroke-linecap="round">'
              f'<path d="M-40 -6 Q-50 -36 -30 -60"/><path d="M40 -6 Q50 -36 30 -60"/><path d="M-66 0 Q-82 -44 -52 -84"/><path d="M66 0 Q82 -44 52 -84"/></g></g>')
    c.a(f"tl.set('#{w}-ond',{{opacity:0}},{q(c.t0)});")
    c.a(f"tl.fromTo('#{w}-ond',{{opacity:0,scale:0.7}},{{opacity:1,scale:1.15,duration:0.45,repeat:{max(1, int((t1 - tn) / 0.45))},ease:'power1.out',svgOrigin:'0 -30'}},{q(tn)});")
    c.a(f"tl.fromTo('#{pid} .telac',{{fill:'#8FC1D4'}},{{fill:'#FFF6D8',duration:0.2,yoyo:true,repeat:{max(1, int((t1 - tn) / 0.2))}}},{q(tn)});")
    an.som(tn, 'tique2', 0.3)
    an.som(tn + 0.4, 'tique2', 0.3)
    vive(c, pid, t, t1, cabeca=False)
    respira(c, pid, t, t1)
    gesticula(c, pid, t + 0.3, t1, 'j-bfa', 5, 0.35)
    rel = _relogio3(200, 1300, 56, hora)   # parede da esquerda, abaixo dos balões e acima do canto do rótulo
    bal = ''
    lista = list(baloes) if baloes else ([(notif, tn + 0.15, 'ponto')] if notif else [])
    for k, b in enumerate(lista):
        txt, tb, ic_ = b[0], _T(b[1]), (b[2] if len(b) > 2 else '')
        bid = f'{w}-b{k}'
        lw = _txt_larg(txt.upper(), 48) + 110   # o balão sai com 48 px (mínimo das peças)
        bx = min(max(640 + 40 * (k % 2), 330 + lw / 2), 910 - lw / 2)   # sempre à direita do relógio de parede (x ~250)
        bal += _balao(bid, bx, 1200 - 118 * k, txt, cor='#F2B544' if ic_ == 'ia' else '#FBF4E4', tam=38, icone=ic_)   # acima do rótulo de canto
        _pop_balao(c, bid, tb, 'pop2')
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{rel}{extra}{sofa}{pessoa_}{bal}</g>')


def casa_fora(c, t, baloes=(), noite=True):
    """A casa por fora, de noite: a janela de cima acesa com o dono no celular (tela brilhando), carro passando com
    farol, poste; os balões (conversa, agenda) saem da janela. Cenário 'rua_noite'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cf')
    rnd = random.Random(_seed(c.id) + 21)
    ch = 1560
    casa = (f'<rect x="300" y="{ch - 640}" width="480" height="640" fill="#5A3E36"/><rect x="750" y="{ch - 640}" width="30" height="640" fill="#4A322C"/>'
            f'<path d="M270 {ch - 630} L540 {ch - 800} L810 {ch - 630}Z" fill="#3A2A2E"/>'
            f'<rect x="440" y="{ch - 560}" width="200" height="170" fill="#F2C46B" id="{w}-jan"/>'
            f'<g transform="translate(470 {ch - 380}) scale(0.62)">{busto(f"{w}-b", estilo="lateral", terno=False, roupa="#8E6A9A")}</g>'
            f'<rect x="560" y="{ch - 470}" width="26" height="44" rx="5" fill="#1E2A3A"/><rect x="564" y="{ch - 466}" width="18" height="34" fill="#FFF6D8" id="{w}-tela"/>'
            f'<rect x="440" y="{ch - 560}" width="200" height="170" fill="none" stroke="#2A1A16" stroke-width="12"/><rect x="534" y="{ch - 560}" width="12" height="170" fill="#2A1A16"/>'
            f'<rect x="340" y="{ch - 300}" width="150" height="130" fill="#2A3550"/><rect x="590" y="{ch - 300}" width="150" height="130" fill="#F2C46B" opacity=".55"/>'
            f'<rect x="500" y="{ch - 160}" width="80" height="160" fill="#2A1A16"/><circle cx="566" cy="{ch - 80}" r="5" fill="#C9A24A"/>')
    _vivo(c, f'{w}-b', t, t1)
    c.a(f"tl.fromTo('#{w}-tela',{{fill:'#FFF6D8'}},{{fill:'#8FC1D4',duration:0.25,ease:'steps(1)',yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.25))}}},{q(c.t0)});")
    bal = ''
    for k, b in enumerate(baloes):
        txt, tb, ic_ = b[0], _T(b[1]), (b[2] if len(b) > 2 else '')
        bid = f'{w}-bl{k}'
        lw = _txt_larg(txt.upper(), 38) + 110
        bx = min(max(700, 170 + lw / 2), 910 - lw / 2)
        bal += _balao(bid, bx, ch - 560 + 112 * k, txt, cor='#F2B544' if ic_ == 'ia' else '#FBF4E4', tam=38, icone=ic_)   # descem da janela (nunca no letreiro)
        _pop_balao(c, bid, tb, 'pop2')
    car = (f'<g id="{w}-car"><g transform="translate(-260 1800) scale(2.2)">{an._carro(0, 0, "#B5523B", "#8E3F2C", 1).replace("data-v", "data-x-v")}</g>'
           f'<path d="M-150 1752 L120 1700 L120 1810 Z" fill="#F7D98A" opacity=".22"/></g>')
    c.a(f"tl.fromTo('#{w}-car',{{x:0}},{{x:1600,duration:{max(1.4, t1 - c.t0 + 0.3):.2f},ease:'none'}},{q(c.t0)});")
    an.som(c.t0 + 0.3, 'whoosh_lento', 0.12)
    gat = (f'<g transform="translate(860 {ch - 6})"><ellipse cx="0" cy="-20" rx="34" ry="18" fill="#1A1A1A"/><circle cx="28" cy="-34" r="14" fill="#1A1A1A"/>'
           f'<path d="M20 -46 L24 -58 L32 -46Z M34 -46 L40 -56 L42 -44Z" fill="#1A1A1A"/><g id="{w}-rabo"><path d="M-32 -16 Q-60 -20 -58 -50" stroke="#1A1A1A" stroke-width="7" fill="none" stroke-linecap="round"/></g></g>')
    c.a(f"tl.fromTo('#{w}-rabo',{{rotation:-12}},{{rotation:14,duration:0.8,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.8))},ease:'sine.inOut',svgOrigin:'-32 -16'}},{q(c.t0)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{casa}{gat}{bal}{car}</g>')


def ponto_onibus(c, t, tempos=(), textos=None, lugar='onibus'):
    """Ponto de ônibus na calçada: pessoa sentada no banco respondendo no celular (polegar mexendo); a cada resposta um
    cartão com ✓ sobe ao lado; gente passando e carro na rua. Cenário 'rua'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'po')
    rnd = random.Random(_seed(c.id) + 22)
    ch = 1560
    if lugar == 'cafe':   # variante: mesinha de café na calçada com guarda-sol
        abrigo = (f'<path d="M300 {ch - 380} Q580 {ch - 470} 860 {ch - 380}Z" fill="#B5523B"/>'
                  + ''.join(f'<path d="M{300 + 56 * k} {ch - 380} L{328 + 56 * k} {ch - 380} L{580} {ch - 452}Z" fill="#FBF6EA" opacity=".9"/>' for k in range(0, 10, 2))
                  + f'<rect x="574" y="{ch - 380}" width="12" height="420" fill="#5A3E28"/>'
                  f'<rect x="640" y="{ch - 10}" width="200" height="16" rx="6" fill="#8A6A45"/><rect x="732" y="{ch + 6}" width="14" height="110" fill="#5A3E28"/>'
                  f'<g transform="translate(700 {ch - 14}) scale(0.8)">{_xicara(0, -6, f"{_T(t):.0f}v")}</g>'
                  f'<rect x="420" y="{ch + 2}" width="200" height="16" rx="6" fill="#8A6A45"/><rect x="440" y="{ch + 18}" width="12" height="100" fill="#5A3E28"/>'
                  f'<rect x="590" y="{ch + 18}" width="12" height="100" fill="#5A3E28"/><rect x="420" y="{ch - 160}" width="16" height="170" fill="#5A3E28"/>')
    else:
      abrigo = (f'<rect x="300" y="{ch - 400}" width="560" height="22" rx="6" fill="#2D4A63"/><rect x="310" y="{ch - 378}" width="12" height="440" fill="#5A646C"/>'
              f'<rect x="838" y="{ch - 378}" width="12" height="440" fill="#5A646C"/><rect x="322" y="{ch - 378}" width="516" height="300" fill="#BFDCE6" opacity=".45"/>'
              f'<rect x="360" y="{ch - 360}" width="150" height="230" fill="#E9DFC6"/><rect x="376" y="{ch - 344}" width="118" height="120" fill="#C98B6B"/>'
              f'<rect x="376" y="{ch - 210}" width="90" height="12" fill="#8A7E6A"/>'
              f'<rect x="420" y="{ch + 2}" width="380" height="18" rx="6" fill="#8A6A45"/><rect x="440" y="{ch + 20}" width="14" height="80" fill="#5A646C"/>'
              f'<rect x="766" y="{ch + 20}" width="14" height="80" fill="#5A646C"/>')
    pid = f'{w}-p'
    pessoa_ = pos(corpo(pid, 'cel_sent', item='celular', roupa='#C9A24A', rnd=rnd), 560, ch + 118, 1.0)
    vive(c, pid, t, t1, cabeca=False)
    gesticula(c, pid, t, t1, 'j-bfa', 6, 0.3)
    respira(c, pid, t, t1)
    textos = list(textos or ['Pergunta', 'Pergunta', 'Pergunta'])
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.6 + 0.8 * k for k in range(len(textos))]
    bal = ''
    for k, (txt, tk) in enumerate(zip(textos, ts_)):
        bid = f'{w}-b{k}'
        bal += _balao(bid, 720, ch - 360 - 105 * k, txt, cauda='', icone='ok', tam=36)
        _pop_balao(c, bid, tk, 'tique2')
    pas = f'{w}-pa'
    pes2 = pos(corpo(pas, 'pasta', item='pasta', rnd=rnd), 1250, 1700, 0.95, -1)
    anda(c, pas, c.t0, 1500 / 0.95 * min(1, (t1 - c.t0) / 4), max(1.0, t1 - c.t0), bracos=False)
    vive(c, pas, c.t0, t1)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{abrigo}{pessoa_}{bal}{pes2}</g>')


def celular_close(c, t, tela='chat', itens=(), tempos=None, titulo='Agente de IA', noite=True):
    """Close do celular na mão (tela grande): tela='chat' (itens = [('lead'|'ia', 'texto')]: mensagens chegando, IA
    digitando antes de responder), 'agenda' (itens = ['Reunião marcada', 'Comercial avisado']: dia marcado na agenda +
    avisos), 'form' (itens = n perguntas: o polegar toca uma opção de cada). Cenário 'celular' (noite) ou 'celular_dia'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cc')
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.5 + 0.8 * k for k in range(len(itens))]
    X0, X1, Y0 = 300, 780, 900
    sx0, sx1, sy0 = X0 + 22, X1 - 22, Y0 + 90
    mao = ('<path d="M250 1960 L250 1520 Q250 1460 300 1450 L330 1450 L330 1960Z" fill="#E3AE84"/>'
           '<path d="M800 1960 L800 1380 Q860 1400 870 1500 L880 1960Z" fill="#D49A70"/>')
    corpo_cel = (f'<rect x="{X0 + 10}" y="{Y0 + 14}" width="{X1 - X0}" height="1060" rx="70" fill="#000" opacity=".25"/>'
                 f'<rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="1060" rx="70" fill="#1E2A3A"/>'
                 f'<rect x="{sx0}" y="{Y0 + 22}" width="{sx1 - sx0}" height="1016" rx="52" fill="{"#F6F1E6" if tela != "form" else "#FBF6EA"}"/>'
                 f'<rect x="{(X0 + X1) / 2 - 60:.0f}" y="{Y0 + 30}" width="120" height="26" rx="13" fill="#1E2A3A"/>'
                 f'<rect x="{sx0}" y="{Y0 + 70}" width="{sx1 - sx0}" height="96" fill="#2D4A63"/>'
                 f'<circle cx="{sx0 + 60}" cy="{Y0 + 118}" r="30" fill="#F2B544"/>'
                 f'<path transform="translate({sx0 + 60} {Y0 + 118})" d="M0 -18 L5 -5 L18 0 L5 5 L0 18 L-5 5 L-18 0 L-5 -5Z" fill="#2D4A63"/>'
                 f'<text class="tc" x="{sx0 + 110}" y="{Y0 + 130}" font-size="36" fill="#FBF6EA">{_html.escape(titulo.upper())}</text>')
    cont = ''
    y = Y0 + 210
    if tela == 'chat':
        for k, ((lado, txt), tk) in enumerate(zip(itens, ts_)):
            mid = f'{w}-m{k}'
            tx = txt
            lw = min(380, _txt_larg(tx, 34, 'serif') + 50)
            if lado == 'ia':
                bx = sx1 - 24 - lw
                cor, tinta = '#F2B544', '#1E2A3A'
                dots = (f'<g id="{mid}-d" transform="translate({sx1 - 120} {y + 30})"><rect x="-20" y="-28" width="110" height="56" rx="28" fill="#E9E0CC"/>'
                        + ''.join(f'<circle class="dd" cx="{8 + 26 * j}" cy="0" r="8" fill="#8A7E6A"/>' for j in range(3)) + '</g>')
                cont += dots
                c.a(f"tl.fromTo('#{mid}-d',{{opacity:0}},{{opacity:1,duration:0.15}},{q(max(c.t0, tk - 0.7))});")
                c.a(f"tl.fromTo('#{mid}-d .dd',{{y:0}},{{y:-8,duration:0.18,yoyo:true,repeat:5,stagger:0.08}},{q(max(c.t0, tk - 0.7))});")
                c.a(f"tl.to('#{mid}-d',{{opacity:0,duration:0.1}},{q(tk - 0.05)});")
                an.som(max(c.t0, tk - 0.6), 'digitando', 0.1)
            else:
                bx = sx0 + 24
                cor, tinta = '#FFFFFF', '#1E2A3A'
            linhas = _quebra(tx, 34, lw - 40)
            h = 30 + 42 * len(linhas)
            cont += (f'<g id="{mid}"><rect x="{bx:.0f}" y="{y}" width="{lw:.0f}" height="{h}" rx="24" fill="{cor}"/>'
                     + ''.join(f'<text class="tg" x="{bx + 22:.0f}" y="{y + 50 + 44 * j}" font-size="38" fill="{tinta}">{_html.escape(l)}</text>' for j, l in enumerate(linhas))
                     + '</g>')
            c.a(f"tl.fromTo('#{mid}',{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.3,ease:'back.out(1.8)'}},{q(tk)});")
            an.som(tk, 'pop2', 0.2)
            y += h + 34 + (40 if lado != 'ia' and k + 1 < len(itens) and itens[k + 1][0] == 'ia' else 0)
    elif tela == 'agenda':
        cont += f'<text class="tc" x="{sx0 + 40}" y="{y + 10}" font-size="40" fill="#1E2A3A">AGENDA</text>'
        gx, gy, cw, chh = sx0 + 30, y + 40, (sx1 - sx0 - 60) / 7, 74
        alvo = (3, 2)
        for r in range(5):
            for cc in range(7):
                eh = (cc, r) == alvo
                cont += (f'<rect {"id=" + chr(34) + w + "-alvo" + chr(34) if eh else ""} x="{gx + cc * cw + 4:.0f}" y="{gy + r * chh + 4}" width="{cw - 8:.0f}" height="{chh - 8}" rx="10" '
                         f'fill="{"#E9E0CC" if (cc + r) % 5 else "#DCD2BC"}"/>')
        ax, ay = gx + alvo[0] * cw + cw / 2, gy + alvo[1] * chh + chh / 2
        cont += f'<path id="{w}-ok" d="M{ax - 16:.0f} {ay:.0f} l11 11 l20 -22" stroke="#FFFFFF" stroke-width="7" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/>'
        for k, (txt, tk) in enumerate(zip(itens, ts_)):
            bid = f'{w}-av{k}'
            cont += _balao(bid, (sx0 + sx1) / 2, gy + 5 * chh + 70 + 100 * k, txt, cauda='', icone='ok', tam=34)
            if k == 0:
                c.a(f"tl.to('#{w}-alvo',{{fill:'#3F7F55',duration:0.2}},{q(tk - 0.15)});")
                c.a(f"tl.fromTo('#{w}-ok',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.25}},{q(tk)});")
                an.som(tk, 'tique2', 0.3)
            _pop_balao(c, bid, tk + 0.1, 'pop2')
    elif tela == 'form':
        n = itens if isinstance(itens, int) else len(itens)
        for k in range(n):
            tk = ts_[k] if k < len(ts_) else t + 0.6 + 0.8 * k
            gy = y + k * 230
            cont += (f'<rect x="{sx0 + 26}" y="{gy}" width="{sx1 - sx0 - 52}" height="200" rx="20" fill="#EFE6D2"/>'
                     f'<rect x="{sx0 + 56}" y="{gy + 30}" width="{(sx1 - sx0) * 0.55:.0f}" height="16" rx="8" fill="#8A7E6A"/>'
                     f'<rect x="{sx0 + 56}" y="{gy + 58}" width="{(sx1 - sx0) * 0.35:.0f}" height="16" rx="8" fill="#B7AC98"/>')
            for j in range(3):
                ox = sx0 + 56 + j * 132
                eh = j == (k * 2 + 1) % 3
                oid = f' id="{w}-o{k}"' if eh else ''
                cont += f'<rect{oid} x="{ox}" y="{gy + 110}" width="118" height="60" rx="30" fill="#FFFFFF" stroke="#2D4A63" stroke-width="3"/>'
                if eh:
                    cont += f'<path id="{w}-ok{k}" d="M{ox + 44} {gy + 140} l11 11 l20 -22" stroke="#FFFFFF" stroke-width="6" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/>'
                    c.a(f"tl.to('#{w}-o{k}',{{fill:'#3F7F55',duration:0.15}},{q(tk)});")
                    c.a(f"tl.fromTo('#{w}-ok{k}',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.2}},{q(tk + 0.05)});")
                    c.a(f"tl.to('#{w}-pol',{{x:{ox + 59 - 760},y:{gy + 140 - 1560},duration:0.3,ease:'power2.inOut'}},{q(tk - 0.32)});")
                    c.a(f"tl.to('#{w}-pol',{{scale:0.92,duration:0.08,yoyo:true,repeat:1}},{q(tk - 0.04)});")
                    an.som(tk, 'madeira', 0.25)
    polegar = (f'<g id="{w}-pol" transform="translate(0 0)"><g transform="translate(760 1560) scale(0.72)">'
               f'<path d="M30 400 L30 40 Q30 -20 -10 -24 Q-50 -26 -54 30 L-60 400Z" fill="#E3AE84"/>'
               f'<path d="M-46 0 Q-30 -22 -6 -16 Q8 -10 6 10 Q-20 4 -46 0Z" fill="#F1C9A5"/></g></g>') if tela == 'form' else \
        '<path d="M800 1560 Q760 1500 790 1450 Q830 1420 860 1470 L900 1960 L820 1960Z" fill="#E3AE84"/>'
    c.a(f"tl.fromTo('#{w}-cel',{{rotation:-1.5}},{{rotation:1.5,duration:1.6,yoyo:true,repeat:{max(1, int((t1 - t) / 1.6))},ease:'sine.inOut',svgOrigin:'540 1500'}},{q(c.t0)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}"><g id="{w}-cel">{mao}{corpo_cel}{cont}{polegar}</g></g>')


def _quebra(txt, tam, larg, fonte='serif'):
    pal, linhas, atual = txt.split(), [], ''
    for p in pal:
        tent = (atual + ' ' + p).strip()
        if _txt_larg(tent, tam, fonte) <= larg or not atual:
            atual = tent
        else:
            linhas.append(atual)
            atual = p
    return linhas + ([atual] if atual else [])


def campanhas(c, t, anuncios=3, cortar=(1, 2), t_ia=None, t_corta=None, lixeira=True, pessoa=True):
    """Escritório vazio à noite: TV grande com os anúncios, a IA (brilho dourado) passando o scanner por eles; em t_corta
    os anúncios de `cortar` levam um X e caem na lixeira, o que fica ganha borda verde. Cenário 'escritorio_noite'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'ca')
    rnd = random.Random(_seed(c.id) + 6)
    tv = (f'<rect x="170" y="850" width="740" height="470" rx="14" fill="#11161F"/><rect x="190" y="870" width="700" height="430" fill="#1F2A44"/>'
          f'<rect x="520" y="1320" width="40" height="60" fill="#2A2F38"/>')
    cards = ''
    cores = ('#B5523B', '#5B7F6E', '#C9A24A', '#6E5A8A')
    formas = ('<rect x="40" y="40" width="80" height="80" rx="10" fill="#FBF6EA"/>',
              '<circle cx="80" cy="80" r="44" fill="#FBF6EA"/>',
              '<path d="M30 120 L80 40 L130 120Z" fill="#FBF6EA"/>')
    for k in range(anuncios):
        x = 215 + k * 225
        cid = f'{w}-a{k}'
        cards += (f'<g transform="translate({x} 900)"><g id="{cid}"><rect width="200" height="370" rx="12" fill="#FBF6EA"/>'
                  f'<rect x="20" y="20" width="160" height="160" rx="8" fill="{cores[k % 4]}"/><g transform="translate(20 20)">{formas[k % 3]}</g>'
                  f'<rect x="20" y="200" width="150" height="16" rx="6" fill="#8A7E6A"/><rect x="20" y="230" width="110" height="16" rx="6" fill="#B7AC98"/>'
                  f'<rect x="20" y="300" width="160" height="46" rx="10" fill="#2D4A63"/>'
                  f'<g class="xx" opacity="0"><path d="M30 30 L170 340 M170 30 L30 340" stroke="#B5523B" stroke-width="16" stroke-linecap="round"/></g>'
                  f'<rect class="okb" x="-6" y="-6" width="212" height="382" rx="16" fill="none" stroke="#3F7F55" stroke-width="10" opacity="0"/></g></g>')
    ti = _T(t_ia) if t_ia is not None else t + 0.3
    scan = (f'<g id="{w}-sc" opacity="0"><rect x="0" y="880" width="16" height="410" fill="#F2B544" opacity=".8"/>'
            f'<rect x="-30" y="880" width="76" height="410" fill="#F2B544" opacity=".18"/>'
            f'<path transform="translate(8 850)" d="M0 -26 L7 -7 L26 0 L7 7 L0 26 L-7 7 L-26 0 L-7 -7Z" fill="#F2B544"/></g>')
    D = max(0.5, t1 - ti)
    c.a(f"tl.set('#{w}-sc',{{opacity:1}},{q(ti)});")
    c.a(f"tl.fromTo('#{w}-sc',{{x:200}},{{x:880,duration:1.1,ease:'sine.inOut',yoyo:true,repeat:{max(1, int(D / 1.1))}}},{q(ti)});")
    an.som(ti, 'shimmer', 0.2)
    lix = ''
    if lixeira:
        lix = (f'<path d="M470 1560 L610 1560 L596 1740 L484 1740Z" fill="#5A6470"/><rect x="460" y="1546" width="160" height="20" rx="6" fill="#47505B"/>'
               + ''.join(f'<rect x="{500 + 26 * j}" y="1590" width="8" height="120" rx="4" fill="#47505B"/>' for j in range(4)))
    if t_corta is not None:
        tc = _T(t_corta)
        for k in range(anuncios):
            cid = f'{w}-a{k}'
            if k in cortar:
                c.a(f"tl.to('#{cid} .xx',{{opacity:1,duration:0.15}},{q(tc + 0.15 * k)});")
                c.a(f"tl.to('#{cid}',{{y:480,x:{225 - 225 * k},rotation:{(-1) ** k * 70},scale:0.35,duration:0.7,ease:'power2.in',transformOrigin:'50% 50%'}},{q(tc + 0.35 + 0.15 * k)});")
                an.som(tc + 0.15 * k, 'batida', 0.25)
            else:
                c.a(f"tl.to('#{cid} .okb',{{opacity:1,duration:0.2}},{q(tc + 0.3)});")
                c.a(f"tl.to('#{cid}',{{scale:1.08,duration:0.3,ease:'back.out(2)',transformOrigin:'50% 50%'}},{q(tc + 0.4)});")
        an.som(tc + 1.0, 'papel', 0.2)
    # mesas vazias com a luminária acesa (fim de expediente)
    rnd2 = random.Random(9)
    mesas = (f'<g transform="translate(-40 {CHAO + 40}) scale(1.05)">{_mesa_lado(0, 0, 300, "#5A4630")}</g>'
             f'<g transform="translate(1120 {CHAO + 40}) scale(-1.05 1.05)">{_mesa_lado(0, 0, 300, "#5A4630")}</g>'
             + _cadeira(250, CHAO + 40, -1, '#2A3550') + _cadeira(830, CHAO + 40, 1, '#2A3550'))
    gente = ''
    if pessoa:   # o dono chega com o café ('anda') ou já está ('fica') olhando o painel; balança a cabeça quando a IA corta
        pid = f'{w}-d'
        rnd_d = random.Random(_seed('dono-painel'))
        gente = pos(corpo(pid, 'cafe', item='cafe', estilo='lateral', roupa='#8FB3C9', pele=PELES[1], cabelo=CABELOS[0], rnd=rnd_d),
                    -120 if pessoa != 'fica' else 180, 1800, 1.1)
        if pessoa != 'fica':
            anda(c, pid, c.t0, 300 / 1.1, min(1.2, max(0.6, _fim(c) - c.t0 - 0.4)), bracos=False)
        vive(c, pid, c.t0, _fim(c))
        respira(c, pid, c.t0 + (1.2 if pessoa != 'fica' else 0), _fim(c))
        if t_corta is not None:
            c.a(f"tl.to('#{pid} .j-cab',{{rotation:-10,duration:0.3,yoyo:true,repeat:3,ease:'sine.inOut',svgOrigin:'0 0'}},{q(_T(t_corta))});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{tv}{cards}{scan}{mesas}{lix}{gente}</g>')


def quarto_ia(c, t, t_ia=None, t_corta=None, cortar=(1, 2), anuncios=3):
    """Quarto à noite: o dono DORMINDO na cama (zzz subindo) e, na escrivaninha, o monitor com os anúncios; um robozinho
    de IA flutua conferindo cada um (feixe dourado). Em t_corta ele corta com a tesoura os de `cortar`, que levam X e
    caem na lixeira; o que fica ganha borda verde. Cenário 'quarto_noite'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'qi')
    rnd = random.Random(_seed(c.id) + 31)
    yb = 1750
    cama = (f'<rect x="60" y="{yb - 330}" width="40" height="330" rx="10" fill="#5A3E28"/>'
            f'<rect x="90" y="{yb - 150}" width="560" height="70" rx="10" fill="#E9E4D8"/><rect x="90" y="{yb - 84}" width="560" height="40" fill="#5A3E28"/>'
            f'<rect x="100" y="{yb - 44}" width="20" height="44" fill="#3A2818"/><rect x="620" y="{yb - 44}" width="20" height="44" fill="#3A2818"/>'
            f'<ellipse cx="185" cy="{yb - 168}" rx="80" ry="32" fill="#FBF6EA"/>'
            f'<g id="{w}-cab"><circle cx="200" cy="{yb - 200}" r="46" fill="#E3AE84"/><path d="M156 {yb - 214} Q160 {yb - 262} 210 {yb - 254} Q246 {yb - 246} 244 {yb - 214} Q220 {yb - 232} 196 {yb - 226} Q172 {yb - 222} 156 {yb - 214}Z" fill="#2B1D14"/>'
            f'<path d="M206 {yb - 196} q8 6 16 0" stroke="#1E1A16" stroke-width="4" fill="none" stroke-linecap="round"/></g>'
            f'<g id="{w}-cob"><path d="M230 {yb - 190} Q420 {yb - 250} 640 {yb - 186} L650 {yb - 140} L230 {yb - 140}Z" fill="#5B4A7A"/>'
            f'<path d="M230 {yb - 168} Q420 {yb - 214} 640 {yb - 166}" stroke="#4A3A66" stroke-width="8" fill="none"/></g>')
    c.a(f"tl.fromTo('#{w}-cob',{{y:0}},{{y:-8,duration:1.3,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 1.3))},ease:'sine.inOut'}},{q(c.t0)});")   # respirando
    zzz = ''.join(f'<text class="tg zz" x="{260 + 26 * k}" y="{yb - 270 - 40 * k}" font-size="{44 + 10 * k}" fill="#F3EBCF">z</text>' for k in range(3))
    c.a(f"tl.fromTo('#{w} .zz',{{opacity:0,y:20}},{{opacity:1,y:-40,duration:1.2,ease:'sine.out',repeat:{max(1, int((t1 - c.t0) / 1.2))},stagger:{{each:0.35,repeat:{max(1, int((t1 - c.t0) / 1.2))}}}}},{q(c.t0)});")
    mesa = (f'<rect x="660" y="{yb - 220}" width="380" height="20" rx="4" fill="#5A3E28"/><rect x="676" y="{yb - 200}" width="16" height="200" fill="#4A3220"/>'
            f'<rect x="1010" y="{yb - 200}" width="16" height="200" fill="#4A3220"/>'
            f'<rect x="830" y="{yb - 268}" width="40" height="50" fill="#2A2F38"/><rect x="790" y="{yb - 226}" width="120" height="10" rx="4" fill="#2A2F38"/>')
    mx0, my0, mw, mh = 640, yb - 560, 420, 300
    mon = (f'<rect x="{mx0 - 14}" y="{my0 - 14}" width="{mw + 28}" height="{mh + 28}" rx="12" fill="#11161F"/>'
           f'<rect x="{mx0}" y="{my0}" width="{mw}" height="{mh}" fill="#1F2A44"/>'
           f'<rect x="{mx0}" y="{my0}" width="{mw}" height="{mh}" fill="#8FC1D4" opacity=".08" id="{w}-brilho"/>')
    c.a(f"tl.fromTo('#{w}-brilho',{{opacity:0.04}},{{opacity:0.14,duration:0.4,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.4))},ease:'steps(2)'}},{q(c.t0)});")
    cores = ('#B5523B', '#5B7F6E', '#C9A24A')
    cards = ''
    for k in range(anuncios):
        x = mx0 + 22 + k * 132
        cid = f'{w}-a{k}'
        cards += (f'<g transform="translate({x} {my0 + 24})"><g id="{cid}"><rect width="118" height="252" rx="8" fill="#FBF6EA"/>'
                  f'<rect x="10" y="10" width="98" height="110" rx="6" fill="{cores[k % 3]}"/><circle cx="59" cy="65" r="26" fill="#FBF6EA" opacity=".8"/>'
                  f'<rect x="10" y="136" width="90" height="12" rx="5" fill="#8A7E6A"/><rect x="10" y="158" width="66" height="12" rx="5" fill="#B7AC98"/>'
                  f'<rect x="10" y="206" width="98" height="32" rx="8" fill="#2D4A63"/>'
                  f'<g class="xx" opacity="0"><path d="M14 14 L104 238 M104 14 L14 238" stroke="#B5523B" stroke-width="12" stroke-linecap="round"/></g>'
                  f'<rect class="okb" x="-5" y="-5" width="128" height="262" rx="12" fill="none" stroke="#3F9F65" stroke-width="8" opacity="0"/></g></g>')
    lix = (f'<path d="M880 {yb - 120} L990 {yb - 120} L978 {yb} L892 {yb}Z" fill="#5A6470"/><rect x="872" y="{yb - 132}" width="126" height="16" rx="5" fill="#47505B"/>')
    # robozinho da IA (flutua; olho dourado; tesoura)
    rob = (f'<g id="{w}-rob"><g transform="scale(1.7)"><g id="{w}-robi"><ellipse cx="0" cy="96" rx="40" ry="8" fill="#000" opacity=".18"/>'
           f'<rect x="-46" y="-40" width="92" height="80" rx="30" fill="#DCE3F0"/><rect x="-34" y="-22" width="68" height="34" rx="14" fill="#1E2A3A"/>'
           f'<circle id="{w}-olho" cx="0" cy="-5" r="10" fill="#F2B544"/><path d="M0 -40 L0 -62" stroke="#DCE3F0" stroke-width="5"/>'
           f'<circle cx="0" cy="-66" r="8" fill="#F2B544"/><rect x="-30" y="40" width="60" height="26" rx="10" fill="#B9C4D6"/>'
           f'<g id="{w}-tes" transform="translate(52 20)"><g class="lm1"><path d="M0 0 L46 -8 L48 -2Z" fill="#AEB4BB"/></g>'
           f'<g class="lm2"><path d="M0 0 L46 8 L48 2Z" fill="#AEB4BB"/></g><circle r="9" fill="none" stroke="#B5523B" stroke-width="5"/></g></g></g></g>')
    c.a(f"tl.fromTo('#{w}-robi',{{y:0}},{{y:-14,duration:0.7,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.7))},ease:'sine.inOut'}},{q(c.t0)});")
    c.a(f"tl.fromTo('#{w}-olho',{{opacity:1}},{{opacity:0.4,duration:0.25,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.25))}}},{q(c.t0)});")
    ti = _T(t_ia) if t_ia is not None else t + 0.2
    feixe = f'<path id="{w}-fx" d="M0 0 L0 0" stroke="#F2B544" stroke-width="0"/>'
    pts = [(mx0 + 81 + k * 132, my0 - 120) for k in range(anuncios)]
    c.a(f"tl.set('#{w}-rob',{{x:560,y:{my0 - 60}}},{q(c.t0)});")
    tt = ti
    seq = []
    if t_corta is None:
        ida_volta = list(range(anuncios)) + list(range(anuncios - 2, 0, -1))
        for j in range(12):
            k = ida_volta[j % len(ida_volta)]
            if tt > t1 - 0.2:
                break
            px, py = pts[k]
            c.a(f"tl.to('#{w}-rob',{{x:{px},y:{py},duration:0.45,ease:'power2.inOut'}},{q(tt)});")
            c.a(f"tl.fromTo('#{w}-a{k}',{{scale:1}},{{scale:1.06,duration:0.2,yoyo:true,repeat:1,transformOrigin:'50% 50%'}},{q(tt + 0.4)});")
            tt += 0.7
        an.som(ti, 'shimmer', 0.18)
    else:
        tc = _T(t_corta)
        for j, k in enumerate(cortar):
            px, py = pts[k]
            tk = tc + 0.75 * j
            c.a(f"tl.to('#{w}-rob',{{x:{px - 130},y:{py + 200},duration:0.4,ease:'power2.inOut'}},{q(tk - 0.45)});")
            c.a(f"tl.fromTo('#{w}-tes .lm1',{{rotation:0}},{{rotation:-24,duration:0.1,yoyo:true,repeat:3,svgOrigin:'0 0'}},{q(tk - 0.05)});")
            c.a(f"tl.fromTo('#{w}-tes .lm2',{{rotation:0}},{{rotation:24,duration:0.1,yoyo:true,repeat:3,svgOrigin:'0 0'}},{q(tk - 0.05)});")
            c.a(f"tl.to('#{w}-a{k} .xx',{{opacity:1,duration:0.12}},{q(tk)});")
            dxl = 935 - (mx0 + 22 + k * 132 + 59)
            c.a(f"tl.to('#{w}-a{k}',{{x:{dxl},y:{yb - 60 - (my0 + 24 + 126)},rotation:{(-1) ** k * 60},scale:0.3,duration:0.55,ease:'power2.in',transformOrigin:'50% 50%'}},{q(tk + 0.2)});")
            an.som(tk, 'batida', 0.22)
            an.som(tk + 0.7, 'papel', 0.18)
        for k in range(anuncios):
            if k not in cortar:
                c.a(f"tl.to('#{w}-a{k} .okb',{{opacity:1,duration:0.2}},{q(tc + 0.75 * len(cortar))});")
                c.a(f"tl.to('#{w}-rob',{{x:{pts[k][0]},y:{pts[k][1]},duration:0.4,ease:'power2.inOut'}},{q(tc + 0.75 * len(cortar) - 0.1)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{cama}{zzz}{mesa}{mon}{cards}{lix}{feixe}{rob}</g>')


def grafico_pergaminho(c, t, titulo, barras, sub='', tempos=None, maximo=100, grade=(25, 50, 75, 100), sufixo='%',
                       carimbo='', t_carimbo=None):
    """Gráfico de barras DESENHADO NO PERGAMINHO (ref. de documentário ilustrado): eixos a tinta, linhas de grade pontilhadas
    com o valor, barras marrons subindo uma a uma com o número CONTANDO em cima, linha pontilhada ligando os topos e a
    última barra em destaque (com texto dentro, opcional). barras = [('Hoje', 80, 'com IA'), ...] (rótulo, valor,
    texto dentro da barra ou ''). Só número que ele falou. Cenário 'pergaminho'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'gp')
    x0, x1, yb, yt = 200, 900, 1700, 1000
    n = len(barras)
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.3 + 0.7 * k for k in range(n)]
    out = [f'<text class="tc" x="{x0 - 60}" y="{yt - 90}" font-size="56" fill="#2A1D12">{_html.escape(titulo.upper())}</text>']
    if sub:
        out.append(f'<text class="tg" x="{x0 - 60}" y="{yt - 40}" font-size="38" fill="#5A4126">{_html.escape(sub)}</text>')
    for g in grade:
        y = yb - (yb - yt) * g / maximo
        out.append(f'<path d="M{x0} {y:.0f} L{x1} {y:.0f}" stroke="#8A6A3A" stroke-width="2" stroke-dasharray="6 8" opacity=".55"/>'
                   f'<text class="tc" x="{x0 - 16}" y="{y + 14:.0f}" text-anchor="end" font-size="38" fill="#5A4126">{g}{sufixo}</text>')
    out.append(f'<path id="{w}-ax" d="M{x0} {yt - 30} L{x0} {yb} L{x1} {yb}" stroke="#2A1D12" stroke-width="5" fill="none" pathLength="1" stroke-dasharray="1 1"/>')
    c.a(f"tl.fromTo('#{w}-ax',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.5,ease:'power2.out'}},{q(max(c.t0, t - 0.2))});")
    bw = min(260 if n == 1 else 170, (x1 - x0 - 60) / n * 0.6)
    passo = (x1 - x0 - 40) / n
    topos = []
    for k, (rot, val, dentro) in enumerate(barras):
        bx = x0 + 40 + passo * k + (passo - bw) / 2
        hh = (yb - yt) * val / maximo
        dest = k == n - 1
        bid = f'{w}-b{k}'
        out.append(f'<rect id="{bid}" x="{bx:.0f}" y="{yb - hh:.0f}" width="{bw:.0f}" height="{hh:.0f}" fill="{"#7A4A22" if dest else "#8A5A2B"}"/>'
                   f'<text class="tc" x="{bx + bw / 2:.0f}" y="{yb + 56}" text-anchor="middle" font-size="44" fill="#2A1D12">{_html.escape(rot.upper())}</text>'
                   f'<text class="tc" id="{bid}-v" x="{bx + bw / 2:.0f}" y="{yb - hh - 22:.0f}" text-anchor="middle" font-size="64" fill="#2A1D12">0{sufixo}</text>')
        if dentro:
            out.append(f'<text class="tc" id="{bid}-d" x="{bx + bw / 2:.0f}" y="{yb - hh + 70:.0f}" text-anchor="middle" font-size="40" fill="#FBF6EA">{_html.escape(dentro.upper())}</text>')
            c.a(f"tl.fromTo('#{bid}-d',{{opacity:0}},{{opacity:1,duration:0.3}},{q(ts_[k] + 0.9)});")
        tk = ts_[k]
        # atributos (sem transform: o scaleY com origem em % deixava a barra deslocada pra cima a própria altura)
        c.a(f"tl.fromTo('#{bid}',{{attr:{{y:{yb},height:0}}}},{{attr:{{y:{yb - hh:.0f},height:{hh:.0f}}},duration:0.9,ease:'power2.out'}},{q(tk)});")
        c.a(f"tl.fromTo('#{bid}-v',{{attr:{{y:{yb - 22}}},opacity:0}},{{attr:{{y:{yb - hh - 22:.0f}}},opacity:1,duration:0.9,ease:'power2.out'}},{q(tk)});")
        c.a(f"conta('#{bid}-v',0,{val},{q(tk)},0.9,'{sufixo}');")
        an.som(tk, 'marimba', 0.18)
        topos.append((bx + bw / 2, yb - hh - 90))
    if n > 1:
        d = 'M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in topos)
        out.append(f'<path id="{w}-l" d="{d}" stroke="#2A1D12" stroke-width="4" fill="none" stroke-dasharray="3 9" opacity=".8"/>')
        c.a(f"tl.fromTo('#{w}-l',{{opacity:0}},{{opacity:0.8,duration:0.4}},{q(ts_[1] + 0.5)});")
    else:   # uma barra só: a linha pontilhada sobe do pé do eixo até o topo da barra durante a cena (nunca parado)
        bx_, by_ = topos[0]
        out.append(f'<path id="{w}-l" d="M{x0 + 20} {yb - 30} C{x0 + 120} {yb - 60} {bx_ - 160} {by_ + 160} {bx_ - 30} {by_ + 70}" '
                   f'stroke="#2A1D12" stroke-width="5" fill="none" stroke-dasharray="4 12" opacity=".8"/>'
                   f'<path id="{w}-lm" d="M{x0 + 20} {yb - 30} C{x0 + 120} {yb - 60} {bx_ - 160} {by_ + 160} {bx_ - 30} {by_ + 70}" '
                   f'stroke="#F3E6C6" stroke-width="9" fill="none" pathLength="1" stroke-dasharray="1 1"/>')
        c.a(f"tl.fromTo('#{w}-lm',{{strokeDashoffset:0}},{{strokeDashoffset:-1,duration:{max(0.8, t1 - ts_[0] - 0.2):.2f},ease:'power1.inOut'}},{q(ts_[0])});")
    if carimbo:
        tcb = _T(t_carimbo) if t_carimbo is not None else ts_[-1] + 1.0
        cx_, cy_ = topos[-1][0] + 170, topos[-1][1] + 250
        cx_ = min(cx_, 960 - 140)
        out.append(f'<g transform="translate({cx_:.0f} {cy_:.0f}) rotate(-12)"><g id="{w}-cb"><rect x="-130" y="-46" width="260" height="92" rx="12" '
                   f'fill="#F3E6C6" fill-opacity=".85" stroke="#3F7F55" stroke-width="8"/>'
                   f'<text class="tc" x="0" y="22" text-anchor="middle" font-size="62" fill="#3F7F55">{_html.escape(carimbo.upper())}</text></g></g>')
        c.a(f"tl.fromTo('#{w}-cb',{{opacity:0,scale:2.2}},{{opacity:1,scale:1,duration:0.22,ease:'power4.in',transformOrigin:'50% 50%'}},{q(tcb)});")
        an.som(tcb + 0.18, 'impacto', 0.28)
    # o gráfico nunca fica parado: a pena (ponta) anda ao longo do eixo e a tinta respira
    out.append(f'<g id="{w}-pena"><path d="M0 0 L60 -150 L74 -146 L14 4Z" fill="#2A1D12"/><path d="M60 -150 Q110 -230 150 -250 Q120 -170 74 -146Z" fill="#E9E0CC" stroke="#8A6A3A" stroke-width="3"/></g>')
    c.a(f"tl.fromTo('#{w}-pena',{{x:{x1 - 60},y:{yb - 10},rotation:-6}},{{x:{x1 - 10},y:{yb - 36},rotation:6,duration:0.35,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.35))},ease:'sine.inOut'}},{q(c.t0)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}</g>')


def mapa(c, t, pontos, tempos=None, rota=True, veiculo=True):
    """MAPA de uma cidade ilustrada e FICTÍCIA (quadras, ruas, rio, praça, árvores) com pinos caindo e a rota sendo
    desenhada de um ponto ao outro, um carrinho seguindo a rota. pontos = [('Lead', x, y), ('IA', x, y), ...] em
    coordenadas de tela (área x 120–960, y 900–1780); tempos = quando cada pino cai. Nunca usar mapa de lugar real.
    Cenário 'pergaminho'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'mp')
    rnd = random.Random(_seed(c.id) + 41)
    X0, X1, Y0, Y1 = 90, 990, 120, 1800   # rodada 8: o mapa ocupa a tela toda (os 40 % de cima ficavam vazios)
    out = [f'<rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" rx="14" fill="#EAD9B0" stroke="#8A6A3A" stroke-width="5"/>']
    # rio
    out.append(f'<path d="M{X0} {Y0 + 300} C{X0 + 260} {Y0 + 220} {X0 + 360} {Y0 + 520} {X0 + 560} {Y0 + 470} S{X1 - 120} {Y0 + 640} {X1} {Y0 + 600}" '
               f'stroke="#8FB6C4" stroke-width="58" fill="none" stroke-linecap="butt"/>')
    # quadras em grade com ruas
    for gx in range(X0 + 30, X1 - 60, 110):
        for gy in range(Y0 + 30, Y1 - 60, 110):
            if abs((gy - Y0) - (300 + 300 * (gx - X0) / (X1 - X0))) < 90:
                continue   # perto do rio
            cor = '#9DBF8A' if rnd.random() < 0.1 else rnd.choice(('#D9C69A', '#D2BD8E', '#DCCBA2'))
            out.append(f'<rect x="{gx}" y="{gy}" width="{rnd.choice((84, 90, 96))}" height="{rnd.choice((84, 90, 96))}" rx="6" fill="{cor}"/>')
            if cor == '#9DBF8A':
                out.append(''.join(f'<circle cx="{gx + 20 + 25 * j}" cy="{gy + 30 + 20 * (j % 2)}" r="12" fill="#5B8F66"/>' for j in range(3)))
    out.append(''.join(f'<path d="M{X0} {y} L{X1} {y}" stroke="#F6EBD3" stroke-width="10" opacity=".7"/>' for y in (Y0 + 250, Y0 + 690, Y0 + 1250)))
    out.append(''.join(f'<path d="M{x} {Y0} L{x} {Y1}" stroke="#F6EBD3" stroke-width="10" opacity=".7"/>' for x in (X0 + 360, X0 + 690)))
    # faixa de pergaminho onde fica o letreiro (o mapa continua em cima e embaixo dela)
    out.append(f'<rect x="{X0 - 10}" y="470" width="{X1 - X0 + 20}" height="420" fill="#F3E6C6" opacity=".93"/>'
               f'<path d="M{X0 - 10} 470 L{X1 + 10} 470 M{X0 - 10} 890 L{X1 + 10} 890" stroke="#8A6A3A" stroke-width="4"/>')
    # rosa dos ventos (09/11: dentro da caixa segura do formato — o "N" é texto e saía pelo pé no RL)
    out.append(f'<g transform="translate({min(X1 - 80, X_LAT[1] - 50)} {min(Y1 - 90, faixa()[1] - 70)})"><circle r="46" fill="none" stroke="#8A6A3A" stroke-width="3"/>'
               f'<path d="M0 -58 L10 0 L0 58 L-10 0Z" fill="#5A4126"/><path d="M-58 0 L0 10 L58 0 L0 -10Z" fill="#8A6A3A"/>'
               f'<text class="tc" x="0" y="-64" text-anchor="middle" font-size="36" fill="#5A4126">N</text></g>')
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.3 + 0.7 * k for k in range(len(pontos))]
    pinos = ''
    for k, (nome, px, py) in enumerate(pontos):
        pid = f'{w}-p{k}'
        dest = k == len(pontos) - 1
        tx = nome.upper()
        lw = _txt_larg(tx, 48) + 40
        lx = min(max(px, 180 + lw / 2), 900 - lw / 2)   # 100 px + o passeio da câmera
        pinos += (f'<g id="{pid}"><path d="M{px} {py} C{px - 30} {py - 40} {px - 34} {py - 70} {px} {py - 92} C{px + 34} {py - 70} {px + 30} {py - 40} {px} {py}Z" '
                  f'fill="{"#3F7F55" if dest else "#B5523B"}"/><circle cx="{px}" cy="{py - 62}" r="13" fill="#FBF6EA"/>'
                  f'<rect x="{lx - lw / 2:.0f}" y="{py - 178}" width="{lw:.0f}" height="66" rx="10" fill="#FBF4E4" stroke="#2A1D12" stroke-width="3"/>'
                  f'<text class="tc" x="{lx:.0f}" y="{py - 128}" text-anchor="middle" font-size="48" fill="#2A1D12">{_html.escape(tx)}</text></g>')
        c.a(f"tl.fromTo('#{pid}',{{y:-160,opacity:0}},{{y:0,opacity:1,duration:0.45,ease:'bounce.out'}},{q(ts_[k])});")
        an.som(ts_[k] + 0.1, 'pop2', 0.22)
    rota_svg = ''
    if rota and len(pontos) > 1:
        for k in range(len(pontos) - 1):
            (_, ax, ay), (_, bx, by) = pontos[k], pontos[k + 1]
            mx, my = (ax + bx) / 2 + rnd.uniform(-60, 60), (ay + by) / 2 + rnd.uniform(-60, 60)
            rid = f'{w}-r{k}'
            rota_svg += f'<path id="{rid}" d="M{ax} {ay - 20} Q{mx:.0f} {my:.0f} {bx} {by - 20}" stroke="#B5523B" stroke-width="9" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/>'
            c.a(f"tl.fromTo('#{rid}',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{max(0.3, ts_[k + 1] - ts_[k] - 0.1):.2f},ease:'power1.inOut'}},{q(ts_[k] + 0.1)});")
        if veiculo:
            vid = f'{w}-v'
            rota_svg += f'<g id="{vid}"><circle r="20" fill="#F2B544" stroke="#2A1D12" stroke-width="4"/><circle r="7" fill="#2A1D12"/></g>'
            (_, ax, ay) = pontos[0]
            c.a(f"tl.set('#{vid}',{{x:{ax},y:{ay - 20},opacity:0}},{q(c.t0)});")
            c.a(f"tl.to('#{vid}',{{opacity:1,duration:0.2}},{q(ts_[0] + 0.1)});")
            for k in range(1, len(pontos)):
                (_, bx, by) = pontos[k]
                c.a(f"tl.to('#{vid}',{{x:{bx},y:{by - 20},duration:{max(0.3, ts_[k] - ts_[k - 1] - 0.1):.2f},ease:'power1.inOut'}},{q(ts_[k - 1] + 0.1)});")
            # depois que a rota fecha, o ponto continua rodando o caminho (volta e vai) até o fim da cena
            tt_, ida = ts_[-1] + 0.1, list(range(len(pontos) - 2, -1, -1)) + list(range(1, len(pontos)))
            j = 0
            while tt_ < t1 - 0.3:
                (_, bx, by) = pontos[ida[j % len(ida)]]
                c.a(f"tl.to('#{vid}',{{x:{bx},y:{by - 20},duration:0.55,ease:'sine.inOut'}},{q(tt_)});")
                tt_ += 0.6
                j += 1
            c.a(f"tl.fromTo('#{vid}',{{scale:1}},{{scale:1.25,duration:0.3,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.3))},ease:'sine.inOut'}},{q(c.t0)});")
    an.som(t, 'papel', 0.18)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}{rota_svg}{pinos}</g>')


def chegada(c, t, n=4, t_porta=None, carro=True):
    """O time chegando de manhã: calçada, gente com café, crachá e pasta andando até a porta de vidro do escritório,
    que abre; carro passando na rua. Cenário 'rua'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'ch')
    rnd = random.Random(_seed(c.id) + 7)
    ch = 1560
    # 08/11 (folha do t108): prédio 100 px mais baixo — o telhado encostava no letreiro de 2 linhas
    pr = (f'<rect x="640" y="{ch - 660}" width="460" height="660" fill="#3B5A75"/><rect x="640" y="{ch - 660}" width="460" height="30" fill="#2A445C"/>'
          + ''.join(f'<rect x="{670 + 100 * j}" y="{ch - 600 + 130 * r}" width="70" height="90" fill="#BFDCE6"/>' for j in range(4) for r in range(2))
          + f'<rect x="680" y="{ch - 300}" width="300" height="300" fill="#22394F"/>'
          f'<g id="{w}-pe"><rect x="692" y="{ch - 288}" width="138" height="288" fill="#BFDCE6" opacity=".85"/></g>'
          f'<g id="{w}-pd"><rect x="830" y="{ch - 288}" width="138" height="288" fill="#BFDCE6" opacity=".85"/></g>'
          f'<rect x="680" y="{ch - 300}" width="300" height="12" fill="#2A445C"/>')
    tp = _T(t_porta) if t_porta is not None else t + 0.7
    c.a(f"tl.to('#{w}-pe',{{x:-120,duration:0.5,ease:'power2.inOut'}},{q(tp)});")
    c.a(f"tl.to('#{w}-pd',{{x:120,duration:0.5,ease:'power2.inOut'}},{q(tp)});")
    an.som(tp, 'swish', 0.15)
    pes = ''
    itens = ('cafe', 'pasta', 'celular', 'cafe', 'papel')
    for k in range(n):
        pid = f'{w}-p{k}'
        it = itens[k % 5]
        pose = {'cafe': 'cafe', 'pasta': 'pasta', 'celular': 'celular', 'papel': 'cafe'}[it]
        x0 = 380 - 210 * k
        pes = pos(corpo(pid, pose, item=it, cracha=True, rnd=rnd), x0, 1660, 0.98) + pes
        dur = max(0.8, t1 - t - 0.05 * k)
        anda(c, pid, t + 0.05 * k, 560 / 0.98 * (dur / 1.7), dur, bracos=False)
        vive(c, pid, t, t1)
    car = ''
    if carro:
        car = f'<g id="{w}-car"><g transform="translate(1250 1800) scale(2.2)">{an._carro(0, 0, "#C9A24A", "#9C7A2E", -1).replace("data-v", "data-x-v")}</g></g>'
        c.a(f"tl.fromTo('#{w}-car',{{x:0}},{{x:-1700,duration:{max(1.2, t1 - t + 0.4):.2f},ease:'none'}},{q(c.t0)});")
        an.som(t + 0.2, 'whoosh_lento', 0.12)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{pr}{pes}{car}</g>')


def sala_reuniao(c, t, tv='grafico', t_tv=None, aperto=None, assina=None, poses=('aperta', 'aperta'), itens=(None, None),
                 comemora=None, empurra=None):
    """Sala de reunião: TV na parede (tv='grafico' barras subindo sem número; 'contrato' contrato sendo assinado + carimbo
    FECHADO; 'video' chamada de vídeo), mesa ao fundo com papéis e duas pessoas de CORPO INTEIRO na frente.
    aperto=t: as duas apertam a mão (poses 'aperta'). Outras poses: 'aponta' (pra TV), 'celular', 'em_pe'. Cenário 'reuniao'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'rr')
    rnd = random.Random(_seed(c.id) + 8)
    tvx0, tvy0, tvw, tvh = 250, 940, 580, 320
    tt = _T(t_tv) if t_tv is not None else t + 0.4
    carimbo_ = ''
    tela = f'<rect x="{tvx0}" y="{tvy0}" width="{tvw}" height="{tvh}" fill="#F3EEDF"/>'
    if tv == 'grafico':
        for k in range(4):
            bx = tvx0 + 70 + k * 120
            hh = 40 + 48 * k
            tela += f'<rect id="{w}-b{k}" x="{bx}" y="{tvy0 + tvh - 40 - hh}" width="80" height="{hh}" fill="{"#B5523B" if k == 3 else "#2D4A63"}"/>'
            c.a(f"tl.fromTo('#{w}-b{k}',{{scaleY:0}},{{scaleY:1,duration:0.5,ease:'power3.out',transformOrigin:'50% 100%'}},{q(tt + 0.35 * k)});")
            an.som(tt + 0.35 * k, 'marimba', 0.16)
        tela += (f'<rect x="{tvx0 + 40}" y="{tvy0 + tvh - 40}" width="{tvw - 80}" height="4" fill="#2A2A2A"/>'
                 f'<path id="{w}-seta" d="M{tvx0 + 90} {tvy0 + tvh - 120} L{tvx0 + 470} {tvy0 + 60}" stroke="#3F7F55" stroke-width="10" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/>'
                 f'<path id="{w}-pt" d="M{tvx0 + 470} {tvy0 + 60} l-46 6 l30 30z" fill="#3F7F55"/>')
        c.a(f"tl.fromTo('#{w}-seta',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.9,ease:'power2.out'}},{q(tt + 1.4)});")
        c.a(f"tl.fromTo('#{w}-pt',{{opacity:0}},{{opacity:1,duration:0.2}},{q(tt + 2.2)});")
    elif tv == 'contrato':
        ta = _T(assina) if assina is not None else tt + 0.6
        tela += (f'<rect x="{tvx0 + 150}" y="{tvy0 + 20}" width="280" height="300" fill="#FFFFFF"/>'
                 f'<text class="tc" x="{tvx0 + 290}" y="{tvy0 + 74}" text-anchor="middle" font-size="44" fill="#1E2A3A">CONTRATO</text>'
                 + ''.join(f'<rect x="{tvx0 + 180}" y="{tvy0 + 100 + 24 * j}" width="{220 - 30 * (j % 3)}" height="8" fill="#C8BFAE"/>' for j in range(6))
                 + f'<path id="{w}-ass" d="M{tvx0 + 190} {tvy0 + 280} q20 -30 36 -4 t40 -6 q16 -20 30 4 t40 -8" stroke="#1E2A3A" stroke-width="4" fill="none" pathLength="1" stroke-dasharray="1 1"/>')
        carimbo_ = (f'<g transform="translate({tvx0 + 395} {tvy0 + 215}) rotate(-10)"><g id="{w}-car"><rect x="-112" y="-36" width="224" height="72" rx="10" fill="#F3EEDF" fill-opacity=".9" stroke="#3F7F55" stroke-width="7"/>'
                 f'<text class="tc" x="0" y="18" text-anchor="middle" font-size="50" fill="#3F7F55">FECHADO</text></g></g>')   # camada acima da TV
        c.a(f"tl.fromTo('#{w}-ass',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:0.9,ease:'power1.inOut'}},{q(ta)});")
        c.a(f"tl.fromTo('#{w}-car',{{opacity:0,scale:2}},{{opacity:1,scale:1,duration:0.2,ease:'power4.in',transformOrigin:'50% 50%'}},{q(ta + 1.0)});")
        an.som(ta, 'papel', 0.2)
        an.som(ta + 1.15, 'impacto', 0.28)
    elif tv == 'video':
        tela += (f'<rect x="{tvx0 + 20}" y="{tvy0 + 20}" width="{tvw / 2 - 30:.0f}" height="{tvh - 40}" fill="#2D4A63"/>'
                 f'<rect x="{tvx0 + tvw / 2 + 10:.0f}" y="{tvy0 + 20}" width="{tvw / 2 - 30:.0f}" height="{tvh - 40}" fill="#3B4E5E"/>'
                 f'<g transform="translate({tvx0 + 60} {tvy0 + 60}) scale(1.2)">{busto(f"{w}-vb", terno=True)}</g>'
                 f'<g transform="translate({tvx0 + tvw / 2 + 50:.0f} {tvy0 + 60}) scale(1.2)">{busto(f"{w}-vc", terno=False)}</g>')
        _vivo(c, f'{w}-vb', t, t1, fala=True)
        _vivo(c, f'{w}-vc', t, t1)
    tvg = (f'<rect x="{tvx0 - 22}" y="{tvy0 - 22}" width="{tvw + 44}" height="{tvh + 44}" rx="12" fill="#11161F"/>'
           f'<svg x="{tvx0}" y="{tvy0}" width="{tvw}" height="{tvh}" viewBox="{tvx0} {tvy0} {tvw} {tvh}">{tela}</svg>'
           + (carimbo_ if tv == 'contrato' else ''))
    mesa = (f'<rect x="240" y="1440" width="600" height="22" rx="6" fill="#5A3E28"/><rect x="300" y="1462" width="24" height="150" fill="#4A3422"/>'
            f'<rect x="756" y="1462" width="24" height="150" fill="#4A3422"/>'
            + ''.join(f'<g transform="translate({330 + 160 * j} 1426) rotate({rnd.uniform(-5, 5):.0f})"><rect width="90" height="16" fill="#FBF6EA"/></g>' for j in range(3))
            + f'<g transform="translate(700 1416)">{_xicara(0, 0, w + "-xv")}</g>'.replace('<g transform="translate(0 0)">', '<g transform="translate(0 0) scale(0.7)">')
            + _cadeira(250, 1612, 1, '#2D3A4F') + _cadeira(830, 1612, -1, '#2D3A4F'))
    _vapor(c, w + '-xv', c.t0, t1)
    pa, pb = f'{w}-a', f'{w}-b'
    xa, xb = (395, 685) if poses[0] == 'aperta' else (230, 860)
    pes = (pos(corpo(pa, poses[0], blazer='#2D3A4F', gravata='#B5523B', roupa='#E9E4D8', item=itens[0], rnd=rnd), xa, 1790, 1.1)
           + pos(corpo(pb, poses[1], blazer=rnd.choice(('#4A3A2C', '#5B7F6E', None)), item=itens[1], rnd=rnd), xb, 1790, 1.1, -1))
    pes_cmd = pes
    vive(c, pa, t, t1, fala=True)
    vive(c, pb, t, t1)
    fundo_ = ''
    if empurra is not None:   # câmera empurra pro gráfico quando a linha sobe e volta antes da comemoração
        te = _T(empurra)
        c.a(f"tl.to('#{w}',{{scale:1.22,duration:0.8,ease:'power2.inOut',svgOrigin:'540 {tvy0 + tvh // 2}'}},{q(te)});")
        c.a(f"tl.to('#{w}',{{scale:1,duration:0.6,ease:'power2.inOut',svgOrigin:'540 {tvy0 + tvh // 2}'}},{q(te + 1.5)});")
    if comemora is not None:   # os dois se aproximam e batem a mão no alto
        tc = _T(comemora)
        # mão de cada um em 'toca_alto' fica a (82+4)*1.1 ≈ 95 px à frente do corpo e 1405-130 ≈ y 1275: os dois param a
        # 190 px um do outro (silhuetas separadas) e as mãos se encontram no meio
        xm = (xa + xb) / 2
        alvo_a, alvo_b = xm - 95, xm + 95
        for p_, k, dx in ((pa, 0, alvo_a - xa), (pb, 1, xb - alvo_b)):
            anda(c, p_, tc - 0.95, max(0, dx) / 1.1, 0.75, bracos=False)
            c.a(f"tl.to('#{p_} .it',{{opacity:0,duration:0.15}},{q(tc - 0.3)});")
            muda_pose(c, p_, poses[k], 'toca_alto', tc - 0.25, 0.25)
        yh = 1790 - (350 + 118) * 1.1
        c.a(f"tl.fromTo('#{w}-hf',{{scale:0.2,opacity:1}},{{scale:1.7,opacity:0,duration:0.5,ease:'power2.out',svgOrigin:'{xm:.0f} {yh:.0f}'}},{q(tc)});")
        an.som(tc, 'pop2', 0.3)
        an.som(tc + 0.05, 'floreio', 0.2)
        fundo_ += (f'<g id="{w}-hf" opacity="0">' + ''.join(
            f'<path d="M{xm:.0f} {yh:.0f} l{60 * math.cos(math.radians(a_)):.0f} {60 * math.sin(math.radians(a_)):.0f}" stroke="#F2B544" stroke-width="7" stroke-linecap="round"/>'
            for a_ in range(0, 360, 45)) + f'<circle cx="{xm:.0f}" cy="{yh:.0f}" r="16" fill="#FFF1C8"/></g>')
    elif t1 - t > 4.0:   # cena longa: alguém passa no corredor do fundo com café (nunca fica parado)
        pf = f'{w}-f'
        fundo_ = pos(corpo(pf, 'cafe', item='cafe', rnd=rnd), -200, 1900, 1.22)
        anda(c, pf, t + 1.0, 1500 / 1.22, max(1.5, t1 - t - 1.0), bracos=False)
        vive(c, pf, t, t1)
    respira(c, pa, t, t1)
    respira(c, pb, t + 0.5, t1)
    if aperto is not None:
        tap = _T(aperto)
        for p in (pa, pb):
            c.a(f"tl.fromTo('#{p} .j-bf',{{rotation:0}},{{rotation:7,duration:0.14,yoyo:true,repeat:7,ease:'sine.inOut',svgOrigin:'0 0'}},{q(tap)});")
        an.som(tap, 'madeira', 0.2)
    for k, p in enumerate((pa, pb)):
        if poses[k] == 'aponta':
            gesticula(c, p, t, t1, 'j-bf', 5, 0.5)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{tvg}{mesa}{pes}{fundo_}</g>')


def operacao(c, t, n=10, ia=8, t_ia=None, t_fim=None, cafe=True):
    """A operação em fileiras de mesas: `ia` estações acendem com a IA (tela dourada + brilho), as outras têm gente
    trabalhando. Ex.: '80% da operação roda com IA' = 8 de 10. Cenário 'escritorio'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'op')
    rnd = random.Random(_seed(c.id) + 9)
    ti = _T(t_ia) if t_ia is not None else t + 0.3
    tf = _T(t_fim) if t_fim is not None else ti + 1.6
    pessoas_idx = {1, 7} if ia == 8 and n == 10 else set(range(ia, n))
    partes = []
    cols = (n + 1) // 2
    ordem_ia = [k for k in range(n) if k not in pessoas_idx]
    # 08/11 (física): o posto inteiro (encosto em x-74·e até o fim da mesa em x+360·e) tem que caber no passo da
    # fileira — com 5 por fila a cadeira de um entrava na mesa do outro. Agora 3 fileiras (fundo → frente), cada uma
    # com quantos postos cabem sem encostar.
    FILAS = ((1440, 0.46), (1625, 0.55), (1820, 0.64))
    lugares = []
    for y_, e_ in FILAS:
        cap = max(1, int(1040 / (434 * e_ + 14)))
        passo = 1040 / cap
        lugares += [(20 + 74 * e_ + passo * j + (passo - 434 * e_) / 2, y_, e_) for j in range(cap)]
    lugares = lugares[:n] if len(lugares) >= n else lugares + lugares[-1:] * (n - len(lugares))
    for k in range(n):
        x, y, esc = lugares[k]
        pid = f'{w}-p{k}'
        if k in pessoas_idx:
            g, _, _ = _posto(c, pid, x, y, esc, 1, 'digita', rnd, tela='linhas', xicara=False)
            vive(c, pid, t, t1)
            digita(c, pid, t, t1)
        else:
            g, _, _ = _posto(c, pid, x, y, esc, 1, 'digita', rnd, tela='ia', xicara=False)
            g = g.replace(f'<g id="{pid}" class="corpo">', f'<g id="{pid}" class="corpo" opacity="0">')
            idx = ordem_ia.index(k)
            tk = ti + (tf - ti) * idx / max(1, len(ordem_ia) - 1)
            c.a(f"tl.to('#{pid}-mon .iag',{{opacity:0.85,duration:0.25}},{q(tk)});")
            c.a(f"tl.fromTo('#{pid}-mon .iast',{{scale:0.4,rotation:0}},{{scale:1.3,rotation:180,duration:0.5,ease:'back.out(2)',svgOrigin:'0 0'}},{q(tk)});")
            c.a(f"tl.to('#{pid}-mon .iast',{{rotation:540,duration:{max(0.5, t1 - tk - 0.5):.2f},ease:'none',svgOrigin:'0 0'}},{q(tk + 0.5)});")
            an.som(tk, 'pop', 0.12)
        partes.append(g)
    if cafe:
        pid = f'{w}-cf'
        partes.append(pos(corpo(pid, 'cafe', item='cafe', rnd=rnd), -150, 1900, 1.15))
        anda(c, pid, t + 0.2, 1350 / 1.15 * min(1, (t1 - t) / 5), t1 - t - 0.2, bracos=False)
        vive(c, pid, t, t1)
    an.som(ti, 'shimmer', 0.18)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(partes)}</g>')


def videochamada(c, t, t_acena=None, rotulo='Você'):
    """Pessoa de headset na mesa acenando pra uma chamada de vídeo com uma cadeira vazia esperando (rotulo no quadro
    vazio, o anel pulsando). Cenário 'escritorio'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'vc')
    rnd = random.Random(_seed(c.id) + 10)
    pid = f'{w}-p'
    ta = _T(t_acena) if t_acena is not None else t + 0.2
    g, _, _ = _posto(c, pid, 170, CHAO + 40, 1.12, 1, 'acena_sent', rnd, monitor=False, headset=True, roupa='#2D4A63')
    mon = (f'<rect x="560" y="1110" width="420" height="300" rx="14" fill="#11161F"/><rect x="576" y="1126" width="388" height="268" fill="#2D4A63"/>'
           f'<rect x="752" y="1410" width="36" height="100" fill="#4A4F57"/><rect x="700" y="1500" width="140" height="14" rx="6" fill="#4A4F57"/>'
           f'<circle cx="770" cy="1230" r="62" fill="#3B5A75"/><circle cx="770" cy="1210" r="26" fill="#6F8FA8"/><path d="M724 1278 Q770 1230 816 1278Z" fill="#6F8FA8"/>'
           f'<circle id="{w}-anel" cx="770" cy="1230" r="70" fill="none" stroke="#F2B544" stroke-width="6"/>'
           f'<text class="tc" x="770" y="1366" text-anchor="middle" font-size="48" fill="#FBF6EA">{_html.escape(rotulo.upper())}</text>')
    c.a(f"tl.fromTo('#{w}-anel',{{scale:0.9,opacity:1}},{{scale:1.25,opacity:0,duration:0.9,repeat:{max(1, int((t1 - t) / 0.9))},ease:'power1.out',svgOrigin:'770 1230'}},{q(t)});")
    vive(c, pid, t, t1, fala=True)
    gesticula(c, pid, ta, t1, 'j-bfa', 22, 0.28)
    an.som(ta, 'glock', 0.18)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{g}{mon}</g>')



# ---------------------------------------------------------------- rodada 4 (06/11): mais ambientes do dia a dia
def copa(c, t, fila=4, t_fila=None, pilha=None, cartoes=()):
    """Copa: máquina de café pingando, fila de gente com caneca chegando (o time crescendo), quadro de cortiça onde as
    faturas vão sendo pregadas (cartoes=[('Ferramenta', t)]), pilha de papel crescendo no balcão (pilha=('Folha', t)).
    Cenário 'copa'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cp')
    rnd = random.Random(_seed(c.id) + 11)
    yb = 1740
    balcao = (f'<rect x="90" y="1470" width="900" height="24" rx="4" fill="#E9E4D8"/><rect x="100" y="1494" width="880" height="{yb - 1494}" fill="#5B7F6E"/>'
              + ''.join(f'<rect x="{x}" y="1512" width="160" height="{yb - 1530}" rx="4" fill="none" stroke="#4A6A5B" stroke-width="5"/>'
                        f'<rect x="{x + 70}" y="1530" width="20" height="8" rx="4" fill="#C9A24A"/>' for x in range(120, 960, 172)))
    vid = f'{w}-v'
    maq = (f'<rect x="160" y="1270" width="150" height="200" rx="10" fill="#2A2F38"/><rect x="176" y="1290" width="118" height="50" rx="6" fill="#1A1E25"/>'
           f'<circle id="{w}-led" cx="270" cy="1315" r="8" fill="#B5523B"/><rect x="214" y="1360" width="42" height="18" fill="#4A4F57"/>'
           f'<rect id="{w}-pingo" x="232" y="1378" width="6" height="40" fill="#6B3E1E"/>'
           f'<g transform="translate(235 1468) scale(0.8)">{_xicara(0, -6, vid)}</g>')
    _vapor(c, vid, c.t0, t1)
    c.a(f"tl.fromTo('#{w}-pingo',{{scaleY:0.2,opacity:0.4}},{{scaleY:1,opacity:1,duration:0.35,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.35))},ease:'sine.inOut',transformOrigin:'50% 0%'}},{q(c.t0)});")
    c.a(f"tl.fromTo('#{w}-led',{{opacity:1}},{{opacity:0.25,duration:0.4,ease:'steps(1)',yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.4))}}},{q(c.t0)});")
    frutas = ''.join(f'<circle cx="{500 + dx}" cy="{1448 + dy}" r="20" fill="{cor}"/>' for dx, dy, cor in ((-24, 0, '#B5523B'), (20, 0, '#C9A24A'), (-2, -22, '#5B8F66')))
    frutas += '<path d="M450 1452 L550 1452 L536 1472 L464 1472Z" fill="#8A6A45"/>'
    quadro = (f'<rect x="392" y="990" width="280" height="250" rx="6" fill="#6B4E31"/><rect x="404" y="1002" width="256" height="226" fill="#C9A273"/>'
              + ''.join(f'<circle cx="{rnd.uniform(420, 640):.0f}" cy="{rnd.uniform(1015, 1215):.0f}" r="3" fill="#8A6A45"/>' for _ in range(30))
              + f'<rect x="420" y="1020" width="70" height="60" fill="#F2E27A" transform="rotate(-6 455 1050)"/><rect x="580" y="1150" width="60" height="56" fill="#F6B98C" transform="rotate(5 610 1178)"/>')
    extra = ''
    for k, (rot, tc) in enumerate(cartoes):
        tc = _T(tc)
        cid = f'{w}-f{k}'
        extra += (f'<g transform="translate({330 + 12 * k} {1030 + 54 * k}) rotate({-5 + 4 * k})"><g id="{cid}">'
                  f'<rect width="270" height="84" rx="5" fill="#FBF6EA"/><rect width="270" height="18" rx="5" fill="#B5523B"/>'
                  f'<circle cx="135" cy="-2" r="8" fill="#B5523B"/>'
                  f'<text class="tc" x="135" y="66" text-anchor="middle" font-size="44" fill="#1E2A3A">{_html.escape(rot.upper())}</text></g></g>')
        c.a(f"tl.fromTo('#{cid}',{{opacity:0,scale:1.5,rotation:-14}},{{opacity:1,scale:1,rotation:0,duration:0.25,ease:'power3.in',transformOrigin:'50% 0%'}},{q(tc)});")
        an.som(tc + 0.22, 'batida', 0.2)
    if pilha:
        rot, tp = pilha
        tp = _T(tp)
        gp = f'{w}-p'
        fol = ''.join(f'<rect class="fl" x="{770 + (k % 2) * 5}" y="{1456 - 15 * k}" width="140" height="14" rx="2" fill="{"#FBF6EA" if k % 2 else "#E9E0CC"}"/>' for k in range(13))
        extra += f'<g id="{gp}">{fol}{_etiqueta(850, 1200, rot, 40, eid=gp + "-e")}</g>'
        c.a(f"tl.fromTo('#{gp} .fl',{{opacity:0,y:-60}},{{opacity:1,y:0,duration:0.22,ease:'power2.out',stagger:0.07}},{q(tp)});")
        _pop_balao(c, f'{gp}-e', tp + 0.3, 'papel')
    pes = ''
    tf = _T(t_fila) if t_fila is not None else t + 0.2
    alvos = [330, 520, 700, 880, 1040][:fila]
    for k, alvo in enumerate(alvos):
        pid = f'{w}-q{k}'
        item = 'cafe' if k else None
        pose = 'cafe' if k else 'aperta'
        if k == 0:     # o primeiro já está na máquina, servindo o café
            pes = pos(corpo(pid, pose, rnd=rnd), alvo, 1840, 1.08, -1) + pes
            gesticula(c, pid, t, t1, 'j-bfa', 8, 0.5)
        else:
            x0 = 1250 + 200 * k
            pes = pos(corpo(pid, pose, item=item, cracha=True, rnd=rnd), x0, 1840, 1.08, -1) + pes
            dur = min(max(0.8, t1 - tf - 0.35 * k), 1.3 + 0.2 * k)
            anda(c, pid, tf + 0.35 * (k - 1), (x0 - alvo) / 1.08, dur, bracos=False)
        vive(c, pid, t, t1, fala=k == 1)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{quadro}{balcao}{maq}{frutas}{extra}{pes}</g>')


def recepcao(c, t, modo='chegada', n=3, t_porta=None):
    """Recepção: porta de vidro, CATRACA com leitor de crachá (luz fica verde e apita a cada um que passa) e
    recepcionista no balcão. modo='chegada' = o time passando a catraca de manhã com café e crachá; modo='espera' =
    poltrona vazia com café servido esperando e a recepcionista acenando. Cenário 'recepcao'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'rc')
    rnd = random.Random(_seed(c.id) + 12)
    yb = 1760
    rec = f'{w}-r'
    balcao = (pos(corpo(rec, 'acena_sent' if modo == 'espera' else 'digita', roupa='#B5523B', estilo='longo', rnd=rnd), 900, yb - 40, 0.95, -1)
              + f'<rect x="740" y="1470" width="300" height="22" rx="4" fill="#E9E4D8"/><rect x="752" y="1492" width="276" height="{yb - 1492}" fill="#8A6A45"/>'
              f'<rect x="752" y="1560" width="276" height="10" fill="#6B4E31"/>'
              + _relogio3(890, 1010, 46, (8, 0)))
    vive(c, rec, t, t1, fala=True)
    if modo == 'espera':
        gesticula(c, rec, t, t1, 'j-bfa', 22, 0.3)
        an.som(t + 0.2, 'glock', 0.16)
    else:
        digita(c, rec, t, t1)
    cat = (f'<g transform="translate(500 1600) scale(0.85)"><rect x="-70" y="-200" width="44" height="200" rx="8" fill="#5A646C"/>'
           f'<rect x="26" y="-200" width="44" height="200" rx="8" fill="#5A646C"/><rect x="-74" y="-214" width="52" height="24" rx="6" fill="#2A2F38"/>'
           f'<circle id="{w}-luz" cx="-48" cy="-202" r="8" fill="#B5523B"/>'
           f'<g id="{w}-braco"><rect x="-26" y="-120" width="52" height="10" rx="5" fill="#AEB4BB"/></g></g>')
    pes = ''
    if modo == 'chegada':
        itens = ('cafe', 'pasta', 'celular', 'cafe')
        for k in range(n):
            pid = f'{w}-p{k}'
            it = itens[k % 4]
            pose = {'cafe': 'cafe', 'pasta': 'pasta', 'celular': 'celular'}[it]
            x0 = -120 - 240 * k
            esc = 0.85
            dist = 1000
            dur = max(1.0, (t1 - t) + 0.6)   # ainda estão passando quando a cena corta
            ti = t + 0.1 * k
            pes = pos(corpo(pid, pose, item=it, cracha=True, rnd=rnd), x0, 1600, esc) + pes
            anda(c, pid, ti, dist / esc, dur, bracos=False)
            vive(c, pid, t, t1)
            tp = ti + dur * (500 - x0) / dist
            if tp < t1 - 0.1:
                c.a(f"tl.to('#{w}-luz',{{fill:'#3F9F65',duration:0.05}},{q(tp - 0.15)});")
                c.a(f"tl.to('#{w}-luz',{{fill:'#B5523B',duration:0.05}},{q(tp + 0.35)});")
                c.a(f"tl.fromTo('#{w}-braco',{{scaleX:1}},{{scaleX:0.1,duration:0.2,yoyo:true,repeat:1,transformOrigin:'0% 50%'}},{q(tp - 0.1)});")
                an.som(tp - 0.12, 'tique2', 0.25)
    else:
        vid = f'{w}-v'
        anel = f'{w}-an'
        pes = (f'<ellipse id="{anel}" cx="330" cy="{yb + 4}" rx="150" ry="26" fill="#F2B544" opacity=".35"/>'
               f'<g transform="translate(330 {yb})"><rect x="-110" y="-150" width="220" height="90" rx="26" fill="#557A8B"/>'
               f'<rect x="-120" y="-300" width="60" height="240" rx="26" fill="#4A6A7A"/><rect x="80" y="-200" width="44" height="140" rx="20" fill="#4A6A7A"/>'
               f'<rect x="-100" y="-60" width="14" height="60" fill="#2A2A2A"/><rect x="86" y="-60" width="14" height="60" fill="#2A2A2A"/></g>'
               f'<rect x="510" y="1640" width="140" height="14" rx="5" fill="#8A6A45"/><rect x="574" y="1654" width="12" height="{yb - 1654}" fill="#6B4E31"/>'
               f'<g transform="translate(580 1636) scale(0.8)">{_xicara(0, -6, vid)}</g>')
        _vapor(c, vid, c.t0, t1)
        c.a(f"tl.fromTo('#{anel}',{{scale:0.85,opacity:0.5}},{{scale:1.15,opacity:0.15,duration:0.8,yoyo:true,repeat:{max(1, int((t1 - t) / 0.8))},ease:'sine.inOut',svgOrigin:'330 {yb}'}},{q(t)});")
        pid = f'{w}-pp'
        pes += pos(corpo(pid, 'celular', item='tablet', rnd=rnd), 1250, 1860, 1.08, -1)
        anda(c, pid, c.t0, 700, max(1.0, t1 - c.t0), bracos=False)
        vive(c, pid, c.t0, t1)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{cat}{pes}{balcao}</g>')


def deposito(c, t, ia=None, entregador=True):
    """Depósito / expedição: esteira andando com as caixas, o portal da IA conferindo (as caixas saem dele com selo ✓),
    gente embalando atrás da esteira e o entregador levando a caixa pra fora. Cenário 'deposito'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'dp')
    rnd = random.Random(_seed(c.id) + 13)
    D = max(1.0, t1 - c.t0)
    ty = 1470
    est = (f'<rect x="-200" y="{ty}" width="1480" height="34" fill="#3A3F47"/><rect x="-200" y="{ty + 34}" width="1480" height="14" fill="#5A646C"/>'
           + ''.join(f'<circle class="rolo" cx="{x}" cy="{ty + 17}" r="13" fill="#5A646C"/>' for x in range(-180, 1280, 46))
           + ''.join(f'<rect x="{x}" y="{ty + 48}" width="20" height="{CHAO - ty - 48}" fill="#5A646C"/>' for x in range(-100, 1280, 230)))
    n = 7
    passo = 1480 / n
    cxs = ''.join(f'<g transform="translate({-200 + passo * k:.0f} {ty})"><g class="cx"><rect x="0" y="-86" width="104" height="86" fill="{rnd.choice(("#C49A62", "#B58A52", "#D3AE76"))}"/>'
                  f'<rect x="44" y="-86" width="16" height="86" fill="#E3CDA2" opacity=".7"/></g></g>' for k in range(n))
    selos = ''.join(f'<g transform="translate({-200 + passo * k:.0f} {ty})"><g class="cx"><circle cx="78" cy="-60" r="16" fill="#3F7F55"/>'
                    f'<path d="M70 -60 l6 6 l12 -13" stroke="#fff" stroke-width="4" fill="none"/></g></g>' for k in range(n))
    clip = f'{w}-clip'
    defs = f'<defs><clipPath id="{clip}"><rect x="600" y="1200" width="900" height="400"/></clipPath></defs>'
    per = passo / 140   # 140 px/s
    rep = max(1, int(D / per) + 1)
    c.a(f"tl.fromTo('#{w} .cx',{{x:0}},{{x:{passo:.0f},duration:{per:.3f},ease:'none',repeat:{rep}}},{q(c.t0)});")
    c.a(f"tl.fromTo('#{w} .rolo',{{rotation:0}},{{rotation:360,duration:0.6,ease:'none',repeat:{max(1, int(D / 0.6))},transformOrigin:'50% 50%'}},{q(c.t0)});")
    ti = _T(ia) if ia is not None else t
    portal = (f'<rect x="520" y="1250" width="26" height="220" fill="#2D4A63"/><rect x="654" y="1250" width="26" height="220" fill="#2D4A63"/>'
              f'<rect x="510" y="1232" width="180" height="30" rx="8" fill="#2D4A63"/>'
              f'<rect id="{w}-luz" x="546" y="1262" width="108" height="208" fill="#F2B544" opacity=".0"/>'
              f'<path transform="translate(600 1247)" d="M0 -14 L4 -4 L14 0 L4 4 L0 14 L-4 4 L-14 0 L-4 -4Z" fill="#F2B544"/>')
    c.a(f"tl.fromTo('#{w}-luz',{{opacity:0.05}},{{opacity:0.45,duration:{per / 2:.3f},yoyo:true,repeat:{max(1, int((t1 - ti) / (per / 2)))},ease:'sine.inOut'}},{q(ti)});")
    an.som(ti, 'shimmer', 0.18)
    emb = f'{w}-e'
    atras = pos(corpo(emb, 'carrega', roupa='#C9A24A', rnd=rnd), 260, 1600, 0.9)
    vive(c, emb, c.t0, t1)
    gesticula(c, emb, c.t0, t1, 'j-bf', 10, 0.45)
    palete = ''.join(f'<rect x="{850 + (k % 2) * 92}" y="{1470 - 80 * (k // 2) - 80}" width="88" height="78" fill="{("#C49A62", "#B58A52")[k % 2]}"/>' for k in range(6))
    palete = f'<rect x="840" y="1470" width="200" height="0" fill="#8A6A45"/>' + palete
    pes = ''
    if entregador:
        pid = f'{w}-ent'
        pes = pos(corpo(pid, 'carrega', item='caixa', roupa='#8A5A2B', calca='#3B4A5E', rnd=rnd), -180, 1870, 1.12)
        anda(c, pid, c.t0 + 0.1, 1500 / 1.12 * min(1, D / 4.5), D - 0.1, bracos=False)
        vive(c, pid, c.t0, t1)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{defs}{palete}{atras}{est}{cxs}<g clip-path="url(#{clip})">{selos}</g>{portal}{pes}</g>')


def dono(c, t, papeis=None, visita=True, t_visita=None, pose='preocupado'):
    """Sala do dono: mesa grande de madeira, abajur verde, calculadora e contas; o dono com a mão na cabeça, papéis
    voando, e alguém entrando com mais papel. Cenário 'sala_dono'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'do')
    rnd = random.Random(_seed(c.id) + 14)
    pid = f'{w}-d'
    g, _, _ = _posto(c, pid, 230, CHAO + 30, 1.15, 1, pose, rnd, monitor=False, xicara=True, blazer='#2D3A4F', gravata='#B5523B', roupa='#E9E4D8')
    g = g.replace('fill="#8A6A45"', 'fill="#5A3E28"')
    topo = CHAO + 30 - 204 * 1.15
    obj = (f'<g transform="translate(560 {topo:.0f})"><rect x="-40" y="-8" width="80" height="8" fill="#C9A24A"/><rect x="-3" y="-120" width="6" height="112" fill="#C9A24A"/>'
           f'<path d="M-50 -110 L50 -110 L36 -150 L-36 -150Z" fill="#2F5A47"/><ellipse cx="0" cy="-110" rx="50" ry="7" fill="#F7D98A"/></g>'
           f'<g transform="translate(470 {topo:.0f})"><rect x="-34" y="-12" width="68" height="12" rx="3" fill="#3B4E5E"/><rect x="-28" y="-30" width="56" height="20" rx="3" fill="#3B4E5E"/>'
           f'<rect x="-22" y="-27" width="44" height="8" fill="#8FE0B0"/></g>'
           + ''.join(f'<rect x="{620 + 3 * k}" y="{topo - 10 - 7 * k:.0f}" width="96" height="7" fill="{("#FBF6EA", "#EFE6D2")[k % 2]}"/>' for k in range(8)))
    c.a(f"tl.fromTo('#{pid} .j-cab',{{rotation:-4}},{{rotation:6,duration:0.9,yoyo:true,repeat:{max(1, int((t1 - t) / 0.9))},ease:'sine.inOut',svgOrigin:'0 0'}},{q(t)});")
    vive(c, pid, t, t1, cabeca=False)
    gesticula(c, pid, t, t1, 'j-bfa', 12, 0.22)
    extra = ''
    if papeis is not None:
        extra += _papeis_voando(c, f'{w}-pv', 650, topo - 60, _T(papeis), sobe=480)
    pes = ''
    if visita:
        vp = f'{w}-v'
        tv = _T(t_visita) if t_visita is not None else t + 0.3
        pes = pos(corpo(vp, 'cafe', item='papel', rnd=rnd), 1250, 1850, 1.1, -1)
        anda(c, vp, tv, (1250 - 870) / 1.1, min(1.4, max(0.8, t1 - tv - 0.1)), bracos=False)
        vive(c, vp, t, t1, fala=True)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{g}{obj}{extra}{pes}</g>')


CSS = """
.quadro{display:block;overflow:visible}
.quadro-w{position:relative;display:flex;justify-content:center}
.cartao-f{position:absolute;right:20px;top:10px;background:#FBF4E4;color:#1E2A3A;font-family:'Cond',sans-serif;font-weight:800;font-stretch:75%;
  text-transform:uppercase;font-size:40px;padding:14px 26px;border-radius:14px;box-shadow:0 10px 0 rgba(0,0,0,.15)}
.cel-w{gap:0}
.notifs{position:absolute;right:0;top:30px;display:flex;flex-direction:column;gap:16px}
.notif{display:flex;align-items:center;gap:14px;background:#FBF4E4;color:#1E2A3A;font-family:'Garamond',serif;font-weight:700;font-size:36px;
  padding:14px 24px;border-radius:16px;box-shadow:0 8px 0 rgba(0,0,0,.15);white-space:nowrap}
.notif i{display:block;width:18px;height:18px;border-radius:50%;background:#B5523B}
.multi{display:flex;flex-direction:column;align-items:center;gap:6px}
.mnum{display:flex;flex-direction:column;align-items:center;font-family:'Garamond',serif;font-weight:700;font-size:150px;line-height:1.05;color:#B5523B}
.t-noite .mnum,.t-capitulo .mnum,.t-cidade_noite .mnum,.t-tarde .mnum{color:#F2B544}
.mrot{font-family:'Cinzel',serif;font-size:34px;letter-spacing:.2em;color:inherit;opacity:.85}
.doc{position:relative;background:#FBF6EA;padding:36px 44px 30px;border-radius:6px;box-shadow:0 14px 0 rgba(0,0,0,.14);transform:rotate(-1.2deg)}
.doc .dt{font-family:'Cond',sans-serif;font-weight:800;font-stretch:75%;text-transform:uppercase;font-size:48px;color:#1E2A3A;border-bottom:3px solid #1E2A3A;padding-bottom:10px;margin-bottom:14px}
.doc ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:12px}
.doc li{display:flex;align-items:center;gap:16px;font-family:'Garamond',serif;font-size:44px;color:#2A2A2A}
.doc li svg{width:44px;height:44px;flex:none;fill:none;stroke-width:6;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1 1}
.doc li.v svg{stroke:#3F7F55}.doc li.x svg{stroke:#B5523B}.doc li.x span{text-decoration:line-through;text-decoration-color:#B5523B;text-decoration-thickness:4px}
.carimbo-a{position:absolute;right:-20px;bottom:-30px;font-family:'Cond',sans-serif;font-weight:800;font-stretch:75%;font-size:64px;color:#B5523B;
  border:7px solid #B5523B;border-radius:12px;padding:4px 22px;text-transform:uppercase;background:rgba(251,246,234,.85)}
.graf{background:#F3E6C6;border-radius:8px;padding:30px 30px 20px;box-shadow:0 14px 0 rgba(0,0,0,.14)}
.graf .gt{font-family:'Cond',sans-serif;font-weight:800;font-stretch:75%;text-transform:uppercase;font-size:44px;color:#2A1D12}
.graf .gs{font-family:'Cinzel',serif;font-size:20px;letter-spacing:.16em;color:#5A4126;margin-top:4px}
.garea{position:relative;margin-top:10px}
.geixo{position:absolute;left:40px;right:40px;bottom:58px;height:3px;background:#2A1D12}
.gb{position:absolute;bottom:58px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end}
.gbar{width:100%;background:#8A5A2B}.gbar.dest{background:#B5523B}
.gv{font-family:'Cond',sans-serif;font-weight:800;font-stretch:75%;font-size:40px;color:#2A1D12;margin-bottom:6px}
.gr{position:absolute;bottom:-50px;white-space:nowrap;font-family:'Cond',sans-serif;font-weight:800;font-stretch:75%;font-size:30px;color:#2A1D12}
.glinha{position:absolute;left:0;top:0;overflow:visible;pointer-events:none}
.glinha path{fill:none;stroke:#2A1D12;stroke-width:3}
"""
