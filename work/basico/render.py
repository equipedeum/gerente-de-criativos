"""Versão BÁSICA (menu 1–4): tela cheia, título estilo Edits nos primeiros segundos (opcional) e legenda.
Vale pra fonte vertical (celular, work/<id>/base.mov) e horizontal 16:9 (work/<id>/base_h.mov) — detecta sozinho.

Uso:
    ./py work/basico/render.py <id> [--formatos RL,IN,GL,YT] [--stills t,t] [--blocos]
    ./py work/basico/render.py <id> palavras        -> lista as palavras da transcrição com índice (pra montar repl/frases)
    SUF=" v2" ./py work/basico/render.py <id>       -> versão nova sem sobrescrever a anterior
Config: work/basico/cfg/<id>.py (molde comentado em work/basico/cfg/_modelo.py).
Saída: saidas/basico/<pasta>/RL <pasta>.mp4 (+ "-IN", "-GL", "-YT" com --formatos).

Estilos do menu:
  1) legenda simples            -> leg_estilo=None (1 linha, branca, sombra leve, SEM animação) + sem_titulo=True
  2) legenda simples + título   -> leg_estilo=None + titulo=[...]
  3) legenda animada            -> leg_estilo="serif", leg_chave=False (frase em até 2 linhas montando palavra por palavra) + sem_titulo=True
  4) legenda animada + título   -> leg_estilo="serif", leg_chave=False + titulo=[...]
"""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, "work")
import criativo  # noqa: E402

criativo.TITULO_EDITS = True   # título estilo Edits (Inter Bold branca, traço preto leve)

ID = sys.argv[1]
sys.argv = [sys.argv[0]] + sys.argv[2:]
spec = importlib.util.spec_from_file_location("cfg", f"work/basico/cfg/{ID}.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
B = dict(m.CFG)
pasta = B["pasta"]
D = f"work/{B.get('id', ID)}"   # cfg de variação (ex.: v01b) pode reaproveitar o preparo de outro id
B.setdefault("id", ID)
WORDS = criativo.carregar_palavras(D, B.get("repl", {}))

if sys.argv[1:2] == ["palavras"]:
    print(" ".join(f"{i}:{w['w']}" for i, w in enumerate(WORDS)))
    sys.exit()

os.makedirs(f"saidas/basico/{pasta}", exist_ok=True)
B["saida"] = f"saidas/basico/{pasta}/RL {pasta}{os.environ.get('SUF', '')}.mp4"
B["ref"] = f"referencias/{B['id']}"
B.update(variante="inteira", t_gancho=0.0, gancho=[], cutaways=[])
B["fonte169"] = os.path.exists(f"{D}/base_h.mov") and not os.path.exists(f"{D}/base.mov")
if B["fonte169"]:
    B["enq169"] = os.environ.get("ENQ") or B.get("enq169", "A")   # A = recorte 9:16 no rosto, TELA CHEIA (padrão; nunca letterbox)
B.setdefault("leg_estilo", None)   # padrão = legenda simples de 1 linha (só muda se pedirem a animada)

if B.get("sem_titulo") or not B.get("titulo"):
    # sem título: legenda desde a 1ª palavra
    B.update(titulo=[], t_titulo=0.0, legenda_desde=-1)
    print(f"{ID}: sem título, legenda desde o início")
    criativo.rodar_formatos(B)
    sys.exit()

ld = B["legenda_desde"]
k = ld if isinstance(ld, int) else next(i for i, w in enumerate(WORDS) if criativo.norm(w["w"]) == criativo.norm(ld))
# Título fica no máximo 6 a 9 s. Se a frase do título passa disso, o resto do gancho vira legenda: escreva os blocos
# desse trecho em `gancho_frases` (até a palavra `legenda_desde` inclusive) e o título sai antes.
if B.get("gancho_frases"):
    _toks = [t for t in B["gancho_frases"].split() if t != "|"]
    k2 = k - len(_toks)
    for _a, _w in zip(_toks, WORDS[k2 + 1:k + 1]):
        assert criativo.norm(_a) == criativo.norm(_w["w"]), (_a, _w["w"])
    B["frases"] = B["gancho_frases"] + "\n" + B["frases"]
    B["legenda_desde"] = k = k2
    B["t_titulo"] = None
    print(f"{ID}: título sai depois de '{WORDS[k]['w']}' ({WORDS[k]['e']:.1f} s), gancho com blocos do cfg")
elif WORDS[k]["e"] > 9.0:
    print(f"ATENÇÃO {ID}: o título passa de 9 s ({WORDS[k]['e']:.1f} s) — use gancho_frases ou um legenda_desde mais cedo")
if B.get("t_titulo") is None:   # sai no meio da pausa entre a última palavra do título e a próxima (fim de frase)
    gap = WORDS[k + 1]["s"] - WORDS[k]["e"] if k + 1 < len(WORDS) else 0.5
    B["t_titulo"] = round(WORDS[k]["e"] + min(max(gap / 2, 0.05), 0.35), 2)
print(f"{ID}: título até {B['t_titulo']} s")
criativo.rodar_formatos(B)
