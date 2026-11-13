---
name: editor-extremo
description: Editor Extremo (menu 8) — versão de um vídeo em motion design de interface escuro e quente, em HyperFrames. Fundo marrom quase preto com retícula e poeira laranja, cada frase vira uma tela de produto recriada (chat, CRM, kanban, checklist em card escuro, passo numerado com squircle laranja, número contando, formulário, card de perfil com cursor), título serifado creme com palavra-chave laranja, 3 modos alternando (dividida / gráfico cheio / pessoa cheia) com whip, flash duplo e blur de foco, sons leves só com evento visível e legenda simples de 1 linha só na pessoa cheia. Usar quando o usuário escolher "Extremo" no menu, pedir "estilo Extremo", ou quando o gerente delegar a versão Extremo de um vídeo.
---

# Editor Extremo

## Arquivos
- Motor: **`hyperframes/extremo.py`** (escreve o `index.html` inteiro; a docstring é o resumo). Um `gerar.py` por vídeo
  em `hyperframes/<id>-extremo/`. **Molde: `hyperframes/exemplos/extremo_gerar.py`** (copiar e trocar tudo).
- Revisão/render: `revisar.py` / `renderizar.py` da skill `video-dividido-hyperframes`
  (`$S = .claude/skills/video-dividido-hyperframes/scripts`).
- Sons: kit do Earshot (MIT) já renderizado em `hyperframes/extremo_sfx/earshot/` (pop = card entrando, tick = X/número
  girando, check = ✓, ding = ✓ final/CTA, swish = whip, foco = entrar/sair da pessoa cheia, hit = flash).
- Fontes (copiadas sozinhas de `ferramentas/fontes`): EB Garamond 400 (título), Inter 500/600/700 (UI), TikTok Sans
  (legenda). Nada abaixo de peso 400.

O motor prepara sozinho `public/` (fontes, gsap, `voz.m4a` com loudnorm −16 e os recortes da pessoa); não precisa do
`preparar.py` da skill do Hyperframe. Recortes: `pessoa-<FMT>-D.mp4` (dividida) e `pessoa-<FMT>-T.mp4` (cheia), feitos
**por take** (`work/<id>/cortes_visuais.json`): em cada take a janela tem tamanho fixo pra o rosto ficar do mesmo tamanho.
Pra refazer um recorte, mande o `.mp4` dele pra Lixeira e rode de novo.

## Gramática (o motor já faz)
1. **3 modos** por cena: `'D'` dividida (RL/IN/GL: gráfico em cima, pessoa embaixo; YT: gráfico à esquerda, pessoa à
   direita), `'G'` gráfico em tela cheia (sem pessoa, sem legenda), `'T'` pessoa em tela cheia (close, só a legenda).
   Base D↔G, troca a cada ~3–4 s; **T a cada ~10 s numa frase inteira** de conversa/virada (pergunta, "e dá pra mudar
   isso", "se a sua empresa…").
2. **Transições** pela troca de modo: entrar no G = flash duplo creme com blur (7 quadros); entrar/sair do T = blur de
   foco; o resto = whip horizontal. Duas cenas T seguidas = a mesma pessoa continuando, sem transição. Fade preto no fim.
3. **Corte seco do vídeo** (jump cut) a até 0,35 s do começo de uma cena vira o ponto de troca dela. Corte no MEIO de
   cena D/T dá AVISO: comece uma cena naquela frase ou use G.
4. Fundo radial marrom + vinheta + retícula laranja + grão + poeira. Empurrão de câmera de +2 % em toda cena D/G e zoom
   leve contínuo na pessoa da dividida (nada parado > 4 s).
5. Entradas blur→nítido + fade + subida em ~6 quadros, ~0,12 s antes da palavra; listas em cascata; item antigo apaga
   a 40 %; pop nos X/✓.
6. Tipografia: `chapeu()` = eyebrow Inter 600 caixa-alta laranja; `titulo()` = EB Garamond creme, 1–2 linhas (`|`
   quebra), `*chave*` laranja, `!chave!` vermelha (ideia negativa).
7. **Legenda simples** (1 linha branca, sombra leve, sem animação) **SÓ na pessoa cheia (T)**, logo abaixo do queixo
   (RL nunca abaixo de 65 %). Na dividida (inclusive o lado a lado do YT) e no gráfico cheio NÃO há legenda.
8. **Som só com evento visível**: `som()` é um pedido; no `aplicar()` o motor lê a timeline real das cenas daquele
   formato e só toca se algo entra/marca/muda a ±2 quadros. Mínimo 0,28 s entre sons de peça. Cada formato grava
   `mapa-sons-<FMT>.txt` (tempo, som, elemento) + descartados.

## Peças (`from extremo import ...`; `t` = índice da palavra (int) ou segundos (float))
- `cena(i0, i1, 'D'|'G'|'T', 'nome', modos={'GL': 'G'}, zoom=(idx,))` — uma por frase. `modos` troca o modo num formato
  (peça alta demais pro painel de 560 px do GL → `'G'` no GL). `zoom` = zoom-cut leve (×1,06) no T, só em começo de frase.
- `chapeu(c, 'texto', t)`, `titulo(c, 'linha|*chave*', t)`, `riscado(c, 'frase', t, t_risco, t_apaga=…)`.
- `passo(c, n, 'Título|*chave*', t, icone=None)`; `checkcard(c, [(txt, t_entra, t_marca, 'ok'|'x')], cabeca='')`;
  `icone(c, 'nome-phosphor', t, rotulo='')`; `hub(c, (icone, rótulo), [(icone, rótulo, t, '')], t)`;
  `pergunta(c, 'enunciado', [opções], t, escolhe=(k, t), rotulo='PERGUNTA 1 DE 3')`;
  `perfil(c, t, t_clique, usuario='seuperfil', nome='Nome', botao=('Seguir', 'Seguindo'))` (foto tirada do próprio vídeo).
- `notificacao`, `chat` (in/out/ia, `digita`, `tag`, `apaga`), `janela` (CRM com `destaca`, `corta`, `troca`), `kanban`,
  `fluxo`, `numero(c, de, ate, t, dur, suf=, rotulo=, barra=)`, `alerta`, `lista`, `reuniao`, `barras`, `equipe`
  (com `fantasmas` + X), `etapas`, `checklist`, `semana`, `pilula`, `linha_icones`, `celulares(c, [perguntas], t, t_fim)`,
  `cta(c, 'Clica aqui embaixo', t, t_clique)` (texto SEM "link").
- `som(t, 'tique'|'blip'|'chime'|'whoosh', vol=None, gap=None)` pra um som extra.

## Regras
- **Texto pelo SENTIDO**, não pelo whisper; crase certa. Reaproveite o `repl`/`frases` revisados do básico se houver.
- **Nada escrito com link, URL, QR, "link na bio" ou "Direct"**: o motor PARA se uma peça tiver isso e omite o bloco de
  legenda que tiver. A frase "clica no link aqui embaixo" vai numa cena **G**; o botão diz "Clica aqui embaixo".
- Troca de modo/cena só em começo/fim de frase. Imagem nunca parada > 4 s (AVISO "s sem nada entrar" = ponha um evento).
- Sem área desfocada (o blur só existe nos quadros de transição).
- Texto e enfeites a ≥ 100 px das laterais; chapéu curto (≤ ~28 letras).
- **Pessoa nunca com cabeça cortada; no cheio, sem zoom exagerado** (o motor avisa). Take em que a pessoa chega perto
  da câmera (rosto ≥ ~420 px no 16:9): não use T ali.
- **A pessoa aparece em todo formato** numa frase inteira a cada ~10 s — conte as cenas T de cada formato na lista do
  `index.html` antes do render. Nada de pessoa em cartão/quadro vertical: na dividida ela ocupa a faixa inteira
  (`X.ZOOM_D = False` = sem zoom e sem aproximar o recorte).
- Sem número/tela/logo inventado apresentado como real (UI é ilustração genérica: "Cliente novo", "Concorrente A").
- **Texto longe do topo**: título, legenda e qualquer texto nunca lá em cima, nunca baixo demais, nunca na altura do
  rosto. Conferir: `MARGEM_SO_VERTICAL=1 node hyperframes/checar_margem.mjs hyperframes/<id>-extremo/public <FMT> saida.json`.
- **A cor da pessoa nunca muda**: sem filtro/grade nela; todo recorte sai em BT.601 com a cor da fonte
  (`hyperframes/cor_pessoa.py`). Conferir um quadro do MP4 final contra o BRUTO.
- Música: sem cama por cima da voz sem pedido (`MUSICA_ON = False`; com pedido, `X.MUSICA_ON = True` e o arquivo em
  `trilhas/extremo.mp3`, que precisa ter licença).

## Passo a passo (MONTAR)
1. Transcrição numerada: `./py -c "import json;w=json.load(open('work/<id>/words_cut.json',encoding='utf-8'));print(' '.join(f'{i}:{p[\"w\"]}@{p[\"s\"]:.2f}' for i,p in enumerate(w)))"`
   e `work/<id>/face_track.json` (em que trecho a pessoa está perto da câmera).
2. Duração: `min(voice.wav, base)` arredondada pra baixo (2 casas).
3. `hyperframes/<id>-extremo/gerar.py` a partir do molde: uma cena por frase, D/G alternando, T a cada ~10 s, 2–5 eventos
   por cena, título com a palavra-chave. Gancho: já abre em D com peça no 1º quadro, 3 modos nos primeiros ~10 s.
4. `./py hyperframes/<id>-extremo/gerar.py phosphor RL` (1ª vez faz os recortes) e ler os AVISOs.
5. `./py $S/revisar.py <id>-extremo RL` → abrir `hyperframes/<id>-extremo/revisao-RL.png` e corrigir sozinho: texto
   cortado/estourando, peça sobre o título, margem < 100 px, cena vazia, cabeça cortada. Instante específico: `--em 3.2,9.9`.
   Depois `IN`, `GL` e `YT`.
6. **Não renderizar.** Devolver os comandos: `./py $S/renderizar.py <id>-extremo saidas/<id>-extremo-v1 RL` e, depois do
   OK, `... YT,IN,GL`.

## Formatos
| | quadro | dividida | caixa do gráfico | legenda (só T) |
|---|---|---|---|---|
| RL | 1080×1920 | 50/50 em y 960 (fonte vertical: gráfico 0–820 / pessoa 820–1920) | D x110–970 y250–890 (vertical y320–800); G y330–1230 | abaixo do queixo, ≤ 1248 |
| IN | 1080×1350 | painel 702 / pessoa 648 | D y50–650; G y225–1175 | ≤ 1215 |
| GL | 1080×1080 | painel 560 / pessoa 520 | D y36–506 (peça alta → `modos={'GL': 'G'}`); G y180–980 | ≤ 975 |
| YT | 1920×1080 | gráfico 1170 à esquerda / pessoa 750 | D x110–1100 y180–900; G y180–960 | ≤ 1000 |

### Fonte vertical (celular)
Sem `base_h.mov` e com `base.mov` 1620×2880, o motor liga `X.VERTICAL` e usa `_recorte_vertical`: plano médio com
rosto pelo `ALVO_V`, topo da cabeça a ~10 %, queixo e ombros dentro, vídeo sempre na largura inteira. **No IN/GL toda D
vira G** → ponha `modos={'IN': 'T', 'GL': 'T'}` em cenas D até ter a pessoa cheia a cada ~10 s; no GL use
`X.ALVO_V[('GL', 'T')] = (420, 0.06)`; onde o motor avisar "legenda vai tampar o queixo", a cena fica G naquele formato.
No YT, T estreito demais → `modos={'YT': 'D'}` + um `titulo`. No RL vertical, peça alta demais pro painel de 480 px →
`modos={'RL': 'G'}`.

### Cuidados
- Tempo das peças: `int` = índice da palavra, `float` = segundos (`88.5` vira 88,5 s, fora da cena).
- Na D o cabeçalho (chapéu+título) fica embaixo das peças; chapéu sozinho fica em cima. Evite `rotulo` de ícone/equipe +
  chapéu na mesma D (eyebrows empilhados).
- `hub` com 2 satélites: o 1º da lista fica à DIREITA.
- O check de GL do `renderizar.py` mede brilho nas trocas pessoa↔gráfico; com flash/blur pode listar quadros "fora" —
  conferir a olho.
