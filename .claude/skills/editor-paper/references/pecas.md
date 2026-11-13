# Catálogo de peças do estilo papel (`remotion/src/paper/pecas.tsx`)

Tempos sempre em **segundos absolutos** do áudio cortado. Painel de cima = 1080 × 960.

```tsx
<Secao s={10.82} e={22.04} tag="A conta" num={3} total={8}>
  <Peca x={540} y={548} t={11.45} entrada="nada" move={[{t: 12.84, x: 705, escala: 0.9}]}>
    <Cupom t0={11.5} w={520} h={630} titulo="Cupom · a conta do mês">
      <ItemLista t={14.16} txt="Salário" tam={34} />
    </Cupom>
  </Peca>
</Secao>
```

## `Secao`

`s`, `e`, `tag`, `num`/`total` (etiqueta numerada "01/08"; sem `num` vira etiqueta marinho). Na troca a cena encolhe
e sai pela esquerda-baixo em 0,3 s enquanto a seção nova começa.

## `Peca` — posiciona e anima qualquer filho

| prop | |
|---|---|
| `x, y` | centro do filho (ou base com `ancora="base"`, canto com `ancora="topoEsq"`) |
| `t` | quando entra (antes disso não renderiza) |
| `entrada` | `pop` (padrão, escala com sobra) · `desliza` + `de` · `cai` (de cima girando) · `carimbo` (2,6× → bate; use em número/valor) · `cresce` (de baixo, `ancora="base"`) · `revela` · `fade` · `nada` |
| `sai`, `saida` | `encolhe` (padrão) · `cai` · `voa` (pra cima) · `some` |
| `move` | reposicionar depois de entrar: `[{t, x?, y?, escala?, rot?}]` |
| `rot`, `escala`, `origem`, `sombra` | `origem` = transform-origin (placa presa no poste: `'100% 50%'`) |

## Figuras

| peça | uso |
|---|---|
| `EtiquetaSecao txt num total` | etiqueta numerada — **desligada por padrão** (só com `etiquetas: true`) |
| `Etiqueta txt cor tam mono` | rótulo/valor. `cor`: navy, destaque (verde), azul, creme, kraft, amarelo, branco |
| `Texto` · `Digita` · `Troca` | texto solto, máquina de escrever, valor que troca |
| `Cupom t0 w h titulo` | fenda de impressora + cupom impresso de cima pra baixo; conteúdo em fluxo |
| `Bate t0 rot` | carimbo em fluxo (dentro de cupom/cartão) |
| `Cartao w h cabecalho corCab barra pad` | cartão creme com borda de baixo rasgada |
| `ItemLista t txt marcador tCheck tam` | linha de recibo (`menos`) ou checklist (`caixa` + ✓) |
| `Carimbo txt cor tam` | carimbo verde (`destaque`) ou azul (com `entrada="carimbo"` ou dentro de `Bate`) |
| `Pessoa cor gravata tam` | boneco silhueta (`cor="kraft"` = papelão) |
| `Moeda` · `Nota` · `Carteira` | dinheiro |
| `Bloco w h txt` | bloco de papelão com rótulo |
| `Calendario num topo` · `MesRiscado t0` | data; mês com os dias riscados |
| `Poste` + `SetaPlaca txt lado cor` | placa de direção |
| `Tesoura tCorte` + `EtiquetaCortada txt tCorte` | cortar algo |
| `ChipIA d` · `Doc w` · `Icone nome tam cor` (Phosphor fill) | IA, papel/tarefa, ícone qualquer |
| `Botao txt tClique` + `Mao tClique` | CTA com a mãozinha clicando |
| `Interrogacao` · `Barra` · `Balao` | "?", barra de gráfico, balão |
| `Seta x1 y1 x2 y2 t0` · `Check` · `Xis` · `Risco` | traços que desenham |
| `IconeRotulo ic txt cor vertical` | ícone + etiqueta (listas de itens da fala) |
| `Gira vel tPara` | gira o filho (engrenagem); freia e para em `tPara` |
| `Pulsa bpm amp` | batimento (coração, sirene, celular tocando) |
| `AoVivo txt` | selo "ao vivo" com bolinha verde pulsando ("neste exato momento") |
| `Relogio hora dia` | relógio digital de papel ("10:21 · quinta-feira") |
| `Pizza ate t0 t1 de txt` | pizza/rosquinha animada (80% da operação; margem sendo comida) |
| `Peso txt` | peso de academia ("custo pesado") |
| `Sirene tam hz` | sirene vermelha piscando com brilho (urgente, alerta) |

## Ideias vistas nas refs e ainda não construídas

Navio no mar, balança/gangorra, prédio de colunas que racha, barril de pólvora com pavio, pódio, termômetro subindo,
pilhas altas de moedas, calendário virando página, motosserra, gráfico com barras acima/abaixo do zero, régua de
"esquerda–centro–direita" com bandeirinha, partículas (comida/dinheiro se desfazendo). Desenhar no `pecas.tsx` com as
cores de `estilo.ts` quando um vídeo pedir, e anotar aqui.
