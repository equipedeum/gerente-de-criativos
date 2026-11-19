"""YouTube dinâmico (menu 11): monta a edição de um vídeo 16:9 da pessoa falando, sem render.

    ./py work/yt/montar.py <id>            (cfg em work/yt/cfg/<id>.py; molde work/yt/cfg/_modelo.py)

Entrada: work/<id>/ do preparo com `--sem-corte --resolucao-original` (base_h.mov na resolução da câmera, 4K ideal,
voice.wav, words_cut.json, face_track.json). Tudo no cfg é em TEMPO DO PRÉ-CORTE (segundos do voice.wav).

Faz:
  1. trechos que ficam: tira a `limpeza` (tropeço/repetição), encurta respiros > 0,85 s pra 0,52 s e acerta a pausa de
     cada capítulo no tamanho do cartão; tudo em quadros, pra áudio e vídeo andarem juntos;
  2. a fala editada em -16 LUFS (medido em estéreo) + efeitos sonoros discretos -> remotion/public-yt/<id>/mix.wav;
  3. os planos (aberto A / médio M / fechado F / ênfase E / painel P0-P2 / selo S), SEMPRE trocando no começo de
     frase (dentro da pausa), zoom diferente em toda troca (>= 10 %) e nada parado > 4 s;
  4. painéis, selos, capítulos e cartão final em quadros + cores/fontes/logo da marca (projeto.json)
     -> remotion/public-yt/<id>/edl.json (a pasta public enxuta do vídeo: edl, mix, fontes, logo);
  5. relatório em work/<id>/yt/relatorio.txt (limpeza, capítulos, painéis, planos e as conferências).
Depois: bash work/yt/folha.sh <id> folha|trans (revisão) e, com a fila livre, bash work/yt/render.sh <id>.
"""
import importlib.util, json, os, re, shutil, subprocess, sys, wave
from fractions import Fraction
import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "work"))
import sistema  # noqa: E402

FF = sistema.FF
SR = 48000
PAUSA_MIN, PAUSA_ALVO = 0.85, 0.52     # respiro maior que isso vira 0,52 s (0,22 depois da fala + 0,30 antes)
FIM_EXTRA = 2.0                        # cartão final depois da última palavra
ID = sys.argv[1]
_spec = importlib.util.spec_from_file_location("cfg_yt", f"work/yt/cfg/{ID}.py")
_m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)
C = dict(_m.CFG)
W_DIR = f"work/{ID}"
PUB = f"remotion/public-yt/{ID}"
OUT_DIR = f"{W_DIR}/yt"
os.makedirs(PUB, exist_ok=True); os.makedirs(OUT_DIR, exist_ok=True)

# fps da gravação (o vídeo final sai no mesmo fps, sem converter)
import av  # noqa: E402
_c = av.open(f"{W_DIR}/base_h.mov"); _vs = _c.streams.video[0]
FPS_Q = Fraction(_vs.average_rate).limit_denominator(1001); SRC_W, SRC_H = _vs.width, _vs.height; _c.close()
FPS = float(FPS_Q)
assert abs(SRC_W / SRC_H - 16 / 9) < 0.02, f"base_h.mov tem que ser 16:9 (é {SRC_W}x{SRC_H}); prepare com --resolucao-original"


def ler_wav(p):
    w = wave.open(p); n = w.getnframes(); ch = w.getnchannels(); sr = w.getframerate()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1: a = a.reshape(-1, ch).mean(1)
    if sr != SR:   # reamostra (o voice.wav do preparo e os sons do projeto já vêm em 48 kHz)
        tmp = f"{OUT_DIR}/_rs.wav"
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", p, "-ac", "1", "-ar", str(SR), tmp], check=True)
        return ler_wav(tmp)
    return a


def grava_wav(p, a, ch=1):
    a = np.clip(a, -1, 1)
    if ch == 2: a = np.repeat(a[:, None], 2, axis=1).reshape(-1)
    w = wave.open(p, "wb"); w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((a * 32767).astype(np.int16).tobytes()); w.close()


def silencios(a, thr=-38.0, minlen=0.18):
    hop = SR // 100; fr = len(a) // hop
    db = 20 * np.log10(np.sqrt((a[:fr * hop].reshape(fr, hop) ** 2).mean(1)) + 1e-9)
    db = np.convolve(db, np.ones(3) / 3, mode="same")
    q = db < thr; runs = []; i = 0
    while i < fr:
        if q[i]:
            j = i
            while j < fr and q[j]: j += 1
            if (j - i) * 0.01 >= minlen: runs.append((i * 0.01, j * 0.01))
            i = j
        else: i += 1
    return runs, db


def lufs(p):
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    s = r[r.rfind("Summary:"):]
    I = float(re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1))
    tp = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", s)
    return I, (float(tp.group(1)) if tp and tp.group(1) != "-inf" else None)


# ------------------------------------------------------------------ 1. trechos
voz = ler_wav(f"{W_DIR}/voice.wav"); DUR = len(voz) / SR
PAL = json.load(open(f"{W_DIR}/words_cut.json", encoding="utf-8"))
C.setdefault("ini", max(0.0, PAL[0]["s"] - 0.40))
C.setdefault("fim", min(DUR, PAL[-1]["e"] + 0.30))
for k in ("limpeza", "capitulos", "paineis", "selos", "enfase"): C.setdefault(k, [])
runs, _ = silencios(voz)

remover = [(0, C["ini"]), (C["fim"], DUR + 1)]
for a, b, _ in C["limpeza"]: remover.append((a, b))
pads = []          # (tempo de inserção, s0, s1): repete um pedaço da própria pausa (tom de sala) pro cartão de capítulo
cap_runs = []
for cp in C["capitulos"]:
    cp.setdefault("alvo", 1.30)
    r = [(s, e) for s, e in runs if s - 0.05 <= cp["pausa"] <= e + 0.05]
    assert r, f"capítulo sem pausa perto de {cp['pausa']} s (pausa = um instante DENTRO do silêncio antes da 1ª palavra)"
    s, e = r[0]; cap_runs.append((s, e)); alvo = cp["alvo"]
    if e - s > alvo: remover.append((s + 0.40, e - (alvo - 0.40)))   # emenda 0,40 s depois da fala: já embaixo do cartão
    elif e - s < alvo:
        falta = alvo - (e - s); m = (s + e) / 2
        p0, p1 = max(s + 0.025, m - falta / 2), min(e - 0.025, m + falta / 2)
        pads.append((min(s + 0.42, e - 0.05), p0, p1))
trims = []
for s, e in runs:
    if e - s < PAUSA_MIN or s < C["ini"] or e > C["fim"]: continue
    if any(not (e <= a or s >= b) for a, b, _ in C["limpeza"]): continue
    if any(abs(s - cs) < 0.05 for cs, _ in cap_runs): continue
    remover.append((s + 0.22, e - 0.30)); trims.append((s, e))

remover.sort(); mrg = []
for a, b in remover:
    if mrg and a <= mrg[-1][1]: mrg[-1] = (mrg[-1][0], max(mrg[-1][1], b))
    else: mrg.append((a, b))
ficam = []; t = 0.0
for a, b in mrg:
    if a > t: ficam.append((t, a))
    t = max(t, b)
if t < DUR: ficam.append((t, DUR))
segs = []
for s0, s1 in ficam:
    pts = sorted(p for p in pads if s0 < p[0] < s1)
    cur = s0
    for m, p0, p1 in pts:
        segs.append(dict(s0=cur, s1=m, pad=False)); segs.append(dict(s0=p0, s1=p1, pad=True)); cur = m
    segs.append(dict(s0=cur, s1=s1, pad=False))

o = 0
for sg in segs:
    sg["f0"] = int(round(sg["s0"] * FPS)); sg["f1"] = int(round(sg["s1"] * FPS))
    sg["o0"] = o; o += sg["f1"] - sg["f0"]; sg["o1"] = o
segs = [sg for sg in segs if sg["o1"] > sg["o0"]]
FALA_FIM = segs[-1]["o1"]
TOTAL = FALA_FIM + int(round(FIM_EXTRA * FPS))


def out_f(t):
    """tempo do pré-corte -> quadro do vídeo editado (fora dos trechos: vai pro começo do próximo)."""
    f = t * FPS
    for sg in segs:
        if sg["pad"]: continue
        if sg["f0"] <= f < sg["f1"]: return int(round(sg["o0"] + f - sg["f0"]))
        if f < sg["f0"]: return sg["o0"]
    return FALA_FIM


def src_t(of):
    for sg in segs:
        if sg["o0"] <= of < sg["o1"]: return (sg["f0"] + of - sg["o0"]) / FPS
    return segs[-1]["f1"] / FPS


# ------------------------------------------------------------------ 2. áudio da fala
fala = np.zeros(int(round(TOTAL / FPS * SR)) + SR, np.float32)
FADE = int(0.005 * SR); rampa = np.sin(np.linspace(0, np.pi / 2, FADE)) ** 2
for i, sg in enumerate(segs):
    a0 = int(round(sg["o0"] / FPS * SR)); a1 = int(round(sg["o1"] / FPS * SR)); n = a1 - a0
    s0 = int(round(sg["f0"] / FPS * SR))
    pedaco = voz[s0:s0 + n].copy()
    if len(pedaco) < n: pedaco = np.pad(pedaco, (0, n - len(pedaco)))
    if i > 0: pedaco[:FADE] *= rampa
    if i < len(segs) - 1: pedaco[-FADE:] *= rampa[::-1]
    fala[a0:a1] = pedaco
# cauda do cartão final: tom de sala do último silêncio, repetido e sumindo
ult = ([r for r in runs if r[1] - r[0] >= 0.3 and r[0] < C["fim"]] or [(0.0, 0.3)])[-1]
tom = voz[int((ult[0] + 0.05) * SR):int((ult[1] - 0.05) * SR)]
a0 = int(round(FALA_FIM / FPS * SR)); a1 = int(round(TOTAL / FPS * SR))
if len(tom) > 100:
    rep = np.tile(np.concatenate([tom, tom[::-1]]), int((a1 - a0) / (2 * len(tom))) + 2)[:a1 - a0]
    rep *= np.linspace(1, 0, len(rep)) ** 1.5; rep[:FADE] *= rampa
    fala[a0:a1] = rep
fala = fala[:a1]

# medido em ESTÉREO (como o YouTube mede o arquivo final): mono duplicado soma +3 dB no ebur128
tmp = f"{OUT_DIR}/_fala_bruta.wav"; grava_wav(tmp, fala, ch=2)
I0, _ = lufs(tmp)
ganho = -16.0 - I0
for _ in range(3):
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", tmp, "-af",
                    f"volume={ganho:.2f}dB,alimiter=limit=0.84:attack=4:release=60:level=disabled",
                    "-ar", str(SR), "-ac", "2", f"{OUT_DIR}/_fala16.wav"], check=True)
    I1, _ = lufs(f"{OUT_DIR}/_fala16.wav")
    if abs(I1 + 16) < 0.1: break
    ganho += -16.0 - I1
fala16 = ler_wav(f"{OUT_DIR}/_fala16.wav")

# ------------------------------------------------------------------ 3. frases no vídeo editado -> pontos de corte
oruns, odb = silencios(fala16[:int(FALA_FIM / FPS * SR)], thr=-38.0 + ganho, minlen=0.16)
cand = []
for s, e in oruns:
    c = int(np.floor((e - 0.07) * FPS))
    if c > s * FPS + 1 and c > 0: cand.append(c)
juntas = [sg["o0"] for sg in segs[1:]]


def fala_em(of):          # quadro com voz? (nenhum corte de plano pode cair no meio de palavra)
    i = int(of / FPS * 100)
    return odb[max(0, i - 1):i + 2].max() > -32.0 + ganho if i < len(odb) else False


# ------------------------------------------------------------------ 4. eventos (painéis, selos, capítulos, fim)
paineis = []
for p in C["paineis"]:
    o0, o1 = out_f(p["t0"]), out_f(p["t1"])
    itens = []
    for it in p["itens"]:
        d = dict(it); d["o"] = max(o0 + 3, out_f(it["t"])); d.pop("t")
        if "risco" in d: d["risco"] = out_f(d["risco"])
        itens.append(d)
    paineis.append(dict(o0=o0, o1=o1, rotulo=p.get("rotulo", ""), itens=itens, ate_capitulo=p.get("ate_capitulo", False)))
selos = [dict(o0=out_f(s["t0"]), o1=out_f(s["t1"]), texto=s["texto"], tam=s.get("tam", 96), legenda=s.get("legenda", "")) for s in C["selos"]]
caps = []
for cp, (s, e) in zip(C["capitulos"], cap_runs):
    ps = out_f(s); pe = ps + int(round(cp["alvo"] * FPS))      # a pausa ficou com 'alvo' s (encurtada ou com pad)
    caps.append(dict(o0=ps + 2, o1=pe + 3, num=cp["num"], titulo=cp["titulo"]))
fim = dict(o0=FALA_FIM - int(round(0.30 * FPS)) + 1, o1=TOTAL)

# ------------------------------------------------------------------ 5. planos
q = lambda s: int(round(s * FPS))   # segundos -> quadros (as constantes abaixo foram medidas a 29,97)
forcado = {}      # quadro -> tipo
supr = []         # faixas sem corte
cobertos = [(cp["o0"] + 9, cp["o1"] - 9) for cp in caps] + [(fim["o0"] + 9, TOTAL)]
juntas = [j for j in juntas if not any(a <= j <= b for a, b in cobertos)]   # emenda embaixo do cartão não vira troca
for cp in caps:
    meio = (cp["o0"] + 9 + cp["o1"] - 9) // 2; forcado[meio] = "A"; supr.append((cp["o0"] - 20, cp["o1"] + 25))
forcado[fim["o0"] + 10] = "A"
for p in paineis:
    near = [c for c in juntas if abs(c - p["o0"]) <= 14] or [c for c in cand if abs(c - p["o0"]) <= 8]
    if near: forcado[min(near, key=lambda c: abs(c - p["o0"]))] = "P"   # sem começo de frase perto: entra sem corte
for s in selos:
    antes = [c for c in cand + juntas if s["o0"] - q(2.5) <= c <= s["o0"] + 3]
    assert antes, f"selo em {s['o0'] / FPS:.2f} s sem começo de frase até 2,5 s antes: mude o t0 do selo"
    f = max(antes)
    forcado[f] = "S"; supr.append((f + 1, s["o1"] + 4))
for t in C["enfase"]:
    of = out_f(t); near = [c for c in cand if abs(c - of) <= 12]
    if near: forcado[min(near, key=lambda c: abs(c - of))] = "E"
    else: print(f"  [aviso] ênfase {t}s sem começo de frase perto")


def suprimido(c): return any(a <= c <= b for a, b in supr)


todos = sorted(set(cand) | set(juntas) | set(forcado))
cortes = [0]; MIN, BOM, MAX = q(1.2), q(3.2), q(5.8)
obrig = sorted(set(juntas) | set(forcado))
for i, c in enumerate(todos):
    if c <= cortes[-1] or c >= FALA_FIM: continue
    if c in juntas or c in forcado:
        cortes.append(c); continue
    if suprimido(c): continue
    L = c - cortes[-1]
    prox_obr = next((x for x in obrig if x > c), TOTAL)
    if prox_obr - c < MIN or L < MIN: continue
    prox_cand = next((x for x in todos[i + 1:] if not suprimido(x)), TOTAL)
    if L >= BOM or (L >= q(2.0) and prox_cand - cortes[-1] > MAX):
        cortes.append(c)
cortes.append(TOTAL)
lim = q(0.5); i = 1   # nada de plano-relâmpago: dois cortes a < 0,5 s -> fica o obrigatório (emenda)
while i < len(cortes) - 1:
    a, b = cortes[i], cortes[i + 1] if i + 1 < len(cortes) - 1 else None
    if b is not None and b - a < lim:
        fica, sai = (a, b) if (a in juntas and b not in juntas) else (b, a) if (b in juntas and a not in juntas) else (a, b)
        if sai in forcado and fica not in forcado: forcado[fica] = forcado[sai]
        cortes.remove(sai); continue
    i += 1


def face_track():
    F = json.load(open(f"{W_DIR}/face_track.json", encoding="utf-8"))
    t = np.array([x["t"] for x in F]); cx = np.array([x["cx"] for x in F], float); cy = np.array([x["cy"] for x in F], float)
    mx, my = np.median(cx), np.median(cy)
    ok = (np.abs(cx - mx) < 0.18 * SRC_W) & (np.abs(cy - my) < 0.18 * SRC_H)   # descarta rosto falso (quadro, cartaz)
    return t[ok], cx[ok], cy[ok]


ft, fcx, fcy = face_track()


def rosto(o0, o1):
    ts = [src_t(f) for f in range(o0, o1, 3)]
    sel = np.zeros_like(ft, bool)
    for x in ts: sel |= np.abs(ft - x) < 0.06
    if sel.sum() < 2: sel = np.abs(ft - ts[len(ts) // 2]) < 1.0
    if sel.sum() < 1: return float(np.median(fcx)), float(np.median(fcy))
    return float(np.median(fcx[sel])), float(np.median(fcy[sel]))


def painel_em(f):
    return next((p for p in paineis if p["o0"] - 16 <= f < p["o1"] - 6), None)


# zoom (início -> fim do plano). Fonte 1080p: zoom > 1,2 amolece a imagem — o 4K aguenta tudo.
ZOOM = dict(A=(1.0, 1.045), M=(1.18, 1.23), F=(1.32, 1.32), E=(1.42, 1.44), P0=(1.0, 1.035), P1=(1.15, 1.18), P2=(1.32, 1.34), S=(1.0, 1.02))


def coberto(f): return any(a <= f <= b for a, b in cobertos)


def zz(tipo, L):
    z0, z1 = ZOOM[tipo]
    if tipo in ("A", "P0") and L <= 3.2: z1 = z0
    if tipo == "F" and L > 3.6: z1 = 1.37
    return z0, z1


inicio_painel = {p["o0"] for p in paineis}
def continua(c): return c not in juntas and any(abs(c - p0) <= 14 for p0 in inicio_painel)


opcoes = []
for k in range(len(cortes) - 1):
    a, b = cortes[k], cortes[k + 1]; f = forcado.get(a)
    if f in ("S", "E", "A") or a == 0: op = [f or "A"]
    elif painel_em(a) is not None: op = ["P0", "P1", "P2"]
    else: op = ["A", "M", "F"]
    opcoes.append(op)


def custo_un(k, t):
    L = (cortes[k + 1] - cortes[k]) / FPS
    return {"F": 0.0 if L < 3.0 else 0.8, "M": 0.0 if L >= 2.4 else 0.6, "P2": 1.5}.get(t, 0.0)


def custo_tr(k, ta, tb):      # troca do plano k-1 (ta) pro k (tb): zoom parecido = pulo de imagem
    c = cortes[k]
    if coberto(c): return 0.0
    La = (cortes[k] - cortes[k - 1]) / FPS; Lb = (cortes[k + 1] - cortes[k]) / FPS
    za, zb = zz(ta, La)[1], zz(tb, Lb)[0]
    r = max(za, zb) / min(za, zb)
    if r >= 1.10: return 0.0
    if tb == "P0" and continua(c) and za < 1.10: return 0.0   # painel entrando sem emenda: a imagem só desliza
    return 100.0


INF = 1e9; n = len(opcoes)
best = [{} for _ in range(n)]
for t in opcoes[0]: best[0][(t, None)] = (custo_un(0, t), None)
for k in range(1, n):
    for t in opcoes[k]:
        for (tp, tpp), (cst, _) in best[k - 1].items():
            v = cst + custo_un(k, t) + custo_tr(k, tp, t) + (0.3 if tpp == t and t not in ("A", "P0", "P1", "P2") else 0.0)
            key = (t, tp)
            if v < best[k].get(key, (INF,))[0]: best[k][key] = (v, (tp, tpp))
key = min(best[-1], key=lambda x: best[-1][x][0]); tipos = [None] * n
for k in range(n - 1, -1, -1):
    tipos[k] = key[0]; key = best[k][key][1] if best[k][key][1] is not None else None
    if key is None: break
planos = []
for k in range(n):
    a, b = cortes[k], cortes[k + 1]; z0, z1 = zz(tipos[k], (b - a) / FPS); fx, fy = rosto(a, b)
    if tipos[k] == "P0" and k > 0 and continua(a) and planos[-1]["z1"] < 1.10:
        z0 = planos[-1]["z1"]; z1 = z0 + 0.03; fx, fy = planos[-1]["fx"], planos[-1]["fy"]   # mesma imagem, só desliza
    planos.append(dict(o0=a, o1=b, tipo=tipos[k], z0=z0, z1=z1, fx=round(fx), fy=round(fy)))
saltos = []
for p1, p2 in zip(planos, planos[1:]):
    r = max(p1["z1"], p2["z0"]) / min(p1["z1"], p2["z0"])
    if r < 1.10 and not coberto(p2["o0"]): saltos.append((p2["o0"], round(r, 3), p1["tipo"], p2["tipo"]))

# ------------------------------------------------------------------ 6. efeitos sonoros (só com evento visível)
SFX = []  # (quadro, arquivo, dB)
def sfx(f, nome, db): SFX.append((int(f), nome, db))


for p in paineis:
    sfx(p["o0"], "sfx-animada/swish.wav", -5)
    for it in p["itens"]:
        if it["o"] - p["o0"] > 6:
            nome = {"check": ("sfx-earshot/tique.wav", -21), "chip": ("sfx-earshot/pop.wav", -15),
                    "passo": ("sfx-earshot/pop.wav", -14), "infinito": ("sfx-earshot/pop.wav", -15),
                    "seta": ("sfx-animada/swish.wav", -6), "numero": ("sfx-earshot/pop.wav", -14)}.get(it["tipo"], ("sfx-earshot/pop.wav", -17))
            sfx(it["o"], *nome)
        if "risco" in it: sfx(it["risco"], "sfx-earshot/tesoura.wav", -13)
for s in selos: sfx(s["o0"], "sfx-earshot/carimbo.wav", -11)
for cp in caps:
    sfx(cp["o0"] - 2, "sfx-earshot/whoosh.wav", -5)
    sfx(cp["o0"] + 12, "sfx-earshot/pop.wav", -14)
    sfx(cp["o1"] - 11, "sfx-animada/whoosh_lento.wav", -17)
sfx(fim["o0"] - 2, "sfx-earshot/whoosh.wav", -6)
sfx(fim["o0"] + 14, "sfx-animada/glock.wav", -17)

mix = fala16.copy()
for f, nome, db in SFX:
    s = ler_wav(f"remotion/public/{nome}") * 10 ** (db / 20)
    a0 = int(round(f / FPS * SR)); a1 = min(len(mix), a0 + len(s))
    if a1 > a0: mix[a0:a1] += s[:a1 - a0]
tmpm = f"{OUT_DIR}/_mix_bruto.wav"; grava_wav(tmpm, mix * 0.7, ch=2)
Im, _ = lufs(tmpm); g = -16.0 - Im
for _ in range(3):       # nivela o conjunto (fala + efeitos) em -16 LUFS com limitador em -1,5 dBFS
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", tmpm, "-af",
                    f"volume={g:.2f}dB,alimiter=limit=0.84:attack=4:release=60:level=disabled",
                    "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", f"{PUB}/mix.wav"], check=True)
    I_fin, tp_fin = lufs(f"{PUB}/mix.wav")
    if abs(I_fin + 16) < 0.1: break
    g += -16.0 - I_fin

# ------------------------------------------------------------------ 7. marca (projeto.json) + public enxuto + EDL
pj = sistema.projeto()
os.makedirs(f"{PUB}/fontes", exist_ok=True); os.makedirs(f"{PUB}/logo", exist_ok=True)
FONTES = {   # padrão: fontes livres (OFL) do projeto; o projeto.json troca com fonte_titulo / fonte_italico / fonte_texto
    "serif": pj.get("fonte_titulo") or "ferramentas/fontes/EBGaramond-400.woff2",
    "serif_bold": pj.get("fonte_titulo_bold") or ("" if pj.get("fonte_titulo") else "ferramentas/fontes/EBGaramond-700.woff2"),
    "italico": pj.get("fonte_italico") or "ferramentas/fontes/instrument-serif/InstrumentSerif-Italic.ttf",
    "sans": pj.get("fonte_texto") or "ferramentas/fontes/Inter-Regular.ttf",
    "sans_bold": pj.get("fonte_texto_bold") or ("" if pj.get("fonte_texto") else "ferramentas/fontes/Inter-Bold.ttf"),
}
arq_fontes = {}
for k, src in FONTES.items():
    if not src: continue
    assert os.path.exists(src), f"fonte não encontrada: {src} (projeto.json)"
    dst = f"fontes/{k}{os.path.splitext(src)[1].lower()}"
    shutil.copy(src, f"{PUB}/{dst}"); arq_fontes[k] = dst


def _logo(chave):
    src = pj.get(chave)
    if not src: return ""
    src = os.path.expanduser(src)
    assert os.path.exists(src), f"{chave} não encontrado: {src} (projeto.json)"
    dst = f"logo/{chave}{os.path.splitext(src)[1].lower()}"; shutil.copy(src, f"{PUB}/{dst}"); return dst


marca = dict(
    papel=pj.get("cor_papel") or "#F5EFE4", tinta=pj.get("cor_tinta") or "#1C1A17",
    destaque=pj.get("cor_destaque") or "#059669", cinza=pj.get("cor_cinza") or "#5F584D",
    nome=pj.get("marca") or pj.get("nome_pessoa") or "", slogan=pj.get("slogan") or "",
    logo=_logo("logo"), simbolo=_logo("logo_simbolo"), fontes=arq_fontes)

marca_dagua = []   # símbolo da marca no canto, fora dos cartões (só se o projeto.json tiver logo_simbolo)
ini = 0
for cp in caps + [fim]:
    marca_dagua.append([ini, cp["o0"]]); ini = cp["o1"]
marca_dagua = [m for m in marca_dagua if m[1] - m[0] > 10]

folha = list(range(q(0.5), TOTAL, q(4.0)))
trans = []
for cp in caps: trans += [cp["o0"] - 4, cp["o0"] + 5, cp["o0"] + 14, (cp["o0"] + cp["o1"]) // 2, cp["o1"] - 6, cp["o1"] + 4]
for p in paineis: trans += [p["o0"] + 4, p["o0"] + 14, min(p["o1"] - 2, max([it["o"] for it in p["itens"]] or [p["o0"]]) + 12)]
for s in selos: trans += [s["o0"] + 4, s["o0"] + 16]
trans += [fim["o0"] + 6, fim["o0"] + 30, TOTAL - 2]

edl = dict(id=ID, titulo=C.get("titulo", ID), fps=FPS, fps_q=f"{FPS_Q.numerator}/{FPS_Q.denominator}", frames=TOTAL,
           fala_fim=FALA_FIM, src_w=SRC_W, src_h=SRC_H, marca=marca,
           segs=[dict(o0=s["o0"], o1=s["o1"], f0=s["f0"]) for s in segs],
           planos=planos, paineis=paineis, selos=selos, caps=caps, fim=fim, marca_dagua=marca_dagua,
           folha=folha, trans=sorted(set(t for t in trans if 0 <= t < TOTAL)))
json.dump(edl, open(f"{PUB}/edl.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ 8. relatório + conferências
def mmss(f): t = f / FPS; return f"{int(t // 60)}:{t % 60:05.2f}"


L = [f"{ID} — {edl['titulo']}", f"fonte: {SRC_W}x{SRC_H} a {FPS:.3f} fps" + ("" if SRC_W >= 3000 else "  (AVISO: abaixo de 4K o fechado/ênfase amolecem)"),
     f"duração: {DUR:.2f} s (pré-corte) -> {TOTAL / FPS:.2f} s (editado, com {FIM_EXTRA:.1f} s de cartão final)",
     f"fala: {I0:.1f} LUFS -> ganho {ganho:+.1f} dB; mix final {I_fin:.1f} LUFS, pico {tp_fin} dBFS", "", "LIMPEZA (pré-corte -> editado):"]
for a, b, d in C["limpeza"]: L.append(f"  {a:7.2f}–{b:7.2f} ({b - a:.2f} s) em {mmss(out_f(b))}: {d}")
L.append(f"RESPIROS > {PAUSA_MIN} s encurtados p/ {PAUSA_ALVO} s ({len(trims)}): " + ", ".join(f"{s:.1f}({e - s:.1f}s)" for s, e in trims))
L.append("CAPÍTULOS:")
for cp in caps: L.append(f"  {mmss(cp['o0'])}–{mmss(cp['o1'])}  {cp['num']} {cp['titulo'].replace(chr(10), ' ').replace('*', '')}")
L.append("PAINÉIS / SELOS:")
for p in paineis: L.append(f"  {mmss(p['o0'])}–{mmss(p['o1'])}  [{p['rotulo']}] " + " | ".join(re.sub(r'[*\n]', ' ', it.get('texto', it['tipo'])).strip() for it in p["itens"]))
for s in selos: L.append(f"  {mmss(s['o0'])}–{mmss(s['o1'])}  selo: {s['texto'].replace(chr(10), ' ')} {s['legenda']}")
L.append(f"PLANOS: {len(planos)} (média {np.mean([(p['o1'] - p['o0']) / FPS for p in planos]):.1f} s, maior {max((p['o1'] - p['o0']) / FPS for p in planos):.1f} s)")
ruins = [c for c in cortes[1:-1] if fala_em(c) and c not in juntas]
L.append(f"cortes de plano com voz no quadro: {len(ruins)} " + " ".join(mmss(c) for c in ruins))
parados = [p for p in planos if p["z0"] == p["z1"] and (p["o1"] - p["o0"]) / FPS > 4.0 and not any(c["o0"] <= p["o0"] <= c["o1"] for c in caps) and p["o0"] < FALA_FIM]
L.append(f"trocas de plano com zoom parecido (< 10%): {len(saltos)} " + " ".join(f"{mmss(f)}({a}->{b} {r})" for f, r, a, b in saltos))
L.append(f"planos parados > 4 s: {len(parados)} " + " ".join(f"{mmss(p['o0'])}({(p['o1'] - p['o0']) / FPS:.1f}s {p['tipo']})" for p in parados))
L.append("")
for p in planos: L.append(f"  {mmss(p['o0'])}  {p['tipo']:2s} {p['z0']:.2f}->{p['z1']:.2f}  {(p['o1'] - p['o0']) / FPS:4.1f}s  src {src_t(p['o0']):6.2f}  rosto {p['fx']},{p['fy']}")
if C.get("aviso"): L.append("AVISO: " + C["aviso"])
open(f"{OUT_DIR}/relatorio.txt", "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L[:13 + len(caps) + len(paineis) + len(selos) + 4]))
