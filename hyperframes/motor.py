# -*- coding: utf-8 -*-
"""Motor das edições em HyperFrames no formato "tela dividida" (pessoa embaixo, painel de animações em cima).

Reutilizável: cada vídeo tem um hyperframes/<video>/gerar.py que chama configurar(...), escreve as cenas com
cena()/letreiro()/svg()/icone()/botao()/clique() e termina com montar(). Exemplo completo:
hyperframes/criativo-22/gerar.py. Processo inteiro: skill .claude/skills/video-dividido-hyperframes.

Estilo: lettering em Inter Bold (linhas grandes) + Montserrat Light (apoio), palavra-chave com o gradiente
esmeralda da marca, ícones Phosphor (ou monolinha próprios), cards/selos/botão do design system Conversão Extrema.
Sem título por padrão (pedido de 29/09: "tire o título / apenas coloque se eu pedir"); o título estilo Edits
(TikTok Sans 800 com contorno preto) só entra com configurar(titulo=[...]) + montar(fim_titulo=...).

Linha de comando do gerar.py de cada vídeo: [phosphor|proprios] [RL|YT|IN|GL] (padrão: phosphor RL).
"""
import html
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

from PIL import ImageFont

RAIZ = Path(__file__).resolve().parent.parent  # raiz do repositório

# Configuração do vídeo (preenchida por configurar())
AQUI = None          # pasta do vídeo (hyperframes/<video>/), com public/
W = None             # palavras da transcrição do áudio já cortado: [{'w','s','e'}, ...]
DUR = None           # duração em s, arredondada pra baixo ao quadro
COMPOSICAO = None    # data-composition-id / chave do timeline
NOME = None          # <title> e cabeçalho do roteiro
TITULO = []          # linhas do título estilo Edits (vazio = sem título, o padrão)
CENAS_PESSOA_GL = set()  # GL: cenas em que a pessoa ocupa o quadrado (as outras são animação em tela cheia)

FPS = 30
VERDE = '#10B981'
BRANCO = '#FFFFFF'

# Formatos. Os dois "quadrados" do RL (painel 1080x960 em cima, pessoa 1080x960 embaixo) são sempre os mesmos;
# cada formato só decide onde eles ficam e em que escala (pedido de 25/09: "mantenha os tamanhos dos quadrados,
# apenas ao invés de ser vertical, colocar um ao lado do outro").
#   palco = (x, y, escala) do quadro das animações; pessoa/divisoria = (x, y, largura, altura);
#   titulo = (centro x, centro y, largura da faixa); video = recorte da pessoa usado
S_YT = 960 / 1080
# IN: a faixa útil do painel do RL (y ~229–856, onde o conteúdo realmente fica) vai pra y ~150–633 dos 675 px de
# cima: o topo vazio do painel é o que sai, não o conteúdo, e o grupo continua baixo como no RL ("nada no alto").
S_IN = 0.77
TY_IN = -26
# GL: sugestão do usuário (25/09): "frase 1 com pessoa no vídeo, frase 2 e 3 animadas, frase 4 com pessoa…".
# Sem divisória: cada cena ocupa o quadrado inteiro, ou com a pessoa (recorte 1080x1080 do 16:9 na escala 1:1,
# rosto do mesmo tamanho do RL) ou com a animação no tamanho do RL. Quais cenas ficam com a pessoa é por vídeo
# (configurar(pessoa_gl=...)): ritmo 1 pessoa : 2 animadas, ajustado pelo conteúdo.

Y_YT = (1080 - 960 * S_YT) / 2
FORMATOS = {
    'RL': dict(w=1080, h=1920, palco=(0, 0, 1.0), pessoa=(0, 960, 1080, 960), divisoria=(0, 959, 1080, 2),
               titulo=(540, 960, 1080), video='pessoa.mp4'),
    # IN: mesmo estilo Reels, divisória no meio (675). pessoa = o mesmo enquadramento do RL (cabeça ao microfone)
    # reduzido a 70 % e mais largo (pessoa-IN.mp4: crop 1536x960 de base_h, escala 1080x676), sem cortar nada.
    'IN': dict(w=1080, h=1350, palco=(540 - 540 * S_IN, TY_IN, S_IN), pessoa=(0, 675, 1080, 675),
               divisoria=(0, 674, 1080, 2), titulo=(540, 675, 1080), video='pessoa-IN.mp4'),
    # GL: pessoa-GL.mp4 = crop 1080x1080 de base_h em x 460 (rosto em x≈1000). Título na altura do microfone.
    'GL': dict(w=1080, h=1080, palco=(0, 0, 1.0), pessoa=(0, 0, 1080, 1080), divisoria=(0, 0, 0, 0),
               titulo=(540, 800, 1080), video='pessoa-GL.mp4'),
    # YT: painel à esquerda, pessoa à direita ocupando a altura inteira (960x1080, sem faixa preta em cima e embaixo
    # — corrigido em 25/09 a pedido do usuário). Usa o recorte quadrado do GL (1080x1080 escala 1:1, rosto
    # centrado) aparado 60 px de cada lado pelo object-fit. Painel: animações na escala 0,889, no meio da altura
    # (fundo preto, então a sobra não aparece). Título sobre a pessoa, na altura do microfone.
    'YT': dict(w=1920, h=1080, palco=(0, Y_YT, S_YT), pessoa=(960, 0, 960, 1080),
               divisoria=(959, 0, 2, 1080), titulo=(1440, 800, 960), video='pessoa-GL.mp4'),
}
ARGS = sys.argv[1:]
MODO = next((a for a in ARGS if a in ('proprios', 'phosphor')), 'phosphor')
FORMATO = next((a for a in ARGS if a in FORMATOS), 'RL')
PHOSPHOR = MODO == 'phosphor'

GL_ESPERA_LINHA = True
# 26/10/2026 (regra do usuário): no RL alternar 3 modos — tela dividida (padrão), pessoa em TELA CHEIA (as cenas de frase
# de conversa: as mesmas do pessoa_gl) e animação em TELA CHEIA (CENAS_ANIM_CHEIA; vazio = escolhe ~1 a cada 5 cenas);
# e a pessoa de baixo (RL/YT) com zoom in/out leve contínuo. TRES_MODOS=False desliga.
TRES_MODOS = True
CENAS_ANIM_CHEIA = set()
CHEIA_SEM_ESPERA = False   # 05/11 (Edição animada): cena com cenário próprio pode virar cheia mesmo com a 1ª linha atrasada
CORTES_PESSOA = None   # 12/11 (Edição animada): tempos EXATOS dos cortes secos (pessoa_cheio.cortes_quadros) no lugar do .json
GNN = None   # 26/10: no GL, a cena animada só cobre a pessoa quando a 1ª linha do letreiro já montou (antes: tela preta com 1 palavra)
LARGURA_MAX = 880   # 25/10: lettering a ≥ 100 px de cada lateral (antes 940)
# Linha fina: a Montserrat Thin (100) saía falhada no celular (29/09) — o player reduz o vídeo à metade e o traço de
# ~2 px some em pedaços. A Light (300) aguenta a partir de ~52 px; abaixo disso a linha usa a Regular (400).
FINO_MIN_LIGHT = 52
CHAVE_FIM = 'rgba(52,211,153,0)'  # palavra-chave: o cinza some e aparece o gradiente da marca por trás


def configurar(pasta, palavras, duracao, composicao, nome, titulo=None, pessoa_gl=(), correcoes=None):
    """pasta: hyperframes/<video>/; palavras: JSON de palavras do áudio cortado (relativo à raiz do repo);
    duracao: s (base_h.mov arredondado pra baixo ao quadro); titulo: linhas do título Edits (só se ele pedir);
    pessoa_gl: ids das cenas com a pessoa no GL; correcoes: {índice: 'texto'} pra erros do whisper (o tempo fica)."""
    global AQUI, W, DUR, COMPOSICAO, NOME, TITULO, CENAS_PESSOA_GL, GNN
    AQUI = Path(pasta).resolve()
    GNN = Path(palavras).parent.name   # work/<gnn>/words_cut.json
    W = json.load(open(RAIZ / palavras, encoding='utf-8'))
    for i, txt in (correcoes or {}).items():
        W[i]['w'] = txt
    DUR, COMPOSICAO, NOME, TITULO = duracao, composicao, nome, list(titulo or [])
    CENAS_PESSOA_GL = set(pessoa_gl)


def cabe(texto, tam, fino):
    """Reduz o corpo até a linha caber em LARGURA_MAX (Inter Bold com tracking -0,02 em; Montserrat -0,01 em).
    Devolve (px, forte): forte = linha fina pequena demais pra Light, que passa pra Regular (FINO_MIN_LIGHT)."""
    limpo = ' '.join(re.sub(r'@\d+$', '', t.lstrip('*')) for t in texto.split())
    t0 = tam

    def reduz(nome, tam, track):
        while tam > 20:
            f = ImageFont.truetype(str(AQUI / 'public/fonts' / nome), tam)
            if f.getlength(limpo) - track * tam * (len(limpo) - 1) <= LARGURA_MAX:
                break
            tam -= 2
        return tam

    forte = False
    if fino:
        tam = reduz('Montserrat-Light.ttf', tam, 0.01)
        if tam < FINO_MIN_LIGHT:
            forte = True
            tam = reduz('Montserrat-Regular.ttf', tam, 0.01)
    else:
        tam = reduz('Inter-Bold.ttf', tam, 0.02)
    if tam != t0 or forte:
        print(f'  "{limpo}": {t0} -> {tam} px pra caber' + (' (linha fina em Regular)' if forte else ''))
    return tam, forte


def q(t):
    return round(round(t * FPS) / FPS, 4)


def fl(t):
    """Tempo do quadro de t arredondado PRA BAIXO em 4 casas. 12/11/2026 (caso real): tl.set(..., q(t)) com o quadro
    terminado em ,x666… (ex.: 54,0667 > 1622/30 = 54,06666…) só valia no quadro SEGUINTE — a pessoa saía 1 quadro
    atrasado, por cima da cena nova. Pra troca seca (set) use fl(); a seção da cena já começa no floor."""
    return math.floor(round(t * FPS) / FPS * 10000) / 10000


def ts(i):
    return W[i]['s']


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s)


def esc(s):
    return html.escape(s, quote=False)


# ---------------------------------------------------------------- ícones (monolinha, viewBox 64)

def P(d, cls=''):
    return f'<path class="d {cls}" pathLength="1" d="{d}"/>'


def C(cx, cy, r, cls=''):
    return f'<circle class="d {cls}" pathLength="1" cx="{cx}" cy="{cy}" r="{r}"/>'


def R(x, y, w, h, rx=0, cls=''):
    return f'<rect class="d {cls}" pathLength="1" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>'


def L(x1, y1, x2, y2, cls=''):
    return f'<line class="d {cls}" pathLength="1" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


def dentes(cx, cy, r1, r2, n=8):
    import math
    out = ''
    for k in range(n):
        a = 2 * math.pi * k / n
        out += L(round(cx + r1 * math.cos(a), 2), round(cy + r1 * math.sin(a), 2),
                 round(cx + r2 * math.cos(a), 2), round(cy + r2 * math.sin(a), 2))
    return out


ICONES = {
    'calendario': R(8, 12, 48, 44, 6) + L(8, 24, 56, 24) + L(20, 6, 20, 16) + L(44, 6, 44, 16)
    + L(18, 34, 22, 34) + L(30, 34, 34, 34) + L(42, 34, 46, 34) + L(18, 45, 22, 45) + L(30, 45, 34, 45),
    'chat': P('M12 12 H52 A6 6 0 0 1 58 18 V40 A6 6 0 0 1 52 46 H30 L18 56 V46 H12 A6 6 0 0 1 6 40 V18 A6 6 0 0 1 12 12 Z')
    + L(20, 25, 44, 25) + L(20, 34, 36, 34),
    'grafico': P('M8 8 V56 H58') + L(19, 48, 19, 38) + L(30, 48, 30, 28) + L(41, 48, 41, 20) + L(52, 48, 52, 32),
    'email': R(8, 14, 48, 36, 5) + P('M10 18 L32 35 L54 18'),
    'documento': P('M16 6 H38 L50 18 V58 H16 Z') + P('M38 6 V18 H50') + L(23, 30, 43, 30) + L(23, 38, 43, 38) + L(23, 46, 35, 46),
    'pessoas': C(24, 22, 8) + P('M8 54 C8 44 15 38 24 38 C33 38 40 44 40 54') + C(45, 24, 6) + P('M43 38 C51 38 57 43 57 52'),
    'engrenagem': C(32, 32, 8) + C(32, 32, 17) + dentes(32, 32, 17, 25),
    'pessoa': C(32, 20, 10) + P('M12 56 C12 44 21 36 32 36 C43 36 52 44 52 56'),
    'megafone': P('M8 26 H18 L40 14 V50 L18 38 H8 Z') + P('M18 38 L22 52 H29 L26 40')
    + P('M47 25 Q52 32 47 39', 'g') + P('M53 19 Q61 32 53 45', 'g'),
    'relogio': C(32, 32, 24) + '<g class="ph">' + L(32, 32, 41, 32) + '</g>'
    + '<g class="pm">' + L(32, 32, 32, 14) + '</g>' + '<circle class="f" cx="32" cy="32" r="2.6"/>',
    'loop': '<g class="lp">' + P('M12 34 A20 20 0 0 1 46 18') + P('M39 10 L47 18 L38 22')
    + P('M52 30 A20 20 0 0 1 18 46') + P('M25 54 L17 46 L26 42') + '</g>',
    'ampulheta': L(14, 8, 50, 8) + L(14, 56, 50, 56)
    + P('M19 8 C19 22 29 26 31 32 C29 38 19 42 19 56') + P('M45 8 C45 22 35 26 33 32 C35 38 45 42 45 56')
    + '<path class="fg areia-t" d="M24 15 H40 C40 21 35 25 32 28 C29 25 24 21 24 15 Z"/>'
    + '<path class="fg areia-b" d="M23 54 C24 46 40 46 41 54 Z"/>',
    'predio_p': R(12, 24, 40, 34, 2) + L(20, 34, 26, 34) + L(38, 34, 44, 34) + L(20, 44, 26, 44)
    + L(38, 44, 44, 44) + P('M28 58 V50 H36 V58') + P('M8 24 L32 12 L56 24', 'g'),
    'predio_m': R(10, 6, 44, 52, 2) + L(18, 16, 24, 16) + L(30, 16, 34, 16) + L(40, 16, 46, 16)
    + L(18, 26, 24, 26) + L(30, 26, 34, 26) + L(40, 26, 46, 26) + L(18, 36, 24, 36) + L(30, 36, 34, 36)
    + L(40, 36, 46, 36) + P('M26 58 V47 H38 V58', 'g'),
    'raio': P('M36 5 L13 36 H30 L26 59 L51 26 H34 Z', 'g'),
    'cronometro': C(32, 36, 22) + L(32, 8, 32, 14) + L(25, 8, 39, 8) + L(49, 17, 53, 13)
    + '<g class="mao">' + L(32, 36, 32, 22, 'g') + '</g>' + '<circle class="f" cx="32" cy="36" r="2.6"/>',
    'seta_baixo': L(32, 8, 32, 52) + P('M17 38 L32 53 L47 38'),
    'quadro': R(6, 8, 52, 34, 3) + L(32, 42, 32, 51) + P('M21 58 L32 51 L43 58') + P('M13 33 L23 24 L31 29 L45 17', 'g'),
    'lupa': C(27, 27, 16) + L(39, 39, 55, 55) + P('M19 27 A8 8 0 0 1 27 19', 'g'),
    'check': P('M17 33 L27 43 L47 22'),
    'xis': L(20, 20, 44, 44) + L(44, 20, 20, 44),
    'trend_up': P('M6 50 L22 32 L33 41 L57 15') + P('M42 15 H57 V30'),
    'trend_down': P('M6 14 L22 32 L33 23 L57 49') + P('M42 49 H57 V34'),
    'seta_dir': L(6, 32, 56, 32) + P('M42 18 L56 32 L42 46'),
    'sino': '<g class="sg">' + P('M18 44 V30 A14 14 0 0 1 46 30 V44 L50 50 H14 Z') + P('M27 54 A5 5 0 0 0 37 54')
    + L(32, 9, 32, 16) + '</g>',
    'ia': R(15, 15, 34, 34, 6, 'g') + L(24, 7, 24, 15, 'g') + L(32, 7, 32, 15, 'g') + L(40, 7, 40, 15, 'g')
    + L(24, 49, 24, 57, 'g') + L(32, 49, 32, 57, 'g') + L(40, 49, 40, 57, 'g')
    + L(7, 24, 15, 24, 'g') + L(7, 32, 15, 32, 'g') + L(7, 40, 15, 40, 'g')
    + L(49, 24, 57, 24, 'g') + L(49, 32, 57, 32, 'g') + L(49, 40, 57, 40, 'g')
    + '<text class="ftxt" x="32" y="37.6" text-anchor="middle">IA</text>',
}



# 'check' e 'xis' ficam sempre com traço desenhado: são marcas que animam (visto, X), não pictogramas
PH = {'calendario': 'calendar-blank', 'chat': 'chat-text', 'grafico': 'chart-bar', 'email': 'envelope-simple',
      'documento': 'file-text', 'pessoas': 'users', 'engrenagem': 'gear', 'pessoa': 'user', 'megafone': 'megaphone',
      'relogio': 'clock', 'loop': 'arrows-clockwise', 'ampulheta': 'hourglass-high', 'predio_p': 'storefront',
      'predio_m': 'buildings', 'raio': 'lightning', 'cronometro': 'timer', 'seta_baixo': 'arrow-down',
      'quadro': 'presentation-chart', 'lupa': 'magnifying-glass', 'trend_up': 'trend-up', 'trend_down': 'trend-down',
      'seta_dir': 'arrow-right', 'sino': 'bell-ringing', 'ia': 'cpu'}
PH_VERDE = {'ia', 'raio'}  # no desenho próprio esses já eram verdes por dentro
PH_DIR = RAIZ / 'ferramentas/phosphor-core/assets/regular'


def ph_svg(arquivo, tam, id_='', cls='', estilo=''):
    corpo = re.search(r'<svg[^>]*>(.*)</svg>', (PH_DIR / f'{arquivo}.svg').read_text(encoding='utf-8'), re.S).group(1)
    ida = f' id="{id_}"' if id_ else ''
    est = f' style="{estilo}"' if estilo else ''
    return (f'<svg{ida} class="ic ph {cls}" width="{tam}" height="{tam}" viewBox="0 0 256 256" fill="#fff"{est}>'
            f'{corpo}</svg>')


def svg(nome, tam, id_='', cls='', sw=2.6, extra=''):
    if PHOSPHOR and nome in PH:
        return ph_svg(PH[nome], tam, id_, cls + (' verde' if nome in PH_VERDE else ''))
    ida = f' id="{id_}"' if id_ else ''
    return (f'<svg{ida} class="ic {cls}" width="{tam}" height="{tam}" viewBox="0 0 64 64" fill="none" '
            f'stroke="#fff" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{extra}>'
            f'{ICONES[nome]}</svg>')


# ---------------------------------------------------------------- cenas

class Cena:
    n = 0

    def __init__(self, i0, i1, nome):
        Cena.n += 1
        self.id = f'c{Cena.n:02d}'
        self.i0, self.i1, self.nome = i0, i1, nome
        self.t0 = 0.0 if i0 == 0 else q(ts(i0) - 0.20)  # troca 0,20 s antes da 1ª palavra
        self.js = []
        self.html = ''
        self.fala = ' '.join(W[i]['w'] for i in range(i0, i1 + 1))

    def a(self, linha):
        self.js.append(linha)


CENAS = []


def cena(i0, i1, nome):
    c = Cena(i0, i1, nome)
    CENAS.append(c)
    return c


def icone(c, sel, t, d=0.4, st=0.05, so_proprio=False):
    """Entrada de um ícone: traço desenhando (próprios) ou revelação de baixo pra cima (Phosphor, regra 16).
    so_proprio: no Phosphor o contêiner já entra sozinho (pop/entra), então não revela de novo."""
    if not PHOSPHOR:
        c.a(f"desenha('{sel} .d',{q(t)},{d},{st});")
    elif not so_proprio:
        c.a(f"revela('{sel}',{q(t)});")


def letreiro(c, spec, estilo=''):
    """spec: linhas separadas por '|', cada uma '{px}texto' (Inter Bold) ou '{pxf}texto' (Montserrat Light). '*palavra' = chave (verde).
    'palavra@N' = usa o tempo da palavra N da transcrição (não avança o ponteiro).
    Demais palavras são casadas em ordem com a fala da cena. Cada palavra entra com a fala."""
    linhas = []
    k = 0
    ptr = c.i0
    ultimo = c.t0 + 0.10
    for parte in spec.split('|'):
        m = re.match(r'\{(\d+)(f?)\}(.*)', parte.strip())
        tam, fino, texto = int(m.group(1)), bool(m.group(2)), m.group(3)
        tam, forte = cabe(texto, tam, fino)
        spans = []
        for tok in texto.split():
            chave = tok.startswith('*') and not fino  # gradiente em traço fino some; destaque só nas linhas bold
            tok = tok.lstrip('*')
            mm = re.match(r'^(.*)@(\d+)$', tok)
            if mm:
                txt, t = mm.group(1), ts(int(mm.group(2)))
            else:
                txt, t = tok, None
                for j in range(ptr, c.i1 + 1):
                    if norm(W[j]['w']) == norm(txt):
                        t = ts(j)
                        ptr = j + 1
                        break
                if t is None:
                    t = ultimo + 0.10
                    print(f'  aviso {c.id}: "{txt}" sem correspondência na fala')
            rev = q(max(ultimo, c.t0 + 0.10, t - 0.06))
            ultimo = rev
            wid = f'{c.id}-w{k}'
            k += 1
            spans.append(f'<span class="w{" k" if chave else ""}" id="{wid}">{esc(txt)}</span>')
            c.a(f"palavra('#{wid}',{rev},'{CHAVE_FIM if chave else BRANCO}');")
        cls = (' fino forte' if forte else ' fino') if fino else ''
        linhas.append(f'<div class="ln{cls}" style="font-size:{tam}px">{" ".join(spans)}</div>')
    return f'<div class="let" style="{estilo}">{"".join(linhas)}</div>'


def miolo(conteudo, cls='', estilo=''):
    if not TITULO:  # sem título, a cena não reserva o espaço dele
        cls = ' '.join(k for k in cls.split() if k != 'sob-titulo')
    return f'<div class="miolo {cls}" style="{estilo}">{conteudo}</div>'


def pontos(c, n):
    """Progresso da lista de tarefas (5 itens)."""
    ds = ''
    for i in range(5):
        cls = 'on' if i < n else ('at' if i == n else '')
        ida = f' id="{c.id}-at"' if i == n else ''
        ds += f'<div class="dot {cls}"{ida}></div>'
    c.a(f"pop('#{c.id}-at',{q(c.t0 + 0.06)});")
    return f'<div class="dots">{ds}</div>'


def botao(c, texto='Agendar reunião'):
    # borda cônica gira 360° a cada 2,5 s (Button shiny do design system); 4 s cobre a cena inteira
    c.a(f"vai('#{c.id}-bt',{{'--ga':'576deg',duration:4,ease:'none'}},{q(c.t0)});")
    return (f'<div class="bt-wrap"><div class="botao" id="{c.id}-bt" style="--ga:0deg">'
            f'<span class="bt-verde" id="{c.id}-btv"></span><span class="pontos"></span>'
            f'<span class="bt-cont"><span>{esc(texto)}</span>{svg("check", 44, c.id + "-btok", "okbt", sw=5)}</span></div>'
            f'<svg id="{c.id}-cur" class="cursor" width="84" height="84" viewBox="0 0 64 64">'
            f'<path d="M14 8 L14 50 L25 40 L33 56 L40 53 L32 37 L46 37 Z" fill="#fff" stroke="#060606" '
            f'stroke-width="3" stroke-linejoin="round"/></svg></div>')


def clique(c, t):
    s = f'#{c.id}'
    ini = max(t - 0.38, c.t0 + 0.08)  # o cursor nunca entra antes do corte
    c.a(f"desliza('{s}-cur',{q(ini)},150,130,{round(min(0.34, t - ini - 0.02), 2)});")
    c.a(f"vai('{s}-cur',{{scale:0.82,duration:0.08}},{q(t)});")
    c.a(f"vai('{s}-cur',{{scale:1,duration:0.14}},{q(t + 0.08)});")
    c.a(f"vai('{s}-bt',{{scale:0.94,duration:0.08}},{q(t)});")
    c.a(f"vai('{s}-bt',{{scale:1,duration:0.2}},{q(t + 0.08)});")
    c.a(f"vai('{s}-btv',{{opacity:1,duration:0.25}},{q(t + 0.08)});")
    c.a(f"desenha('{s}-btok .d',{q(t + 0.12)},0.25);")



# ---------------------------------------------------------------- montagem

CSS = """
@font-face{font-family:'Inter';src:url('fonts/Inter-Regular.ttf') format('truetype');font-weight:400;font-display:block}
@font-face{font-family:'Inter';src:url('fonts/Inter-Bold.ttf') format('truetype');font-weight:700;font-display:block}
@font-face{font-family:'Montserrat';src:url('fonts/Montserrat-Light.ttf') format('truetype');font-weight:300;font-display:block}
@font-face{font-family:'Montserrat';src:url('fonts/Montserrat-Regular.ttf') format('truetype');font-weight:400;font-display:block}
@font-face{font-family:'TikTok Sans';src:url('fonts/TikTokSans-Variable.ttf') format('truetype');font-weight:300 900;font-display:block}
*{box-sizing:border-box}
html,body{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#060606;font-family:'Inter',sans-serif;color:#fff}
#root{position:relative;width:100%;height:100%;overflow:hidden;background:#060606}
#palco{position:absolute;width:1080px;height:960px;overflow:hidden;transform-origin:0 0}
#pessoa{position:absolute;object-fit:cover}
#divisoria{position:absolute;background:rgba(255,255,255,0.18)}
.cena{position:absolute;left:0;top:0;width:1080px;height:960px;overflow:hidden}
.miolo{position:absolute;left:0;top:0;width:1080px;height:960px;padding:220px 70px 50px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px}
.miolo.sob-titulo{padding-bottom:175px}
.let{font-family:'Inter',sans-serif;font-weight:700;color:#fff;text-align:center;line-height:1.08;letter-spacing:-0.02em}
.let .ln.fino{font-family:'Montserrat',sans-serif;font-weight:300;letter-spacing:-0.01em;line-height:1.2}
.let .ln.fino.forte{font-weight:400}
.let .w.k{background-image:linear-gradient(90deg,#10B981,#34D399);-webkit-background-clip:text;background-clip:text}
.let .ln{white-space:nowrap}
.let .w{display:inline-block}
.linha{display:flex;align-items:center;justify-content:center}
.grade{display:flex;flex-wrap:wrap;justify-content:center;gap:26px}
.tile{width:172px;height:172px;border-radius:38px;background:transparent;border:2px solid #2A2A2A;display:flex;align-items:center;justify-content:center;position:relative;flex:none}
.tile.p{width:88px;height:88px;border-radius:22px}
.tile.mini{width:80px;height:80px;border-radius:20px}
.tile.gd{border:3px solid #10B981;background:#0B2419;border-radius:40px}
.risco{position:absolute;left:0;top:0}
.xis{position:absolute;left:0;top:0}
.ic .g{stroke:#10B981}
.ic.verde{stroke:#10B981}
.ic.preto{stroke:#060606}
.ic.ph{fill:#fff}
.ic.ph.verde{fill:#10B981}
.ic .d{stroke-dasharray:1 2}
.ic .f{fill:#fff;stroke:none}
.ic .fg{fill:#10B981;stroke:none}
.ic .ftxt{fill:#10B981;stroke:none;font-family:'Inter',sans-serif;font-weight:700;font-size:14px;letter-spacing:0}
svg .d{stroke-dasharray:1 2}
.chip{display:inline-flex;align-items:center;gap:14px;padding:16px 36px;border-radius:9999px;background:rgba(16,185,129,0.16);color:#34D399;font-family:'Inter',sans-serif;font-weight:400;font-size:38px;letter-spacing:0.02em;white-space:nowrap}
.chip.mini{padding:8px 22px;font-size:28px}
.slot{width:130px;height:130px;border-radius:30px;border:3px dashed #3A3A3A;display:flex;align-items:center;justify-content:center}
.slot .q{display:block;font-family:'Inter',sans-serif;font-weight:700;font-size:64px;color:#10B981}
.barras{display:flex;align-items:flex-end;gap:26px}
.barra{border-radius:16px 16px 6px 6px;background:#fff}
.cartao{background:transparent;border:2px solid #262626;border-radius:40px;position:relative}
.fila{display:flex;align-items:center;gap:22px}
.rot{width:130px;font-size:26px;font-weight:400;letter-spacing:0.14em;text-transform:uppercase;color:#A8A8A8}
.rot.g{color:#10B981}
.trilho{flex:1;height:40px;border-radius:20px;background:#1E1E1E;overflow:hidden}
.barra-h{width:100%;height:100%;border-radius:20px}
.val{width:130px;text-align:right;font-size:46px;font-weight:700;color:#fff}
.val.g{color:#10B981}
.selo{position:absolute;right:-14px;top:-14px;width:52px;height:52px;border-radius:26px;background:#10B981;display:flex;align-items:center;justify-content:center}
.dots{display:flex;gap:14px}
.dot{width:18px;height:18px;border-radius:9px;background:#2E2E2E}
.dot.on{background:#fff}
.dot.at{background:#10B981}
.avatar{width:130px;height:130px;border-radius:65px;background:#1E1E1E;display:flex;align-items:center;justify-content:center;flex:none}
.cinza{height:22px;border-radius:11px;background:#2E2E2E}
.bolha{padding:22px 32px;border-radius:32px;font-size:40px;white-space:nowrap}
.bolha.in{align-self:flex-start;background:#262626;color:#fff;border-bottom-left-radius:8px;font-weight:400}
.vaga{position:relative;height:98px;align-self:stretch}
.bolha.out{position:absolute;right:0;top:0;background:#10B981;color:#060606;border-bottom-right-radius:8px;font-weight:700}
.digita{position:absolute;right:0;top:10px;display:flex;gap:10px;padding:24px 28px;background:#1E1E1E;border-radius:28px}
.digita i{display:block;width:14px;height:14px;border-radius:7px;background:#8A8A8A}
.badge{position:absolute;right:10px;top:14px;width:58px;height:58px;border-radius:29px;background:#10B981;color:#060606;font-size:28px;font-weight:700;display:flex;align-items:center;justify-content:center}
.kick{font-size:26px;font-weight:400;letter-spacing:0.14em;text-transform:uppercase;color:#A8A8A8}
.tarefa{display:flex;align-items:center;gap:22px}
.tarefa-rep{display:flex;align-items:center;gap:20px;padding:20px 30px;width:500px;border-radius:22px;font-size:38px;color:#BDBDBD}
.caixa{width:340px;height:290px;border-radius:30px;border:3px dashed #3A3A3A;display:flex;align-items:center;justify-content:center;font-size:190px;font-weight:700;line-height:1;color:#fff}
.caixa span{display:block}
.pilha{display:flex;flex-direction:column-reverse;gap:6px}
.moeda{width:150px;height:32px;border-radius:16px;border:3px solid #10B981;background:#0B2419}
.bt-wrap{position:relative}
.botao{position:relative;overflow:hidden;isolation:isolate;display:flex;align-items:center;padding:34px 76px;border-radius:9999px;border:3px solid transparent;color:#fff;font-size:52px;font-weight:700;white-space:nowrap;background:linear-gradient(#1c2421,#0a0a0a) padding-box,conic-gradient(from var(--ga,0deg),transparent 0%,#047857 5%,#10B981 15%,#047857 30%,transparent 40%,transparent 100%) border-box;box-shadow:inset 0 2px 3px rgba(255,255,255,0.15),inset 0 -5px 15px rgba(0,0,0,0.2),0 30px 60px -20px rgba(0,0,0,0.5)}
.botao .bt-verde{position:absolute;left:0;top:0;right:0;bottom:0;border-radius:9999px;background:linear-gradient(#10B981,#047857);opacity:0;z-index:0}
.botao .pontos{position:absolute;left:0;top:0;right:0;bottom:0;border-radius:9999px;z-index:1;background-image:radial-gradient(circle at 1.25px 1.25px,rgba(16,185,129,0.6) 1.25px,transparent 0);background-size:12px 12px;-webkit-mask-image:linear-gradient(125deg,transparent 54%,rgba(0,0,0,0.85) 66%,rgba(0,0,0,0.85) 74%,transparent 85%);mask-image:linear-gradient(125deg,transparent 54%,rgba(0,0,0,0.85) 66%,rgba(0,0,0,0.85) 74%,transparent 85%)}
.botao .bt-cont{position:relative;z-index:2;display:flex;align-items:center;gap:20px}
.okbt{stroke:#fff}
.cursor{position:absolute;right:-20px;bottom:-54px}
.cal{display:grid;grid-template-columns:repeat(7,60px);gap:12px}
.cel{width:60px;height:60px;border-radius:14px;background:#1E1E1E;border:2px solid #1E1E1E;display:flex;align-items:center;justify-content:center}
.av{width:110px;height:110px;border-radius:55px;background:#1E1E1E;border:4px solid #060606;margin-left:-18px;display:flex;align-items:center;justify-content:center}
.passo{width:130px;height:130px;border-radius:65px;border:5px solid #3A3A3A;display:flex;align-items:center;justify-content:center;position:relative;font-size:56px;font-weight:700}
.passo .k-passo{position:absolute;left:22px;top:22px}
.elo{width:150px;height:8px;background:#2A2A2A;border-radius:3px;overflow:hidden}
.elo-f{width:100%;height:100%;background:#10B981}
#titulo{position:absolute;height:300px;display:flex;flex-direction:column;align-items:center;justify-content:center}
#titulo .tl{font-family:'TikTok Sans',sans-serif;font-weight:800;font-size:68px;line-height:1.14;color:#fff;letter-spacing:-0.01em;-webkit-text-stroke:8px #000;paint-order:stroke fill;text-shadow:0 4px 16px rgba(0,0,0,0.35);white-space:nowrap}
"""

JS_BASE = """
const tl = gsap.timeline({ paused: true });
function palavra(s,t,cor){tl.fromTo(s,{opacity:0,y:8,color:'#5A5A5A'},{opacity:1,y:0,color:cor,duration:0.2,ease:'power2.out'},t);}
function entra(s,t,d){tl.fromTo(s,{opacity:0,scale:0.92},{opacity:1,scale:1,duration:d||0.2,ease:'power3.out',transformOrigin:'50% 50%'},t);}
function pop(s,t,st){tl.fromTo(s,{opacity:0,scale:0.3},{opacity:1,scale:1,duration:0.32,ease:'back.out(1.6)',stagger:st||0,transformOrigin:'50% 50%'},t);}
function aparece(s,t,d){tl.fromTo(s,{opacity:0},{opacity:1,duration:d||0.15,ease:'none'},t);}
function desenha(s,t,d,st){tl.fromTo(s,{strokeDashoffset:1.02},{strokeDashoffset:0,duration:d||0.4,ease:'power2.inOut',stagger:st||0},t);}
function sobe(s,t,d,st){tl.fromTo(s,{scaleY:0},{scaleY:1,duration:d||0.45,ease:'power3.out',stagger:st||0,transformOrigin:'50% 100%'},t);}
function estica(s,t,d,st){tl.fromTo(s,{scaleX:0},{scaleX:1,duration:d||0.45,ease:'power3.out',stagger:st||0,transformOrigin:'0% 50%'},t);}
function vai(s,v,t){tl.to(s,Object.assign({duration:0.3,ease:'power2.inOut'},v),t);}
function desliza(s,t,dx,dy,d){tl.fromTo(s,{opacity:0,x:dx,y:dy},{opacity:1,x:0,y:0,duration:d||0.3,ease:'power3.out'},t);}
function conta(s,a,b,t,d,suf){const el=document.querySelector(s);const o={v:a};tl.to(o,{v:b,duration:d,ease:'power2.out',onUpdate:function(){el.textContent=Math.round(o.v)+(suf||'');}},t);}
function gira(s,a,b,t,d,orig,ease){tl.fromTo(s,{rotation:a},{rotation:b,duration:d,ease:ease||'none',svgOrigin:orig},t);}
function balanca(s,t,n,amp,per,orig){tl.fromTo(s,{rotation:-amp},{rotation:amp,duration:per,ease:'sine.inOut',yoyo:true,repeat:n,svgOrigin:orig,immediateRender:false},t);tl.to(s,{rotation:0,duration:per/2,ease:'sine.out',svgOrigin:orig},t+per*(n+1));}
function revela(s,t,d){tl.fromTo(s,{clipPath:'inset(100% 0% 0% 0%)'},{clipPath:'inset(0% 0% 0% 0%)',duration:d||0.32,ease:'power3.out'},t);}
function giraO(s,a,b,t,d,orig,ease){tl.to(s,{rotation:b,duration:d,ease:ease||'none',transformOrigin:orig},t);}
function balancaO(s,t,n,amp,per,orig){tl.to(s,{rotation:amp,duration:per,ease:'sine.inOut',yoyo:true,repeat:n,transformOrigin:orig},t);tl.to(s,{rotation:0,duration:per/2,ease:'sine.out',transformOrigin:orig},t+per*(n+1));}
function quica(s,t,n,dy,per,st){tl.to(s,{y:dy,duration:per,ease:'sine.inOut',yoyo:true,repeat:n,stagger:st||0},t);}
"""


def css_formato(f):
    px, py, esc = f['palco']
    tx, ty, tw, th = f['pessoa']
    dx, dy, dw, dh = f['divisoria']
    cx, cy, larg = f['titulo']
    extra = {
        'YT': '.miolo.sob-titulo{padding-bottom:50px}',  # no YT o título não fica sobre o painel
        # GL: cena animada cobre o quadrado inteiro (fundo preto por cima da pessoa); com o título na tela,
        # o conteúdo fica entre y 180 e 700 pra não encostar nele
        'GL': '#palco{height:1080px}.cena{height:1080px;background:#060606}'
              '.miolo{height:1080px;padding:250px 70px 110px}.miolo.sob-titulo{padding:180px 70px 380px}'
              '#divisoria{display:none}',
    }.get(FORMATO, '')
    return (f"#palco{{left:{px:.2f}px;top:{py:.2f}px;transform:scale({esc:.5f})}}"
            f"#pessoa{{left:{tx:.2f}px;top:{ty:.2f}px;width:{tw:.2f}px;height:{th:.2f}px}}"
            f"#divisoria{{left:{dx:.2f}px;top:{dy:.2f}px;width:{dw:.2f}px;height:{dh:.2f}px}}"
            f"#titulo{{left:{cx - larg / 2:.2f}px;top:{cy - 150:.2f}px;width:{larg}px}}{extra}")  # faixa de 300 px centrada em cy


def antecipar_fim(linhas, t0, t1, folga=0.3):
    """Palavra do letreiro que cairia a menos de `folga` s do corte (a fala emenda na frase seguinte) entra em
    t1 - folga: senão ela aparece por 1–3 quadros e some (visto num vlog)."""
    lim = q(max(t0 + 0.1, t1 - folga))
    saida = []
    for ln in linhas:
        m = re.match(r"palavra\('([^']+)',([\d.]+),('[^']+')\);$", ln)
        if m and float(m.group(2)) > lim:
            ln = f"palavra('{m.group(1)}',{lim},{m.group(3)});"
        saida.append(ln)
    return saida


def montar(fim_titulo=None):
    """Escreve public/index.html do FORMATO pedido e roteiro.md. fim_titulo = início da cena em que o título some
    (só vale se configurar() recebeu titulo; sem título é o padrão)."""
    com_titulo = bool(TITULO) and fim_titulo is not None
    f = FORMATOS[FORMATO]
    fim = [CENAS[k + 1].t0 for k in range(len(CENAS) - 1)] + [DUR]
    secoes = []
    js = [JS_BASE]
    for c, t1 in zip(CENAS, fim):
        if FORMATO == 'GL' and c.id in CENAS_PESSOA_GL:
            js.append(f'// {c.id} [{c.t0:.2f}–{t1:.2f}] pessoa em tela cheia: {c.fala}')
            continue  # sem cena por cima: aparece o vídeo da pessoa
        # termina 0,01 s antes do corte: com 4 casas, início + duração passava do quadro do corte e a cena
        # anterior aparecia junto com a seguinte por 1 quadro
        dur = round(q(t1 - c.t0) - 0.01, 4)
        # início arredondado pra baixo: 5.0667 > 152/30 = 5.06666… e a cena entrava 1 quadro atrasada
        ini = math.floor(round(c.t0 * FPS) / FPS * 10000) / 10000
        secoes.append(f'<section id="{c.id}" class="cena clip" data-start="{ini}" data-duration="{dur}" '
                      f'data-track-index="2">{c.html}</section>')
        js.append(f'// {c.id} [{c.t0:.2f}–{t1:.2f}] {c.fala}')
        linhas_js = antecipar_fim(c.js, c.t0, t1)
        js.extend(linhas_js)
        if FORMATO == 'GL' and GL_ESPERA_LINHA:
            m1 = re.search(r'<div class="ln[^"]*"[^>]*>(.*?)</div>', c.html, re.S)
            ids = re.findall(r'id="(c\d+-w\d+)"', m1.group(1)) if m1 else []
            tt = [float(x) for i in ids for x in re.findall(rf"palavra\('#{i}',([\d.]+)", ' '.join(linhas_js))]
            if tt and max(tt) > ini + 0.05:
                js.append(f"tl.set('#{c.id}',{{opacity:0}},{ini});tl.set('#{c.id}',{{opacity:1}},{q(min(max(tt) + 0.04, t1 - 0.2))});")
    if TRES_MODOS:
        # zoom in/out leve na pessoa (3,5 s pra entrar, 3,5 s pra sair; até +6 %). 27/10 (usuário, "falso corte"): nos cortes
        # secos do tratado (work/<gNN>/cortes_visuais.json) o enquadramento troca na hora (1,00 <-> 1,12), vira troca de câmera
        cortes = []
        cv = RAIZ / 'work' / GNN / 'cortes_visuais.json' if GNN else None
        if cv and cv.exists():
            cortes = [c for c in json.loads(cv.read_text()) if 0.5 < c < DUR - 0.5]
        if CORTES_PESSOA is not None:   # 12/11: o .json é aproximado (até 2 quadros antes do take novo aparecer)
            cortes = [c for c in CORTES_PESSOA if 0.5 < c < DUR - 0.5]
        # 02/11 (usuário, caso real "muito zoom no rosto"): a pessoa em tela cheia já é o recorte 9:16 (1,78x) — sem zoom por
        # cima; no de baixo o zoom caiu de 1,12/+6 % pra 1,06/+3 %, a partir do topo (origem 50% 0%): crescendo do meio ele
        # subia por cima da divisória e aparecia uma "linha solta" atravessando o vídeo
        alvos = ['#pessoa']
        lim = [0.0] + cortes + [DUR]
        for alvo in alvos:
            js.append(f"tl.set('{alvo}',{{scale:1,transformOrigin:'50% 0%'}},0);")
            for i in range(len(lim) - 1):
                a, b = lim[i], lim[i + 1]; base = 1.06 if i % 2 else 1.0
                if i: js.append(f"tl.set('{alvo}',{{scale:{base}}},{fl(a)});")   # 12/11: fl = no quadro do corte, não 1 depois
                k, dentro = a, True
                while k < b - 0.05:
                    d = min(3.5, b - k)
                    js.append(f"tl.to('{alvo}',{{scale:{round(base * (1.03 if dentro else 1), 4)},duration:{q(d)},ease:'sine.inOut'}},{q(k)});")
                    k += 3.5; dentro = not dentro
    if TRES_MODOS and FORMATO == 'RL':
        def linha1_pronta(c, t1):   # 1ª linha do letreiro montada até 0,5 s depois do início e cena com ≥ 1,5 s
            ini = math.floor(round(c.t0 * FPS) / FPS * 10000) / 10000
            m1 = re.search(r'<div class="ln[^"]*"[^>]*>(.*?)</div>', c.html, re.S)
            ids = re.findall(r'id="(c\d+-w\d+)"', m1.group(1)) if m1 else []
            tt = [float(x) for i in ids for x in re.findall(rf"palavra\('#{i}',([\d.]+)", ' '.join(c.js))]
            return not (tt and max(tt) > ini + 0.5) and q(t1) - ini >= 1.5
        anim = set(CENAS_ANIM_CHEIA)
        if not anim:   # ~1 a cada 5 cenas, só entre as que podem virar cheias desde o início
            ult = -9
            for k_, (c, t1) in enumerate(zip(CENAS, fim)):
                if 2 <= k_ < len(CENAS) - 2 and k_ - ult >= 4 and c.id not in CENAS_PESSOA_GL and linha1_pronta(c, t1):
                    anim.add(c.id); ult = k_
        for c, t1 in zip(CENAS, fim):
            ini = math.floor(round(c.t0 * FPS) / FPS * 10000) / 10000; t1f = fl(t1); t1 = q(t1)
            if c.id in CENAS_PESSOA_GL:      # pessoa em tela cheia falando a frase
                # 12/11 (caso real): sai no quadro em que a cena seguinte começa (fl), não 1 quadro depois (q arredondava pra cima)
                js.append(f"tl.set('#pessoacheio',{{opacity:1}},{ini});tl.set('#divisoria',{{opacity:0}},{ini});"
                          f"tl.set('#pessoacheio',{{opacity:0}},{t1f});tl.set('#divisoria',{{opacity:1}},{t1f});")
            elif c.id in anim:              # animação em tela cheia (a cena cresce pra 1920 e o conteúdo desce pro meio)
                # 26/10: só vira tela cheia depois que a 1ª linha do letreiro montou (antes: tela inteira preta com 1 palavra)
                m1 = re.search(r'<div class="ln[^"]*"[^>]*>(.*?)</div>', c.html, re.S)
                ids = re.findall(r'id="(c\d+-w\d+)"', m1.group(1)) if m1 else []
                js_c = ' '.join(c.js)
                tt = [float(x) for i in ids for x in re.findall(rf"palavra\('#{i}',([\d.]+)", js_c)]
                # 02/11 (usuário, caso real 0:04: "a animação corta NO MEIO, isso nunca deve ocorrer; cortes são antes ou no
                # final das frases e animações"): a troca pra tela cheia só acontece NO INÍCIO da cena. Só vira cena
                # cheia a que já monta a 1ª linha em até 0,5 s (senão a tela preta com 1 palavra de 26/10); a outra fica dividida
                if (tt and max(tt) > ini + 0.5 and not CHEIA_SEM_ESPERA) or t1 - ini < 1.5:
                    continue
                ta = ini
                fundo = ",backgroundColor:'#060606'" if GL_ESPERA_LINHA else ''   # HF: cena sem fundo próprio (o VOX já tem o papel)
                js.append(f"tl.set('#palco',{{height:1920}},{ta});tl.set('#{c.id}',{{height:1920{fundo}}},{ta});"
                          f"tl.set('#{c.id} .miolo',{{top:480}},{ta});tl.set('#divisoria',{{opacity:0}},{ta});"
                          f"tl.set('#palco',{{height:960}},{t1f});tl.set('#divisoria',{{opacity:1}},{t1f});")   # o fundo da cena cobre a pessoa (mexer na opacidade do vídeo apagava ele depois)
    js.append(f'window.__timelines["{COMPOSICAO}"] = tl;')
    titulo = (f'<div id="titulo" class="clip" data-start="0" data-duration="{round(fim_titulo - 0.01, 4)}" data-track-index="5">'
              + ''.join(f'<div class="tl">{esc(t)}</div>' for t in TITULO) + '</div>') if com_titulo else ''
    video_cheio = ''
    if TRES_MODOS and FORMATO == 'RL' and CENAS_PESSOA_GL and GNN:
        import pessoa_cheio
        pessoa_cheio.gerar(GNN, AQUI.name)
        video_cheio = (f'\n      <video id="pessoacheio" src="pessoa-cheio.mp4" muted playsinline data-start="0" data-duration="{DUR}" '
                       f'data-track-index="1" style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;opacity:0;z-index:6"></video>')
    pagina = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width={f['w']}, height={f['h']}" />
    <title>{esc(NOME)}</title>
    <style>{CSS}{css_formato(f)}</style>
  </head>
  <body>
    <div id="root" data-composition-id="{COMPOSICAO}" data-start="0" data-duration="{DUR}" data-fps="30" data-width="{f['w']}" data-height="{f['h']}">
      <video id="pessoa" src="{f['video']}" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>{video_cheio}
      <audio id="voz" src="voz.m4a" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
      <div id="palco">{''.join(secoes)}</div>
      <div id="divisoria"></div>
      {titulo}
    </div>
    <script src="vendor/gsap.min.js"></script>
    <script>
{chr(10).join(js)}
    </script>
  </body>
</html>
"""
    (AQUI / 'public/index.html').write_text(pagina, encoding='utf-8')

    linhas = [f'# {NOME} — roteiro de cenas (HyperFrames)', '',
              (f'Título na divisória de 0 a {fim_titulo:.2f} s: "{" / ".join(TITULO)}" (TikTok Sans 800).'
               if com_titulo else 'Sem título.'), '',
              '| cena | início | fim | fala | visual |', '|---|---|---|---|---|']
    for c, t1 in zip(CENAS, fim):
        linhas.append(f'| {c.id} | {c.t0:.2f} | {t1:.2f} | {c.fala} | {c.nome} |')
    (AQUI / 'roteiro.md').write_text('\n'.join(linhas) + '\n', encoding='utf-8')
    durs = [t1 - c.t0 for c, t1 in zip(CENAS, fim)]
    print(f'[{MODO} {FORMATO}] {len(CENAS)} cenas, média {sum(durs) / len(durs):.2f} s, mín {min(durs):.2f}, máx {max(durs):.2f}; '
          + (f'título até {fim_titulo}' if com_titulo else 'sem título'))
