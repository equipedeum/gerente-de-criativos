"""Monta os blocos de legenda (unidade de sentido) a partir da transcrição por palavra.

Uso:
  python scripts/montar_legenda.py <words.json> <blocos.txt> [inicio] [fim]

- words.json: lista [{"w","s","e"}] (saída do faster-whisper já no tempo do bruto cortado).
- blocos.txt: um bloco por linha, texto revisado, já quebrado por unidade de sentido
  (nunca separar artigo/preposição/adjetivo do nome; pontuação fecha bloco; 1–4 palavras).
- Casa os blocos com as palavras em ordem (comparação sem acento/caixa/pontuação) e imprime JSON
  [{"s","e","txt"}] para colar em `legendas` da timeline.
"""
import json, sys, unicodedata, re

def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())

def main():
    words = json.load(open(sys.argv[1], encoding="utf-8"))
    blocos = [l.strip() for l in open(sys.argv[2], encoding="utf-8") if l.strip()]
    ini = float(sys.argv[3]) if len(sys.argv) > 3 else 0
    fim = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
    words = [w for w in words if ini <= w["s"] <= fim]
    saida, i = [], 0
    for b in blocos:
        alvo = [norm(p) for p in b.split() if norm(p)]
        # avança até casar a 1ª palavra do bloco (tolera palavra reconhecida diferente: compara por prefixo)
        while i < len(words) and not (norm(words[i]["w"]).startswith(alvo[0][:3]) or alvo[0].startswith(norm(words[i]["w"])[:3])):
            i += 1
        if i >= len(words):
            sys.exit(f"não achei o bloco: {b!r}")
        s = words[i]["s"]
        j = min(i + len(alvo), len(words))
        e = words[j - 1]["e"]
        saida.append({"s": round(s, 2), "e": round(e, 2), "txt": b})
        i = j
    print(json.dumps(saida, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
