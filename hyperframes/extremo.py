# -*- coding: utf-8 -*-
"""Editor Extremo (04/11/2026) — motion design de interface escuro e quente, a partir das 4 referências do usuário
(análise completa em skill editor-extremo; processo na skill .claude/skills/editor-extremo).

07/11/2026 (terminado): recortes da pessoa por take com o rosto do mesmo tamanho (dividida = plano médio, como a
referência), corte seco do tratado vira ponto de troca de cena, GL cima/baixo, peças da v2 (passo, checkcard, icone,
hub, pergunta, perfil), empurrão de câmera +2 % no conteúdo, AVISOs (cabeça cortada, zoom exagerado, > 4 s parado,
corte no meio de cena) e bloqueio de link/QR/bio/Direct/URL na tela; música desligada por padrão (MUSICA_ON).
Molde: hyperframes/exemplos/extremo_gerar.py.

DNA: fundo marrom quase preto com vinheta, retícula e poeira laranja; 3 modos que se alternam o tempo todo —
  D  dividida (RL/IN/GL: gráfico em cima, pessoa embaixo; YT: gráfico à esquerda, pessoa à direita)
  G  gráfico em tela cheia (sem a pessoa, sem legenda)
  T  pessoa em tela cheia (única com legenda), como "pontuação" na frase de virada (zoom-cut leve no meio, só em começo de frase)
Cada frase vira UI recriada (chat de WhatsApp, janela de CRM, kanban, checklist numerado, número grande, alerta,
agente de IA, fluxo de nós, botão com cursor…). Título serifado (EB Garamond) creme com palavra-chave laranja
(vermelha quando é negativa) + chapéu em caixa-alta espaçada; texto de UI em Inter. Entradas blur→nítido + fade +
subida em ~6 quadros; listas em cascata; itens antigos ficam a ~40 %. Transições: whip horizontal, flash duplo,
blur de foco (escolhidas pela troca de modo). SFX do Earshot (08/11: kit em extremo_sfx/earshot, só tocam com evento
visível no formato — ver _audios e mapa-sons-<FMT>.txt); cama musical baixíssima só com MUSICA_ON = True (trilha
licenciada). Legenda simples de 1 linha (padrão do usuário) SÓ na pessoa cheio, abaixo do queixo (08/11: nada de legenda
na dividida nem no gráfico cheio). 08/11: fonte vertical de celular em plano médio (ALVO_V); chapéu e
rótulos espaçados cabem em 880 px (_espacado). 12/11 (REGRA do usuário): a cor da pessoa NUNCA muda — a grade COR_V saiu
e os recortes só trocam a matriz pra BT.601 (cor_pessoa.py); no RL de fonte vertical a dividida dá mais altura ao
pessoa (GEO_V_RL: gráfico 0–820, pessoa 820–1920), senão o rosto enchia a faixa e cortava cabeça e queixo.

Não usa o motor.montar(): este módulo escreve o index.html inteiro (os modos e as transições pedem outro layout), mas
mantém o mesmo formato de pasta (hyperframes/<id>-extremo/public) e os comentários "// cNN [t0–t1]" que o
revisar.py / renderizar.py da skill video-dividido-hyperframes leem.

Uso no gerar.py de cada vídeo (molde: hyperframes/exemplos/extremo_gerar.py):
    import extremo as X
    X.configurar(pasta=..., palavras='work/<id>/words_cut.json', duracao=<dur>, composicao='<id>-extremo', nome=...,
                 repl={...}, frases='''bloco | bloco | ...''')
    c = X.cena(0, 9, 'D', 'Lead caro')          # modo D/G/T; modos={'GL': 'G'} troca o modo num formato
    X.chapeu(c, 'VOCÊ PAGA CARO', 1); X.titulo(c, 'para cada *lead*', 5)   # *chave* laranja, !chave! vermelha
    X.notificacao(c, ...); X.chat(c, ...); ...
    X.aplicar()
Linha de comando: python gerar.py [phosphor] RL|IN|GL|YT
"""
import html as _html
import json
import math
import random
import re
import shutil
import subprocess
import sys
import unicodedata
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cor_pessoa  # noqa: E402   (12/11: REGRA do usuário — a cor da pessoa nunca muda)

RAIZ = Path(__file__).resolve().parent.parent
FPS = 30
F = 1 / FPS
FF = (RAIZ / 'ferramentas/ffmpeg_path.txt').read_text().strip()
_PH = RAIZ / 'ferramentas/phosphor-core/assets'
_FONTES = {
    'EBGaramond-400.woff2': RAIZ / 'ferramentas/fontes',
    'EBGaramond-OFL.txt': RAIZ / 'ferramentas/fontes',
    'inter-latin-500-normal.woff2': RAIZ / 'ferramentas/fontes',
    'inter-latin-600-normal.woff2': RAIZ / 'ferramentas/fontes',
    'inter-latin-700-normal.woff2': RAIZ / 'ferramentas/fontes',
    'TikTokSans-Variable.ttf': RAIZ / 'ferramentas/fontes',
}
_SFX_DIR = RAIZ / 'hyperframes/extremo_sfx'
MUSICA = RAIZ / 'trilhas/extremo.mp3'   # cama musical opcional (só com MUSICA_ON): ponha aqui uma trilha que você tenha licença

# paleta medida na referência (analise.md §9)
LARANJA, LARANJA2, LARANJA3, LARANJA_ESC = '#CA661F', '#EA7C2E', '#C45F18', '#A35E1D'
CREME, UI, UI2, VERMELHO, VERMELHO2 = '#F4EBD2', '#D4D2B1', '#97805F', '#D4383A', '#E7474A'

ARGS = sys.argv[1:]
FORMATO = next((a for a in ARGS if a in ('RL', 'IN', 'GL', 'YT')), 'RL')

# ---------------------------------------------------------------- geometria por formato
# quadro, painel do gráfico na dividida, slot da pessoa na dividida, caixa útil do conteúdo (D e G),
# legenda (x, y) na dividida e na pessoa cheio. Conteúdo é desenhado numa caixa virtual de 880 px de largura e
# escalado pra caber na caixa útil (margem lateral ≥ 100 px no quadro final, regra de 23/10).
#
# 07/11: a caixa útil começa em x 110 (não 100) porque o conteúdo ganha um empurrão de câmera de +2 % por cena e a
# borda não pode chegar a menos de ~100 px da lateral. GL virou cima/baixo (como RL/IN, mais perto da referência
# vertical): na lateral de 430 px o rosto da pessoa (≥ 355 px no 16:9, sem poder diminuir) enchia a faixa inteira.
# Recortes da pessoa (rosto_D/rosto_T = largura alvo do rosto em px no quadro final; pos = altura do centro do rosto
# na janela): o tamanho do rosto é igualado em cada take (work/<id>/cortes_visuais.json), como na referência
# (dividida = plano médio com o microfone, rosto ~330 px no RL; pessoa cheia = close de ~52 % da largura).
GEO = {
    'RL': dict(w=1080, h=1920, painel=(0, 0, 1080, 960), slot=(0, 960, 1080, 960),
               cx_D=(110, 250, 860, 640), cx_G=(110, 330, 860, 900), cap=1.0,
               leg_D=(540, 960), leg_T=(540, 1196), leg_px=54, origem_T=0.30,
               rosto_D=(340, 0.39), rosto_T=(560, 0.30)),
    'IN': dict(w=1080, h=1350, painel=(0, 0, 1080, 702), slot=(0, 702, 1080, 648),
               cx_D=(110, 50, 860, 600), cx_G=(110, 225, 860, 950), cap=1.0,
               leg_D=(540, 702), leg_T=(540, 1040), leg_px=50, origem_T=0.32,
               rosto_D=(250, 0.40), rosto_T=(480, 0.33)),
    'GL': dict(w=1080, h=1080, painel=(0, 0, 1080, 560), slot=(0, 560, 1080, 520),
               cx_D=(110, 36, 860, 470), cx_G=(110, 180, 860, 800), cap=1.0,
               leg_D=(540, 560), leg_T=(540, 905), leg_px=46, origem_T=0.35,
               rosto_D=(230, 0.40), rosto_T=(430, 0.36)),
    'YT': dict(w=1920, h=1080, painel=(0, 0, 1170, 1080), slot=(1170, 0, 750, 1080),
               cx_D=(110, 180, 990, 720), cx_G=(300, 180, 1320, 780), cap=1.15,
               leg_D=(1170, 978), leg_T=(960, 960), leg_px=48, origem_T=0.35,
               rosto_D=(330, 0.36), rosto_T=(330, 0.34)),
}
# 12/11/2026 (usuário, caso real "mal enquadrado"): no RL de fonte VERTICAL (celular, rosto ~900 px na base 1620) a
# dividida 50/50 (faixa 1080x960) não deixa abrir o plano: a janela já é a largura inteira do celular, o rosto ficava com
# 600 px e enchia a faixa — cabelo encostando na divisória e queixo no pé do quadro (cabeça y67, queixo y950 de 960),
# sem ombro nem microfone. Agora a pessoa ganha 1100 px de altura (gráfico 0–820, caixa útil y 320–800 — texto nunca
# acima de 320, regra de 12/11 — escala 0,73, como no GL): topo da cabeça a ~8–10 %, queixo a ~74 % (p95 ~88 %),
# ombros dentro. Só vale com X.VERTICAL.
GEO_V_RL = dict(painel=(0, 0, 1080, 820), slot=(0, 820, 1080, 1100), cx_D=(110, 320, 860, 480), leg_D=(540, 820))
# 12/11/2026 — REGRA DO USUÁRIO (caso real/caso real): título, legenda, letreiro e qualquer texto NUNCA lá em cima (o
# Instagram tampa), nunca baixo demais, nunca na altura do rosto. RL: topo do texto ≥ 320 px e base < ~1500; nos outros
# longe do topo também (checagem: IN ≥ 200, GL/YT ≥ 160; aqui as caixas começam em 225/180). As caixas G do IN/GL/YT, a D do YT e a D do RL vertical
# começam aí (a altura da legenda não mudou). Conferir com MARGEM_SO_VERTICAL=1 node hyperframes/checar_margem.mjs.
# PENDENTE: a D do RL/IN/GL de fonte 16:9 (painel em cima) ainda começa em y 250/50/36 — ver com o usuário.
CX_W = 880   # largura da caixa virtual
DERIVA = 1.02   # empurrão de câmera no conteúdo (D e G) ao longo da cena: nada parado > 4 s (regra 26/10)
ZOOM_T = 1.06   # zoom-cut na pessoa cheio (só em começo de frase); base 1,0 — "sem zoom exagerado"
# 13/11/2026 (usuário, caso real: "pessoa menor. Ele tá dando um zoom sem necessidade") — opções POR VÍDEO (no gerar.py):
# CARTAO_D = (w, h, topo): no RL a dividida mostra a pessoa num cartão w x h de cantos arredondados, centrado na faixa e
#   a `topo` px do topo dela, sobre o marrom do estilo (fonte de celular: rosto ~470 px em vez de ~600 na faixa inteira);
# ZOOM_D = False: sem o zoom alternado (1,0/1,045) e contínuo (+0,025) da pessoa na dividida (e, na fonte de celular,
#   sem aproximar o recorte: janela mais larga possível).
# 13/11 (usuário, caso real v2): "pessoa foi colocado num quadro na vertical" — o CARTAO_D foi REJEITADO; não usar.
#   pessoa menor sem quadro = ZOOM_D False (na fonte de celular o vídeo já ocupa a largura toda no mínimo de escala).
CARTAO_D = None
ZOOM_D = True
PROIBIDO = re.compile(r'\b(link|links|qr|qr ?code|bio|direct|www|https?)\b|\.com\b|\.com\.br\b', re.I)

# ---------------------------------------------------------------- estado do vídeo
AQUI = W = DUR = COMPOSICAO = NOME = GNN = None
VERTICAL = False     # 07/11: fonte de celular vertical (work/<id>/base.mov 1620x2880, sem base_h.mov) — ver _recorte_vertical
REPL, FRASES = {}, ''
CENAS, SFX = [], []
TRANS = []           # (t, som, descrição) das trocas de modo — montado em _transicoes, tocado em _audios
CORTES = []          # cortes secos do tratado (work/<id>/cortes_visuais.json): jump cuts entre takes
_CROP = {}           # nome do recorte -> [dict(a, b, y0, s, rosto)] por take (pra achar queixo/cabeça no quadro)
_n = [0]


def configurar(pasta, palavras, duracao, composicao, nome, repl=None, frases=''):
    """palavras: work/<id>/words_cut.json (tempos); repl: {índice: (n_palavras, ['novas', ...])} correções do whisper
    pra LEGENDA (mesmo formato do cfg do básico); frases: legenda em blocos separados por '|' (1 linha cada)."""
    global AQUI, W, DUR, COMPOSICAO, NOME, GNN, REPL, FRASES, VERTICAL
    AQUI = Path(pasta).resolve()
    GNN = Path(palavras).parent.name
    VERTICAL = not (RAIZ / 'work' / GNN / 'base_h.mov').exists() and (RAIZ / 'work' / GNN / 'base.mov').exists()
    if VERTICAL:   # 12/11: dividida do RL com mais altura pro pessoa (ver GEO_V_RL)
        GEO['RL'] = {**GEO['RL'], **GEO_V_RL}
    W = json.load(open(RAIZ / palavras, encoding='utf-8'))
    DUR, COMPOSICAO, NOME = duracao, composicao, nome
    REPL, FRASES = dict(repl or {}), frases
    cv = RAIZ / 'work' / GNN / 'cortes_visuais.json'
    CORTES[:] = [float(c) for c in json.loads(cv.read_text())] if cv.exists() else []


def _no_meio_de_palavra(t):
    return any(p['s'] + 0.02 < t < p['e'] - 0.02 for p in W)


def q(t):
    return round(round(t * FPS) / FPS, 4)


def T(x):
    """Índice de palavra (int) → início dela; float → o próprio tempo (s)."""
    return W[x]['s'] if isinstance(x, int) else float(x)


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return re.sub(r'[^a-z0-9%]', '', ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn'))


def esc(s):
    return _html.escape(s, quote=False)


GAP_SOM = 0.28   # intervalo mínimo entre sons de peça (s)


def som(t, nome, vol=None, gap=None):
    """Pede um efeito em t (s): blip (card/peça entrando) | tique (marca/X/número girando) | check (✓ marcando) |
    chime (✓ final, CTA) | whoosh (= hit do flash). 08/11/2026: é só um PEDIDO — no aplicar() o som só toca se, NAQUELE
    formato, um elemento visível entra/marca/muda no mesmo instante (±2 quadros) na timeline real (GSAP); senão sai
    (e aparece no mapa de sons como descartado). Volume padrão em VOL. gap (12/11) = intervalo mínimo deste som pros
    outros (padrão GAP_SOM 0,28 s; a rajada de `celulares` usa 0,1 s — entre dois sons vale o maior dos dois)."""
    SFX.append((round(float(t), 3), nome, VOL[nome] if vol is None else vol, GAP_SOM if gap is None else gap))


# 08/11/2026: kit do Earshot (MIT, ferramentas/earshot-src; renderizado em hyperframes/extremo_sfx/earshot/ por
# _kit_earshot) no lugar dos 4 sintetizados. nome lógico -> (arquivo, segundos do início do arquivo até o pico): o
# arquivo começa em t − pico, então o pico cai no quadro do evento (whoosh/swish: pico 1 quadro DEPOIS do corte).
KIT = {'blip': ('pop', 0.003), 'tique': ('tick', 0.002), 'check': ('check', 0.003), 'chime': ('ding', 0.004),
       'whoosh': ('hit', 0.022), 'swish': ('swish', 0.119 - 0.033), 'foco': ('foco', 0.202 - 0.033)}
KIT_EARSHOT = {'pop': ('pro_pop/thup', []), 'tick': ('pro_click/soft', []), 'check': ('pro_click/tink', []),
               'ding': ('pro_notify/ding_2045', []), 'hit': ('cut_hit/sub', []),
               'swish': ('swish/flick', ['--apex', '0.12']), 'foco': ('swish/soft', ['--dur', '0.5', '--apex', '0.2'])}
VOL = {'blip': 0.26, 'tique': 0.19, 'check': 0.24, 'chime': 0.21, 'whoosh': 0.12, 'swish': 0.20, 'foco': 0.13}


# ---------------------------------------------------------------- cenas
class Cena:
    def __init__(self, i0, i1, modo, nome, modos=None, zoom=()):
        self.id = f'c{len(CENAS) + 1:02d}'
        self.i0, self.i1, self.nome = i0, i1, nome
        self.modo_base = modo
        self.modos = dict(modos or {})
        self.t0 = 0.0 if i0 == 0 else q(T(i0) - 0.20)
        if i0:
            # 07/11: um corte seco do tratado perto do começo da cena vira o próprio ponto de troca — o jump cut some
            # atrás da transição (como na referência: "todos os jump cuts ficam escondidos atrás delas")
            perto = [c for c in CORTES if -0.30 <= c - self.t0 <= 0.35 and c >= W[i0 - 1]['e'] - 0.02
                     and not _no_meio_de_palavra(c)]
            if perto:
                self.t0 = q(min(perto, key=lambda c: abs(c - self.t0)))
        self.zoom = [q(T(z) - 0.12) for z in zoom]   # zoom-cut na pessoa cheio (só em começo de frase)
        self.ev = []         # tempos dos eventos visuais (pra conferir "nada parado > 4 s")
        self.partes = []     # HTML das peças (na ordem)
        self.cab = []        # chapéu + título
        self.js = []
        self.fala = ' '.join(W[i]['w'] for i in range(i0, i1 + 1))

    @property
    def modo(self):
        m = self.modos.get(FORMATO, self.modo_base)
        # 07/11 (só fonte vertical): no IN/GL a faixa da pessoa na dividida é larga e baixa demais pro celular (a cabeça
        # não cabe) — a dividida vira gráfico cheio, e a pessoa aparece nos T (modos={'IN': 'T'} na cena muda isso)
        if VERTICAL and m == 'D' and FORMATO in ('IN', 'GL') and FORMATO not in self.modos:
            return 'G'
        return m

    def a(self, linha):
        self.js.append(linha)

    def add(self, html):
        self.partes.append(html)
        return html


def cena(i0, i1, modo, nome, modos=None, zoom=()):
    c = Cena(i0, i1, modo, nome, modos, zoom)
    CENAS.append(c)
    return c


def _id(c, p):
    _n[0] += 1
    return f'{c.id}-{p}{_n[0]}'


def _t(c, x, antes=0.12):
    """Tempo de entrada de um elemento: ~0,12 s antes da palavra, nunca antes do início da cena + 2 quadros."""
    t = q(max(c.t0 + 0.07, T(x) - antes))
    c.ev.append(t)
    return t


def ic(nome, tam=56, peso='regular', cls=''):
    corpo = re.search(r'<svg[^>]*>(.*)</svg>', (_PH / peso / f'{nome}{"" if peso == "regular" else "-" + peso}.svg')
                      .read_text(encoding='utf-8'), re.S).group(1)
    return (f'<svg class="ph {cls}" width="{tam}" height="{tam}" viewBox="0 0 256 256" fill="currentColor">'
            f'{corpo}</svg>')


# ================================================================ TIPOGRAFIA
_FT = {}


def _fonte(nome, tam):
    k = (nome, tam)
    if k not in _FT:
        src = _FONTES[nome] / nome
        f = ImageFont.truetype(str(src), tam)
        if nome.startswith('TikTok'):
            f.set_variation_by_axes([36, 100, 650, 0])
        _FT[k] = f
    return _FT[k]


def _marca(txt):
    """*chave* → laranja; !chave! → vermelho."""
    s = esc(txt)
    s = re.sub(r'\*([^*]+)\*', r'<span class="k">\1</span>', s)
    return re.sub(r'!([^!]+)!', r'<span class="kn">\1</span>', s)


def _espacado(texto, px, ls, larg=CX_W - 40, fonte='inter-latin-600-normal.woff2'):
    """08/11/2026 (margem de segurança, caso real: o chapéu "O CUSTO DA MINHA OPERAÇÃO ERA PESADO" encostava nas duas
    laterais): texto de 1 linha com letter-spacing (em) tem que caber em `larg` px da caixa virtual (840 = 1080 − 2×100
    no RL com folga pro empurrão de câmera de 2 %). Reduz o espaçamento até 60 % e o corpo até 75 %; se ainda não
    couber, quebra em 2 linhas na palavra mais perto do meio. Devolve (style inline, html do texto) — style vazio quando nada mudou."""
    def larg_de(t_, px_, ls_):
        return _fonte(fonte, px_).getlength(t_) + max(0, len(t_) - 1) * ls_ * px_
    px0, ls0 = px, ls
    while larg_de(texto, px, ls) > larg and ls > ls0 * 0.6 + 1e-6:
        ls = round(ls - 0.02, 3)
    while larg_de(texto, px, ls) > larg and px > round(px0 * 0.75):
        px -= 1
    html_ = esc(texto)
    if larg_de(texto, px, ls) > larg and ' ' in texto:
        pal = texto.split(' ')
        k = min(range(1, len(pal)), key=lambda i: abs(len(' '.join(pal[:i])) - len(' '.join(pal[i:]))))
        l1, l2 = ' '.join(pal[:k]), ' '.join(pal[k:])
        px, ls = px0, ls0
        while max(larg_de(l1, px, ls), larg_de(l2, px, ls)) > larg and px > round(px0 * 0.75):
            px -= 1
        html_ = f'{esc(l1)}<br>{esc(l2)}'
    if (px, ls) == (px0, ls0) and '<br>' not in html_:
        return '', html_
    return f' style="font-size:{px}px;letter-spacing:{ls}em;margin-right:-{ls}em;line-height:1.5"', html_


def chapeu(c, texto, t):
    """Eyebrow: Inter 600, caixa-alta, tracking aberto, laranja escuro; entra ~0,15 s antes do título. Cabe sempre em
    880 px (≥ 100 px das laterais): aperta o espaçamento/corpo ou quebra em 2 linhas (_espacado)."""
    eid = _id(c, 'e')
    c.a(f"entra('#{eid}',{_t(c, t, 0.15)},0.14,8);")
    st, h = _espacado(texto.upper(), 30, 0.32)
    c.cab.append(f'<div class="chapeu" id="{eid}"{st}>{h}</div>')


def titulo(c, spec, t, tam=96):
    """Título serifado (EB Garamond) creme; '|' quebra linha; *chave* laranja, !chave! vermelha. Entra inteiro de uma
    vez com a palavra-chave falada (t = índice ou s). Reduz o corpo até toda linha caber em 880 px."""
    tid = _id(c, 'h')
    linhas = [ln.strip() for ln in spec.split('|')]
    limpas = [re.sub(r'[*!]', '', ln) for ln in linhas]
    while tam > 50 and max(_fonte('EBGaramond-400.woff2', tam).getlength(ln) for ln in limpas) > CX_W - 10:
        tam -= 2
    c.a(f"entra('#{tid}',{_t(c, t)},0.22,16);")
    c.cab.append(f'<div class="titulo" id="{tid}" style="font-size:{tam}px">'
                 + ''.join(f'<div>{_marca(ln)}</div>' for ln in linhas) + '</div>')


# ================================================================ PEÇAS (UI recriada, dados genéricos)
def _card(cls, inner, cid, estilo=''):
    return f'<div class="cd {cls}" id="{cid}" style="{estilo}">{inner}</div>'


def notificacao(c, titulo_, sub, t, icone='whatsapp-logo', hora='', av='', chip=None, larg=800):
    """Card de notificação (lead novo): avatar + nome + sub + ícone; chip=(texto, t, 'neg'|'') opcional à direita."""
    nid = _id(c, 'n')
    c.a(f"entra('#{nid}',{_t(c, t)});")
    som(_t(c, t), 'blip')
    avh = f'<div class="av">{esc(av)}</div>' if av else f'<div class="av">{ic("user", 34)}</div>'
    hr = f'<div class="hr">{esc(hora)}</div>' if hora else ''
    ch = ''
    if chip:
        txt, tc, tipo = (list(chip) + [''])[:3]
        ch = f'<div class="pill {tipo}" id="{nid}-p">{esc(txt)}</div>'
        c.a(f"pop('#{nid}-p',{_t(c, tc)});")
        som(_t(c, tc), 'blip')
    return c.add(_card('notif', f'{avh}<div class="nt"><div class="nm">{esc(titulo_)}</div><div class="sb">{esc(sub)}</div>'
                       f'</div>{hr}<div class="ico">{ic(icone, 44)}</div>{ch}', nid, f'width:{larg}px'))


def chat(c, nome, sub, msgs, t, larg=820, av='', icone='whatsapp-logo'):
    """Chat de WhatsApp. msgs = [dict(lado='in'|'out'|'ia', txt, t, hora='', apaga=t, digita=t_inicio, tag=(txt, t, tipo))].
    'digita' mostra os três pontinhos de t_inicio até a mensagem entrar."""
    cid = _id(c, 'ch')
    c.a(f"entra('#{cid}',{_t(c, t)});")
    som(_t(c, t), 'blip')
    corpo = []
    for k, m in enumerate(msgs):
        mid = f'{cid}-m{k}'
        tm = _t(c, m['t'])
        if 'digita' in m:
            td = _t(c, m['digita'])
            corpo.append(f'<div class="digit {m["lado"]}" id="{mid}-d"><i></i><i></i><i></i></div>')
            c.a(f"entra('#{mid}-d',{td},0.14,8);tl.set('#{mid}-d',{{display:'none'}},{tm});")
            c.a(f"tl.fromTo('#{mid}-d i',{{opacity:0.3}},{{opacity:1,duration:0.25,stagger:0.12,repeat:{max(0, int((tm - td) / 0.5))},"
                f"yoyo:true,ease:'sine.inOut',immediateRender:false}},{td});")
        hr = f'<span class="hr">{esc(m.get("hora", ""))}{" ✓✓" if m["lado"] != "in" else ""}</span>' if m.get('hora') else ''
        tag = ''
        if m.get('tag'):
            tt, tc, tipo = (list(m['tag']) + [''])[:3]
            tag = f'<div class="pill {tipo} tagm" id="{mid}-g">{esc(tt)}</div>'
            c.a(f"pop('#{mid}-g',{_t(c, tc)});")
            som(_t(c, tc), 'blip')
        rob = f'<div class="robo">{ic("robot", 30)}<span>Agente de IA</span></div>' if m['lado'] == 'ia' else ''
        corpo.append(f'<div class="msg {m["lado"]}" id="{mid}">{rob}<span>{esc(m["txt"])}</span>{hr}{tag}</div>')
        c.a(f"entra('#{mid}',{tm},0.2,14);")
        som(tm, 'blip')
        if m.get('apaga') is not None:
            c.a(f"apaga('#{mid}',{_t(c, m['apaga'])});")
    avh = f'<div class="av">{esc(av)}</div>' if av else f'<div class="av">{ic("user", 34)}</div>'
    hd = (f'<div class="hd">{avh}<div class="nt"><div class="nm">{esc(nome)}</div><div class="sb">{esc(sub)}</div></div>'
          f'<div class="ico">{ic(icone, 44)}</div></div>')
    return c.add(_card('chat', hd + '<div class="msgs">' + ''.join(corpo) + '</div>', cid, f'width:{larg}px'))


def janela(c, caminho, colunas, linhas, t, larg=820, stagger=0.07):
    """Janela de app (CRM): 3 bolinhas + caminho + tabela. linhas = [dict(av, nome, tag, tipo='', t=None,
    destaca=t, corta=(t, 'PAUSADA'), troca=(t, 'NOVO TEXTO', tipo))]. Sem t próprio, entram em cascata."""
    jid = _id(c, 'j')
    t0 = _t(c, t)
    c.a(f"entra('#{jid}',{t0});")
    som(t0, 'blip')
    rows = []
    for k, ln in enumerate(linhas):
        rid = f'{jid}-r{k}'
        tr = _t(c, ln['t']) if ln.get('t') is not None else q(t0 + 0.2 + stagger * k)
        c.a(f"entra('#{rid}',{tr},0.16,10);")
        if ln.get('destaca') is not None:
            c.a(f"destaca('#{rid}',{_t(c, ln['destaca'])});")
        if ln.get('corta'):
            tc, novo = ln['corta']
            tc = _t(c, tc)
            c.a(f"tl.set('#{rid} .tag',{{className:'tag neg'}},{tc});tl.set('#{rid} .tag',{{textContent:'{novo}'}},{tc});")
            c.a(f"destaca('#{rid}',{tc},'{VERMELHO}');apaga('#{rid}',{q(tc + 0.45)});")
            som(tc, 'blip')
        if ln.get('troca'):
            tc, novo, tipo = ln['troca']
            tc = _t(c, tc)
            c.a(f"tl.set('#{rid} .tag',{{className:'tag {tipo}'}},{tc});tl.set('#{rid} .tag',{{textContent:'{novo}'}},{tc});"
                f"pop('#{rid} .tag',{tc});")
            som(tc, 'blip')
        av = ln.get('av', '')
        avh = f'<div class="av p">{esc(av)}</div>' if len(av) <= 3 else f'<div class="av p">{ic(av, 26)}</div>'
        val = f'<div class="vl">{esc(ln["valor"])}</div>' if ln.get('valor') else ''
        rows.append(f'<div class="row" id="{rid}">{avh}<div class="nm">{esc(ln["nome"])}</div>{val}'
                    f'<div class="tag {ln.get("tipo", "")}">{esc(ln.get("tag", ""))}</div></div>')
    cols = ''.join(f'<span>{esc(x)}</span>' for x in colunas)
    return c.add(_card('jan', f'<div class="bar"><i></i><i></i><i></i><span>{esc(caminho)}</span></div>'
                       f'<div class="cols">{cols}</div>' + ''.join(rows), jid, f'width:{larg}px'))


def kanban(c, colunas, cartao, sub, t, passos, larg=860):
    """Kanban de colunas; o cartão começa na 1ª coluna e anda pra coluna k no tempo t_k. passos=[(k, t), ...]."""
    kid = _id(c, 'kb')
    t0 = _t(c, t)
    c.a(f"entra('#{kid}',{t0});")
    som(t0, 'blip')
    gap, pad = 18, 16
    cw = (larg - gap * (len(colunas) - 1)) / len(colunas)
    cols = ''.join(f'<div class="col" style="width:{cw:.1f}px"><div class="chd">{esc(x)}</div>'
                   f'<div class="fant"></div><div class="fant"></div></div>' for x in colunas)
    c.a(f"entra('#{kid}-c',{q(t0 + 0.18)},0.18,10);")
    for k, tk in passos:
        tk = _t(c, tk)
        c.a(f"tl.to('#{kid}-c',{{x:{(cw + gap) * k:.1f},duration:0.32,ease:'power3.inOut'}},{tk});")
        som(tk, 'blip')
    ult = len(colunas) - 1
    c.a(f"tl.to('#{kid}-c',{{borderColor:'{LARANJA}',duration:0.15}},{_t(c, passos[-1][1]) + 0.3});" if passos and passos[-1][0] == ult else '')
    card = (f'<div class="kc" id="{kid}-c" style="left:{pad}px;width:{cw - 2 * pad:.1f}px">'
            f'<div class="av p">{ic("user", 24)}</div><div><div class="nm">{esc(cartao)}</div><div class="sb">{esc(sub)}</div></div></div>')
    return c.add(f'<div class="cd kb" id="{kid}" style="width:{larg}px">{cols}{card}</div>')


def checklist(c, itens, numerado=True, larg=820, chime_ultimo=True):
    """Checklist em cascata: itens = [(texto, t_entra, t_ok|None)]. Numerado = badge laranja com numeral serifado.
    O ✓ estala no t_ok; o último ✓ toca o chime de 2 notas."""
    lid = _id(c, 'ck')
    its = []
    for k, (txt, te, tok) in enumerate(itens):
        iid = f'{lid}-{k}'
        te = _t(c, te)
        c.a(f"entra('#{iid}',{te},0.2,14);")
        som(te, 'blip')
        if tok is not None:
            to = _t(c, tok, 0.0)
            c.a(f"pop('#{iid} .ok',{to});destaca('#{iid}',{to});")
            if k == len(itens) - 1 and chime_ultimo:
                som(to, 'chime')
        num = f'<div class="nsq">{k + 1}</div>' if numerado else f'<div class="nsq ico">{ic("check", 40, "bold")}</div>'
        okh = f'<div class="ok">{ic("check", 34, "bold")}</div>' if tok is not None else ''
        its.append(f'<div class="it" id="{iid}">{num}<div class="tx">{_marca(txt)}</div>{okh}</div>')
    return c.add(f'<div class="ck" id="{lid}" style="width:{larg}px">{"".join(its)}</div>')


def numero(c, de, ate, t, dur=1.0, pre='', suf='', rotulo='', barra=None, tam=230, neg=False):
    """Número grande serifado contando de→até (ease-out forte, como o contador 0→100 da referência).
    barra = t (barra de progresso que enche junto até ate %)."""
    nid = _id(c, 'nb')
    t0 = _t(c, t)
    c.a(f"entra('#{nid}',{t0},0.2,14);conta('#{nid}-v',{de},{ate},{t0},{dur});")
    som(t0, 'blip')
    som(q(t0 + dur * 0.7), 'tique', 0.22)
    rot = '<div class="rt"{}>{}</div>'.format(*_espacado(rotulo, 30, 0.3)) if rotulo else ''
    br = ''
    if barra is not None:
        tb = _t(c, barra)
        br = f'<div class="pb"><i id="{nid}-b" style="width:{ate}%"></i></div>'
        c.a(f"estica('#{nid}-b',{tb},{dur});")
    return c.add(f'<div class="nb{" neg" if neg else ""}" id="{nid}">{rot}<div class="v" style="font-size:{tam}px">'
                 f'<span class="pre">{esc(pre)}</span><span id="{nid}-v">{de}</span><span class="u">{esc(suf)}</span></div>{br}</div>')


def alerta(c, texto, sub, t, larg=800, icone='x'):
    """Card de alerta vermelho (negativo): X em círculo vermelho dá pop."""
    aid = _id(c, 'al')
    t0 = _t(c, t)
    c.a(f"entra('#{aid}',{t0});pop('#{aid} .xr',{q(t0 + 0.12)});")
    som(t0, 'blip')
    sb = f'<div class="sb">{esc(sub)}</div>' if sub else ''
    return c.add(_card('al', f'<div class="xr">{ic(icone, 40, "bold")}</div><div><div class="nm">{_marca(texto)}</div>{sb}</div>',
                       aid, f'width:{larg}px'))


def fluxo(c, nos, chip=None, larg=820):
    """Nós (squircle laranja + rótulo) ligados por linha que se desenha. nos = [(icone, rotulo, t, 'neg'|'')].
    chip = (texto, t_saida, t_chegada, idx_destino): pílula que corre pela linha até o nó de destino."""
    fid = _id(c, 'fx')
    n = len(nos)
    nw, lw = 230, (larg - 230 * n) / max(1, n - 1)
    partes = []
    for k, (icn, rot, tk, tipo) in enumerate(nos):
        tk = _t(c, tk)
        partes.append(f'<div class="no" id="{fid}-{k}" style="width:{nw}px"><div class="sq {tipo}">{ic(icn, 62)}</div>'
                      f'<div class="lb">{esc(rot)}</div></div>')
        c.a(f"entra('#{fid}-{k}',{tk},0.22,14);")
        som(tk, 'blip')
        if k < n - 1:
            tl_ = _t(c, nos[k + 1][2])
            partes.append(f'<div class="lk" id="{fid}-l{k}" style="width:{lw:.1f}px"></div>')
            c.a(f"estica('#{fid}-l{k}',{q(max(tk + 0.1, tl_ - 0.32))},0.3);")
    ch = ''
    if chip:
        txt, ts_, tc, dst = chip
        ts_, tc = _t(c, ts_), _t(c, tc)
        x0 = nw / 2
        x1 = nw / 2 + dst * (nw + lw)
        ch = f'<div class="fchip" id="{fid}-c" style="left:{x0:.1f}px">{esc(txt)}</div>'
        c.a(f"entra('#{fid}-c',{ts_},0.16,8);tl.to('#{fid}-c',{{x:{x1 - x0:.1f},duration:{max(0.3, tc - ts_):.2f},ease:'power2.inOut'}},{ts_});")
        destino_neg = nos[dst][3] == 'neg'
        c.a(f"tl.to('#{fid}-c',{{backgroundColor:'{VERMELHO if destino_neg else LARANJA}',duration:0.12}},{tc});"
            f"pop('#{fid}-{dst} .sq',{tc});")
        som(tc, 'blip' if destino_neg else 'chime')
    return c.add(f'<div class="fx" id="{fid}" style="width:{larg}px">{"".join(partes)}{ch}</div>')


def cta(c, texto, t, t_clique, icone='arrow-right', sub=''):
    """Botão genérico (sem link/URL/QR) + cursor que entra e clica: o botão fica laranja e toca o chime."""
    bid = _id(c, 'bt')
    t0, tc = _t(c, t), _t(c, t_clique, 0.0)
    c.a(f"entra('#{bid}',{t0},0.22,14);")
    c.a(f"tl.fromTo('#{bid}-cur',{{opacity:0,x:120,y:90}},{{opacity:1,x:0,y:0,duration:0.3,ease:'power3.out',immediateRender:true}},{q(max(t0 + 0.1, tc - 0.4))});")
    c.a(f"tl.to('#{bid}-cur',{{scale:0.85,duration:0.06}},{tc});tl.to('#{bid}-cur',{{scale:1,duration:0.12}},{q(tc + 0.06)});")
    c.a(f"tl.to('#{bid} .bg',{{opacity:1,duration:0.1}},{q(tc + 0.03)});tl.to('#{bid} .b',{{scale:0.96,duration:0.06}},{tc});"
        f"tl.to('#{bid} .b',{{scale:1,duration:0.14}},{q(tc + 0.06)});")
    som(t0, 'blip')
    som(tc, 'chime')
    sb = f'<div class="ctas">{esc(sub)}</div>' if sub else ''
    return c.add(f'<div class="ctaw" id="{bid}"><div class="b"><span class="bg"></span><span class="bt">{esc(texto)}'
                 f'{ic(icone, 44, "bold")}</span></div>{sb}'
                 f'<svg id="{bid}-cur" class="cur" width="70" height="70" viewBox="0 0 64 64"><path d="M14 8 L14 50 L25 40 '
                 f'L33 56 L40 53 L32 37 L46 37 Z" fill="#fff" stroke="#1a1208" stroke-width="3" stroke-linejoin="round"/></svg></div>')


def semana(c, t, passo=0.12, xis=None, dias=('SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SÁB', 'DOM'), icone='user'):
    """7 dias em cascata; xis = t em que cada dia ganha o X vermelho (em cascata)."""
    sid = _id(c, 'sm')
    t0 = _t(c, t)
    ds = []
    for k, d in enumerate(dias):
        ds.append(f'<div class="dia" id="{sid}-{k}"><div class="d">{d}</div>{ic(icone, 40)}'
                  + (f'<div class="xr">{ic("x", 22, "bold")}</div>' if xis is not None else '') + '</div>')
        c.a(f"entra('#{sid}-{k}',{q(t0 + passo * k)},0.18,12);")
        if xis is not None:
            c.a(f"pop('#{sid}-{k} .xr',{q(_t(c, xis, 0.0) + 0.06 * k)});")
    som(t0, 'blip')
    if xis is not None:
        som(_t(c, xis, 0.0), 'blip')
    return c.add(f'<div class="sem">{"".join(ds)}</div>')


def lista(c, itens, larg=820):
    """Linhas de pessoa/empresa: itens = [dict(av, nome, sub, t, tag=(txt, tipo), apaga=t)] em cascata."""
    lid = _id(c, 'ls')
    rs = []
    for k, it in enumerate(itens):
        rid = f'{lid}-{k}'
        tr = _t(c, it['t'])
        c.a(f"entra('#{rid}',{tr},0.2,14);")
        som(tr, 'blip')
        if it.get('apaga') is not None:
            c.a(f"apaga('#{rid}',{_t(c, it['apaga'])});")
        av = it.get('av', '')
        avh = f'<div class="av">{esc(av)}</div>' if len(av) <= 3 else f'<div class="av">{ic(av, 32)}</div>'
        tg = f'<div class="pill {it["tag"][1]}">{esc(it["tag"][0])}</div>' if it.get('tag') else ''
        rs.append(f'<div class="cd lrow" id="{rid}">{avh}<div class="nt"><div class="nm">{esc(it["nome"])}</div>'
                  f'<div class="sb">{esc(it.get("sub", ""))}</div></div>{tg}</div>')
    return c.add(f'<div class="ls" style="width:{larg}px">{"".join(rs)}</div>')


def reuniao(c, titulo_, sub, t, t_ok, dia='QUI', num='14', larg=800):
    """Card de reunião: folhinha creme (card claro da referência) + texto + ✓ que estala com chime."""
    rid = _id(c, 'rn')
    t0, to = _t(c, t), _t(c, t_ok, 0.0)
    c.a(f"entra('#{rid}',{t0});pop('#{rid} .ok',{to});destaca('#{rid}',{to});")
    som(t0, 'blip')
    som(to, 'chime')
    return c.add(_card('rn', f'<div class="folha"><div class="fd">{esc(dia)}</div><div class="fn">{esc(num)}</div></div>'
                       f'<div class="nt"><div class="nm">{esc(titulo_)}</div><div class="sb">{esc(sub)}</div></div>'
                       f'<div class="ok">{ic("check", 34, "bold")}</div>', rid, f'width:{larg}px'))


def barras(c, valores, t, rotulos=(), passo=0.1, t_linha=None, larg=800, alt=330):
    """Gráfico de barras crescendo (últimas em laranja) + linha de tendência que se desenha em t_linha."""
    gid = _id(c, 'gr')
    t0 = _t(c, t)
    n = len(valores)
    mx = max(valores)
    bs = []
    for k, v in enumerate(valores):
        cls = 'on' if k >= n - 2 else ''
        rot = f'<span>{esc(rotulos[k])}</span>' if k < len(rotulos) else ''
        bs.append(f'<div class="bw"><div class="b {cls}" id="{gid}-{k}" style="height:{v / mx * 100:.1f}%"></div>{rot}</div>')
    c.a(f"entra('#{gid}',{t0},0.2,12);sobe('#{gid} .b',{q(t0 + 0.12)},0.4,{passo});")
    som(t0, 'blip')
    ln = ''
    if t_linha is not None:
        tl_ = _t(c, t_linha)
        lw_, lh_ = larg - 68, alt - 34   # área das barras em px (sem os rótulos)
        pts = ' '.join(f'{(k + 0.5) / n * lw_:.1f},{lh_ - v / mx * lh_ * 0.92 - 14:.1f}' for k, v in enumerate(valores))
        ln = (f'<svg class="tend" width="{lw_}" height="{lh_}" viewBox="0 0 {lw_} {lh_}"><polyline id="{gid}-l" points="{pts}" '
              f'pathLength="1"/></svg>')
        c.a(f"desenha('#{gid}-l',{tl_},0.45);")
        som(tl_, 'blip')
    return c.add(f'<div class="cd gr" id="{gid}" style="width:{larg}px"><div class="gb" style="height:{alt}px">{"".join(bs)}{ln}</div></div>')


def equipe(c, n, t, fantasmas=0, t_x=None, rotulo=''):
    """Time: n avatares em cascata + 'fantasmas' tracejados (contratações que NÃO aconteceram) que ganham X em t_x."""
    eid = _id(c, 'eq')
    t0 = _t(c, t)
    av = []
    for k in range(n):
        av.append(f'<div class="ep" id="{eid}-{k}">{ic("user", 54)}</div>')
        c.a(f"entra('#{eid}-{k}',{q(t0 + 0.08 * k)},0.18,12);")
    for k in range(fantasmas):
        av.append(f'<div class="ep fan" id="{eid}-f{k}">{ic("user-plus", 50)}<div class="xr">{ic("x", 22, "bold")}</div></div>')
        c.a(f"entra('#{eid}-f{k}',{q(t0 + 0.08 * (n + k))},0.18,12);")
        if t_x is not None:
            c.a(f"pop('#{eid}-f{k} .xr',{q(_t(c, t_x, 0.0) + 0.07 * k)});apaga('#{eid}-f{k}',{q(_t(c, t_x, 0.0) + 0.25)});")
    som(t0, 'blip')
    if t_x is not None:
        som(_t(c, t_x, 0.0), 'blip')
    rt = '<div class="eqr"{}>{}</div>'.format(*_espacado(rotulo, 30, 0.24)) if rotulo else ''
    return c.add(f'<div class="eqw"><div class="eq">{"".join(av)}</div>{rt}</div>')


def etapas(c, passos, larg=760):
    """Passos 1-2-3 ligados (ex.: perguntas rápidas): passos = [(rótulo, t)]; cada um acende no seu tempo."""
    pid = _id(c, 'et')
    n = len(passos)
    ps = []
    for k, (rot, tk) in enumerate(passos):
        tk = _t(c, tk)
        ps.append(f'<div class="ep2" id="{pid}-{k}"><div class="bol">{k + 1}</div><div class="lb">{esc(rot)}</div></div>')
        c.a(f"entra('#{pid}-{k}',{tk},0.18,12);tl.to('#{pid}-{k} .bol',{{backgroundColor:'{LARANJA}',color:'#FFF6EA',borderColor:'{LARANJA2}',duration:0.12}},{q(tk + 0.12)});")
        som(tk, 'blip')
        if k < n - 1:
            ps.append(f'<div class="elk"><i id="{pid}-l{k}"></i></div>')
            c.a(f"estica('#{pid}-l{k}',{q(tk + 0.1)},0.25);")
    return c.add(f'<div class="et" style="width:{larg}px">{"".join(ps)}</div>')


def pilula(c, texto, t, icone='sparkle', cls='cheio'):
    """Pílula laranja com ícone (ex.: COM INTELIGÊNCIA ARTIFICIAL) que dá pop na palavra."""
    pid = _id(c, 'pl')
    c.a(f"pop('#{pid}',{_t(c, t)});")
    som(_t(c, t), 'blip')
    return c.add(f'<div class="pill big {cls}" id="{pid}">{ic(icone, 34, "bold")}<span>{esc(texto.upper())}</span></div>')


def linha_icones(c, itens, gap=40):
    """Squircles soltos em linha: itens = [(icone, t, 'neg'|'')]."""
    lid = _id(c, 'li')
    ps = []
    for k, (icn, tk, tipo) in enumerate(itens):
        tk = _t(c, tk)
        ps.append(f'<div class="sq {tipo}" id="{lid}-{k}">{ic(icn, 62)}</div>')
        c.a(f"pop('#{lid}-{k}',{tk});")
        som(tk, 'blip')
    return c.add(f'<div class="lic" style="gap:{gap}px">{"".join(ps)}</div>')


# ---------------------------------------------------------------- peças da v2 "Checklist dos acessos" (07/11)
def passo(c, n, spec, t, icone=None, larg=820):
    """Cabeçalho de passo da v2: squircle laranja com numeral serifado (ou ícone) + título de 2 linhas alinhado à
    esquerda ('linha 1|*linha 2*': a 2ª costuma ser laranja). Entra inteiro com a palavra (t)."""
    pid = _id(c, 'ps')
    t0 = _t(c, t)
    c.a(f"pop('#{pid} .nsq',{t0});entra('#{pid} .pt',{q(t0 + 0.08)},0.22,10);")
    som(t0, 'blip')
    linhas = [ln.strip() for ln in spec.split('|')]
    dentro = ic(icone, 66, 'bold') if icone else str(n)
    return c.add(f'<div class="passo" id="{pid}" style="width:{larg}px"><div class="nsq g{" ico" if icone else ""}">{dentro}</div>'
                 f'<div class="pt">' + ''.join(f'<div>{_marca(ln)}</div>' for ln in linhas) + '</div></div>')


def checkcard(c, itens, cabeca='', larg=780, chime_ultimo=True):
    """Checklist num card escuro (v2 01:02 "FALHOU EM ALGUM?"): caixinhas quadradas que viram ✓ laranja em cascata.
    itens = [(texto, t_entra, t_marca|None, 'ok'|'x')]; 'x' = X vermelho e a linha apaga (item que falhou)."""
    kid = _id(c, 'kc')
    t_card = min(_t(c, it[1]) for it in itens)
    c.a(f"entra('#{kid}',{q(t_card - 0.05) if t_card - 0.05 > c.t0 else t_card});")
    som(t_card, 'blip')
    rs = []
    for k, it in enumerate(itens):
        txt, te, tm = it[:3]
        tipo = it[3] if len(it) > 3 else 'ok'
        rid = f'{kid}-{k}'
        te = _t(c, te)
        if k:
            c.a(f"entra('#{rid}',{te},0.18,10);")
        if tm is not None:
            tm = _t(c, tm, 0.0)
            if tipo == 'x':
                c.a(f"tl.set('#{rid} .cx',{{className:'cx neg'}},{tm});pop('#{rid} .cx .xx',{tm});apaga('#{rid}',{q(tm + 0.3)});")
                som(tm, 'tique')
            else:
                c.a(f"tl.set('#{rid} .cx',{{className:'cx on'}},{tm});pop('#{rid} .cx .vv',{tm});"
                    f"tl.to('#{rid} .tx',{{color:'#F4EBD2',duration:0.12}},{tm});")
                som(tm, 'chime' if (k == len(itens) - 1 and chime_ultimo) else 'check')
        rs.append(f'<div class="kr" id="{rid}"><div class="cx"><span class="vv">{ic("check", 30, "bold")}</span>'
                  f'<span class="xx">{ic("x", 26, "bold")}</span></div><div class="tx">{_marca(txt)}</div></div>')
    cab = f'<div class="kh">{esc(cabeca.upper())}</div>' if cabeca else ''
    return c.add(_card('kcard', cab + ''.join(rs), kid, f'width:{larg}px'))


def pergunta(c, texto, opcoes, t, escolhe=None, rotulo='', larg=800):
    """Pergunta de formulário (sem link, sem URL): enunciado + opções em cascata; escolhe=(k, t) marca a opção k
    (borda laranja + bolinha cheia + blip). rotulo = chapéu pequeno dentro do card (ex.: 'PERGUNTA 1 DE 3')."""
    fid = _id(c, 'pg')
    t0 = _t(c, t)
    c.a(f"entra('#{fid}',{t0});")
    som(t0, 'blip')
    ops = []
    for k, op in enumerate(opcoes):
        oid = f'{fid}-{k}'
        c.a(f"entra('#{oid}',{q(t0 + 0.18 + 0.08 * k)},0.16,8);")
        ops.append(f'<div class="op" id="{oid}"><i class="rd"></i><span>{esc(op)}</span></div>')
    if escolhe:
        k, te = escolhe
        te = _t(c, te, 0.0)
        c.a(f"destaca('#{fid}-{k}',{te});tl.set('#{fid}-{k} .rd',{{className:'rd on'}},{te});pop('#{fid}-{k} .rd',{te});")
        som(te, 'blip')
    rt = f'<div class="kh">{esc(rotulo.upper())}</div>' if rotulo else ''
    return c.add(_card('perg', f'{rt}<div class="pq">{esc(texto)}</div>' + ''.join(ops), fid, f'width:{larg}px'))


def hub(c, centro, satelites, t, larg=820, alt=560):
    """Estrutura em volta de um núcleo (v2 01:10 "estrutura digital"): squircle grande no centro e satélites em
    círculo ligados por linha que se desenha. centro = (icone, rotulo); satelites = [(icone, rotulo, t, 'neg'|'')]."""
    hid = _id(c, 'hb')
    t0 = _t(c, t)
    c.a(f"pop('#{hid}-c',{t0});")
    som(t0, 'blip')
    cx, cy = larg / 2, alt / 2 - 20
    n = len(satelites)
    rx, ry = larg / 2 - 95, alt / 2 - 70
    ps, ls = [], []
    for k, (icn, rot, tk, tipo) in enumerate(satelites):
        ang = -math.pi / 2 + 2 * math.pi * k / n + (math.pi / n if n % 2 == 0 else 0)
        x, y = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
        tk = _t(c, tk)
        ls.append(f'<line id="{hid}-l{k}" x1="{cx:.0f}" y1="{cy:.0f}" x2="{x:.0f}" y2="{y:.0f}" pathLength="1"/>')
        c.a(f"desenha('#{hid}-l{k}',{q(max(t0 + 0.05, tk - 0.18))},0.22);pop('#{hid}-{k}',{tk});")
        som(tk, 'blip')
        lb = f'<div class="lb">{esc(rot)}</div>' if rot else ''
        ps.append(f'<div class="hs" id="{hid}-{k}" style="left:{x:.0f}px;top:{y:.0f}px"><div class="sq p {tipo}">{ic(icn, 44)}</div>{lb}</div>')
    icn, rot = centro
    lb = f'<div class="lb">{esc(rot)}</div>' if rot else ''
    return c.add(f'<div class="hub" style="width:{larg}px;height:{alt}px"><svg class="hl" width="{larg}" height="{alt}">{"".join(ls)}</svg>'
                 f'<div class="hs hc" id="{hid}-c" style="left:{cx:.0f}px;top:{cy:.0f}px"><div class="sq g">{ic(icn, 80)}</div>{lb}</div>'
                 f'{"".join(ps)}</div>')


def icone(c, nome, t, rotulo='', tipo='', som_='blip'):
    """Card laranja com ícone (squircle grande com moldura escura), opcionalmente com rótulo em caixa-alta embaixo."""
    iid = _id(c, 'ig')
    t0 = _t(c, t)
    c.a(f"pop('#{iid} .sq',{t0});" + (f"entra('#{iid} .lb',{q(t0 + 0.1)},0.16,8);" if rotulo else ''))
    som(t0, som_)
    lb = '<div class="lb"{}>{}</div>'.format(*_espacado(rotulo.upper(), 28, 0.3)) if rotulo else ''
    return c.add(f'<div class="igw" id="{iid}"><div class="sq g {tipo}">{ic(nome, 92)}</div>{lb}</div>')


def perfil(c, t, t_clique, rede='INSTAGRAM', usuario='seuperfil', nome='Seu nome',
           botao=('Seguir', 'Seguindo'), foto_em=None, larg=800):
    """CTA da referência: pílula da rede + card de perfil com a foto da pessoa (tirada do próprio vídeo) e selo, botão que
    o cursor clica e muda de texto (laranja + chime). Botão sem link/bio/Direct (regra 29/10)."""
    pid = _id(c, 'pf')
    t0, tc = _t(c, t), _t(c, t_clique, 0.0)
    foto = _foto_perfil(foto_em)
    c.a(f"pop('#{pid}-r',{t0});entra('#{pid}',{q(t0 + 0.08)});")
    c.a(f"tl.fromTo('#{pid}-cur',{{opacity:0,x:110,y:80}},{{opacity:1,x:0,y:0,duration:0.3,ease:'power3.out',immediateRender:true}},{q(max(t0 + 0.2, tc - 0.4))});")
    c.a(f"tl.to('#{pid}-cur',{{scale:0.85,duration:0.06}},{tc});tl.to('#{pid}-cur',{{scale:1,duration:0.12}},{q(tc + 0.06)});"
        f"tl.to('#{pid} .pb2 .bg',{{opacity:1,duration:0.1}},{q(tc + 0.03)});tl.set('#{pid} .pb2 .a',{{display:'none'}},{q(tc + 0.03)});"
        f"tl.set('#{pid} .pb2 .b',{{display:'inline'}},{q(tc + 0.03)});")
    som(t0, 'blip')
    som(tc, 'chime')
    selo = ('<svg class="selo" width="34" height="34" viewBox="0 0 24 24"><path fill="#3897F0" d="M12 1l2.6 2.2 3.4-.4.9 3.3 '
            '3 1.7-1.3 3.2 1.3 3.2-3 1.7-.9 3.3-3.4-.4L12 23l-2.6-2.2-3.4.4-.9-3.3-3-1.7L3.4 13 2.1 9.8l3-1.7.9-3.3 3.4.4z"/>'
            '<path d="M7.5 12.3l3 3 6-6.2" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    return c.add(f'<div class="pfw"><div class="pill rede" id="{pid}-r">{esc(rede)}</div>'
                 f'<div class="cd pf" id="{pid}" style="width:{larg}px"><div class="pfh"><div class="foto" style="background-image:url({foto})"></div>'
                 f'<div class="nt"><div class="nm">{esc(usuario)} {selo}</div><div class="sb">{esc(nome)}</div></div></div>'
                 f'<div class="pb2"><span class="bg"></span><span class="a">{esc(botao[0])}</span><span class="b">{esc(botao[1])}</span>'
                 f'<svg id="{pid}-cur" class="cur" width="64" height="64" viewBox="0 0 64 64"><path d="M14 8 L14 50 L25 40 '
                 f'L33 56 L40 53 L32 37 L46 37 Z" fill="#fff" stroke="#1a1208" stroke-width="3" stroke-linejoin="round"/></svg></div></div></div>')


def _foto_perfil(t=None):
    """Quadrado no rosto da pessoa tirado do base_h.mov (no tempo t ou no meio do 1º take) -> public/perfil.jpg."""
    saida = AQUI / 'public/perfil.jpg'
    if saida.exists():
        return 'perfil.jpg'
    trilha = json.load(open(RAIZ / 'work' / GNN / 'face_track.json'))
    wmed = float(np.median([p['w'] for p in trilha]))
    if t is None:
        fim1 = CORTES[0] if CORTES else trilha[-1]['t']
        t = fim1 / 2
    p = min((p for p in trilha if p['w'] >= 0.7 * wmed), key=lambda p: abs(p['t'] - t))
    lado = int(min(1080, p['w'] * 2.0)) // 2 * 2
    x0 = int(min(max(p['cx'] - lado / 2, 0), 1920 - lado))
    y0 = int(min(max(p['cy'] - lado * 0.45, 0), 1080 - lado))
    subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{p["t"]:.3f}', '-i', str(RAIZ / 'work' / GNN / 'base_h.mov'),
                    '-vf', f'crop={lado}:{lado}:{x0}:{y0},scale=240:240:flags=lanczos', '-frames:v', '1', '-q:v', '3',
                    str(saida)], check=True)
    return 'perfil.jpg'


# ---------------------------------------------------------------- peças de 12/11/2026 (caso real)
def riscado(c, texto, t, t_risco, tam=90, dur=0.25, t_apaga=None):
    """Frase em lettering (EB Garamond creme) que entra junto da fala e é RISCADA quando ela acaba: um traço laranja se
    desenha da esquerda pra direita em `dur` s (~0,25) — nega uma ideia antes da frase seguinte (caso real: "o seu time
    ~~não é pequeno~~, ele está ocupado com a coisa errada"). t = índice/segundos (entra inteira) ou lista com um tempo
    por palavra (entra palavra por palavra, junto da fala); t_risco = começo do traço, sem antecipação (fim da última
    palavra − ~0,08 s); t_apaga = a frase riscada desbota (a 55 %) quando a seguinte entra. Toca blip na entrada e
    tique no risco. Reduz o corpo até caber em 840 px."""
    rid = _id(c, 'rs')
    pal = texto.split()
    while tam > 50 and _fonte('EBGaramond-400.woff2', tam).getlength(texto) > CX_W - 40:
        tam -= 2
    ts = list(t) if isinstance(t, (list, tuple)) else [t] * len(pal)
    assert len(ts) == len(pal), f'riscado: {len(pal)} palavras e {len(ts)} tempos'
    spans = []
    for k, (p, tk) in enumerate(zip(pal, ts)):
        c.a(f"entra('#{rid}-{k}',{_t(c, tk)},0.2,14);")
        spans.append(f'<span class="rw" id="{rid}-{k}">{esc(p)}</span>')
    som(_t(c, ts[0]), 'blip')
    tr = _t(c, t_risco, 0.0)
    c.a(f"tl.fromTo('#{rid}-l',{{scaleX:0,rotation:-1.2}},{{scaleX:1,rotation:-1.2,duration:{dur},ease:'power2.out',"
        f"transformOrigin:'0% 50%'}},{tr});")
    som(tr, 'tique')
    if t_apaga is not None:
        c.a(f"tl.to('#{rid} .rw',{{opacity:0.55,duration:0.2,ease:'power2.out'}},{_t(c, t_apaga)});")
    return c.add(f'<div class="risc" id="{rid}" style="font-size:{tam}px">{" ".join(spans)}<i class="rl" id="{rid}-l"></i></div>')


_CEL_JIT = [(-6, 5, -4), (6, -6, 3), (-4, 8, -2.5), (7, -3, 4.5), (-5, -5, 3.5), (4, 6, -4.5), (-7, 2, 2), (3, -7, -3),
            (6, 5, 4)]   # (dx, dy, rotação°) de cada posição — leve, determinístico
_CEL_HORA = ('08:02', '08:47', '09:31', '10:15', '11:40', '13:22', '15:08', '16:54', '18:30')


def _alt_cab(c):
    """Altura (px da caixa virtual) do chapéu + título já postos na cena."""
    h = 0
    for x in c.cab:
        if 'class="chapeu"' in x:
            h += 45 * (2 if '<br>' in x else 1)
        elif 'class="titulo"' in x:
            h += int(re.search(r'font-size:(\d+)px', x).group(1)) * 1.06 * x.count('<div>')
    return h + (16 * (len(c.cab) - 1) + 34 if c.cab else 0)


def celulares(c, msgs, t, t_fim, cols=4, nomes=('Cliente', 'Lead novo', 'Contato'), ordem=None, acelera=0.85,
              vol=0.17, larg=None, alt=None, sobre=None, tijolo=None):
    """Vários celulares (6–9) com uma conversa de WhatsApp no estilo escuro do Extremo, cada um com uma pergunta parecida
    de cliente, caindo um atrás do outro, rápido e com leve rotação, numa grade que se sobrepõe um pouco (a fileira de
    baixo tampa só a barra de digitar da de cima) — caso real "responde a mesma pergunta 100 vezes". Blip leve a cada
    celular (rajada com intervalo mínimo de 0,1 s entre os sons).
    msgs = ['Quanto custa?', 'Qual o preço?', ...] (um celular por mensagem, na ordem em que chegam); t = 1º celular
    (índice da palavra ou s), t_fim = último; acelera < 1 = o intervalo encurta (a rajada acelera até o fim da frase);
    ordem = posição na grade de cada um (padrão: espalhado). O tamanho se ajusta à caixa do formato — chame DEPOIS do
    chapeu/titulo da cena. Padrões por formato: RL/IN/GL 4 colunas em 820 px; YT 4 colunas em tijolo, até 1250 px.
    Sem radial-gradient/blur/clip-path no CSS do celular: o check do HyperFrames conta os elementos "heavy overlay" (pela
    1ª classe do seletor) e com ~40 o render sai preto na 1ª metade (com gradiente radial, os 8 celulares levavam o
    t142 de 26 a 34). O blur da entrada vem do GSAP e não conta."""
    pid0 = _id(c, 'cl')
    n = len(msgs)
    rows = math.ceil(n / cols)
    g = GEO[FORMATO]
    modo = c.modo if c.modo in 'DG' else 'G'
    alt_v = _caixa(c, modo, g)[3]
    yt = FORMATO == 'YT'
    larg = larg or (1250 if yt else 820)
    sobre = (0.40 if yt else 0.22) if sobre is None else sobre
    tijolo = (yt and rows > 1) if tijolo is None else tijolo
    alt = alt or (alt_v - _alt_cab(c) - 40)
    # tamanho: cabe na altura (aspecto 1:2) e na largura (sobreposição lateral de até 12 % do celular)
    h = alt / (1 + (rows - 1) * (1 - sobre))
    w = h / 2
    meio = 0.5 if tijolo else 0.0
    gx = min(24.0, (larg - w) / (cols - 1 + meio) - w) if cols > 1 else 0.0
    if gx < -0.12 * w:
        w = larg / (1 + 0.88 * (cols - 1 + meio))
        gx = -0.12 * w
    h = 2 * w
    e = w / 10   # 1 em do celular
    sx, sy = w + gx, h * (1 - sobre)
    W_ = (cols - 1 + meio) * sx + w
    H_ = (rows - 1) * sy + h
    # corpo da pergunta: a palavra mais longa cabe na bolha (tela 9,4 em − respiro 1 em, 94 %, menos o padding da
    # bolha 1,1 × corpo), máx. 1,3 em
    fpx = 1.3 * e
    while fpx > 0.8 * e and max(_fonte('inter-latin-600-normal.woff2', round(fpx)).getlength(p)
                                for m in msgs for p in m.split()) > 7.9 * e - 1.1 * fpx:
        fpx -= 0.5
    # nome do contato inteiro no cabeçalho (tela 9,4 − padding 1,3 − seta 1,05 − avatar 2 − 2 vãos 0,9 = 4,15 em)
    fnome = 0.95 * e
    while fnome > 0.6 * e and max(_fonte('inter-latin-600-normal.woff2', round(fnome)).getlength(x) for x in nomes) > 4.0 * e:
        fnome -= 0.5
    ordem = list(ordem) if ordem else random.Random(n * 7 + 3).sample(range(n), n)
    # tempos: rajada que acelera (intervalos em progressão geométrica de razão `acelera`)
    t0, t1 = _t(c, t), _t(c, t_fim)
    if n > 1:
        r = acelera
        a = (t1 - t0) * ((1 - r) / (1 - r ** (n - 1)) if abs(1 - r) > 1e-6 else 1 / (n - 1))
        tempos, acc = [], t0
        for k in range(n):
            tempos.append(q(acc))
            acc += a * r ** k
    else:
        tempos = [t0]
    curto = min((b - a_ for a_, b in zip(tempos, tempos[1:])), default=1)
    if curto < 0.12:
        print(f'  AVISO {c.id}: celulares com {curto:.2f} s entre um e outro (< 0,12 s, o blip some) — aumente o trecho ou use acelera mais perto de 1')
    cels = []
    for k, (msg, tk) in enumerate(zip(msgs, tempos)):
        pos = ordem[k]
        row, col = divmod(pos, cols)
        na_linha = min(cols, n - row * cols)
        off = (cols - na_linha) * sx / 2 + (sx / 2 if tijolo and row % 2 else 0)
        dx, dy, rot = _CEL_JIT[pos % len(_CEL_JIT)]
        x, y = col * sx + off + dx, row * sy + dy
        cid = f'{pid0}-{k}'
        c.ev.append(tk)
        c.a(f"tl.fromTo('#{cid}',{{opacity:0,y:-46,scale:1.14,rotation:{rot + (8 if rot >= 0 else -8)},filter:'blur(6px)'}},"
            f"{{opacity:1,y:0,scale:1,rotation:{rot},filter:'blur(0px)',duration:0.22,ease:'back.out(1.5)'}},{tk});"
            f"tl.fromTo('#{cid}-b',{{opacity:0,scale:0.5}},{{opacity:1,scale:1,duration:0.18,ease:'back.out(1.7)',"
            f"transformOrigin:'0% 100%'}},{q(tk + 0.08)});")
        som(tk, 'blip', vol, gap=0.1)
        nome = nomes[k % len(nomes)]
        # a barra de digitar só nos de baixo: nos de cima ela fica atrás da fileira seguinte (texto sobre texto)
        barra = (f'<div class="cin"><div class="cf"><span>Mensagem</span></div><div class="cm">{ic("microphone", 24, "fill")}'
                 f'</div></div>') if row == rows - 1 or sobre < 0.15 else ''
        cels.append(
            f'<div class="celw" id="{cid}" style="left:{x:.1f}px;top:{y:.1f}px;width:{w:.1f}px;height:{h:.1f}px;'
            f'font-size:{e:.2f}px;z-index:{row * 10 + col}"><div class="cel"><div class="ilha"></div><div class="tela">'
            f'<div class="chd">{ic("caret-left", 24, "bold")}<div class="cav">{ic("user", 24)}</div>'
            f'<div class="cnt"><div class="cnm" style="font-size:{fnome:.1f}px">{esc(nome)}</div><div class="csb">online</div></div></div>'
            f'<div class="cms"><div class="cdia">HOJE</div><div class="cb" id="{cid}-b" style="font-size:{fpx:.1f}px">'
            f'<span>{esc(msg)}</span><span class="chr">{_CEL_HORA[k % len(_CEL_HORA)]}</span></div></div>'
            f'{barra}</div></div></div>')
    return c.add(f'<div class="celg" id="{pid0}" style="width:{W_:.1f}px;height:{H_:.1f}px">{"".join(cels)}</div>')


# ================================================================ SFX sintetizados (numpy, sem baixar nada)
def _grava(nome, x, sr=48000):
    x = np.clip(x, -1, 1)
    _SFX_DIR.mkdir(exist_ok=True)
    with wave.open(str(_SFX_DIR / f'{nome}.wav'), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        est = np.stack([x, x], 1) if x.ndim == 1 else x
        w.writeframes((est * 32767).astype(np.int16).tobytes())


def sintetizar_sfx(forcar=False):
    """tique (25 ms, banda larga ~6,5 kHz), chime de 2 notas (Dó7 2093 Hz → Sol7 3136 Hz, 0,45 s entre elas),
    blip (~2,35 kHz, 140 ms) e whoosh descendente (~0,8 s, 9 → 3 kHz). Medidas da analise.md §10."""
    if not forcar and all((_SFX_DIR / f'{n}.wav').exists() for n in ('tique', 'chime', 'blip', 'whoosh')):
        return
    sr = 48000
    rng = np.random.default_rng(7)
    # tique: ruído com derivada (puxa pro agudo) + clique senoidal curto; estéreo levemente diferente
    n = int(0.03 * sr)
    tt = np.arange(n) / sr
    env = np.exp(-tt / 0.0045)
    l = np.diff(rng.standard_normal(n + 1)) * env * 0.5 + np.sin(2 * np.pi * 6500 * tt) * env * 0.5
    r = np.diff(rng.standard_normal(n + 1)) * env * 0.5 + np.sin(2 * np.pi * 6300 * tt) * env * 0.5
    est = np.stack([l, r], 1)
    _grava('tique', est / np.abs(est).max() * 0.7)
    # chime: 2 notas com parcial 2x baixo, ataque de 3 ms, cauda de ~0,4 s
    tot = int(1.15 * sr)
    x = np.zeros(tot)
    for f0, ini in ((2093.0, 0.0), (3136.0, 0.45)):
        i0 = int(ini * sr)
        tt = np.arange(tot - i0) / sr
        e = np.minimum(1, tt / 0.003) * np.exp(-tt / 0.22)
        x[i0:] += e * (np.sin(2 * np.pi * f0 * tt) + 0.18 * np.sin(2 * np.pi * 2 * f0 * tt) + 0.06 * np.sin(2 * np.pi * 3 * f0 * tt))
    _grava('chime', x / np.abs(x).max() * 0.7)
    # blip: 2,4 → 2,25 kHz, 140 ms
    n = int(0.16 * sr)
    tt = np.arange(n) / sr
    fr = 2400 - 150 * (tt / tt[-1])
    fase = 2 * np.pi * np.cumsum(fr) / sr
    e = np.minimum(1, tt / 0.002) * np.exp(-tt / 0.045)
    x = e * (np.sin(fase) + 0.12 * np.sin(2 * fase))
    _grava('blip', x / np.abs(x).max() * 0.7)
    # whoosh: ruído filtrado com passa-banda descendo de 9 kHz a 3 kHz (bloco a bloco por FFT), envelope sobe e desce
    n = int(0.8 * sr)
    ruido = rng.standard_normal((n, 2))
    blocos, saida = 40, np.zeros((n, 2))
    bl = n // blocos
    janela = np.hanning(bl * 2)
    for b in range(blocos * 2 - 1):
        i0 = b * bl // 2
        seg = ruido[i0:i0 + bl * 2]
        if len(seg) < bl * 2:
            break
        cen = 9000 * (3000 / 9000) ** (i0 / n)
        S = np.fft.rfft(seg * janela[:, None], axis=0)
        f = np.fft.rfftfreq(bl * 2, 1 / sr)
        S *= np.exp(-0.5 * ((np.log(f + 1) - np.log(cen)) / 0.45) ** 2)[:, None]
        saida[i0:i0 + bl * 2] += np.fft.irfft(S, n=bl * 2, axis=0)
    tt = np.arange(n) / n
    env = np.sin(np.pi * np.clip(tt / 0.55, 0, 1) ** 0.7 * 0.5) ** 2 * np.exp(-np.clip(tt - 0.45, 0, 1) * 6)
    saida *= env[:, None]
    _grava('whoosh', saida / np.abs(saida).max() * 0.7)


# ================================================================ mídia (recortes da pessoa por formato)
def _dur(arq):
    out = subprocess.run([FF, '-hide_banner', '-i', str(arq)], capture_output=True, text=True).stderr
    h, m, s = out.split('Duration: ')[1].split(',')[0].split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def _takes(dur_base):
    lim = [0.0] + [c for c in CORTES if 0.3 < c < dur_base - 0.3] + [dur_base]
    return list(zip(lim, lim[1:]))


def recorte(nome, saida_wh, rosto, pos_y, sigma=1.2):
    """Recorte da pessoa pra saida_wh a partir de work/<id>/base_h.mov, POR TAKE (cortes_visuais.json): em cada take a
    janela tem tamanho fixo, escolhido pra o rosto ficar com ~`rosto` px de largura no quadro final (sem nunca ampliar
    além do que o 16:9 tem de altura/largura), com o centro do rosto a `pos_y` da altura; na horizontal segue o rosto
    devagar (média de ~1,2 s, câmera suave de 02/11), sem atravessar o corte. Guarda os parâmetros em <nome>.json (o
    motor usa pra achar queixo e cabeça). Não refaz se o arquivo já existe (apague o .mp4 pra refazer)."""
    pub = AQUI / 'public'
    saida, meta = pub / nome, (pub / nome).with_suffix('.json')
    if saida.exists() and meta.exists():
        from pessoa_cheio import video_ok   # 09/11 (varredura): recorte gerado pela metade não pode ser reaproveitado
        if video_ok(saida):
            prm = json.loads(meta.read_text())
            import av
            with av.open(str(saida)) as ct:
                tam = (ct.streams.video[0].width, ct.streams.video[0].height)
            # 12/11 (REGRA: a cor da pessoa nunca muda): recorte feito com a COR_V antiga (grade) é refeito sem ela — o
            # antigo vai pra Lixeira; recorte sem grade mas em BT.709 só troca a matriz (cor_pessoa.py). Recorte de outro
            # tamanho (ex.: a dividida do RL vertical, que passou de 960 pra 1160 de altura) também é refeito.
            if (VERTICAL and not (prm and prm[0].get('cor') == 'original')) or tam != tuple(saida_wh):
                print(f'  {saida.name}: ' + (f'tamanho {tam[0]}x{tam[1]} != {saida_wh[0]}x{saida_wh[1]}'
                                             if tam != tuple(saida_wh) else 'feito com a cor alterada (COR_V antiga)')
                      + ' — refazendo (o antigo vai pra Lixeira)')
                if not cor_pessoa.lixeira(saida):
                    sys.exit(f'{saida.name} não foi pra Lixeira (aberto em outro programa?) — feche e rode de novo')
            else:
                if not cor_pessoa.ok(saida):
                    cor_pessoa.converter(saida)
                _CROP[nome] = prm
                return saida
        else:
            print(f'AVISO: {saida.name} estava corrompido (gerado pela metade); refazendo')
            saida.unlink()
    if VERTICAL:
        return _recorte_vertical(nome, saida_wh, rosto, sigma)
    base = RAIZ / 'work' / GNN / 'base_h.mov'
    trilha = json.load(open(RAIZ / 'work' / GNN / 'face_track.json'))
    wmed = float(np.median([p['w'] for p in trilha]))
    boas = [p for p in trilha if p['w'] >= 0.6 * wmed] or trilha
    dur_b = _dur(base)
    n_tot = int(round(dur_b * FPS))
    W_, H_ = saida_wh
    smin = max(H_ / 1080, W_ / 1920)
    params, filtros, cmds = [], [], []
    takes = _takes(dur_b)
    for k, (a, b) in enumerate(takes):
        ps = [p for p in boas if a <= p['t'] < b] or boas
        wr, cyr = float(np.median([p['w'] for p in ps])), float(np.median([p['cy'] for p in ps]))
        s = max(smin, rosto / wr)
        cw = min(1920, int(round(W_ / s / 2)) * 2)
        ch = min(1080, int(round(H_ / s / 2)) * 2)
        s = H_ / ch
        y0 = int(min(max(round(cyr - pos_y * ch), 0), 1080 - ch))
        # 07/11 (aditivo): se o topo da cabeça (cy − 0,85·w) ficaria fora da janela, desce a janela até caber com 4 %
        # de folga (ex.: GL D no take em que ele chega perto da câmera). Recortes já gerados não mudam.
        y0 = int(min(y0, max(0, round(cyr - 0.85 * wr - 0.04 * ch))))
        fa, fb = int(round(a * FPS)), (n_tot if k == len(takes) - 1 else int(round(b * FPS)))
        tq = np.arange(fa, fb) / FPS
        cx = np.interp(tq, [p['t'] for p in ps], [p['cx'] for p in ps])
        sig = sigma * FPS
        ker = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2)
        ker /= ker.sum()
        cx = np.convolve(np.pad(cx, len(ker) // 2, mode='edge'), ker, mode='valid')[:len(tq)]
        x0 = np.clip(cx - cw / 2, 0, 1920 - cw).round().astype(int)
        arq = f'{saida.stem}.k{k}.cmd.txt'
        (pub / arq).write_text(''.join(f'{i / FPS:.4f} crop@k{k} x {int(x)};\n' for i, x in enumerate(x0)), encoding='utf-8')
        cmds.append(pub / arq)
        filtros.append(f'[s{k}]trim=start_frame={fa}:end_frame={fb},setpts=PTS-STARTPTS,sendcmd=f={arq},'
                       f'crop@k{k}={cw}:{ch}:{int(x0[0])}:{y0},scale={W_}:{H_}:flags=lanczos,setsar=1[v{k}]')
        params.append(dict(a=round(a, 4), b=round(b, 4), y0=y0, s=round(s, 4), rosto=round(wr * s), cw=cw, ch=ch,
                           cabeca=round((cyr - 0.85 * wr - y0) * s), queixo=round((cyr + 0.55 * wr - y0) * s)))
    n = len(takes)
    grafo = (f'[0:v]split={n}' + ''.join(f'[s{k}]' for k in range(n)) + ';' + ';'.join(filtros) + ';'
             + ''.join(f'[v{k}]' for k in range(n)) + f'concat=n={n}:v=1:a=0[out]')
    # 12/11 (REGRA: a cor da pessoa nunca muda): só troca a matriz pra BT.601 (mesma cor; ver cor_pessoa.py)
    grafo = grafo.replace('[0:v]split=', f'[0:v]{cor_pessoa.vf(base)[1:] or "null"},split=', 1)
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(base), '-filter_complex', grafo, '-map', '[out]', '-an',
                    '-r', str(FPS), '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-g', '30', '-keyint_min', '30',
                    '-pix_fmt', 'yuv420p', *cor_pessoa.ARGS, '-movflags', '+faststart', saida.name], check=True, cwd=str(pub))
    for f in cmds:
        f.unlink()
    meta.write_text(json.dumps(params), encoding='utf-8')
    _CROP[nome] = params
    print(f'  recorte {nome} -> {W_}x{H_}: ' + ' | '.join(f"take {p['a']:.1f}-{p['b']:.1f}s janela {p['cw']}x{p['ch']} "
                                                         f"rosto {p['rosto']}px cabeça y{p['cabeca']}" for p in params))
    return saida


# 08/11/2026 — fonte vertical refeita (o usuário reprovou o caso real/caso real: "cor estranha", "enquadramento ruim",
# "sobra espaço em cima e corta ele embaixo"). Agora é PLANO MÉDIO: rosto bem menor que o close antigo (~570 px), cabeça
# no terço de cima com folga pequena, queixo e ombros dentro. Como o celular não tem largura pra isso no quadro largo,
# o vídeo fica numa coluna central com as laterais esfumadas (gradiente, sem blur) no marrom do estilo.
# ALVO_V[(formato, papel)] = (largura do rosto no quadro final em px, 0 = janela mais larga possível; topo da cabeça em
# fração da altura do quadro). Topo da cabeça = cy − 0,62·w e queixo = cy + 0,55·w (calibrado no g22/b53b em 08/11: a
# caixa do detector é só o rosto, sem cabelo).
ALVO_V = {('RL', 'D'): (380, 0.10), ('RL', 'T'): (0, 0.10), ('IN', 'D'): (300, 0.10), ('IN', 'T'): (470, 0.10),
          ('GL', 'D'): (260, 0.10), ('GL', 'T'): (420, 0.10), ('YT', 'D'): (0, 0.10), ('YT', 'T'): (450, 0.10)}
K_CAB_V, K_QX_V = 0.62, 0.55
# 12/11/2026 — REGRA DO USUÁRIO (caso real "cor alterada", caso real "não muda a cor dele"): a cor da pessoa NUNCA muda.
# A COR_V de 08/11 (hue/colorbalance/curves pra imitar o "Cor pessoa ref2") foi REMOVIDA: medida no g22, ela tirava
# -27 de vermelho e -15 de verde da pele (testa 250,178,148 -> 209,156,147). O recorte só troca a matriz pra BT.601
# (mesma cor) por causa da extração JPG do render do HyperFrames — ver hyperframes/cor_pessoa.py.
FUNDO_V = '0x140d06'   # marrom do estilo atrás da coluna do vídeo (com vinheta)


def _suave(v, seg, med=True):
    """mediana móvel de 0,8 s (tira detecção solta) + gaussiana de `seg` s."""
    v = np.asarray(v, float)
    if med:
        m = int(0.8 * FPS) | 1
        pad = np.pad(v, m // 2, mode='edge')
        v = np.array([np.median(pad[i:i + m]) for i in range(len(v))])
    sig = max(1.0, seg * FPS)
    ker = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2)
    ker /= ker.sum()
    return np.convolve(np.pad(v, len(ker) // 2, mode='edge'), ker, mode='valid')[:len(v)]


def _recorte_vertical(nome, saida_wh, rosto, sigma=1.2):
    """Fonte de celular (work/<id>/base.mov 1620x2880, sem base_h.mov). Por take: escala fixa pra o rosto ter ~ALVO_V
    px (janela nunca maior que o vertical); se ainda sobra teto, aproxima um pouco (rosto ≤ 60 % da largura); se o
    queixo passaria de 90 % da altura, abre. A janela segue a cabeça devagar na vertical (mediana 0,8 s + gaussiana
    1,2 s) e o rosto na horizontal. Quando o vídeo fica mais estreito que o quadro, vai numa coluna central com as
    bordas esfumadas sobre o marrom do estilo. Cor: a ORIGINAL (12/11: nada de grade; só a matriz BT.601 do
    cor_pessoa). Guarda y0s (10/s) pro _rosto_T achar queixo e cabeça."""
    pub = AQUI / 'public'
    saida, meta = pub / nome, (pub / nome).with_suffix('.json')
    base = RAIZ / 'work' / GNN / 'base.mov'
    BW, BH = 1620, 2880
    trilha = json.load(open(RAIZ / 'work' / GNN / 'face_track.json'))
    wmed = float(np.median([p['w'] for p in trilha]))
    boas = [p for p in trilha if 0.6 * wmed <= p['w'] <= 1.5 * wmed] or trilha
    dur_b = _dur(base)
    n_tot = int(round(dur_b * FPS))
    W_, H_ = saida_wh
    papel = 'T' if nome.endswith('-T.mp4') else 'D'
    alvo, f_topo = ALVO_V[(FORMATO, papel)]
    params, filtros, cmds = [], [], []
    takes = _takes(dur_b)
    for k, (a, b) in enumerate(takes):
        ps = [p for p in boas if a <= p['t'] < b] or boas
        tp = [p['t'] for p in ps]
        wr = float(np.median([p['w'] for p in ps]))
        fa, fb = int(round(a * FPS)), (n_tot if k == len(takes) - 1 else int(round(b * FPS)))
        tq = np.arange(fa, fb) / FPS
        cx = _suave(np.interp(tq, tp, [p['cx'] for p in ps]), sigma)
        # topo da cabeça: mediana 0,8 s, depois o MÍNIMO numa janela de ±0,6 s (a janela sobe antes de ele subir — no
        # b53b a suavização atrasada encostava o cabelo no alto) e gaussiana 1,2 s
        topo = _suave(np.interp(tq, tp, [p['cy'] - K_CAB_V * p['w'] for p in ps]), 0.01)
        mm = int(0.6 * FPS)
        pad = np.pad(topo, mm, mode='edge')
        topo = _suave(np.array([pad[i:i + 2 * mm + 1].min() for i in range(len(topo))]), 1.2, med=False)
        qx = _suave(np.interp(tq, tp, [p['cy'] + K_QX_V * p['w'] for p in ps]), 1.2)
        # 08/11 (usuário, caso real "tá HORRÍVEL isso"): nada de coluna estreita com laterais escuras — o vídeo SEMPRE
        # ocupa a largura inteira do quadro (cover); a janela nunca é mais larga nem mais alta que o vertical
        s_lo = max(H_ / BH, W_ / BW)
        s = max(s_lo, alvo / wr) if alvo else max(s_lo, W_ / BW)
        # quadro inteiro (RL T): aproxima no máximo 8 % (no b53b o celular deixa ~25 % de teto, mas ele chega perto
        # da câmera no fim e o rosto passava de 66 %); nos outros, rosto ≤ 60 % da largura
        s_cap = max(s, min(0.60 * W_ / wr, s * 1.08)) if not alvo else max(s, 0.60 * W_ / wr)
        if papel == 'D' and not ZOOM_D:   # 13/11 (caso real): sem zoom na dividida = nem aproximar o recorte (pessoa o menor possível na largura toda)
            s_cap = s
        t_med, q95 = float(np.median(topo)), float(np.percentile(qx, 95))
        for _ in range(80):
            ch = H_ / s
            y0m = min(max(t_med - f_topo * ch, 0), BH - ch)
            if (q95 - y0m) * s > 0.90 * H_ and s > s_lo * 1.001:            # queixo apertado embaixo: abre
                s = max(s_lo, s / 1.02)
            elif (t_med - y0m) * s > (f_topo + 0.05) * H_ and s < s_cap:     # sobra teto: aproxima um pouco
                s = min(s_cap, s * 1.02)
            else:
                break
        cw = min(BW, int(W_ / s / 2) * 2)
        ch = min(BH, int(round(H_ / s / 2)) * 2)
        s = H_ / ch
        dw = min(W_, int(round(cw * s / 2)) * 2)
        if W_ - dw <= 8:   # 08/11 (varredura): falta de 2-4 px por arredondamento não pode virar laterais esfumadas
            dw = W_
        x0 = np.clip(cx - cw / 2, 0, BW - cw).round().astype(int)
        y0s = np.clip(topo - f_topo * ch, 0, BH - ch).round().astype(int)
        y0 = int(np.median(y0s))
        arq = f'{saida.stem}.k{k}.cmd.txt'
        (pub / arq).write_text(''.join(f'{i / FPS:.4f} crop@k{k} x {int(x)}, crop@k{k} y {int(y)};\n'
                                       for i, (x, y) in enumerate(zip(x0, y0s))), encoding='utf-8')
        cmds.append(pub / arq)
        filtros.append(f'[s{k}]trim=start_frame={fa}:end_frame={fb},setpts=PTS-STARTPTS,sendcmd=f={arq},'
                       f'crop@k{k}={cw}:{ch}:{int(x0[0])}:{int(y0s[0])},scale={dw}:{H_}:flags=lanczos,setsar=1')
        idx = [min(len(y0s) - 1, max(0, int(round((p['t'] - a) * FPS)))) for p in ps]
        cab = [p['cy'] - K_CAB_V * p['w'] - y0s[i] for p, i in zip(ps, idx)]
        qxs = [p['cy'] + K_QX_V * p['w'] - y0s[i] for p, i in zip(ps, idx)]
        params.append(dict(a=round(a, 4), b=round(b, 4), y0=y0, s=round(s, 4), rosto=round(wr * s), cw=cw, ch=ch,
                           dw=dw, cabeca=round(float(np.percentile(cab, 5)) * s),
                           queixo=round(float(np.percentile(qxs, 95)) * s), y0s=[int(v) for v in y0s[::3]],
                           cor='original'))
    n = len(takes)
    dw = max(p['dw'] for p in params)
    # takes de larguras diferentes: os mais estreitos ganham margem do marrom até a maior (a máscara é uma só)
    filtros = [f + (f',pad={dw}:{H_}:(ow-iw)/2:0:color={FUNDO_V}' if p['dw'] < dw else '') + f'[v{k}]'
               for k, (f, p) in enumerate(zip(filtros, params))]
    # 12/11 (REGRA: a cor da pessoa nunca muda): sem grade; só a matriz BT.601 (mesma cor) pro render do HF (cor_pessoa.py)
    grafo = (f'[0:v]{cor_pessoa.vf(base)[1:] or "null"},split={n}' + ''.join(f'[s{k}]' for k in range(n)) + ';'
             + ';'.join(filtros) + ';' + ''.join(f'[v{k}]' for k in range(n)) + f'concat=n={n}:v=1:a=0[cat]')
    entradas = ['-i', str(base)]
    if dw < W_:
        mask = pub / f'{saida.stem}.mascara.png'
        F = min(150.0, 0.17 * dw)
        xx = np.arange(dw, dtype=float)
        e = np.clip(np.minimum(xx, dw - 1 - xx) / F, 0, 1)
        e = e * e * (3 - 2 * e)
        Image.fromarray(np.tile((e * 255).round().astype(np.uint8), (H_, 1)), 'L').save(mask)
        entradas += ['-loop', '1', '-framerate', str(FPS), '-t', f'{dur_b:.3f}', '-i', mask.name]
        grafo += (f';[1:v]format=gray[m];[cat]format=yuva420p[ca];[ca][m]alphamerge[cm];'
                  f'color=c={FUNDO_V}:s={W_}x{H_}:r={FPS}:d={dur_b:.3f},vignette=angle=PI/3.2[bg];'
                  f'[bg][cm]overlay=x={(W_ - dw) // 2}:y=0:shortest=1,format=yuv420p[out]')
        cmds.append(mask)
    else:
        grafo += ';[cat]null[out]'
    subprocess.run([FF, '-v', 'error', '-y', *entradas, '-filter_complex', grafo, '-map', '[out]', '-an',
                    '-r', str(FPS), '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-g', '30', '-keyint_min', '30',
                    '-pix_fmt', 'yuv420p', *cor_pessoa.ARGS, '-movflags', '+faststart', saida.name], check=True, cwd=str(pub))
    for f in cmds:
        f.unlink()
    meta.write_text(json.dumps(params), encoding='utf-8')
    _CROP[nome] = params
    print(f'  recorte VERTICAL {nome} -> {W_}x{H_}: ' + ' | '.join(
        f"take {p['a']:.1f}-{p['b']:.1f}s janela {p['cw']}x{p['ch']} coluna {p['dw']}px y{p['y0']} rosto {p['rosto']}px "
        f"cabeça y{p['cabeca']} queixo y{p['queixo']}" for p in params))
    return saida


def _midia():
    """(vídeo da dividida, vídeo da pessoa cheio) do formato, gerando o que faltar."""
    g = GEO[FORMATO]
    sx, sy, sw, sh = g['slot']
    d, t = f'pessoa-{FORMATO}-D.mp4', f'pessoa-{FORMATO}-T.mp4'
    recorte(d, (CARTAO_D[0], CARTAO_D[1]) if (CARTAO_D and FORMATO == 'RL') else (sw, sh), *g['rosto_D'])
    recorte(t, (g['w'], g['h']), *g['rosto_T'])
    return d, t


def _preparar():
    """Fontes, gsap, hyperframes.json e voz.m4a (loudnorm -16) se faltarem — o motor não depende do preparar.py."""
    pub = AQUI / 'public'
    (pub / 'fonts').mkdir(parents=True, exist_ok=True)
    for nome, pasta in _FONTES.items():
        if not (pub / 'fonts' / nome).exists():
            shutil.copy2(pasta / nome, pub / 'fonts' / nome)
    if not (pub / 'vendor/gsap.min.js').exists():
        (pub / 'vendor').mkdir(exist_ok=True)
        shutil.copy2(RAIZ / '.claude/skills/talking-head-recut/assets/vendor/gsap.min.js', pub / 'vendor/gsap.min.js')
    if not (pub / 'hyperframes.json').exists():
        (pub / 'hyperframes.json').write_text(json.dumps({
            '$schema': 'https://hyperframes.heygen.com/schema/hyperframes.json',
            'registry': 'https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry',
            'paths': {'blocks': 'compositions', 'components': 'compositions/components', 'assets': 'assets'},
            'media': {'autoProxy': True}, 'authoringSkill': 'talking-head-recut'}, indent=2), encoding='utf-8')
    if not (pub / 'voz.m4a').exists():
        subprocess.run([FF, '-v', 'error', '-y', '-i', str(RAIZ / 'work' / GNN / 'voice.wav'), '-af',
                        'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k',
                        str(pub / 'voz.m4a')], check=True)


def _musica():
    """Cama: trecho do começo da faixa (é um build lento de pads, como a da referência), cortada na duração e com
    fade-out de 0,6 s. Volume no <audio> (~25 dB abaixo da voz)."""
    saida = AQUI / 'public/musica.m4a'
    if not saida.exists() and MUSICA.exists():
        subprocess.run([FF, '-v', 'error', '-y', '-i', str(MUSICA), '-vn', '-t', f'{DUR:.2f}', '-af',
                        f'afade=t=in:st=0:d=0.35,afade=t=out:st={DUR - 0.6:.2f}:d=0.6', '-ar', '48000', '-c:a', 'aac',
                        '-b:a', '160k', str(saida)], check=True)
    return saida.exists()


# ================================================================ LEGENDA (1 linha, branca, sombra leve, sem animação)
def _tokens():
    toks, i = [], 0
    while i < len(W):
        if i in REPL:
            n, novos = REPL[i]
            ss = [W[j]['s'] for j in range(i, i + n)]
            for k, tk in enumerate(novos):
                toks.append((tk, ss[min(k, len(ss) - 1)], W[min(i + k, i + n - 1)]['e']))
            i += n
        else:
            toks.append((W[i]['w'], W[i]['s'], W[i]['e']))
            i += 1
    return toks


def blocos_legenda():
    toks = _tokens()
    blocos, k = [], 0
    for parte in re.split(r'\||\n', FRASES):
        txt = ' '.join(parte.split())
        if not txt:
            continue
        ws = txt.split()
        seg = toks[k:k + len(ws)]
        for a, b in zip(ws, seg):
            assert norm(a) == norm(b[0]), f"legenda: '{a}' != '{b[0]}' no token {k} ({' '.join(x[0] for x in toks[k:k + 6])})"
        blocos.append(dict(txt=txt, s=seg[0][1], e=seg[-1][2]))
        k += len(ws)
    assert k == len(toks), f"legenda: sobraram palavras: {' '.join(x[0] for x in toks[k:])}"
    for a, b in zip(blocos, blocos[1:]):
        a['e'] = min(b['s'], a['e'] + 0.9)   # some na pausa longa, senão emenda no próximo
    blocos[-1]['e'] = min(DUR - 0.05, blocos[-1]['e'] + 0.9)
    return blocos


def _leg_px(txt, px, larg_max):
    while px > 34 and _fonte('TikTokSans-Variable.ttf', px).getlength(txt) > larg_max:
        px -= 2
    return px, _fonte('TikTokSans-Variable.ttf', px).getlength(txt)


LIM_T = {'RL': 1248, 'IN': 1215, 'GL': 975, 'YT': 1000}   # base da legenda na pessoa cheio (RL: 65 % da altura)
_TRILHA = []


def _rosto_T(a, z, escalas):
    """(queixo máx, cabeça mín, rosto máx) em px do quadro na pessoa cheio entre a e z, pelo face_track (queixo =
    cy + 0,55·w, topo da cabeça = cy − 0,85·w no 16:9), com o recorte do take e o zoom CSS da cena."""
    if not _TRILHA:
        _TRILHA.extend(json.load(open(RAIZ / 'work' / GNN / 'face_track.json')))
    takes = _CROP[f'pessoa-{FORMATO}-T.mp4']
    oy = GEO[FORMATO]['h'] * GEO[FORMATO]['origem_T']
    qs, cs, rs = [], [], []
    wmed = float(np.median([p['w'] for p in _TRILHA]))
    for p in _TRILHA:
        if a - 0.1 <= p['t'] <= z + 0.1 and p['w'] >= 0.6 * wmed:
            tk = next((k for k in takes if k['a'] <= p['t'] < k['b']), takes[-1])
            e = max([e for t_, e in escalas if t_ <= p['t']] or [escalas[0][1]])
            ty0 = tk['y0']
            if tk.get('y0s'):   # recorte vertical: a janela acompanha a cabeça (10 alturas por segundo)
                ty0 = tk['y0s'][min(len(tk['y0s']) - 1, max(0, int((p['t'] - tk['a']) * 10)))]
            kc = K_CAB_V if VERTICAL else 0.85   # 08/11: no celular a caixa do detector é só o rosto (calibrado)
            yq = (p['cy'] + 0.55 * p['w'] - ty0) * tk['s']
            yc = (p['cy'] - kc * p['w'] - ty0) * tk['s']
            qs.append(oy + (yq - oy) * e)
            cs.append(oy + (yc - oy) * e)
            rs.append(p['w'] * tk['s'] * e)
    if not qs:
        return 0, 0, 0
    # robusto contra detecção solta: queixo no percentil 90, cabeça no 10, rosto na mediana
    qx, cb, ro = float(np.percentile(qs, 90)), float(np.percentile(cs, 10)), float(np.median(rs))
    return qx, cb, ro


def _legenda_html(intervalos):
    """intervalos = [(t0, t1, modo, escalas)] das cenas; trecho < 0,28 s some. REGRA DO USUÁRIO 08/11/2026: legenda SÓ
    na pessoa cheio (T) — na dividida (D, inclusive o lado a lado do YT) e no gráfico cheio (G) não há legenda ("quando
    tem tela dividida, não coloque legenda — assim tem muita informação na tela"). No T ela fica logo abaixo do queixo
    (nunca acima do limite LIM_T; se não couber, avisa)."""
    g = GEO[FORMATO]
    out = []
    for b in blocos_legenda():
        for a, z, modo, escalas in intervalos:
            s, e = max(b['s'], a), min(b['e'], z)
            if modo != 'T' or e - s < 0.28:
                continue
            if PROIBIDO.search(b['txt']):
                print(f'  AVISO legenda "{b["txt"]}" ({s:.2f}s) tem palavra proibida na tela (link/QR/bio/Direct/URL): '
                      f'bloco omitido — ponha essa frase numa cena G')
                continue
            x, y = g['leg_D'] if modo == 'D' else g['leg_T']
            px, larg = _leg_px(b['txt'], g['leg_px'], g['w'] - 200)
            if modo == 'T':
                qx = _rosto_T(s, e, escalas)[0]
                y = max(y, qx + 0.85 * px)
                if y + 0.55 * px > LIM_T[FORMATO]:
                    # 12/11 (caso real): forçada no limite, a legenda cai em cima do queixo — não entregar assim
                    print(f'  AVISO legenda "{b["txt"]}" ({s:.2f}s): queixo em {qx:.0f}, não cabe abaixo dele antes do limite '
                          f'{LIM_T[FORMATO]} — a legenda vai tampar o queixo: use modos={{\'{FORMATO}\': \'G\'}} nessa cena')
                    y = LIM_T[FORMATO] - 0.55 * px
            x = min(max(x, 100 + larg / 2), g['w'] - 100 - larg / 2)   # nunca a menos de 100 px das laterais
            s0 = math.floor(round(s * FPS)) / FPS
            out.append(f'<div class="leg clip" data-start="{s0:.4f}" data-duration="{q(e - s0) - 0.01:.4f}" data-track-index="4" '
                       f'style="left:{x:.0f}px;top:{y:.0f}px;font-size:{px}px">{esc(b["txt"])}</div>')
    return '\n      '.join(out)


# ================================================================ CSS / JS
CSS = r"""
@font-face{font-family:'Garamond';src:url('fonts/EBGaramond-400.woff2') format('woff2');font-weight:400;font-display:block}
@font-face{font-family:'Inter';src:url('fonts/inter-latin-500-normal.woff2') format('woff2');font-weight:500;font-display:block}
@font-face{font-family:'Inter';src:url('fonts/inter-latin-600-normal.woff2') format('woff2');font-weight:600;font-display:block}
@font-face{font-family:'Inter';src:url('fonts/inter-latin-700-normal.woff2') format('woff2');font-weight:700;font-display:block}
@font-face{font-family:'TikTok Sans';src:url('fonts/TikTokSans-Variable.ttf') format('truetype');font-weight:300 900;font-display:block}
*{box-sizing:border-box}
html,body{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#050300}
#root{position:relative;width:100%;height:100%;overflow:hidden;background:#050300;font-family:'Inter',sans-serif}
#mundo{position:absolute;left:0;top:0;width:100%;height:100%;overflow:hidden}
.slot{position:absolute;overflow:hidden;background:#050300}
.slot video{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover}
#palco{position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none}
.cena{position:absolute;overflow:hidden}
.cena .fundo{position:absolute;inset:0;background:radial-gradient(ellipse 75% 65% at 50% 46%,#281B09 0%,#1A1206 55%,#0A0601 100%)}
.cena.G .fundo{background:radial-gradient(ellipse 70% 60% at 50% 42%,#171004 0%,#0D0900 50%,#050300 100%)}
.cena .ret{position:absolute;inset:0;background-image:radial-gradient(circle,rgba(234,124,46,.13) 0 0.9px,transparent 1.4px);background-size:6px 6px;
  -webkit-mask-image:radial-gradient(ellipse 60% 55% at 50% 45%,#000 0%,rgba(0,0,0,.35) 60%,transparent 100%);mask-image:radial-gradient(ellipse 60% 55% at 50% 45%,#000 0%,rgba(0,0,0,.35) 60%,transparent 100%)}
.cena .vin{position:absolute;inset:0;background:radial-gradient(ellipse 80% 75% at 50% 48%,transparent 55%,rgba(0,0,0,.55) 100%)}
.cena .grao{position:absolute;inset:0;opacity:.07;background-image:__GRAO__}
.pz{position:absolute;border-radius:50%;background:#F08A3A;box-shadow:0 0 6px 1px rgba(240,138,58,.55)}
.caixa{position:absolute;left:0;top:0;width:880px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;transform-origin:0 0}
.cab{display:flex;flex-direction:column;align-items:center;gap:16px}
.D .cab{order:9}
.D .cab.so{order:0}
.chapeu{font:600 30px 'Inter';letter-spacing:.32em;color:#CF7A36;text-align:center;margin-right:-.32em;white-space:nowrap}
.titulo{font-family:'Garamond',serif;font-weight:400;color:#F4EBD2;line-height:1.06;text-align:center;letter-spacing:-.005em;white-space:nowrap;
  text-shadow:-1.5px 0 rgba(70,150,255,.28),1.5px 0 rgba(255,190,70,.30),0 0 22px rgba(202,102,31,.22)}
.titulo .k{color:#D9712A;text-shadow:-1.5px 0 rgba(60,200,140,.22),1.5px 0 rgba(255,60,40,.25),0 0 26px rgba(234,124,46,.35)}
.titulo .kn{color:#E04547;text-shadow:-1.5px 0 rgba(60,160,255,.22),1.5px 0 rgba(255,160,60,.22),0 0 26px rgba(212,56,58,.35)}
.cd{position:relative;background:linear-gradient(180deg,#34240F,#241809);border:1.5px solid rgba(234,124,46,.16);border-radius:30px;
  box-shadow:0 34px 80px -24px rgba(0,0,0,.85),inset 0 1px 0 rgba(255,220,170,.07)}
.ph{display:block;flex:none}
.av{width:68px;height:68px;border-radius:50%;flex:none;background:radial-gradient(circle at 35% 30%,#8A5526,#4C2D12);display:flex;align-items:center;justify-content:center;color:#FFD2A6;font:700 25px 'Inter';box-shadow:0 0 0 3px rgba(234,124,46,.25)}
.av.p{width:54px;height:54px;font-size:21px}
.nm{font:600 32px/1.2 'Inter';color:#EFE8D0;white-space:nowrap}
.sb{font:500 25px/1.25 'Inter';color:#A68C68;white-space:nowrap;margin-top:3px}
.nt{flex:1;min-width:0}
.ico{color:#E07A2E;margin-left:auto}
.pill{font:700 22px 'Inter';letter-spacing:.12em;padding:9px 16px;border-radius:12px;border:1.5px solid #B8692A;color:#F0A060;background:rgba(202,102,31,.12);white-space:nowrap}
.pill.neg{border-color:#D4383A;color:#FF7B7B;background:rgba(212,56,58,.14)}
.pill.big{display:flex;align-items:center;gap:12px;font-size:26px;padding:14px 24px;border-radius:16px}
.pill.cheio{background:#CA661F;border-color:#EA7C2E;color:#FFF6EA}
.notif{display:flex;align-items:center;gap:22px;padding:26px 30px;margin-bottom:14px}
.notif .hr{font:500 24px 'Inter';color:#A68C68;margin-left:auto}
.notif .pill{position:absolute;right:26px;bottom:-24px}
.chat{padding:22px 26px 28px}
.chat .hd{display:flex;align-items:center;gap:20px;padding:4px 4px 18px;border-bottom:1.5px solid rgba(234,124,46,.12);margin-bottom:20px}
.msgs{display:flex;flex-direction:column;gap:16px}
.msg{position:relative;max-width:82%;padding:18px 24px 16px;border-radius:26px;border-bottom-left-radius:8px;background:#3E2B16;font:500 31px/1.3 'Inter';color:#EDE6CE;align-self:flex-start}
.msg.out{align-self:flex-end;border-bottom-left-radius:26px;border-bottom-right-radius:8px;background:#54391C}
.msg.ia{align-self:flex-end;border-bottom-left-radius:26px;border-bottom-right-radius:8px;background:linear-gradient(180deg,#DC7630,#B85A16);color:#FFF7EC}
.msg .hr{display:block;text-align:right;font:500 22px 'Inter';color:#B49A76;margin-top:6px}
.msg.ia .hr{color:#FFE0C2}
.msg .robo{display:flex;align-items:center;gap:8px;font:700 21px 'Inter';letter-spacing:.08em;color:#FFE3C8;margin-bottom:6px;text-transform:uppercase}
.msg .tagm{position:absolute;right:-18px;top:-22px}
.digit{display:flex;gap:10px;padding:22px 26px;border-radius:26px;background:#3E2B16;align-self:flex-end;width:fit-content}
.digit.in{align-self:flex-start}
.digit i{display:block;width:13px;height:13px;border-radius:50%;background:#C08A5A}
.jan{padding:0 0 18px;overflow:hidden}
.jan .bar{display:flex;align-items:center;gap:10px;padding:18px 24px;border-bottom:1.5px solid rgba(234,124,46,.10);background:rgba(0,0,0,.12)}
.jan .bar i{display:block;width:14px;height:14px;border-radius:50%;background:#5E4428}
.jan .bar span{margin-left:12px;font:500 24px 'Inter';color:#A68C68}
.jan .cols{display:flex;justify-content:space-between;padding:16px 30px 8px;font:600 21px 'Inter';letter-spacing:.2em;color:#8C7250}
.row{display:flex;align-items:center;gap:18px;margin:8px 16px;padding:14px 18px;border-radius:18px;background:#22170A;border:2px solid transparent}
.row .nm{flex:1;font-size:30px}
.row .vl{font:600 28px 'Inter';color:#D9C9A6;margin-right:8px}
.tag{font:700 21px 'Inter';letter-spacing:.12em;padding:8px 14px;border-radius:10px;border:1.5px solid #B8692A;color:#F0A060;white-space:nowrap}
.tag.cinza{border-color:#5E4A32;color:#A08868}
.tag.neg{border-color:#D4383A;color:#FF7B7B}
.tag.cheio{background:#CA661F;border-color:#EA7C2E;color:#FFF6EA}
.kb{display:flex;gap:18px;padding:18px;background:none;border:none;box-shadow:none}
.kb .col{position:relative;min-height:300px;padding:18px 16px;border-radius:22px;background:rgba(36,24,10,.92);border:1.5px solid rgba(234,124,46,.12)}
.kb .chd{font:700 21px 'Inter';letter-spacing:.16em;color:#B08455;margin-bottom:16px;white-space:nowrap}
.kb .fant{height:64px;border-radius:14px;background:rgba(255,255,255,.025);border:1.5px dashed rgba(234,124,46,.10);margin-bottom:12px}
.kc{position:absolute;top:76px;display:flex;align-items:center;gap:12px;padding:14px 14px;border-radius:16px;background:linear-gradient(180deg,#4A3118,#36230F);border:2px solid rgba(234,124,46,.35);box-shadow:0 16px 30px rgba(0,0,0,.5)}
.kc .nm{font-size:25px}.kc .sb{font-size:21px}
.kc .av.p{width:44px;height:44px}
.ck{display:flex;flex-direction:column;gap:18px}
.ck .it{display:flex;align-items:center;gap:26px;padding:18px 24px;border-radius:26px;background:linear-gradient(180deg,#2F200E,#22170A);border:2px solid rgba(234,124,46,.12)}
.nsq{width:84px;height:84px;border-radius:24px;flex:none;background:linear-gradient(180deg,#EA7C2E,#DE6F22 50%,#C45F18);box-shadow:0 0 0 7px #332110,0 14px 30px rgba(0,0,0,.45);
  font:400 56px/1 'Garamond';color:#FFF4E2;display:flex;align-items:center;justify-content:center;padding-bottom:6px}
.nsq.ico{color:#fff;padding:0}
.ck .tx{flex:1;font:600 36px/1.2 'Inter';color:#EFE8D0;white-space:nowrap}
.ck .tx .k{color:#F0913F}
.ok{width:58px;height:58px;border-radius:50%;flex:none;background:#CA661F;color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 0 18px rgba(234,124,46,.45)}
.nb{display:flex;flex-direction:column;align-items:center;gap:8px}
.nb .rt{font:600 30px 'Inter';letter-spacing:.3em;color:#CF7A36;margin-right:-.3em}
.nb .v{font-family:'Garamond',serif;line-height:.95;color:#F4EBD2;white-space:nowrap;text-shadow:-2px 0 rgba(70,150,255,.25),2px 0 rgba(255,190,70,.28),0 0 40px rgba(202,102,31,.3)}
.nb .v .u,.nb .v .pre{color:#D9712A}
.nb.neg .v .u{color:#E04547}
.pb{width:700px;height:24px;border-radius:12px;background:#22170A;border:1.5px solid rgba(234,124,46,.18);overflow:hidden;margin-top:18px}
.pb i{display:block;height:100%;border-radius:12px;background:linear-gradient(90deg,#B85A16,#EA7C2E);transform-origin:0 50%}
.al{display:flex;align-items:center;gap:26px;padding:26px 30px;border-color:rgba(212,56,58,.45);background:linear-gradient(180deg,#3A1A10,#26120A)}
.xr{width:64px;height:64px;border-radius:50%;flex:none;background:#D4383A;color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 0 22px rgba(231,71,74,.45)}
.al .nm{white-space:normal}
.al .nm .k{color:#F0913F}.al .nm .kn{color:#FF6B6B}
.fx{position:relative;display:flex;align-items:flex-start;justify-content:center}
.fx .no{display:flex;flex-direction:column;align-items:center;gap:18px;flex:none}
.sq{width:124px;height:124px;border-radius:36px;flex:none;background:linear-gradient(180deg,#EA7C2E,#DE6F22 50%,#C45F18);box-shadow:0 0 0 9px #332110,0 20px 40px rgba(0,0,0,.55);color:#fff;display:flex;align-items:center;justify-content:center}
.sq.neg{background:linear-gradient(180deg,#E7474A,#B42A2D)}
.sq.esc{background:linear-gradient(180deg,#4A3118,#2E1E0C);color:#E9B486}
.fx .lb{font:600 30px/1.2 'Inter';color:#D9CBA8;text-align:center;white-space:nowrap}
.fx .lk{height:5px;margin-top:60px;border-radius:3px;background:linear-gradient(90deg,#B85A16,#EA7C2E);transform-origin:0 50%;flex:none;box-shadow:0 0 10px rgba(234,124,46,.4)}
.fchip{position:absolute;top:44px;transform:translateX(-50%);margin-left:0;font:700 22px 'Inter';letter-spacing:.14em;padding:9px 16px;border-radius:12px;background:#7A4418;color:#FFF3E4;white-space:nowrap;box-shadow:0 8px 20px rgba(0,0,0,.5)}
.ctaw{position:relative;display:flex;flex-direction:column;align-items:center;gap:18px}
.ctaw .b{position:relative;overflow:hidden;border-radius:9999px;background:#2F200E;border:2px solid rgba(234,124,46,.5);box-shadow:0 26px 60px -20px rgba(0,0,0,.8)}
.ctaw .bg{position:absolute;inset:0;background:linear-gradient(180deg,#EA7C2E,#C45F18);opacity:0}
.ctaw .bt{position:relative;display:flex;align-items:center;gap:18px;padding:30px 64px;font:700 46px 'Inter';color:#FFF4E4;white-space:nowrap}
.ctas{font:500 27px 'Inter';color:#A68C68}
.cur{position:absolute;right:-6px;top:58px;filter:drop-shadow(0 6px 8px rgba(0,0,0,.6))}
.sem{display:flex;gap:14px}
.dia{position:relative;width:104px;height:128px;border-radius:22px;background:linear-gradient(180deg,#2F200E,#22170A);border:1.5px solid rgba(234,124,46,.16);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;color:#C9935E}
.dia .d{font:700 22px 'Inter';letter-spacing:.1em;color:#B08455}
.dia .xr{position:absolute;right:-12px;top:-12px;width:42px;height:42px}
.ls{display:flex;flex-direction:column;gap:18px}
.lrow{display:flex;align-items:center;gap:22px;padding:22px 26px;border-radius:26px}
.rn{display:flex;align-items:center;gap:28px;padding:26px 30px}
.folha{width:124px;height:136px;border-radius:22px;flex:none;overflow:hidden;background:#FDFEEE;box-shadow:0 12px 26px rgba(0,0,0,.45);display:flex;flex-direction:column;align-items:center}
.folha .fd{width:100%;text-align:center;padding:8px 0 6px;background:#CA661F;color:#FFF6EA;font:700 21px 'Inter';letter-spacing:.14em}
.folha .fn{font:400 70px/1.1 'Garamond';color:#2A1A0A}
.gr{padding:34px 34px 26px}
.gb{position:relative;display:flex;align-items:flex-end;gap:22px}
.bw{flex:1;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:10px}
.bw span{font:600 21px 'Inter';color:#8C7250;letter-spacing:.1em}
.gr .b{width:100%;border-radius:14px 14px 6px 6px;background:linear-gradient(180deg,#5A3C1E,#3E2912);transform-origin:50% 100%}
.gr .b.on{background:linear-gradient(180deg,#EA7C2E,#B85A16);box-shadow:0 0 22px rgba(234,124,46,.35)}
.tend{position:absolute;left:0;top:0;overflow:visible}
.tend polyline{fill:none;stroke:#F4EBD2;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1 2}
.eqw{display:flex;flex-direction:column;align-items:center;gap:22px}
.eq{display:flex;gap:16px}
.ep{position:relative;width:100px;height:100px;border-radius:30px;background:linear-gradient(180deg,#EA7C2E,#C45F18);box-shadow:0 0 0 8px #332110;color:#fff;display:flex;align-items:center;justify-content:center}
.ep.fan{background:transparent;box-shadow:none;border:3px dashed rgba(234,124,46,.45);color:#9A7450}
.ep .xr{position:absolute;right:-14px;top:-14px;width:44px;height:44px}
.eqr{font:600 30px 'Inter';letter-spacing:.24em;color:#CF7A36;margin-right:-.24em}
.et{display:flex;align-items:flex-start;justify-content:center}
.ep2{display:flex;flex-direction:column;align-items:center;gap:16px;width:190px;flex:none}
.ep2 .bol{width:96px;height:96px;border-radius:50%;border:3px solid rgba(234,124,46,.4);background:#22170A;color:#C9935E;font:400 54px/1 'Garamond';display:flex;align-items:center;justify-content:center;padding-bottom:6px}
.ep2 .lb{font:600 28px 'Inter';color:#D9CBA8;white-space:nowrap}
.elk{flex:1;height:5px;margin-top:46px;border-radius:3px;background:rgba(234,124,46,.15);overflow:hidden}
.elk i{display:block;height:100%;background:#EA7C2E;transform-origin:0 50%}
.lic{display:flex;align-items:center;justify-content:center}
.cam{position:absolute;inset:0;transform-origin:50% 45%}
.passo{display:flex;align-items:center;gap:34px;padding-left:8px}
.nsq.g{width:118px;height:118px;border-radius:34px;font-size:78px;box-shadow:0 0 0 9px #332110,0 20px 40px rgba(0,0,0,.55)}
.passo .pt{font-family:'Garamond',serif;font-size:70px;line-height:1.02;color:#F4EBD2;white-space:nowrap;
  text-shadow:-1.5px 0 rgba(70,150,255,.25),1.5px 0 rgba(255,190,70,.28),0 0 22px rgba(202,102,31,.2)}
.passo .pt .k{color:#D9712A}.passo .pt .kn{color:#E04547}
.kcard{padding:26px 30px 22px}
.kh{font:600 24px 'Inter';letter-spacing:.3em;color:#CF7A36;text-align:center;margin:0 -.3em 18px 0}
.kr{display:flex;align-items:center;gap:24px;padding:16px 8px;border-top:1.5px solid rgba(234,124,46,.08)}
.kr:first-of-type{border-top:none}
.cx{position:relative;width:52px;height:52px;border-radius:14px;flex:none;border:2.5px solid rgba(234,124,46,.45);background:#1C1308}
.cx span{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff;opacity:0}
.cx.on{background:linear-gradient(180deg,#EA7C2E,#C45F18);border-color:#EA7C2E;box-shadow:0 0 16px rgba(234,124,46,.45)}
.cx.neg{background:#D4383A;border-color:#E7474A}
.kr .tx{font:600 34px/1.2 'Inter';color:#CDBF9F;white-space:nowrap}
.kr .tx .k{color:#F0913F}.kr .tx .kn{color:#FF6B6B}
.perg{padding:28px 30px 24px}
.perg .pq{font:600 36px/1.25 'Inter';color:#F1EAD2;margin:0 4px 20px;white-space:nowrap}
.op{display:flex;align-items:center;gap:20px;margin-top:12px;padding:18px 22px;border-radius:18px;background:#22170A;border:2px solid rgba(234,124,46,.10);
  font:500 31px 'Inter';color:#D9CBA8;white-space:nowrap}
.rd{display:block;width:34px;height:34px;border-radius:50%;flex:none;border:2.5px solid rgba(234,124,46,.5)}
.rd.on{background:radial-gradient(circle,#EA7C2E 0 42%,transparent 46%);border-color:#EA7C2E}
.hub{position:relative}
.hl{position:absolute;left:0;top:0;overflow:visible}
.hl line{stroke:#D06A22;stroke-width:4;stroke-linecap:round;stroke-dasharray:1 2;opacity:.85}
.hs{position:absolute;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;gap:12px}
.hs .lb{font:600 25px 'Inter';color:#D9CBA8;white-space:nowrap;position:absolute;top:100%;margin-top:10px}
.hc .lb{font:700 24px 'Inter';letter-spacing:.2em;color:#CF7A36;margin-right:-.2em}
.sq.p{width:96px;height:96px;border-radius:28px;box-shadow:0 0 0 7px #332110,0 14px 30px rgba(0,0,0,.5)}
.sq.g{width:170px;height:170px;border-radius:48px;box-shadow:0 0 0 12px #332110,0 26px 50px rgba(0,0,0,.6),0 0 60px rgba(234,124,46,.18)}
.igw{display:flex;flex-direction:column;align-items:center;gap:26px}
.igw .lb{font:600 28px 'Inter';letter-spacing:.3em;color:#CF7A36;margin-right:-.3em}
.pfw{display:flex;flex-direction:column;align-items:center;gap:22px}
.pill.rede{font-size:22px;letter-spacing:.3em;border-radius:9999px;padding:8px 22px}
.pf{padding:28px 30px}
.pfh{display:flex;align-items:center;gap:24px}
.foto{width:112px;height:112px;border-radius:50%;flex:none;background-size:cover;background-position:center;box-shadow:0 0 0 4px #CA661F,0 0 0 9px #2A1C0C}
.pf .nm{display:flex;align-items:center;gap:8px;font-size:36px}
.pf .selo{display:block}
.pb2{position:relative;margin-top:24px;height:84px;border-radius:18px;background:#2C1E0D;border:2px solid rgba(234,124,46,.25);display:flex;align-items:center;justify-content:center;
  font:700 34px 'Inter';color:#F2E8D0}
.pb2 .bg{position:absolute;inset:0;border-radius:16px;background:linear-gradient(180deg,#EA7C2E,#C45F18);opacity:0}
.pb2 .a,.pb2 .b{position:relative}
.pb2 .b{display:none}
.pb2 .cur{position:absolute;right:auto;left:58%;top:34px}
.risc{position:relative;font-family:'Garamond',serif;font-weight:400;color:#F4EBD2;line-height:1.06;white-space:nowrap;text-align:center;
  text-shadow:-1.5px 0 rgba(70,150,255,.28),1.5px 0 rgba(255,190,70,.30),0 0 22px rgba(202,102,31,.22)}
.risc .rw{display:inline-block}
.risc .rl{position:absolute;left:-.07em;right:-.07em;top:.64em;height:.075em;border-radius:.04em;background:linear-gradient(90deg,#D9712A,#F08A3A);
  box-shadow:0 0 14px rgba(234,124,46,.6),0 2px 6px rgba(0,0,0,.45);transform:scaleX(0);transform-origin:0 50%}
.celg{position:relative;flex:none}
.celw{position:absolute;transform-origin:50% 60%}
.cel{position:absolute;inset:0;border-radius:1.7em;padding:.3em;background:linear-gradient(160deg,#4A3520,#1B1209 40%,#2A1D0E);
  box-shadow:0 1.8em 3.2em -1em rgba(0,0,0,.9),0 0 0 .07em rgba(234,124,46,.30),inset 0 0 0 .06em rgba(255,220,170,.10)}
.cel .tela{position:relative;width:100%;height:100%;border-radius:1.42em;overflow:hidden;background:linear-gradient(180deg,#171007,#0F0A04)}
.cel .ilha{position:absolute;z-index:3;top:.72em;left:50%;width:2.6em;height:.72em;margin-left:-1.3em;border-radius:1em;background:#000}
.cel .chd{display:flex;align-items:center;gap:.45em;padding:1.8em .65em .6em;background:#24180A;border-bottom:.07em solid rgba(234,124,46,.14);color:#C9935E}
.cel .chd>svg{width:1.05em;height:1.05em}
.cel .cav{width:2em;height:2em;border-radius:50%;flex:none;background:linear-gradient(160deg,#8A5526,#4C2D12);display:flex;align-items:center;justify-content:center;color:#FFD2A6}
.cel .cav svg{width:1.15em;height:1.15em}
.cel .cnt{flex:1;min-width:0}
.cel .cnm{font:600 .95em/1.15 'Inter';color:#EFE8D0;white-space:nowrap;overflow:hidden}
.cel .csb{font:500 .7em/1.25 'Inter';color:#A68C68;white-space:nowrap}
.cel .cms{display:flex;flex-direction:column;align-items:flex-start;gap:.55em;padding:.85em .5em}
.cel .cdia{align-self:center;font:600 .6em 'Inter';letter-spacing:.14em;margin-right:-.14em;color:#8C7250;padding:.35em .8em;border-radius:.8em;background:rgba(255,255,255,.045)}
.cel .cb{max-width:94%;padding:.42em .55em .36em;border-radius:.7em;border-bottom-left-radius:.2em;background:#3E2B16;color:#F1EAD2;
  font-family:'Inter';font-weight:600;line-height:1.2;box-shadow:0 .3em .8em rgba(0,0,0,.35)}
.cel .chr{display:block;text-align:right;font:500 .5em 'Inter';color:#B49A76;margin-top:.25em}
.cel .cin{position:absolute;left:.5em;right:.5em;bottom:.8em;display:flex;align-items:center;gap:.4em}
.cel .cf{flex:1;height:2.1em;border-radius:1.05em;background:#24180A;border:.06em solid rgba(234,124,46,.14);display:flex;align-items:center;padding-left:.8em;overflow:hidden}
.cel .cf span{font:500 .78em 'Inter';color:#7E6A4E;white-space:nowrap}
.cel .cm{width:2.1em;height:2.1em;border-radius:50%;flex:none;background:linear-gradient(180deg,#EA7C2E,#C45F18);color:#fff;display:flex;align-items:center;justify-content:center}
.cel .cm svg{width:1.05em;height:1.05em}
.leg{position:absolute;transform:translate(-50%,-50%);white-space:nowrap;font-family:'TikTok Sans',sans-serif;font-weight:650;color:#fff;line-height:1.1;
  text-shadow:0 2px 6px rgba(0,0,0,.55),0 0 2px rgba(0,0,0,.35);z-index:20}
#flash{position:absolute;inset:0;background:#FFF1DC;opacity:0;z-index:30;pointer-events:none}
#preto{position:absolute;inset:0;background:#000;opacity:0;z-index:31;pointer-events:none}
"""

_GRAO = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='f'%3E"
         "%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23f)'/%3E%3C/svg%3E\")")

JS = r"""
const tl = gsap.timeline({ paused: true });
function entra(s,t,d,y){tl.fromTo(s,{opacity:0,y:(y==null?18:y),filter:'blur(10px)'},{opacity:1,y:0,filter:'blur(0px)',duration:d||0.2,ease:'power3.out'},t);}
function pop(s,t){tl.fromTo(s,{opacity:0,scale:0.4},{opacity:1,scale:1,duration:0.2,ease:'back.out(1.5)',transformOrigin:'50% 50%'},t);}
function apaga(s,t){tl.to(s,{opacity:0.4,duration:0.16,ease:'power2.out'},t);}
function destaca(s,t,cor){tl.to(s,{borderColor:cor||'#CA661F',boxShadow:'0 0 0 1px '+(cor||'#CA661F')+', 0 0 26px rgba(234,124,46,.25)',duration:0.1,ease:'power2.out'},t);}
function estica(s,t,d){tl.fromTo(s,{scaleX:0},{scaleX:1,duration:d||0.3,ease:'power3.out',transformOrigin:'0% 50%'},t);}
function sobe(s,t,d,st){tl.fromTo(s,{scaleY:0},{scaleY:1,duration:d||0.4,ease:'power3.out',stagger:st||0,transformOrigin:'50% 100%'},t);}
function desenha(s,t,d){tl.fromTo(s,{strokeDashoffset:1.02},{strokeDashoffset:0,duration:d||0.4,ease:'power2.inOut'},t);}
function conta(s,a,b,t,d){const el=document.querySelector(s);const o={v:a};tl.fromTo(o,{v:a},{v:b,duration:d,ease:'expo.out',onUpdate:function(){el.textContent=Math.round(o.v);}},t);}
"""


def _poeira(c, t1, w, h, n=24):
    """Poeira laranja flutuando devagar (posição determinística por cena)."""
    rng = random.Random(sum(ord(ch) * (k + 1) for k, ch in enumerate(c.id)) % 9973)   # 08/11: hash() mudava a cada formato
    ps = []
    for k in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.choice([1.6, 2, 2.4, 3, 3.6])
        op = rng.uniform(0.25, 0.75)
        v = rng.uniform(8, 22)
        pid = f'{c.id}-pz{k}'
        ps.append(f'<i class="pz" id="{pid}" style="left:{x:.0f}px;top:{y:.0f}px;width:{r}px;height:{r}px;opacity:{op:.2f}"></i>')
        c.js.append(f"tl.fromTo('#{pid}',{{y:0,x:0}},{{y:{-v * (t1 - c.t0):.1f},x:{rng.uniform(-10, 10):.1f},duration:{q(t1 - c.t0)},ease:'none',immediateRender:false}},{c.t0});")
    return ''.join(ps)


def _transicoes(bordas, dur):
    """Transição em cada troca de cena: entrar no gráfico cheio = flash duplo; entrar/sair da pessoa cheio = blur de
    foco; o resto = whip horizontal (os dois painéis juntos). Tique em toda troca (analise.md §7 e §10)."""
    js = []
    for t, de, pra in bordas:
        if pra == 'G' and de != 'G':
            tipo = 'flash'
        elif 'T' in (de, pra):
            tipo = 'foco'
        else:
            tipo = 'whip'
        TRANS.append((t, {'flash': 'whoosh', 'foco': 'foco', 'whip': 'swish'}[tipo], f'transição {tipo} {de}→{pra}'))
        if tipo == 'flash':
            # 7 quadros: 2 de clarão no plano que sai, 1 de volta, 2 no que entra, 2 resolvendo (07/11: começa 2 quadros
            # antes do corte, não 3 — o quadro de revisão, tirado 0,08 s antes do fim da cena, sai nítido)
            for k, (op, bl) in enumerate([(0.42, 6), (0.55, 10), (0.18, 8), (0.5, 10), (0.55, 8), (0.25, 5), (0, 0)]):
                tk = q(t + (k - 2) * F)
                js.append(f"tl.set('#flash',{{opacity:{op}}},{tk});tl.set('#mundo',{{filter:'{f'blur({bl}px)' if bl else 'none'}'}},{tk});")
        elif tipo == 'foco':
            for k, bl in enumerate([6, 12, 12, 8, 4, 0]):
                tk = q(t + (k - 2) * F)
                js.append(f"tl.set('#mundo',{{filter:'{f'blur({bl}px)' if bl else 'none'}'}},{tk});")
        else:
            for k, (sd, dx) in enumerate([(24, -18), (60, -40), (60, 40), (30, 18), (10, 6), (0, 0)]):
                tk = q(t + (k - 2) * F)
                js.append(f"tl.set('#fwb',{{attr:{{stdDeviation:'{sd} 0'}}}},{tk});"
                          f"tl.set('#mundo',{{filter:'{'url(#fw)' if sd else 'none'}',x:{dx}}},{tk});")
    js.append(f"tl.fromTo('#preto',{{opacity:0}},{{opacity:1,duration:0.5,ease:'power1.in',immediateRender:false}},{q(dur - 0.5)});")
    return js


_RE_EV = [(re.compile(r"\b(entra|pop|apaga|destaca|estica|sobe|desenha)\('([^']*)',([\d.]+)"), 1, 2, 3),
          (re.compile(r"\b(conta)\('([^']*)',[-\d.]+,[-\d.]+,([\d.]+)"), 1, 2, 3),
          (re.compile(r"\btl\.(set|to|fromTo)\('([^']*)',\{[^;]*?\},([\d.]+)\)"), 1, 2, 3)]
_RE_CONTA = re.compile(r"\bconta\('[^']*',[-\d.]+,[-\d.]+,([\d.]+),([\d.]+)\)")


def _eventos_visiveis(fins):
    """Eventos visuais reais do FORMATO, tirados do JS (GSAP) das cenas que aparecem nele (D/G; no T as peças não
    aparecem): [(t, descrição)] + intervalos de número girando [(t0, t1, descrição)]. Só vale o que cai dentro da cena."""
    ev, giro = [], []
    for c, t1 in zip(CENAS, fins):
        if c.modo == 'T':
            continue
        for linha in c.js:
            for rx, gf, gs, gt in _RE_EV:
                for m in rx.finditer(linha):
                    t = float(m.group(gt))
                    if c.t0 - 0.05 <= t < t1 - 0.05:
                        ev.append((t, f'{c.id} {m.group(gf)} {m.group(gs)}'))
            for m in _RE_CONTA.finditer(linha):
                t, d = float(m.group(1)), float(m.group(2))
                giro.append((t, min(t + d, t1), f'{c.id} número girando'))
    return sorted(ev), giro


def _kit_earshot():
    """Kit do Earshot (MIT) já renderizado em hyperframes/extremo_sfx/earshot/ (16 bits, 48 kHz) — vem pronto no projeto.
    Só se faltar algum som e o Earshot estiver instalado (ferramentas/earshot-venv, opcional) ele é renderizado de novo."""
    d = _SFX_DIR / 'earshot'
    d.mkdir(parents=True, exist_ok=True)
    py = next((x for x in (RAIZ / 'ferramentas/earshot-venv/bin/python', RAIZ / 'ferramentas/earshot-venv/Scripts/python.exe')
               if x.exists()), None)
    env = dict(__import__('os').environ, PYTHONUTF8='1')
    for nome, (sid, extra) in KIT_EARSHOT.items():
        alvo = d / f'{nome}.wav'
        if alvo.exists():
            continue
        if py is None:
            print(f'AVISO: som {nome}.wav faltando em {d} e o Earshot não está instalado — esse som fica de fora')
            continue
        tmp = d / f'_24bit-{nome}.wav'
        subprocess.run([str(py), '-m', 'earshot', 'sfx', 'render', sid, '-o', str(tmp), *extra], check=True, env=env,
                       capture_output=True)
        subprocess.run([FF, '-v', 'error', '-y', '-i', str(tmp), '-c:a', 'pcm_s16le', '-ar', '48000', str(alvo)], check=True)
        tmp.unlink()
    return d


def _audios(com_musica, fins):
    """SFX em <audio> nas trilhas 11–16 sem sobreposição. REGRA 08/11/2026 (usuário, caso real: "tem efeito solto, em
    que não acontece nada na cena"): cada som pedido só toca se NESTE formato um elemento visível entra/marca/muda a
    ±2 quadros dele (timeline GSAP real das cenas D/G — peça de cena que vira T no formato sai) ou se um número está
    girando; o som é encaixado no quadro exato do evento. Transições (swish/foco/hit) sempre têm a troca na tela.
    Mínimo de 0,28 s entre sons de peça (prioridade chime > check > tique > blip); os de transição ficam por baixo.
    Nunca nos 0,2 s finais. Grava mapa-sons-<FMT>.txt (tempo, som, evento visual) e os descartados. Música na trilha 17."""
    pub = AQUI / 'public/sfx'
    pub.mkdir(parents=True, exist_ok=True)
    kit = _kit_earshot()
    ev, giro = _eventos_visiveis(fins)
    tev = np.array([e[0] for e in ev]) if ev else np.array([99999.0])
    tol = 2 * F + 1e-6
    pedidos, fora = [], []
    for t, nome, vol, gap in SFX:
        k = int(np.abs(tev - t).argmin())
        if abs(tev[k] - t) <= tol:
            pedidos.append((float(tev[k]), nome, vol, ev[k][1], gap))
            continue
        g_ = next((g for g in giro if g[0] - tol <= t <= g[1]), None)
        if g_ and nome in ('tique', 'blip'):
            pedidos.append((t, nome, vol, g_[2], gap))
            continue
        fora.append((t, nome, 'nenhum elemento visível entra/muda nesse instante neste formato'))
    PRI = {'chime': 0, 'check': 1, 'tique': 2, 'blip': 3}
    aceitos = []
    for t, nome, vol, desc, gap in sorted(pedidos, key=lambda x: (PRI.get(x[1], 9), x[0])):
        if t < 0 or t >= DUR - 0.2:
            fora.append((t, nome, 'fim do vídeo'))
            continue
        perto = next((a for a in aceitos if abs(a[0] - t) < max(gap, a[4])), None)
        if perto:
            fora.append((t, nome, f'outro som de peça a menos de {max(gap, perto[4]):.2f} s'.replace('.', ',')))
            continue
        aceitos.append((t, nome, vol, desc, gap))
    for t, nome, desc in TRANS:
        if 0 < t < DUR - 0.2:
            aceitos.append((t, nome, VOL[nome], desc, 0))
    fim_trilha = {k: -1.0 for k in range(11, 17)}
    tags, mapa = [], []
    for t, nome, vol, desc, _gap in sorted(aceitos):
        arq, pico = KIT[nome]
        src = kit / f'{arq}.wav'
        shutil.copy(src, pub / src.name)
        t0 = round(max(0.0, t - pico), 3)
        with wave.open(str(src)) as w_:
            d = w_.getnframes() / w_.getframerate()
        d = round(min(d, DUR - t0 - 0.05), 3)
        trilha = next((k for k, f in fim_trilha.items() if f <= t0), None)
        if trilha is None:
            fora.append((t, nome, 'sem trilha livre'))
            continue
        fim_trilha[trilha] = t0 + d + 0.01
        tags.append(f'<audio id="sfx{len(tags)}" src="sfx/{src.name}" data-start="{t0}" data-duration="{d}" '
                    f'data-track-index="{trilha}" data-volume="{vol}"></audio>')
        mapa.append(f'{t:7.3f}s  {nome:7s} ({arq}.wav, vol {vol})  <- {desc}')
    (AQUI / f'mapa-sons-{FORMATO}.txt').write_text(
        f'Mapa de sons {NOME} [{FORMATO}] — {len(mapa)} sons (tempo do evento visual, som, elemento)\n'
        + '\n'.join(mapa) + f'\n\nDescartados ({len(fora)}):\n'
        + '\n'.join(f'{t:7.3f}s  {n:7s} {m}' for t, n, m in sorted(fora)) + '\n', encoding='utf-8')
    if com_musica:
        tags.append(f'<audio id="musica" src="musica.m4a" data-start="0" data-duration="{DUR}" data-track-index="17" '
                    f'data-volume="{MUSICA_VOL}"></audio>')
    return '\n      '.join(tags), len(tags)


MUSICA_VOL = 0.07   # ~25 dB abaixo da voz, como a referência
MUSICA_ON = False   # regra do projeto: nunca música por cima da voz sem pedido (ligar com X.MUSICA_ON = True)


def _caixa(c, modo, g):
    """Posição/escala da caixa virtual dentro da seção."""
    rx, ry, rw, rh = g['cx_' + modo]
    px, py = (g['painel'][0], g['painel'][1]) if modo == 'D' else (0, 0)
    esc_ = min(rw / CX_W, rh / 660 if modo == 'D' else rh / 760, g['cap'])
    alt_v = rh / esc_
    x = rx - px + (rw - CX_W * esc_) / 2
    return x, ry - py, esc_, alt_v


def aplicar():
    """Escreve public/index.html do FORMATO (RL|IN|GL|YT) e roteiro.md. Chamar no fim do gerar.py."""
    g = GEO[FORMATO]
    pub = AQUI / 'public'
    _preparar()
    v_div, v_cheio = _midia()
    com_musica = MUSICA_ON and _musica()

    fins = [c.t0 for c in CENAS[1:]] + [DUR]
    secoes, js, bordas, intervalos, avisos = [], [JS], [], [], []
    sx, sy, sw, sh = g['slot']
    zoom_div = 0
    for k, (c, t1) in enumerate(zip(CENAS, fins)):
        modo = c.modo
        ini = math.floor(round(c.t0 * FPS) / FPS * 10000) / 10000
        dur = round(q(t1 - c.t0) - 0.01, 4)
        escalas = [(c.t0, 1.0)] + [(z, ZOOM_T) for z in c.zoom]
        intervalos.append((c.t0, t1, modo, escalas))
        # 13/11 (caso real v3): duas cenas T seguidas = o mesmo pessoa cheia continuando — sem transição (blur/som) entre elas
        if k and not (modo == 'T' and CENAS[k - 1].modo == 'T'):
            bordas.append((c.t0, CENAS[k - 1].modo, modo))
        js.append(f'// {c.id} [{c.t0:.2f}–{t1:.2f}]{" pessoa" if modo == "T" else ""} {modo} {c.nome}: {c.fala}')
        # corte seco do tratado no MEIO de uma cena com a pessoa = pulo de imagem visível (falso corte)
        for ct in CORTES:
            if modo in 'DT' and c.t0 + 0.1 < ct < t1 - 0.1:
                avisos.append(f'{c.id}: corte seco do vídeo em {ct:.2f}s no meio da cena {modo} — comece uma cena ali '
                              f'(fronteira de frase) ou use G nesse trecho')
        if any(PROIBIDO.search(re.sub(r'<[^>]+>', ' ', h)) for h in c.partes + c.cab):
            sys.exit(f'{c.id}: texto na tela com link/QR/bio/Direct/URL — proibido em anúncio (regra 29/10)')
        if modo == 'T':
            # 07/11: pessoa cheia sem zoom por cima (base 1,0); zoom-cut leve (ZOOM_T) só em começo de frase
            # 13/11 (caso real v3): T seguido de T sumia com a pessoa a cena inteira — o opacity:0 em q(t1) (14,2667) caía
            # DEPOIS do opacity:1 da cena seguinte no ini arredondado pra baixo (14,2666) e aparecia a dividida por baixo
            # (painel preto + pessoa na faixa, legenda no rosto). Agora só esconde se a próxima não for T, no mesmo arredondamento.
            fim_t = math.floor(round(t1 * FPS) / FPS * 10000) / 10000
            prox_t = k + 1 < len(CENAS) and CENAS[k + 1].modo == 'T'
            js.append(f"tl.set('#tcheio',{{opacity:1}},{ini});" + ('' if prox_t else f"tl.set('#tcheio',{{opacity:0}},{fim_t});")
                      + f"tl.set('#vcheio',{{scale:1}},{ini});")
            for z in c.zoom:
                js.append(f"tl.set('#vcheio',{{scale:{ZOOM_T}}},{z});")
            qx, cb, ro = _rosto_T(c.t0, t1, escalas)
            if cb < 0:
                avisos.append(f'{c.id}: cabeça da pessoa cortada no topo (y {cb:.0f}) — tire o zoom-cut ou troque o modo')
            if ro > 0.66 * g['w'] and FORMATO != 'YT':
                avisos.append(f'{c.id}: rosto com {ro / g["w"]:.0%} da largura na pessoa cheio (zoom exagerado) — '
                              f'use T só nos takes em que ele está mais longe da câmera')
            continue
        if modo == 'D':   # pessoa da dividida: enquadramento muda de um bloco pro outro + zoom leve contínuo (regra 26/10)
            zoom_div += 1
            if ZOOM_D:
                b0 = 1.0 if zoom_div % 2 else 1.045
                js.append(f"tl.set('#vdiv',{{scale:{b0}}},{ini});tl.fromTo('#vdiv',{{scale:{b0}}},{{scale:{round(b0 + 0.025, 3)},"
                          f"duration:{q(t1 - c.t0)},ease:'none',immediateRender:false}},{ini});")
            else:
                js.append(f"tl.set('#vdiv',{{scale:1}},{ini});")
            x0, y0, w0, h0 = g['painel']
        else:
            x0, y0, w0, h0 = 0, 0, g['w'], g['h']
        cx, cy, esc_, alt_v = _caixa(c, modo, g)
        poeira = _poeira(c, t1, w0, h0)
        js.extend(c.js)
        # empurrão de câmera no conteúdo (nada parado > 4 s) — a caixa útil já deixa a folga pra margem de 100 px
        js.append(f"tl.fromTo('#{c.id} .cam',{{scale:1}},{{scale:{DERIVA},duration:{q(t1 - c.t0)},ease:'none',"
                  f"immediateRender:false}},{ini});")
        evs = sorted([c.t0] + [e for e in c.ev if c.t0 <= e <= t1] + [t1])
        buraco = max(b - a for a, b in zip(evs, evs[1:]))
        if buraco > 4.0:
            avisos.append(f'{c.id} ({modo}): {buraco:.1f} s sem nada entrar ou mudar no gráfico — ponha um evento no meio')
        partes = ''.join(c.partes)
        # 07/11 (aditivo): na dividida o cabeçalho vai pra baixo das peças; se for só o chapéu (sem título), ele fica
        # em cima, como eyebrow da peça (senão lia "peça / CHAPÉU")
        so = '' if any('class="titulo"' in h for h in c.cab) else ' so'
        cab = f'<div class="cab{so}">{"".join(c.cab)}</div>' if c.cab else ''
        secoes.append(f'<section id="{c.id}" class="cena clip {modo}" data-start="{ini}" data-duration="{dur}" data-track-index="2" '
                      f'style="left:{x0}px;top:{y0}px;width:{w0}px;height:{h0}px">'
                      f'<div class="fundo"></div><div class="ret"></div><div class="grao"></div>{poeira}<div class="vin"></div>'
                      f'<div class="cam"><div class="caixa" style="left:{cx:.1f}px;top:{cy:.1f}px;height:{alt_v:.1f}px;transform:scale({esc_:.4f})">'
                      f'{cab}{partes}</div></div></section>')
    for a in avisos:
        print('  AVISO', a)
    js.extend(_transicoes(bordas, DUR))
    audios, n_sfx = _audios(com_musica, fins)
    js.append(f'window.__timelines["{COMPOSICAO}"] = tl;')
    css = CSS.replace('__GRAO__', _GRAO) + (
        f"#sdiv{{left:{sx}px;top:{sy}px;width:{sw}px;height:{sh}px}}"
        f"#tcheio{{left:0;top:0;width:{g['w']}px;height:{g['h']}px;opacity:0;z-index:5}}"
        f"#vcheio{{transform-origin:50% {g['origem_T'] * 100:.0f}%}}"
        f"#vdiv{{transform-origin:{'50% 30%' if FORMATO == 'YT' else '50% 0%'}}}")
    if CARTAO_D and FORMATO == 'RL':   # pessoa menor num cartão sobre o marrom do estilo (ver CARTAO_D)
        cw_, ch_, tp_ = CARTAO_D
        css += (f"#sdiv{{background:radial-gradient(ellipse at 50% 42%,#2b1b0e 0%,#170f07 58%,#0b0703 100%)}}"
                f"#vdiv{{left:{(sw - cw_) // 2}px;top:{tp_}px;width:{cw_}px;height:{ch_}px;border-radius:28px;"
                f"box-shadow:0 18px 50px rgba(0,0,0,.55),0 0 0 2px rgba(255,170,100,.20)}}")
    pagina = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width={g['w']}, height={g['h']}" />
    <title>{esc(NOME)}</title>
    <style>{css}</style>
  </head>
  <body>
    <svg width="0" height="0" style="position:absolute;left:0;top:0" aria-hidden="true"><defs>
      <filter id="fw" x="-10%" y="0%" width="120%" height="100%" color-interpolation-filters="sRGB"><feGaussianBlur id="fwb" stdDeviation="0 0"/></filter>
    </defs></svg>
    <div id="root" data-composition-id="{COMPOSICAO}" data-start="0" data-duration="{DUR}" data-fps="30" data-width="{g['w']}" data-height="{g['h']}">
      <div id="mundo">
        <div class="slot" id="sdiv"><video id="vdiv" src="{v_div}" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video></div>
        <div id="palco">{''.join(secoes)}</div>
        <div class="slot" id="tcheio"><video id="vcheio" src="{v_cheio}" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video></div>
        {_legenda_html(intervalos)}
      </div>
      <div id="flash"></div>
      <div id="preto"></div>
      <audio id="voz" src="voz.m4a" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
      {audios}
    </div>
    <script src="vendor/gsap.min.js"></script>
    <script>
{chr(10).join(js)}
    </script>
  </body>
</html>
"""
    (pub / 'index.html').write_text(pagina, encoding='utf-8')
    linhas = [f'# {NOME} — roteiro (Editor Extremo)', '', f'| cena | modo {FORMATO} | início | fim | fala | visual |',
              '|---|---|---|---|---|---|']
    for c, t1 in zip(CENAS, fins):
        linhas.append(f'| {c.id} | {c.modo} | {c.t0:.2f} | {t1:.2f} | {c.fala} | {c.nome} |')
    (AQUI / 'roteiro.md').write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    modos = [c.modo for c in CENAS]
    durs = [t1 - c.t0 for c, t1 in zip(CENAS, fins)]
    print(f'[Extremo {FORMATO}] {len(CENAS)} cenas (D {modos.count("D")}, G {modos.count("G")}, T {modos.count("T")}), '
          f'média {sum(durs) / len(durs):.2f} s, máx {max(durs):.2f} s; {n_sfx} efeitos; música {"sim" if com_musica else "não"}')
