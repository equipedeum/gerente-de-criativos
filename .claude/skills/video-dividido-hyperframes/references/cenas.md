# Escrevendo as cenas — API do motor e catálogo de metáforas

O `gerar.py` de um vídeo faz `from motor import *`, chama `configurar(...)`, cria as cenas e termina com
`montar(fim_titulo=...)`. Tudo o que aparece aqui vem de `hyperframes/motor.py`; o exemplo aprovado inteiro é
`hyperframes/exemplos/hyperframe_gerar.py` (copiar trechos de lá é o caminho mais rápido).

## Índice
1. API (Python) · 2. Helpers de animação (JS) · 3. Classes CSS prontas · 4. Catálogo de metáforas · 5. Checklist

## 1. API (Python)

| chamada | faz |
|---|---|
| `configurar(pasta, palavras, duracao, composicao, nome, titulo=None, pessoa_gl, correcoes)` | carrega a transcrição e os dados do vídeo; `titulo` só se pedirem |
| `c = cena(i0, i1, 'descrição')` | cena da palavra `i0` à `i1`; `c.id` = `c01`, `c02`…; `c.t0` = 0,20 s antes da palavra `i0` (0 na 1ª) |
| `ts(i)` | início (s) da palavra `i` — use pra sincronizar qualquer animação com a fala |
| `q(t)` | arredonda pro quadro (30 fps) — todo tempo que vai pro JS passa por `q()` |
| `c.a("js;")` | acrescenta uma linha ao timeline (tempos **absolutos**) |
| `c.html = miolo(conteudo, cls='', estilo='')` | o conteúdo da cena, centrado na faixa baixa do painel; `cls='sob-titulo'` nas cenas sob o título (só quando há título) |
| `letreiro(c, spec)` | lettering palavra por palavra (ver abaixo) |
| `svg(nome, tam, id, cls)` | ícone: Phosphor se houver no mapa `PH`, senão o desenho próprio de `ICONES`; `cls='verde'` pinta de esmeralda |
| `ph_svg('arquivo-phosphor', tam, id, cls, estilo)` | qualquer ícone do Phosphor pelo nome do arquivo (`ferramentas/phosphor-core/assets/regular/*.svg`) |
| `icone(c, '#id', t, d, st, so_proprio=False)` | entrada do ícone (revela o Phosphor / desenha o traço do próprio) |
| `pontos(c, n)` | 5 pontinhos de progresso (listas de 5 itens), o `n`-ésimo verde |
| `botao(c, 'Agendar reunião')` + `clique(c, t)` | botão CTA shiny + cursor que clica em `t` |
| `montar()` (ou `montar(fim_titulo=CENAS[k].t0)` com título) | escreve `public/index.html` do formato pedido e `roteiro.md` |

**`letreiro(c, spec)`** — `spec` = linhas separadas por `|`; cada linha começa com `{px}` (Inter Bold) ou
`{pxf}` (Montserrat Light; Regular se ficar < 52 px). `*palavra` = palavra-chave (gradiente; ignorado em linha fina). As palavras são casadas
em ordem com a fala da cena; pra palavra que o whisper escreveu diferente ou que não é dita, use `palavra@N` (tempo
da palavra N). Ex.: `'{64f}Hoje eu pago|{96}a *metade do preço'`, `'{60f}Primeiro,|{96}o@95 *custo *caiu@100'`.
Palavra sem correspondência gera aviso no terminal — resolver com `@N`.

Nomes de `svg()` com Phosphor: calendario, chat, grafico, email, documento, pessoas, engrenagem, pessoa, megafone,
relogio, loop, ampulheta, predio_p, predio_m, raio, cronometro, seta_baixo, quadro, lupa, trend_up, trend_down,
seta_dir, sino, ia. Pra outros, `ph_svg('nome-do-arquivo', ...)` — procurar em
`ferramentas/phosphor-core/assets/regular/` (ex.: `ls ... | grep -i money`). `check` e `xis` são sempre traço
desenhado (marcas que animam).

## 2. Helpers de animação (JS, dentro de `c.a(...)`)

`palavra(s,t,cor)` · `entra(s,t,d)` fade+escala 0,92→1 · `pop(s,t,stagger)` itens de conjunto ·
`aparece(s,t,d)` · `desenha(s,t,d,stagger)` traço (elementos `.d`) · `revela(s,t,d)` de baixo pra cima ·
`sobe(s,t,d,stagger)` barras verticais · `estica(s,t,d,stagger)` barras horizontais ·
`vai(s,{props},t)` qualquer `to` (2ª animação de um elemento é sempre `vai`) ·
`desliza(s,t,dx,dy,d)` · `conta(s,de,ate,t,d,sufixo)` contador ·
`giraO(s,0,graus,t,d,'50% 50%')` gira svg inteiro (positivo = horário) · `balancaO(s,t,n,amp,per,orig)` balanço ·
`quica(s,t,n,dy,per,stagger)` · `tl.set(s,{...},t)` troca instantânea.
Não use `repeat:-1`, `Math.random`, `Date.now`; nunca anime `.cena`/`#titulo` (são clips).

## 3. Classes CSS prontas

`.linha` (flex centrado) · `.grade` (flex-wrap) · `.tile`, `.tile.p`, `.tile.mini`, `.tile.gd` (IA em verde) ·
`.cartao` (card só contorno) · `.kick` (rótulo eyebrow) · `.chip`, `.chip.mini` (Badge) · `.fila/.rot/.trilho/.barra-h/.val`
(comparação com barra) · `.barras/.barra` · `.bolha.in/.out/.digita/.vaga` (chat) · `.badge` (contador no sino) ·
`.selo` (círculo verde com visto) · `.tarefa/.tarefa-rep/.cinza` (listas) · `.caixa` (quadro tracejado com número) ·
`.pilha/.moeda` · `.cal/.cel/.av` (calendário e avatares) · `.passo/.elo/.elo-f` (etapas) · `.slot/.q` (espaço com "?").

## 4. Catálogo de metáforas (ideia da frase → visual que já funcionou)

| ideia falada | visual (reaproveitável) |
|---|---|
| cancelar/cortar várias coisas | grade de ícones sendo riscados um a um |
| crescer, produzir mais | barras crescendo, a última verde + seta de alta |
| o que entrou no lugar / lacuna | espaços tracejados com "?" verde |
| uma coisa concentra/substitui outras | chip no centro, ícones em volta ligados por linhas e absorvidos |
| pergunta retórica ("sabe o que é mais louco?") | pergunta grande + sublinhado verde desenhando |
| redução de preço/custo | cartão ANTES 100 % × HOJE encolhendo com contador |
| novidade que ninguém tinha | fileira com X → seta → item novo com visto |
| lista de tarefas falada | uma cena por item com pontinhos de progresso (megafone, cartão com termômetro, chat, sino, checklist) |
| "em dois lugares", dois pontos | dois quadros tracejados com 1 e 2 |
| custo caindo / faturamento subindo | cartão com linha descendo + seta pra baixo; cartão com barras subindo + seta |
| equipe parando de perder tempo | pessoas + relógio que fica verde |
| tarefa repetitiva | setas em loop girando + "Mesma tarefa" empilhando |
| tempo indo embora | ampulheta (cheia → meio → vazia) |
| porte de empresa | loja + prédio |
| decisão rápida | cronômetro pulsando + raio verde |
| lucro aparecendo | pilhas de moedas crescendo + seta de alta |
| chamada pra ação | botão CTA com cursor clicando + seta pra baixo quicando (sem "link" escrito) |
| marcar conversa/reunião | calendário com o dia marcado + avatares |
| explicar em detalhes | quadro de apresentação + lupa |
| implementar em etapas | 3 etapas marcando em sequência + selo |
| palavra de fecho ("Fechado?") | palavra única gigante |
| negação ("não é…", "não consegue…") | ícone riscado com X desenhando na palavra negada |
| algo que para quando você para | engrenagem que desacelera e fica cinza; duas engrenagens girando = operação rodando |
| tudo depende de você | hub: você no centro, mensagens ligadas por linhas |
| celular não para | celular com contador de notificações subindo |
| muita gente | grade de pessoas surgindo |
| filtrar o importante | tarefas cinzas → funil → uma estrela verde → equipe |
| complicado × simples | rabisco embolado desenhando; linha reta verde até um visto |
| não entende × qualquer um aprende | notebook com interrogações; pessoa com capelo → ícone |

GL/3 modos: a pessoa em tela cheia nas frases de conversa ("Duro, né?", "Fechado?", pergunta direta), ~1 a cada 3 cenas.

Números e dados: nunca inventar (sem "R$ 12 mil", "3,2 %" se a pessoa não disse). Mensagens de chat e rótulos
ilustrativos podem, desde que não pareçam dado real.

## 5. Checklist da cena
- Começa com texto na tela em ≤ 0,2 s e tem algo acontecendo até o fim (cena > 3 s precisa de uma 2ª ação).
- Metáfora literal da frase; um visual novo por cena (não repetir o mesmo desenho em cenas seguidas).
- Palavra-chave em linha bold; linha fina sem `*`.
- Sob o título (primeiros ~10 s, só quando houver título): `miolo(..., 'sob-titulo')`.
- Todo `id` começa com o id da cena (`c07-…`), pra não colidir.
