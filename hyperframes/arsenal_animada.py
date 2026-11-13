# -*- coding: utf-8 -*-
"""ARSENAL da Edição animada (07/11/2026) — tudo OPT-IN: só muda um vídeo cujo gerar.py faz `import arsenal_animada as ar`.

Pedido do usuário ("tá bom, mas achei meio repetitivo; ali tem muita referência pra ele"): análise de 5 vídeos do canal
documentários ilustrados. O que entrou aqui (detalhes e assinaturas na skill edicao-animada):

  ar.escolhe(ideia, opcoes)      VARIEDADE: escolhe a variante evitando o que já apareceu no vídeo e nos outros vídeos do
                                 mesmo gancho/meio/final (histórico em hyperframes/_arsenal_historico.json, semente do vídeo)
  ar.transicao(c, nome)          transições novas na ENTRADA da cena c: tinta, pagina, iris, zoom, persiana, chicote,
                                 mancha, 'auto' (escolhe sem repetir a anterior)
  ar.camera(c, tipo)             câmera própria da cena: push, pull, tilt_baixo, tilt_cima, pan_dir, pan_esq, dolly;
                                 ar.tremor(c, t) = impacto
  ambientes novos (an.cenario)   campo, porto, porto_tarde, fabrica, loja, cafe, transito, aereo, corte, preto,
                                 capitulo_vermelho, capitulo_verde, tunel, casa, parque, banco_praca(=parque op)
  cenas / infográficos / metáforas / cartelas: arsenal_cenas.py e arsenal_info.py (reexportados aqui)

Regras que valem pra tudo daqui: vetor chapado igual ao bonecos.py, nada de foto/logo/link/QR/URL escrito, texto de peça
≥ 48 px e a ≥ 170 px das laterais na camada de ação, número só o falado, nunca parado (vida automática por classe).
"""
import json
import os
import random
import re
import sys
import zlib
from pathlib import Path

import animada as an
import bonecos as bo
import motor
from motor import q

_T = bo._T
HIST = motor.RAIZ / 'hyperframes/_arsenal_historico.json'
REESCOLHE = os.environ.get('ARSENAL_REESCOLHE') == '1'


# ================================================================ VARIEDADE (semente + histórico)
_EST = {'cont': {}, 'escolhas': {}, 'grupo': None, 'trans': {}, 'cam': {}, 'pecas': []}


def grupo(G=None, C=None, A=None):
    """Gancho/meio/final do vídeo (ex.: ar.grupo('G05', 'C3', 'A2')). Sem chamar, lê do docstring do gerar.py."""
    _EST['grupo'] = {'G': G, 'C': C, 'A': A}
    return _EST['grupo']


def _meu_grupo():
    if _EST['grupo'] is None:
        doc = (getattr(sys.modules.get('__main__'), '__doc__', '') or '')
        m = re.search(r'G(\d+)\s+C(\d+)\s+A(\d+)', doc)
        _EST['grupo'] = {'G': f'G{m.group(1)}', 'C': f'C{m.group(2)}', 'A': f'A{m.group(3)}'} if m else {'G': None, 'C': None, 'A': None}
    return _EST['grupo']


def _hist():
    try:
        return json.loads(HIST.read_text(encoding='utf-8'))
    except Exception:
        return {'videos': {}}


def escolhe(ideia, opcoes, base=None, pecas=None):
    """Escolhe UMA das opções pra uma ideia da fala, sem repetir:
      - nunca a mesma opção duas vezes no mesmo vídeo (enquanto houver outra);
      - evita o que os vídeos IRMÃOS usaram pra mesma ideia (mesmo gancho G, meio C ou final A — o prefixo da ideia diz
        qual: 'G:...', 'C:...', 'A:...'), depois o que qualquer vídeo do lote usou pra ela;
      - empate decidido pela semente do vídeo. A escolha fica gravada no histórico: rodar o gerar.py de novo devolve a
        mesma (ARSENAL_REESCOLHE=1 sorteia de novo).
    opcoes: lista/tupla de nomes ou dict {nome: valor} (devolve o nome). base = a opção do molde (vai pro fim da fila)."""
    nomes = list(opcoes.keys()) if isinstance(opcoes, dict) else list(opcoes)
    n = _EST['cont'].get(ideia, 0)
    _EST['cont'][ideia] = n + 1
    chave = f'{ideia}#{n}'
    comp = motor.COMPOSICAO or ''
    h = _hist()
    meu = h['videos'].get(comp, {})
    ant = meu.get('escolhas', {}).get(chave)
    if ant in nomes and not REESCOLHE and ant not in _EST['escolhas'].values():
        _EST['escolhas'][chave] = ant
        return ant
    seg = ideia.split(':')[0] if ':' in ideia else ''
    g = _meu_grupo()
    usados_aqui = list(_EST['escolhas'].values())
    rnd = random.Random(bo.semente_video() * 31 + zlib.crc32(chave.encode('utf-8')))
    pont = {}
    for o in nomes:
        bases = base if isinstance(base, (list, tuple, set)) else (base,)
        p = 1000 * usados_aqui.count(o) + (300 if o in bases else 0)
        for vid, reg in h['videos'].items():
            if vid == comp:
                continue
            gv = reg.get('grupo') or {}
            irmao = seg and gv.get(seg) and gv.get(seg) == g.get(seg)
            mesmo_g = gv.get('G') and gv.get('G') == g.get('G')
            for k, ov in (reg.get('escolhas') or {}).items():
                if ov != o:
                    continue
                p += 1
                if k.split('#')[0] == ideia:
                    p += 8 + (40 if irmao else 0) + (12 if mesmo_g else 0)
            # a mesma PEÇA usada fora da receita num irmão também conta (pecas = {opção: (nomes das peças)})
            if pecas and set(pecas.get(o, ())) & set(reg.get('pecas') or ()):
                parente = any(gv.get(x) and gv.get(x) == g.get(x) for x in ('G', 'C', 'A'))
                p += 2 + (15 if parente else 0)
        pont[o] = p + rnd.random() * 0.9
    o = min(nomes, key=lambda x: pont[x])
    _EST['escolhas'][chave] = o
    return o


def _grava_hist():
    comp = motor.COMPOSICAO
    if not comp:
        return
    h = _hist()
    tipos = [an.CEN.get(c.id, ('?', {}))[0] for c in motor.CENAS if c.id not in motor.CENAS_PESSOA_GL]
    h['videos'][comp] = {'grupo': _meu_grupo(), 'escolhas': dict(_EST['escolhas']),
                         'ambientes': tipos, 'transicoes': {k: v[0] for k, v in _EST['trans'].items()},
                         'cameras': dict(_EST['cam']), 'pecas': sorted(set(_EST['pecas']))}
    HIST.write_text(json.dumps(h, ensure_ascii=False, indent=1), encoding='utf-8')
    # aviso de repetição (regra: nenhum ambiente em mais de 3 cenas; 2 seguidas só com ação diferente)
    from collections import Counter
    for tp, n in Counter(tipos).items():
        if n > 3:
            print(f'  AVISO arsenal: ambiente "{tp}" em {n} cenas (máx. 3)')


# ================================================================ TRANSIÇÕES (entrada da cena c)
TRANSICOES = ('tinta', 'pagina', 'iris', 'zoom', 'persiana', 'chicote', 'mancha')


def transicao(c, nome='auto', **op):
    """Transição própria na ENTRADA da cena c (no lugar do mergulho no escuro). nome: tinta (pincelada de tinta varre a
    tela), pagina (folha de papel vira), iris (círculo fecha num ponto e abre no outro; op ponto=(x%, y%) = match cut),
    zoom (a câmera mergulha num ponto da cena anterior; op ponto=), persiana (faixas verticais), chicote (whip pan com
    rastros), mancha (mancha de tinta cresce e encolhe), auto (escolhe sem repetir a anterior). op cor='#...'."""
    if nome == 'auto':
        usadas = [v[0] for v in _EST['trans'].values()]
        cands = [t_ for t_ in TRANSICOES if t_ not in usadas] or [t_ for t_ in TRANSICOES if t_ not in usadas[-2:]]
        nome = escolhe('T:transicao', cands)
    _EST['trans'][c.id] = (nome, op)
    an.SEM_MERGULHO.add(c.id)
    return c


_OV = 'position:absolute;inset:0;z-index:7;pointer-events:none;overflow:hidden'


def _ov(id_, corpo, extra=''):
    return f'<div class="arx" id="{id_}" style="{_OV};{extra}">{corpo}</div>'


def _pincel(cor):
    # pincelada larga com borda irregular (cobre 1080x1920 com folga)
    return (f'<svg viewBox="0 0 1400 1920" preserveAspectRatio="none" style="position:absolute;left:-10%;top:0;width:130%;height:100%">'
            f'<path d="M120 0 C60 220 170 380 90 560 C20 760 150 900 70 1100 C0 1300 140 1460 60 1660 C20 1780 90 1860 80 1920 '
            f'L1320 1920 C1380 1700 1260 1560 1340 1380 C1400 1180 1280 1040 1350 860 C1400 700 1290 520 1360 340 C1390 200 1300 90 1330 0Z" fill="{cor}"/>'
            f'<circle cx="40" cy="300" r="26" fill="{cor}"/><circle cx="20" cy="1240" r="18" fill="{cor}"/><circle cx="1380" cy="980" r="22" fill="{cor}"/></svg>')


def _transicoes_pos():
    cenas = motor.CENAS
    pessoa = set(motor.CENAS_PESSOA_GL) if an.TELA_CHEIA else set()
    for k, c in enumerate(cenas):
        if c.id not in _EST['trans'] or k == 0:
            continue
        nome, op = _EST['trans'][c.id]
        ant = cenas[k - 1]
        T = c.t0
        cor = op.get('cor')
        a_ok = ant.id not in pessoa
        if c.id in pessoa:
            continue
        if nome == 'tinta':
            cor = cor or '#17120E'
            if a_ok:
                ant.html += _ov(f'{ant.id}-trs', _pincel(cor), 'transform:translateX(110%)')
                ant.a(f"tl.fromTo('#{ant.id}-trs',{{xPercent:115}},{{xPercent:0,duration:0.3,ease:'power2.in'}},{q(T - 0.3)});")
            c.html += _ov(f'{c.id}-tre', _pincel(cor))
            c.a(f"tl.fromTo('#{c.id}-tre',{{xPercent:0}},{{xPercent:-118,duration:0.42,ease:'power2.out'}},{q(T)});")
            an.som(max(0.0, T - 0.3), 'swish', 0.2)
        elif nome == 'pagina':
            cor = cor or '#EADCB8'
            folha = (f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,{cor} 0%,{cor} 86%,#C9B48A 100%);'
                     f'box-shadow:30px 0 60px rgba(0,0,0,.35)"></div>'
                     f'<div style="position:absolute;inset:0;opacity:.3;background-image:radial-gradient(rgba(90,60,20,.3) 1px,transparent 1.4px);background-size:7px 7px"></div>')
            if a_ok:
                ant.html += _ov(f'{ant.id}-trs', folha, 'overflow:visible;transform-origin:0 50%')
                ant.a(f"tl.fromTo('#{ant.id}-trs',{{rotationY:-100,transformPerspective:2200,transformOrigin:'0% 50%'}},{{rotationY:0,duration:0.3,ease:'power2.in'}},{q(T - 0.3)});")
            c.html += _ov(f'{c.id}-tre', folha, 'overflow:visible')
            c.a(f"tl.fromTo('#{c.id}-tre',{{rotationY:0,transformPerspective:2200,transformOrigin:'100% 50%'}},{{rotationY:100,duration:0.5,ease:'power2.inOut'}},{q(T)});")
            c.a(f"tl.set('#{c.id}-tre',{{opacity:0}},{q(T + 0.5)});")
            an.som(max(0.0, T - 0.25), 'papel', 0.26)
        elif nome == 'iris':
            px, py = op.get('ponto', (50, 62))
            p2 = op.get('ponto2', (px, py))
            if a_ok:
                ant.a(f"tl.fromTo('#{ant.id}-tema',{{clipPath:'circle(150% at {px}% {py}%)'}},{{clipPath:'circle(0% at {px}% {py}%)',duration:0.34,ease:'power2.in'}},{q(T - 0.34)});")
            c.a(f"tl.fromTo('#{c.id}-tema',{{clipPath:'circle(0% at {p2[0]}% {p2[1]}%)'}},{{clipPath:'circle(150% at {p2[0]}% {p2[1]}%)',duration:0.5,ease:'power2.out'}},{q(T)});")
            an.som(max(0.0, T - 0.3), 'whoosh_lento', 0.16)
        elif nome == 'zoom':
            px, py = op.get('ponto', (50, 60))
            if a_ok:
                ant.html += _ov(f'{ant.id}-trs', '', 'background:#F6EBD3;opacity:0')
                ant.a(f"tl.fromTo('#{ant.id}-tema',{{scale:1}},{{scale:2.8,duration:0.32,ease:'power3.in',transformOrigin:'{px}% {py}%'}},{q(T - 0.32)});")
                ant.a(f"tl.fromTo('#{ant.id}-trs',{{opacity:0}},{{opacity:0.85,duration:0.32,ease:'power3.in'}},{q(T - 0.32)});")
            c.html += _ov(f'{c.id}-tre', '', 'background:#F6EBD3')
            c.a(f"tl.fromTo('#{c.id}-tema',{{scale:1.4}},{{scale:1,duration:0.55,ease:'power3.out',transformOrigin:'50% 55%'}},{q(T)});")
            c.a(f"tl.fromTo('#{c.id}-tre',{{opacity:0.85}},{{opacity:0,duration:0.4,ease:'power1.out'}},{q(T)});")
            an.som(max(0.0, T - 0.3), 'transicao', 0.18)
        elif nome == 'persiana':
            cor = cor or '#14203A'
            n = 8
            barras = ''.join(f'<i class="pb" style="position:absolute;top:0;bottom:0;left:{100 * j / n:.3f}%;width:{100 / n + 0.2:.3f}%;background:{cor}"></i>' for j in range(n))
            if a_ok:
                ant.html += _ov(f'{ant.id}-trs', barras)
                ant.a(f"tl.fromTo('#{ant.id}-trs .pb',{{scaleX:0}},{{scaleX:1,duration:0.2,ease:'power2.in',stagger:0.018,transformOrigin:'0% 50%'}},{q(T - 0.33)});")
            c.html += _ov(f'{c.id}-tre', barras)
            c.a(f"tl.fromTo('#{c.id}-tre .pb',{{scaleX:1}},{{scaleX:0,duration:0.24,ease:'power2.out',stagger:0.022,transformOrigin:'100% 50%'}},{q(T)});")
            an.som(max(0.0, T - 0.3), 'swish', 0.18)
        elif nome == 'chicote':
            rastro = ''.join(f'<i style="position:absolute;left:-20%;width:140%;top:{y}%;height:{h}px;background:rgba(246,235,211,{a})"></i>'
                             for y, h, a in ((8, 10, .5), (17, 4, .7), (29, 14, .35), (41, 6, .6), (52, 20, .3), (63, 5, .7), (74, 12, .45), (86, 7, .6), (94, 16, .35)))
            if a_ok:
                ant.html += _ov(f'{ant.id}-trs', rastro, 'opacity:0')
                ant.a(f"tl.fromTo('#{ant.id}-tema',{{x:0}},{{x:-520,duration:0.2,ease:'power2.in'}},{q(T - 0.2)});")
                ant.a(f"tl.fromTo('#{ant.id}-trs',{{opacity:0}},{{opacity:1,duration:0.2}},{q(T - 0.2)});")
            c.html += _ov(f'{c.id}-tre', rastro)
            c.a(f"tl.fromTo('#{c.id}-tema',{{x:520}},{{x:0,duration:0.3,ease:'power3.out'}},{q(T)});")
            c.a(f"tl.fromTo('#{c.id}-tre',{{opacity:1}},{{opacity:0,duration:0.3}},{q(T)});")
            an.som(max(0.0, T - 0.22), 'swish', 0.26)
        elif nome == 'mancha':
            cor = cor or '#1A140F'
            px, py = op.get('ponto', (50, 70))
            blob = (f'<svg viewBox="0 0 400 260" style="position:absolute;left:{px}%;top:{py}%;width:400px;height:260px;margin:-130px 0 0 -200px;overflow:visible">'
                    '<path d="M60 140 C20 90 70 30 140 46 C190 10 270 20 300 60 C370 60 390 130 350 170 C360 230 270 250 220 222 C170 255 90 240 80 200 C30 200 30 160 60 140Z" '
                    f'fill="{cor}"/></svg>')
            if a_ok:
                ant.html += _ov(f'{ant.id}-trs', blob)
                ant.a(f"tl.fromTo('#{ant.id}-trs svg',{{scale:0,rotation:-30}},{{scale:9,rotation:0,duration:0.36,ease:'power2.in'}},{q(T - 0.36)});")
            c.html += _ov(f'{c.id}-tre', blob)
            c.a(f"tl.fromTo('#{c.id}-tre svg',{{scale:9,rotation:0}},{{scale:0,rotation:25,duration:0.45,ease:'power2.out'}},{q(T)});")
            an.som(max(0.0, T - 0.1), 'impacto_ar', 0.2)


# ================================================================ CÂMERA
def camera(c, tipo='push', forca=1.0, origem=None, ease=None):
    """Movimento de câmera da cena (o .cenario inteiro: fundo + ação; o letreiro fica parado). tipo: push (aproxima),
    pull (afasta revelando), tilt_baixo (desce do céu/teto até o chão), tilt_cima, pan_dir, pan_esq, dolly (aproxima
    andando de lado). forca 0.5–1.5. Cuidado: com push forte, balão perto da borda sai da margem — revise a folha."""
    f = forca
    pre = {
        'push': ("{scale:1}", f"{{scale:{1 + 0.16 * f:.3f}}}", origem or '50% 72%', 'power1.inOut'),
        'pull': (f"{{scale:{1 + 0.2 * f:.3f}}}", "{scale:1}", origem or '50% 70%', 'power2.out'),
        'tilt_baixo': (f"{{scale:1.22,y:{420 * f:.0f}}}", "{scale:1.22,y:0}", origem or '50% 100%', 'power1.inOut'),
        'tilt_cima': ("{scale:1.22,y:0}", f"{{scale:1.22,y:{380 * f:.0f}}}", origem or '50% 100%', 'power1.inOut'),
        'pan_dir': (f"{{scale:1.18,x:{90 * f:.0f}}}", f"{{scale:1.18,x:{-90 * f:.0f}}}", origem or '50% 60%', 'none'),
        'pan_esq': (f"{{scale:1.18,x:{-90 * f:.0f}}}", f"{{scale:1.18,x:{90 * f:.0f}}}", origem or '50% 60%', 'none'),
        'dolly': (f"{{scale:1.04,x:{70 * f:.0f}}}", f"{{scale:{1.04 + 0.2 * f:.3f},x:{-50 * f:.0f}}}", origem or '50% 70%', 'power1.inOut'),
    }[tipo]
    an.CAM[c.id] = {'de': pre[0], 'para': pre[1], 'origem': pre[2], 'ease': ease or pre[3]}
    _EST['cam'][c.id] = tipo
    return c


def tremor(c, t, dur=0.5, amp=0.7):
    """Tremida de impacto (gira o .cenario de leve, ± amp graus)."""
    t = _T(t)
    n = max(2, int(dur / 0.05))
    c.a(f"tl.fromTo('#{c.id} .cenario',{{rotation:-{amp}}},{{rotation:{amp},duration:0.05,ease:'none',yoyo:true,repeat:{n}}},{q(t)});")
    c.a(f"tl.to('#{c.id} .cenario',{{rotation:0,duration:0.08}},{q(t + 0.05 * (n + 1))});")
    an.som(t, 'impacto', 0.24)
    return ''


# ================================================================ VIDA AUTOMÁTICA das classes do arsenal
def _vida_pos():
    """Classes vivas dos ambientes/peças do arsenal (o _vida do animada não as conhece): ar-gira (data-v graus/s,
    data-o 'x y'), ar-fuma (fumaça subindo), ar-onda (água), ar-chuva/ar-neve, ar-anda (data-v px/s), ar-pisca,
    ar-balanca (data-a graus, data-o), ar-bob (sobe e desce). Uma vez por cena, de c.t0 até o fim."""
    cenas = motor.CENAS
    fims = [cenas[k + 1].t0 for k in range(len(cenas) - 1)] + [motor.DUR]
    for c, t1 in zip(cenas, fims):
        h = c.html
        if 'ar-' not in h:
            continue
        D = max(0.3, t1 - c.t0)
        t0 = c.t0
        # gira: um seletor por (v, o) distinto
        for v, o in sorted(set(re.findall(r'class="ar-gira" data-v="([-\d.]+)" data-o="([-\d. ]+)"', h))):
            c.a(f"tl.fromTo('#{c.id} .ar-gira[data-v=\"{v}\"][data-o=\"{o}\"]',{{rotation:0}},{{rotation:{float(v) * D:.0f},duration:{q(D)},ease:'none',svgOrigin:'{o}'}},{q(t0)});")
        if 'class="ar-fuma"' in h:
            c.a(f"tl.fromTo('#{c.id} .ar-fuma',{{y:0,scale:0.5,opacity:0}},{{keyframes:{{y:[0,-90,-200],scale:[0.5,1.1,1.7],opacity:[0,0.7,0]}},duration:2.4,ease:'none',repeat:{max(1, int(D / 2.4) + 1)},stagger:{{each:0.6,repeat:{max(1, int(D / 2.4) + 1)}}},transformOrigin:'50% 50%'}},{q(t0 - 1.2)});")
        if 'class="ar-onda"' in h:
            c.a(f"tl.fromTo('#{c.id} .ar-onda',{{x:-18}},{{x:18,duration:1.3,ease:'sine.inOut',yoyo:true,repeat:{max(1, int(D / 1.3))},stagger:0.17}},{q(t0)});")
        if 'class="ar-chuva"' in h:
            c.a(f"tl.fromTo('#{c.id} .ar-chuva',{{y:-260}},{{y:260,duration:0.42,ease:'none',repeat:{max(1, int(D / 0.42))}}},{q(t0)});")
        if 'class="ar-neve"' in h:
            c.a(f"tl.fromTo('#{c.id} .ar-neve',{{y:-300,x:-20}},{{y:300,x:20,duration:3.2,ease:'none',repeat:{max(1, int(D / 3.2) + 1)}}},{q(t0 - 1.6)});")
        for v in sorted(set(re.findall(r'class="ar-anda" data-v="([-\d.]+)"', h))):
            c.a(f"tl.fromTo('#{c.id} .ar-anda[data-v=\"{v}\"]',{{x:0}},{{x:{float(v) * D:.0f},duration:{q(D)},ease:'none'}},{q(t0)});")
        if 'class="ar-pisca"' in h:
            c.a(f"tl.fromTo('#{c.id} .ar-pisca',{{opacity:1}},{{opacity:0.25,duration:0.5,ease:'steps(1)',yoyo:true,repeat:{max(1, int(D / 0.5))},stagger:{{each:0.31,repeat:0}}}},{q(t0)});")
        for a_, o in sorted(set(re.findall(r'class="ar-balanca" data-a="([\d.]+)" data-o="([-\d. ]+)"', h))):
            c.a(f"tl.fromTo('#{c.id} .ar-balanca[data-a=\"{a_}\"][data-o=\"{o}\"]',{{rotation:-{a_}}},{{rotation:{a_},duration:1.5,ease:'sine.inOut',yoyo:true,repeat:{max(1, int(D / 1.5))},svgOrigin:'{o}',stagger:0.3}},{q(t0)});")
        if 'class="ar-bob"' in h:
            c.a(f"tl.fromTo('#{c.id} .ar-bob',{{y:0}},{{y:-10,duration:1.1,ease:'sine.inOut',yoyo:true,repeat:{max(1, int(D / 1.1))},stagger:0.35}},{q(t0)});")
        # capítulos coloridos do arsenal: raios girando e pulsando como o capítulo padrão
        tipo = an.CEN.get(c.id, ('', {}))[0]
        if tipo in ('capitulo_vermelho', 'capitulo_verde'):
            c.a(f"tl.fromTo('#{c.id} .raios',{{rotation:0}},{{rotation:{16 * D:.0f},duration:{q(D)},ease:'none'}},{q(t0)});")
            c.a(f"tl.fromTo('#{c.id} .raios',{{opacity:0.7}},{{opacity:1,duration:0.6,yoyo:true,repeat:{max(1, int(D / 0.6))},ease:'sine.inOut'}},{q(t0)});")


def _pre():
    # capítulos coloridos e cartela preta: zoom mais forte que o padrão (cartela nunca quase parada)
    for c in motor.CENAS:
        tipo = an.CEN.get(c.id, ('', {}))[0]
        if tipo in ('capitulo_vermelho', 'capitulo_verde', 'preto') and c.id not in an.CAM:
            an.CAM[c.id] = {'de': '{scale:1}', 'para': '{scale:1.12}', 'origem': '50% 45%', 'ease': 'none'}


_CSS_AR = """
.t-capitulo_vermelho .data .dn,.t-capitulo_verde .data .dn,.t-preto .data .dn,.t-porto_tarde .data .dn,.t-tunel .data .dn{color:#F2B544;text-shadow:0 4px 18px rgba(0,0,0,.5)}
.t-capitulo_vermelho .data .dl,.t-capitulo_verde .data .dl,.t-preto .data .dl,.t-tunel .data .dl{color:#F6EBD3}
.t-capitulo_vermelho .data .mancha,.t-capitulo_verde .data .mancha,.t-preto .data .mancha{fill:#F2B544;fill-opacity:.12}
.arx svg{display:block}
"""


def _yt_vertical():
    """YT de fonte VERTICAL (celular, sem base_h.mov: b53b, g22): o painel da pessoa ao lado (840x1080) usava o recorte
    16:9 do vertical (1620x912) e ficava um close cortando a testa. Aqui o painel ganha um vídeo próprio, 840x1080 tirado
    da largura inteira do vertical (1620x2083: cabeça e ombros com folga); nas cenas da pessoa em tela cheia continua o 16:9."""
    if motor.FORMATO != 'YT' or not motor.GNN:
        return
    w = motor.RAIZ / 'work' / motor.GNN
    if (w / 'base_h.mov').exists() or not (w / 'base.mov').exists():
        return
    import pessoa_cheio
    pub = motor.AQUI / 'public'
    saida = pub / 'pessoa-YT-lado.mp4'
    if not saida.exists():
        pessoa_cheio._gerar_vertical(motor.GNN, pub, saida, (840, 1080), pos_rosto=0.36)
    elif not pessoa_cheio.cor_pessoa.ok(saida):   # 12/11: recorte antigo em BT.709 (render do HF amarelava a pele)
        pessoa_cheio.cor_pessoa.converter(saida)
    arq = pub / 'index.html'
    s = arq.read_text(encoding='utf-8')
    if 'id="pessoalado"' in s:
        return
    tag = (f'<video id="pessoalado" src="pessoa-YT-lado.mp4" muted playsinline data-start="0" data-duration="{motor.DUR}" '
           f'data-track-index="2" style="position:absolute;left:1080px;top:0;width:840px;height:1080px;object-fit:cover"></video>')
    m = re.search(r'<video id="pessoa" [^>]*></video>', s)
    if not m:
        return
    s = s[:m.end()] + chr(10) + '      ' + tag + s[m.end():]
    cenas = motor.CENAS
    fims = [cenas[k + 1].t0 for k in range(len(cenas) - 1)] + [motor.DUR]
    js = ["tl.set('#pessoalado',{opacity:1},0);"]
    for c, t1 in zip(cenas, fims):
        if c.id in motor.CENAS_PESSOA_GL:
            js.append(f"tl.set('#pessoalado',{{opacity:0}},{c.t0});tl.set('#pessoalado',{{opacity:1}},{q(t1)});")
    s = s.replace(chr(10) + '// c01 ', chr(10) + ''.join(js) + chr(10) + '// c01 ', 1)
    arq.write_text(s, encoding='utf-8')


def _fim_css():
    arq = motor.AQUI / 'public/index.html'
    s = arq.read_text(encoding='utf-8')
    if '/*arsenal*/' not in s:
        s = s.replace('</head>', f'<style>/*arsenal*/{_CSS_AR}</style></head>', 1)
        arq.write_text(s, encoding='utf-8')


# ================================================================ REGISTRO (ganchos do animada.py + ambientes)
def _registra():
    if getattr(an, '_ARSENAL', False):
        return
    an._ARSENAL = True
    an.GANCHOS_PRE.append(_pre)
    an.GANCHOS_POS.append(_transicoes_pos)
    an.GANCHOS_POS.append(_vida_pos)
    an.GANCHOS_FIM.append(_fim_css)
    an.GANCHOS_FIM.append(_yt_vertical)
    an.GANCHOS_FIM.append(_grava_hist)
    import arsenal_fundos as af
    an.TEMAS.update(af.TEMAS)
    an.SALAS = tuple(an.SALAS) + tuple(t_ for t_ in af.TEMAS if t_ not in an.SALAS)
    orig = bo.fundo

    def fundo(tipo, seed, op=None):
        if tipo in af.FUNDOS:
            return af.FUNDOS[tipo](random.Random(seed), op or {})
        return orig(tipo, seed, op)
    bo.fundo = fundo


_registra()
from arsenal_cenas import *  # noqa: E402,F401,F403
from arsenal_info import *  # noqa: E402,F401,F403
from arsenal_receitas import RECEITAS, receita  # noqa: E402,F401


# ================================================================ uso das peças (pra receita não repetir uma peça já usada à mão)
def _conta_uso(nome, fn):
    import functools

    @functools.wraps(fn)
    def w(*a, **k):
        _EST['pecas'].append(nome)
        return fn(*a, **k)
    w._arsenal = True
    return w


def _instala_contagem():
    import arsenal_cenas as _ac
    import arsenal_info as _ai
    g = globals()
    for nome in list(_ac.__all__) + list(_ai.__all__):
        if not getattr(g[nome], '_arsenal', False):
            g[nome] = _conta_uso(nome, g[nome])
    for nome in ('escritorio', 'fachada', 'pote', 'crescimento_predio', 'sala_noite', 'celular_close', 'campanhas', 'chegada',
                 'sala_reuniao', 'operacao', 'grafico_pergaminho', 'mapa', 'quarto_ia', 'videochamada', 'copa', 'recepcao',
                 'deposito', 'dono', 'casa_fora', 'ponto_onibus', 'documento'):
        f = getattr(bo, nome, None)
        if f and not getattr(f, '_arsenal', False):
            setattr(bo, nome, _conta_uso(nome, f))


def pecas_usadas():
    return list(_EST['pecas'])


_instala_contagem()
