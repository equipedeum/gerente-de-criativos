# -*- coding: utf-8 -*-
"""Peças prontas de cena para o motor (hyperframes/motor.py) — os padrões aprovados nos Criativos 22 e 24.

Uso no gerar.py de um vídeo (depois de `from motor import *` e `configurar(...)`):

    from pecas import *
    c = cena(10, 20, 'Loja riscada')
    monta(c, '{64f}você não tem|{104}uma *empresa', linha(c, [ic('storefront', 230, x=14)]))

Tempos: onde uma peça pede um tempo, pode ser um int (índice da palavra → ts(i)) ou um float (segundos).
"""
from motor import (CENAS, ICONES, VERDE, botao, clique, icone, letreiro, miolo, ph_svg, q, svg, ts)  # noqa: F401
import motor as _m


def T(x):
    """Índice de palavra (int) → início dela; float → o próprio tempo."""
    return ts(x) if isinstance(x, int) else float(x)


def monta(c, spec, *partes, sob=False, gap=None, estilo=''):
    """Letreiro + peças, centrado na faixa baixa do painel. sob=True nas cenas sob o título Edits."""
    corpo = (letreiro(c, spec) if spec else '') + ''.join(partes)
    est = (f'gap:{gap}px;' if gap else '') + estilo
    c.html = miolo(corpo, 'sob-titulo' if sob else '', est)
    return c


# ---------------------------------------------------------------- fileira de ícones

def ic(nome, tam=220, cls='', t=None, anim='revela', **fx):
    """Um ícone da fileira. nome = arquivo Phosphor, ou 'IA' (tile verde com chip), 'SELO' (círculo verde com
    visto). anim = revela | pop | entra | desliza. Efeitos (tempos em índice ou s): x=riscar, gira=graus/s
    (+ horário), pulsa=t, quica=t, sai=t (sobe e some), verde=t (fica verde), badge=('9', t) ou ('1→9', t, t_fim)."""
    return dict(nome=nome, tam=tam, cls=cls, t=t, anim=anim, fx=fx)


def linha(c, itens, gap=50, alinhar='center'):
    partes = []
    for k, it in enumerate(itens):
        iid = f'{c.id}-i{k}'
        nome, tam, fx = it['nome'], it['tam'], it['fx']
        t = T(it['t']) if it['t'] is not None else c.t0 + 0.15 + 0.12 * k
        if nome == 'IA':
            html = f'<div class="tile gd" id="{iid}" style="width:{tam}px;height:{tam}px">{svg("ia", int(tam * 0.72))}</div>'
            c.a(f"pop('#{iid}',{q(t)});")
        elif nome == 'SELO':
            html = (f'<div class="selo" id="{iid}" style="position:static;width:{tam}px;height:{tam}px;border-radius:{tam // 2}px">'
                    f'{svg("check", int(tam * 0.64), sw=7, cls="preto")}</div>')
            c.a(f"pop('#{iid}',{q(t)});")
        else:
            html = ph_svg(nome, tam, iid, it['cls'])
            if 'x' in fx:  # ícone riscado: X desenhando por cima
                html = (f'<div id="{iid}-w" style="position:relative;width:{tam}px;height:{tam}px">{html}'
                        f'<svg class="xis" width="{tam}" height="{tam}" viewBox="0 0 64 64" fill="none" stroke="#fff" '
                        f'stroke-width="3" stroke-linecap="round">{ICONES["xis"]}</svg></div>')
                c.a(f"desenha('#{iid}-w .xis .d',{q(T(fx['x']))},0.22,0.08);")
                c.a(f"vai('#{iid}',{{opacity:0.25,duration:0.22}},{q(T(fx['x']))});")
            if 'badge' in fx:
                b = fx['badge']
                html = (f'<div style="position:relative">{html}<div class="badge" id="{iid}-b">'
                        f'<span id="{iid}-bn">{b[0].split("→")[0]}</span></div></div>')
                c.a(f"pop('#{iid}-b',{q(T(b[1]))});")
                if '→' in b[0]:
                    a0, a1 = b[0].split('→')
                    c.a(f"conta('#{iid}-bn',{a0},{a1},{q(T(b[1]))},{q(T(b[2]) - T(b[1]))},'');")
            anim = it['anim']
            if anim == 'revela':
                icone(c, f'#{iid}', t)
            elif anim == 'pop':
                c.a(f"pop('#{iid}',{q(t)});")
            elif anim == 'entra':
                c.a(f"entra('#{iid}',{q(t)});")
            elif anim == 'desliza':
                c.a(f"desliza('#{iid}',{q(t)},-120,0,0.5);")
            if 'gira' in fx:
                vel = fx['gira']
                c.a(f"giraO('#{iid}',0,{round(vel * 6)},{q(t + 0.1)},6,'50% 50%');")  # 6 s cobre a cena
            if 'pulsa' in fx:  # só depois da entrada (pop/entra também mexem na escala)
                tp = max(T(fx['pulsa']), t + 0.35)
                c.a(f"tl.to('#{iid}',{{scale:1.1,duration:0.14,ease:'sine.inOut',yoyo:true,repeat:3,"
                    f"transformOrigin:'50% 50%'}},{q(tp)});")
            if 'quica' in fx:
                c.a(f"quica('#{iid}',{q(T(fx['quica']))},3,-26,0.2,0);")
            if 'sai' in fx:
                c.a(f"vai('#{iid}',{{y:-80,opacity:0,duration:0.45,ease:'power2.in'}},{q(T(fx['sai']))});")
            if 'verde' in fx:
                c.a(f"vai('#{iid}',{{fill:'{VERDE}',duration:0.2}},{q(T(fx['verde']))});")
        partes.append(html)
    return f'<div class="linha" style="gap:{gap}px;align-items:{alinhar}">{"".join(partes)}</div>'


# ---------------------------------------------------------------- widgets

def chip(c, texto, t, mini=False):
    cid = f'{c.id}-chip'
    c.a(f"pop('#{cid}',{q(T(t))});")
    return f'<div class="chip{" mini" if mini else ""}" id="{cid}">{texto}</div>'


def sublinhado(c, t, larg=600):
    c.a(f"desenha('#{c.id}-sub .d',{q(T(t))},0.3);")
    return (f'<svg id="{c.id}-sub" width="{larg}" height="30" viewBox="0 0 {larg} 30" fill="none" stroke="{VERDE}" '
            f'stroke-width="9" stroke-linecap="round" style="margin-top:-30px"><path class="d" pathLength="1" '
            f'd="M10 18 Q{larg // 2} 4 {larg - 10} 18"/></svg>')


def chat(c, msg_in, msg_out, t_in, t_dig, t_out, chip_txt=None, t_chip=None, larg=820):
    s = f'#{c.id}'
    c.a(f"entra('{s}-chat',{q(c.t0 + 0.14)});")
    c.a(f"desliza('{s}-b1',{q(T(t_in))},-30,0);")
    c.a(f"aparece('{s}-dig',{q(T(t_dig))});")
    c.a(f"quica('{s}-dig i',{q(T(t_dig) + 0.05)},3,-9,0.13,0.06);")
    c.a(f"vai('{s}-dig',{{opacity:0,duration:0.08}},{q(T(t_out) - 0.04)});")
    c.a(f"pop('{s}-b2',{q(T(t_out))});")
    extra = ''
    if chip_txt:
        c.a(f"pop('{s}-cc',{q(T(t_chip))});")
        extra = f'<div class="chip mini" id="{c.id}-cc" style="align-self:flex-end">{chip_txt}</div>'
    return (f'<div class="cartao" id="{c.id}-chat" style="width:{larg}px;padding:34px;display:flex;flex-direction:column;gap:20px">'
            f'<div class="bolha in" id="{c.id}-b1">{msg_in}</div>'
            f'<div class="vaga"><div class="digita" id="{c.id}-dig"><i></i><i></i><i></i></div>'
            f'<div class="bolha out" id="{c.id}-b2">{msg_out}</div></div>{extra}</div>')


def baloes(c, textos, tempos, verde_ultimo=True):
    """Balões de fala surgindo um depois do outro (repetição, conversa)."""
    out = ''
    for k, (tx, t) in enumerate(zip(textos, tempos)):
        cls = 'out' if (verde_ultimo and k == len(textos) - 1) else 'in'
        lado = 'flex-end' if k % 2 else 'flex-start'
        out += (f'<div class="bolha {cls}" id="{c.id}-bl{k}" style="position:static;align-self:{lado}">{tx}</div>')
        c.a(f"pop('#{c.id}-bl{k}',{q(T(t))});")
    return f'<div style="display:flex;flex-direction:column;gap:18px;width:760px">{out}</div>'


def calendario(c, t_marca, t_equipe=None, rotulo='Reunião'):
    s = f'{c.id}'
    cels = ''.join(f'<div class="cel"{f" id={s}-alvo" if k == 11 else ""}>'
                   + (svg('check', 46, f'{s}-ok', 'preto', sw=8) if k == 11 else '') + '</div>' for k in range(21))
    c.a(f"entra('#{s}-cal',{q(c.t0 + 0.12)});")
    c.a(f"pop('#{s} .cel',{q(c.t0 + 0.2)},0.008);")
    c.a(f"vai('#{s}-alvo',{{backgroundColor:'{VERDE}',borderColor:'{VERDE}',duration:0.2}},{q(T(t_marca) - 0.1)});")
    c.a(f"desenha('#{s}-ok .d',{q(T(t_marca))},0.22);")
    avs = ''
    if t_equipe is not None:
        avs = ''.join(f'<div class="av">{svg("pessoa", 66)}</div>' for _ in range(3))
        avs = f'<div class="linha" style="gap:0">{avs}</div>'
        c.a(f"pop('#{s} .av',{q(T(t_equipe))},0.08);")
    return (f'<div class="linha" style="gap:40px"><div class="cartao" id="{s}-cal" style="padding:30px">'
            f'<div class="kick" style="margin-bottom:18px">{rotulo}</div><div class="cal">{cels}</div></div>{avs}</div>')


def cta(c, t_clique, texto='Agendar reunião', seta_t=None):
    """Botão shiny com cursor clicando em t_clique; seta_t = seta pra baixo quicando ("aqui embaixo")."""
    html = botao(c, texto)
    c.a(f"entra('#{c.id}-bt',{q(c.t0 + 0.1)});")
    clique(c, T(t_clique))
    if seta_t is not None:
        html += svg('seta_baixo', 130, f'{c.id}-seta', 'verde', sw=4)
        icone(c, f'#{c.id}-seta', T(seta_t) - 0.1)
        c.a(f"quica('#{c.id}-seta',{q(T(seta_t) + 0.25)},1,16,0.2,0);")
    return html


def grafico_linha(c, t, icone_nome='megaphone'):
    pts = '20,160 90,128 160,142 230,92 300,104 380,40'
    c.a(f"entra('#{c.id}-graf',{q(T(t))});")
    c.a(f"desenha('#{c.id}-graf .d',{q(T(t) + 0.12)},0.65);")
    c.a(f"pop('#{c.id}-pt',{q(T(t) + 0.75)});")
    icone(c, f'#{c.id}-gi', T(t) - 0.1)
    return (f'<div class="linha" style="gap:40px">{ph_svg(icone_nome, 210, f"{c.id}-gi")}'
            f'<div class="cartao" id="{c.id}-graf" style="width:520px;height:270px;padding:24px 30px">'
            f'<svg width="460" height="220" viewBox="0 0 400 190" fill="none" stroke="#fff" stroke-width="5" '
            f'stroke-linecap="round" stroke-linejoin="round"><polyline class="d" pathLength="1" points="{pts}"/>'
            f'<circle id="{c.id}-pt" cx="380" cy="40" r="11" fill="{VERDE}" stroke="none"/></svg></div></div>')


def barras(c, t, rotulo, alturas=(60, 90, 110, 140, 175, 215), verde=True, seta='trend-up', t_seta=None):
    cor = VERDE if verde else '#fff'
    bs = ''.join(f'<div class="barra" style="width:56px;height:{h}px;background:{cor}"></div>' for h in alturas)
    c.a(f"entra('#{c.id}-card',{q(T(t) - 0.1)});")
    c.a(f"sobe('#{c.id} .barra',{q(T(t))},0.45,0.08);")
    s = ''
    if seta:
        s = ph_svg(seta, 130, f'{c.id}-ss', 'verde')
        icone(c, f'#{c.id}-ss', T(t_seta) if t_seta is not None else T(t) + 0.6)
    return (f'<div class="cartao" id="{c.id}-card" style="width:820px;padding:30px 40px;display:flex;flex-direction:column;gap:14px">'
            f'<div class="kick">{rotulo}</div><div class="linha" style="gap:40px;align-items:flex-end">'
            f'<div class="barras" style="gap:22px">{bs}</div>{s}</div></div>')


def comparacao(c, t, antes='Antes', depois='Hoje', de=100, ate=50, t_muda=None):
    """Barra ANTES 100 % × DEPOIS mudando pra `ate` % com contador."""
    s = c.id
    tm = T(t_muda) if t_muda is not None else T(t) + 0.8
    c.a(f"entra('#{s}-card',{q(T(t) - 0.1)});")
    c.a(f"estica('#{s}-a',{q(T(t))},0.45);")
    c.a(f"estica('#{s}-h',{q(T(t) + 0.1)},0.45);")
    c.a(f"vai('#{s}-h',{{scaleX:{ate / 100},duration:0.6,ease:'power3.inOut'}},{q(tm)});")
    c.a(f"conta('#{s}-v',{de},{ate},{q(tm)},0.6,'%');")
    return (f'<div class="cartao" id="{s}-card" style="width:860px;padding:38px 40px;display:flex;flex-direction:column;gap:30px">'
            f'<div class="fila"><div class="rot">{antes}</div><div class="trilho"><div class="barra-h" id="{s}-a" style="background:#fff"></div></div><div class="val">{de}%</div></div>'
            f'<div class="fila"><div class="rot g">{depois}</div><div class="trilho"><div class="barra-h" id="{s}-h" style="background:{VERDE}"></div></div><div class="val g" id="{s}-v">{de}%</div></div></div>')


def passos(c, tempos, rotulos=None):
    s = c.id
    h = ''
    for i, t in enumerate(tempos):
        h += (f'<div class="passo" id="{s}-c{i}"><span id="{s}-n{i}">{(rotulos or [])[i] if rotulos else i + 1}</span>'
              f'{svg("check", 76, f"{s}-k{i}", "k-passo", sw=6)}</div>')
        if i < len(tempos) - 1:
            h += f'<div class="elo"><div class="elo-f" id="{s}-f{i}"></div></div>'
        c.a(f"vai('#{s}-c{i}',{{borderColor:'{VERDE}',backgroundColor:'#0B2419',duration:0.2}},{q(T(t))});")
        c.a(f"vai('#{s}-n{i}',{{opacity:0,duration:0.1}},{q(T(t))});")
        c.a(f"desenha('#{s}-k{i} .d',{q(T(t) + 0.05)},0.25);")
        if i < len(tempos) - 1:
            c.a(f"estica('#{s}-f{i}',{q(T(t) + 0.12)},0.4);")
    c.a(f"entra('#{s}-passos',{q(c.t0 + 0.3)});")
    return f'<div class="linha" style="gap:0" id="{s}-passos">{h}</div>'


def lead(c, t, chip_txt='Quente'):
    s = c.id
    c.a(f"entra('#{s}-lead',{q(T(t) - 0.1)});")
    c.a(f"estica('#{s}-m',{q(T(t))},0.45);")
    c.a(f"pop('#{s}-lc',{q(T(t) + 0.4)});")
    return (f'<div class="cartao" id="{s}-lead" style="width:760px;padding:36px 40px;display:flex;align-items:center;gap:30px">'
            f'<div class="avatar">{svg("pessoa", 86)}</div><div style="flex:1;display:flex;flex-direction:column;gap:14px">'
            f'<div class="cinza" style="width:320px"></div><div class="cinza" style="width:220px"></div>'
            f'<div class="linha" style="gap:18px;justify-content:flex-start"><div class="trilho" style="width:300px;height:22px">'
            f'<div class="barra-h" id="{s}-m" style="background:{VERDE}"></div></div>'
            f'<div class="chip mini" id="{s}-lc">{chip_txt}</div></div></div></div>')


def engrenagens(c, t, vel=120, tam=230, pessoa_sai=None):
    """Duas engrenagens girando em sentidos opostos (operação rodando); pessoa_sai = t em que você sai de cima."""
    s = c.id
    topo = ''
    if pessoa_sai is not None:
        topo = f'<div id="{s}-eu">{ph_svg("user", 120)}</div>'
        c.a(f"entra('#{s}-eu',{q(c.t0 + 0.12)});")
        c.a(f"vai('#{s}-eu',{{y:-70,opacity:0,duration:0.45,ease:'power2.in'}},{q(T(pessoa_sai))});")
    icone(c, f'#{s}-g1', T(t))
    icone(c, f'#{s}-g2', T(t) + 0.1)
    c.a(f"giraO('#{s}-g1',0,{vel * 6},{q(T(t))},6,'50% 50%');")
    c.a(f"giraO('#{s}-g2',0,-{int(vel * 1.35 * 6)},{q(T(t))},6,'50% 50%');")
    return (f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px">{topo}'
            f'<div class="linha" style="gap:0;align-items:flex-start">{ph_svg("gear", tam, f"{s}-g1", "verde")}'
            f'<div style="margin-left:-{int(tam * 0.13)}px;margin-top:-{int(tam * 0.05)}px">'
            f'{ph_svg("gear-six", int(tam * 0.74), f"{s}-g2")}</div></div></div>')


def hub(c, t_bolhas, t_linhas, t_verde, icone_bolha='chat-circle-dots'):
    """Você no centro com 6 bolhas ligadas por linhas ("tudo depende de você")."""
    s = c.id
    pos = [(90, 165), (210, 45), (210, 285), (690, 45), (690, 285), (810, 165)]
    bolhas = ''.join(f'<div class="tile p" style="position:absolute;left:{x - 44}px;top:{y - 44}px">'
                     f'{ph_svg(icone_bolha, 50)}</div>' for x, y in pos)
    ls = ''.join(f'<line class="d" pathLength="1" x1="{x}" y1="{y}" x2="450" y2="165"/>' for x, y in pos)
    c.a(f"entra('#{s}-eu',{q(c.t0 + 0.15)});")
    c.a(f"pop('#{s} .tile.p',{q(T(t_bolhas))},0.06);")
    c.a(f"desenha('#{s}-lin .d',{q(T(t_linhas))},0.35,0.05);")
    c.a(f"vai('#{s}-eu',{{backgroundColor:'rgba(16,185,129,0.16)',duration:0.2}},{q(T(t_verde))});")
    c.a(f"vai('#{s}-eu .ic',{{fill:'{VERDE}',duration:0.2}},{q(T(t_verde))});")
    return (f'<div style="position:relative;width:900px;height:330px">'
            f'<svg id="{s}-lin" width="900" height="330" viewBox="0 0 900 330" fill="none" stroke="#fff" stroke-width="3" '
            f'stroke-linecap="round" style="position:absolute;left:0;top:0;opacity:0.45">{ls}</svg>{bolhas}'
            f'<div class="avatar" id="{s}-eu" style="position:absolute;left:365px;top:80px;width:170px;height:170px">'
            f'{ph_svg("user", 110)}</div></div>')


def quadro_lupa(c, t_quadro, t_lupa):
    s = c.id
    icone(c, f'#{s}-q', T(t_quadro))
    c.a(f"pop('#{s}-lupa',{q(T(t_lupa))});")
    return (f'<div style="position:relative;width:520px;height:340px">{ph_svg("presentation-chart", 340, f"{s}-q")}'
            f'<div id="{s}-lupa" style="position:absolute;left:310px;top:150px">{ph_svg("magnifying-glass", 190, "", "verde")}</div></div>')


def rabisco(c, t, dur=1.1):
    c.a(f"desenha('#{c.id}-rab .d',{q(T(t))},{dur});")
    return (f'<svg id="{c.id}-rab" width="700" height="240" viewBox="0 0 700 240" fill="none" stroke="#fff" stroke-width="8" '
            f'stroke-linecap="round" stroke-linejoin="round"><path class="d" pathLength="1" '
            f'd="M20 150 C70 20 130 250 190 120 C230 30 290 60 260 150 C230 230 330 230 350 130 C370 40 450 20 440 120 '
            f'C430 210 520 230 540 140 C560 60 620 50 600 150 C590 200 660 190 680 90"/></svg>')


def grade_pessoas(c, t, n=12, icone_nome='user', cols=6):
    larg = cols * 84 + (cols - 1) * 16
    gente = ''.join(f'<div class="mini-u">{ph_svg(icone_nome, 84)}</div>' for _ in range(n))
    c.a(f"pop('#{c.id} .mini-u',{q(T(t))},0.05);")
    return f'<div class="grade" style="width:{larg}px;gap:16px">{gente}</div>'
