"""
Tags de YouTube Shorts a partir de buscas reais (autocompletar do YouTube, sem login nem API key).

Uso:
  ./py work/shorts_tags.py buscar "termo 1" "termo 2" ...
      imprime as sugestões do autocompletar do YouTube (pt-BR) para cada termo
  ./py work/shorts_tags.py contar "tag 1, tag 2, ..."
      confere o limite de 500 caracteres do campo de tags
"""
import json
import sys
import urllib.parse
import urllib.request

LIMITE = 500


def sugestoes(termo):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=pt-BR&gl=br&q="
           + urllib.parse.quote(termo))
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode("utf-8", "replace"))[1]


def tamanho(tags):
    """Conta como o YouTube: vírgulas entram, e tag com espaço ganha aspas (+2)."""
    return sum(len(t) + (2 if " " in t else 0) for t in tags) + max(len(tags) - 1, 0)


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("buscar", "contar"):
        sys.exit(__doc__)
    if sys.argv[1] == "buscar":
        for termo in sys.argv[2:]:
            print(f"## {termo}")
            for s in sugestoes(termo):
                print("  " + s)
    else:
        tags = [t.strip() for t in ",".join(sys.argv[2:]).split(",") if t.strip()]
        n = tamanho(tags)
        print(f"{len(tags)} tags, {n}/{LIMITE} caracteres" + ("  PASSOU DO LIMITE" if n > LIMITE else ""))


if __name__ == "__main__":
    main()
