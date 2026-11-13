---
name: video-dividido-hyperframes
description: "Hyperframe (menu 5) — editar um vídeo em HyperFrames no formato \"tela dividida\": pessoa embaixo, painel preto em cima com tudo o que ela fala virando lettering palavra por palavra (Inter Bold / Montserrat Light) + ícones Phosphor e widgets, sem legenda e sem título (só se pedirem), alternando os 3 modos; depois YT 1920x1080, IN 1080x1350 e GL 1080x1080. Também guarda os scripts comuns a todos os estilos HyperFrames (preparar, revisar, renderizar, exportar). Usar quando o usuário escolher \"Hyperframe\" no menu, pedir \"tela dividida com animações em cima\", ou quando o gerente delegar a versão Hyperframe de um vídeo."
---

# Hyperframe — tela dividida em HyperFrames

O motor está pronto em `hyperframes/motor.py` (+ peças em `hyperframes/pecas.py`); cada vídeo só escreve as **cenas**
num `hyperframes/<id>-hf/gerar.py`. **Molde: `hyperframes/exemplos/hyperframe_gerar.py`**. Scripts desta skill em
`.claude/skills/video-dividido-hyperframes/scripts/` (abaixo: `$S`) — servem também ao VOX, Extremo e Edição animada.

## Regra de entrega — primeiro o RL, depois o resto
1. Montar e revisar → render **só do RL** → conferir → entregar pro usuário aprovar.
2. Com o OK: YT, IN e GL. Nunca gastar render nos outros formatos antes do OK do RL.
Cada revisão é um arquivo novo (`-v2`, `-v3`…); nunca sobrescrever o que já foi entregue.

## Passo a passo

### 1. Preparar a pasta
O gerente já rodou `work/pipeline/preparar.py` (corte, transcrição, rosto em `work/<id>/`). Aqui:
```bash
./py $S/preparar.py <id> <id>-hf --formatos
```
Recorta a pessoa (1080x960, escala ~1:1 — não fechar demais no rosto; fonte vertical: largura inteira com a janela
seguindo o rosto), normaliza a voz, copia fontes e GSAP e imprime a **duração** e a **transcrição numerada** (os índices
são os que as cenas usam). A cor da pessoa nunca muda: os recortes saem com a cor da fonte em matriz BT.601
(`hyperframes/cor_pessoa.py`); `revisar.py` e `renderizar.py` convertem sozinhos o que faltar. Conferir um quadro do
`pessoa.mp4`: cabeça com folga em cima.

### 2. Escrever as cenas (`hyperframes/<id>-hf/gerar.py`)
Copiar o molde e consultar `references/cenas.md` (API do motor + metáforas prontas). Com `from pecas import *` cada
cena vira 2 linhas: `c = cena(i0, i1, 'nome')` + `monta(c, '{64f}apoio|{104}*chave', linha(c, [ic('storefront', 200, t=14)]))`.
Peças: `ic()` (revela/pop/desliza + efeitos riscar, gira, pulsa, quica, sai, verde, badge), `chat`, `baloes`,
`calendario`, `cta` (botão + seta), `grafico_linha`, `barras`, `comparacao`, `passos`, `lead`, `engrenagens`, `hub`,
`quadro_lupa`, `rabisco`, `grade_pessoas`, `chip`, `sublinhado`. Princípios:
- **Uma cena por frase** (unidade de sentido), ~2–3 s. A troca é 0,20 s antes da 1ª palavra. Corte seco.
- **Tudo que é dito aparece em cima**: lettering da frase (palavras entram na hora em que são faladas) + um ícone/widget
  que é a metáfora literal da frase. Sem legenda.
- Lettering: linha de apoio fina (`{64f}…`, Montserrat Light) + linha bold (`{96}…`, Inter Bold); palavra-chave com `*`
  (verde) só em linha bold. O motor reduz o corpo se a linha não couber (≥ 100 px das laterais).
- **Sem título** por padrão. Só se pedirem: `configurar(titulo=[...])` + `montar(fim_titulo=CENAS[k].t0)` (máx. ~9 s) e
  as cenas sob ele com `monta(..., sob=True)`.
- Nada no alto: o conteúdo fica numa faixa baixa do painel.
- **3 modos** (motor `TRES_MODOS`): cenas do `pessoa_gl` = pessoa em tela cheia (frase de conversa INTEIRA, ritmo
  ~1 pessoa : 2 animadas, a cada ~10 s), algumas cenas = animação cheia, o resto dividida com zoom leve na pessoa. Troca
  só em fronteira de frase; a pessoa cheia sem zoom.
- Correções de palavra (`correcoes`) com a mesma ortografia da legenda revisada; nunca número, logo ou tela inventados.

### 3. Revisar antes de renderizar
```bash
./py $S/revisar.py <id>-hf RL        # depois GL, IN e YT
```
Roda o `hyperframes check` (0 erros; avisos de "sub-composition"/"too dense" podem ficar), fotografa o fim de cada cena e
salva `hyperframes/<id>-hf/revisao-RL.png`. **Abrir a folha** e corrigir: texto estourando, elementos sobrepostos, cena
vazia, conteúdo alto demais, palavra-chave em linha fina, ícone girando contra o sentido das setas. Instante
específico: `--em 3.2,9.9`.

### 4. Render (fila do gerente)
```bash
./py $S/renderizar.py <id>-hf saidas/<id>-hf-v1 RL          # depois do OK: ... YT,IN,GL
```
Gravação de celular: `--crf 20` (com a qualidade padrão o vídeo de mão balançando sai pesado demais). O `renderizar.py`
confere quadro, duração, áudio e, no GL, que cada troca pessoa ↔ animação cai no quadro do corte.

### 5. Exportar (opcional)
`./py $S/exportar.py saidas/<id>-hf-v1 "<título>"` cria `~/Desktop/<pasta>/<título>/RL|IN|GL|YT <título>.mp4`.
No fluxo do gerente a entrega é pelo `work/pipeline/entregar.py`.

## Formatos (detalhes em `references/formatos.md`)
**YT** os dois quadrados lado a lado; **IN** divisória em 675, pessoa sem cortar; **GL** sem divisória, alternando pessoa
e animação em tela cheia.

## Armadilhas já resolvidas (não repetir)
- Arredondamento de tempo: cada cena começa no quadro exato e termina 0,01 s antes do corte.
- `fromTo` duplicado no mesmo elemento: a 2ª animação usa `vai()` (to), não outro fromTo.
- Clip nunca é animado (`.cena`, `#titulo`): visibilidade é do `data-start/data-duration`.
- Altura ímpar não codifica em libx264 (1080x675 → 1080x676).
- Gradiente em traço fino some → destaque só em linha bold.
- Fonte fina peso 100 sai falhada no celular: a linha fina é Light (300); abaixo de 52 px vira Regular (400).
- Última palavra colada no corte: `antecipar_fim` faz toda palavra entrar no máximo 0,3 s antes do corte; mesmo assim,
  dividir as cenas numa pausa real quando der.
- Rosto errado (gente ao fundo): `preparar.py` só usa detecção com ≥ 60 % da largura mediana; conferir na folha.
- `pop` + `pulsa` ao mesmo tempo brigam pela escala: `ic()` adia o pulso.
- Selo verde chapado com texto preto em caixa alta fica feio → `.chip` translúcido.

## Referências
- `references/estilo.md` — regras visuais (tipografia, cores, tempos, o que foi recusado).
- `references/formatos.md` — RL/YT/IN/GL: posições, escalas, recortes da pessoa.
- `references/cenas.md` — API do motor + catálogo de metáforas.
