# -*- coding: utf-8 -*-
"""Cenas de ação do arsenal (07/11/2026): dia a dia de empresa e de vida, com PLANOS DIFERENTES (close de rosto, plano
médio, plano aberto, vista em corte, contraluz) — a análise das referências (analise-2.md) mostrou que o nosso editor
só tinha um enquadramento (sala vista de lado, gente de corpo inteiro no chão). Todas desenham na camada de ação
(bo._amb) e devolvem '' pro monta(). Tempos em índice de palavra (int) ou s (float).

Close / plano médio:  close_rosto, vendedor_telefone, notebook_grafico, caixa_registradora, carteira, celular_mao, agenda,
                      celulares_pergunta (6 celulares caindo, cada um com a mesma pergunta de cliente; 12/11)
Dia a dia:            entregador, balcao, reuniao_em_pe, cafe_maquina, transito_preso, fabrica_linha, escritorio_aberto,
                      predio_corte, contraluz, familia_jantar, parque_passeio, viagem, porto_carga
Clima e montagem:     clima (chuva/neve/folhas/sol), picotado (2–4 quadros rápidos dentro de uma frase)
"""
import html as _html
import math
import random

import animada as an
import bonecos as bo
import motor
from bonecos import (_T, _amb, _balao, _entra_amb, _etiqueta, _fim, _pop_balao, _seed, _txt_larg, anda, corpo, digita,
                     gesticula, muda_pose, pos, respira, vive)
from motor import q
import arsenal_fundos as af

__all__ = ['close_rosto', 'vendedor_telefone', 'notebook_grafico', 'caixa_registradora', 'carteira', 'celular_mao', 'agenda',
           'entregador', 'balcao', 'reuniao_em_pe', 'cafe_maquina', 'transito_preso', 'fabrica_linha', 'escritorio_aberto',
           'predio_corte', 'contraluz', 'familia_jantar', 'parque_passeio', 'viagem', 'porto_carga', 'clima', 'picotado',
           'balao', 'cartao', 'de_costas', 'caravana', 'celulares_pergunta']

SILH = ('<filter id="arsilh"><feColorMatrix type="matrix" values="0 0 0 0 0.07  0 0 0 0 0.05  0 0 0 0 0.04  0 0 0 1 0"/></filter>')


def _bx(x, txt, tam=48, extra=0):
    """x do centro de um balão/etiqueta com o texto dentro da margem (170 px = 100 + passeio da câmera)."""
    meia = (_txt_larg(txt.upper(), tam) + extra + 56) / 2
    return min(max(x, 230 + meia), 850 - meia)   # 230 = 100 de margem + passeio do piso + zoom lento (medido no t138)


def balao(c, x, y, texto, t, icone='', cor='#FBF4E4', som='pop2'):
    """Balão solto (fica na margem sozinho). icone: ok, ponto, ia."""
    bid = an._id(c, 'bl')
    x = _bx(x, texto, 48, 50 if icone else 0)
    _pop_balao(c, bid, _T(t), som)
    return _amb(c, _balao(bid, x, y, texto, cor=cor, icone=icone))


def cartao(c, x, y, texto, t, cor='#FBF6EA', faixa='#B5523B', rot=-3):
    """Cartão de papel com faixa colorida em cima (fatura, pedido, tarefa) caindo no lugar."""
    cid = an._id(c, 'ct')
    tx = texto.upper()
    w = _txt_larg(tx, 48) + 60
    x = min(max(x, 230 + w / 2), 850 - w / 2)
    c.a(f"tl.fromTo('#{cid}',{{opacity:0,y:-90,rotation:-12}},{{opacity:1,y:0,rotation:0,duration:0.38,ease:'back.out(1.8)'}},{q(_T(t))});")
    an.som(_T(t), 'pop2', 0.2)
    return _amb(c, f'<g transform="translate({x - w / 2:.0f} {y:.0f}) rotate({rot})"><g id="{cid}"><rect width="{w:.0f}" height="96" rx="6" fill="#000" opacity=".14" y="8"/>'
            f'<rect width="{w:.0f}" height="96" rx="6" fill="{cor}"/><rect width="{w:.0f}" height="20" rx="6" fill="{faixa}"/>'
            f'<text class="tc" x="{w / 2:.0f}" y="76" text-anchor="middle" font-size="48" fill="#1E2A3A">{_html.escape(tx)}</text></g></g>')


def _vis():
    pele, cab, est, roupa = bo._visual()
    return pele, cab, ('curto' if est == 'cacheado' else est), roupa


# ================================================================ CLOSE DE ROSTO (plano fechado, à moda da referência)
def close_rosto(c, t, expressao='pensa', objeto=None, t_reacao=None, roupa=None, terno=None, x=540):
    """Rosto GRANDE ocupando a metade de baixo (cabeça e ombros, ~680 px). expressao: pensa (olhos pra cima + 3
    pontinhos), preocupado (sobrancelha caída + gota de suor escorrendo), sorri, surpreso (boca em O + sobrancelha sobe),
    ideia (lâmpada acende em cima). objeto: 'celular' (celular na mão brilhando) ou 'cafe'. t_reacao = quando muda a cara."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cr')
    tr = _T(t_reacao) if t_reacao is not None else t + 0.5
    pele, cab, est, rp = _vis()
    if terno is None:
        terno = random.Random(_seed(c.id)).random() < 0.4
    s = 3.3
    ox, oy = x - 100 * s, 1940 - 262 * s
    bid = f'{w}-b'
    corpo_ = bo.busto(bid, pele=pele, cabelo=cab, estilo=est, roupa=roupa or (None if terno else rp), terno=terno)
    extra = ''
    if expressao == 'preocupado':
        extra += (f'<g id="{w}-gota"><path d="M146 66 Q152 78 146 84 Q140 78 146 66Z" fill="#9FD3E6"/></g>'
                  f'<g id="{w}-sb"><path d="M76 86 L94 78 M106 78 L124 86" stroke="{bo._esc(cab, 0.9)}" stroke-width="4.5" stroke-linecap="round"/></g>')
        c.a(f"tl.fromTo('#{w}-gota',{{y:0,opacity:0}},{{y:40,opacity:1,duration:1.2,ease:'power1.in',repeat:{max(1, int((t1 - tr) / 1.2))}}},{q(tr)});")
        c.a(f"tl.to('#{bid} .boca',{{scaleY:-0.6,duration:0.3,svgOrigin:'100 125'}},{q(tr)});")
    elif expressao == 'sorri':
        c.a(f"tl.to('#{bid} .boca',{{scaleY:2.2,scaleX:1.15,duration:0.3,ease:'back.out(2)',svgOrigin:'100 123'}},{q(tr)});")
    elif expressao == 'surpreso':
        extra += f'<ellipse id="{w}-o" cx="100" cy="126" rx="9" ry="12" fill="#5A2A1E" opacity="0"/>'
        c.a(f"tl.to('#{w}-o',{{opacity:1,duration:0.15}},{q(tr)});tl.to('#{bid} .boca',{{opacity:0,duration:0.1}},{q(tr)});")
        c.a(f"tl.fromTo('#{bid} .olhos',{{scale:1}},{{scale:1.35,duration:0.2,ease:'back.out(3)',svgOrigin:'100 97'}},{q(tr)});")
        an.som(tr, 'pop2', 0.2)
    elif expressao == 'pensa':
        extra += ''.join(f'<circle class="{w}-pt" cx="{150 + 16 * k}" cy="{36 - 14 * k}" r="{5 + 2 * k}" fill="#FBF6EA" opacity="0"/>' for k in range(3))
        c.a(f"tl.to('#{bid} .olhos',{{x:6,y:-5,duration:0.3}},{q(tr)});")
        c.a(f"tl.fromTo('.{w}-pt',{{opacity:0}},{{opacity:1,duration:0.2,stagger:0.25,repeat:{max(1, int((t1 - tr) / 1.2))},repeatDelay:0.45,yoyo:true}},{q(tr)});")
    elif expressao == 'ideia':
        extra += (f'<g id="{w}-lp" opacity="0"><g transform="translate(100 -30)"><circle r="26" fill="#F2B544"/><circle r="44" fill="#F2B544" opacity=".2"/>'
                  f'<rect x="-10" y="22" width="20" height="16" rx="3" fill="#8A8F96"/>'
                  + ''.join(f'<rect x="-3" y="-66" width="6" height="16" rx="3" fill="#F2B544" transform="rotate({a})"/>' for a in (-60, -30, 0, 30, 60)) + '</g></g>')
        c.a(f"tl.fromTo('#{w}-lp',{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3,ease:'back.out(2)'}},{q(tr)});")
        c.a(f"tl.to('#{bid} .boca',{{scaleY:2,duration:0.3,svgOrigin:'100 123'}},{q(tr)});")
        an.som(tr, 'brilho', 0.22)
    if objeto == 'celular':
        extra += (f'<g transform="translate(150 150) rotate(-12)"><rect x="-6" y="-4" width="40" height="72" rx="7" fill="#1E2A3A"/>'
                  f'<rect x="-1" y="2" width="30" height="58" rx="3" fill="#FFF6D8" id="{w}-tl"/><ellipse cx="14" cy="82" rx="22" ry="14" fill="{pele}"/></g>')
        c.a(f"tl.fromTo('#{w}-tl',{{fill:'#FFF6D8'}},{{fill:'#8FC1D4',duration:0.3,yoyo:true,repeat:{max(1, int((t1 - t) / 0.3))}}},{q(t)});")
    elif objeto == 'cafe':
        extra += f'<g transform="translate(160 200) scale(1.3)">{bo._xicara(0, 0, w + "-v")}</g>'
        bo._vapor(c, w + '-v', c.t0, t1)
    bo._vivo(c, bid, t, t1, fala=False)
    c.a(f"tl.fromTo('#{w}-r',{{y:0}},{{y:-8,duration:1.4,ease:'sine.inOut',yoyo:true,repeat:{max(1, int((t1 - t) / 1.4))}}},{q(t)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}"><g transform="translate({ox:.0f} {oy:.0f}) scale({s})"><g id="{w}-r">{corpo_}{extra}</g></g></g>')


# ================================================================ VENDEDOR AO TELEFONE (plano médio, atrás da mesa)
def vendedor_telefone(c, t, anotacoes=3, t_anot=None, baloes=(), headset=False, roupa=None):
    """Plano médio: vendedor atrás da mesa com o telefone na orelha (ou headset), ondas de voz saindo, bloquinho na
    mesa ganhando ✓ a cada venda (t_anot = lista de tempos), café com vapor, monitor. baloes=[('Fechado', t, 'ok')]."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'vt')
    rnd = random.Random(_seed(c.id) + 61)
    pid = f'{w}-p'
    esc = 2.2
    pes = pos(corpo(pid, 'digita' if headset else 'tel_sent', item=None if headset else 'celular', headset=headset, roupa=roupa, rnd=rnd),
              330, 2080, esc, 1)
    vive(c, pid, t, t1, fala=True)
    respira(c, pid, t, t1)
    if headset:
        digita(c, pid, t + 0.2, t1)
    else:
        gesticula(c, pid, t, t1, 'j-bt', 6, 0.5)
    # ondas de voz perto da boca
    hx, hy = 330 + 40 * esc, 2080 - (378 - 104 + 30) * esc
    ond = (f'<g transform="translate({hx + 50:.0f} {hy:.0f})"><g id="{w}-on" fill="none" stroke="#F2B544" stroke-width="6" stroke-linecap="round">'
           '<path d="M0 -20 Q14 0 0 20"/><path d="M16 -34 Q38 0 16 34"/><path d="M32 -48 Q62 0 32 48"/></g></g>')
    c.a(f"tl.fromTo('#{w}-on path',{{opacity:0}},{{opacity:1,duration:0.25,stagger:0.12,yoyo:true,repeat:{max(1, int((t1 - t) / 0.5))}}},{q(t)});")
    mesa = ('<rect x="-60" y="1660" width="1200" height="34" rx="8" fill="#8A6A45"/><rect x="-60" y="1694" width="1200" height="260" fill="#6B4E31"/>'
            '<rect x="-60" y="1694" width="1200" height="12" fill="#5A3E28"/>')
    mon = bo._monitor(860, 1660, 230, 160, 'grafico', rnd)
    # bloquinho com os ✓
    ts_ = [_T(x) for x in t_anot] if t_anot else [t + 0.6 + 0.7 * k for k in range(anotacoes)]
    bloco = (f'<g transform="translate(520 1572) rotate(-6)"><rect x="0" y="0" width="210" height="96" rx="4" fill="#FBF6EA"/>'
             f'<rect x="0" y="0" width="210" height="14" fill="#C9A24A"/>'
             + ''.join(f'<rect x="54" y="{26 + 22 * k}" width="{120 - 20 * (k % 2)}" height="6" fill="#B7AC98"/>'
                       f'<path id="{w}-ck{k}" d="M16 {30 + 22 * k} l8 8 l16 -14" stroke="#3F7F55" stroke-width="6" fill="none" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>'
                       for k in range(min(3, len(ts_)))) + '</g>')
    for k, tk in enumerate(ts_[:3]):
        c.a(f"tl.to('#{w}-ck{k}',{{strokeDashoffset:0,duration:0.25,ease:'power2.out'}},{q(tk)});")
        an.som(tk, 'tique2', 0.22)
    xi = f'<g transform="translate(150 1650) scale(1.5)">{bo._xicara(0, 0, w + "-v")}</g>'
    bo._vapor(c, w + '-v', c.t0, t1)
    bal = ''
    for k, b in enumerate(baloes):
        txt, tb, ic_ = b[0], _T(b[1]), (b[2] if len(b) > 2 else 'ok')
        bid = f'{w}-bl{k}'
        bal += _balao(bid, _bx(720, txt, 48, 50), 1150 - 110 * k, txt, icone=ic_)
        _pop_balao(c, bid, tb)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{mon}{pes}{ond}{mesa}{bloco}{xi}{bal}</g>')


# ================================================================ NOTEBOOK COM GRÁFICO (close de objeto)
def notebook_grafico(c, t, sentido='sobe', t_linha=None, celular=True, maos=True, alerta=None):
    """Close do notebook na mesa: na tela, o gráfico de linha DESENHANDO (sobe = verde, desce = vermelho e a tela pisca
    em alerta), com o ponto correndo na ponta; mãos digitando na frente, café com vapor, celular vibrando na mesa.
    Sem número (só o desenho)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'nb')
    tl_ = _T(t_linha) if t_linha is not None else t + 0.3
    sobe = sentido == 'sobe'
    cor = '#3F7F55' if sobe else '#B03A2A'
    X0, Y0, W_, H_ = 200, 1010, 680, 440
    pts = [(0.0, 0.78), (0.18, 0.66), (0.34, 0.70), (0.5, 0.5), (0.66, 0.42), (0.82, 0.24), (1.0, 0.1)]
    if not sobe:
        pts = [(x, 1 - y + 0.02) for x, y in pts]
    P = [(X0 + 50 + (W_ - 100) * x, Y0 + 40 + (H_ - 90) * y) for x, y in pts]
    d = 'M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in P)
    area = d + f' L{P[-1][0]:.0f} {Y0 + H_ - 50} L{P[0][0]:.0f} {Y0 + H_ - 50}Z'
    tela = (f'<rect x="{X0 - 26}" y="{Y0 - 26}" width="{W_ + 52}" height="{H_ + 52}" rx="22" fill="#1E2A3A"/>'
            f'<rect x="{X0}" y="{Y0}" width="{W_}" height="{H_}" rx="6" fill="#F3EEDF"/>'
            + ''.join(f'<path d="M{X0 + 40} {Y0 + 40 + k * (H_ - 90) / 4:.0f} L{X0 + W_ - 30} {Y0 + 40 + k * (H_ - 90) / 4:.0f}" stroke="#C9BEA6" stroke-width="2" stroke-dasharray="6 8"/>' for k in range(5))
            + f'<path d="M{X0 + 40} {Y0 + 30} L{X0 + 40} {Y0 + H_ - 50} L{X0 + W_ - 30} {Y0 + H_ - 50}" stroke="#2A2A2A" stroke-width="4" fill="none"/>'
            f'<path id="{w}-ar" d="{area}" fill="{cor}" opacity="0"/>'
            f'<path id="{w}-ln" d="{d}" stroke="{cor}" stroke-width="10" fill="none" stroke-linejoin="round" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1"/>'
            f'<g id="{w}-pt"><circle r="16" fill="{cor}"/><circle r="30" fill="{cor}" opacity=".25"/></g>'
            f'<rect id="{w}-al" x="{X0}" y="{Y0}" width="{W_}" height="{H_}" rx="6" fill="#E0573E" opacity="0"/>')
    base = (f'<path d="M{X0 - 90} 1500 L{X0 + W_ + 90} 1500 L{X0 + W_ + 150} 1600 L{X0 - 150} 1600Z" fill="#B9BFC4"/>'
            f'<rect x="{X0 - 150}" y="1596" width="{W_ + 300}" height="16" rx="6" fill="#8A8F96"/>'
            + ''.join(f'<rect x="{X0 - 40 + 52 * k}" y="{1516 + 24 * j}" width="44" height="16" rx="3" fill="#8A8F96"/>' for j in range(3) for k in range(15))
            + f'<rect x="{X0 + 220}" y="1588" width="240" height="6" rx="3" fill="#8A8F96"/>')
    mesa = '<rect x="-300" y="1590" width="1680" height="400" fill="#8A6A45"/><rect x="-300" y="1590" width="1680" height="14" fill="#6B4E31"/>'
    dur = max(0.8, min(2.4, t1 - tl_ - 0.3))
    c.a(f"tl.fromTo('#{w}-ln',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{dur:.2f},ease:'power1.inOut'}},{q(tl_)});")
    c.a(f"tl.to('#{w}-ar',{{opacity:0.16,duration:{dur:.2f}}},{q(tl_)});")
    c.a(f"tl.set('#{w}-pt',{{x:{P[0][0]:.0f},y:{P[0][1]:.0f}}},{q(c.t0)});")
    seg = dur / max(1, len(P) - 1)
    for k in range(1, len(P)):
        c.a(f"tl.to('#{w}-pt',{{x:{P[k][0]:.0f},y:{P[k][1]:.0f},duration:{seg:.2f},ease:'none'}},{q(tl_ + seg * (k - 1))});")
    c.a(f"tl.fromTo('#{w}-pt',{{scale:1}},{{scale:1.3,duration:0.3,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.3))},ease:'sine.inOut'}},{q(c.t0)});")
    an.som(tl_, 'riser' if sobe else 'sub', 0.14)
    if not sobe:
        ta = _T(alerta) if alerta is not None else tl_ + dur
        c.a(f"tl.fromTo('#{w}-al',{{opacity:0}},{{opacity:0.22,duration:0.25,yoyo:true,repeat:{max(1, int((t1 - ta) / 0.25))},ease:'steps(1)'}},{q(ta)});")
    extra = f'<g transform="translate(110 1640) scale(1.7)">{bo._xicara(0, 0, w + "-v")}</g>'
    bo._vapor(c, w + '-v', c.t0, t1)
    if celular:
        extra += (f'<g transform="translate(940 1700)"><g id="{w}-cel"><rect x="-44" y="-80" width="88" height="160" rx="14" fill="#1E2A3A" transform="rotate(70)"/>'
                  f'<rect x="-34" y="-68" width="68" height="136" rx="6" fill="#FFF6D8" transform="rotate(70)" id="{w}-ct"/></g></g>')
        c.a(f"tl.fromTo('#{w}-cel',{{x:-3}},{{x:3,duration:0.05,yoyo:true,repeat:{max(1, int((t1 - t - 0.8) / 0.05))},ease:'none'}},{q(t + 0.8)});")
        an.som(t + 0.8, 'tique2', 0.2)
    if maos:
        pele = bo._visual()[0]
        maos_ = ''.join(f'<g transform="translate({x} 1640)"><g id="{w}-m{k}"><ellipse cx="0" cy="0" rx="62" ry="38" fill="{pele}"/>'
                        f'<rect x="-50" y="20" width="100" height="300" rx="40" fill="#2D4A63"/></g></g>' for k, x in enumerate((420, 660)))
        extra += maos_
        for k in range(2):
            c.a(f"tl.fromTo('#{w}-m{k}',{{y:0}},{{y:-10,duration:{0.11 + 0.02 * k:.2f},yoyo:true,repeat:{max(1, int((t1 - t) / 0.11))},ease:'sine.inOut'}},{q(t)});")
        an.som(t + 0.2, 'digitando', 0.08)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{mesa}{tela}{base}{extra}</g>')


# ================================================================ CAIXA REGISTRADORA (close)
def caixa_registradora(c, t, t_abre=None, notas=True):
    """Close da caixa registradora antiga (chapada): teclas afundando uma a uma, a gaveta abre (sino) e as notas e
    moedas saltam; a fita do recibo vai saindo por cima. Sem número no visor."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cx')
    ta = _T(t_abre) if t_abre is not None else t + 1.0
    X, Y = 200, 1120
    alt_ft = 150   # 08/11: a fita do recibo sobe menos (antes 280: passava por cima do letreiro)
    corpo_ = (f'<rect x="{X}" y="{Y + 140}" width="680" height="380" rx="26" fill="#B5523B"/>'
              f'<rect x="{X + 20}" y="{Y + 150}" width="640" height="24" rx="10" fill="#C96A52"/>'
              f'<path d="M{X + 60} {Y + 140} L{X + 140} {Y - 10} L{X + 540} {Y - 10} L{X + 620} {Y + 140}Z" fill="#8E3F2C"/>'
              f'<rect x="{X + 200}" y="{Y - 110}" width="280" height="110" rx="12" fill="#2A2A2A"/>'
              f'<rect x="{X + 216}" y="{Y - 96}" width="248" height="80" rx="6" fill="#8FE0B0" id="{w}-vis"/>'
              + ''.join(f'<rect class="{w}-dg" x="{X + 236 + 42 * k}" y="{Y - 76}" width="26" height="40" rx="4" fill="#2F6A4A" opacity=".85"/>' for k in range(5)))
    teclas = ''
    for j in range(3):
        for k in range(6):
            teclas += (f'<g transform="translate({X + 140 + 70 * k + 14 * j} {Y + 10 + 42 * j})"><g class="{w}-tc">'
                       f'<rect x="-24" y="-16" width="48" height="30" rx="8" fill="#F4EFE6"/><rect x="-24" y="10" width="48" height="6" rx="3" fill="#C9BEA6"/></g></g>')
    gav = (f'<g id="{w}-gv"><rect x="{X + 40}" y="{Y + 360}" width="600" height="140" rx="10" fill="#7E3526"/>'
           f'<rect x="{X + 60}" y="{Y + 372}" width="560" height="70" rx="6" fill="#3A1A12"/>'
           + ''.join(f'<rect x="{X + 80 + 110 * k}" y="{Y + 380}" width="96" height="54" rx="4" fill="#7FB08A"/>' for k in range(3))
           + ''.join(f'<circle cx="{X + 440 + 50 * k}" cy="{Y + 410}" r="20" fill="#F2B544"/>' for k in range(3))
           + f'<rect x="{X + 280}" y="{Y + 460}" width="120" height="18" rx="9" fill="#C9A24A"/></g>')
    fita = f'<rect id="{w}-ft" x="{X + 520}" y="{Y - 60}" width="90" height="10" fill="#FBF6EA"/>'
    c.a(f"tl.fromTo('.{w}-tc',{{y:0}},{{y:10,duration:0.08,yoyo:true,repeat:1,stagger:{{each:0.19,from:'random'}}}},{q(t)});")
    c.a(f"tl.fromTo('.{w}-dg',{{opacity:0.15}},{{opacity:0.9,duration:0.1,stagger:0.18,ease:'steps(1)'}},{q(t + 0.1)});")
    an.som(t + 0.05, 'madeira', 0.18)
    c.a(f"tl.fromTo('#{w}-gv',{{y:0}},{{y:150,duration:0.28,ease:'back.out(1.6)'}},{q(ta)});")
    an.som(ta, 'glock', 0.3)
    c.a(f"tl.fromTo('#{w}-ft',{{attr:{{y:{Y - 60},height:10}}}},{{attr:{{y:{Y - 50 - alt_ft},height:{alt_ft}}},duration:{max(0.8, t1 - t - 0.3):.2f},ease:'power1.out'}},{q(t + 0.3)});")
    nt = ''
    if notas:
        gn = f'{w}-n'
        nt = (f'<g id="{gn}">' + ''.join(
            f'<g transform="translate({X + 320} {Y + 560})"><g class="nt"><rect x="-44" y="-22" width="88" height="44" rx="5" fill="#7FB08A"/>'
            f'<rect x="-34" y="-14" width="68" height="28" rx="3" fill="none" stroke="#3F7F55" stroke-width="3"/><circle r="9" fill="#3F7F55"/></g></g>'
            for _ in range(6)) + '</g>')
        rep = max(0, int((t1 - ta - 0.2) / 1.3))
        c.a(f"tl.fromTo('#{gn} .nt',{{x:0,y:0,opacity:0,rotation:0}},{{x:(i)=>[-300,220,-140,320,-240,120][i%6],y:(i)=>[-430,-380,-470,-350,-400,-450][i%6],opacity:1,rotation:(i)=>[-120,140,-60,170,-90,60][i%6],"
            f"duration:1.3,ease:'power2.out',repeat:{rep},stagger:{{each:0.2,repeat:{rep}}}}},{q(ta + 0.1)});")
    pele = bo._visual()[0]
    mao = (f'<g transform="translate(980 {Y + 120})"><g id="{w}-mao"><rect x="-10" y="-20" width="300" height="80" rx="38" fill="#2D4A63"/>'
           f'<ellipse cx="-10" cy="20" rx="56" ry="40" fill="{pele}"/><rect x="-80" y="0" width="70" height="26" rx="13" fill="{pele}"/></g></g>')
    c.a(f"tl.fromTo('#{w}-mao',{{x:0,y:0}},{{x:-30,y:16,duration:0.19,yoyo:true,repeat:{max(1, int((ta - t) / 0.19))},ease:'sine.inOut'}},{q(t)});")
    c.a(f"tl.to('#{w}-mao',{{x:80,y:-20,duration:0.4}},{q(ta + 0.05)});")
    sombra = f'<ellipse cx="{X + 340}" cy="{Y + 540}" rx="420" ry="30" fill="#000" opacity=".2"/>'
    _entra_amb(c, w, t)
    # 08/11 (margem segura): a caixa inteira (fita, visor, corpo, gaveta aberta) encaixa abaixo do letreiro e acima do pé
    # do formato; a mão que vem da borda direita vai junto (ela pode sangrar)
    return _amb(c, bo.encaixa(f'<g id="{w}">{sombra}{fita}{gav}<g id="{w}-cx">{corpo_}{teclas}</g>{nt}{mao}</g>', (X - 20, Y - 60 - alt_ft, X + 700, Y + 560)))


# ================================================================ CARTEIRA (close das mãos)
def carteira(c, t, modo='esvazia', t_fim=None):
    """Close das duas mãos segurando a carteira aberta. esvazia: as notas saem voando uma a uma e no fim sai uma
    mariposa (carteira vazia); enche: as notas chegam voando e a carteira estufa."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'ca')
    tf = _T(t_fim) if t_fim is not None else max(t + 1.2, t1 - 1.0)
    pele = bo._visual()[0]
    # 08/11 (margem segura): a carteira (de cy-40 a cy+190) fica inteira acima do pé do formato (RL 1470)
    cx, cy = 540, min(1430, bo.faixa()[1] - 190)
    cart = (f'<g transform="translate({cx} {cy})"><g id="{w}-c">'
            f'<path d="M-260 -40 L0 -10 L0 190 L-260 160Z" fill="#6B3E1E"/><path d="M260 -40 L0 -10 L0 190 L260 160Z" fill="#7A4A26"/>'
            f'<path d="M-240 -20 L-10 6 L-10 120 L-240 96Z" fill="#4A2A12"/><path d="M240 -20 L10 6 L10 120 L240 96Z" fill="#4A2A12"/>'
            f'<path d="M-250 30 l40 -4 l40 4 l40 -4 l40 4" stroke="#8A5A30" stroke-width="4" fill="none"/></g></g>')
    maos = ''.join(f'<g transform="translate({cx + s * 270} {cy + 90}) scale({s} 1)"><ellipse cx="0" cy="0" rx="70" ry="96" fill="{pele}"/>'
                   + ''.join(f'<rect x="-86" y="{-60 + 32 * k}" width="60" height="26" rx="13" fill="{bo._esc(pele, 0.94)}"/>' for k in range(4))
                   + f'<rect x="10" y="40" width="120" height="700" rx="50" fill="#2D4A63"/></g>' for s in (-1, 1))
    n = 6
    notas = ''.join(f'<g transform="translate({cx - 120 + 46 * k} {cy - 10})"><g class="{w}-nt"><rect x="-70" y="-110" width="140" height="70" rx="5" fill="#7FB08A"/>'
                    f'<rect x="-58" y="-98" width="116" height="46" rx="3" fill="none" stroke="#3F7F55" stroke-width="3"/><circle cx="0" cy="-75" r="12" fill="#3F7F55"/></g></g>'
                    for k in range(n))
    if modo == 'esvazia':
        per = max(0.25, (tf - t) / n)
        c.a(f"tl.fromTo('.{w}-nt',{{x:0,y:0,rotation:0,opacity:1}},{{x:(i)=>[-560,520,-460,580,-600,480][i%6],y:(i)=>[-380,-300,-420,-340,-260,-400][i%6],rotation:(i)=>[-200,160,-90,220,-140,100][i%6],opacity:0,"
            f"duration:0.9,ease:'power2.out',stagger:{per:.2f}}},{q(t)});")
        an.som(t, 'papel', 0.2)
        mar = (f'<g transform="translate({cx} {cy})"><g id="{w}-mr" opacity="0"><ellipse cx="0" cy="0" rx="8" ry="20" fill="#5A4A3A"/>'
               f'<g class="{w}-as"><path d="M0 -6 Q-50 -50 -46 6 Q-30 20 0 4Z" fill="#B9A88A"/><path d="M0 -6 Q50 -50 46 6 Q30 20 0 4Z" fill="#B9A88A"/></g></g></g>')
        c.a(f"tl.fromTo('#{w}-mr',{{opacity:0,x:0,y:0}},{{opacity:1,x:160,y:-420,duration:{max(0.8, t1 - tf):.2f},ease:'sine.inOut'}},{q(tf)});")
        c.a(f"tl.fromTo('.{w}-as',{{scaleY:1}},{{scaleY:0.2,duration:0.12,yoyo:true,repeat:{max(1, int((t1 - tf) / 0.12))},svgOrigin:'0 0'}},{q(tf)});")
        an.som(tf, 'swish', 0.14)
    else:
        mar = ''
        per = max(0.25, (tf - t) / n)
        c.a(f"tl.fromTo('.{w}-nt',{{x:(i)=>[-560,520,-460,580,-600,480][i%6],y:(i)=>[-380,-300,-420,-340,-260,-400][i%6],rotation:(i)=>[-200,160,-90,220,-140,100][i%6],opacity:0}},"
            f"{{x:0,y:0,rotation:0,opacity:1,duration:0.6,ease:'power2.out',stagger:{per:.2f}}},{q(t)});")
        c.a(f"tl.fromTo('#{w}-c',{{scaleY:1}},{{scaleY:1.12,duration:{max(0.5, tf - t):.2f},ease:'power1.in',svgOrigin:'0 190'}},{q(t)});")
        an.som(t, 'glock', 0.18)
    c.a(f"tl.fromTo('#{w}-tudo',{{y:0}},{{y:-10,duration:1.2,ease:'sine.inOut',yoyo:true,repeat:{max(1, int((t1 - t) / 1.2))}}},{q(t)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}"><g id="{w}-tudo">{notas}{cart}{maos}{mar}</g></g>')


# ================================================================ CELULAR NA MÃO (close, com notificações empilhando)
def celular_mao(c, t, notifs=(), t_vibra=None):
    """Mão grande segurando o celular de baixo pra cima; as notificações entram empilhando na tela (cartão com ícone
    e texto curto ≥ 48 px) e o polegar toca. notifs=[('Lead novo', t, 'ponto'|'ok'|'ia'), ...] (até 4)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cm')
    pele = bo._visual()[0]
    X, Y, W_, H_ = 290, 1000, 500, 980
    cel = (f'<rect x="{X}" y="{Y}" width="{W_}" height="{H_}" rx="60" fill="#1E2A3A"/>'
           f'<rect x="{X + 22}" y="{Y + 24}" width="{W_ - 44}" height="{H_ - 40}" rx="42" fill="#EDE6D4" id="{w}-tela"/>'
           f'<rect x="{X + W_ / 2 - 50:.0f}" y="{Y + 36}" width="100" height="22" rx="11" fill="#1E2A3A"/>')
    cards = ''
    for k, n_ in enumerate(list(notifs)[:4]):
        txt, tk, ic_ = n_[0], _T(n_[1]), (n_[2] if len(n_) > 2 else 'ponto')
        tam = 48
        while _txt_larg(txt.upper(), tam) > W_ - 170 and tam > 40:
            tam -= 2
        cid = f'{w}-n{k}'
        y = Y + 90 + 150 * k
        icn = {'ok': '<circle cx="0" cy="0" r="24" fill="#3F7F55"/><path d="M-11 0 l8 8 l14 -15" stroke="#fff" stroke-width="5" fill="none"/>',
               'ia': '<circle r="26" fill="#2A2416"/><path d="M0 -18 L5 -5 L18 0 L5 5 L0 18 L-5 5 L-18 0 L-5 -5Z" fill="#F2B544"/>',
               'ponto': '<circle r="24" fill="#B5523B"/><circle r="9" fill="#FBF6EA"/>'}.get(ic_, '')
        cards += (f'<g transform="translate({X + 44} {y})"><g id="{cid}"><rect width="{W_ - 88}" height="124" rx="22" fill="#FBF6EA"/>'
                  f'<rect width="{W_ - 88}" height="124" rx="22" fill="none" stroke="#D8CDB5" stroke-width="3"/>'
                  f'<g transform="translate(50 62)">{icn}</g>'
                  f'<text class="tc" x="96" y="{62 + tam * 0.36:.0f}" font-size="{tam}" fill="#1E2A3A">{_html.escape(txt.upper())}</text></g></g>')
        c.a(f"tl.fromTo('#{cid}',{{opacity:0,y:-40}},{{opacity:1,y:0,duration:0.32,ease:'back.out(1.8)'}},{q(tk)});")
        an.som(tk, 'tique2', 0.24)
    mao = (f'<g transform="translate(780 1680)"><ellipse cx="0" cy="0" rx="110" ry="150" fill="{pele}"/>'
           f'<rect x="-30" y="80" width="200" height="400" rx="80" fill="#B5523B"/></g>'
           f'<g transform="translate(300 1640)">' + ''.join(f'<rect x="-40" y="{-70 + 52 * k}" width="80" height="44" rx="22" fill="{pele}"/>' for k in range(4)) + '</g>'
           f'<g transform="translate(720 1560)"><g id="{w}-pol"><rect x="-30" y="-140" width="60" height="170" rx="30" fill="{bo._esc(pele, 0.95)}" transform="rotate(-28)"/></g></g>')
    tv = _T(t_vibra) if t_vibra is not None else t + 0.2
    c.a(f"tl.fromTo('#{w}-pol',{{x:0,y:0}},{{x:-40,y:-30,duration:0.25,yoyo:true,repeat:{max(1, int((t1 - t) / 0.5))},repeatDelay:0.25,ease:'sine.inOut'}},{q(t)});")
    c.a(f"tl.fromTo('#{w}-cel',{{rotation:-6}},{{rotation:-4,duration:1.3,yoyo:true,repeat:{max(1, int((t1 - t) / 1.3))},ease:'sine.inOut',svgOrigin:'540 1900'}},{q(t)});")
    c.a(f"tl.fromTo('#{w}-ond',{{opacity:0,scale:0.8}},{{opacity:1,scale:1.2,duration:0.4,repeat:{max(1, int((t1 - tv) / 0.8))},repeatDelay:0.4,svgOrigin:'540 1000'}},{q(tv)});")
    ond = (f'<g id="{w}-ond" fill="none" stroke="#F2B544" stroke-width="7" stroke-linecap="round" opacity="0">'
           '<path d="M240 1040 Q200 990 240 940"/><path d="M200 1060 Q140 990 200 920"/><path d="M840 1040 Q880 990 840 940"/><path d="M880 1060 Q940 990 880 920"/></g>')
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{ond}<g id="{w}-cel">{cel}{cards}</g>{mao}</g>')


# ================================================================ VÁRIOS CELULARES COM A MESMA PERGUNTA (12/11/2026)
_PERGUNTAS = ('Quanto custa?', 'Qual o preço?', 'Quanto $$$?', 'Ainda tem?', 'Quanto custa?', 'Qual o valor?')


def _quebra2(txt, tam, larg_max):
    """Texto em até 2 linhas (caixa alta) com a linha mais larga ≤ larg_max; encolhe até 40 px se precisar."""
    tx = txt.upper()
    pal = tx.split()
    opc = [[tx]] + [[' '.join(pal[:k]), ' '.join(pal[k:])] for k in range(1, len(pal))]
    while True:
        larg = [(max(_txt_larg(l_, tam) for l_ in ls), ls) for ls in opc]
        cabem = [(len(ls), lg, ls) for lg, ls in larg if lg <= larg_max]
        if cabem:
            return min(cabem, key=lambda x: (x[0], x[1]))[2], tam
        if tam <= 40:
            return min(larg, key=lambda x: x[0])[1], tam
        tam -= 2


def _vibra(sel, t, amp, n):
    """Celular vibrando: n batidas de ±amp graus em 0,05 s e volta a 0. tl.to com keyframes (vários fromTo no mesmo
    alvo dão "repeated_fromto_without_baseline" no hyperframes check)."""
    ks = ','.join(str(amp if k % 2 else -amp) for k in range(n)) + ',0'
    return f"tl.to({sel},{{keyframes:{{rotation:[{ks}]}},duration:{0.05 * (n + 1):.2f},ease:'none',transformOrigin:'50% 50%'}},{q(t)});"


def celulares_pergunta(c, t, perguntas=_PERGUNTAS, tempos=None, t_todos=None, passo=0.285, vol=0.1):
    """Vários celulares (6) caindo um após o outro, bem rápido, espalhados em 2 fileiras que se sobrepõem (a de baixo por
    cima), cada um com uma conversa aberta e uma pergunta de cliente num balão (2 linhas, 48 px): "Quanto custa?", "Qual o
    preço?"... Cada um vibra, ganha a bolinha vermelha e toca um plim leve quando a pergunta chega; t_todos = todos vibram
    juntos (ex.: no "100 vezes"); depois seguem flutuando e vibrando de vez em quando. Encaixado na caixa segura abaixo do
    letreiro (bo.encaixa). Pedido do usuário no caso real ("responde a mesma pergunta 100 vezes"). Tempos em índice ou s."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'kz')
    n = min(6, len(perguntas))
    tempos = [_T(x) for x in tempos] if tempos else [t + passo * k for k in range(n)]
    W_, H_ = 246, 400
    corpos = ('#1E2A3A', '#F6EBD3', '#2D4A63', '#C9A24A', '#3F6B4E', '#5A4126')
    topos = ('#2D4A63', '#3F6B4E', '#7E3526', '#3B4E5E', '#2D4A63', '#5B7F6E')
    peles = ('#E8B48F', '#C68A62', '#8D5A3B', '#F1C9A5', '#B07A52', '#D9A07A')
    # ordem no desenho = fileira de cima e depois a de baixo (a de baixo cobre só a parte vazia das de cima); a ordem de
    # ENTRADA é espalhada (esq. em cima, meio embaixo, dir. em cima...)
    Y = 900
    lugares = [(290, Y + 215, -7), (790, Y + 222, 6), (540, Y + 200, -2),
               (300, Y + 480, 5), (780, Y + 486, -6), (540, Y + 470, 3)][:n]
    ordem = [0, 5, 1, 3, 2, 4][:n] if n == 6 else list(range(n))
    quando = {i: tempos[k] for k, i in enumerate(ordem)}
    sx0, sy0 = -W_ / 2 + 12, -H_ / 2 + 16          # canto da tela
    sw, sh = W_ - 24, H_ - 32
    tel = []
    xs, ys = [], []
    for i, (cx, cy, rot) in enumerate(lugares):
        tk = quando[i]
        pid = f'{w}-{i}'
        linhas, tam = _quebra2(perguntas[i % len(perguntas)], 48, sw - 20 - 32)
        bw = max(_txt_larg(l_, tam) for l_ in linhas) + 32
        # entrelinha 1,34 em: a caixa da fonte (ascendente 48 + descendente 15 a 48 px) não pode encostar na da linha de
        # baixo — com 1,06 o hyperframes check dava content_overlap (erro que trava o render)
        passo_l = tam * 1.34
        bh = 14 + tam * 0.86 + (len(linhas) - 1) * passo_l + tam * 0.36
        bx, by = sx0 + 10, sy0 + 64 + 18
        # um <text> só com as linhas em <tspan>. As 2 linhas do MESMO balão num celular inclinado (e vibrando) têm caixas
        # retas que se cruzam — o hyperframes check acusava content_overlap (falso: é a mesma pergunta em 2 linhas) e
        # travava o render; data-layout-allow-overlap é a marca dele pra camada intencional
        txt = (f'<text class="tc" font-size="{tam}" fill="#1E2A3A">'
               + ''.join(f'<tspan x="16" y="{14 + tam * 0.86 + j * passo_l:.0f}" data-layout-allow-overlap="">{_html.escape(l_)}</tspan>'
                         for j, l_ in enumerate(linhas))
               + '</text>')
        bal = (f'<g transform="translate({bx:.0f} {by:.0f})"><g id="{pid}-b">'
               f'<rect x="0" y="5" width="{bw:.0f}" height="{bh:.0f}" rx="20" fill="#000" opacity=".10"/>'
               f'<path d="M14 0 L-12 -4 L4 22Z" fill="#FFFFFF"/>'
               f'<rect width="{bw:.0f}" height="{bh:.0f}" rx="20" fill="#FFFFFF"/>{txt}</g></g>')
        dy_ = by + bh + 16
        digi = (f'<g transform="translate({bx:.0f} {dy_:.0f})"><g id="{pid}-d" opacity="0"><rect width="74" height="34" rx="17" fill="#FFFFFF"/>'
                + ''.join(f'<circle class="{pid}-dp" cx="{20 + 17 * j}" cy="17" r="5.5" fill="#8A8F96"/>' for j in range(3)) + '</g></g>')
        corpo_ = corpos[i % len(corpos)]
        claro = corpo_ in ('#F6EBD3', '#C9A24A')
        hd = topos[i % len(topos)]
        fone = (f'<rect x="{-W_ / 2}" y="{-H_ / 2 + 14}" width="{W_}" height="{H_}" rx="36" fill="#000" opacity=".22"/>'
                f'<rect x="{-W_ / 2}" y="{-H_ / 2}" width="{W_}" height="{H_}" rx="36" fill="{corpo_}"/>'
                f'<rect x="{-W_ / 2 + 2}" y="{-H_ / 2 + 2}" width="{W_ - 4}" height="{H_ - 4}" rx="34" fill="none" stroke="{"#5A4126" if claro else "#F6EBD3"}" stroke-width="3" opacity=".3"/>'
                f'<rect x="{sx0}" y="{sy0}" width="{sw}" height="{sh}" rx="24" fill="#EDE6D4"/>'
                f'<path d="M{sx0} {sy0 + 64} V{sy0 + 24} Q{sx0} {sy0} {sx0 + 24} {sy0} H{sx0 + sw - 24} Q{sx0 + sw} {sy0} {sx0 + sw} {sy0 + 24} V{sy0 + 64}Z" fill="{hd}"/>'
                f'<rect x="-28" y="{sy0 + 6}" width="56" height="12" rx="6" fill="{corpo_ if not claro else "#1E2A3A"}"/>'
                f'<g transform="translate({sx0 + 34} {sy0 + 40})"><circle r="19" fill="#F6EBD3"/><circle cy="-4" r="7.5" fill="{peles[i % len(peles)]}"/>'
                f'<path d="M-12 13 Q0 1 12 13Z" fill="{peles[i % len(peles)]}"/></g>'
                f'<rect x="{sx0 + 62}" y="{sy0 + 28}" width="96" height="12" rx="6" fill="#F6EBD3" opacity=".85"/>'
                f'<rect x="{sx0 + 62}" y="{sy0 + 46}" width="58" height="8" rx="4" fill="#F6EBD3" opacity=".5"/>'
                f'<rect x="{sx0 + 10}" y="{sy0 + sh - 52}" width="{sw - 70}" height="40" rx="20" fill="#FFFFFF"/>'
                f'<circle cx="{sx0 + sw - 30}" cy="{sy0 + sh - 32}" r="20" fill="{hd}"/>'
                f'<path d="M{sx0 + sw - 38} {sy0 + sh - 40} L{sx0 + sw - 20} {sy0 + sh - 32} L{sx0 + sw - 38} {sy0 + sh - 24}Z" fill="#F6EBD3"/>'
                f'{bal}{digi}'
                f'<g id="{pid}-bd" opacity="0"><circle cx="{W_ / 2 - 8}" cy="{-H_ / 2 + 8}" r="22" fill="#D2462F" stroke="#F6EBD3" stroke-width="4"/></g>')
        ondas = (f'<g id="{pid}-o" fill="none" stroke="#F2B544" stroke-width="6" stroke-linecap="round" opacity="0">'
                 f'<path d="M{-W_ / 2 - 14} -40 Q{-W_ / 2 - 30} 0 {-W_ / 2 - 14} 40"/><path d="M{W_ / 2 + 14} -40 Q{W_ / 2 + 30} 0 {W_ / 2 + 14} 40"/></g>')
        # grupos: de fora parado (lugar), -m anda em y (queda + flutua), -v gira (vibra), -f escala (entra) — GSAP nunca
        # escala e move no mesmo <g> (armadilha 3) nem anima x/y num <g> com transform (armadilha 2)
        tel.append(f'<g transform="translate({cx} {cy}) rotate({rot})"><g id="{pid}-m"><g id="{pid}-v">{ondas}'
                   f'<g id="{pid}-f" data-imp="kz">{fone}</g></g></g></g>')
        c.a(f"tl.fromTo('#{pid}-m',{{y:-70}},{{y:0,duration:0.28,ease:'power2.out'}},{q(tk)});")
        c.a(f"tl.fromTo('#{pid}-f',{{opacity:0,scale:0.6,transformOrigin:'50% 50%'}},{{opacity:1,scale:1,duration:0.3,ease:'back.out(1.6)',transformOrigin:'50% 50%'}},{q(tk)});")
        tb = tk + 0.08
        c.a(f"tl.fromTo('#{pid}-b',{{opacity:0,scale:0.3,transformOrigin:'0% 0%'}},{{opacity:1,scale:1,duration:0.26,ease:'back.out(2)',transformOrigin:'0% 0%'}},{q(tb)});")
        c.a(f"tl.fromTo('#{pid}-bd',{{opacity:0,scale:0.2,transformOrigin:'50% 50%'}},{{opacity:1,scale:1,duration:0.22,ease:'back.out(3)',transformOrigin:'50% 50%'}},{q(tb + 0.04)});")
        c.a(_vibra(f"'#{pid}-v'", tb, 3, 6))
        c.a(f"tl.to('#{pid}-o',{{keyframes:{{opacity:[1,0.2,1,0]}},duration:0.32,ease:'none'}},{q(tb)});")
        an.som(tb, 'glock', vol)
        # cliente digitando de novo (os 3 pontinhos) e o celular flutuando devagar até o fim da cena
        td = tb + 0.5
        if td < t1 - 0.3:
            c.a(f"tl.to('#{pid}-d',{{opacity:1,duration:0.15}},{q(td)});")
            c.a(f"tl.fromTo('.{pid}-dp',{{opacity:0.25}},{{opacity:1,duration:0.2,yoyo:true,repeat:{max(1, int((t1 - td) / 0.2))},stagger:0.1}},{q(td)});")
        tf = tk + 0.32
        if tf < t1 - 0.4:
            c.a(f"tl.to('#{pid}-m',{{y:{-8 if i % 2 else 8},duration:0.9,ease:'sine.inOut',yoyo:true,repeat:{max(1, int((t1 - tf) / 0.9))}}},{q(tf)});")
        # caixa do que importa (corpo + bolinha + pico do back.out e da vibração)
        a_ = math.radians(abs(rot) + 4)
        hw = (W_ / 2 * math.cos(a_) + H_ / 2 * math.sin(a_)) * 1.05 + 14
        hh = (H_ / 2 * math.cos(a_) + W_ / 2 * math.sin(a_)) * 1.05 + 14
        xs += [cx - hw, cx + hw]
        ys += [cy - hh - 8, cy + hh + 8]
    if t_todos is not None:   # "100 vezes": todos vibram juntos
        tt = _T(t_todos)
        ids = ','.join(f"'#{w}-{i}-v'" for i in range(n))
        c.a(_vibra(f'[{ids}]', tt, 4, 10))
        ons = ','.join(f"'#{w}-{i}-o'" for i in range(n))
        c.a(f"tl.to([{ons}],{{keyframes:{{opacity:[1,0.2,1,0.2,1,0]}},duration:0.5,ease:'none'}},{q(tt)});")
        an.som(tt + 0.1, 'glock', vol + 0.04)
        # e depois, de vez em quando, um deles vibra de novo (a tela nunca para)
        for k, i in enumerate(ordem[:3]):
            tv = tt + 0.7 + 0.35 * k
            if tv < t1 - 0.3:
                c.a(_vibra(f"'#{w}-{i}-v'", tv, 2.5, 6))
    svg = f'<g id="{w}">{"".join(tel)}</g>'
    return _amb(c, bo.encaixa(svg, (min(xs), min(ys), max(xs), max(ys))))


# ================================================================ AGENDA / CALENDÁRIO (close)
def agenda(c, t, modo='riscando', n=10, tempos=None, mes='', dias=None):
    """Calendário de parede grande. modo 'riscando' = um X vermelho por dia, rápido (o tempo passando); 'marcando' =
    caneta circulando dias (compromissos marcados, tempos = quando cada um); 'folhas' = bloquinho de folhas arrancadas
    voando (dias passando). mes = nome do mês só se ele FALOU. dias = quais dias marcar (padrão: seguidos)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'ag')
    X, Y, W_, H_ = 170, 980, 740, 820
    out = [f'<rect x="{X + 10}" y="{Y + 14}" width="{W_}" height="{H_}" rx="10" fill="#000" opacity=".16"/>',
           f'<rect x="{X}" y="{Y}" width="{W_}" height="{H_}" rx="10" fill="#FBF6EA"/>',
           f'<rect x="{X}" y="{Y}" width="{W_}" height="130" rx="10" fill="#B5523B"/>']
    out.append(''.join(f'<rect x="{X + 60 + 90 * k}" y="{Y - 30}" width="16" height="60" rx="8" fill="#5A5F66"/>' for k in range(8)))
    if mes:
        out.append(f'<text class="tc" x="{X + W_ / 2:.0f}" y="{Y + 92}" text-anchor="middle" font-size="64" fill="#FBF6EA">{_html.escape(mes.upper())}</text>')
    else:
        out.append(f'<rect x="{X + 230}" y="{Y + 52}" width="280" height="26" rx="13" fill="#FBF6EA" opacity=".85"/>')
    cw, ch = W_ / 7, (H_ - 160) / 5
    pos_ = {}
    for d in range(1, 32):
        i = d + 2
        col, lin = i % 7, i // 7
        if lin > 4:
            break
        x, y = X + cw * col, Y + 150 + ch * lin
        pos_[d] = (x + cw / 2, y + ch / 2)
        if modo == 'folhas':
            continue   # o bloquinho cobre a grade (e o check acusava texto sobreposto)
        out.append(f'<rect x="{x + 4:.0f}" y="{y + 4:.0f}" width="{cw - 8:.0f}" height="{ch - 8:.0f}" rx="6" fill="#F1E8D4"/>'
                   f'<text class="tc" x="{x + cw / 2:.0f}" y="{y + ch / 2 + 17:.0f}" text-anchor="middle" font-size="48" fill="#3A2A1A">{d}</text>')
    dias = list(dias or range(3, 3 + n))
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.25 + (max(0.6, t1 - t - 0.6) / max(1, len(dias))) * k for k in range(len(dias))]
    marcas = ''
    for k, (d, tk) in enumerate(zip(dias, ts_)):
        if d not in pos_:
            continue
        x, y = pos_[d]
        mid = f'{w}-x{k}'
        if modo == 'marcando':
            marcas += f'<ellipse id="{mid}" cx="{x:.0f}" cy="{y:.0f}" rx="{cw / 2 - 4:.0f}" ry="{ch / 2 - 6:.0f}" fill="none" stroke="#2D4A63" stroke-width="7" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>'
            c.a(f"tl.to('#{mid}',{{strokeDashoffset:0,duration:0.35,ease:'power1.inOut'}},{q(tk)});")
            an.som(tk, 'tique', 0.16)
        else:
            r = min(cw, ch) / 2 - 10
            marcas += (f'<path id="{mid}" d="M{x - r:.0f} {y - r:.0f} L{x + r:.0f} {y + r:.0f} M{x + r:.0f} {y - r:.0f} L{x - r:.0f} {y + r:.0f}" stroke="#B03A2A" '
                       f'stroke-width="9" stroke-linecap="round" fill="none" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>')
            c.a(f"tl.to('#{mid}',{{strokeDashoffset:0,duration:0.18,ease:'power1.out'}},{q(tk)});")
            if k % 2 == 0:
                an.som(tk, 'tique2', 0.12)
    folhas = ''
    if modo == 'folhas':
        folhas = ''.join(f'<g transform="translate({X + W_ / 2:.0f} {Y + 470})"><g class="{w}-fl"><rect x="-300" y="-320" width="600" height="640" rx="8" fill="#FBF6EA"/>'
                         f'<rect x="-300" y="-320" width="600" height="110" rx="8" fill="#2D4A63"/>'
                         f'<text class="tg" x="0" y="140" text-anchor="middle" font-size="300" fill="#3A2A1A">{d}</text></g></g>' for d in range(n + 2, 1, -1))
        per = max(0.25, (t1 - t - 0.5) / n)
        c.a(f"tl.to('.{w}-fl',{{x:(i)=>[-900,900,-860,880,-920,900][i%6],y:(i)=>[160,-40,220,0,180,60][i%6],rotation:(i)=>[-30,25,-35,30,-20,35][i%6],duration:0.7,ease:'power2.in',stagger:{{each:{per:.2f},from:'end'}}}},{q(t + 0.2)});")
        # 08/11 (margem segura): a folha arrancada some ANTES de chegar na borda (o número dela não sai cortado da tela)
        c.a(f"tl.to('.{w}-fl',{{opacity:0,duration:0.18,ease:'none',stagger:{{each:{per:.2f},from:'end'}}}},{q(t + 0.2)});")
        an.som(t + 0.2, 'papel', 0.22)
    caneta = ''
    if modo == 'marcando':
        caneta = (f'<g id="{w}-cn"><g transform="rotate(30)"><rect x="-10" y="-180" width="22" height="170" rx="8" fill="#2D4A63"/>'
                  f'<path d="M-10 -10 L12 -10 L1 18Z" fill="#1E2A3A"/></g></g>')
        for k, (d, tk) in enumerate(zip(dias, ts_)):
            if d in pos_:
                x, y = pos_[d]
                c.a(f"tl.to('#{w}-cn',{{x:{x + 20:.0f},y:{y + 10:.0f},duration:0.25,ease:'power2.inOut'}},{q(max(c.t0, tk - 0.25))});")
                c.a(f"tl.to('#{w}-cn',{{rotation:20,duration:0.12,yoyo:true,repeat:1,svgOrigin:'{x + 20:.0f} {y + 10:.0f}'}},{q(tk)});")
        d0 = dias[0] if dias[0] in pos_ else 3
        c.a(f"tl.set('#{w}-cn',{{x:{pos_[d0][0] + 200:.0f},y:{pos_[d0][1] + 300:.0f}}},{q(c.t0)});")
    c.a(f"tl.fromTo('#{w}-cal',{{rotation:-1.2}},{{rotation:1.2,duration:1.6,yoyo:true,repeat:{max(1, int((t1 - t) / 1.6))},ease:'sine.inOut',svgOrigin:'540 {Y - 20}'}},{q(t)});")
    _entra_amb(c, w, t)
    # 08/11 (margem segura): o calendário inteiro encaixa abaixo do letreiro e acima do pé do formato
    return _amb(c, bo.encaixa(f'<g id="{w}"><g id="{w}-cal">{"".join(out)}{marcas}</g>{folhas}{caneta}</g>', (X - 10, Y - 40, X + W_ + 20, Y + H_ + 20)))


# ================================================================ ENTREGADOR (rua)
def entregador(c, t, t_chega=None, t_entrega=None, texto='Entregue', cliente=True):
    """A van de entrega chega e estaciona, o entregador desce com a caixa e leva até a porta; o cliente recebe e
    acena; balão ✓ (texto). Cenário 'rua' (ou 'rua_tarde', 'transito')."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'en')
    rnd = random.Random(_seed(c.id) + 71)
    tc = _T(t_chega) if t_chega is not None else t + 0.1
    te = _T(t_entrega) if t_entrega is not None else min(t1 - 0.6, tc + 2.2)
    van = (f'<g id="{w}-van"><g transform="translate(-520 1820) scale(2.3)">{af.caminhao(0, 0, "#2D4A63", 1.0, 1)}</g></g>')
    c.a(f"tl.fromTo('#{w}-van',{{x:0}},{{x:720,duration:{max(0.6, min(1.4, te - tc - 1.0)):.2f},ease:'power2.out'}},{q(tc)});")
    an.som(tc, 'whoosh_lento', 0.14)
    pid = f'{w}-e'
    xe0 = 330
    ent = pos(corpo(pid, 'carrega', item='caixa', roupa='#C9A24A', calca='#3B4A5E', cracha=True, rnd=rnd), xe0, 1700, 0.98)
    t_sai = tc + max(0.6, min(1.4, te - tc - 1.0))
    c.a(f"tl.fromTo('#{w}-ew',{{opacity:0}},{{opacity:1,duration:0.2}},{q(t_sai)});")
    anda(c, pid, t_sai, (800 - xe0) / 0.98, max(0.6, te - t_sai - 0.1), bracos=False)
    vive(c, pid, t, t1)
    cli = ''
    if cliente:
        cid = f'{w}-c'
        cli = pos(corpo(cid, 'em_pe', rnd=rnd), 930, 1660, 0.92, -1)
        vive(c, cid, t, t1, fala=True)
        respira(c, cid, t, t1)
        muda_pose(c, cid, 'em_pe', 'acena', te)
        gesticula(c, cid, te + 0.45, t1, 'j-bfa', 18, 0.3)
    porta = ('<rect x="860" y="1300" width="170" height="380" fill="#5A3E28"/><rect x="876" y="1316" width="138" height="160" fill="#BFDCE6"/>'
             '<circle cx="1000" cy="1520" r="8" fill="#C9A24A"/><rect x="840" y="1676" width="210" height="14" fill="#8A7E6A"/>')
    bid = f'{w}-bl'
    bal = _balao(bid, _bx(700, texto, 48, 50), 1180, texto, icone='ok')
    _pop_balao(c, bid, te, 'tique2')
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{porta}{cli}<g id="{w}-ew" opacity="0">{ent}</g>{van}{bal}</g>')


# ================================================================ BALCÃO (loja / café)
def balcao(c, t, t_paga=None, sacola=True, baloes=()):
    """Balcão de atendimento: atendente atrás do balcão, cliente entra e para; na hora de pagar a gaveta da caixa abre,
    a nota sai e o recibo cresce; a sacola desliza pro cliente. Cenário 'loja' (ou 'cafe')."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'bc')
    rnd = random.Random(_seed(c.id) + 72)
    tp = _T(t_paga) if t_paga is not None else min(t1 - 0.8, t + 1.6)
    aid = f'{w}-a'
    at = pos(corpo(aid, 'mostra', roupa='#5B7F6E', rnd=rnd), 800, 1700, 1.05, -1)
    vive(c, aid, t, t1, fala=True)
    respira(c, aid, t, t1)
    cid = f'{w}-c'
    cli = pos(corpo(cid, 'anda', item=None, rnd=rnd), -160, 1860, 1.12)
    anda(c, cid, t + 0.05, (330 + 160) / 1.12, max(0.6, min(1.5, tp - t - 0.2)))
    vive(c, cid, t, t1)
    muda_pose(c, cid, 'anda', 'mostra', tp - 0.3)
    bal_ = ('<rect x="420" y="1470" width="700" height="34" rx="6" fill="#8A6A45"/><rect x="440" y="1504" width="660" height="300" fill="#6B4E31"/>'
            '<rect x="440" y="1504" width="660" height="14" fill="#5A3E28"/>' + ''.join(f'<rect x="{x}" y="1540" width="8" height="240" fill="#5A3E28"/>' for x in range(500, 1100, 120)))
    caixa = (f'<g transform="translate(580 1470)"><rect x="-80" y="-120" width="160" height="120" rx="10" fill="#3B4E5E"/>'
             f'<rect x="-60" y="-104" width="120" height="44" rx="4" fill="#8FE0B0"/><g id="{w}-gv"><rect x="-90" y="-20" width="180" height="26" rx="4" fill="#2D3A4F"/></g>'
             f'<rect id="{w}-rc" x="30" y="-130" width="40" height="8" fill="#FBF6EA"/></g>')
    c.a(f"tl.fromTo('#{w}-gv',{{x:0}},{{x:-60,duration:0.25,ease:'back.out(2)'}},{q(tp)});")
    c.a(f"tl.fromTo('#{w}-rc',{{attr:{{y:-130,height:8}}}},{{attr:{{y:-300,height:178}},duration:{max(0.5, t1 - tp - 0.2):.2f},ease:'power1.out'}},{q(tp)});")
    an.som(tp, 'glock', 0.26)
    sac = ''
    if sacola:
        sac = (f'<g transform="translate(760 1470)"><g id="{w}-sc"><path d="M-60 0 L60 0 L50 -150 L-50 -150Z" fill="#C49A62"/>'
               f'<path d="M-26 -150 Q0 -200 26 -150" stroke="#8A5A2B" stroke-width="7" fill="none"/></g></g>')
        c.a(f"tl.fromTo('#{w}-sc',{{x:0}},{{x:-250,duration:0.5,ease:'power2.out'}},{q(tp + 0.5)});")
    bal = ''
    for k, b in enumerate(baloes):
        txt, tb, ic_ = b[0], _T(b[1]), (b[2] if len(b) > 2 else '')
        bid = f'{w}-bl{k}'
        bal += _balao(bid, _bx(560, txt, 48, 50 if ic_ else 0), 1130 - 110 * k, txt, icone=ic_)
        _pop_balao(c, bid, tb)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{at}{bal_}{caixa}{sac}{cli}{bal}</g>')


# ================================================================ REUNIÃO EM PÉ (quadro de tarefas)
def reuniao_em_pe(c, t, t_move=None, n=3, ok=True):
    """Reunião rápida em pé em volta do quadro de tarefas (3 colunas de post-its, sem palavra): um post-it atravessa
    da 1ª pra última coluna e ganha ✓; o time balança a cabeça, um aponta. Cenário 'escritorio'/'escritorio2'/'reuniao'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'rp')
    rnd = random.Random(_seed(c.id) + 73)
    tm = _T(t_move) if t_move is not None else t + 0.8
    QX, QY, QW, QH = 330, 1000, 420, 420
    quadro = (f'<rect x="{QX - 14}" y="{QY - 14}" width="{QW + 28}" height="{QH + 28}" rx="8" fill="#8A8F96"/>'
              f'<rect x="{QX}" y="{QY}" width="{QW}" height="{QH}" fill="#FBFAF5"/>'
              + ''.join(f'<rect x="{QX + QW * k / 3 - 2:.0f}" y="{QY + 20}" width="4" height="{QH - 40}" fill="#D8D3C6"/>' for k in (1, 2))
              + f'<rect x="{QX + 40}" y="{QY + QH + 14}" width="14" height="{1720 - QY - QH - 14}" fill="#5A5F66"/><rect x="{QX + QW - 54}" y="{QY + QH + 14}" width="14" height="{1720 - QY - QH - 14}" fill="#5A5F66"/>'
              + '<g fill="#8A8F96"><circle cx="{0}" cy="{1}" r="16"/></g>'.format(QX + 70, QY + 44)
              + f'<path d="M{QX + 205} {QY + 44} l30 0 l-10 -10 m10 10 l-10 10" stroke="#8A8F96" stroke-width="6" fill="none"/>'
              f'<path d="M{QX + 335} {QY + 44} l10 10 l20 -20" stroke="#3F7F55" stroke-width="7" fill="none"/>')
    cores = ('#F2D46B', '#F2A58A', '#9FD3E6', '#B9DDA0')
    notas = ''
    for col in range(3):
        for j in range(2):
            x = QX + 22 + QW * col / 3 + rnd.uniform(-4, 4)
            y = QY + 90 + 100 * j
            notas += f'<rect x="{x:.0f}" y="{y:.0f}" width="96" height="84" fill="{rnd.choice(cores)}" transform="rotate({rnd.uniform(-5, 5):.1f} {x + 48:.0f} {y + 42:.0f})"/>'
    mv = (f'<g transform="translate({QX + 22} {QY + 290})"><g id="{w}-pi"><rect width="96" height="84" fill="#F2D46B"/>'
          f'<path id="{w}-ck" d="M24 44 l14 14 l30 -30" stroke="#3F7F55" stroke-width="9" fill="none" stroke-linecap="round" opacity="0"/></g></g>')
    c.a(f"tl.to('#{w}-pi',{{keyframes:{{x:[0,140,{QW * 2 / 3:.0f}],y:[0,-200,-0]}},duration:0.9,ease:'power1.inOut'}},{q(tm)});")
    c.a(f"tl.to('#{w}-pi',{{rotation:8,duration:0.45,yoyo:true,repeat:1,svgOrigin:'48 42'}},{q(tm)});")
    if ok:
        c.a(f"tl.to('#{w}-ck',{{opacity:1,duration:0.15}},{q(tm + 0.95)});")
        an.som(tm + 0.95, 'tique2', 0.24)
    an.som(tm, 'papel', 0.18)
    pes = ''
    lugares = ((150, 1, 'aponta'), (930, -1, 'em_pe'), (1010, -1, 'mostra'))[:n]
    for k, (x, d, pose) in enumerate(lugares):
        pid = f'{w}-p{k}'
        pes += pos(corpo(pid, pose, item='tablet' if pose == 'mostra' else ('cafe' if k == 1 else None), rnd=rnd), x, 1760 if k < 2 else 1880, 1.0 if k < 2 else 1.1, d)
        vive(c, pid, t, t1, fala=k == 0)
        respira(c, pid, t, t1)
        if pose == 'aponta':
            gesticula(c, pid, t, t1, 'j-bf', 5, 0.5)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{quadro}{notas}{mv}{pes}</g>')


# ================================================================ CAFÉ SAINDO DA MÁQUINA
def cafe_maquina(c, t, pessoa=True, t_pega=None):
    """Máquina de espresso grande no balcão: o café escorrendo na xícara, vapor subindo, alguém esperando e pegando a
    xícara (começo do dia, pausa). Cenário 'cafe' ou 'copa'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cm')
    rnd = random.Random(_seed(c.id) + 74)
    tp = _T(t_pega) if t_pega is not None else max(t + 1.2, t1 - 1.0)
    maq = ('<rect x="-300" y="1560" width="1680" height="40" fill="#8A6A45"/><rect x="-300" y="1600" width="1680" height="400" fill="#6B4E31"/>'
           '<rect x="160" y="1060" width="460" height="500" rx="26" fill="#B9BFC4"/><rect x="160" y="1060" width="460" height="90" rx="26" fill="#8A8F96"/>'
           '<rect x="200" y="1180" width="380" height="120" rx="14" fill="#9AA0A6"/>'
           '<circle cx="270" cy="1240" r="28" fill="#2A2A2A"/><circle cx="270" cy="1240" r="14" fill="#E0573E" class="ar-pisca"/>'
           '<rect x="330" y="1220" width="200" height="40" rx="8" fill="#2A2A2A"/>'
           '<rect x="320" y="1320" width="140" height="44" rx="10" fill="#3A3A3A"/><rect x="368" y="1364" width="44" height="30" fill="#3A3A3A"/>'
           '<rect x="200" y="1540" width="380" height="20" rx="6" fill="#5A5F66"/>')
    jato = f'<rect id="{w}-j" x="384" y="1394" width="12" height="90" fill="#6B3E1E"/>'
    c.a(f"tl.fromTo('#{w}-j',{{scaleY:0.2,opacity:1}},{{scaleY:1,duration:0.18,yoyo:true,repeat:{max(1, int((tp - t) / 0.18))},svgOrigin:'390 1394'}},{q(t)});")
    c.a(f"tl.to('#{w}-j',{{opacity:0,duration:0.1}},{q(tp - 0.1)});")
    xi = f'<g transform="translate(390 1500)"><g id="{w}-xi"><g transform="scale(1.8)">{bo._xicara(0, 0, w + "-v")}</g></g></g>'
    bo._vapor(c, w + '-v', t, t1)
    an.som(t, 'shimmer', 0.1)
    p = ''
    if pessoa:
        pid = f'{w}-p'
        p = pos(corpo(pid, 'em_pe', rnd=rnd), 860, 1880, 1.15, -1)
        vive(c, pid, t, t1)
        respira(c, pid, t, t1)
        muda_pose(c, pid, 'em_pe', 'cafe', tp)
        c.a(f"tl.to('#{w}-xi',{{x:330,y:-200,opacity:0,duration:0.4,ease:'power2.in'}},{q(tp)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{maq}{jato}{xi}{p}</g>')


# ================================================================ PRESO NO TRÂNSITO
def transito_preso(c, t, relogio=True, buzina=True, baloes=()):
    """O seu carro (grande, na frente) parado no engarrafamento: motorista batucando, buzina, relógio em cima com os
    ponteiros correndo (o tempo indo embora). Cenário an.cenario(c, 'transito', parado=True)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'tp')
    pele, cab, est, roupa = _vis()
    car = (f'<g transform="translate(540 1900) scale(3.4)">{af.carro(0, 0, "#C9A24A", 1.0, 1)}</g>'
           f'<g transform="translate(560 1764)"><g id="{w}-mot"><circle cx="0" cy="0" r="19" fill="{pele}"/><path d="M-19 -3 Q-19 -22 0 -22 Q19 -22 19 -4 Q9 -14 -19 -3Z" fill="{cab}"/></g></g>')
    c.a(f"tl.fromTo('#{w}-mot',{{y:0}},{{y:-6,duration:0.18,yoyo:true,repeat:{max(1, int((t1 - t) / 0.18))},ease:'sine.inOut'}},{q(t)});")
    c.a(f"tl.fromTo('#{w}-car',{{y:0}},{{y:-4,duration:0.12,yoyo:true,repeat:{max(1, int((t1 - t) / 0.12))},ease:'none'}},{q(t)});")
    ex = ''
    if buzina:
        ex += (f'<g transform="translate(760 1760)"><g id="{w}-bz" fill="none" stroke="#E0573E" stroke-width="8" stroke-linecap="round">'
               '<path d="M0 -20 L40 -50"/><path d="M10 0 L60 0"/><path d="M0 20 L40 50"/></g></g>')
        c.a(f"tl.fromTo('#{w}-bz',{{opacity:0,scale:0.6}},{{opacity:1,scale:1.15,duration:0.2,yoyo:true,repeat:{max(1, int((t1 - t) / 0.7))},repeatDelay:0.3,svgOrigin:'0 0'}},{q(t + 0.3)});")
        an.som(t + 0.3, 'batida', 0.14)
    if relogio:
        ex += f'<g transform="translate(540 1150)"><g id="{w}-rl"><circle r="118" fill="#FBF6EA" opacity=".25"/>{bo._relogio3(0, 0, 100)}</g></g>'
        ex += f'<g transform="translate(540 1150)"><g id="{w}-pn"><rect x="-4" y="-86" width="8" height="86" rx="4" fill="#B03A2A"/></g></g>'
        c.a(f"tl.fromTo('#{w}-pn',{{rotation:0}},{{rotation:{int((t1 - t) * 540)},duration:{q(t1 - t)},ease:'none',svgOrigin:'0 0'}},{q(t)});")
        c.a(f"tl.fromTo('#{w}-rl',{{y:0}},{{y:-12,duration:1,yoyo:true,repeat:{max(1, int(t1 - t))},ease:'sine.inOut'}},{q(t)});")
        an.som(t + 0.1, 'tique', 0.16)
    bal = ''
    for k, b in enumerate(baloes):
        txt, tb, ic_ = b[0], _T(b[1]), (b[2] if len(b) > 2 else 'ponto')
        bid = f'{w}-bl{k}'
        bal += _balao(bid, _bx(540, txt, 48, 50), 1380 - 110 * k, txt, icone=ic_)
        _pop_balao(c, bid, tb)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}"><g id="{w}-car">{car}</g>{ex}{bal}</g>')


# ================================================================ LINHA DE PRODUÇÃO (fábrica)
def fabrica_linha(c, t, ia=None, operario=True):
    """Esteira com caixas passando, prensa batendo, braço robótico pegando e pondo; com ia=t o braço ganha o brilho
    da IA e acelera (automação). Cenário 'fabrica'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'fl')
    rnd = random.Random(_seed(c.id) + 75)
    D = max(0.8, t1 - c.t0)
    est = ('<rect x="-300" y="1640" width="1680" height="60" rx="10" fill="#3A3F46"/><rect x="-300" y="1650" width="1680" height="10" fill="#5A5F66"/>'
           + ''.join(f'<g transform="translate({x} 1670)"><g class="ar-gira" data-v="360" data-o="0 0"><circle r="22" fill="#8A8F96"/><rect x="-3" y="-22" width="6" height="44" fill="#5A5F66"/></g></g>'
                     for x in range(-260, 1400, 120))
           + ''.join(f'<rect x="{x}" y="1700" width="24" height="200" fill="#3A3F46"/>' for x in range(-200, 1400, 300)))
    caixas = ''.join(f'<g transform="translate({x} 1640)"><rect x="-56" y="-100" width="112" height="100" fill="#C49A62"/><rect x="-56" y="-100" width="112" height="14" fill="#A87F4A"/>'
                     f'<rect x="-10" y="-100" width="20" height="100" fill="#E3CDA2" opacity=".7"/></g>' for x in range(-560, 1700, 280))
    v = 220
    c.a(f"tl.fromTo('#{w}-cx',{{x:0}},{{x:{280},duration:{280 / v:.2f},ease:'none',repeat:{max(1, int(D * v / 280))}}},{q(c.t0)});")
    prensa = ('<rect x="300" y="1060" width="40" height="420" fill="#5A646C"/><rect x="560" y="1060" width="40" height="420" fill="#5A646C"/>'
              '<rect x="280" y="1040" width="340" height="60" rx="8" fill="#3B5A6E"/>'
              f'<g id="{w}-pr"><rect x="436" y="1100" width="28" height="260" fill="#8A8F96"/><rect x="370" y="1360" width="160" height="50" rx="6" fill="#B5523B"/></g>')
    c.a(f"tl.fromTo('#{w}-pr',{{y:0}},{{y:120,duration:0.22,ease:'power3.in',yoyo:true,repeat:{max(1, int(D / 0.7))},repeatDelay:0.26}},{q(c.t0)});")
    an.som(c.t0 + 0.22, 'batida', 0.1)
    braco = (f'<g transform="translate(860 1500)"><rect x="-60" y="0" width="120" height="140" rx="10" fill="#E9B53A"/>'
             f'<g id="{w}-b1"><rect x="-22" y="-240" width="44" height="250" rx="20" fill="#E9B53A"/><circle cy="0" r="34" fill="#C99A2A"/>'
             f'<g transform="translate(0 -240)"><g id="{w}-b2"><circle r="26" fill="#C99A2A"/><rect x="-18" y="-10" width="200" height="36" rx="16" fill="#E9B53A"/>'
             f'<g transform="translate(190 8)"><path d="M0 0 L26 -24 M0 0 L26 24" stroke="#5A5F66" stroke-width="10" stroke-linecap="round"/></g>'
             f'<g id="{w}-ia" opacity="0" transform="translate(80 -40)"><circle r="34" fill="#F2B544" opacity=".3"/><path d="M0 -24 L7 -7 L24 0 L7 7 L0 24 L-7 7 L-24 0 L-7 -7Z" fill="#F2B544"/></g>'
             f'</g></g></g></g>')
    per = 1.1
    c.a(f"tl.fromTo('#{w}-b1',{{rotation:-25}},{{rotation:25,duration:{per / 2},yoyo:true,repeat:{max(1, int(D / (per / 2)))},ease:'sine.inOut',svgOrigin:'0 0'}},{q(c.t0)});")
    c.a(f"tl.fromTo('#{w}-b2',{{rotation:30}},{{rotation:80,duration:{per / 2},yoyo:true,repeat:{max(1, int(D / (per / 2)))},ease:'sine.inOut',svgOrigin:'0 0'}},{q(c.t0)});")
    if ia is not None:
        ti = _T(ia)
        c.a(f"tl.to('#{w}-ia',{{opacity:1,duration:0.3}},{q(ti)});")
        c.a(f"tl.fromTo('#{w}-ia',{{rotation:0}},{{rotation:360,duration:1.2,repeat:{max(1, int((t1 - ti) / 1.2))},ease:'none',svgOrigin:'0 0'}},{q(ti)});")
        an.som(ti, 'shimmer', 0.2)
    op_ = ''
    if operario:
        pid = f'{w}-o'
        op_ = pos(corpo(pid, 'mostra', item='tablet', roupa='#3B5A6E', rnd=rnd), 110, 1880, 1.08)
        vive(c, pid, t, t1)
        respira(c, pid, t, t1)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{prensa}{braco}{est}<g id="{w}-cx">{caixas}</g>{op_}</g>')


# ================================================================ ESCRITÓRIO ABERTO (plano aberto, muita gente)
def escritorio_aberto(c, t, n=7, tempos=None, ia=False):
    """Plano ABERTO: duas fileiras de mesas pequenas (4 atrás, 3 na frente), as telas acendendo uma a uma (tempos) —
    com ia=True as telas acendem douradas. Cenário 'escritorio'/'escritorio2'/'escritorio_noite'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'ea')
    rnd = random.Random(_seed(c.id) + 76)
    partes = []
    # 08/11 (folha do t61): com 230/330 de passo a cadeira de cada um entrava na mesa do vizinho (o posto inteiro =
    # encosto em x-74·e até o fim da mesa em x+360·e). Agora cada posto cabe no seu passo, com folga.
    lug = [(60 + 255 * k, 1500, 0.55, 1) for k in range(4)] + [(80 + 345 * k, 1800, 0.75, 1) for k in range(3)]
    lug = lug[:n]
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.3 + 0.28 * k for k in range(len(lug))]
    poses = ('digita', 'headset', 'tel_sent', 'digita', 'acena_sent', 'digita', 'headset')
    for k, (x, y, esc, d) in enumerate(lug):
        pid = f'{w}-p{k}'
        g, mx, mon_x = bo._posto(c, pid, x, y, esc, d, poses[k % 7], rnd, tela='ia' if ia else 'linhas', xicara=k % 3 == 0,
                                 headset=poses[k % 7] == 'headset')
        partes.append(g)
        vive(c, pid, t, t1, fala=poses[k % 7] in ('headset', 'tel_sent'))
        if poses[k % 7] in ('digita', 'headset'):
            digita(c, pid, t + 0.1 * k, t1)
        c.a(f"tl.fromTo('#{pid}-mon .scr',{{opacity:0.15}},{{opacity:1,duration:0.2,ease:'steps(2)'}},{q(ts_[k])});")
        if ia:
            c.a(f"tl.fromTo('#{pid}-mon .iag',{{opacity:0}},{{opacity:0.7,duration:0.4,yoyo:true,repeat:{max(1, int((t1 - ts_[k]) / 0.8))}}},{q(ts_[k])});")
        an.som(ts_[k], 'tique', 0.1)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(partes)}</g>')


# ================================================================ PRÉDIO EM CORTE (casa de bonecas)
def predio_corte(c, t, andares=(('Marketing', 'digita'), ('Comercial', 'telefone'), ('Operação', 'caixa')), tempos=None, ia=None, rotulos=True):
    """Prédio em CORTE (como a vista em corte da referência): 3 andares, cada um com gente fazendo uma coisa, as luzes
    acendendo andar por andar (tempos) com a etiqueta do setor; ia=t = a estrela da IA sobe pelo poço do elevador e
    acende cada andar. Ação por andar: digita, telefone, headset, caixa (anda carregando), cafe, reuniao. Cenário 'corte'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'pc')
    rnd = random.Random(_seed(c.id) + 77)
    ts_ = [_T(x) for x in tempos] if tempos else [t + 0.3 + 0.6 * k for k in range(len(andares))]
    partes, sombras, etq = [], '', ''
    for k, ((rot, acao), (y0, y1)) in enumerate(zip(andares, af.andares())):
        esc = 0.5 if y1 - y0 >= 260 else 0.44   # 08/11: andar mais baixo no RL (af.ANDARES_RL)
        pid = f'{w}-p{k}'
        if acao in ('digita', 'headset', 'tel_sent', 'preocupado'):
            g, _, _ = bo._posto(c, pid, 380, y1 - 4, esc, 1, acao, rnd, xicara=False, headset=acao == 'headset')
            partes.append(g)
            if acao in ('digita', 'headset'):
                digita(c, pid, t, t1)
        elif acao == 'caixa':
            partes.append(pos(corpo(pid, 'carrega', item='caixa', rnd=rnd), 200, y1 - 4, esc))
            anda(c, pid, t + 0.2, 1100, max(1.0, t1 - t - 0.2), bracos=False)
        elif acao == 'reuniao':
            partes.append(pos(corpo(pid, 'aponta', rnd=rnd), 330, y1 - 4, esc) + pos(corpo(pid + 'b', 'em_pe', rnd=rnd), 640, y1 - 4, esc, -1))
            vive(c, pid + 'b', t, t1)
        else:   # telefone / cafe / celular em pé
            partes.append(pos(corpo(pid, acao if acao in bo.POSES else 'telefone', item='celular' if acao in ('telefone', 'celular') else ('cafe' if acao == 'cafe' else None), rnd=rnd),
                              420, y1 - 4, esc))
            gesticula(c, pid, t, t1, 'j-bt', 8, 0.6)
        vive(c, pid, t, t1, fala=acao in ('telefone', 'headset'))
        # segunda pessoa passando no andar (vida)
        p2 = f'{w}-q{k}'
        partes.append(pos(corpo(p2, ('cafe', 'pasta', 'papel')[k % 3] if k % 3 != 2 else 'anda', item=('cafe', 'pasta', None)[k % 3], rnd=rnd), 980, y1 - 4, esc * 0.96, -1))
        anda(c, p2, t + 0.3 * k, 260 / (esc * 0.96), max(1.0, t1 - t - 0.5), bracos=k % 3 == 2)
        vive(c, p2, t, t1)
        sid = f'{w}-s{k}'
        sombras += f'<rect id="{sid}" x="110" y="{y0}" width="860" height="{y1 - y0}" fill="#0A0F1E" opacity=".55"/>'
        c.a(f"tl.to('#{sid}',{{opacity:0,duration:0.3,ease:'power1.out'}},{q(ts_[k])});")
        an.som(ts_[k], 'tique2', 0.16)
        if rotulos and rot:
            eid = f'{w}-e{k}'
            etq += _etiqueta(_bx(720, rot, 48), y0 + 92, rot, 48, '#2D4A63', '#FBF6EA', rot=0, eid=eid)
            c.a(f"tl.fromTo('#{eid} .bp',{{opacity:0,scale:0.5,transformOrigin:'50% 50%'}},{{opacity:1,scale:1,duration:0.3,ease:'back.out(2)',transformOrigin:'50% 50%'}},{q(ts_[k] + 0.1)});")
    ia_ = ''
    if ia is not None:
        ti = _T(ia)
        ia_ = (f'<g id="{w}-ia" opacity="0"><circle r="34" fill="#F2B544" opacity=".3"/><path d="M0 -24 L7 -7 L24 0 L7 7 L0 24 L-7 7 L-24 0 L-7 -7Z" fill="#F2B544"/></g>')
        AND = af.andares()
        c.a(f"tl.set('#{w}-ia',{{x:930,y:{AND[-1][1] - 20}}},{q(c.t0)});tl.to('#{w}-ia',{{opacity:1,duration:0.2}},{q(ti)});")
        c.a(f"tl.to('#{w}-ia',{{y:{AND[0][0] + 70},duration:{max(0.8, t1 - ti - 0.3):.2f},ease:'power1.inOut'}},{q(ti)});")
        c.a(f"tl.fromTo('#{w}-ia',{{rotation:0}},{{rotation:360,duration:1.4,repeat:{max(1, int((t1 - ti) / 1.4))},ease:'none'}},{q(ti)});")
        an.som(ti, 'shimmer', 0.2)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(partes)}{sombras}{etq}{ia_}</g>')


# ================================================================ CONTRALUZ (silhuetas indo pra porta clara)
def contraluz(c, t, n=2, nomes=(), t_anda=None):
    """Silhuetas escuras andando pelo corredor em direção à porta iluminada (encolhendo com a distância), com o nome
    em cima de cada uma (opcional, ≥ 48 px). Metáfora de passo seguinte / decisão / reunião. Cenário 'tunel'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cl')
    rnd = random.Random(_seed(c.id) + 78)
    ta = _T(t_anda) if t_anda is not None else t + 0.1
    D = max(1.0, t1 - ta)
    out = [f'<defs>{SILH}</defs>']
    for k in range(n):
        pid = f'{w}-p{k}'
        x0 = (330, 760, 560)[k % 3]
        y0 = 1900
        silh = corpo(pid, 'anda', pele='#140E0B', cabelo='#140E0B', roupa='#140E0B', calca='#140E0B', rnd=rnd)
        out.append(f'<g transform="translate({x0} {y0})"><g id="{pid}-m"><g id="{pid}-s"><g filter="url(#arsilh)">'
                   f'{pos(silh, 0, 0, 1.25, 1 if x0 < 540 else -1)}</g></g></g></g>')
        c.a(f"tl.fromTo('#{pid}-m',{{x:0,y:0}},{{x:{(540 - x0) * 0.7:.0f},y:{-300 - 30 * k},duration:{D:.2f},ease:'power1.out'}},{q(ta)});")
        c.a(f"tl.fromTo('#{pid}-s',{{scale:1}},{{scale:0.5,duration:{D:.2f},ease:'power1.out',svgOrigin:'0 0'}},{q(ta)});")
        anda(c, pid, ta + 0.1 * k, 0, D)
        if k < len(nomes) and nomes[k]:
            eid = f'{w}-e{k}'
            out.append(f'<g transform="translate({x0} {y0 - 690})"><g id="{eid}-m">'
                       f'<text class="tc" x="0" y="0" text-anchor="middle" font-size="52" fill="#FBF6EA" stroke="#140E0B" stroke-width="8" style="paint-order:stroke">{_html.escape(nomes[k].upper())}</text>'
                       f'<rect x="-60" y="14" width="120" height="4" fill="#F2B544"/></g></g>')
            c.a(f"tl.fromTo('#{eid}-m',{{opacity:0,x:0,y:0}},{{opacity:1,x:{(540 - x0) * 0.7:.0f},y:{(-300 - 30 * k) + 690 * 0.5:.0f},duration:{D:.2f},ease:'power1.out'}},{q(ta)});")
    an.som(ta, 'whoosh_lento', 0.12)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}</g>')


# ================================================================ JANTAR EM FAMÍLIA (vida)
def familia_jantar(c, t, celular=True, t_olha=None):
    """Mesa de jantar em casa. REFEITA em 08/11/2026: o usuário reprovou a v1 (caso real) — gente com a cabeça abaixo do
    tampo, um senhor pequeno "sentado embaixo da mesa", pernas da mesa atravessando as pessoas.

    Geometria (adultos na escala E, chão das pessoas em F):
      - tampo a ~200·E do chão (≈ 75 cm pra um adulto sentado de ≈ 130 cm): ombros ~70 px ACIMA do tampo, cabeça inteira acima;
      - 2 sentados ATRÁS da mesa (tronco e cabeça acima do tampo, pernas escondidas pela toalha comprida, pés no chão)
        + 1 em cada PONTA (corpo inteiro de perfil na cadeira, pés no chão, joelho entrando embaixo da toalha);
      - pernas da mesa só nos cantos, fora de qualquer corpo; cadeiras na mesma escala das pessoas;
      - a criança senta numa almofada alta (escala 0,82, sem óculos/barba/careca): nunca um adulto em miniatura.
    celular=True: o dono (ponta da esquerda) está no celular com a tela piscando e todo mundo vira o rosto pra ele.
    Cenário 'casa' (de dia) ou 'sala_noite'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'fj')
    rnd = random.Random(_seed(c.id) + 79)
    F, E = 1770, 1.12                     # chão das pessoas e escala dos adultos
    X0, X1 = 300, 780                     # mesa de frente (toalha) de X0 a X1
    YF = F + 30                           # pé da mesa (um pouco à frente das pessoas)
    TOPO = F - round(200 * E)             # borda da frente do tampo (~1546)
    FUNDO = TOPO - 30                     # borda de trás do tampo (vista de leve de cima)
    BAIXA = YF - 64                       # fim da toalha comprida (os pés aparecem embaixo)
    # ---- cadeiras (atrás de tudo), mesma escala dos adultos
    def cadeira(x, d):   # cadeira de jantar de madeira (assento na altura do quadril sentado: 114 do chão)
        return (f'<g transform="translate({x} {F}) scale({E * d:.3f} {E})">'
                '<rect x="-74" y="-330" width="18" height="330" rx="6" fill="#5A3E28"/><rect x="-80" y="-336" width="30" height="14" rx="6" fill="#6B4E31"/>'
                '<rect x="-70" y="-290" width="12" height="150" fill="#6B4E31"/>'
                '<rect x="-74" y="-124" width="132" height="18" rx="6" fill="#7A5A3A"/>'
                '<rect x="40" y="-108" width="14" height="108" fill="#5A3E28"/><rect x="-68" y="-108" width="14" height="108" fill="#5A3E28"/></g>')
    XS = {'d': 175, 'a': 440, 'k': 650, 'b': 905}
    cads = ''.join(cadeira(XS[k], d) for k, d in (('d', 1), ('a', -1 if celular else 1), ('k', -1), ('b', -1)))
    # ---- pessoas
    dono, a2, kid, a4 = f'{w}-d', f'{w}-a', f'{w}-k', f'{w}-b'
    pes = [
        pos(corpo(dono, 'cel_sent' if celular else 'come_ponta', item='celular' if celular else 'garfo', rnd=rnd), XS['d'], F, E, 1),
        pos(corpo(a2, 'come_sent', item='garfo', rnd=rnd), XS['a'], F, E, -1 if celular else 1),
        pos(corpo(kid, 'come_sent', item='garfo', estilo=rnd.choice(('cacheado', 'coque', 'curto')), oculos=False, barba=False,
                  roupa=rnd.choice(('#E0A030', '#5B9BD5', '#D9644A', '#6FAF7A')), rnd=rnd), XS['k'], F - 70, 0.82, -1),
        pos(corpo(a4, 'come_ponta', item='garfo', rnd=rnd), XS['b'], F, E, -1),
    ]
    # ---- mesa: tampo em leve perspectiva + toalha comprida + pernas só nos cantos
    ondas = ' '.join(f'Q{X1 - (k + 0.5) * (X1 - X0) / 8:.0f} {BAIXA + 12} {X1 - (k + 1) * (X1 - X0) / 8:.0f} {BAIXA}' for k in range(8))
    mesa = (f'<ellipse cx="{(X0 + X1) / 2:.0f}" cy="{YF + 4}" rx="{(X1 - X0) / 2 + 60:.0f}" ry="16" fill="#000" opacity=".14"/>'
            f'<rect x="{X0 + 14}" y="{BAIXA - 10}" width="22" height="{YF - BAIXA + 10}" fill="#5A3E28"/>'
            f'<rect x="{X1 - 36}" y="{BAIXA - 10}" width="22" height="{YF - BAIXA + 10}" fill="#5A3E28"/>'
            f'<path d="M{X0 + 24} {FUNDO} L{X1 - 24} {FUNDO} L{X1} {TOPO} L{X0} {TOPO}Z" fill="#F4EFE6"/>'
            f'<path d="M{X0} {TOPO} L{X1} {TOPO} L{X1 + 6} {BAIXA} {ondas} L{X0 - 6} {BAIXA}Z" fill="#E9E0CC"/>'
            f'<rect x="{X0}" y="{TOPO}" width="{X1 - X0}" height="8" fill="#D8CDB6"/>'
            + ''.join(f'<rect x="{x}" y="{TOPO + 8}" width="6" height="{BAIXA - TOPO - 14}" fill="#DCD2BC"/>' for x in (X0 + 120, X0 + 240, X0 + 360)))
    # ---- em cima do tampo: pratos, copos, travessa com vapor, vela no meio
    vid = f'{w}-v'
    cima = (''.join(f'<ellipse cx="{x}" cy="{FUNDO + 16}" rx="40" ry="9" fill="#FFFFFF"/><ellipse cx="{x}" cy="{FUNDO + 14}" rx="22" ry="5" fill="{cor}"/>'
                    for x, cor in ((350, '#C98B4A'), (505, '#8DB07A'), (610, '#C98B4A'), (735, '#8DB07A')))
            + f'<g transform="translate(428 {TOPO - 6})"><g class="vapor" id="{vid}" fill="none" stroke="#FFFFFF" stroke-width="4" '
              'stroke-linecap="round" opacity=".7"><path d="M-12 -24 Q-18 -34 -12 -44 Q-6 -54 -12 -64"/><path d="M8 -24 Q2 -34 8 -44 Q14 -54 8 -64"/></g>'
              '<path d="M-40 -16 Q-36 8 0 8 Q36 8 40 -16Z" fill="#B5523B"/><ellipse cx="0" cy="-16" rx="40" ry="8" fill="#D98C5F"/></g>'
            + ''.join(f'<rect x="{x}" y="{FUNDO - 30}" width="18" height="42" rx="5" fill="#BFDCE6" opacity=".85"/>' for x in (468, 690))
            + f'<g transform="translate(552 {FUNDO + 10})"><rect x="-8" y="-50" width="16" height="50" fill="#FBF6EA"/>'
              '<rect x="-18" y="-4" width="36" height="8" rx="3" fill="#C9A24A"/>'
              '<path class="ar-pisca" d="M0 -86 Q12 -66 0 -54 Q-12 -66 0 -86Z" fill="#F2B544"/><circle cy="-68" r="32" fill="#F2B544" opacity=".15"/></g>')
    bo._vapor(c, vid, t, t1)
    # ---- vida: todo mundo respira e pisca; quem come mexe o garfo; um fala
    for p in (dono, a2, kid, a4):
        vive(c, p, t, t1, fala=p == (a2 if celular else a4))
        respira(c, p, t, t1)
    for k, p in enumerate((a2, kid, a4) if celular else (dono, a2, kid, a4)):
        gesticula(c, p, t + 0.25 * k, t1, 'j-bfa', 7, 0.55 + 0.07 * k)
    if celular:
        c.a(f"tl.fromTo('#{dono} .telac',{{fill:'#8FC1D4'}},{{fill:'#FFF6D8',duration:0.25,yoyo:true,repeat:{max(1, int((t1 - t) / 0.25))}}},{q(t)});")
        gesticula(c, dono, t, t1, 'j-bfa', 5, 0.3)
        an.som(t + 0.3, 'tique2', 0.18)
    _entra_amb(c, w, t)
    # as pontas vêm por cima da mesa (mão no tampo; joelho para antes da toalha); os de trás ficam atrás dela
    return _amb(c, f'<g id="{w}">{cads}{pes[1]}{pes[2]}{mesa}{cima}{pes[0]}{pes[3]}</g>')


# ================================================================ PARQUE (vida, tempo livre)
def parque_passeio(c, t, cachorro=True, corredor=True, crianca=True):
    """Fim de semana no parque: o dono passeando com o cachorro, alguém correndo no sentido contrário, criança com
    pipa/balão. Cenário 'parque'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'pq')
    rnd = random.Random(_seed(c.id) + 80)
    D = max(1.0, t1 - t)
    out = []
    pid = f'{w}-d'
    out.append(pos(corpo(pid, 'anda', rnd=rnd), 60, 1760, 1.05))
    anda(c, pid, t, 620 / 1.05, D)
    vive(c, pid, t, t1, fala=True)
    if cachorro:
        out.append(f'<g transform="translate(330 1770) scale(0.8)"><g id="{w}-cao"><ellipse cx="0" cy="-34" rx="80" ry="34" fill="#C9935F"/>'
                   f'<circle cx="76" cy="-62" r="30" fill="#C9935F"/><circle cx="96" cy="-66" r="5" fill="#1E1A16"/><path d="M60 -86 Q48 -62 62 -46Z" fill="#8A5A30"/>'
                   f'<g class="{w}-pa"><rect x="-56" y="-12" width="14" height="40" rx="6" fill="#B07A4A"/><rect x="40" y="-12" width="14" height="40" rx="6" fill="#B07A4A"/></g>'
                   f'<path d="M-80 -40 Q-110 -60 -104 -90" stroke="#C9935F" stroke-width="12" fill="none" stroke-linecap="round" class="{w}-rb"/></g></g>'
                   f'<path id="{w}-gu" d="M260 1520 Q300 1620 340 1700" stroke="#B5523B" stroke-width="4" fill="none"/>')
        c.a(f"tl.fromTo('#{w}-cao',{{x:0}},{{x:620,duration:{D:.2f},ease:'none'}},{q(t)});")
        c.a(f"tl.fromTo('#{w}-gu',{{x:0}},{{x:620,duration:{D:.2f},ease:'none'}},{q(t)});")
        c.a(f"tl.fromTo('#{w}-cao',{{y:0}},{{y:-8,duration:0.15,yoyo:true,repeat:{max(1, int(D / 0.15))}}},{q(t)});")
    if corredor:
        rid = f'{w}-r'
        out.append(pos(corpo(rid, 'anda', roupa='#E0573E', manga='curta', rnd=rnd), 1300, 1660, 0.85, -1))
        anda(c, rid, t + 0.2, 1700 / 0.85, max(1.0, D - 0.2))
        vive(c, rid, t, t1)
    if crianca:
        kid = f'{w}-k'
        out.append(pos(corpo(kid, 'acena', rnd=rnd), 820, 1600, 0.55, -1))
        out.append(f'<g transform="translate(800 1100)"><g id="{w}-bal"><path d="M0 0 C-10 60 10 120 0 230" stroke="#3A3A3A" stroke-width="3" fill="none"/>'
                   f'<ellipse cx="0" cy="-40" rx="44" ry="54" fill="#E0573E"/></g></g>')
        c.a(f"tl.fromTo('#{w}-bal',{{rotation:-8}},{{rotation:8,duration:1.2,yoyo:true,repeat:{max(1, int(D / 1.2))},ease:'sine.inOut',svgOrigin:'0 230'}},{q(t)});")
        gesticula(c, kid, t, t1, 'j-bfa', 16, 0.3)
        vive(c, kid, t, t1)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}</g>')


# ================================================================ VIAGEM (carro com mala na estrada + avião)
def viagem(c, t, aviao=True):
    """Carro com a mala no teto atravessando o campo e o avião cruzando o céu deixando rastro (ficar longe, férias,
    30 dias fora). Cenário 'campo' (ou 'dia')."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'vg')
    D = max(1.0, t1 - c.t0)
    car = (f'<g id="{w}-car"><g transform="translate(-200 1800) scale(2.6)">{af.carro(0, 0, "#B5523B", 1.0, 1)}'
           f'<rect x="-30" y="-66" width="56" height="14" rx="3" fill="#5A3A26"/><rect x="-22" y="-74" width="40" height="10" rx="3" fill="#C9A24A"/></g></g>')
    c.a(f"tl.fromTo('#{w}-car',{{x:0}},{{x:1500,duration:{max(2.0, D * 1.15):.2f},ease:'none'}},{q(c.t0)});")
    c.a(f"tl.fromTo('#{w}-car',{{y:0}},{{y:-5,duration:0.14,yoyo:true,repeat:{max(1, int(D / 0.14))}}},{q(c.t0)});")
    av = ''
    if aviao:
        av = (f'<path id="{w}-rs" d="M1180 300 L-100 420" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round" opacity=".7" pathLength="1" stroke-dasharray="1 1"/>'
              f'<g id="{w}-av"><g transform="scale(-1 1)"><path d="M-60 0 L60 -6 Q80 0 60 6Z" fill="#E9E4D8"/><path d="M-6 -2 L-30 -40 L-14 -40 L20 -2Z" fill="#B9B2A8"/>'
              f'<path d="M-6 2 L-30 40 L-14 40 L20 2Z" fill="#B9B2A8"/><path d="M-56 -2 L-70 -24 L-60 -24 L-44 -2Z" fill="#B5523B"/></g></g>')
        c.a(f"tl.fromTo('#{w}-av',{{x:1180,y:300}},{{x:-100,y:420,duration:{max(2.0, D):.2f},ease:'none'}},{q(c.t0)});")
        c.a(f"tl.fromTo('#{w}-rs',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{max(2.0, D):.2f},ease:'none'}},{q(c.t0)});")
        an.som(c.t0 + 0.2, 'whoosh_lento', 0.12)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{av}{car}</g>')


# ================================================================ PORTO: carga sendo embarcada
def porto_carga(c, t, t_ergue=None, caminhao=True):
    """No píer: o caminhão chega com o contêiner, o guindaste ergue a carga e o trabalhador de capacete sinaliza.
    Escala / expansão / logística. Cenário 'porto'."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'pt')
    rnd = random.Random(_seed(c.id) + 81)
    te = _T(t_ergue) if t_ergue is not None else t + 1.0
    cont = (f'<g transform="translate(880 1460)"><g id="{w}-ct"><path d="M-60 -110 L0 -200 L60 -110" stroke="#2A2A2A" stroke-width="4" fill="none"/>'
            f'<rect x="-90" y="-110" width="180" height="96" fill="#B5523B"/>'
            + ''.join(f'<rect x="{-80 + 20 * k}" y="-102" width="6" height="80" fill="#8E3F2C"/>' for k in range(9)) + '</g></g>')
    c.a(f"tl.fromTo('#{w}-ct',{{y:0,x:0}},{{keyframes:{{y:[0,-360,-360],x:[0,0,-140]}},duration:{max(1.0, t1 - te - 0.2):.2f},ease:'power1.inOut'}},{q(te)});")
    an.som(te, 'riser', 0.12)
    cam = ''
    if caminhao:
        cam = f'<g id="{w}-cm"><g transform="translate(-200 1700) scale(1.8)">{af.caminhao(0, 0, "#5B7F6E", 1.0, 1)}</g></g>'
        c.a(f"tl.fromTo('#{w}-cm',{{x:0}},{{x:620,duration:{max(0.8, te - t):.2f},ease:'power2.out'}},{q(t)});")
    pid = f'{w}-o'
    tr = pos(corpo(pid, 'acena', roupa='#E9B53A', rnd=rnd), 700, 1820, 1.0, -1)
    capacete = ''
    gesticula(c, pid, t, t1, 'j-bfa', 20, 0.35)
    vive(c, pid, t, t1)
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{cont}{cam}{tr}{capacete}</g>')


# ================================================================ CLIMA (camada por cima de tudo)
def clima(c, tipo='chuva', t=None, forca=1.0):
    """Clima por cima da cena (vale com qualquer ambiente): chuva (riscos caindo + poças), neve, folhas (caindo
    girando), sol (raios girando no canto de cima). Leve: o letreiro continua legível."""
    t = c.t0 if t is None else _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cl')
    rnd = random.Random(_seed(c.id) + 82)
    if tipo == 'chuva':
        n = int(70 * forca)
        riscos = ''.join(f'<rect x="{rnd.uniform(-100, 1180):.0f}" y="{rnd.uniform(-200, 1920):.0f}" width="4" height="{rnd.uniform(40, 80):.0f}" rx="2" fill="#DCEBF2" opacity="{rnd.uniform(.25, .5):.2f}" transform="rotate(12)"/>' for _ in range(n))
        pocas = ''.join(f'<ellipse class="{w}-po" cx="{rnd.uniform(120, 960):.0f}" cy="{rnd.uniform(1760, 1880):.0f}" rx="30" ry="6" fill="none" stroke="#DCEBF2" stroke-width="3" opacity=".5"/>' for _ in range(6))
        c.a(f"tl.fromTo('.{w}-po',{{scale:0.2,opacity:0.7}},{{scale:1.6,opacity:0,duration:0.7,repeat:{max(1, int((t1 - t) / 0.7))},stagger:{{each:0.13,repeat:{max(1, int((t1 - t) / 0.7))}}},transformOrigin:'50% 50%'}},{q(t)});")
        an.som(t, 'shimmer', 0.06)
        corpo_ = f'<g class="ar-chuva">{riscos}</g>{pocas}<rect x="-300" y="0" width="1680" height="1920" fill="#2A3A55" opacity=".12"/>'
    elif tipo == 'neve':
        corpo_ = '<g class="ar-neve">' + ''.join(f'<circle cx="{rnd.uniform(-60, 1140):.0f}" cy="{rnd.uniform(-300, 1920):.0f}" r="{rnd.choice((4, 6, 8))}" fill="#FFFFFF" opacity="{rnd.uniform(.5, .9):.2f}"/>' for _ in range(int(60 * forca))) + '</g>'
    elif tipo == 'folhas':
        fol = ''.join(f'<g transform="translate({rnd.uniform(60, 1020):.0f} -60)"><g class="{w}-fo"><path d="M0 -16 Q14 0 0 16 Q-14 0 0 -16Z" fill="{rnd.choice(("#C98B4A", "#B5523B", "#C9A24A"))}"/></g></g>' for _ in range(int(12 * forca)))
        c.a(f"tl.fromTo('.{w}-fo',{{y:0,x:0,rotation:0}},{{y:2000,x:(i)=>[-120,90,-60,140,-30,70][i%6],rotation:(i)=>[540,-420,360,-600,480,-300][i%6],duration:4.5,ease:'none',stagger:{{each:0.4,repeat:{max(1, int((t1 - t) / 4.5) + 1)}}}}},{q(t - 2)});")
        corpo_ = fol
    else:   # sol
        raios = ''.join(f'<rect x="-6" y="-520" width="12" height="260" rx="6" fill="#FFF1C8" opacity=".25" transform="rotate({a})"/>' for a in range(0, 360, 24))
        corpo_ = f'<g transform="translate(940 160)"><g class="ar-gira" data-v="12" data-o="0 0">{raios}</g><circle r="80" fill="#FFF1C8" opacity=".35"/></g>'
    return _amb(c, f'<g id="{w}">{corpo_}</g>')


# ================================================================ PICOTADO: quadros rápidos dentro de uma frase
def picotado(c, quadros):
    """Corta a cena em 2–4 quadros rápidos (ritmo da abertura da referência: planos de 0,5–2 s). quadros = [(t, fn), ...]
    onde fn() desenha UMA cena do arsenal/bonecos na camada de ação desta mesma cena (ex.: lambda: ar.carteira(c, t)).
    Cada quadro fica visível do seu t até o t do próximo, com um corte seco + flash leve."""
    lista = bo.AMB.setdefault(c.id, [])
    grupos = []
    for k, (tq, fn) in enumerate(quadros):
        n0 = len(lista)
        fn()
        novos = lista[n0:]
        del lista[n0:]
        gid = an._id(c, 'pq')
        grupos.append((gid, _T(tq), ''.join(novos)))
    out = ''
    for k, (gid, tq, svg) in enumerate(grupos):
        out += f'<g id="{gid}">{svg}</g>'
        if k:
            c.a(f"tl.set('#{gid}',{{opacity:0}},{q(c.t0)});tl.set('#{gid}',{{opacity:1}},{q(tq)});")
            c.a(f"tl.fromTo('#{gid}',{{scale:1.06}},{{scale:1,duration:0.35,ease:'power2.out',svgOrigin:'540 1500'}},{q(tq)});")
            an.som(tq, 'obturador', 0.14)
        if k + 1 < len(grupos):
            c.a(f"tl.set('#{gid}',{{opacity:0}},{q(grupos[k + 1][1])});")
    return _amb(c, out)


# ================================================================ DE COSTAS (personagem grande em primeiro plano, de costas)
def de_costas(c, t, x=760, roupa=None, cabelo=None):
    """Pessoa GRANDE de costas no canto de baixo olhando a cena (o frade olhando o porto, na referência): dá
    profundidade e põe o espectador no lugar dela. Combine com qualquer ambiente aberto (porto, rua, campo, aereo)."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'dc')
    pele, cab, est, rp = _vis()
    cab = cabelo or cab
    roupa = roupa or rp
    s = 2.6
    corpo_ = (f'<path d="M-170 300 L-160 150 Q-150 70 -70 52 L70 52 Q150 70 160 150 L170 300Z" fill="{roupa}"/>'
              f'<path d="M-70 52 Q0 90 70 52 L60 40 Q0 70 -60 40Z" fill="{bo._esc(roupa, 0.8)}"/>'
              f'<rect x="-22" y="20" width="44" height="40" fill="{bo._esc(pele, 0.85)}"/>'
              f'<ellipse cx="-62" cy="-8" rx="10" ry="16" fill="{pele}"/><ellipse cx="62" cy="-8" rx="10" ry="16" fill="{pele}"/>'
              f'<ellipse cx="0" cy="-10" rx="62" ry="70" fill="{cab}"/>'
              f'<path d="M-58 10 Q0 40 58 10 L56 30 Q0 54 -56 30Z" fill="{bo._esc(cab, 0.85)}"/>')
    c.a(f"tl.fromTo('#{w}-r',{{y:0}},{{y:-6,duration:1.5,ease:'sine.inOut',yoyo:true,repeat:{max(1, int((t1 - t) / 1.5))}}},{q(t)});")
    c.a(f"tl.fromTo('#{w}-cab',{{rotation:-3}},{{rotation:3,duration:2.2,ease:'sine.inOut',yoyo:true,repeat:{max(1, int((t1 - t) / 2.2))},svgOrigin:'0 40'}},{q(t)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}"><g transform="translate({x} {1920 - 300 * s + 40:.0f}) scale({s})"><g id="{w}-r">'
                   f'{corpo_.split("<rect")[0]}<g id="{w}-cab"><rect{corpo_.split("<rect", 1)[1]}</g></g></g></g>')


# ================================================================ CARAVANA (fila de gente cruzando o horizonte)
def caravana(c, t, n=9, silhueta=True, y=1380, esc=0.34, dir_=1):
    """Fila de gente andando em linha pelo horizonte (procissão/caravana da referência): contra o pôr do sol vira
    silhueta. Bom em 'tarde', 'campo_tarde', 'capitulo_vermelho', 'porto_tarde'. O time chegando, a fila de clientes."""
    t = _T(t)
    t1 = _fim(c)
    w = an._id(c, 'cv')
    rnd = random.Random(_seed(c.id) + 83)
    D = max(1.0, t1 - c.t0)
    out = [f'<defs>{SILH}</defs>'] if silhueta else []
    pes = ''
    for k in range(n):
        pid = f'{w}-p{k}'
        kw = dict(pele='#140E0B', cabelo='#140E0B', roupa='#140E0B', calca='#140E0B') if silhueta else {}
        item = ('pasta', 'caixa', None, 'cafe')[k % 4]
        pes += pos(corpo(pid, 'carrega' if item == 'caixa' else 'anda', item=item, rnd=rnd, **kw), (-120 - 95 * k) if dir_ > 0 else (1200 + 95 * k), y, esc, dir_)
        anda(c, pid, c.t0, 0, D)
    out.append(f'<g id="{w}-f"' + (' filter="url(#arsilh)"' if silhueta else '') + f'>{pes}</g>')
    c.a(f"tl.fromTo('#{w}-f',{{x:0}},{{x:{dir_ * (700 + 95 * n) * min(1.0, D / 6):.0f},duration:{D:.2f},ease:'none'}},{q(c.t0)});")
    _entra_amb(c, w, t)
    return _amb(c, f'<g id="{w}">{"".join(out)}</g>')
