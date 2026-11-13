"""Auditoria das quebras de legenda de um cfg (regra do usuário, 06/10/2026 — exemplo BOM/RUIM em references/padrao-criativos.md).
Aponta: bloco com mais de 4 palavras, bloco que termina em artigo/preposição/conjunção/"que", frase nova no meio do bloco.
Uso: PYTHONUTF8=1 $PY work/auditar_legenda.py work/grav2909/cfg/L2.py [...]   (e conferir o tempo na tela com `render.py <id> --blocos`: nada < 0,28 s)"""
import importlib.util, re, sys, unicodedata
sa = lambda x: "".join(c for c in unicodedata.normalize("NFD", x.lower()) if unicodedata.category(c) != "Mn")
FRACAS = {"de","da","do","das","dos","a","o","as","os","um","uma","e","ou","mas","que","para","pra","com","em","no","na","nos","nas","por","pelo","pela","seu","sua","meu","minha","se","sem","ao","aos",
          # 08/11 (varredura): preposições e contrações que faltavam
          "ate","pelos","pelas","num","numa","nuns","numas","dum","duma","sobre","entre","desde","contra","apos","sob"}
for caminho in sys.argv[1:]:
    spec = importlib.util.spec_from_file_location("c", caminho); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    blocos = [p.strip() for ln in m.CFG["frases"].strip().split("\n") for p in ln.split("|") if p.strip()]
    for b in blocos:
        ws = b.split(); mot = []
        if len(ws) > 4: mot.append(f"{len(ws)} palavras")
        if sa(re.sub(r"\W", "", ws[-1])) in FRACAS and not re.search(r"[.,?!:;…]$", ws[-1]): mot.append(f"termina em '{ws[-1]}'")
        if re.search(r"[.?!…] +[A-ZÁÉÍÓÚÂÊÔÃÕÇ]", b): mot.append("frase nova no meio")
        if re.search(r"(?i)thiago", b): mot.append("pessoa -> pessoa")
        if mot: print(f"{caminho.split('/')[-1]}  [{'; '.join(mot)}]  {b}")
