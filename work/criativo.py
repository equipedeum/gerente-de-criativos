"""Renderizador do padrão CRIATIVOS (references/padrao-criativos.md). Cada vídeo tem um script de
configuração (work/cN/cN.py) que monta um dict CFG e chama `rodar(CFG)`.

CFG:
  id        'c2'                          pasta work/<id> com base.mov, voice.wav, words_cut.json, face_track.json, cuts.json
  ref       'referencias/<id>'      pasta do material real
  titulo    ['linha 1', 'linha 2']
  t_gancho  4.4     corte seco dividida -> tela cheia
  t_titulo  10.0    título some (fim da frase do gancho)
  gancho    [(t0, t1, arquivo, foco_vertical, recorte|None), ...]   área de baixo durante o gancho
  cutaways  [(t0, t1, arquivo, foco, recorte), ...]                  voltas à dividida no meio
  repl      {indice: (n_tokens, [novos])}  correções da transcrição
  frases    texto com '|' separando blocos e '\\n' entre linhas (1–4 palavras, por unidade de sentido)
  legenda_desde  palavra (normalizada) depois da qual a legenda começa (padrão: última do gancho)
  enquadro  função t -> (zoom, face_at) para a tela cheia; padrão (1.32, 0.33)
  saida     'saidas/criativo-2-v1.mp4'
  fonte169  True -> fonte 16:9 (work/<id>/base_h.mov 1920x1080, sem base.mov vertical). Opt-in; o caminho vertical não muda.
  enq169    'A' recorte 9:16 no rosto | 'B' faixa 16:9 inteira + fundo desfocado (título em cima, legenda embaixo) | 'C' dividida (painel liso com título em cima, pessoa 1080x960 embaixo)
            (RL; IN/GL usam o recorte A; YT = quadro 16:9 original inteiro)
  variante  'dividida' (padrão: gancho em tela dividida + cutaways) | 'inteira' (tela cheia do primeiro quadro ao fim, sem material embaixo)
  inserto   dict(t0=s, dur=s, rl='...RL.mp4', yt='...YT.mp4') — vídeo em tela cheia por cima da pessoa (corte seco),
            legenda continua por cima. RL usa o rl; YT usa o yt; IN/GL recortam o centro do rl. (plataforma, 13/10/2026)
"""
import json, math, os, re, subprocess, sys, functools
import numpy as np
import av
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
FF = open("ferramentas/ffmpeg_path.txt").read().strip()
FPS = 30
HOLD_FIM, FADE_FIM = 0.4, 0.24   # segura o último quadro 0,4 s depois da fala; fade preto nos últimos 0,24 s (já sem voz)
# formato: (largura, altura, divisória). Legenda fica em 63,4% da altura (1218/1920 na referência).
FORMATOS = {"RL": (1080, 1920, 960), "IN": (1080, 1350, 675), "GL": (1080, 1080, 600), "YT": (1920, 1080, 780), "YB": (960, 1080, 600), "GB": (1080, 830, 460), "RB": (1080, 1560, 800), "IB": (1080, 1100, 560)}   # RB/IB (22/10): área abaixo do banner no RL/IN   # YB (22/10): metade direita do YT com banner — vídeo cheio 960x1080, sem laterais desfocadas   # YT (bruto vertical): 9:16 centralizado + fundo desfocado; SPLIT = altura do título   # GL: faixa de cima maior p/ a cabeça caber
W, H, SPLIT = FORMATOS["RL"]
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
FONTE = "ferramentas/fontes/TikTokSans-Variable.ttf"

def cl(x): return max(0.0, min(1.0, x))
def ease(x): x = cl(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k
def norm(s): return re.sub(r"[^\wÀ-ÿ]", "", s).lower()

@functools.lru_cache(32)
def tk(size, wght):
    f = ImageFont.truetype(FONTE, int(size)); f.set_variation_by_axes([36, 100, wght, 0]); return f

def carregar_palavras(D, repl):
    W0 = json.load(open(f"{D}/words_cut.json")); out = []; i = 0
    while i < len(W0):
        if i in repl:
            n, novos = repl[i]; s0, e0 = W0[i]["s"], W0[i + n - 1]["e"]; dt = (e0 - s0) / max(1, len(novos))
            for j, p in enumerate(novos): out.append({"w": p, "s": round(s0 + j * dt, 3), "e": round(s0 + (j + 1) * dt, 3)})
            i += n; continue
        out.append(dict(W0[i])); i += 1
    return out

def montar_blocos(WORDS, frases, desde, t_end):
    lista = [p.strip() for ln in frases.strip().split("\n") for p in ln.split("|") if p.strip()]
    k = (desde if isinstance(desde, int) else next(i for i, w in enumerate(WORDS) if norm(w["w"]) == norm(desde))) + 1   # desde: palavra ou índice
    blocos = []
    for fr in lista:
        toks = fr.split(); ws = WORDS[k:k + len(toks)]
        for a, b in zip(toks, ws):
            assert norm(a) == norm(b["w"]), f"'{a}' != '{b['w']}' em {k} ({' '.join(x['w'] for x in WORDS[k-2:k+5])})"
        blocos.append({"txt": fr, "s": ws[0]["s"], "e": ws[-1]["e"], "ws": [w["s"] for w in ws]}); k += len(toks)
    assert k == len(WORDS), f"sobraram palavras: {' '.join(w['w'] for w in WORDS[k:])}"
    for a, b in zip(blocos, blocos[1:]): a["e"] = b["s"]
    blocos[-1]["e"] = t_end
    return blocos

def sombra_div():
    im = Image.new("RGBA", (W, 240), (0, 0, 0, 0))
    for y in range(240): ImageDraw.Draw(im).line((0, y, W, y), fill=(0, 0, 0, int(190 * (1 - y / 240) ** 1.4)))
    return im

def com_sombra(img, lay, alpha=0.6, blur=7, dy=3):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(lay.split()[3].point(lambda v: int(v * alpha)))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).transform(sh.size, Image.AFFINE, (1, 0, 0, 0, 1, -dy))
    img.alpha_composite(Image.alpha_composite(sh, lay))

# Título estilo EDITS (pedido de 29/09/2026): Helvetica Bold branca com traço preto leve, corpo grande, 2 linhas centradas.
# Opt-in: TITULO_EDITS = True (o render do básico liga). Emoji no fim da linha sai colorido (ver _emoji_img).
TITULO_EDITS = False
TIT_TAM = 80   # corpo máximo do título Edits (88 -> 80: "em alguns tá um pouquinho grande demais")
HELV_BOLD = "ferramentas/fontes/Inter-Bold.ttf"   # título estilo Edits (Inter Bold, OFL — parecida com Helvetica Bold)
def _e_emoji(ch): return ord(ch) >= 0x2600 or 0x231A <= ord(ch) <= 0x23FF   # ⌛⏰⏳ (bloco Misc Technical) também são emoji
# Emoji do título, nesta ordem: (1) PNG em ferramentas/emoji/<codepoint>.png (ex.: Twemoji, baixado na instalação);
# (2) fonte de emoji do sistema — Mac: Apple Color Emoji (o padrão preferido); Windows: Segoe UI Emoji; (3) sem emoji.
EMOJI_DIR = os.environ.get("EMOJI_DIR", "ferramentas/emoji")
EMOJI_FONTES = [("/System/Library/Fonts/Apple Color Emoji.ttc", 160), ("C:/Windows/Fonts/seguiemj.ttf", 109)]
@functools.lru_cache(256)
def _emoji_base(ch):
    p = f"{EMOJI_DIR}/{ord(ch):x}.png"
    if os.path.exists(p): return Image.open(p).convert("RGBA")
    for arq, tam in EMOJI_FONTES:   # Apple Color Emoji só desenha em tamanhos fixos (160 é o maior)
        if not os.path.exists(arq): continue
        try:
            ef = ImageFont.truetype(arq, tam); im = Image.new("RGBA", (tam * 2, tam * 2), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((tam // 4, tam // 4), ch, font=ef, embedded_color=True)
            bb = im.getbbox()
            if bb: return im.crop(bb)
        except OSError: pass
    return None
def _apple(ch, tam):
    b = _emoji_base(ch)
    return b.resize((int(tam * 1.12),) * 2, Image.LANCZOS) if b else None

def titulo_edits(img, linhas, yc=None):
    linhas = [ln.replace("\ufe0f", "") for ln in linhas]   # 19/10: o seletor invisível do ⚠️ (U+FE0F) contava como 2º emoji e descentralizava a linha
    tam = TIT_TAM; larg_max = W - 200   # 23/10 (usuário, caso real): título a ≥ 100 px de cada lateral (antes 45 px; rompia a margem segura)
    def medir(f, ln):
        tot = 0.0
        for ch in ln: tot += ((int(f.size * 1.12) if _apple(ch, f.size) else 0) if _e_emoji(ch) else f.getlength(ch))
        return tot
    while tam > 50:
        f = ImageFont.truetype(HELV_BOLD, tam)
        if all(medir(f, ln) <= larg_max for ln in linhas): break
        tam -= 4
    f = ImageFont.truetype(HELV_BOLD, tam)
    passo = int(tam * 1.13); y0 = (SPLIT if yc is None else yc) - passo * len(linhas) / 2 + passo / 2
    if LEG_FUNDO_CLARO:   # 18/11: título branco em cima de fundo claro (telão, papel) — decide 1 vez por formato
        k = ("tit", FORMATO_ATUAL)
        if k not in _CLARO_BLOCO:
            fx = img.crop((int(W * 0.12), max(0, int(y0 - passo * 0.6)), int(W * 0.88), min(H, int(y0 + passo * (len(linhas) - 0.4))))).convert("L")
            _CLARO_BLOCO[k] = float(np.asarray(fx, float).mean()) > 150
        # 19/11 (usuário: "faixa preta ridícula atrás do título"): NADA de faixa escura; o reforço é só na própria letra
    tit_forte = LEG_FUNDO_CLARO and _CLARO_BLOCO.get(("tit", FORMATO_ATUAL), False)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i, ln in enumerate(linhas):
        # 26/10 (usuário, caso real: "não ficou centralizado linha 1 e 2"): cada linha é desenhada à parte e centrada pelo
        # que aparece de fato (bbox dos pixels) — a medida da fonte + a folga do PNG do emoji deslocavam a linha
        l2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(l2)
        x = (W - medir(f, ln)) / 2; yc = y0 + i * passo
        for ch in ln:
            if _e_emoji(ch):
                ap = _apple(ch, tam)
                if ap: l2.alpha_composite(ap, (int(x), int(yc - ap.height / 2))); x += ap.width
            else: d.text((x, yc), ch, font=f, fill=WHITE, anchor="lm", stroke_width=3 if tit_forte else 2, stroke_fill=(0, 0, 0)); x += f.getlength(ch)
        bb = l2.getbbox()
        if bb: lay.alpha_composite(l2.crop(bb), (int(round((W - (bb[2] - bb[0])) / 2)), bb[1]))
    com_sombra(img, lay, *((1.0, 6, 3) if tit_forte else (0.35, 5, 2)))

def titulo(img, linhas, yc=None):
    if TITULO_EDITS: return titulo_edits(img, linhas, yc)
    f = tk(64, 700); asc, desc = f.getmetrics()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    passo = 70; y0 = SPLIT - passo * len(linhas) / 2 + 5     # referência: linhas em 875 e 945 p/ 2 linhas
    for i, ln in enumerate(linhas):
        d.text(((W - f.getlength(ln)) / 2, y0 + i * passo + asc - 6), ln, font=f, fill=WHITE, anchor="ls")
    com_sombra(img, lay)

LEG_OVERRIDE = None   # (corpo, baseline em px) — usado pelas variantes 16:9 B/C

# Legenda "serif keyword" (teste de 19/10/2026, inspirada no mg-cap-emphasis do 21st.dev): a palavra-chave de cada bloco
# sai em Instrument Serif itálica, maior e colorida, e "acende" quando é falada; o resto segue na fonte da legenda.
# Opt-in no cfg: leg_estilo="serif" (+ leg_cor_destaque=(r,g,b)). Palavra-chave: a marcada com *asteriscos* em `frases`,
# senão a mais longa que não seja palavra de ligação (≥ 5 letras); bloco sem candidata fica sem destaque.
LEG_ESTILO = None; LEG_CHAVE = True; LEG_ESTATICA = False; LEG_SOMBRA = (0.6, 7, 2); LEG_COR = (0, 165, 97)   # #00A561 (cor escolhida pelo usuário no 21st.dev)
SERIF_IT = "ferramentas/fontes/instrument-serif/InstrumentSerif-Italic.ttf"
_LIGACAO = set("aquele aquela aquilo porque quando sobre entre depois antes ainda então mesmo também muito minha nossa vocês dessa desse nessa nesse essas esses isso esse essa está estão você para pelo pela com sem mais menos cada todo toda todos todas onde como".split())

def juntar_2linhas(blocos, max_linha=26, max_total=50):
    """Estilo serif (19/10, usuário: "pra ficar legal nesse estilo tem que ter 2 linhas — nesse estilo pode quebrar a
    regra"): junta os blocos de 1–4 palavras em telas de até 2 linhas. Cada frase (até . ? !) é dividida em telas
    escolhendo os cortes de menor custo: poucas telas, corte de preferência depois de vírgula, telas equilibradas.
    A quebra de linha cai sempre entre blocos (unidade de sentido), na posição mais equilibrada que caiba."""
    def L(bs): return len(" ".join(b["txt"] for b in bs))
    def linhas_de(bs):
        if len(bs) == 1 or L(bs) <= max_linha: return [" ".join(b["txt"] for b in bs)]
        ks = [k for k in range(1, len(bs)) if L(bs[:k]) <= max_linha and L(bs[k:]) <= max_linha] or list(range(1, len(bs)))
        k = min(ks, key=lambda j: abs(L(bs[:j]) - L(bs[j:])))
        return [" ".join(b["txt"] for b in bs[:k]), " ".join(b["txt"] for b in bs[k:])]
    def cabe(bs): return L(bs) <= max_total and all(len(l) <= max_linha + 4 for l in linhas_de(bs))
    frases, cur = [], []
    for b in blocos:
        cur.append(b)
        if re.search(r"[.?!…]$", b["txt"].strip()): frases.append(cur); cur = []
    if cur: frases.append(cur)
    out = []
    for fr in frases:
        n = len(fr); best = [(0, None)] + [(1e9, None)] * n   # best[j]: custo pra cobrir fr[:j]
        for j in range(1, n + 1):
            for i in range(j):
                seg = fr[i:j]
                if len(seg) > 1 and not cabe(seg): continue
                fim_fraco = j < n and not seg[-1]["txt"].rstrip().endswith((",", ";", ":"))
                custo = (best[i][0] + 100 + (35 if fim_fraco else 0) + (15 if fim_fraco and len(seg[-1]["txt"]) <= 10 else 0)   # tela que termina num pedaço curto sem pontuação ("e já está") fica pendurada
                         + abs(L(seg) - 34) * 0.5)
                if custo < best[j][0]: best[j] = (custo, i)
        cortes, j = [], n
        while j > 0: i = best[j][1]; cortes.append((i, j)); j = i
        for i, j in reversed(cortes):
            seg = fr[i:j]
            out.append({"txt": "\n".join(linhas_de(seg)), "s": seg[0]["s"], "e": seg[-1]["e"], "ws": [w for b in seg for w in b["ws"]]})
    return out

def _chave(toks):
    for i, tk_ in enumerate(toks):
        if tk_.startswith("*"): return i
    cand = [(len(norm(x)), i) for i, x in enumerate(toks) if len(norm(x)) >= 5 and norm(x) not in _LIGACAO]
    return max(cand)[1] if cand else None

def legenda_serif(img, b, t, corpo, yb):
    linhas_txt = b["txt"].split("\n")
    toks, lin = [], []
    for li, ln in enumerate(linhas_txt):
        for x in ln.split(): toks.append(x); lin.append(li)
    ultima = [i for i in range(len(toks)) if lin[i] == lin[-1]]   # palavra-chave de preferência na última linha (fecha a frase)
    ki = next((i for i, x in enumerate(toks) if x.startswith("*")), None)
    if not LEG_CHAVE: ki = -1   # 19/10: "sem mudar a fonte, só o efeito de entrada" — sem palavra-chave em serifa/verde
    elif ki is None:
        k2 = _chave([toks[i] for i in ultima]); ki = ultima[k2] if k2 is not None else _chave(toks)
    toks = [x.strip("*") for x in toks]
    def fontes(c): return tk(c, 650), ImageFont.truetype(SERIF_IT, int(c * 1.55))
    c = corpo
    while True:
        fs, fz = fontes(c); sp = fs.getlength(" ")
        ls = [(fz if i == ki else fs).getlength(x) for i, x in enumerate(toks)]
        tots = [sum(ls[i] for i in range(len(toks)) if lin[i] == li) + sp * (lin.count(li) - 1) for li in range(len(linhas_txt))]
        if max(tots) <= W - 200 or c <= 40: break   # 25/10: legenda a ≥ 100 px de cada lateral (revisão geral achou linhas a 20–30 px)
        c -= 2
    passo = round(c * 1.32); nl = len(linhas_txt)
    xs_lin = [(W - tt) / 2 for tt in tots]; ys_lin = [round(yb) - (nl - 1 - li) * passo for li in range(nl)]   # última linha na altura de sempre
    pos, cx = [], {}
    for i in range(len(toks)):
        li = lin[i]; x_ = cx.get(li, xs_lin[li]); pos.append((x_, ys_lin[li])); cx[li] = x_ + ls[i] + sp
    # animação igual à do mg-cap-emphasis (vista no preview do 21st.dev em 19/10): cada palavra entra quando é falada
    # (sobe 22 px + fade em 0,2 s, posições reservadas); a palavra-chave entra BRANCA na fonte da legenda e, 0,25 s depois,
    # vira serifa itálica na cor de destaque (crossfade de 0,35 s, leve crescimento) com brilho suave da mesma cor.
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow); tem_glow = False
    for i, (tok, lw) in enumerate(zip(toks, ls)):
        x, y0 = pos[i]
        t0 = b["ws"][i] - 0.08 if i else min(b["ws"][0] - 0.08, b["s"])   # 1ª palavra junto com o bloco
        u = 1.0 if LEG_ESTATICA else ease((t - t0) / 0.2)   # 29/10 leg_estatica: a frase inteira aparece de uma vez, sem animação
        if u <= 0: continue
        a_ = int(255 * u); dy = round((1 - u) * 22)
        if i == ki:
            v = ease((t - t0 - 0.25) / 0.35)                                   # troca pra serifa
            if v < 1:   # versão "normal" (branca, fonte da legenda), some enquanto a serifa aparece
                xs = x + (lw - fs.getlength(tok)) / 2
                d.text((xs, y0 + dy), tok, font=fs, fill=WHITE[:3] + (round(a_ * (1 - v)),), anchor="ls")
            if v > 0:
                zf = ImageFont.truetype(SERIF_IT, max(8, int(fz.size * lerp(0.92, 1.0, v))))
                xw = x + (lw - zf.getlength(tok)) / 2; ca = LEG_COR + (round(a_ * v),)
                d.text((xw, y0 + 5 + dy), tok, font=zf, fill=ca, anchor="ls", stroke_width=1, stroke_fill=ca)   # traço de 1 px: a Instrument Serif é fina e falhava no celular
                dg.text((xw, y0 + 5 + dy), tok, font=zf, fill=LEG_COR + (round(200 * v),), anchor="ls", stroke_width=6, stroke_fill=LEG_COR + (round(200 * v),))
                tem_glow = True
        else:
            d.text((x, y0 + dy), tok, font=fs, fill=WHITE[:3] + (a_,), anchor="ls",
                   stroke_width=LEG_TRACO, stroke_fill=(0, 0, 0, round(a_ * 0.85)))
    if tem_glow: img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(16)))   # brilho suave atrás da palavra-chave
    com_sombra(img, lay, *LEG_SOMBRA)   # (alpha, blur, dy); um teste de 19/10 usou sombra mais forte na própria letra

# Legenda/título sobre fundo claro ou carregado (18–19/11/2026). Opt-in no cfg: leg_fundo_claro=True.
# REGRA do usuário (19/11): NUNCA faixa/tarja escura atrás do texto ("faixa preta ridícula"). O reforço é só na letra:
# contorno escuro fino (3 px) + sombra forte. Decidido no 1º quadro de cada bloco, pra não piscar.
LEG_FUNDO_CLARO = False; _CLARO_BLOCO = {}; LEG_TRACO = 0   # LEG_TRACO: contorno das palavras da legenda animada (só fundo claro)
def _fundo_claro(img, b, yb):
    k = (FORMATO_ATUAL, b["s"])
    if k not in _CLARO_BLOCO:
        y0 = max(0, int(yb) - 110); y1 = min(H, int(yb) + 25)
        _a = np.asarray(img.crop((int(W * 0.15), y0, int(W * 0.85), y1)).convert("L"), float)
        # fundo claro (papel, telão branco) OU carregado (tela de celular/computador com texto e ícones: muito contraste)
        _CLARO_BLOCO[k] = float(_a.mean()) > 165 or (float(_a.std()) > 55 and float(np.percentile(_a, 90)) > 170)
    return _CLARO_BLOCO[k]

def legenda(img, blocos, t, forte=False):   # forte: contorno preto (sobre fundo claro, ex.: inserto da plataforma)
    b = next((x for x in blocos if x["s"] <= t < x["e"]), None)
    if not b: return
    claro = False
    if LEG_FUNDO_CLARO and not forte:
        _tam, _yb = LEGENDA_FMT.get(FORMATO_ATUAL, (51, 0.634))
        claro = _fundo_claro(img, b, LEG_OVERRIDE[1] if LEG_OVERRIDE else H * _yb)
        if claro and LEG_ESTILO == "serif": forte = True   # animada: o forte é sombra carregada + contorno na letra
    if LEG_ESTILO == "serif":
        tam, ybase = LEGENDA_FMT.get(FORMATO_ATUAL, (51, 0.634))
        yb = next((y for a, c, y in b.get("faixas", []) if a <= t < c), None) or (LEG_OVERRIDE[1] if LEG_OVERRIDE else H * ybase)
        if forte:   # sobre inserto (ex.: trechos do evento, 21/10): mesmo estilo, sombra mais forte na própria letra
            global LEG_SOMBRA, LEG_TRACO
            antes = LEG_SOMBRA, LEG_TRACO; LEG_SOMBRA = (1.0, 5, 3); LEG_TRACO = 3 if claro else 0   # 19/11: fundo claro = contorno fino (sem faixa)
            try: return legenda_serif(img, b, t, LEG_OVERRIDE[0] if LEG_OVERRIDE else tam, yb)
            finally: LEG_SOMBRA, LEG_TRACO = antes
        return legenda_serif(img, b, t, LEG_OVERRIDE[0] if LEG_OVERRIDE else tam, yb)
    tam, ybase = LEGENDA_FMT.get(FORMATO_ATUAL, (51, 0.634))
    f = tk(LEG_OVERRIDE[0] if LEG_OVERRIDE else tam, 650)
    if LEG_OVERRIDE:   # nunca passar das margens (60 px de cada lado)
        c = LEG_OVERRIDE[0]
        while f.getlength(b["txt"]) > W - 200 and c > 44: c -= 2; f = tk(c, 650)   # 25/10: ≥ 100 px de cada lateral
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    yb = next((y for a, c, y in b.get("faixas", []) if a <= t < c), None)   # IN/GL da fonte 16:9 A: desce abaixo do queixo nos punch-ins
    yb = yb or (LEG_OVERRIDE[1] if LEG_OVERRIDE else H * ybase)   # "y" por bloco: IN/GL da fonte 16:9 A desviam do queixo nos punch-ins
    x0 = (W - f.getlength(b["txt"])) / 2
    if forte:   # inserto da plataforma (cola 13/10): tarja escura semitransparente atrás, sem contorno carregado
        l, tp, r, bt = d.textbbox((x0, round(yb)), b["txt"], font=f, anchor="ls")
        tj = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(tj).rounded_rectangle((l - 26, tp - 18, r + 26, bt + 20), radius=18, fill=(0, 0, 0, 165))
        img.alpha_composite(tj)
    if claro:   # fundo claro/carregado (opt-in): mesma legenda simples, com contorno escuro fino e sombra forte (sem tarja)
        d.text((x0, round(yb)), b["txt"], font=f, fill=WHITE, anchor="ls", stroke_width=3, stroke_fill=(0, 0, 0, 215))
        com_sombra(img, lay, 1.0, 5, 3); return
    d.text((x0, round(yb)), b["txt"], font=f, fill=WHITE, anchor="ls")
    com_sombra(img, lay, 0.55, 6, 2)

def cortes_visuais(D, lim=12.0):
    """Cortes do tratado (diferença média de luma em 96x54 > lim), em s; cache em <D>/cortes_visuais.json."""
    cache = f"{D}/cortes_visuais.json"
    if os.path.exists(cache): return json.load(open(cache))
    c = av.open(f"{D}/base_h.mov" if os.path.exists(f"{D}/base_h.mov") else f"{D}/base.mov"); v = c.streams.video[0]; v.thread_type = "AUTO"
    prev = None; out = []
    for n, fr in enumerate(c.decode(v)):
        a = np.asarray(fr.to_image().resize((96, 54)).convert("L"), float)
        if prev is not None and np.abs(a - prev).mean() > lim: out.append(round(float(fr.time) if fr.time is not None else n / FPS, 3))   # 08/11: tempo real (fonte 60 fps marcava o dobro)
        prev = a
    c.close(); json.dump(out, open(cache, "w")); return out

def cobrir(im, w, h, foco=0.5, push=1.0):
    k = max(w / im.width, h / im.height) * push
    cw, ch = w / k, h / k
    left = (im.width - cw) / 2; top = (im.height - ch) * foco
    return im.crop((int(left), int(top), int(left + cw), int(top + ch))).resize((w, h), Image.LANCZOS)

class Inserto:
    """Lê os quadros de um vídeo de inserto em ordem (render) ou com reabertura se voltar no tempo (stills)."""
    def __init__(self, path): self.path = path; self.c = None; self.n = -1; self.img = None
    def _abrir(self):
        if self.c: self.c.close()
        self.c = av.open(self.path); v = self.c.streams.video[0]; v.thread_type = "AUTO"
        self.rate = float(v.average_rate or 30); self.it = self.c.decode(v); self.n = -1; self.img = None
    def quadro(self, dt):
        if self.c is None: self._abrir()
        k = int(dt * self.rate + 1e-6)
        if k < self.n: self._abrir()
        while self.n < k:
            try: self.img = next(self.it).to_image(); self.n += 1
            except StopIteration: break   # passou do fim: segura o último quadro
        return self.img

# tela cheia por formato: (multiplicador do zoom, face_at). Quadro mais baixo pede menos zoom p/ o queixo não bater na legenda.
LEGENDA_FMT = {"YT": (62, 0.86)}     # (corpo, baseline em % da altura); os demais formatos usam 51 px a 63,4 %
FORMATO_ATUAL = "RL"
AJUSTE = {"RL": (1.0, None, 0.44, 0), "IN": (0.95, 0.34, 0.47, 200), "GL": (0.85, 0.34, 0.50, 120), "YT": (1.0, 0.50, 0.50, 0), "YB": (0.85, 0.40, 0.50, 0), "GB": (0.80, 0.32, 0.50, 0), "RB": (1.0, 0.22, 0.50, 0), "IB": (0.85, 0.27, 0.50, 0)}   # (zoom x, face_at cheia, face_at dividida, recuo do material no cutaway p/ a legenda cair em faixa preta)

def rodar_formatos(CFG):
    """CLI: `--formatos IN,GL [--stills t,t]` ou `--stills t,t` (RL) ou `--blocos` ou nada (RL)."""
    argv = sys.argv[1:]; fmts = ["RL"]
    if argv[:1] == ["--formatos"]:
        fmts = argv[1].split(","); sys.argv = [sys.argv[0]] + argv[2:]
    for f in fmts: rodar(CFG, f)

def rodar(CFG, formato="RL"):
    global W, H, SPLIT, FORMATO_ATUAL, LEG_OVERRIDE, LEG_ESTILO, LEG_COR, LEG_CHAVE, LEG_ESTATICA, LEG_FUNDO_CLARO
    FORMATO_ATUAL = formato; LEG_OVERRIDE = None
    LEG_FUNDO_CLARO = bool(CFG.get("leg_fundo_claro"))   # 18/11: opt-in, ver _fundo_claro()
    LEG_ESTILO = CFG.get("leg_estilo"); LEG_CHAVE = CFG.get("leg_chave", True); LEG_COR = tuple(CFG.get("leg_cor_destaque", (0, 165, 97)))
    LEG_ESTATICA = CFG.get("leg_estatica", False)   # 29/10 (reportagem NSC): legenda simples SEM animação
    if formato != "RL" and CFG.get("titulo_fin") and formato in CFG.get("titulo_fin_em", ("YT",)): CFG = {**CFG, "titulo": CFG["titulo_fin"]}   # finais: quebra/emoji própria (t2, 13/10: emoji longe da haste)
    W, H, SPLIT = FORMATOS[formato]; SOMBRA_DIV = sombra_div()
    kz, fa_fmt, fa_div, recuo = AJUSTE[formato]
    D = f"work/{CFG['id']}"; REF = CFG["ref"]
    WORDS = carregar_palavras(D, CFG.get("repl", {}))
    # FIM (padrão do lote, 13/10/2026 — caso real "cortou a última palavra"): a fala vai até o fim do áudio do tratado
    # (o whisper marca o fim da última palavra cedo); segura o último quadro HOLD_FIM s depois e só então escurece
    # (fade de imagem FADE_FIM s, todo depois da fala). Áudio sem fade, completado com silêncio até o fim.
    FALA_FIM = min(json.load(open(f"{D}/cuts.json"))["total"], WORDS[-1]["e"] + 0.6)
    T_END = round(FALA_FIM + HOLD_FIM, 3); T_FADE = T_END - FADE_FIM
    # 08/11 (varredura): índice, não a palavra — com a palavra, o montar_blocos pegava a 1ª vez que ela aparecia no vídeo
    desde = CFG.get("legenda_desde")
    if desde is None: desde = next(i for i, w in enumerate(WORDS) if w["s"] >= CFG["t_titulo"]) - 1
    BLOCOS = montar_blocos(WORDS, CFG["frases"], desde, T_END)
    if CFG.get("leg_estilo") == "serif": BLOCOS = juntar_2linhas(BLOCOS)
    enq = CFG.get("enquadro", lambda t: (1.32, 0.33))
    # 26/10/2026 (regra do usuário): a imagem nunca fica mais de 4 s parada — zoom leve contínuo (entra 3,5 s, sai 3,5 s,
    # +0 a +5 %) por cima do enquadramento do vídeo; os punch-ins/cortes continuam valendo. cfg mov_amp=0 desliga.
    # 26/10 v2 (usuário: "o 256 tá igual os outros" — 5 % contínuo não aparecia): agora são PLANOS que trocam no começo
    # de uma frase da legenda (no mínimo a cada 2,5 s, no máximo 4 s), alternando aberto (1,00) e fechado (+14 %), e
    # dentro de cada plano a câmera empurra devagar (+4 %). cfg mov_amp=0 desliga.
    _enq0, _amp = enq, CFG.get("mov_amp", 0.14)
    TIT_FIM = CFG.get("t_titulo") if CFG.get("titulo") else 0.0
    _cortes = [float(TIT_FIM or 0.0)]
    # 07/11/2026 (usuário, caso real): no gancho, "a cada frase, dar um corte e zoom in leve, deixa uma frase, depois volta".
    # cfg planos_gancho = [t, t, ...] (começo de cada frase do gancho depois do título): corte seco alternando aberto e
    # fechado leve (planos_amp, padrão +10 %, empurrão 2 %); depois do último, segue a regra automática por bloco.
    _PG = sorted(float(x) for x in CFG.get("planos_gancho", []) if x > _cortes[0]); _cortes += _PG
    # 09/11 (varredura; regra 02/11 "corte nunca no meio"): o corte extra num trecho longo sem início de bloco caía em
    # tempo fixo (+3,5 s), às vezes no meio de uma palavra; agora encosta no começo de palavra mais próximo (±1 s).
    _ini_pal = np.array([w["s"] for w in WORDS], float)
    def _encosta(t, ate):
        if not len(_ini_pal): return t
        j = int(np.argmin(np.abs(_ini_pal - t)))
        ok = abs(_ini_pal[j] - t) <= 1.0 and _ini_pal[j] - _cortes[-1] >= 2.5 and _ini_pal[j] < ate
        return float(_ini_pal[j]) if ok else t
    # 12/11/2026 (usuário, num vídeo: "tem alguns zooms no meio da fala, meio da frase, aí fica feio"): cfg planos_por_frase=True
    # troca o plano SÓ no começo de uma frase (bloco depois de . ? !), sem os cortes de enchimento a cada 3,5 s — dentro do
    # plano a câmera continua empurrando devagar (a imagem não fica parada). Opt-in; sem a chave nada muda.
    _PPF = bool(CFG.get("planos_por_frase"))
    for _i, _b in enumerate(BLOCOS):
        if _PG and _b["s"] <= _PG[-1] + 1.0: continue
        if _PPF:
            if _i and BLOCOS[_i - 1]["txt"].rstrip().endswith((".", "?", "!")) and _b["s"] - _cortes[-1] >= 2.5: _cortes.append(_b["s"])
            continue
        while _b["s"] - _cortes[-1] > 4.0: _cortes.append(_encosta(_cortes[-1] + 3.5, _b["s"]))
        if _b["s"] - _cortes[-1] >= 2.5: _cortes.append(_b["s"])
    while not _PPF and T_END - _cortes[-1] > 4.0: _cortes.append(_cortes[-1] + 3.5)
    _cortes = np.array([0.0] + _cortes if _cortes[0] > 0 else _cortes)
    # 26/10 v3 (usuário): a gravação tem "dois momentos" — câmera ABERTA no começo e no fim (aí pode brincar mais: planos
    # +0/+24 % e empurrão de 6 %) e câmera já em zoom no MEIO (aí só zooms leves: +0/+10 % e empurrão de 3 %). O momento
    # sai do tamanho do rosto no quadro (face_track): rosto > 1,25x o tamanho do plano aberto = meio com zoom.
    _zoom_cache = {}
    def _no_zoom(t):
        if "f" not in _zoom_cache:
            ws = np.array([f["w"] for f in FACE], float); base_w = float(np.percentile(ws, 20))
            _zoom_cache["f"] = (np.array([f["t"] for f in FACE], float), ws > 1.25 * base_w)
        tt, zz = _zoom_cache["f"]; i = int(np.clip(np.searchsorted(tt, t), 0, len(tt) - 1)); return bool(zz[i])
    def _mov(t):
        k = int(np.searchsorted(_cortes, t, side="right") - 1); a0 = _cortes[k]
        a1 = _cortes[k + 1] if k + 1 < len(_cortes) else T_END
        if TIT_FIM and t < TIT_FIM: return 1.0   # com o título na tela, o quadro fica parado (o zoom levava o título pra boca)
        meio = _no_zoom(a0)
        amp, emp = (min(_amp, 0.06), 0.03) if meio else (max(_amp, 0.18), 0.05)   # meio: até ~10 % no total
        if _PG and a0 <= _PG[-1]: amp, emp = CFG.get("planos_amp", 0.10), 0.02     # gancho com planos por frase: zoom leve
        base = 1 + (amp if k % 2 else 0.0)
        return base * (1 + emp * min(1.0, (t - a0) / max(0.5, a1 - a0)))
    MOV = _mov if _amp else (lambda t: 1.0)   # aplicado depois do limite do recorte (no 16:9 o zoom do enquadro já está no teto)

    FACE = json.load(open(f"{D}/face_track.json"))
    ft = np.array([f["t"] for f in FACE], float)
    def sm(k, n=5):
        v = np.array([f[k] for f in FACE], float)
        med = np.array([np.median(v[max(0, i - 4):i + 5]) for i in range(len(v))])
        if CFG.get("camera_suave", True):
            # 02/11/2026 (usuário, caso real: "trackeamento muito abrupto… quero algo mais delicado, que se mexa aos poucos,
            # não uma câmera que se move o tempo todo"): câmera "preguiçosa" — fica parada enquanto o rosto está dentro de
            # uma zona morta e só então vai atrás dele devagar (constante de ~2,5 s), depois média longa (~3 s).
            dz = 0.035 * max(1.0, float(np.max(v)))
            cortes = cortes_visuais(D); kc = 0   # no corte seco a câmera já começa no lugar novo (sem panorâmica lenta)
            cam = np.empty_like(med); c = med[0]
            for i, x in enumerate(med):
                pulou = False
                while kc < len(cortes) and cortes[kc] <= ft[i]: kc += 1; pulou = True
                if pulou: c = float(np.median(med[i:i + 6]))
                elif abs(x - c) > dz: c += (x - c) * 0.04
                cam[i] = c
            n = 15; out = np.empty_like(cam); lim = [0] + [int(np.searchsorted(ft, x)) for x in cortes] + [len(cam)]
            for a, b in zip(lim, lim[1:]):   # média longa só dentro de cada plano (não arrasta através do corte)
                if b > a: out[a:b] = np.convolve(np.pad(cam[a:b], (n, n), mode="edge"), np.ones(2 * n + 1) / (2 * n + 1), mode="valid")
            return out
        return np.convolve(np.pad(med, (n, n), mode="edge"), np.ones(2 * n + 1) / (2 * n + 1), mode="valid")
    cx, cy = sm("cx"), sm("cy")
    def face(t): return float(np.interp(t, ft, cx)), float(np.interp(t, ft, cy))

    F169 = bool(CFG.get("fonte169")); ENQ = CFG.get("enq169", "A") if (F169 and formato == "RL") else "A"
    if F169 and formato == "YT": ENQ = "YT"
    if F169 and ENQ == "B": LEG_OVERRIDE = (56, 1440)
    if F169 and ENQ == "C": LEG_OVERRIDE = (64, 500)
    if F169 and ENQ == "A" and formato == "RL":   # recorte 9:16 amplia o rosto ~1,8x: legenda de 51 px fica pequena perto dele (piloto t1, 12/10) -> corpo maior e mais baixa (no peito)
        LEG_OVERRIDE = tuple(CFG.get("leg169", (66, 1260)))   # 1360 -> 1320 (OK do RL t1, 12/10) -> 1260 (t2, 13/10): ainda encostava no conector da haste do microfone
        # 09/11 (usuário: "tente manter dentro da margem de segurança"): baseline 1260 deixava o pé da letra ~25 px abaixo
        # da linha de 65 % -> base no máximo a linha menos o descendente da fonte
        _lim_rl = round(H * 0.65) - tk(LEG_OVERRIDE[0], 650).getmetrics()[1]
        if LEG_OVERRIDE[1] > _lim_rl and not CFG.get("leg_rl_fora_zona"):
            LEG_OVERRIDE = (LEG_OVERRIDE[0], _lim_rl)
    if not F169 and formato in CFG.get("leg_vert", {}):   # bruto vertical em selfie (selfie de evento): legenda maior e no peito, longe do queixo
        LEG_OVERRIDE = tuple(CFG["leg_vert"][formato])
    src_c = av.open(f"{D}/base_h.mov" if F169 else f"{D}/base.mov"); VS = src_c.streams.video[0]; VS.thread_type = "AUTO"
    SW, SH = VS.width, VS.height
    RATE = VS.average_rate or FPS; DT = 1 / float(RATE)   # saída na taxa da fonte (29,97 -> 30000/1001): 30 fixo encurtava/adiantava 0,1%
    NFR = int(round(T_END / DT))
    def frames():   # quadros da fonte até T_END; se a fonte acabar antes, repete o último (segura o fim)
        n, last = 0, None
        for fr in src_c.decode(VS):
            if n >= NFR: return
            last = fr.to_image(); yield last; n += 1
        while last is not None and n < NFR: yield last; n += 1

    def presenter(src, t, rh, zoom, face_at):
        cw = SW / zoom; ch = cw * rh / W
        if cw > SW: cw = SW; ch = cw * rh / W          # zoom < 1 (IN/GL) nunca pode pedir mais largura que o quadro: dava borda preta (18/09)
        if ch > SH: ch = SH; cw = ch * W / rh
        if rh == H: cw /= MOV(t); ch /= MOV(t)   # 26/10: planos aberto/fechado + empurrão (só na imagem cheia)
        fx, fy = face(t)
        PX = CFG.get("puxa_rl")   # 14/10 (caso real): no começo, puxa o recorte do RL pro lado (ex.: mostrar o celular na mão); dict(ate=s, volta=s, cx=px fonte)
        if PX and formato == "RL" and t < PX["ate"] + PX["volta"]:
            u = 0.0 if t <= PX["ate"] else (t - PX["ate"]) / PX["volta"]; u = u * u * (3 - 2 * u)
            fx = PX["cx"] * (1 - u) + fx * u
        left = max(0, min(SW - cw, fx - cw / 2)); top = max(0, min(SH - ch, fy - ch * face_at))
        RF = CFG.get("recorte_rl")   # opt-in (02/11/2026): cfg recorte_rl(t, left, top, cw, ch, face) -> (left, top, cw, ch) no RL cheio
        if RF and formato == "RL" and rh == H:   # (ex.: logo/hashtag gravados no topo da fonte: tirar o recorte de cima deles)
            left, top, cw, ch = RF(t, left, top, cw, ch, face)
        return src.crop((int(left), int(top), int(left + cw), int(top + ch))).resize((W, rh), Image.LANCZOS)

    # abre169 (opt-in por cfg, fonte 16:9): no começo do vídeo abre o recorte (mais largo, altura inteira) centrado em `cx`
    # pra caber algo ao lado do rosto (ex.: celular na mão, t1 12/10); faixas acima/abaixo = o próprio quadro desfocado.
    # dict(ate=s, volta=s, cx=px fonte, cw=px fonte). Até `ate` fica aberto; volta ao recorte normal com ease em `volta` s.
    AB = CFG.get("abre169") if F169 else None
    def peso_abre(t):
        if not AB or t >= AB["ate"] + AB["volta"]: return 0.0
        return 1.0 if t < AB["ate"] else 1.0 - ease((t - AB["ate"]) / AB["volta"])
    if AB:
        fys = [face(t)[1] for t in np.arange(0, AB["ate"], 0.1)]; AB_FY = float(np.median(fys))
    def presenter_abre(src, t, zoom, face_at, u):
        cw_n = SW / zoom; ch_n = cw_n * H / W
        if cw_n > SW: cw_n = SW; ch_n = cw_n * H / W
        if ch_n > SH: ch_n = SH; cw_n = ch_n * W / H
        cw_w = float(AB["cw"]); ch_w = SH
        if cw_w <= cw_n: return presenter(src, t, H, zoom, face_at)       # formato já é largo (GL): nada a abrir
        fx, fy = face(t)
        left_n = max(0, min(SW - cw_n, fx - cw_n / 2)); top_n = max(0, min(SH - ch_n, fy - ch_n * face_at))
        left_w = max(0, min(SW - cw_w, AB["cx"] - cw_w / 2))
        # faixa aberta posicionada pra o rosto cair na mesma altura do recorte normal (sem pulo na volta)
        y_face = (AB_FY - max(0, min(SH - ch_n, AB_FY - ch_n * face_at))) * H / ch_n
        h_w = ch_w * W / cw_w; y_w = max(0.0, min(H - h_w, y_face - AB_FY * W / cw_w))
        cw = lerp(cw_n, cw_w, u); ch = lerp(ch_n, ch_w, u); left = lerp(left_n, left_w, u); top = lerp(top_n, 0, u)
        dh = round(ch * W / cw); dy = round(lerp(0, y_w, u))
        fg = src.crop((int(left), int(top), int(left + cw), int(top + ch))).resize((W, dh), Image.LANCZOS)
        if dh >= H and dy == 0: return fg.crop((0, 0, W, H))
        bg = cobrir(src, W, H, 0.5).filter(ImageFilter.GaussianBlur(38)).point(lambda v: int(v * 0.55))
        bg.paste(fg, (0, dy)); return bg

    @functools.lru_cache(16)
    def img_ref(n): return Image.open(f"{REF}/{n}").convert("RGB")
    def clipe(img, t, lista, d=0):
        for s, e, nome, foco, rec in lista:
            if s <= t < e:
                im = img_ref(nome); im = im.crop(rec) if rec else im
                push = lerp(1.0, 1.04, (t - s) / max(0.4, e - s))
                img.paste(cobrir(im, W, H - SPLIT - d, foco, push), (0, SPLIT + d)); return

    def titulo_y():
        # título fora do rosto (pedido de 08/10): acima da cabeça se couber; senão na altura do peito, logo abaixo do queixo
        if not TITULO_EDITS or CFG.get("variante") != "inteira": return None
        if F169 and ENQ == "B": return 380
        if F169 and ENQ == "C": return 480
        if F169 and ENQ == "YT":   # quadro 16:9 original 1:1: acima da cabeça se couber, senão no peito, nunca no rosto (12/10)
            topo, queixo = 1e9, -1e9
            for t in np.arange(0, CFG["t_titulo"], 0.1):
                fx, fy = face(t); w = float(np.interp(t, ft, [f["w"] for f in FACE]))
                topo = min(topo, fy - 0.75 * w); queixo = max(queixo, fy + 0.62 * w)
            n = len(CFG["titulo"]); bloco = int(TIT_TAM * 1.13) * n + 20
            if topo - 40 >= bloco: return max(bloco / 2 + 40, topo + 20 - bloco / 2)
            y = min(H * 0.80 - bloco / 2, queixo + 40 + bloco / 2)
            return max(queixo + 10 + bloco / 2, y + CFG.get("tit169_dy_fin", -140))   # finais t2 (13/10): emoji encostava na haste -> sobe, sem passar do queixo
        FW = {f["t"]: f["w"] for f in FACE}; topo, queixo = 1e9, -1e9
        for t in np.arange(0, CFG["t_titulo"], 0.1):
            z, fa = enq(t); zoom = z * kz; fa = fa_fmt or fa
            cw = SW / zoom; ch = cw * H / W
            if formato == "YT": cw = SW / z; ch = cw * H / 608
            if cw > SW: cw = SW; ch = cw * H / W
            if ch > SH: ch = SH; cw = ch * W / H
            if formato != "YT": cw /= MOV(t); ch /= MOV(t)
            fx, fy = face(t); top = max(0, min(SH - ch, fy - ch * fa)); esc = (608 if formato == "YT" else W) / cw
            if F169 and formato == "YT" and SW != W: top, esc = 0, W / SW   # 11/11 (fonte 4K): YT é o quadro inteiro reduzido
            w = float(np.interp(t, ft, [f["w"] for f in FACE]))
            topo = min(topo, (fy - 0.75 * w - top) * esc); queixo = max(queixo, (fy + 0.62 * w - top) * esc)
        n = len(CFG["titulo"]); bloco = int(TIT_TAM * 1.13) * n + 20 if W >= 1080 else 200
        # 12/11 (usuário, 4K em plano aberto: "coloque o título também central, se não vai ficar fora da área de segurança"):
        # cfg titulo_no_peito=True pula o "acima da cabeça" (no plano aberto ele caía no topo, fora da zona segura). Opt-in.
        if topo - 40 >= bloco and not CFG.get("titulo_no_peito"): return max(bloco / 2 + 40, topo + 20 - bloco / 2)       # espaço em cima da cabeça
        y = min(H * 0.80 - bloco / 2, queixo + 40 + bloco / 2)                         # peito
        if F169 and ENQ == "A":   # RL, IN e GL — padrão da fonte 16:9 (t2, 13/10): no peito o emoji encostava na ponta da haste do microfone -> sobe 70 px, sem passar do queixo
            y = max(queixo + 10 + bloco / 2, y + (CFG.get("tit169_dy", -70) if formato == "RL" else CFG.get("tit169_dy_fin", -140)))
        if formato == "RL":   # 26/10 (usuário): título inteiro na zona segura de anúncio (base acima de 65 % da altura)
            y = min(y, H * 0.645 - bloco / 2)
        return y
    TIT_Y = titulo_y(); print("título y =", TIT_Y)

    # PADRÃO DA FONTE 16:9 (t2 v4, 13/10) — IN/GL da fonte 16:9 "A": o recorte já usa a altura inteira do quadro
    # (não dá pra tirar zoom sem letterbox, proibido), então nos punch-ins do tratado o queixo descia até a legenda
    # (63,4 % da altura). Regra: legenda NUNCA no rosto, topo do texto ≥ 40 px abaixo do queixo (face_track: cy + 0,62·w
    # no punch-in, que deixou a haste livre no GL; 0,70·w no plano normal, onde ele inclina a cabeça).
    # t14 (14/10): RL com punch-in forte (23-29 s) deixava a legenda no queixo -> cfg leg_punch_rl=True liga a mesma regra no RL
    RL_P = F169 and ENQ == "A" and formato == "RL" and CFG.get("leg_punch_rl")
    if F169 and ENQ == "A" and (formato in ("IN", "GL") or RL_P):
        cw_ = np.array([f["w"] for f in FACE], float); sw_ = np.convolve(np.pad(cw_, (5, 5), mode="edge"), np.ones(11) / 11, mode="valid")
        tam_ = LEGENDA_FMT.get(formato, (51, 0.634))[0]; base_n = round(H * LEGENDA_FMT.get(formato, (51, 0.634))[1])
        if RL_P: tam_, base_n = LEG_OVERRIDE[0], round(LEG_OVERRIDE[1])
        def queixo_out(t, k=0.62):
            zoom = enq(t)[0] * kz; fa = fa_fmt or enq(t)[1]
            cw = SW / zoom; ch = cw * H / W
            if cw > SW: cw = SW; ch = cw * H / W
            if ch > SH: ch = SH; cw = ch * W / H
            cw /= MOV(t); ch /= MOV(t)
            fx, fy = face(t); top = max(0, min(SH - ch, fy - ch * fa))
            return (fy + k * float(np.interp(t, ft, sw_)) - top) * H / ch
        f_ = tk(tam_, 650); topo_max = max(-f_.getbbox(b["txt"], anchor="ls")[1] for b in BLOCOS)
        # planos = trechos entre cortes do tratado. Plano em que o queixo pede descer em > 30 % dos quadros = punch-in:
        # o plano inteiro usa LEG_PUNCH (muda de altura junto com o corte). Nos demais planos, só o bloco que pedir desce
        # (queixo 0,70·w, cabeça inclinada) até a altura que precisa — troca na entrada do bloco, nunca no meio.
        ts = np.arange(0, T_END, 1 / FPS); need = np.array([queixo_out(t) + 40 + topo_max for t in ts])
        lim = [0.0] + [c for c in cortes_visuais(D) if 0 < c < T_END] + [T_END]
        punch = [(a, c) for a, c in zip(lim, lim[1:]) if c - a > 0.3 and (need[round(a * FPS):round(c * FPS)] > base_n).mean() > 0.30]
        for b in BLOCOS: b["faixas"] = []
        if punch:
            LEG_PUNCH = round(min(max(need[round(a * FPS):round(c * FPS)].max() for a, c in punch) + 12,   # +12: no GL (escala 1:1) o 0,62·w deixava ~38 px no pior quadro (t2 23 s)
                                  H - CFG.get("leg_punch_margem", {"IN": 150, "GL": 120, "RL": 300}[formato])))
            if formato == "RL":   # 26/10 (usuário: "nem A nem B, um meio termo"): no zoom a legenda fica no meio do caminho entre a
                LEG_PUNCH = round((LEG_PUNCH + base_n) / 2)   # altura que livra o queixo e a da zona segura (65 %)
            LEG_PUNCH = CFG.get("leg_punch", {}).get(formato, LEG_PUNCH)
            for b in BLOCOS: b["faixas"] += [(a, c, LEG_PUNCH) for a, c in punch]
            print(f"{formato}: punch-in -> legenda y={LEG_PUNCH} em {[(round(a,2), round(c,2)) for a, c in punch]} (normal {base_n})")
        for b in BLOCOS:
            tt = [t for t in np.arange(b["s"], b["e"], 1 / FPS) if not any(a <= t < c for a, c in punch)
                  and not any(abs(t - c) < 0.35 for c in lim[1:-1])]   # perto do corte o face_track suavizado ainda "carrega" o plano anterior
            if not tt: continue
            y = max(queixo_out(t, 0.70) for t in tt) + 40 - f_.getbbox(b["txt"], anchor="ls")[1]
            if y > base_n:
                y = round(min(y, H - 120)); b["faixas"].append((b["s"], b["e"], y))
                print(f"{formato}: bloco '{b['txt']}' {b['s']:.2f}-{b['e']:.2f} desce p/ y={y} (inclinado, sem corte)")
        if formato == "RL" and not CFG.get("leg_rl_fora_zona"):
            # 09/11 (usuário): no RL a legenda fica dentro da zona segura (pé da letra acima de 65 %); pode encostar no queixo,
            # mas nunca cobrir o rosto -> sobe até a zona segura, parando onde o topo do texto chegaria na boca (cy + 0,35·w)
            lim_ = round(H * 0.65) - f_.getmetrics()[1]
            for b in BLOCOS:
                nf = []
                for a, c, y in b["faixas"]:
                    if y > lim_:
                        tt = np.arange(max(a, b["s"]), min(c, b["e"]), 1 / FPS)
                        boca = max((queixo_out(t, 0.35) for t in tt), default=0) - f_.getbbox(b["txt"], anchor="ls")[1] + 10
                        y2 = round(min(y, max(lim_, boca)))
                        if y2 > lim_: print(f"RL: bloco '{b['txt']}' fica em y={y2} (zona segura = {lim_}) pra não cobrir a boca")
                        y = y2
                    nf.append((a, c, y))
                b["faixas"] = nf
    # opt-in (02/11/2026): cfg leg_y = {formato: [(t0, t1, baseline), ...]} força a altura da legenda num trecho
    # (ex.: texto já gravado na fonte embaixo -> recorte sem ele e legenda acima da cabeça). Vale antes das faixas automáticas.
    for a_, c_, y_ in CFG.get("leg_y", {}).get(formato, []):
        for b in BLOCOS: b["faixas"] = [(a_, c_, y_)] + b.get("faixas", [])

    # inserto único (`inserto`) ou vários (`insertos`, lista do mesmo dict — ex.: trechos do evento num lote de evento)
    INSS = ([CFG["inserto"]] if CFG.get("inserto") else []) + list(CFG.get("insertos", []))
    INS_RS = [Inserto(i["yt"] if formato == "YT" else i["rl"]) for i in INSS]
    def ins_em(t): return next((k for k, i in enumerate(INSS) if i["t0"] <= t < i["t0"] + i["dur"]), None)
    def em_ins(t): return ins_em(t) is not None
    def inserto(img, t):   # tela cheia por cima da pessoa, corte seco na entrada e na saída
        k = ins_em(t)
        if k is None: return
        q = INS_RS[k].quadro(t - INSS[k]["t0"])
        if q is None: return
        img.paste(q.convert("RGB") if q.size == (W, H) else cobrir(q.convert("RGB"), W, H, 0.5), (0, 0))

    def compose169(src, t, img):
        """Variantes B/C/YT para fonte 16:9 (1920x1080). A usa o caminho normal (presenter recorta 9:16 no rosto)."""
        fx, fy = face(t)
        if ENQ == "YT": img.paste(src.convert("RGB") if src.size == (W, H) else src.convert("RGB").resize((W, H), Image.LANCZOS), (0, 0))   # 11/11 (fonte 4K): colava o canto do 4K
        elif ENQ == "B":
            bg = cobrir(src, W, H, 0.5).filter(ImageFilter.GaussianBlur(38)).point(lambda v: int(v * 0.55))
            bg.paste(src.resize((W, 608), Image.LANCZOS), (0, (H - 608) // 2)); img.paste(bg, (0, 0))
        else:   # C: painel liso em cima, pessoa 1080x960 embaixo (recorte de altura inteira em volta do rosto)
            cw = SH * W / 960; left = max(0, min(SW - cw, fx - cw / 2))
            img.paste(Image.new("RGB", (W, 960), (14, 14, 14)), (0, 0))
            img.paste(src.crop((int(left), 0, int(left + cw), SH)).resize((W, 960), Image.LANCZOS), (0, 960))
        inserto(img, t)
        if t < CFG["t_titulo"]: titulo(img, CFG["titulo"], TIT_Y)
        else: legenda(img, BLOCOS, t, em_ins(t))
        if t > T_FADE:
            img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ease(min(1.0, (t - T_FADE) / FADE_FIM))))))   # Draw.rectangle em RGBA não mistura: era corte seco pro preto
        return img.convert("RGB")

    def compose(src, t):
        img = Image.new("RGBA", (W, H), (*BLACK, 255))
        inteira = CFG.get("variante", "dividida") == "inteira"
        if F169 and ENQ in ("B", "C", "YT"): return compose169(src, t, img)
        gancho = t < CFG["t_gancho"] and not inteira
        dividida = gancho or (not inteira and any(s <= t < e for s, e, *_ in CFG.get("cutaways", [])))
        if dividida:
            img.paste(presenter(src, t, SPLIT, 1.0, fa_div), (0, 0))
            clipe(img, t, CFG["gancho"]) if gancho else clipe(img, t, CFG["cutaways"], recuo)
        else:
            z, fa = enq(t)
            if formato == "YT" and not CFG.get("yt_desfocado"):   # bruto vertical em 16:9: recorte 16:9 cheio em volta do rosto
                pr = presenter(src, t, H, CFG.get("yt_zoom_cheio", 1.0), CFG.get("yt_rosto", 0.42))   # (REGRA: nunca área desfocada)
            elif formato == "YT":   # opt-in yt_desfocado=True: vídeo inteiro no centro (9:16) e fundo = o mesmo quadro desfocado
                yz = CFG.get("yt_zoom", 1.0); FWY = int(608 * yz)   # 21/10: zoom leve (ex.: 1,3) pra ocupar mais espaço, sem encher a tela
                ch = SW / z * H / 608 / yz; cw = ch * FWY / H
                if ch > SH: ch = SH; cw = ch * FWY / H
                if cw > SW: cw = SW; ch = cw * H / FWY
                fx, fy = face(t); left = max(0, min(SW - cw, fx - cw / 2)); top = max(0, min(SH - ch, fy - ch * fa))
                fg = src.crop((int(left), int(top), int(left + cw), int(top + ch))).resize((FWY, H), Image.LANCZOS)
                # fundo desfocado calculado em 1/8 do tamanho (21/10: em tamanho cheio o YT levava ~30 min por vídeo)
                bg = cobrir(src, W // 8, H // 8, 0.4).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR).point(lambda v: int(v * 0.62))
                pr = bg; pr.paste(fg, ((W - FWY) // 2, 0))
            elif peso_abre(t) > 0: pr = presenter_abre(src, t, z * kz, fa_fmt or fa, peso_abre(t))
            else: pr = presenter(src, t, H, z * kz, fa_fmt or fa)
            if any(a <= t < b for a, b in CFG.get("pb", [])): pr = pr.convert("L").convert("RGB")     # brincadeira em preto e branco (29/09)
            img.paste(pr, (0, 0))
        inserto(img, t)
        if t < CFG["t_titulo"]:
            if gancho:   # sombra no topo da área de baixo p/ o título não cair em fundo claro (manchete branca)
                img.alpha_composite(SOMBRA_DIV, (0, SPLIT))
            titulo(img, CFG["titulo"], TIT_Y)
        else:
            if dividida and not recuo: img.alpha_composite(SOMBRA_DIV, (0, SPLIT))   # RL: legenda cai sobre o material
            legenda(img, BLOCOS, t, em_ins(t))
        if t > T_FADE:
            img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * ease(min(1.0, (t - T_FADE) / FADE_FIM))))))   # Draw.rectangle em RGBA não mistura: era corte seco pro preto
        return img.convert("RGB")

    if sys.argv[1:2] == ["--stills"]:
        want = sorted(float(x) for x in sys.argv[2].split(",")); os.makedirs(f"{D}/prev", exist_ok=True); i = 0
        for n, src in enumerate(frames()):
            t = n * DT
            while i < len(want) and want[i] <= t + 1e-6:
                compose(src, t).save(f"{D}/prev/{formato}-t{want[i]:05.2f}.png"); i += 1
            if i >= len(want): break
        print("prévias:", i); return
    if sys.argv[1:2] == ["--blocos"]:
        for b in BLOCOS: print(f"{b['s']:6.2f}-{b['e']:6.2f}  {b['txt']}")
        return
    out = CFG["saida"] if formato == "RL" else CFG["saida"].replace(".mp4", f"-{formato}.mp4")
    p = subprocess.Popen([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(RATE), "-i", "-", "-i", f"{D}/voice.wav", "-af", "apad", "-t", f"{NFR * DT:.3f}",
                          # cor da pessoa intacta: RGB -> YUV na matriz BT.709 e marcado como 709 (sem isso o ffmpeg usava
                          # a 601 sem marca e o player, lendo como 709, deixava a pele ~6 níveis mais vermelha)
                          "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-colorspace", "bt709", "-color_primaries", "bt709",
                          "-color_trc", "bt709", "-color_range", "tv",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for n, src in enumerate(frames()):
        p.stdin.write(compose(src, n * DT).tobytes())
        if n % 600 == 0: print(n, flush=True)
    p.stdin.close()
    if p.wait():   # 08/11 (varredura): antes a falha do ffmpeg saía com código 0 e a fila achava que o vídeo existia
        sys.exit(f"ffmpeg falhou ({p.returncode}) em {out}: confira espaço em disco e o nome do arquivo")
    print("saída:", out)
