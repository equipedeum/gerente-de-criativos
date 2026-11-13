# -*- coding: utf-8 -*-
"""Editor "Edição animada" (05/11/2026) — documentário ilustrado em vetor chapado, sobre o motor da tela dividida.

Referência: documentários ilustrados em vetor chapado (processo na skill edicao-animada). O que se pega do estilo (sem copiar personagens, marca nem cenas deles):
  - cenários ilustrados em vetor chapado, em camadas (céu em degradê, nuvens, montanhas com perspectiva atmosférica,
    árvores, cidade com janelas acesas), com a câmera sempre andando devagar e PARALAXE entre as camadas;
  - paleta dessaturada e quente: azul-acinzentado, creme de pergaminho, laranja de fogo, azul-noite;
  - (cartela de capítulo da referência: o RÓTULO "CAPÍTULO I" foi proibido em 08/11/2026 — não faz sentido num anúncio;
    o fundo de raios só como cenário de passagem com letreiro falado + ação);
  - data/número grande em serifa sobre pergaminho;
  - rótulo de lugar/hora no canto de baixo com relógio de bolso (ponteiros andando);
  - transição por mergulho no escuro quando o cenário muda; sons do Earshot (whoosh macio, tique, impacto de ar).

Peças (todas devolvem HTML para o monta(); tempos em índice de palavra (int) ou s (float)):
  cenario(c, tipo, **op)     fundo ilustrado da cena: 'dia', 'tarde', 'noite', 'cidade', 'cidade_noite',
                             'interior', 'pergaminho', 'capitulo'. Cenas seguidas com o mesmo tipo = mesmo cenário
                             com a câmera contínua (plano longo).
  cheia(c)                   no RL a cena ocupa a tela inteira (animação cheia; regra dos 3 modos de 26/10)
  capitulo(...)              DESATIVADO em 08/11/2026 (sem rótulo de capítulo em anúncio); não desenha nada
  data(c, '23h', t, legenda) número/data grande em serifa, carimbando no pergaminho
  rotulo(c, 'TÍTULO', 'sub', t)  lower-third com relógio de bolso
  risca(c, t, linha=-1)      traço de pincel riscando uma linha do letreiro (depois do monta; 12/11)
  + ic()/linha()/chat()/calendario()/cta() do pecas.py, redesenhados no estilo (objetos chapados com sombra)

Uso no gerar.py (hyperframes/<id>-animada/gerar.py):
    configurar(...); from pecas import *; import animada as an
    c = an.cenario(cena(0, 3, '...'), 'dia'); monta(c, '{64f}A sua empresa|{120}*cresceu', linha(...))
    ...
    an.aplicar()     # no lugar de montar()
"""
import html as _html
import json
import random
import re
import shutil
import wave
from pathlib import Path

import numpy as np
from PIL import ImageFont

import motor
import pecas
from motor import q

RAIZ = motor.RAIZ
_SFX_DIR = RAIZ / 'remotion/public/sfx-animada'      # gerados com o Earshot (ferramentas/earshot-venv), MIT
_FONTES = {
    'TikTokSans-Variable.ttf': RAIZ / 'ferramentas/fontes/TikTokSans-Variable.ttf',
    'EBGaramond-400.woff2': RAIZ / 'ferramentas/fontes/EBGaramond-400.woff2',
    'EBGaramond-700.woff2': RAIZ / 'ferramentas/fontes/EBGaramond-700.woff2',
    'Cinzel-700.woff2': RAIZ / 'ferramentas/fontes/cinzel-latin-700-normal.woff2',
}

# ---------------------------------------------------------------- paleta (vetor chapado, dessaturada e quente)
TINTA, CREME, OURO, FERRUGEM, NOITE = '#1E2A3A', '#F6EBD3', '#F2B544', '#B5523B', '#101B36'
TEMAS = {   # tipo -> (claro?, cor do texto, cor do apoio, cor da chave, cor dos objetos, objeto destaque)
    'dia':          (True,  TINTA, '#33424F', FERRUGEM, '#2D4A63', FERRUGEM),
    'interior':     (True,  TINTA, '#3B3328', FERRUGEM, '#3B4E5E', FERRUGEM),
    'pergaminho':   (True,  '#3A2A1A', '#4A3A28', FERRUGEM, '#5A4126', FERRUGEM),
    'cidade':       (True,  TINTA, '#33424F', FERRUGEM, '#2D4A63', FERRUGEM),
    'tarde':        (False, CREME, '#FBE9D0', OURO, CREME, OURO),
    'noite':        (False, CREME, '#DCE3F0', OURO, CREME, OURO),
    'cidade_noite': (False, CREME, '#DCE3F0', OURO, CREME, OURO),
    'capitulo':     (False, CREME, '#DCE3F0', OURO, CREME, OURO),
    # 06/11 (v3): ambientes do dia a dia desenhados pelo bonecos.fundo()
    'escritorio':       (True,  TINTA, '#3B3328', '#9A4430', '#3B4E5E', FERRUGEM),   # chave mais escura: contraste ≥ 3:1
    'escritorio_noite': (False, CREME, '#E6DCC6', OURO, CREME, OURO),
    'reuniao':          (True,  TINTA, '#2E3A36', FERRUGEM, '#3B4E5E', FERRUGEM),
    'sala_noite':       (False, CREME, '#E6DCC6', OURO, CREME, OURO),
    'rua':              (True,  TINTA, '#2A3A48', FERRUGEM, '#2D4A63', FERRUGEM),
    'rua_tarde':        (False, CREME, '#FBE9D0', OURO, CREME, OURO),
    'celular':          (False, CREME, '#DCE3F0', OURO, CREME, OURO),
    'celular_dia':      (True,  TINTA, '#3B3328', FERRUGEM, '#3B4E5E', FERRUGEM),
    'recepcao':         (True,  TINTA, '#3B3328', FERRUGEM, '#3B4E5E', FERRUGEM),
    'deposito':         (True,  TINTA, '#232E38', FERRUGEM, '#2D4A63', FERRUGEM),
    'copa':             (True,  TINTA, '#2E3A36', FERRUGEM, '#3B4E5E', FERRUGEM),
    'sala_dono':        (False, CREME, '#E6DCC6', OURO, CREME, OURO),
    'rua_noite':        (False, CREME, '#DCE3F0', OURO, CREME, OURO),
    'quarto_noite':     (False, CREME, '#E6DCC6', OURO, CREME, OURO),
    'escritorio2':      (True,  TINTA, '#3B3328', '#8E3A26', '#3B4E5E', FERRUGEM),   # chave mais escura: contraste ≥ 3:1 na parede clara
}
SALAS = ('escritorio', 'escritorio_noite', 'reuniao', 'sala_noite', 'rua', 'rua_tarde', 'rua_noite', 'celular', 'celular_dia',
         'recepcao', 'deposito', 'copa', 'sala_dono', 'quarto_noite', 'escritorio2')

CEN = {}          # id da cena -> (tipo, opções)
CHEIAS = set()    # cenas em animação cheia no RL (só com TELA_CHEIA=False)
TELA_CHEIA = True   # 05/11: animação em tela cheia o vídeo todo + pessoa em tela cheia nas cenas do pessoa_gl
# 12/11/2026 (usuário, caso real: "quando fica pessoa em tela cheia quero legenda padrão"): nas cenas da pessoa em tela
# cheia (pessoa_gl, nos 4 formatos) entra a legenda PADRÃO do básico — UMA linha, branca, sombra leve, sem animação,
# blocos de até 4 palavras pelo sentido, na altura padrão de cada formato. LEGENDA_PESSOA=False desliga.
LEGENDA_PESSOA = True
LEG_PESSOA = {}      # {id da cena: 'bloco um|bloco dois|...'} quebra manual (mesmas palavras da fala); sem ela, automática
PUNCH_PESSOA = 1.05  # 12/11: corte seco do tratado no MEIO da frase da pessoa cheio = punch-in leve (falso corte), nunca pulo
SFX = []          # (t, nome, volume)
_n = [0]
# 07/11 (arsenal_animada.py): ganchos OPCIONAIS — vazios = nada muda num gerar.py que não importa o arsenal
SEM_MERGULHO = set()   # cenas cuja entrada é uma transição própria do arsenal (sem o mergulho/empurrão padrão)
CAM = {}               # id da cena -> movimento de câmera próprio do .cenario (no lugar do zoom lento padrão)
GANCHOS_PRE = []       # funções chamadas no aplicar() depois de acertar os t0 (antes de montar as cenas)
GANCHOS_POS = []       # funções chamadas logo antes do motor.montar() (as cenas já embrulhadas no tema)
GANCHOS_FIM = []       # funções chamadas depois de gravar o index.html


def _id(c, pref):
    _n[0] += 1
    return f'{c.id}-{pref}{_n[0]}'


def som(t, nome, vol=0.2):
    """Efeito em t (s): transicao, swish, papel, whoosh_lento, respiro, impacto_ar, batida, impacto, tique, tique2,
    pop, pop2, glock, marimba, floreio, riser, brilho, obturador, madeira, shimmer, sub, digitando."""
    SFX.append((round(float(t), 3), nome, vol))


def cenario(c, tipo='dia', **op):
    if tipo not in TEMAS:
        raise ValueError(f'cenário desconhecido: {tipo}')
    CEN[c.id] = (tipo, op)
    return c


def cheia(c):
    CHEIAS.add(c.id)
    return c


_FILL = RAIZ / 'ferramentas/phosphor-core/assets/fill'


def _ph_fill(arquivo, tam, id_='', cls='', estilo=''):
    """Ícones Phosphor no peso fill: objeto chapado (cor do tema) com sombra dura embaixo, como no vetor da referência."""
    corpo = re.search(r'<svg[^>]*>(.*)</svg>', (_FILL / f'{arquivo}-fill.svg').read_text(encoding='utf-8'), re.S).group(1)
    ida = f' id="{id_}"' if id_ else ''
    est = f' style="{estilo}"' if estilo else ''
    return f'<svg{ida} class="ic ph {cls}" width="{tam}" height="{tam}" viewBox="0 0 256 256"{est}>{corpo}</svg>'


motor.ph_svg = _ph_fill
pecas.ph_svg = _ph_fill


def _T(x):
    return motor.ts(x) if isinstance(x, int) else float(x)


# ================================================================ PEÇAS
_AVISOU_CAP = []


def capitulo(c, texto, t=None):
    """DESATIVADO (08/11/2026, regra do usuário): nada de rótulo "CAPÍTULO I/II" — era da referência (da referência) e
    não faz sentido num anúncio da pessoa ("por que Capítulo 1?", revisão do caso real). Continua existindo só pra gerar.py
    antigo não quebrar: não desenha nada, não toca som e avisa. A cartela de raios ('capitulo', 'capitulo_vermelho',
    'capitulo_verde') só vale como cenário de passagem com o letreiro FALADO e uma peça de ação/dado; o aplicar() avisa
    quando ela fica sem ação."""
    if not _AVISOU_CAP:
        print(f'  AVISO capitulo: an.capitulo({texto!r}) ignorado em {c.id} — rótulo de capítulo proibido desde 08/11; tire do gerar.py')
        _AVISOU_CAP.append(1)
    return ''


def data(c, texto, t, legenda=''):
    """Data/número grande em serifa (EB Garamond 700) que carimba no pergaminho, com legenda pequena embaixo."""
    did = _id(c, 'd')
    t = _T(t)
    # rodada 6: mancha de tinta abrindo atrás do número (e crescendo devagar até o fim da cena)
    k_ = motor.CENAS.index(c)
    t1_ = motor.CENAS[k_ + 1].t0 if k_ + 1 < len(motor.CENAS) else (q(motor.ts(c.i1 + 1) - 0.2) if c.i1 + 1 < len(motor.W) else motor.DUR)
    c.a(f"tl.fromTo('#{did} .mancha',{{scale:0.15,rotation:-20,opacity:0}},{{scale:1,rotation:0,opacity:1,duration:0.55,ease:'power3.out',transformOrigin:'50% 50%'}},{q(t - 0.12)});")
    c.a(f"tl.to('#{did} .mancha',{{scale:1.12,rotation:6,duration:{max(0.5, t1_ - t - 0.5):.2f},ease:'none',transformOrigin:'50% 50%'}},{q(t + 0.45)});")
    c.a(f"tl.fromTo('#{did} .dn',{{opacity:0,scale:1.1,y:24}},{{opacity:1,scale:1,y:0,duration:0.32,ease:'power3.out'}},{q(t)});")
    c.a(f"tl.fromTo('#{did} .dw',{{rotation:-2}},{{rotation:0,duration:0.25,ease:'back.out(3)'}},{q(t + 0.25)});")
    c.a(f"tl.fromTo('#{did} .dl',{{opacity:0,y:12}},{{opacity:1,y:0,duration:0.35,ease:'power2.out'}},{q(t + 0.35)});")
    som(t + 0.05, 'impacto', 0.30)
    leg = f'<div class="dl">{_html.escape(legenda)}</div>' if legenda else ''
    mancha = ('<svg class="mancha" viewBox="0 0 400 260"><path d="M60 140 C20 90 70 30 140 46 C190 10 270 20 300 60 C370 60 390 130 350 170 '
              'C360 230 270 250 220 222 C170 255 90 240 80 200 C30 200 30 160 60 140Z"/><circle cx="360" cy="70" r="12"/><circle cx="40" cy="220" r="9"/>'
              '<circle cx="330" cy="236" r="7"/></svg>')
    return f'<div class="data" id="{did}">{mancha}<div class="dw"><div class="dn">{_html.escape(texto)}</div></div>{leg}</div>'


_RELOGIO = ('<svg class="rel" viewBox="0 0 100 116" width="96" height="112">'
            '<rect x="43" y="2" width="14" height="12" rx="3" fill="#C9A24A"/><circle cx="50" cy="14" r="5" fill="none" stroke="#C9A24A" stroke-width="3"/>'
            '<circle cx="50" cy="64" r="46" fill="#C9A24A"/><circle cx="50" cy="64" r="40" fill="#8E6B22"/>'
            '<circle cx="50" cy="64" r="37" fill="#FBF6EA"/>'
            + ''.join(f'<rect x="49" y="30" width="2" height="{7 if k % 3 == 0 else 4}" fill="#3A2A1A" transform="rotate({k * 30} 50 64)"/>' for k in range(12))
            + '<g class="ph"><rect x="48.5" y="40" width="3" height="26" rx="1.5" fill="#1E2A3A"/></g>'
              '<g class="pm"><rect x="49" y="31" width="2" height="35" rx="1" fill="#B5523B"/></g>'
              '<circle cx="50" cy="64" r="3.5" fill="#1E2A3A"/></svg>')


def rotulo(c, titulo, sub='', t=None):
    """Lower-third no canto de baixo: relógio de bolso (ponteiros andando) + TÍTULO em sans condensada + sub."""
    rid = _id(c, 'r')
    t = c.t0 + 0.3 if t is None else _T(t)
    c.a(f"tl.fromTo('#{rid}',{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.3,ease:'power2.out'}},{q(t)});")   # 06/11: a caixa vazia aparecia antes
    c.a(f"tl.fromTo('#{rid} .rel',{{opacity:0,scale:0.6,rotation:-25}},{{opacity:1,scale:1,rotation:0,duration:0.4,ease:'back.out(1.8)'}},{q(t)});")
    c.a(f"tl.fromTo('#{rid} .rt',{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.35,ease:'power3.out'}},{q(t + 0.15)});")
    c.a(f"tl.fromTo('#{rid} .rf',{{scaleX:0}},{{scaleX:1,duration:0.35,ease:'power2.out'}},{q(t + 0.3)});")
    c.a(f"tl.fromTo('#{rid} .rs',{{opacity:0}},{{opacity:1,duration:0.3}},{q(t + 0.4)});")
    c.a(f"tl.fromTo('#{rid} .pm',{{rotation:0}},{{rotation:360,duration:6,ease:'none',svgOrigin:'50 64'}},{q(t)});")
    c.a(f"tl.fromTo('#{rid} .ph',{{rotation:0}},{{rotation:30,duration:6,ease:'none',svgOrigin:'50 64'}},{q(t)});")
    for k in range(3):
        som(t + 0.05 + 0.3 * k, 'tique', 0.22)
    s = f'<div class="rs">{_html.escape(sub)}</div>' if sub else ''
    return (f'<div class="rotulo" id="{rid}">{_RELOGIO}<div class="rtx"><div class="rt">{_html.escape(titulo)}</div>'
            f'<i class="rf"></i>{s}</div></div>')


_RISCO = ('<svg viewBox="0 0 1000 100" preserveAspectRatio="none"><path d="M8 36 C140 22 300 34 460 26 C640 18 820 30 990 16 '
          'C1000 30 998 50 992 66 C830 78 650 66 470 76 C320 84 160 74 12 88 C0 74 0 50 8 36Z"/></svg>')


def risca(c, t, linha=-1, dur=0.25, apaga=0.5, cor=None, vol=0.22):
    """12/11/2026 (usuário, caso real: "quando acaba a frase RISCA ela, e aí vem a frase seguinte"): risca uma linha do
    letreiro da cena com um traço de pincel desenhado da esquerda pra direita em `dur` s a partir de t (índice de palavra
    ou s). Chamar DEPOIS do monta(c, ...). linha = índice da linha do letreiro (-1 = a última). As palavras riscadas
    apagam até `apaga` de opacidade (o traço fica por cima, legível). cor=None = a cor do texto da linha (tema)."""
    t = _T(t)
    rid = _id(c, 'rk')
    linhas = list(re.finditer(r'<div class="ln[^"]*" style="font-size:\d+px">(.*?)</div>', c.html))
    if not linhas:
        print(f'  AVISO risca: {c.id} sem letreiro pra riscar (chame an.risca depois do monta)')
        return c
    m = linhas[linha]
    est = f'clip-path:inset(0% 100% 0% 0%);' + (f'color:{cor};' if cor else '')
    c.html = c.html[:m.end(1)] + f'<i class="risco" id="{rid}" style="{est}">{_RISCO}</i>' + c.html[m.end(1):]
    c.a(f"tl.fromTo('#{rid}',{{clipPath:'inset(0% 100% 0% 0%)'}},{{clipPath:'inset(0% 0% 0% 0%)',duration:{dur},ease:'power2.inOut'}},{q(t)});")
    ids = re.findall(r'id="(c\d+-w\d+)"', m.group(1))
    if ids and apaga is not None:
        c.a(f"tl.to([{','.join(repr('#' + i) for i in ids)}],{{opacity:{apaga},duration:0.2,ease:'power1.out'}},{q(t + dur * 0.5)});")
    som(t, 'papel', vol)
    return c


# ================================================================ CENÁRIOS (SVG em camadas, ancorados embaixo)
_PAN = 300   # cada camada tem 300 px de sobra de cada lado pra câmera andar


def _montanhas(rnd, larg, alt, base, amp, n, cor, suave=False):
    """Serra em polígono: n picos entre base-amp e base; devolve <path> numa caixa larg x alt (y pra baixo)."""
    pts = [(0, alt)]
    x = 0.0
    passo = larg / n
    while x <= larg + passo:
        pico = alt - base - rnd.uniform(0.35, 1.0) * amp
        vale = alt - base + rnd.uniform(0.0, 0.25) * amp
        pts.append((x + passo * rnd.uniform(0.35, 0.65), pico))
        pts.append((x + passo, vale))
        x += passo
    pts.append((larg, alt))
    if suave:
        d = f'M0 {alt} ' + ' '.join(f'Q{pts[i][0]:.0f} {pts[i][1]:.0f} {(pts[i][0] + pts[i + 1][0]) / 2:.0f} {(pts[i][1] + pts[i + 1][1]) / 2:.0f}'
                                     for i in range(1, len(pts) - 2)) + f' L{larg} {alt}Z'
    else:
        d = 'M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in pts) + 'Z'
    return f'<path d="{d}" fill="{cor}"/>'


def _pinheiros(rnd, larg, alt, base, n, cor, h0=60, h1=130):
    out = []
    for _ in range(n):
        x = rnd.uniform(0, larg)
        h = rnd.uniform(h0, h1)
        w = h * 0.42
        y = alt - base + rnd.uniform(-8, 10)
        out.append(f'<path d="M{x:.0f} {y - h:.0f} L{x + w / 2:.0f} {y:.0f} L{x - w / 2:.0f} {y:.0f}Z" fill="{cor}"/>')
    return ''.join(out)


def _nuvem(x, y, s, cor):
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({s:.2f})" fill="{cor}">'
            '<ellipse cx="0" cy="0" rx="70" ry="30"/><ellipse cx="45" cy="-18" rx="48" ry="34"/>'
            '<ellipse cx="-40" cy="-10" rx="40" ry="26"/><ellipse cx="85" cy="2" rx="45" ry="22"/></g>')


def _predios(rnd, larg, alt, base, hmin, hmax, cor, janela=None, acesas=0.0, wmin=70, wmax=150):
    out, x = [], -20.0
    while x < larg:
        w = rnd.uniform(wmin, wmax)
        h = rnd.uniform(hmin, hmax)
        y = alt - base - h
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h + base:.0f}" fill="{cor}"/>')
        if rnd.random() < 0.3:   # caixa d'água / antena
            out.append(f'<rect x="{x + w * 0.3:.0f}" y="{y - 18:.0f}" width="{w * 0.18:.0f}" height="18" fill="{cor}"/>')
        if janela:
            for jy in range(int(y + 18), int(alt - base - 14), 26):
                for jx in range(int(x + 12), int(x + w - 16), 22):
                    acesa = rnd.random() < acesas
                    pj = ' class="pj"' if acesa and rnd.random() < 0.18 else ''
                    out.append(f'<rect x="{jx}" y="{jy}" width="10" height="14" fill="{janela[1] if acesa else janela[0]}"{pj}/>')
        x += w + rnd.uniform(4, 18)
    return ''.join(out)


def _camada(svg_corpo, alt, vel, cls=''):
    """Camada ancorada embaixo, 1080 + 2*_PAN de largura; vel = px/s de paralaxe."""
    larg = 1080 + 2 * _PAN
    return (f'<div class="cam {cls}" data-vel="{vel}" style="height:{alt}px">'
            f'<svg width="{larg}" height="{alt}" viewBox="0 0 {larg} {alt}">{svg_corpo}</svg></div>')


def _ceu(grad, extra=''):
    return f'<div class="ceu" style="background:{grad}">{extra}</div>'


TW = ' class="tw"'


def _estrelas(rnd, n=90):
    pts = ''.join(f'<circle cx="{rnd.uniform(0, 1680):.0f}" cy="{rnd.uniform(0, 1250):.0f}" r="{rnd.choice((1.2, 1.6, 2.2))}" '
                  f'fill="#fff" opacity="{rnd.uniform(0.35, 0.95):.2f}"{TW if rnd.random() < 0.3 else ""}/>' for _ in range(n))
    return f'<div class="cam est" data-vel="1.5" style="top:0;bottom:auto;height:1250px"><svg width="1680" height="1250">{pts}</svg></div>'


def _nuvens(rnd, cor, n=5, topo=110):
    xs = [rnd.uniform(240, 560) if k % 2 else rnd.uniform(1120, 1440) for k in range(n)]   # laterais (o meio é do texto)
    g = ''.join(_nuvem(x, rnd.uniform(60, 200), rnd.uniform(0.6, 1.1), cor) for x in xs)
    return f'<div class="cam nuv" data-vel="7" style="top:0;bottom:auto;height:300px;opacity:.9"><svg width="1680" height="300">{g}</svg></div>'



# ---------------------------------------------------------------- vida no cenário (usuário 05/11: "todo momento tem que
# estar acontecendo alguma ação na tela"): pássaros, carros, janelas acendendo, estrelas piscando, estrela cadente,
# relógio de parede, planta balançando, brasas subindo, rota sendo desenhada. O JS de cada uma sai no aplicar().
def _aves(rnd, cor, n=3):
    g = []
    for k in range(n):
        y = rnd.uniform(140, 330)
        s = rnd.uniform(0.7, 1.15)
        g.append(f'<g class="ave" transform="translate(0 {y:.0f})"><g transform="scale({s:.2f})"><g class="asa">'
                 f'<path d="M-22 0 Q-11 -12 0 0 Q11 -12 22 0" fill="none" stroke="{cor}" stroke-width="4" stroke-linecap="round"/></g></g></g>')
    return f'<div class="aves"><svg width="1080" height="420" overflow="visible">{"".join(g)}</svg></div>'


def _carro(x, y, cor, teto, v):
    """Carrinho chapado (x,y = ponto do chão); v = px/s (negativo anda pra esquerda)."""
    esc = -1 if v < 0 else 1
    return (f'<g class="carro" data-v="{v}" data-x="{x:.0f}"><g transform="translate({x:.0f} {y}) scale({esc} 1)">'
            f'<rect x="-48" y="-30" width="96" height="22" rx="6" fill="{cor}"/>'
            f'<path d="M-30 -30 L-20 -48 L18 -48 L30 -30Z" fill="{teto}"/>'
            f'<rect x="-14" y="-45" width="14" height="13" fill="#CFE3EA"/><rect x="4" y="-45" width="14" height="13" fill="#CFE3EA"/>'
            f'<circle cx="-28" cy="-8" r="9" fill="#1A1A1A"/><circle cx="28" cy="-8" r="9" fill="#1A1A1A"/>'
            f'<circle cx="46" cy="-22" r="3.5" fill="#F7D98A"/></g></g>')


def _transito(rnd, L, y, cores, n=3):
    out = []
    for _ in range(n):
        v = rnd.choice((1, -1)) * rnd.uniform(90, 160)
        cor, teto = rnd.choice(cores)
        out.append(_carro(rnd.uniform(200, L - 200), y + (0 if v > 0 else -12), cor, teto, round(v, 1)))
    return ''.join(out)


def _relogio_parede(x, y, r=46):
    return (f'<g transform="translate({x} {y})"><circle r="{r + 6}" fill="#6B4E31"/><circle r="{r}" fill="#FBF6EA"/>'
            + ''.join(f'<rect x="-1.5" y="{-r + 4}" width="3" height="{9 if k % 3 == 0 else 5}" fill="#3A2A1A" transform="rotate({k * 30})"/>' for k in range(12))
            + f'<rect x="-2" y="{-r * 0.5:.0f}" width="4" height="{r * 0.5:.0f}" fill="#1E2A3A" transform="rotate(60)"/>'
              f'<g class="seg"><rect x="-1" y="{-r * 0.8:.0f}" width="2" height="{r * 0.9:.0f}" fill="#B5523B"/></g><circle r="4" fill="#1E2A3A"/></g>')


def _planta(x, y):
    folhas = ''.join(f'<path d="M0 0 C{-30 + 15 * k} -40 {-20 + 10 * k} -90 {-35 + 18 * k} -120 C{-5 + 6 * k} -90 {5 + 2 * k} -40 0 0Z" fill="{c}"/>'
                     for k, c in enumerate(('#3F6B4E', '#4F7F5C', '#5B8F66', '#3F6B4E', '#4F7F5C')))
    return (f'<g transform="translate({x} {y})"><g class="folha">{folhas}</g>'
            f'<path d="M-34 0 L34 0 L26 60 L-26 60Z" fill="#B5523B"/><rect x="-38" y="-6" width="76" height="12" rx="4" fill="#8E3F2C"/></g>')


def _brasas(rnd, n=16):
    return ('<div class="brasas">' + ''.join(
        f'<i class="br" style="left:{rnd.uniform(60, 1020):.0f}px;bottom:{rnd.uniform(-40, 200):.0f}px;'
        f'width:{rnd.choice((5, 7, 9))}px;height:{rnd.choice((5, 7, 9))}px"></i>' for _ in range(n)) + '</div>')


def _cenario_html(tipo, op, seed):
    rnd = random.Random(seed)
    L = 1080 + 2 * _PAN
    cam = []
    if tipo in ('dia', 'tarde', 'noite'):
        pal = {
            'dia':   dict(ceu='linear-gradient(#8FC1D4 0%,#C9E0E4 55%,#EEE7D6 100%)', astro='#FFF8E6', nuv='#FFFFFF',
                          m=('#9DBCC4', '#6F9AA8', '#4F7F8A'), arv='#335A58', chao='#C8B98E', chao2='#B7A57A'),
            'tarde': dict(ceu='linear-gradient(#3C3F6B 0%,#B9627A 42%,#F0A35E 72%,#F7D49A 100%)', astro='#FFE3A8', nuv='#F6B98C',
                          m=('#9A6A86', '#6E4E72', '#4A3656'), arv='#2D2340', chao='#3A2A3E', chao2='#2B1F30'),
            'noite': dict(ceu='linear-gradient(#0B1530 0%,#1A2A55 55%,#34497A 100%)', astro='#F3EBCF', nuv='#2A3A66',
                          m=('#2C3D66', '#22305A', '#18244A'), arv='#101A36', chao='#141E3C', chao2='#0E1630'),
        }[tipo]
        astro = (f'<div class="astro" style="background:{pal["astro"]};box-shadow:0 0 90px 30px {pal["astro"]}55"></div>'
                 if tipo != 'noite' else
                 f'<div class="astro lua" style="background:{pal["astro"]};box-shadow:0 0 70px 14px {pal["astro"]}40"></div>')
        cam.append(_ceu(pal['ceu'], astro))
        if tipo == 'noite':
            cam.append(_estrelas(rnd))
            cam.append('<div class="cadente"></div>')
        cam.append(_nuvens(rnd, pal['nuv'], 5 if tipo == 'dia' else 4))
        if tipo != 'noite':
            cam.append(_aves(rnd, '#2E3B4A' if tipo == 'dia' else '#3A2238', 4))
        cam.append(_camada(_montanhas(rnd, L, 470, 150, 260, 5, pal['m'][0]), 470, 3))
        cam.append(_camada(_montanhas(rnd, L, 380, 120, 170, 7, pal['m'][1], suave=True), 380, 6))
        cam.append(_camada(_montanhas(rnd, L, 300, 90, 110, 9, pal['m'][2], suave=True)
                           + _pinheiros(rnd, L, 300, 90, 38, pal['arv'], 50, 110), 300, 10))
        cam.append(_camada(f'<rect x="0" y="40" width="{L}" height="160" fill="{pal["chao"]}"/>'
                           f'<rect x="0" y="40" width="{L}" height="10" fill="{pal["chao2"]}"/>'
                           + f'<rect x="0" y="120" width="{L}" height="36" fill="{pal["chao2"]}"/>'
                           + _transito(rnd, L, 150, (('#B5523B', '#8E3F2C'), ('#2D4A63', '#1E3347'), ('#C9A24A', '#9C7A2E')), 3)
                           + _pinheiros(rnd, L, 110, 100, 10, pal['arv'], 90, 170), 200, 16))
    elif tipo in ('cidade', 'cidade_noite'):
        noite = tipo == 'cidade_noite'
        ceu = ('linear-gradient(#0E1834 0%,#1F2F5C 60%,#3B4F80 100%)' if noite
               else 'linear-gradient(#9CC6D6 0%,#D3E5E6 60%,#F1E9D8 100%)')
        cam.append(_ceu(ceu, '<div class="astro lua" style="background:#F3EBCF;box-shadow:0 0 70px 14px #F3EBCF40"></div>' if noite
                   else '<div class="astro" style="background:#FFF8E6;box-shadow:0 0 90px 30px #FFF8E655"></div>'))
        if noite:
            cam.append(_estrelas(rnd, 60))
        cam.append(_nuvens(rnd, '#2A3A66' if noite else '#FFFFFF', 4))
        cam.append('<div class="cadente"></div>' if noite else _aves(rnd, '#2E3B4A', 3))
        cam.append(_camada(_predios(rnd, L, 560, 60, 180, 420, '#2A3B66' if noite else '#A9C2CB', wmin=60, wmax=120), 560, 3))
        cam.append(_camada(_predios(rnd, L, 470, 60, 140, 330, '#1C2A50' if noite else '#7D9DAA',
                                    janela=('#26386A', '#F2C46B') if noite else ('#6A8B98', '#E9DFC6'), acesas=0.35 if noite else 0.15), 470, 7))
        cam.append(_camada(_predios(rnd, L, 340, 60, 100, 230, '#121C3A' if noite else '#4F7380',
                                    janela=('#1A2748', '#F7B955') if noite else ('#456876', '#F2E6C8'), acesas=0.45 if noite else 0.1,
                                    wmin=110, wmax=190)
                           + f'<rect x="0" y="280" width="{L}" height="60" fill="{"#0B1228" if noite else "#3A5560"}"/>'
                           + ''.join(f'<rect x="{x}" y="308" width="40" height="4" fill="#E9DFC6" opacity=".6"/>' for x in range(0, L, 110))
                           + _transito(rnd, L, 336, (('#B5523B', '#8E3F2C'), ('#F2B544', '#C98F2A'), ('#DCE3F0', '#9FB0C8')), 4), 340, 12))
    elif tipo == 'interior':
        # escritório: parede creme com rodameio, janela à direita (cidade lá fora), estante à esquerda; o meio fica livre
        cam.append(_ceu('linear-gradient(#EADCC0 0%,#E3D2B2 70%,#D9C6A2 100%)'))
        P = _PAN
        jx, jy, jw, jh = P + 700, 150, 230, 320
        fora = _predios(random.Random(seed + 1), jw, jh, 0, 60, 200, '#7FA4B1', wmin=40, wmax=80)
        jan = (f'<rect x="{jx}" y="{jy}" width="{jw}" height="{jh}" fill="#A9CFDD"/>'
               f'<svg x="{jx}" y="{jy}" width="{jw}" height="{jh}">{fora}</svg>'
               f'<rect x="{jx}" y="{jy}" width="{jw}" height="{jh}" fill="none" stroke="#6B4E31" stroke-width="14"/>'
               f'<rect x="{jx + jw / 2 - 6:.0f}" y="{jy}" width="12" height="{jh}" fill="#6B4E31"/>'
               f'<rect x="{jx}" y="{jy + 150}" width="{jw}" height="12" fill="#6B4E31"/>'
               f'<rect x="{jx - 16}" y="{jy + jh}" width="{jw + 32}" height="16" fill="#8A6A45"/>')
        cores = ('#B5523B', '#2D4A63', '#C9A24A', '#5B7F6E', '#7E3526', '#3B4E5E')
        livros, bx = [], P + 150
        r2 = random.Random(seed + 2)
        for prat in (170, 290, 410):
            x = bx + 10
            while x < bx + 200:
                w, h = r2.uniform(14, 26), r2.uniform(60, 92)
                livros.append(f'<rect x="{x:.0f}" y="{prat - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{r2.choice(cores)}"/>')
                x += w + 2
            livros.append(f'<rect x="{bx}" y="{prat}" width="220" height="12" fill="#6B4E31"/>')
        est = f'<rect x="{bx - 8}" y="60" width="236" height="372" fill="#8A6A45" opacity=".35"/>' + ''.join(livros)
        cam.append(_camada(jan + est + _relogio_parede(P + 815, 82, r=40), 560, 4))
        cam.append(_camada(f'<rect x="0" y="0" width="{L}" height="14" fill="#B79A6E"/>'
                           f'<rect x="0" y="14" width="{L}" height="110" fill="#C4A77A"/>'
                           + ''.join(f'<rect x="{x}" y="14" width="5" height="110" fill="#A88B60"/>' for x in range(0, L, 120))
                           + f'<rect x="0" y="124" width="{L}" height="76" fill="#8A6A45"/>'
                           + ''.join(f'<rect x="{x}" y="124" width="3" height="76" fill="#7A5B38"/>' for x in range(0, L, 90))
                           + _planta(P + 560, 64), 200, 8))
    elif tipo == 'pergaminho':
        cam.append(_ceu('radial-gradient(ellipse 75% 70% at 50% 45%,#F3E6C6 0%,#E9D6AA 60%,#C9A975 100%)',
                        '<div class="grao"></div><div class="rosa"></div>'))
        linhas = ''.join(f'<path d="M0 {y} C420 {y - 40} 1260 {y + 40} {L} {y}" stroke="#8A6A3A" stroke-width="1.5" fill="none" opacity=".22"/>'
                         for y in range(80, 1900, 150))
        rota = (f'<path class="rota" pathLength="1" d="M{_PAN + 150} 1800 C{_PAN + 280} 1690 {_PAN + 240} 1580 {_PAN + 460} 1540 '
                f'S{_PAN + 820} 1640 {_PAN + 930} 1460" fill="none" stroke="#B5523B" stroke-width="5" stroke-linecap="round" stroke-dasharray="1 1"/>')
        cam.append(f'<div class="cam" data-vel="2" style="top:0;bottom:auto;height:1920px"><svg width="{L}" height="1920">{linhas}{rota}</svg></div>')
    elif tipo in SALAS:
        import bonecos
        if tipo == 'rua_noite':
            cam.append(_ceu('linear-gradient(#0B1530 0%,#1A2A55 55%,#3B4A7A 100%)',
                            '<div class="astro lua" style="top:120px;background:#F3EBCF;box-shadow:0 0 70px 14px #F3EBCF40"></div>'))
            cam.append(_estrelas(rnd, 70))
            cam.append('<div class="cadente"></div>')
        if tipo in ('rua', 'rua_tarde'):
            tarde = tipo == 'rua_tarde'
            cam.append(_ceu('linear-gradient(#3C3F6B 0%,#B9627A 40%,#F0A35E 66%,#F7D49A 100%)' if tarde
                            else 'linear-gradient(#8FC1D4 0%,#C9E0E4 50%,#EEE7D6 100%)',
                            f'<div class="astro" style="top:{240 if tarde else 70}px;background:{"#FFE3A8" if tarde else "#FFF8E6"};box-shadow:0 0 90px 30px {"#FFE3A855" if tarde else "#FFF8E655"}"></div>'))
            cam.append(_nuvens(rnd, '#F6B98C' if tarde else '#FFFFFF', 5))
            cam.append(_aves(rnd, '#3A2238' if tarde else '#2E3B4A', 4))
        camadas, frente = bonecos.fundo(tipo, seed, op)
        cam += camadas
        cam.append('<!--AMB-->')
        if frente:
            cam.append(frente)
    elif tipo == 'capitulo':
        cam.append(_ceu('radial-gradient(ellipse 70% 60% at 50% 42%,#2B3F7A 0%,#16244C 55%,#0A1230 100%)',
                        '<div class="raios"></div>'))
        cam.append(_estrelas(rnd, 70))
        cam.append(_brasas(rnd, 44))
    fundo = ''.join(x for x in cam if x.startswith(('<div class="ceu"', '<div class="aves"', '<div class="cadente"', '<div class="brasas"'))
                    or 'class="cam est"' in x or 'class="cam nuv"' in x)
    pais = ''.join(x for x in cam if x not in fundo)
    # .mundo = o desenho inteiro; no GL/IN os ambientes (SALAS, feitos em 1080x1920) encolhem nele pra caber texto + ação
    return (f'<div class="cenario"><div class="mundo{" sala" if tipo in SALAS else ""}">{fundo}<div class="pais">{pais}</div></div>'
            f'<div class="luzlat"></div><div class="vinheta"></div><div class="grao2"></div><div class="veu"></div></div>')



def _vida(cid, cen, t0, t1, js_cena):
    """Tweens dos elementos vivos da cena (todos dentro de [t0, t1])."""
    D = max(0.3, t1 - t0)
    out = []
    n = cen.count('class="ave"')
    for k in range(n):   # pássaros atravessam a tela batendo asa
        dur = 7.5 + 1.7 * k
        x0 = -120 - 260 * k + (t0 * 37 % 300)
        out.append(f"tl.fromTo('#{cid} .ave:nth-of-type({k + 1})',{{x:{x0:.0f}}},{{x:{x0 + 1400 * D / dur:.0f},duration:{q(D)},ease:'none'}},{q(t0)});")
    if n:
        out.append(f"tl.fromTo('#{cid} .asa',{{scaleY:1}},{{scaleY:-0.35,duration:0.22,ease:'sine.inOut',yoyo:true,repeat:{int(D / 0.22)},transformOrigin:'50% 50%'}},{q(t0)});")
    for k, (v, x) in enumerate(re.findall(r'class="carro" data-v="([-\d.]+)" data-x="([\d.]+)"', cen)):
        v = float(v)
        out.append(f"tl.fromTo('#{cid} .carro:nth-of-type({k + 1})',{{x:0}},{{x:{v * D:.0f},duration:{q(D)},ease:'none'}},{q(t0)});")
    if 'class="pj"' in cen:   # janelas acendendo/apagando
        out.append(f"tl.fromTo('#{cid} .pj',{{opacity:1}},{{opacity:0.15,duration:0.8,ease:'steps(1)',yoyo:true,repeat:{max(1, int(D / 0.8))},stagger:{{each:0.53,repeat:0}}}},{q(t0)});")
    if 'class="tw"' in cen:   # estrelas piscando
        out.append(f"tl.fromTo('#{cid} .tw',{{opacity:1}},{{opacity:0.2,duration:0.7,ease:'sine.inOut',yoyo:true,repeat:{max(1, int(D / 0.7))},stagger:{{each:0.21,repeat:0}}}},{q(t0)});")
    if 'class="cadente"' in cen and D > 2.2:   # estrela cadente, uma por cena
        tc = t0 + min(1.2, D - 1.0)
        out.append(f"tl.fromTo('#{cid} .cadente',{{opacity:0,x:0,y:0}},{{opacity:1,x:-260,y:115,duration:0.35,ease:'power1.in'}},{q(tc)});")
        out.append(f"tl.to('#{cid} .cadente',{{opacity:0,duration:0.25}},{q(tc + 0.35)});")
    if 'class="seg"' in cen:
        out.append(f"tl.fromTo('#{cid} .seg',{{rotation:{t0 * 6 % 360:.0f}}},{{rotation:{t0 * 6 % 360 + 6 * D:.0f},duration:{q(D)},ease:'steps({max(1, int(D))})',svgOrigin:'0 0'}},{q(t0)});")
    if 'class="folha"' in cen:
        out.append(f"tl.fromTo('#{cid} .folha',{{rotation:-3}},{{rotation:3,duration:1.6,ease:'sine.inOut',yoyo:true,repeat:{max(1, int(D / 1.6))},svgOrigin:'0 0'}},{q(t0)});")
    if 'class="br"' in cen:   # brasas subindo (mais rápidas e balançando: a cartela nunca fica parada)
        out.append(f"tl.fromTo('#{cid} .br',{{y:0,opacity:0}},{{y:-1100,opacity:1,duration:2.2,ease:'none',stagger:{{each:0.09,repeat:{max(1, int((D + 1.5) / 2.2))}}}}},{q(t0 - 1.5)});")
        out.append(f"tl.fromTo('#{cid} .br',{{x:-14}},{{x:14,duration:0.7,yoyo:true,repeat:{max(1, int(D / 0.7))},ease:'sine.inOut',stagger:0.05}},{q(t0)});")
    if 'class="rota"' in cen:
        out.append(f"tl.fromTo('#{cid} .rota',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{q(max(0.6, D - 0.3))},ease:'power1.inOut'}},{q(t0 + 0.2)});")
    if 'class="pend"' in cen:
        out.append(f"tl.fromTo('#{cid} .pend',{{rotation:-1.4}},{{rotation:1.4,duration:2.2,yoyo:true,repeat:{max(1, int(D / 2.2))},ease:'sine.inOut',svgOrigin:'0 0',stagger:0.4}},{q(t0)});")
    if 'class="copa"' in cen:
        out.append(f"tl.fromTo('#{cid} .copa',{{x:-3}},{{x:3,duration:1.8,yoyo:true,repeat:{max(1, int(D / 1.8))},ease:'sine.inOut',stagger:0.3}},{q(t0)});")
    if 'class="rosa"' in cen:
        out.append(f"tl.fromTo('#{cid} .rosa',{{rotation:0}},{{rotation:{3 * D:.0f},duration:{q(D)},ease:'none'}},{q(t0)});")
    # objetos (ícones) nunca parados: depois de entrar, flutuam devagar
    for iid, tt in re.findall(r"(?:pop|revela|entra)\('#(c\d+-i\d+)',([\d.]+)", ' '.join(js_cena)):
        ini = float(tt) + 0.5
        if ini < t1 - 0.4:
            out.append(f"tl.to('#{iid}',{{y:-10,duration:1.1,ease:'sine.inOut',yoyo:true,repeat:{max(1, int((t1 - ini) / 1.1))}}},{q(ini)});")
    return out

# ================================================================ ESTILO
def _fonte(nome, tam, larg=None, peso=None):
    f = ImageFont.truetype(str(_FONTES[nome]), tam)
    if larg:
        f.set_variation_by_axes([36, larg, peso, 0])
    return f


def _ajusta(m):
    """Bold = TikTok Sans 800 na largura 75 (condensada, em caixa alta); apoio = EB Garamond (medida com 6 % de folga).
    Nunca passa de 860 px (margem lateral ≥ 100 px, regra de 23/10)."""
    cls, tam, miolo_ = m.group(1), int(m.group(2)), m.group(3)
    fino = 'fino' in cls
    txt = _html.unescape(re.sub(r'<[^>]+>', '', miolo_))
    alvo = round(tam * (1.38 if fino else 1.12))   # 06/11: apoio em serifa subiu 2x (rodada 5: ~88 px, letra ~55 px)
    while alvo > (54 if fino else 30):
        f = _fonte('EBGaramond-400.woff2', alvo) if fino else _fonte('TikTokSans-Variable.ttf', alvo, 75, 800)
        larg_ = f.getlength(txt) * 1.06 if fino else f.getlength(txt.upper()) + 0.01 * alvo * len(txt)   # + letter-spacing .01em
        if larg_ <= (790 if fino else 820):   # rodada 6: o revisor mediu 856 px com o limite antigo (faltava o espaçamento)
            break
        alvo -= 2
    return f'<div class="ln{cls}" style="font-size:{alvo}px">{miolo_}</div>'


def _pe_letreiro(c, fmt):
    """08/11 (margem segura): y do MUNDO (camada de ação, 1080x1920) logo abaixo do que o miolo mostra no alto da cena
    (capítulo + letreiro + data), pra peça encaixada (bo.encaixa) nunca ficar por cima do texto. Conta igual ao CSS:
    RL cheia = miolo no y 540 (calibrado no t68: topo 526–540); GL/YT = 140 e letreiro em escala .86 (mundo encolhido
    0,6585 a partir do chão); IN = 200, escala .92 (mundo 0,8133)."""
    h = 0.0
    n = 0
    for cls, tam in re.findall(r'<div class="ln((?: fino)?(?: forte)?)" style="font-size:(\d+)px">', c.html):
        h += int(tam) * (1.15 if 'fino' in cls else 1.02) + 4
        n += 1
    h += 6 * max(0, n - 1)
    if 'class="kap"' in c.html:
        h += 70
    dn = {'GL': 180, 'YT': 180, 'IN': 210}.get(fmt, 330)
    if 'class="data"' in c.html:
        h += 30 + dn * 1.1 + (60 if 'class="dl"' in c.html else 0)
    if fmt in ('GL', 'YT'):
        return 1920 - (1080 - (TOPO_LET['GL'] + h * ESC_LET['GL'])) / _esc_mundo('GL')
    if fmt == 'IN':
        return 1920 - (1350 - (TOPO_LET['IN'] + h * ESC_LET['IN'])) / _esc_mundo('IN')
    return 540 + h


# 12/11/2026 — REGRA DO USUÁRIO (caso real): texto NUNCA lá em cima (o Instagram tampa), nunca baixo demais, nunca na
# altura do rosto. RL: topo ≥ 320 (o letreiro já fica em ~526); nos outros longe do topo (~15 %: IN ≥ 200, GL/YT ≥ 160;
# antes ~126/186). O miolo sobe 14 px ao longo da cena e a caixa da letra passa ~6–15 px acima da linha (medido no g22),
# por isso o letreiro começa ~30 px abaixo do limite (antes: GL/YT 140, IN 200). checar_margem.mjs confere (CAIXA_TEXTO).
# Pra o letreiro mais baixo não cair em cima dos objetos de parede (quadro, máquina, TV, mapa — 1ª tentativa, folha do
# g22), ele encolhe um pouco (ESC_LET, antes .86/.92) e o ambiente mostra um pouco mais do alto do mundo (TOPO_MUNDO,
# antes 280/260): 240 é o máximo sem abrir faixa escura nas laterais (as camadas têm 300 px de sobra).
TOPO_LET = {'GL': 194, 'YT': 194, 'IN': 232}
ESC_LET = {'GL': 0.78, 'YT': 0.78, 'IN': 0.86}
TOPO_MUNDO = {'GL': 240, 'YT': 240, 'IN': 240}


def _esc_mundo(fmt):
    return {'GL': 1080, 'YT': 1080, 'IN': 1350}[fmt] / (1920 - TOPO_MUNDO[fmt])


def _css_mundo(h, topo):
    """GL/IN: o ambiente (desenhado em 1080x1920) encolhe pra mostrar do y `topo` do mundo até o chão; as camadas têm
    300 px de sobra de cada lado, então a largura continua cheia. Texto em cima (miolo), ação embaixo, nada cortado."""
    esc = h / (1920 - topo)
    return (f'.mundo.sala{{inset:auto;left:50%;bottom:0;width:1080px;height:1920px;margin-left:-540px;transform:scale({esc:.4f});'
            f'transform-origin:50% 100%}}.mundo.sala .ceu{{left:-300px;right:-300px}}')


def _css(fmt):
    alt_cena = {'GL': 1080, 'IN': 1350}.get(fmt, 960)
    extra = ''
    if fmt == 'IN':
        extra += '#palco,.cena{height:1350px}.miolo{height:1350px;padding:250px 100px 420px}'
        extra += _css_mundo(1350, TOPO_MUNDO['IN']) + '.data .dn{font-size:210px}.data{margin-top:6px}'
        extra += f'.cena .miolo{{padding-top:{TOPO_LET["IN"]}px !important}}.let{{transform:scale({ESC_LET["IN"]});transform-origin:50% 0}}'
    elif fmt in ('GL', 'YT'):
        extra += '.miolo{padding:150px 100px 330px}'
        extra += _css_mundo(1080, TOPO_MUNDO['GL']) + '.data .dn{font-size:180px}.data{margin-top:0}.data .dl{font-size:28px}'
        if fmt == 'YT':
            extra += '#divisoria{background:#0A0F1E !important}'
        # 06/11: o `.cena .miolo` do estilo (padding 235) ganhava do GL; o letreiro sobe e encolhe um pouco pra caber acima
        # dos objetos de parede (que no GL começam em y ~380)
        extra += f'.cena .miolo{{padding-top:{TOPO_LET["GL"]}px !important}}.let{{transform:scale({ESC_LET["GL"]});transform-origin:50% 0}}'
    temas = []
    for tipo, (claro, cor, apoio, chave, obj, dest) in TEMAS.items():
        sombra = '0 2px 0 rgba(255,255,255,.35)' if claro else '0 3px 14px rgba(0,0,0,.55),0 2px 0 rgba(0,0,0,.35)'
        temas.append(f'.t-{tipo} .let .ln{{color:{cor};text-shadow:{sombra}}}.t-{tipo} .let .ln.fino{{color:{apoio}}}'
                     f'.t-{tipo} .let .w.k{{color:{chave}}}.t-{tipo} .ic.ph{{fill:{obj}}}.t-{tipo} .ic.ph.verde{{fill:{dest}}}'
                     f'.t-{tipo} .ic:not(.ph){{stroke:{obj}}}.t-{tipo} .kap{{color:{cor}}}.t-{tipo} .kap .kf{{background:{chave}}}')
    import bonecos   # cenas com gente (06/11); importado aqui pra não dar import circular
    return bonecos.CSS + f"""
@font-face{{font-family:'Cond';src:url('fonts/TikTokSans-Variable.ttf') format('truetype');font-weight:300 900;font-stretch:75% 150%;font-display:block}}
@font-face{{font-family:'Garamond';src:url('fonts/EBGaramond-400.woff2') format('woff2');font-weight:400;font-display:block}}
@font-face{{font-family:'Garamond';src:url('fonts/EBGaramond-700.woff2') format('woff2');font-weight:700;font-display:block}}
@font-face{{font-family:'Cinzel';src:url('fonts/Cinzel-700.woff2') format('woff2');font-weight:700;font-display:block}}
html,body,#root{{background:#0A0F1E}}
.mundo{{position:absolute;inset:0}}
.amb{{position:absolute;left:0;bottom:0;width:1080px;height:1920px;pointer-events:none}}.amb svg{{display:block;overflow:visible}}.amb svg svg{{overflow:hidden}}
text.tc{{font-family:'Cond',sans-serif;font-weight:800;font-stretch:75%}}text.tg{{font-family:'Garamond',serif;font-weight:700}}
{''.join(f'.cheia.t-{t_} .pais{{transform:none}}' for t_ in SALAS)}
.cena{{background:#0A0F1E}}
.cenario{{position:absolute;inset:0;overflow:hidden;transform-origin:50% 100%}}
.ceu{{position:absolute;inset:0}}
.cam{{position:absolute;left:-{_PAN}px;bottom:0;width:{1080 + 2 * _PAN}px}}
.cam svg{{display:block}}
.astro{{position:absolute;right:110px;top:70px;width:110px;height:110px;border-radius:50%}}
.astro.lua{{width:96px;height:96px}}
.raios{{position:absolute;left:50%;top:42%;width:2600px;height:2600px;margin:-1300px 0 0 -1300px;background:repeating-conic-gradient(from 0deg,rgba(255,236,190,.07) 0deg 6deg,transparent 6deg 15deg);-webkit-mask-image:radial-gradient(circle,#000 0%,transparent 55%);mask-image:radial-gradient(circle,#000 0%,transparent 55%)}}
.grao{{position:absolute;inset:0;opacity:.35;background-image:radial-gradient(rgba(90,60,20,.25) 1px,transparent 1.4px);background-size:7px 7px}}
.rosa{{position:absolute;right:-120px;bottom:-120px;width:520px;height:520px;border-radius:50%;border:3px solid rgba(110,80,40,.18);background:repeating-conic-gradient(rgba(110,80,40,.10) 0deg 2deg,transparent 2deg 22.5deg)}}
.pais{{position:absolute;inset:0;transform-origin:50% 100%}}.cheia .miolo{{padding-top:60px !important}}.cheia .ic.ph{{scale:1.3}}.cheia .let .ln{{margin:2px 0}}.cheia .pais{{transform:scale(1.75)}}.cheia.t-interior .pais{{transform:scale(1.25)}}.cheia .data .dn{{font-size:330px}}
.aves{{position:absolute;left:0;top:0;width:1080px;height:420px;pointer-events:none}}.cadente{{position:absolute;left:640px;top:90px;width:180px;height:3px;border-radius:2px;opacity:0;background:linear-gradient(90deg,rgba(255,255,255,0),#fff);transform:rotate(-24deg)}}.brasas{{position:absolute;inset:0;pointer-events:none}}.brasas .br{{position:absolute;border-radius:50%;background:#F2B544;box-shadow:0 0 10px 3px rgba(242,181,68,.55);opacity:0}}
.veu{{position:absolute;inset:0;background:#05080F;opacity:0;pointer-events:none}}
.let .w{{display:none}}
/* rodada 5 (revisor: "cara de banco de imagem"): look da referência — dessaturado e quente, luz baixa vindo da esquerda,
   vinheta suave e grão leve. Sem blur. */
.mundo{{filter:saturate(.72) sepia(.16) contrast(1.05) brightness(.88)}}
.luzlat{{position:absolute;inset:0;pointer-events:none;background:linear-gradient(100deg,rgba(255,206,130,.17) 0%,rgba(255,206,130,0) 34%,rgba(20,10,0,0) 52%,rgba(20,10,0,.34) 100%)}}
.vinheta{{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse 78% 70% at 48% 46%,rgba(0,0,0,0) 58%,rgba(18,10,2,.42) 100%)}}
.grao2{{position:absolute;inset:-40px;pointer-events:none;opacity:.10;mix-blend-mode:overlay;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/></filter><rect width='240' height='240' filter='url(%23n)'/></svg>")}}
.cena .miolo{{z-index:2;justify-content:flex-start;padding:235px 100px 280px;gap:30px}}
.let{{display:flex;flex-direction:column;align-items:center;gap:6px;line-height:1}}
.let .ln{{font-family:'Cond',sans-serif;font-weight:800;font-stretch:75%;text-transform:uppercase;letter-spacing:.01em;line-height:1.02}}
.let .ln.fino{{font-family:'Garamond',serif;font-weight:400;font-stretch:100%;text-transform:none;letter-spacing:0;line-height:1.15;font-style:normal}}
.let .ln.fino.forte{{font-weight:700}}
.let .w.k{{-webkit-background-clip:border-box;background-clip:border-box;background-image:none}}
.let .ln:has(>.risco){{position:relative}}.let .risco{{position:absolute;left:-2%;width:104%;top:50%;height:.2em;margin-top:-.07em;pointer-events:none;color:inherit;z-index:1;transform:rotate(-1.2deg)}}.let .risco svg{{display:block;width:100%;height:100%;overflow:visible}}.let .risco svg path{{fill:currentColor}}
.ic.ph{{overflow:visible;filter:drop-shadow(0 12px 0 rgba(0,0,0,.16))}}
.kap{{display:flex;align-items:center;gap:22px;font-family:'Cinzel',serif;font-weight:700;font-size:38px;letter-spacing:.32em;margin-bottom:6px}}
.kap .kf{{display:block;width:90px;height:2px;opacity:.85}}
.data{{display:flex;flex-direction:column;align-items:center;gap:10px;margin-top:26px;position:relative;isolation:isolate}}
.data .mancha{{position:absolute;left:50%;top:50%;width:640px;height:420px;margin:-250px 0 0 -320px;z-index:-1;fill:#5A4126;fill-opacity:.15;overflow:visible}}
.t-noite .data .mancha,.t-capitulo .data .mancha,.t-cidade_noite .data .mancha,.t-tarde .data .mancha,.t-rua_noite .data .mancha,.t-sala_noite .data .mancha,.t-quarto_noite .data .mancha,.t-escritorio_noite .data .mancha{{fill:#F2B544;fill-opacity:.12}}
.data .dn{{font-family:'Garamond',serif;font-weight:700;font-size:250px;line-height:1.1;color:#3A2A1A;letter-spacing:-.01em;text-shadow:2px 3px 0 rgba(120,80,30,.18)}}
.t-noite .data .dn,.t-capitulo .data .dn,.t-cidade_noite .data .dn,.t-tarde .data .dn,.t-rua_noite .data .dn,.t-sala_noite .data .dn,.t-quarto_noite .data .dn,.t-escritorio_noite .data .dn{{color:{OURO};text-shadow:0 4px 18px rgba(0,0,0,.5)}}
.data .dl{{font-family:'Cinzel',serif;font-weight:700;font-size:38px;letter-spacing:.22em;color:#5A4126}}
.t-noite .data .dl,.t-capitulo .data .dl,.t-cidade_noite .data .dl,.t-tarde .data .dl,.t-rua_noite .data .dl,.t-sala_noite .data .dl,.t-quarto_noite .data .dl,.t-escritorio_noite .data .dl{{color:{CREME}}}
.rotulo{{position:absolute;left:100px;bottom:100px;display:flex;align-items:center;gap:20px;z-index:3;padding:14px 30px 14px 20px;border-radius:16px;background:rgba(10,15,30,.55)}}
.rotulo .rt{{font-family:'Cond',sans-serif;font-weight:800;font-stretch:75%;font-size:54px;color:#FBF6EA;text-transform:uppercase;letter-spacing:.02em;text-shadow:0 2px 10px rgba(0,0,0,.6)}}
.rotulo .rf{{display:block;height:2px;width:100%;background:{OURO};transform-origin:0 50%;margin:4px 0 6px}}
.rotulo .rs{{font-family:'Cinzel',serif;font-weight:700;font-size:36px;letter-spacing:.2em;color:#E9DFC9;text-transform:uppercase;text-shadow:0 2px 8px rgba(0,0,0,.6)}}
/* widgets do motor em cartão creme chapado */
.cartao{{background:#FBF4E4 !important;border:none !important;border-radius:20px !important;box-shadow:0 14px 0 rgba(0,0,0,.14)}}
.cartao .kick,.kick,.rot{{color:#6A5A44 !important;font-family:'Cinzel',serif}}
.cartao svg polyline,.cartao svg path{{stroke:{FERRUGEM}}}
.barra{{background:#2D4A63 !important;border-radius:8px 8px 3px 3px !important}}
.barras .barra:last-child{{background:{FERRUGEM} !important}}
.bolha{{font-family:'Garamond',serif;box-shadow:0 8px 0 rgba(0,0,0,.14)}}
.bolha.in{{background:#FBF4E4 !important;color:{TINTA} !important}}
.bolha.out{{background:{OURO} !important;color:{TINTA} !important}}
.digita{{background:#FBF4E4 !important}}
.chip{{background:#FBF4E4 !important;color:{TINTA} !important;font-family:'Cinzel',serif;font-weight:700;box-shadow:0 8px 0 rgba(0,0,0,.14)}}
.cel{{background:#FBF4E4 !important;border-color:#E2D2B0 !important}}
.av,.avatar{{background:#FBF4E4 !important;border-color:#2D4A63 !important}}
.passo{{background:#FBF4E4 !important;border-color:#2D4A63 !important;color:{TINTA}}}
.tile{{border-color:rgba(0,0,0,.18)}}
.tile.gd{{background:#2D4A63;border-color:#2D4A63}}
.botao{{background:{FERRUGEM} !important;border:none !important;color:#FBF6EA;font-family:'Cond',sans-serif;font-weight:800;font-stretch:75%;text-transform:uppercase;box-shadow:0 12px 0 rgba(0,0,0,.22) !important}}
.botao .pontos{{display:none}}.botao .bt-verde{{background:#7E3526 !important}}
.selo{{background:{FERRUGEM} !important}}
.moeda{{border-color:#8E6B22 !important;background:{OURO} !important}}
.val,.val.g{{color:{TINTA} !important;font-family:'Cond'}}
{''.join(temas)}
{extra}
"""


JS_ANIM = """
// Edição animada: palavra sobe e acende devagar (sem trocar de cor: a cor vem do tema do cenário)
function palavra0(s,t,cor){tl.set(s,{display:'inline-block',opacity:1,y:0},0);}
function palavra(s,t,cor){tl.set(s,{display:'inline-block'},t);tl.fromTo(s,{opacity:0,y:16},{opacity:1,y:0,duration:0.24,ease:'power2.out'},t);}
function pop(s,t,st){tl.fromTo(s,{opacity:0,scale:0.5,y:40},{opacity:1,scale:1,y:0,duration:0.45,ease:'back.out(1.7)',stagger:st||0,transformOrigin:'50% 100%'},t);}
function revela(s,t,d){tl.fromTo(s,{opacity:0,y:50},{opacity:1,y:0,duration:d||0.45,ease:'power3.out'},t);}
"""


def _dur_wav(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def _audios():
    """Efeitos em <audio>, trilhas 11–16 sem sobreposição; mínimo de 0,28 s entre dois sons (prioridade abaixo)."""
    pub = motor.AQUI / 'public/sfx'
    pub.mkdir(exist_ok=True)
    fim_trilha = {k: -1.0 for k in range(11, 17)}
    PRI = {'impacto_ar': 0, 'impacto': 0, 'tique': 1, 'pop2': 1, 'madeira': 1, 'pop': 2, 'respiro': 2, 'transicao': 3, 'swish': 3}
    aceitos, tags = [], []
    for t, nome, vol in sorted(SFX, key=lambda x: (PRI.get(x[1], 2), x[0])):
        longo = nome in ('respiro', 'riser', 'whoosh_lento')   # sons que crescem antes do corte podem encostar em outro
        if (not longo and any(abs(t - a) < 0.28 for a in aceitos)) or t >= motor.DUR - 0.2 or t < 0:
            continue
        aceitos.append(t)
        src = _SFX_DIR / f'{nome}.wav'
        if not (pub / src.name).exists():
            shutil.copy(src, pub / src.name)
        d = round(min(_dur_wav(src), motor.DUR - t - 0.05), 3)
        trilha = next((k for k, f in fim_trilha.items() if f <= t), None)
        if trilha is None:
            continue
        fim_trilha[trilha] = t + d + 0.01
        tags.append(f'<audio id="sfx{len(tags)}" src="sfx/{src.name}" data-start="{t}" data-duration="{d}" '
                    f'data-track-index="{trilha}" data-volume="{vol}"></audio>')
    return '\n      '.join(tags)


# ================================================================ PESSOA CHEIO: cortes do tratado e legenda padrão (12/11/2026)
_PUNCH = []   # (índice da cena da pessoa, tempo do corte) — corte seco no meio da frase dele


def _cortes_pessoa(cenas, pessoa_ids):
    """12/11/2026 (usuário, caso real "teve um erro de corte por volta de 0:22"). Causa: a pessoa entrava em 20,567 s, mas
    o corte seco do tratado (take aberto -> take fechado) só aparece no quadro de 20,667 — 3 quadros do take ANTERIOR e
    um pulo de enquadramento logo no começo da frase. Regra (troca de modo/corte só no início ou fim de frase):
      - corte entre a entrada da pessoa e o começo da 1ª palavra dele (+0,12 s) -> a pessoa entra NO quadro do corte;
      - corte depois da última palavra e antes da saída -> a pessoa sai no quadro do corte (a animação volta ali);
      - corte no MEIO da frase -> punch-in leve (falso corte, PUNCH_PESSOA) no RL; no GL/IN/YT o zoom do motor já troca
        de plano no corte (agora no quadro exato, motor.CORTES_PESSOA).
    Os quadros vêm de pessoa_cheio.cortes_quadros (o cortes_visuais.json é aproximado)."""
    _PUNCH.clear()
    if not motor.GNN:
        return
    import pessoa_cheio
    cq = [f / motor.FPS for f in pessoa_cheio.cortes_quadros(motor.GNN)]
    motor.CORTES_PESSOA = cq
    for k, c in enumerate(cenas):
        if c.id not in pessoa_ids:
            continue
        w0, we = float(motor.W[c.i0]['s']), float(motor.W[c.i1]['e'])
        for tc in cq:
            t1 = cenas[k + 1].t0 if k + 1 < len(cenas) else motor.DUR
            if not (c.t0 - 0.001 < tc < t1 - 0.001):
                continue
            if tc <= w0 + 0.12:
                if tc > c.t0 + 0.001:
                    print(f'  corte seco em {tc:.3f} s: {c.id} (pessoa) entra no quadro do corte (era {c.t0:.3f})')
                    c.t0 = q(tc)
            elif tc >= we + 0.03 and k + 1 < len(cenas):
                print(f'  corte seco em {tc:.3f} s: {c.id} (pessoa) sai no quadro do corte (era {t1:.3f})')
                cenas[k + 1].t0 = q(tc)
            else:
                print(f'  corte seco em {tc:.3f} s no meio da frase de {c.id} (pessoa): punch-in leve {PUNCH_PESSOA}')
                _PUNCH.append((k, tc))


# legenda padrão do básico (work/criativo.py, leg_estilo=None): TikTok Sans 650, branca, sombra 0,55/6/2 (= CSS 0 2px
# 12px), corpo/baseline por formato — RL 16:9 = leg169 (66, 1260) limitada à linha de 65 % (1228); IN/GL 51 px a 63,4 %
# da altura; YT 62 px a 86 %. Nos 4 formatos o topo do texto fica ≥ 40 px abaixo do queixo (no peito; RL pelo p95 da cena, base ≤ ~1480)
# (o recorte já usa a altura inteira, não dá pra tirar zoom) — uma altura por cena, nunca muda no meio da frase.
_LEG_FMT = {'RL': (66, None), 'IN': (51, 0.634), 'GL': (51, 0.634), 'YT': (62, 0.86)}
_LEG_MARGEM = {'IN': 150, 'GL': 120, 'YT': 120}
_FRACAS = {'de', 'da', 'do', 'das', 'dos', 'a', 'o', 'as', 'os', 'à', 'às', 'um', 'uma', 'e', 'ou', 'mas', 'que', 'para', 'pra', 'com',
           'em', 'no', 'na', 'nos', 'nas', 'por', 'pelo', 'pela', 'seu', 'sua', 'meu', 'minha', 'se', 'sem', 'ao', 'aos',
           'até', 'pelos', 'pelas', 'num', 'numa', 'dum', 'duma', 'sobre', 'entre', 'desde', 'contra', 'após', 'sob',
           'seus', 'suas', 'meus', 'minhas', 'nosso', 'nossa', 'teu', 'tua'}   # = work/auditar_legenda.py (+ possessivos)
_FRACAS2 = {'não', 'eu', 'te', 'me', 'lhe', 'você', 'ele', 'ela', 'muito', 'mais', 'tão'}   # fim de bloco ruim (prende no verbo)
_INICIO = {'e', 'que', 'como', 'quando', 'onde', 'porque', 'mas', 'para', 'pra', 'aqui', 'quanto', 'qual', 'quem', 'se',
           'ou', 'então', 'só', 'sem', 'com', 'pelo', 'pela'}   # bom começo de bloco (quebra antes deles)
_GENIT = {'de', 'do', 'da', 'dos', 'das'}   # "campanha | de tráfego" separa o que é um nome só


def _nw(w):
    """Palavra pra comparar com as listas: minúscula, sem pontuação, COM acento ('é' verbo != 'e' conjunção)."""
    return re.sub(r'[^\wÀ-ÿ%]', '', w.lower())


def _fonte_leg(tam):
    f = ImageFont.truetype(str(_FONTES['TikTokSans-Variable.ttf']), tam)
    f.set_variation_by_axes([36, 100, 650, 0])
    return f


def _tokens(c=None):
    """Palavras da cena (motor.W já com as correções do gerar.py; 'Tem IA' vira 2, '' some); c=None = o vídeo todo.
    Cada uma leva 'g' = índice no vídeo todo (pra casar com a legenda do básico)."""
    out = []
    for i in range(len(motor.W)):
        p = motor.W[i]
        ps = str(p['w']).split()
        s, e = float(p['s']), float(p['e'])
        for j, w in enumerate(ps):
            out.append({'w': w, 's': s + (e - s) * j / len(ps), 'e': s + (e - s) * (j + 1) / len(ps), 'i': i,
                        'g': len(out)})
    return out if c is None else [t for t in out if c.i0 <= t['i'] <= c.i1]


_BAS = {}


def _blocos_basico():
    """Legenda REVISADA da versão básica do mesmo vídeo (work/*/cfg/<id>.py, CFG['frases'], já passou pelos revisores
    de texto e forma): devolve {índice g da palavra: (nº do bloco, palavra como está no básico)}. Vazio se não achar."""
    if motor.GNN in _BAS:
        return _BAS[motor.GNN]
    import difflib
    import runpy
    res = {}
    for cfg in sorted((RAIZ / 'work').glob(f'*/cfg/{motor.GNN}.py')):
        try:
            CFG = runpy.run_path(str(cfg)).get('CFG') or {}
        except Exception as e:
            print(f'  AVISO legenda: não li {cfg.relative_to(RAIZ)} ({e})')
            continue
        if CFG.get('id') != motor.GNN or not CFG.get('frases'):
            continue
        blocos = [p.strip() for ln in CFG['frases'].strip().split('\n') for p in ln.split('|') if p.strip()]
        bt = [(motor.norm(w), k, w) for k, b in enumerate(blocos) for w in b.split()]
        at = _tokens()
        sm = difflib.SequenceMatcher(None, [motor.norm(t['w']) for t in at], [x[0] for x in bt], autojunk=False)
        for op, a0, a1, b0, b1 in sm.get_opcodes():
            if op == 'equal' or (op == 'replace' and a1 - a0 == b1 - b0):
                for da in range(a1 - a0):
                    res[at[a0 + da]['g']] = (bt[b0 + da][1], bt[b0 + da][2])
        print(f'  legenda da pessoa: quebras da versão básica ({cfg.relative_to(RAIZ)}), {len(res)}/{len(at)} palavras casadas')
        break
    _BAS[motor.GNN] = res
    return res


def _quebra_basico(toks):
    """Agrupa as palavras da cena pelos blocos do básico; bloco com mais de 4 palavras é requebrado (_quebra_auto)."""
    bas = _blocos_basico()
    if not bas or not all(t['g'] in bas for t in toks):
        return None
    grupos, ult = [], None
    for t in toks:
        k, w = bas[t['g']]
        t = dict(t, w=w)
        if k != ult:
            grupos.append([])
            ult = k
        grupos[-1].append(t)
    out = []
    for g in grupos:
        out += [g] if len(g) <= 4 else _quebra_auto(g)
    return out


def _quebra_auto(toks):
    """Blocos de 1–4 palavras pelo sentido: quebra obrigatória na pontuação (, . ? ! : ;); dentro da oração, menor custo
    (nunca termina em artigo/preposição/conjunção/'que'; nem em 'não'/'eu'/'te'; prefere quebrar antes de 'e', 'que',
    'como', 'aqui'...; evita separar 'X de Y'; prefere 2–3 palavras e bloco que não pisca, ≥ 0,28 s)."""
    oracoes, cur = [], []
    for t in toks:
        cur.append(t)
        if re.search(r'[,.;:?!…]$', t['w']):
            oracoes.append(cur)
            cur = []
    if cur:
        oracoes.append(cur)
    blocos = []
    for o in oracoes:
        n = len(o)
        best = [0.0] + [1e9] * n
        de = [0] * (n + 1)
        for j in range(1, n + 1):
            for i in range(max(0, j - 4), j):
                b = o[i:j]
                nb = len(b)
                custo = 1.0 + {1: 2.5, 2: 0.2, 3: 0.0, 4: 0.5}[nb]
                fim = _nw(b[-1]['w'])
                if j < n:   # quebra dentro da oração
                    if fim in _FRACAS:
                        custo += 20
                    elif fim in _FRACAS2:
                        custo += 6
                    prox = _nw(o[j]['w'])
                    if prox in _INICIO:
                        custo -= 0.6
                    if prox in _GENIT:
                        custo += 2.5
                    # "um dia | normal", "no modo | avião": artigo/possessivo + nome, e a palavra seguinte ainda é do
                    # mesmo nome (não é começo de oração nem preposição) -> não separa
                    if nb >= 2 and _nw(b[-2]['w']) in _FRACAS - {'e', 'ou', 'mas', 'que', 'se'} \
                            and prox not in _INICIO | _FRACAS:
                        custo += 2.0
                    gap = o[j]['s'] - b[-1]['e']
                    if gap >= 0.15:
                        custo -= min(1.0, gap * 3)
                    dur = o[j]['s'] - b[0]['s']
                    if dur < 0.28:
                        custo += 5
                    elif dur < 0.4:
                        custo += 1
                if best[i] + custo < best[j]:
                    best[j], de[j] = best[i] + custo, i
        cortes, j = [], n
        while j > 0:
            cortes.append((de[j], j))
            j = de[j]
        blocos += [o[a:b] for a, b in reversed(cortes)]
    return blocos


def _quebra_manual(c, toks, spec):
    """LEG_PESSOA[c.id] = 'bloco|bloco': as palavras têm que ser as da fala (sem pontuação/acento/maiúscula); o texto
    mostrado é o da spec (pra acertar grafia). Se não casar, avisa e usa a automática."""
    blocos, k = [], 0
    for parte in [p.strip() for p in spec.split('|') if p.strip()]:
        ws = parte.split()
        b = toks[k:k + len(ws)]
        if len(b) != len(ws) or any(motor.norm(a) != motor.norm(t['w']) for a, t in zip(ws, b)):
            print(f'  AVISO legenda {c.id}: "{parte}" não casa com a fala '
                  f'("{" ".join(t["w"] for t in toks[k:k + len(ws)])}") — usando a quebra automática')
            return None
        blocos.append([dict(t, w=w) for w, t in zip(ws, b)])
        k += len(ws)
    if k != len(toks):
        print(f'  AVISO legenda {c.id}: sobraram palavras ({" ".join(t["w"] for t in toks[k:])}) — usando a quebra automática')
        return None
    return blocos


def _face_cena(t0, t1):
    tr = json.load(open(RAIZ / 'work' / motor.GNN / 'face_track.json'))
    if not tr:
        return []
    wmed = float(np.median([p['w'] for p in tr]))
    return [p for p in tr if p['w'] >= 0.6 * wmed and t0 - 0.05 <= p['t'] <= t1 + 0.05]


def _legenda_pessoa(fmt, cenas, fims):
    """Monta (html, js, css) da legenda padrão nas cenas da pessoa em tela cheia. fmt = formato pedido (RL/IN/GL/YT)."""
    if not (LEGENDA_PESSOA and motor.CENAS_PESSOA_GL and motor.GNN):
        return '', '', ''
    W_, H_ = {'RL': (1080, 1920), 'IN': (1080, 1350), 'GL': (1080, 1080), 'YT': (1920, 1080)}[fmt]
    w_ = RAIZ / 'work' / motor.GNN
    horiz = (w_ / 'base_h.mov').exists()
    # escala vídeo-fonte -> tela do recorte que aparece nas cenas da pessoa (y começa em 0 em todos os recortes 16:9)
    S = {'RL': 1920 / 1080, 'IN': 1350 / 1080, 'GL': 1.0, 'YT': 1.0}[fmt] if horiz else None
    cq = list(motor.CORTES_PESSOA or [])
    tam0, frac = _LEG_FMT[fmt]
    divs, js = [], []
    for k, (c, t1) in enumerate(zip(cenas, fims)):
        if c.id not in motor.CENAS_PESSOA_GL:
            continue
        toks = [t for t in _tokens(c) if t['w']]
        if not toks:
            continue
        # quebra: manual do gerar.py (LEG_PESSOA) > a da versão básica revisada > automática pelo sentido
        blocos = ((_quebra_manual(c, toks, LEG_PESSOA[c.id]) if c.id in LEG_PESSOA else None)
                  or _quebra_basico(toks) or _quebra_auto(toks))
        txts = [' '.join(t['w'] for t in b) for b in blocos]
        # corpo: o básico encolhe de 2 em 2 até caber a ≥ 100 px de cada lateral (mín. 44)
        tam = tam0
        while tam > 44 and max(_fonte_leg(tam).getlength(x) for x in txts) > W_ - 200:
            tam -= 2
        f = _fonte_leg(tam)
        asc = max(-f.getbbox(x, anchor='ls')[1] for x in txts)
        desc = f.getmetrics()[1]
        base = (round(H_ * 0.65) - desc) if fmt == 'RL' else round(H_ * frac)
        if fmt == 'RL':
            base = min(1260, base)   # leg169 = (66, 1260), limitada à linha de 65 % (criativo.py, 09/11)
        ini = [max(c.t0, b[0]['s'] - 0.05) if i == 0 else b[0]['s'] for i, b in enumerate(blocos)]
        fim = ini[1:] + [t1]
        # altura: a PADRÃO do formato; só desce (como no básico, criativo.py) quando ia cobrir o rosto —
        #   RL: topo do texto ≥ 40 px abaixo do queixo (p95 da cena; com punch-in o rosto cresce a partir de 30 %),
        #   base ≤ 1500 − descendente (12/11: texto nunca na altura do rosto — no peito);
        #   IN/GL/YT: topo do texto ≥ 40 px abaixo do queixo (cy + 0,62·w), com o zoom do motor (base 1,06 × 1,03).
        # UMA altura por cena (a frase da pessoa é um plano só, como o "punch-in -> legenda y=" do básico): se algum
        # instante dela pede (mais de 8 px), a cena inteira desce até onde precisa; a legenda nunca pula entre blocos.
        face = _face_cena(c.t0, t1) if S else []
        p_ini = min([tc for kk, tc in _PUNCH if kk == k], default=None)

        def precisa(p):
            if fmt == 'RL':
                # 12/11 (regra do usuário: texto nunca na altura do rosto — no peito): o topo das letras ≥ 40 px abaixo
                # do queixo (cy + 0,62·w); com punch-in o rosto cresce a partir de 30 % da altura
                z = PUNCH_PESSOA if p_ini is not None and p['t'] >= p_ini else 1.0
                oy = 0.30 * H_
                return oy + ((p['cy'] + 0.62 * p['w']) * S - oy) * z + 40 + asc
            z = (1.06 if sum(1 for x in cq if x <= p['t']) % 2 else 1.0) * 1.03
            return (p['cy'] + 0.62 * p['w']) * S * z + 52 + asc
        # teto: RL base ≤ 1500 menos o descendente (o pé da letra fica dentro da caixa de texto, y ≤ 1500)
        lim = (1500 - desc) if fmt == 'RL' else (H_ - _LEG_MARGEM[fmt])
        nec = [(p['t'], precisa(p)) for p in face]
        alturas, motivo = [base] * len(blocos), ''
        if nec:
            # RL: p95 do queixo na cena (um instante de cabeça baixa não arrasta a cena toda); IN/GL/YT: o pior quadro
            ys = sorted(y for _, y in nec)
            alvo = ys[min(len(ys) - 1, int(round(0.95 * (len(ys) - 1))))] if fmt == 'RL' else ys[-1]
            if alvo > base + 8:
                yc = min(lim, round(alvo))
                alturas = [yc] * len(blocos)
                motivo = f' desce p/ {yc} (≥ 40 px abaixo do queixo{", p95" if fmt == "RL" else ""})'
        for i, (b, x) in enumerate(zip(blocos, txts)):
            a_, b_ = motor.fl(ini[i]), motor.fl(fim[i])
            if b_ - a_ < 0.28:
                print(f'  AVISO legenda {c.id}: bloco "{x}" fica só {b_ - a_:.2f} s (pisca)')
            lid = f'{c.id}-lt{i}'
            divs.append(f'<div class="lt" id="{lid}" data-cena="{c.id}" data-ini="{a_}" data-fim="{b_}" '
                        f'style="top:{alturas[i] - tam}px;font-size:{tam}px">{_html.escape(x)}</div>')
            js.append(f"tl.set('#{lid}',{{opacity:1}},{a_});tl.set('#{lid}',{{opacity:0}},{b_});")
        print(f'  legenda {c.id} ({fmt} {tam}px, base y {base}{";" + motivo if motivo else ""}): ' + ' | '.join(txts))
    if not divs:
        return '', '', ''
    # line-height 1,3 = ascendente (1,0 em) + descendente (0,3 em) da TikTok Sans: a linha de base fica em top + 1 em
    css = (f'#legpessoa{{position:absolute;left:0;top:0;width:{W_}px;height:{H_}px;pointer-events:none;z-index:7}}'
           f"#legpessoa .lt{{position:absolute;left:0;width:{W_}px;text-align:center;white-space:nowrap;font-family:'Cond',sans-serif;"
           'font-weight:650;font-stretch:100%;line-height:1.3;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.55);opacity:0}')
    return f'<div id="legpessoa">{"".join(divs)}</div>', '\n'.join(js), css


def aplicar():
    """Equivale ao montar() do motor + estilo Edição animada. Chamar no fim do gerar.py."""
    pub = motor.AQUI / 'public'
    (pub / 'fonts').mkdir(exist_ok=True)
    for nome, src in _FONTES.items():
        if not (pub / 'fonts' / nome).exists():
            shutil.copy(src, pub / 'fonts' / nome)
    fmt = motor.FORMATO
    cenas = motor.CENAS
    # 12/11 (caso real, folha do YT): fonte VERTICAL de celular — no 16:9 a janela mais larga do celular (1620x912) não
    # cabe a cabeça dele (rosto ~900 px de 1620): a pessoa em tela cheia 16:9 saía com a testa cortada. No YT as frases
    # da pessoa ficam no lado a lado (cenário + letreiro da cena à esquerda, pessoa 840 px à direita com cabeça e ombros,
    # o pessoa-YT-lado do arsenal) — como o modos={'YT': 'D'} do Editor Extremo.
    pessoa_orig = None
    w_ = motor.RAIZ / 'work' / (motor.GNN or '_')
    if fmt == 'YT' and motor.GNN and not (w_ / 'base_h.mov').exists() and (w_ / 'base.mov').exists():
        pessoa_orig = set(motor.CENAS_PESSOA_GL)
        motor.CENAS_PESSOA_GL = set()
    # 06/11 (revisor, "corte no meio da palavra"): o motor troca de cena 0,20 s antes da 1ª palavra, mas a última palavra
    # da cena anterior ainda está soando (37,50 no meio de "converte", 51,77 em "artificial", 64,37 em "rápidas", 67,00
    # antes do fim de "comigo"). Aqui nenhuma cena começa antes do FIM da palavra anterior + 0,03 s — vale pra toda cena,
    # principalmente as da pessoa (entrada e saída).
    for k, c in enumerate(cenas):
        if k and c.i0 > 0:
            fim_pal = float(motor.W[c.i0 - 1].get('e', 0)) + 0.03
            if c.t0 < fim_pal:
                c.t0 = q(fim_pal)
    # 12/11 (caso real): corte seco do tratado x entrada/saída da pessoa cheio (entra/sai no quadro do corte; no meio da
    # frase vira punch-in leve)
    _cortes_pessoa(cenas, pessoa_orig if pessoa_orig is not None else motor.CENAS_PESSOA_GL)   # mesmos tempos nos 4 formatos
    fims = [cenas[k + 1].t0 for k in range(len(cenas) - 1)] + [motor.DUR]
    if fmt == 'RL' and TELA_CHEIA and _PUNCH:
        n_p = {}
        for k, tc in _PUNCH:
            n_p[k] = n_p.get(k, 0) + 1
            cenas[k].js.append(f"tl.set('#pessoacheio',{{scale:{PUNCH_PESSOA if n_p[k] % 2 else 1},transformOrigin:'50% 30%'}},{motor.fl(tc)});"
                               f"tl.set('#pessoacheio',{{scale:1}},{motor.fl(fims[k])});")
    # 08/11 (usuário, caso real): cartela de raios só como passagem com letreiro falado + AÇÃO (peça na camada de ação,
    # número/data ou contador) — nunca só o letreiro sobre os raios
    import bonecos
    for c in cenas:
        if (CEN.get(c.id, ('',))[0] in ('capitulo', 'capitulo_vermelho', 'capitulo_verde') and c.id not in motor.CENAS_PESSOA_GL
                and not bonecos.AMB.get(c.id) and 'class="data"' not in c.html and 'ar-cont' not in c.html):
            print(f'  AVISO cartela: {c.id} está na cartela de raios sem ação — troque por um cenário com ação')
        # 08/11 (folha do t96): no prédio em corte o telhado é fixo; letreiro de 3 linhas descia por cima do telhado
        if CEN.get(c.id, ('',))[0] == 'corte' and c.id not in motor.CENAS_PESSOA_GL:
            import arsenal_fundos as _af
            if _pe_letreiro(c, fmt) > _af.andares()[0][0] - 100:
                print(f'  AVISO corte: {c.id} letreiro desce até y {_pe_letreiro(c, fmt):.0f} e o telhado do prédio em corte está em '
                      f'{_af.andares()[0][0] - 70} — encurte o letreiro (2 linhas)')
    for f_ in GANCHOS_PRE:
        f_()
    # corridas de cenas seguidas com o mesmo cenário = um plano só (mesmo desenho, câmera contínua)
    tipo_ant, corrida, ini_corrida = None, -1, {}
    tipos = []
    for c in cenas:
        tipo, op = CEN.get(c.id, (tipo_ant or 'dia', {}))
        if tipo != tipo_ant or op.get('novo'):
            corrida += 1
            ini_corrida[corrida] = c.t0
        tipos.append((tipo, op, corrida))
        tipo_ant = tipo
    fim_corrida = {}
    for (tipo, op, r), t1 in zip(tipos, fims):
        fim_corrida[r] = t1
    dmax = {}   # cena mais longa de cada plano: limita o passeio da câmera (texto/enfeite nunca a < 100 px da borda)
    for (tipo, op, r), c, t1 in zip(tipos, cenas, fims):
        dmax[r] = max(dmax.get(r, 0.0), t1 - c.t0)
    import bonecos
    pessoa = set(motor.CENAS_PESSOA_GL) if TELA_CHEIA else set()
    ultimo_mergulho = [-99.0]
    for k, (c, t1) in enumerate(zip(cenas, fims)):
        tipo, op, r = tipos[k]
        c.html = re.sub(r'<div class="ln((?: fino)?(?: forte)?)" style="font-size:(\d+)px">(.*?)</div>', _ajusta, c.html)
        # 08/11 (margem segura): número/data grande (an.data) cabe na largura segura — 'Metade' em 330 px dava 1057 px
        # (com a entrada em escala 1,1). Mede com a EB Garamond 700 de verdade e encolhe só o que não cabe.
        base_dn = {'GL': 180, 'YT': 180, 'IN': 210}.get(fmt, 330 if TELA_CHEIA else 250)

        def _fit_dn(m, base_dn=base_dn):
            txt = _html.unescape(m.group(1))
            larg = ImageFont.truetype(str(_FONTES['EBGaramond-700.woff2']), base_dn).getlength(txt) * 1.1
            if larg <= 800:
                return m.group(0)
            return f'<div class="dn" style="font-size:{int(base_dn * 800 / larg)}px">{m.group(1)}</div>'
        c.html = re.sub(r'<div class="dn">(.*?)</div>', _fit_dn, c.html)
        a, b = ini_corrida[r], fim_corrida[r]
        D = max(0.5, b - a)
        cen = _cenario_html(tipo, op, seed=1000 + r * 17 + bonecos.semente_video())   # rodada 7: cenário muda de vídeo pra vídeo
        # 06/11 (v3): camada de AÇÃO em tela cheia (bonecos de corpo inteiro, móveis, objetos) dentro do cenário
        amb = ''.join(bonecos.AMB.get(c.id, []))
        if 'data-enc=' in amb:   # 08/11: peças encaixadas na caixa segura, abaixo do letreiro desta cena
            # laterais: descontam o zoom/push/pan da câmera da cena (an.CAM) + o passeio do piso (~50 px)
            cm = CAM.get(c.id) or {}
            S = max([1.05] + [float(v) for v in re.findall(r'scale:([\d.]+)', cm.get('de', '') + cm.get('para', ''))])
            X = max([0.0] + [abs(float(v)) for v in re.findall(r'x:(-?[\d.]+)', cm.get('de', '') + cm.get('para', ''))])
            l0 = min(300.0, 540 - (430 - X) / S + 50)
            amb = bonecos.resolve_encaixe(amb, _pe_letreiro(c, fmt) + 80, fmt, lat=(l0, 1080 - l0))
        if amb:
            amb_div = (f'<div class="amb" id="{c.id}-amb"><svg width="1080" height="1920" viewBox="0 0 1080 1920" '
                       f'overflow="visible">{amb}</svg></div>')
            if '<!--AMB-->' in cen:
                cen = cen.replace('<!--AMB-->', amb_div)
            else:   # cenário antigo (pergaminho, capítulo...): a ação entra no .mundo, que encolhe junto no GL/IN
                cen = cen.replace('</div><div class="luzlat">', amb_div + '</div><div class="luzlat">', 1)
                cen = cen.replace('<div class="mundo">', '<div class="mundo sala">', 1)
        cen = cen.replace('<!--AMB-->', '')
        if amb and tipo == 'pergaminho':   # gráfico/mapa no pergaminho: sem a linha vermelha decorativa cruzando por trás
            cen = re.sub(r'<path class="rota"[^>]*/>', '', cen)
        c.html = f'<div class="tema t-{tipo}" id="{c.id}-tema" style="position:absolute;inset:0">{cen}{c.html}</div>'
        js = []
        # paralaxe: cada camada vai de +vel*D/2 a -vel*D/2 ao longo da corrida (limitado à sobra de 280 px)
        piso = re.search(r'class="cam sala piso" data-vel="([\d.]+)"', cen)
        f_sala = 1.0
        if piso:   # ambientes v3: o piso anda no máx. ~120 px por cena (8–15 % da largura) e as outras camadas na proporção
            f_sala = min(1.0, 120 / max(0.5, dmax[r]) / float(piso.group(1)))
        for vel in sorted({float(v) for v in re.findall(r'data-vel="([\d.]+)"', cen)}):
            v = min(vel * f_sala, 560 / D)
            x0 = v * D / 2 - v * (c.t0 - a)
            x1 = v * D / 2 - v * (t1 - a)
            js.append(f"tl.fromTo('#{c.id} .cam[data-vel=\"{vel:g}\"]',{{x:{x0:.1f}}},{{x:{x1:.1f},duration:{q(max(0.1, t1 - c.t0))},ease:'none'}},{q(c.t0)});")
        zz = 0.12 if tipo == 'capitulo' else 0.05   # rodada 6: a cartela não pode ficar quase parada
        z0 = 1 + zz * (c.t0 - a) / D
        z1 = 1 + zz * (t1 - a) / D
        cm_ = CAM.get(c.id)
        if cm_:   # arsenal: push-in / pull-out / tilt / pan próprios (de/para em scale, x, y; origem e ease)
            js.append(f"tl.set('#{c.id} .cenario',{{transformOrigin:'{cm_.get('origem', '50% 100%')}'}},{q(c.t0)});")
            js.append(f"tl.fromTo('#{c.id} .cenario',{cm_['de']},{{...{cm_['para']},duration:{q(max(0.1, t1 - c.t0))},ease:'{cm_.get('ease', 'none')}'}},{q(c.t0)});")
        else:
            js.append(f"tl.fromTo('#{c.id} .cenario',{{scale:{z0:.4f}}},{{scale:{z1:.4f},duration:{q(max(0.1, t1 - c.t0))},ease:'none'}},{q(c.t0)});")
        if tipo == 'capitulo':
            js.append(f"tl.fromTo('#{c.id} .raios',{{rotation:{(c.t0 - a) * 16:.1f}}},{{rotation:{(t1 - a) * 16:.1f},duration:{q(max(0.1, t1 - c.t0))},ease:'none'}},{q(c.t0)});")
            js.append(f"tl.fromTo('#{c.id} .raios',{{opacity:0.7}},{{opacity:1,duration:0.6,yoyo:true,repeat:{max(1, int((t1 - c.t0) / 0.6))},ease:'sine.inOut'}},{q(c.t0)});")
        if amb and piso:   # a ação anda junto com o piso (mesma velocidade: ninguém patina)
            vp = min(float(piso.group(1)) * f_sala, 560 / D)
            p = vp * (t1 - c.t0)
            js.append(f"tl.fromTo('#{c.id}-amb',{{x:{p / 2:.1f}}},{{x:{-p / 2:.1f},duration:{q(max(0.1, t1 - c.t0))},ease:'none'}},{q(c.t0)});")
        if k == 0:
            # rodada 8: o texto do gancho já está na tela no quadro 0 (as palavras faladas até 0,6 s entram em t=0)
            c.js = [re.sub(r"^palavra\('([^']+)',([\d.]+),", lambda m: f"palavra0('{m.group(1)}',0," if float(m.group(2)) <= 0.6 else m.group(0), l)
                    for l in c.js]
            # rodada 7 (gancho no 1º segundo): o quadro 0 já tem ação forte — a câmera entra num empurrão rápido. E a
            # 1ª cena não pode abrir só com a linha fina de apoio: o 1º letreiro precisa de linha grossa no começo.
            # 08/11 (margem segura): 1,07 no máximo — com 1,22 o letreiro do quadro 0 (o do gancho) passava 30 px da margem
            js.append(f"tl.fromTo('#{c.id}-tema',{{scale:1.07}},{{scale:1,duration:0.75,ease:'power3.out',transformOrigin:'50% 55%'}},0);")
            som(0.0, 'impacto_ar', 0.22)
            m1 = re.search(r'<div class="ln( fino)?', c.html)
            if m1 and m1.group(1):
                print(f'  AVISO gancho: {c.id} abre com a linha fina de apoio — comece com a linha grossa ({{120}}...) ou ação forte')
        if k and c.t0 == a and c.id not in SEM_MERGULHO:
            # 06/11 (revisor): troca de LUGAR = mergulho no escuro com dissolve 0,6 s (a cena anterior escurece no fim);
            # nos 3 primeiros segundos nada de preto: clarão creme + a câmera entrando (zoom). Rodada 5: no máx. um
            # mergulho a cada 8 s (dois seguidos pareciam piscar) — os outros viram um empurrão de câmera sem escurecer.
            if c.t0 < 3.0 or c.t0 - ultimo_mergulho[0] < 8.0:
                if c.t0 >= 3.0:
                    js.append(f"tl.fromTo('#{c.id}-tema',{{scale:1.04,x:14}},{{scale:1,x:0,duration:0.55,ease:'power2.out',transformOrigin:'50% 50%'}},{q(c.t0)});")   # 08/11: era 1,07 + 60 px (texto saía da margem)
                    som(max(0.0, c.t0 - 0.15), 'swish', 0.14)
            if c.t0 < 3.0:
                js.append(f"tl.set('#{c.id} .veu',{{backgroundColor:'#F6EBD3'}},{q(c.t0)});")
                js.append(f"tl.fromTo('#{c.id} .veu',{{opacity:0.8}},{{opacity:0,duration:0.45,ease:'power1.out'}},{q(c.t0)});")
                js.append(f"tl.fromTo('#{c.id}-tema',{{scale:1.07}},{{scale:1,duration:0.6,ease:'power2.out',transformOrigin:'50% 45%'}},{q(c.t0)});")   # 08/11: era 1,12
                som(max(0.0, c.t0 - 0.2), 'swish', 0.16)
            elif c.t0 - ultimo_mergulho[0] >= 8.0:
                ultimo_mergulho[0] = c.t0
                js.append(f"tl.fromTo('#{c.id} .veu',{{opacity:0.92}},{{opacity:0,duration:0.6,ease:'power1.out'}},{q(c.t0)});")
                ant = cenas[k - 1]
                if ant.id not in pessoa:
                    ant.js.append(f"tl.to('#{ant.id} .veu',{{opacity:0.55,duration:0.2,ease:'power1.in'}},{q(c.t0 - 0.21)});")
                som(max(0.0, c.t0 - 0.25), 'transicao', 0.16)
        js += _vida(c.id, cen, c.t0, t1, c.js)
        js.append(f"tl.fromTo('#{c.id} .grao2',{{x:0,y:0}},{{x:37,y:-23,duration:0.25,ease:'steps(2)',repeat:{max(1, int((t1 - c.t0) / 0.25))}}},{q(c.t0)});")
        # miolo sobe junto, devagar (a câmera nunca para)
        js.append(f"tl.fromTo('#{c.id} .miolo',{{y:0}},{{y:-14,duration:{q(max(0.1, t1 - c.t0))},ease:'none'}},{q(c.t0)});")
        for tt in re.findall(r"pop\('#[^']+',([\d.]+)", ' '.join(c.js)):
            som(float(tt), 'pop', 0.14)
        for tt in re.findall(r"vai\('#c\d+-bt',\{scale:0\.94,duration:0\.08\},([\d.]+)\)", ' '.join(c.js)):
            som(float(tt), 'madeira', 0.35)
        c.js[:0] = js
    ult = cenas[-1]
    if ult.id not in pessoa:
        fim_voz = float(motor.W[-1].get('e', motor.DUR)) if motor.W else motor.DUR
        ini_f = max(fim_voz - 0.02, motor.DUR - 0.3)
        if ini_f < motor.DUR - 0.05:
            ult.js.append(f"tl.to('#{ult.id}-tema',{{opacity:0.25,duration:{q(motor.DUR - ini_f - 0.02)},ease:'power1.in'}},{q(ini_f)});")
    if fmt == 'IN':
        motor.FORMATOS['GL'] = dict(w=1080, h=1350, palco=(0, 0, 1.0), pessoa=(0, 0, 1080, 1350), divisoria=(0, 0, 0, 0),
                                    titulo=(540, 1000, 1080), video='pessoa-IN-cheio.mp4')
        import pessoa_cheio
        pessoa_cheio.gerar(motor.GNN, motor.AQUI.name, larg=864, saida_wh=(1080, 1350), nome='pessoa-IN-cheio.mp4')
        motor.FORMATO = 'GL'
    elif fmt == 'YT':
        # rodada 8: YT 1920x1080 = a composição quadrada do GL (1080x1080, ambiente encolhido: texto em cima, ação
        # embaixo) à esquerda + a pessoa à direita (840 px, o recorte 16:9 inteiro deslocado: rosto no meio do painel);
        # nas cenas do pessoa_gl o vídeo volta pra x 0 e a pessoa fica em TELA CHEIA 16:9. Sem área vazia.
        motor.FORMATOS['GL'] = dict(w=1920, h=1080, palco=(0, 0, 1.0), pessoa=(540, 0, 1920, 1080), divisoria=(1078, 0, 4, 1080),
                                    titulo=(540, 800, 1080), video='pessoa-YT-cheio.mp4')
        import pessoa_cheio
        pessoa_cheio.gerar(motor.GNN, motor.AQUI.name, larg=1920, saida_wh=(1920, 1080), nome='pessoa-YT-cheio.mp4')
        fims_ = [cenas[k + 1].t0 for k in range(len(cenas) - 1)] + [motor.DUR]
        js_t = ["tl.set('#pessoa',{x:0},0);tl.set('#divisoria',{opacity:1},0);"]
        for c, t1 in zip(cenas, fims_):
            if c.id in motor.CENAS_PESSOA_GL:   # 12/11: fl = no quadro exato (q arredondava pra cima e atrasava 1 quadro)
                js_t.append(f"tl.set('#pessoa',{{x:-540}},{motor.fl(c.t0)});tl.set('#divisoria',{{opacity:0}},{motor.fl(c.t0)});"
                            f"tl.set('#pessoa',{{x:0}},{motor.fl(t1)});tl.set('#divisoria',{{opacity:1}},{motor.fl(t1)});")
        primeira = next(c for c in cenas if c.id not in motor.CENAS_PESSOA_GL)
        primeira.js.extend(js_t)
        motor.FORMATO = 'GL'
    # 05/11 (usuário): o vídeo inteiro é animação em tela cheia; a pessoa entra em tela cheia numa frase a cada ~15 s
    # (as cenas do pessoa_gl do configurar). TELA_CHEIA=False volta à tela dividida.
    cheias = {c.id for c in cenas if c.id not in motor.CENAS_PESSOA_GL} if TELA_CHEIA else set(CHEIAS)
    motor.CENAS_ANIM_CHEIA = cheias
    motor.GL_ESPERA_LINHA = False   # o cenário já entra pronto; não precisa esperar a 1ª linha
    motor.CHEIA_SEM_ESPERA = True   # idem no RL: a cena cheia já abre com a paisagem, nunca é tela preta com 1 palavra
    for f_ in GANCHOS_POS:
        f_()
    motor.montar()
    motor.FORMATO = fmt

    arq = pub / 'index.html'
    s = arq.read_text(encoding='utf-8')
    # só as cenas que o motor realmente pôs em tela cheia (ele recusa as que demoram a montar a 1ª linha) ganham a paisagem maior
    for cid in (re.findall(r"tl\.set\('#(c\d+)',\{height:1920", s) if not (TELA_CHEIA and fmt == 'RL')
                else [c.id for c in cenas if c.id not in motor.CENAS_PESSOA_GL]):
        s = re.sub(rf'<div class="tema (t-[a-z0-9_]+)" id="{cid}-tema"', lambda m, i=cid: f'<div class="tema {m.group(1)} cheia" id="{i}-tema"', s, count=1)
        s = re.sub(rf'<div class="tema (t-[a-z0-9_]+)" id="{cid}-tema"', rf'<div class="tema  cheia" id="{cid}-tema"', s, count=1)
    css_cheia = ('#palco,.cena{height:1920px !important}.cena .miolo{top:480px !important}#divisoria{display:none !important}'
                 '.rotulo{bottom:-30px !important}'   # 08/11 (margem segura): fim em y ~1470, nunca abaixo de 1500 (a interface do Reels cobre)
                 ''
                 if (TELA_CHEIA and fmt == 'RL') else '')
    # 12/11 (usuário, caso real): legenda padrão do básico nas cenas da pessoa em tela cheia (LEGENDA_PESSOA)
    leg_html, leg_js, leg_css = _legenda_pessoa(fmt, cenas, fims)
    s = s.replace('</head>', f'<style>{_css(fmt)}{css_cheia}{leg_css}</style></head>', 1)
    s = s.replace('<div id="divisoria"></div>', f'<div id="divisoria"></div>\n      {leg_html}\n      {_audios()}', 1)
    s = s.replace('\n// c01 ', JS_ANIM + '\n// c01 ', 1)
    if leg_js:
        s = s.replace(f'window.__timelines["{motor.COMPOSICAO}"] = tl;', f'// legenda da pessoa cheio\n{leg_js}\n'
                      f'window.__timelines["{motor.COMPOSICAO}"] = tl;', 1)
    arq.write_text(s, encoding='utf-8')
    for f_ in GANCHOS_FIM:
        f_()
    if pessoa_orig is not None:
        motor.CENAS_PESSOA_GL = pessoa_orig
    print(f'Edição animada aplicada em {arq} ({fmt}): {len(set(t for t, _, _ in tipos))} tipos de cenário, '
          f'{len(ini_corrida)} planos, {len(CHEIAS)} cenas cheias, {s.count(chr(60) + "audio id=" + chr(34) + "sfx")} efeitos')
