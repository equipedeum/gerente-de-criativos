# -*- coding: utf-8 -*-
"""Editor VOX (23/10/2026) — estilo explainer Vox / colagem documental sobre o motor da tela dividida.

Nasceu de um teste aprovado: papel creme com grão e vinheta, manchetes em tiras de
papel rasgado (TikTok Sans 900), apoio em recorte de jornal (EB Garamond), marca-texto amarelo na palavra-chave, fita
adesiva, retícula, círculo desenhado à mão, ícones Phosphor (fill) como recorte, stop-motion a 12 fps e "boil".
Somou o que as referências de explainer estilo Vox têm em comum — análise em skill editor-vox:
  foto()     foto do PRÓPRIO pessoa (quadro do vídeo) impressa em retícula P&B, borda branca, fita e sombra
  numero()   número gigante cortado ao meio, as metades entram de lados opostos
  nota()     bilhete preso com tachinha vermelha e checklist que vai sendo marcado
  jornal()   recorte de jornal com o trecho marcado em amarelo
  carimbo()  carimbo vermelho batendo
  escura(c)  cena em azul-noite (alterna o ritmo papel claro / fundo escuro)
  secoes()   régua de progresso no alto — DESLIGADA por padrão (usuário, 23/10: "eu tiraria essa linha"); só se ele pedir
  + câmera empurrando devagar em toda cena e efeitos sonoros leves (whoosh na troca, pop, papel, tique, carimbo)

Uso no gerar.py de cada vídeo (hyperframes/<nome>-vox/gerar.py):
    configurar(...); from pecas import *; import vox
    ...cenas com monta()/linha()/ic() e as peças do vox...
    vox.aplicar()          # no lugar de montar()
Formatos: python gerar.py phosphor RL|YT|IN|GL (RL/YT tela dividida; IN/GL alternam pessoa cheia e animação cheia).
"""
import html as _html
import re
import shutil
import subprocess
import wave
from pathlib import Path
from urllib.parse import quote as _quote

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

import motor
import pecas
from motor import q

CREME, PAPEL, JORNAL, PRETO, AMARELO, TIJOLO, NOITE = '#EEE5D1', '#FBF8F0', '#E6DECA', '#151515', '#F5D90A', '#B8432F', '#14182B'
_BASE = motor.RAIZ / 'ferramentas/fontes'
_SFX_DIR = motor.RAIZ / 'remotion/public/sfx'

SFX = []          # (t, nome, volume) — efeitos sonoros leves
SECOES = []       # (t, rótulo) — régua de progresso
ESCURAS = set()   # ids das cenas em azul-noite
_n = [0]


def _id(c, pref):
    _n[0] += 1
    return f'{c.id}-{pref}{_n[0]}'


def som(t, nome, vol=0.2):
    """Efeito sonoro em t (s). nome: whoosh, pop, papel, tique, carimbo, clique, ping, tesoura."""
    SFX.append((round(float(t), 3), nome, vol))


def secoes(lista):
    """[(t, 'Rótulo'), ...] — blocos do vídeo na régua de progresso do alto."""
    SECOES[:] = [(float(t), r) for t, r in lista]


def escura(c):
    ESCURAS.add(c.id)
    return c


# ---------------------------------------------------------------- ícones: Phosphor fill (vira recorte) + setas à mão
_FILL = motor.RAIZ / 'ferramentas/phosphor-core/assets/fill'
_SETAS = {
    'arrow-right': 'M8 54 C26 44 46 58 64 48 C74 42 80 46 90 50 M72 30 C80 38 86 44 91 50 C84 56 78 62 70 72',
    'arrow-down': 'M52 6 C44 26 58 44 48 64 C46 72 49 80 50 90 M30 70 C38 78 44 84 50 91 C56 84 62 78 72 68',
}


def _ph_vox(arquivo, tam, id_='', cls='', estilo=''):
    ida = f' id="{id_}"' if id_ else ''
    if arquivo in _SETAS:
        return (f'<svg{ida} class="ic mao {cls}" width="{tam}" height="{tam}" viewBox="0 0 100 100" fill="none" '
                f'stroke="#151515" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" overflow="visible">'
                f'<path class="d" pathLength="1" d="{_SETAS[arquivo]}"/></svg>')
    corpo = re.search(r'<svg[^>]*>(.*)</svg>', (_FILL / f'{arquivo}-fill.svg').read_text(encoding='utf-8'), re.S).group(1)
    est = f' style="{estilo}"' if estilo else ''
    return f'<svg{ida} class="ic ph {cls}" width="{tam}" height="{tam}" viewBox="0 0 256 256"{est}>{corpo}</svg>'


motor.ph_svg = _ph_vox
pecas.ph_svg = _ph_vox


# ================================================================ PEÇAS NOVAS
def _meio_tom(im, larg, celula=7):
    """Foto em retícula P&B (pontos pretos sobre papel), misturada com um pouco do cinza pra manter o rosto legível."""
    g = ImageOps.autocontrast(im.convert('L'), cutoff=2)
    h = round(larg * g.height / g.width)
    g = g.resize((larg, h), Image.LANCZOS)
    a = np.asarray(g.resize((max(1, larg // celula), max(1, h // celula)), Image.BILINEAR), float) / 255
    pontos = Image.new('L', (larg, h), 238)
    d = ImageDraw.Draw(pontos)
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            r = (1 - a[y, x]) ** 0.85 * celula * 0.74
            if r > 0.45:
                cx, cy = x * celula + celula / 2, y * celula + celula / 2
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=20)
    return Image.blend(pontos, g, 0.32).convert('RGB')


def foto(c, t, momento, larg=430, rot=-3.0, legenda='', proporcao=1.2, cy=0.42):
    """Foto do próprio pessoa (quadro do vídeo em `momento` s) impressa em retícula, com borda branca, fita e sombra.
    Nunca usar imagem inventada: a foto sai do vídeo dele. cy = centro vertical do recorte (0–1)."""
    fid = _id(c, 'f')
    pub = motor.AQUI / 'public'
    (pub / 'vox').mkdir(exist_ok=True)
    tmp = pub / 'vox' / f'{fid}.png'
    subprocess.run([str(_ff()), '-v', 'error', '-y', '-ss', f'{momento:.3f}', '-i', str(pub / 'pessoa.mp4'),
                    '-frames:v', '1', str(tmp)], check=True)
    im = Image.open(tmp)
    w, h = im.size
    alt = min(h, round(w * proporcao))
    y0 = int(min(max(cy * h - alt / 2, 0), h - alt))
    _meio_tom(im.crop((0, y0, w, y0 + alt)), larg).save(pub / 'vox' / f'{fid}.jpg', quality=88)
    tmp.unlink()
    leg = f'<div class="fleg">{_html.escape(legenda)}</div>' if legenda else ''
    c.a(f"tl.fromTo('#{fid}',{{opacity:0,y:-70,rotation:{rot - 9},scale:1.12}},{{opacity:1,y:0,rotation:{rot},scale:1,"
        f"duration:0.32,ease:'back.out(1.6)'}},{q(t)});")
    som(t, 'papel', 0.28)
    return f'<div class="foto" id="{fid}" style="width:{larg}px"><img src="vox/{fid}.jpg"/><i class="fita1"></i><i class="fita2"></i>{leg}</div>'


def numero(c, texto, t, tam=250, cor=PRETO, legenda=''):
    """Número gigante cortado ao meio: metade de cima entra pela esquerda, a de baixo pela direita."""
    nid = _id(c, 'n')
    tx = _html.escape(texto)
    c.a(f"tl.fromTo('#{nid} .a',{{x:-420,opacity:0}},{{x:0,opacity:1,duration:0.32,ease:'power3.out'}},{q(t)});")
    # metade de baixo = ::after do próprio .num (texto só uma vez no DOM: o check não acusa sobreposição)
    c.a(f"tl.fromTo('#{nid}',{{'--bx':'420px','--bo':0}},{{'--bx':'0px','--bo':1,duration:0.32,ease:'power3.out'}},{q(t)});")
    c.a(f"desenha('#{nid}-s .d',{q(t + 0.3)},0.3);")
    som(t, 'whoosh', 0.22)
    # legenda pequena embaixo do número, do jeito que ele fala (25/10, usuário: "se ele fala 11 da noite, escreva assim")
    leg = ''
    if legenda:
        c.a(f"tl.fromTo('#{nid}-l',{{opacity:0,y:14}},{{opacity:1,y:0,duration:0.22,ease:'power2.out'}},{q(t + 0.3)});")
        leg = f'<div class="nleg" id="{nid}-l">{_html.escape(legenda)}</div>'
    return (f'<div class="numw">' if legenda else '') + (f'<div class="num" id="{nid}" data-t="{tx}" style="font-size:{tam}px;color:{cor}"><span class="a">{tx}</span>'
            f'<svg id="{nid}-s" class="sub" viewBox="0 0 100 10" preserveAspectRatio="none"><path class="d" pathLength="1" '
            f'd="M2 6 C25 3 45 8 60 5 C75 3 88 6 98 4"/></svg></div>') + (f'{leg}</div>' if legenda else '')


def nota(c, titulo, itens, tempos, larg=640):
    """Bilhete preso com tachinha; cada item entra e ganha o ✓ no seu tempo (tempos = índices de palavra ou s)."""
    nid = _id(c, 'b')
    ts_ = [motor.ts(x) if isinstance(x, int) else float(x) for x in tempos]
    c.a(f"entra('#{nid}',{q(max(c.t0 + 0.05, ts_[0] - 0.35))},0.3);")
    som(max(c.t0 + 0.05, ts_[0] - 0.35), 'papel', 0.22)
    lis = []
    for k, (txt, t) in enumerate(zip(itens, ts_)):
        c.a(f"tl.fromTo('#{nid}-{k}',{{opacity:0,x:-24}},{{opacity:1,x:0,duration:0.2,ease:'power2.out'}},{q(t - 0.05)});")
        c.a(f"desenha('#{nid}-{k} .ok .d',{q(t + 0.12)},0.22);")
        som(t + 0.12, 'tique', 0.3)
        lis.append(f'<li id="{nid}-{k}"><svg class="ok" viewBox="0 0 40 40"><rect x="3" y="3" width="34" height="34" rx="4"/>'
                   f'<path class="d" pathLength="1" d="M9 21 L17 29 L32 10"/></svg><span>{_html.escape(txt)}</span></li>')
    return (f'<div class="nota" id="{nid}" style="width:{larg}px"><i class="pino"></i>'
            f'<div class="nt">{_html.escape(titulo)}</div><ul>{"".join(lis)}</ul></div>')


def jornal(c, texto, destaque, t, t_marca, cabecalho='CONVERSÃO EXTREMA · 2026', larg=760):
    """Recorte de jornal; `destaque` (trecho de `texto`) é pintado de amarelo em t_marca."""
    jid = _id(c, 'j')
    tx = _html.escape(texto).replace(_html.escape(destaque), f'<mark id="{jid}-m">{_html.escape(destaque)}</mark>', 1)
    c.a(f"entra('#{jid}',{q(t)},0.3);")
    c.a(f"tl.fromTo('#{jid}-m',{{backgroundSize:'0% 80%'}},{{backgroundSize:'100% 80%',duration:0.4,ease:'power1.inOut'}},{q(t_marca)});")
    som(t, 'papel', 0.25)
    return (f'<div class="jornal" id="{jid}" style="width:{larg}px"><div class="jh">{_html.escape(cabecalho)}</div>'
            f'<p>{tx}</p></div>')


def carimbo(c, texto, t, rot=-11):
    """Carimbo vermelho batendo (ex.: GRÁTIS, NOVO, 80%)."""
    kid = _id(c, 'k')
    c.a(f"tl.fromTo('#{kid}',{{opacity:0,scale:2.3,rotation:{rot - 8}}},{{opacity:1,scale:1,rotation:{rot},duration:0.18,"
        f"ease:'power4.in'}},{q(t)});")
    som(t + 0.15, 'carimbo', 0.32)
    return f'<div class="carimbo" id="{kid}">{_html.escape(texto)}</div>'


# ================================================================ ESTILO + MONTAGEM
def _ff():
    return Path((motor.RAIZ / 'ferramentas/ffmpeg_path.txt').read_text().strip())


def _fonte(nome, tam, peso=None):
    f = ImageFont.truetype(str(_BASE / nome), tam)
    if peso:
        f.set_variation_by_axes([peso])
    return f


def _ajusta(m):
    """Manchete: TikTok Sans 900; apoio: EB Garamond (OFL). Nunca passa de 840/860 px (margem lateral ≥ 100 px, regra de 23/10)."""
    cls, tam, miolo_ = m.group(1), int(m.group(2)), m.group(3)
    fino = 'fino' in cls
    txt = _html.unescape(re.sub(r'<[^>]+>', '', miolo_))
    alvo = round(tam * (0.92 if fino else 0.94))
    while alvo > 30:
        f = _fonte('EBGaramond-400.woff2', alvo) if fino else _fonte('TikTokSans-Variable.ttf', alvo, 900)
        if f.getlength(txt) * (1 if fino else 0.98) <= (820 if fino else 800):
            break
        alvo -= 2
    return f'<div class="ln{cls}" style="font-size:{alvo}px">{miolo_}</div>'


def _circulo(iid):
    return (f'<svg class="circ" id="{iid}-cir" viewBox="0 0 100 100" preserveAspectRatio="none" fill="none" '
            f'stroke="{PRETO}" stroke-width="2.6" stroke-linecap="round"><path class="d" pathLength="1" '
            f'd="M62 7 C30 2 4 22 6 52 C8 84 46 98 76 88 C100 78 99 34 80 17 C70 8 52 6 40 11"/></svg>')


def _svg_uri(s):
    return 'url("data:image/svg+xml,' + _quote(s, safe=" =:/'.,-()") + '")'


_GRAO = _svg_uri("<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'><filter id='f'>"
                 "<feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/>"
                 "<feColorMatrix values='0 0 0 0 0.30 0 0 0 0 0.24 0 0 0 0 0.14 0 0 0 0.55 0'/></filter>"
                 "<rect width='100%' height='100%' filter='url(#f)' opacity='0.42'/></svg>")
_FIBRA = _svg_uri("<svg xmlns='http://www.w3.org/2000/svg' width='520' height='520'><filter id='f'>"
                  "<feTurbulence type='fractalNoise' baseFrequency='0.012 0.16' numOctaves='3' stitchTiles='stitch'/>"
                  "<feColorMatrix values='0 0 0 0 0.45 0 0 0 0 0.36 0 0 0 0 0.20 0 0 0 0.9 -0.35'/></filter>"
                  "<rect width='100%' height='100%' filter='url(#f)' opacity='0.30'/></svg>")
_FITA = ('polygon(0 8%,6% 0,12% 10%,18% 0,24% 9%,30% 0,70% 0,76% 9%,82% 0,88% 10%,94% 0,100% 8%,'
         '97% 50%,100% 92%,94% 100%,88% 90%,82% 100%,76% 91%,70% 100%,30% 100%,24% 91%,18% 100%,12% 90%,6% 100%,0 92%,3% 50%)')
_FITA_BG = 'linear-gradient(rgba(255,255,255,.25),rgba(255,255,255,0) 70%),rgba(222,210,170,.78)'
_PAPEL_BG = (f'radial-gradient(ellipse 78% 72% at 50% 46%,rgba(60,40,10,0) 52%,rgba(60,40,10,.34) 100%),'
             f'{_GRAO},{_FIBRA},{CREME}')
_AMASSADO = _svg_uri("<svg xmlns='http://www.w3.org/2000/svg' width='1080' height='960'><filter id='f' x='0' y='0' width='100%' height='100%'>"
                     "<feTurbulence type='fractalNoise' baseFrequency='0.006 0.009' numOctaves='5' seed='11' result='n'/>"
                     "<feDiffuseLighting in='n' lighting-color='#fff' surfaceScale='4' diffuseConstant='1.1'>"
                     "<feDistantLight azimuth='225' elevation='38'/></feDiffuseLighting></filter>"
                     "<rect width='100%' height='100%' filter='url(#f)'/></svg>")
# 23/10 (usuário): o azul-noite não agradou — "folha cinza escuro, meio amassada, que dá pra ver ser papel, com elementos claros"
_NOITE_BG = (f'radial-gradient(ellipse 80% 72% at 50% 46%,rgba(0,0,0,0) 50%,rgba(0,0,0,.45) 100%),{_GRAO},{_AMASSADO},#3B3935')
_NOITE_BLEND = 'background-blend-mode:normal,normal,overlay,normal;background-size:auto,auto,100% 100%,auto'

FILTROS = """<svg width="0" height="0" style="position:absolute;left:0;top:0" aria-hidden="true"><defs>
<filter id="rasgo" x="-6%" y="-35%" width="112%" height="170%" color-interpolation-filters="sRGB">
<feTurbulence id="turb1" type="fractalNoise" baseFrequency="0.07" numOctaves="3" seed="1" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="13" xChannelSelector="R" yChannelSelector="G"/>
<feDropShadow dx="3" dy="6" stdDeviation="3.5" flood-color="#2a1c08" flood-opacity="0.34"/></filter>
<filter id="rasgo2" x="-6%" y="-35%" width="112%" height="170%" color-interpolation-filters="sRGB">
<feTurbulence id="turb2" type="fractalNoise" baseFrequency="0.11" numOctaves="2" seed="2" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="8" xChannelSelector="R" yChannelSelector="G"/>
<feDropShadow dx="2" dy="4" stdDeviation="2.5" flood-color="#2a1c08" flood-opacity="0.28"/></filter>
<filter id="recorte" x="-25%" y="-25%" width="150%" height="150%" color-interpolation-filters="sRGB">
<feMorphology in="SourceAlpha" operator="dilate" radius="9" result="dil"/>
<feTurbulence id="turb3" type="fractalNoise" baseFrequency="0.09" numOctaves="2" seed="3" result="n"/>
<feDisplacementMap in="dil" in2="n" scale="9" xChannelSelector="R" yChannelSelector="G" result="borda"/>
<feFlood flood-color="#FBF8F0"/><feComposite in2="borda" operator="in" result="papel"/>
<feDropShadow in="papel" dx="3" dy="6" stdDeviation="3" flood-color="#2a1c08" flood-opacity="0.33" result="sombra"/>
<feMerge><feMergeNode in="sombra"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="rasgo3" x="-2%" y="-60%" width="104%" height="260%" color-interpolation-filters="sRGB">
<feTurbulence id="turb4" type="fractalNoise" baseFrequency="0.035 0.08" numOctaves="3" seed="4" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="22" xChannelSelector="R" yChannelSelector="G"/>
<feDropShadow dx="0" dy="5" stdDeviation="4" flood-color="#000" flood-opacity="0.45"/></filter>
<filter id="rasgo3v" x="-60%" y="-2%" width="260%" height="104%" color-interpolation-filters="sRGB">
<feTurbulence id="turb5" type="fractalNoise" baseFrequency="0.08 0.035" numOctaves="3" seed="5" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="22" xChannelSelector="R" yChannelSelector="G"/>
<feDropShadow dx="5" dy="0" stdDeviation="4" flood-color="#000" flood-opacity="0.45"/></filter>
</defs></svg>"""

JS_STOP = """
// stop-motion: todo tween anda em degraus de 1/12 s (a curva original fica, só o tempo é quantizado)
const _Q=12;
function _qz(v){if(!v||typeof v!=='object')return v;v=Object.assign({},v);const d=v.duration==null?0.5:v.duration;const n=Math.max(1,Math.round(d*_Q));const b=gsap.parseEase(v.ease||'power1.out');v.ease=function(p){return p>=1?1:b(Math.ceil(p*n)/n);};return v;}
const _ft=tl.fromTo.bind(tl),_to=tl.to.bind(tl);
tl.fromTo=function(s,a,b,t){return _ft(s,a,_qz(b),t);};
tl.to=function(s,b,t){return _to(s,_qz(b),t);};
"""

JS_VOX = """
// Vox: tira de papel pula na tela com a 1ª palavra; palavra-chave ganha o marca-texto pintando da esquerda pra direita
const _ROT=[-1.8,1.3,-0.9,2.0,-1.4,0.8,-2.2,1.6];
let _nl=0;
function tira(ln,t){const r=_ROT[_nl++%_ROT.length];tl.fromTo(ln,{opacity:0,scale:0.8,rotation:r-8,y:-28},{opacity:1,scale:1,rotation:r,y:0,duration:0.25,ease:'back.out(2.2)',transformOrigin:'50% 50%'},Math.max(0,t-0.04));}
function palavra(s,t,cor){const el=document.querySelector(s);const ln=el.closest('.ln');if(ln&&!ln.dataset.vox){ln.dataset.vox='1';tira(ln,t);}tl.fromTo(s,{opacity:0},{opacity:1,duration:0.04,ease:'none'},t);if(el.classList.contains('k'))tl.fromTo(s,{backgroundSize:'0% 74%'},{backgroundSize:'100% 74%',duration:0.25,ease:'power1.inOut'},t+0.03);}
function pop(s,t,st){tl.fromTo(s,{opacity:0,scale:0.4,rotation:-14},{opacity:1,scale:1,rotation:0,duration:0.3,ease:'back.out(2)',stagger:st||0,transformOrigin:'50% 50%'},t);}
function entra(s,t,d){tl.fromTo(s,{opacity:0,scale:0.84,rotation:5},{opacity:1,scale:1,rotation:0,duration:d||0.25,ease:'back.out(1.8)',transformOrigin:'50% 50%'},t);}
function revela(s,t,d){const el=document.querySelector(s);if(el&&el.classList.contains('mao')){desenha(s+' .d',t,0.42);return;}tl.fromTo(s,{opacity:0,scale:0.5,rotation:-12,y:30},{opacity:1,scale:1,rotation:0,y:0,duration:0.3,ease:'back.out(2)',transformOrigin:'50% 50%'},t);}
"""

JS_BOIL = """
// boil: as bordas rasgadas trocam entre 3 desenhos a 8 por segundo (como papel filmado quadro a quadro)
const _turbs=['#turb1','#turb2','#turb3','#turb4','#turb5'].map(function(x){return document.querySelector(x);});
const _bo={v:0};
tl.to(_bo,{v:__DUR__,duration:__DUR__,ease:'none',onUpdate:function(){const k=Math.floor(_bo.v*8)%3;_turbs.forEach(function(el,i){if(el)el.setAttribute('seed',String(1+k*7+i));});}},0);
"""


def _css(fmt):
    if fmt == 'YT':
        fundo = ('#root{background:' + _PAPEL_BG.replace('ellipse 78% 72% at 50% 46%', 'ellipse 40% 72% at 25% 50%')
                 + '}.cena{background:transparent}' + f'.cena.escura{{background:{_NOITE_BG};{_NOITE_BLEND}}}')
    else:
        fundo = f'.cena{{background:{_PAPEL_BG}}}.cena.escura{{background:{_NOITE_BG};{_NOITE_BLEND}}}'
    if fmt == 'IN':
        fundo += '#palco,.cena{height:1350px}.miolo{height:1350px;padding:300px 100px 220px}'
    elif fmt == 'GL':
        fundo += '.miolo{padding:170px 100px 120px}'
    div = {'RL': f'#divisoria{{top:936px !important;height:44px !important;background:{CREME} !important;filter:url(#rasgo3)}}',
           'YT': f'#divisoria{{left:928px !important;top:0 !important;width:44px !important;height:1080px !important;'
                 f'background:{CREME} !important;filter:url(#rasgo3v)}}'}.get(fmt, '#divisoria{display:none}')
    return f"""
@font-face{{font-family:'Vox';src:url('fonts/TikTokSans-Variable.ttf') format('truetype');font-weight:300 900;font-display:block}}
@font-face{{font-family:'Jornal';src:url('fonts/EBGaramond-400.woff2') format('woff2');font-weight:400;font-display:block}}
html,body,#root{{background:{PRETO}}}
{fundo}
.miolo{{gap:34px;padding-left:100px;padding-right:100px}}
.ht{{position:absolute;border-radius:50%;background-size:22px 22px;-webkit-mask-image:radial-gradient(circle,#000 0 34%,transparent 70%);mask-image:radial-gradient(circle,#000 0 34%,transparent 70%)}}
.ht0{{left:560px;top:150px;width:620px;height:620px;background-image:radial-gradient(circle,rgba(21,21,21,.16) 0 32%,transparent 35%)}}
.ht1{{left:-170px;top:400px;width:640px;height:640px;background-image:radial-gradient(circle,rgba(21,21,21,.16) 0 32%,transparent 35%)}}
.ht2{{left:600px;top:470px;width:600px;height:600px;background-image:radial-gradient(circle,rgba(21,21,21,.16) 0 32%,transparent 35%)}}
.ht3{{left:-150px;top:130px;width:620px;height:620px;background-image:radial-gradient(circle,rgba(21,21,21,.16) 0 32%,transparent 35%)}}
.escura .ht{{filter:invert(1);opacity:.5}}
.let{{display:flex;flex-direction:column;align-items:center;gap:20px;line-height:1;letter-spacing:0;color:{PRETO}}}
.let .ln{{position:relative;width:fit-content;padding:.15em .36em .1em;font-family:'Vox',sans-serif;font-weight:900;color:{PRETO};letter-spacing:-.025em;line-height:1;isolation:isolate}}
.let .ln::before{{content:'';position:absolute;inset:0;z-index:-1;background:{_GRAO},{PAPEL};filter:url(#rasgo)}}
.let .ln.fino{{font-family:'Jornal',serif;font-weight:400;letter-spacing:0;line-height:1.08;padding:.2em .55em .2em;color:#262420}}
.let .ln.fino::before{{background:{_GRAO},repeating-linear-gradient(0deg,rgba(0,0,0,.03) 0 2px,transparent 2px 6px),{JORNAL};filter:url(#rasgo2)}}
.let .w.k{{color:{PRETO};-webkit-background-clip:border-box;background-clip:border-box;background-image:linear-gradient(178deg,{AMARELO},#F2D20C 60%,{AMARELO});background-repeat:no-repeat;background-position:0 70%;background-size:0% 74%;padding:0 .07em;margin:0 -.03em;border-radius:.06em .14em .08em .12em}}
.let .ln:first-child::after{{content:'';position:absolute;left:-40px;top:-20px;width:120px;height:40px;transform:rotate(-27deg);background:{_FITA_BG};box-shadow:0 1px 3px rgba(40,25,0,.22);clip-path:{_FITA}}}
.let .ln:last-child:not(:first-child)::after{{content:'';position:absolute;right:-38px;bottom:-16px;width:110px;height:38px;transform:rotate(-22deg);background:{_FITA_BG};box-shadow:0 1px 3px rgba(40,25,0,.22);clip-path:{_FITA}}}
.ic.ph{{fill:{PRETO};filter:url(#recorte);overflow:visible}}
.ic.ph.verde{{fill:{TIJOLO}}}
.ic.mao{{overflow:visible;stroke:{PRETO} !important}}
.escura .ic.mao{{stroke:{PAPEL} !important}}
.xis{{stroke:{TIJOLO};stroke-width:5px;overflow:visible}}
.circ-w{{position:relative;display:flex}}
.circ{{position:absolute;left:-24%;top:-20%;width:148%;height:140%;overflow:visible;pointer-events:none}}
.circ .d{{stroke-width:3.4px}}
.escura .circ{{stroke:{PAPEL}}}
.tile{{border:3px solid {PRETO}}}
.tile.gd{{background:{PRETO};border-color:{PRETO};border-radius:24px;filter:url(#recorte)}}
.tile.gd .ic{{stroke:{CREME}}}
.ic .g{{stroke:{AMARELO}}}
.ic .ftxt{{fill:{AMARELO}}}
.botao{{background:{AMARELO} !important;border:4px solid {PRETO} !important;color:{PRETO};border-radius:12px;font-family:'Vox',sans-serif;font-weight:900;box-shadow:7px 9px 0 rgba(40,25,0,.28) !important;transform:rotate(-1.5deg)}}
.botao .pontos{{display:none}}
.botao .bt-verde{{background:#3A9A5B;border-radius:8px}}
.okbt{{stroke:{PRETO}}}
/* foto da pessoa em retícula */
.foto{{position:relative;padding:14px 14px 18px;isolation:isolate}}
.foto::before{{content:'';position:absolute;inset:0;z-index:-1;background:#fff;box-shadow:6px 10px 0 rgba(30,20,5,.30),0 2px 8px rgba(0,0,0,.25);filter:url(#rasgo2)}}
.foto img{{display:block;width:100%;height:auto}}
.foto .fita1,.foto .fita2{{position:absolute;width:120px;height:38px;background:{_FITA_BG};clip-path:{_FITA};box-shadow:0 1px 3px rgba(40,25,0,.22)}}
.foto .fita1{{left:-34px;top:-12px;transform:rotate(-32deg)}}
.foto .fita2{{right:-34px;top:-12px;transform:rotate(30deg)}}
.foto .fleg{{position:absolute;left:50%;bottom:-30px;transform:translateX(-50%) rotate(-2deg);white-space:nowrap;background:{PRETO};color:{PAPEL};font-family:'Vox';font-weight:800;font-size:34px;padding:6px 16px}}
/* número gigante cortado */
.num{{position:relative;font-family:'Vox',sans-serif;font-weight:900;line-height:.86;letter-spacing:-.04em;padding:.14em 0 .06em;--bx:0px;--bo:1}}
.num .a{{display:block;clip-path:inset(0 0 50% 0)}}
.num::after{{content:attr(data-t);position:absolute;left:0;top:.14em;clip-path:inset(50% 0 0 0);transform:translateX(var(--bx));opacity:var(--bo)}}
.num .sub{{position:absolute;left:4%;bottom:-.12em;width:92%;height:.12em;overflow:visible;fill:none;stroke:{TIJOLO};stroke-width:4;stroke-linecap:round}}
/* bilhete com checklist */
.nota{{position:relative;padding:46px 46px 34px;transform:rotate(-1.6deg);isolation:isolate}}
.nota::before{{content:'';position:absolute;inset:0;z-index:-1;background:{_GRAO},#FFFDF4;box-shadow:5px 9px 0 rgba(30,20,5,.28);filter:url(#rasgo2)}}
.nota .pino{{position:absolute;left:50%;top:-18px;width:38px;height:38px;margin-left:-19px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ff8a7a,{TIJOLO} 55%,#6d1f12);box-shadow:2px 5px 4px rgba(0,0,0,.35)}}
.nota .nt{{font-family:'Vox';font-weight:900;font-size:66px;color:{PRETO};border-bottom:3px solid {PRETO};padding-bottom:12px;margin-bottom:18px}}
.nota ul{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:16px}}
.nota li{{display:flex;align-items:center;gap:18px;font-family:'Jornal',serif;font-size:54px;color:#262420}}
.nota .ok{{width:54px;height:54px;flex:none;fill:none;stroke:{PRETO};stroke-width:3}}
.nota .ok .d{{stroke:{TIJOLO};stroke-width:5;stroke-linecap:round;stroke-linejoin:round}}
/* recorte de jornal */
.jornal{{position:relative;padding:30px 40px 34px;transform:rotate(1.2deg);isolation:isolate}}
.jornal::before{{content:'';position:absolute;inset:0;z-index:-1;background:{_GRAO},repeating-linear-gradient(0deg,rgba(0,0,0,.035) 0 2px,transparent 2px 6px),{JORNAL};box-shadow:5px 9px 0 rgba(30,20,5,.26);filter:url(#rasgo2)}}
.jornal .jh{{font-family:'Jornal',serif;font-size:24px;letter-spacing:.18em;border-top:3px double #333;border-bottom:1px solid #333;padding:6px 0;margin-bottom:16px;text-align:center;color:#333}}
.jornal p{{margin:0;font-family:'Jornal',serif;font-size:46px;line-height:1.28;color:#222;text-align:justify}}
.jornal mark{{color:#111;background-image:linear-gradient(178deg,{AMARELO},#F2D20C 60%,{AMARELO});background-repeat:no-repeat;background-position:0 70%;background-size:0% 80%;background-color:transparent}}
/* carimbo */
.carimbo{{font-family:'Vox';font-weight:900;font-size:86px;color:{TIJOLO};border:8px solid {TIJOLO};border-radius:14px;padding:6px 30px;letter-spacing:.04em;mix-blend-mode:multiply;opacity:.92}}
.escura .carimbo{{mix-blend-mode:normal}}
/* régua de progresso (ref.: Vox, explainer com marcadores) */
#vx-regua{{position:absolute;left:100px;right:100px;top:42px;height:40px;z-index:4;pointer-events:none}}
#vx-regua .tr{{position:absolute;left:0;right:0;top:18px;height:4px;background:rgba(21,21,21,.25);border-radius:2px}}
#vx-regua .en{{position:absolute;left:0;right:0;top:18px;height:4px;background:{TIJOLO};border-radius:2px;transform-origin:0 50%}}
#vx-regua .mk{{position:absolute;top:10px;width:20px;height:20px;margin-left:-10px;border-radius:50%;background:{CREME};border:3px solid {PRETO}}}
#vx-regua .bo{{position:absolute;top:4px;left:0;width:32px;height:32px;margin-left:-16px;border-radius:50%;background:{TIJOLO};border:4px solid {PRETO};box-shadow:2px 3px 0 rgba(0,0,0,.25)}}
/* widgets do motor em estilo papel */
.cartao{{border:none !important;border-radius:3px !important;isolation:isolate}}
.cartao::before{{content:'';position:absolute;inset:0;z-index:-1;background:{_GRAO},{PAPEL};box-shadow:5px 9px 0 rgba(30,20,5,.26);filter:url(#rasgo2)}}
.kick,.rot{{font-family:'Jornal',serif !important;color:#4A443A !important;letter-spacing:.12em}}
.barra{{background:{PRETO} !important;border-radius:3px !important;filter:url(#recorte)}}
.barras .barra:last-child{{background:{TIJOLO} !important}}
.cartao svg polyline,.cartao svg path{{stroke:{PRETO}}}
.cartao svg circle{{fill:{TIJOLO}}}
.bolha{{border-radius:6px !important;font-family:'Jornal',serif;box-shadow:4px 6px 0 rgba(30,20,5,.22)}}
.bolha.in{{background:{JORNAL} !important;color:#262420 !important}}
.bolha.out{{background:{AMARELO} !important;color:{PRETO} !important}}
.digita{{background:{PAPEL} !important;border-radius:6px !important}}
.digita i{{background:#8A8070 !important}}
.chip{{background:{PAPEL} !important;color:{PRETO} !important;border:2px solid {PRETO};border-radius:6px !important;font-family:'Jornal',serif}}
.cel{{background:{JORNAL} !important;border:2px solid {PRETO} !important;border-radius:3px !important}}
.av,.avatar{{background:{PAPEL} !important;border-color:{PRETO} !important}}
.passo{{border-color:{PRETO} !important;background:{PAPEL} !important;color:{PRETO}}}
.passo svg{{stroke:{TIJOLO} !important}}
.ic.verde{{stroke:{PRETO}}}
.elo{{background:rgba(21,21,21,.18) !important}}
.elo-f{{background:{PRETO} !important}}
.dot{{background:rgba(21,21,21,.2) !important}}.dot.on{{background:{PRETO} !important}}.dot.at{{background:{TIJOLO} !important}}
.cinza{{background:rgba(21,21,21,.22) !important}}
.trilho{{background:rgba(21,21,21,.12) !important}}.barra-h{{background:{PRETO} !important}}
.val,.val.g{{color:{PRETO} !important;font-family:'Vox'}}
.badge{{background:{TIJOLO} !important;color:#fff !important}}
.selo{{background:{PRETO} !important}}
.moeda{{border-color:{PRETO} !important;background:{AMARELO} !important}}
.caixa,.slot{{border-color:{PRETO} !important;color:{PRETO} !important}}
.slot .q{{color:{TIJOLO} !important}}
.escura .carimbo{{color:#F2765C;border-color:#F2765C}}
.numw{{display:flex;flex-direction:column;align-items:center;gap:18px}}
.nleg{{position:relative;font-family:'Jornal',serif;font-size:60px;color:#262420;padding:.18em .55em;isolation:isolate}}
.nleg::before{{content:'';position:absolute;inset:0;z-index:-1;background:{_GRAO},{JORNAL};filter:url(#rasgo2)}}
{div}
"""


def _regua(fmt):
    if not SECOES or fmt in ('IN', 'GL'):
        return '', ''
    larg = (960 if fmt == 'YT' else 1080) - 200
    mks = ''.join(f'<i class="mk" style="left:{t / motor.DUR * 100:.2f}%"></i>' for t, _ in SECOES)
    estilo = 'style="left:100px;width:760px;right:auto"' if fmt == 'YT' else ''
    html_ = f'<div id="vx-regua" {estilo}><div class="tr"></div><div class="en"></div>{mks}<i class="bo"></i></div>'
    js = (f"tl.fromTo('#vx-regua .en',{{scaleX:0}},{{scaleX:1,duration:{motor.DUR},ease:'none'}},0);"
          f"tl.fromTo('#vx-regua .bo',{{x:0}},{{x:{larg},duration:{motor.DUR},ease:'none'}},0);")
    return html_, js


def _dur_wav(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def _audios():
    """Efeitos em <audio> do próprio HyperFrames, em trilhas 11–16 sem sobreposição; mínimo de 0,28 s entre dois sons."""
    pub = motor.AQUI / 'public/sfx'
    pub.mkdir(exist_ok=True)
    fim_trilha = {k: -1.0 for k in range(11, 17)}
    tags, aceitos = [], []
    # prioridade quando dois sons caem a menos de 0,28 s: clique/carimbo > tique/papel > pop > whoosh
    PRI = {'clique': 0, 'carimbo': 0, 'tique': 1, 'papel': 1, 'ping': 1, 'tesoura': 1, 'pop': 2, 'whoosh': 3}
    for t, nome, vol in sorted(SFX, key=lambda x: (PRI.get(x[1], 2), x[0])):
        if any(abs(t - a) < 0.28 for a in aceitos) or t >= motor.DUR - 0.2:
            continue
        aceitos.append(t)
    for t, nome, vol in sorted(x for x in SFX if x[0] in aceitos):
        if t in [float(m) for m in re.findall(r'data-start="([\d.]+)"', ' '.join(tags))]:
            continue
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


def aplicar():
    """Equivale ao montar() do motor + estilo VOX. Chamar no fim do gerar.py."""
    pub = motor.AQUI / 'public'
    (pub / 'fonts').mkdir(exist_ok=True)
    for f in ('TikTokSans-Variable.ttf', 'EBGaramond-400.woff2'):
        if not (pub / 'fonts' / f).exists():
            shutil.copy(_BASE / f, pub / 'fonts' / f)
    fmt = motor.FORMATO
    _ult_wh = [-9.0]
    for k, c in enumerate(motor.CENAS):
        c.html = re.sub(r'<div class="ln((?: fino)?(?: forte)?)" style="font-size:(\d+)px">(.*?)</div>', _ajusta, c.html)
        fim = motor.CENAS[k + 1].t0 if k + 1 < len(motor.CENAS) else motor.DUR
        for iid in re.findall(r'<svg id="(c\d+-i\d+)" class="ic ph verde"', c.html):
            c.html = re.sub(rf'(<svg id="{iid}" class="ic ph verde".*?</svg>)',
                            lambda mm, i=iid: f'<div class="circ-w">{mm.group(1)}{_circulo(i)}</div>', c.html, count=1, flags=re.S)
            tt = re.findall(rf"(?:pop|revela|entra)\('#{iid}',([\d.]+)", ' '.join(c.js))
            t = float(tt[0]) if tt else c.t0 + 0.3
            c.a(f"desenha('#{iid}-cir .d',{q(max(c.t0 + 0.1, min(t + 0.15, fim - 0.55)))},0.36);")
        for tt in re.findall(r"pop\('#[^']+',([\d.]+)", ' '.join(c.js)):
            som(float(tt), 'pop', 0.16)
        for tt in re.findall(r"vai\('#c\d+-bt',\{scale:0\.94,duration:0\.08\},([\d.]+)\)", ' '.join(c.js)):
            som(float(tt), 'clique', 0.4)   # clique do botão (usuário 23/10)
        if k and c.t0 - _ult_wh[0] >= 3.5:   # whoosh na troca, no máximo 1 a cada 3,5 s (efeito leve, não bateria)
            som(c.t0, 'whoosh', 0.10)
            _ult_wh[0] = c.t0
        c.html = f'<div class="ht ht{k % 4}" id="{c.id}-ht"></div>' + c.html
        c.js.insert(0, f"tl.fromTo('#{c.id}-ht',{{scale:0.55,opacity:0}},{{scale:1,opacity:1,duration:0.25,ease:'back.out(1.7)'}},{q(c.t0 + 0.02)});")
        # câmera empurrando devagar (o conteúdo, não o fundo)
        c.js.insert(0, f"tl.fromTo('#{c.id} .miolo',{{scale:1}},{{scale:1.035,duration:{q(max(0.3, fim - c.t0))},ease:'none'}},{q(c.t0)});")
    if fmt == 'IN':
        motor.FORMATOS['GL'] = dict(w=1080, h=1350, palco=(0, 0, 1.0), pessoa=(0, 0, 1080, 1350), divisoria=(0, 0, 0, 0),
                                    titulo=(540, 1000, 1080), video='pessoa-IN-cheio.mp4')
        # 27/10 (usuário, caso real "IN tão em baixa quando corta pro pessoa"): antes usava o pessoa-IN.mp4 (1080x676) esticado
        # pra 1350 de altura (2x). Agora recorte 4:5 próprio do base_h (864x1080 -> 1080x1350) seguindo o rosto.
        import pessoa_cheio
        pessoa_cheio.gerar(motor.GNN, motor.AQUI.name, larg=864, saida_wh=(1080, 1350), nome='pessoa-IN-cheio.mp4')
        motor.FORMATO = 'GL'
    motor.CENAS_ANIM_CHEIA = set(ESCURAS)   # 26/10: no RL as cenas escuras (folha cinza amassada) viram animação em tela cheia
    motor.GL_ESPERA_LINHA = False   # VOX: o papel já entra com conteúdo; regra do GL é só pros Hyperframe escuros
    motor.montar()
    motor.FORMATO = fmt

    arq = pub / 'index.html'
    s = arq.read_text(encoding='utf-8')
    for cid in ESCURAS:
        s = s.replace(f'<section id="{cid}" class="cena clip"', f'<section id="{cid}" class="cena clip escura"', 1)
    regua_html, regua_js = _regua(fmt)
    s = s.replace('</head>', f'<style>{_css(fmt)}</style></head>', 1)
    s = s.replace('<div id="root"', FILTROS + '\n    <div id="root"', 1)
    s = s.replace('<div id="divisoria"></div>', f'<div id="divisoria"></div>\n      {regua_html}\n      {_audios()}', 1)
    s = s.replace('const tl = gsap.timeline({ paused: true });', 'const tl = gsap.timeline({ paused: true });' + JS_STOP, 1)
    s = s.replace('\n// c01 ', JS_VOX + '\n' + regua_js + '\n// c01 ', 1)
    s = s.replace(f'window.__timelines["{motor.COMPOSICAO}"]', JS_BOIL.replace('__DUR__', str(motor.DUR))
                  + f'window.__timelines["{motor.COMPOSICAO}"]', 1)
    arq.write_text(s, encoding='utf-8')
    print(f'estilo VOX aplicado em {arq} ({fmt}): {len(ESCURAS)} cenas escuras, {s.count("<audio id=\"sfx")} efeitos, '
          f'régua {"sim" if regua_html else "não"}')
