---
name: editor-paper
description: "Editor Paper (menu 6) — estilo papel em Remotion: tela dividida com papel creme amassado em cima (recortes chapados que se acumulam por seção, cupom impresso, carimbos, destaque verde, dinheiro verde, sirene/coração/fogo vermelhos, sem etiqueta de seção) e a pessoa embaixo, com legenda karaokê (palavra falada em verde) numa faixa de papel sobre a borda rasgada; alterna os 3 modos. Usar quando o usuário escolher \"Paper\" no menu, pedir \"estilo papel\", \"metade de cima animada com recortes\", ou quando o gerente delegar a versão Paper de um vídeo."
---

# Editor Paper — estilo papel em Remotion

Metade de baixo: a pessoa (recorte do vídeo dela). Metade de cima: papel creme amassado onde recortes de papel entram no
tempo da fala, uma metáfora literal por frase, acumulando dentro de cada seção. Legenda karaokê (palavra falada em verde)
numa faixa de papel inclinada sobre a borda rasgada. Molde: `remotion/src/paper/videos/demo.tsx` (+ `demo-blocos.txt`).

## Onde está o quê

| | |
|---|---|
| `remotion/src/paper/PaperVideo.tsx` | composição: pessoa, papel + borda rasgada, legenda karaokê, `Secao`, formatos, 3 modos, sons |
| `remotion/src/paper/pecas.tsx` | recortes (`Peca` + figuras, `Cupom`, `Bate`…) — catálogo em `references/pecas.md` |
| `remotion/src/paper/estilo.ts` / `tempo.ts` | cores/fontes/layout; molas, rampas, rasgo, medida de texto |
| `remotion/src/paper/videos/<id>.tsx` | as cenas de cada vídeo; registrar em `paper/videos/index.ts` |
| `remotion/public/paper/` | `papel.jpg`, `kraft.jpg` (gerados por `scripts/papel.py`), `icones/` (Phosphor fill, MIT) |
| `remotion/scripts/` | `preparar_paper.py`, `legenda_paper.py`, `sfx_auto.py`, `fotos.mjs`, `folha.py`, `trilha_cheio.py` |

## Passo a passo (MONTAR)

1. **Preparo** já feito pelo gerente em `work/<id>/` (`work/pipeline/preparar.py`: base, voz, `words_cut.json`, rosto).
2. `./py remotion/scripts/preparar_paper.py <id>` → vídeo e voz em `remotion/public/brutos/`; imprime `rosto`, `duracao`
   (usar essa) e a transcrição com tempos. Fonte vertical (celular): gera `<id>-metade.mp4` já recortado e o vídeo leva
   `recortado: true`.
3. **Legenda**: `remotion/src/paper/videos/<id>-blocos.txt` — 1 a 3 palavras (máx. 4), unidade de sentido, nunca
   terminar em artigo/preposição/"que", ≤ ~16 caracteres por linha; `|` quebra linha dentro do bloco (a 1ª linha também
   nunca termina em artigo/preposição). Texto corrigido pelo sentido. Depois:
   `./py remotion/scripts/legenda_paper.py work/<id>/words_cut.json remotion/src/paper/videos/<id>-blocos.txt remotion/src/paper/videos/<id>-legenda.json`
   e resolver o que ele listar em "revisar".
4. **Roteiro visual**: seções de 5–15 s. Dentro da seção, um elemento novo por frase (metáfora literal da fala),
   entrando ~0,1 s antes da palavra; os elementos se acumulam. Números: etiqueta que **bate como carimbo**; listas e
   contas: **cupom saindo da impressora**; virada: carimbo grande. Nunca inventar número, logo ou tela.
5. **`remotion/src/paper/videos/<id>.tsx`** a partir do `demo.tsx`; registrar em `videos/index.ts`. Seção troca 0,2 s
   antes da 1ª palavra da frase que a abre. **Punch-in**: 3–4 frases de impacto, zoom ~1,08–1,2 até a frase seguinte,
   nunca duas seguidas, sempre em fronteira de frase.
6. **3 modos** (regra: a imagem nunca fica > 4 s parada): no RL, de tempos em tempos uma frase inteira com a pessoa em
   tela cheia e outra com o papel em tela cheia (`modos` no `VideoPapel`; trilha do rosto com `trilha_cheio.py`).
7. **Sons**: `./py remotion/scripts/sfx_auto.py <id>` → `<id>-auto.json` com `sfx` (som no instante de cada animação) e
   `pessoaGL` (trechos do GL com a pessoa em tela cheia — **frase inteira**, 2–4 por vídeo). Importar no `.tsx`.
   Som só quando algo aparece/marca/muda NA TELA daquele formato. Som "papel" (farfalhar) vetado.
8. **Revisar por quadros**: `cd remotion && node scripts/fotos.mjs paper-<id> ../work/<id>/fotos <t1> <t2> …` e
   `./py remotion/scripts/folha.py work/<id>/fotos 6 360`; abrir a folha. Corrigir sozinho: sobreposição, carimbo
   cobrindo texto, papel vazio > 0,5 s, texto ilegível no celular, conteúdo fora de y 240–870, cabeça sob o rasgo.
9. `cd remotion && npx tsc --noEmit -p .` sem erro. **Não renderizar** (o gerente põe na fila).

## Render (fila do gerente)

`bash remotion/render_paper.sh paper-<id>:../saidas/<id>-paper-v1.mp4` (RL; já usa `--color-space=bt709`). Depois do OK
do RL: `paper-<id>-YT`, `-IN`, `-GL` → `../saidas/<id>-paper-v1-YT.mp4` etc.
- **YT** 1920×1080: papel à esquerda, pessoa à direita, rasgo vertical, legenda sobre o rasgo.
- **IN** 1080×1350: dividido no meio. **GL** 1080×1080: papel em tela cheia alternando com a pessoa em tela cheia nos
  trechos `pessoaGL` (frase inteira; sons mudos nesses trechos).

## Regras do estilo

- Borda rasgada em y 960; pessoa = vídeo recortado 1080×960 em escala ~1:1 centrado no rosto (não fechar demais no
  rosto). Cabeça nunca sob o rasgo: plano fechado → `desce` (~46 px, máx. ~50) e punch-in com `origem: 'topo'`.
- Legenda: Montserrat Black ~84 px (reduz pra caber), faixa creme inclinada ±2°, palavra falada em verde `#059669`,
  resto marinho `#1C1A2B`.
- **Sem etiqueta de seção** e **sem título** na tela (só se pedirem: `etiquetas: true`).
- Dinheiro é verde; objeto com cor "de verdade" mantém a cor (sirene/alerta, coração, fogo em vermelho); número ruim
  (perda, custo subindo) em vermelho, número bom em verde.
- Celular/telas desenhados: só o que a pessoa fala; o resto sem texto (nada inventado que pareça real).
- Quando algo é substituído (tarefa → time/IA), anular o rótulo antigo com um X depois que os elementos somem.
- Ícone que gira, gira no sentido das setas (`arrows-clockwise` → velocidade positiva); conferir em 2–3 quadros.
- Margem ≥ 40 px do topo em todos os formatos e ≥ 90–100 px das laterais.

## Armadilhas já resolvidas

- Props da composição precisam ser JSON: a `Composition` recebe só `{nome}`; o vídeo vem do registro.
- `Peca` é absoluta no painel; dentro de cartão/cupom usar componentes em fluxo (`Total`, `Bate`, `ItemLista`).
- `Seta` só some com `sai` ou com a seção; sub-cena precisa de `sai`.
- Carimbo dentro do cupom: abaixo da linha que ele comenta, nunca por cima da anterior.
- X de negação (`Xis`) por cima do texto deixa a palavra ilegível: pôr sobre o ícone ou ao lado.
- Dentro de `Peca` com `entrada` própria não usar `Bate` também (anima duas vezes): `entrada="nada"`.
- `legenda_paper.py`: palavra que só existe no texto revisado ocupa o vão entre as vizinhas.
- `larguraTexto` mede no Chrome do render (fontes carregadas pelo `delayRender` do `Root`).
- Não renderizar ao mesmo tempo que outro render (a fila do gerente cuida disso).
