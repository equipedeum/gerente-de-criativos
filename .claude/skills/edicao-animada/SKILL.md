---
name: edicao-animada
description: Edição animada (menu 9) — o vídeo vira um documentário ilustrado em vetor chapado: animação em TELA CHEIA o vídeo inteiro com a voz da pessoa narrando, cenários em camadas com paralaxe e muita ação (pássaros, carros, janelas, relógio, gente de corpo inteiro trabalhando), número falado em serifa grande, rótulo com relógio de bolso; a pessoa entra em tela cheia numa frase a cada ~10–15 s, com legenda simples. Sons do Earshot. Usar quando o usuário escolher "Edição animada" no menu, pedir "vídeo animado/ilustrado", ou quando o gerente delegar.
---

# Edição animada

Motor: `hyperframes/motor.py` + `hyperframes/pecas.py` + **estilo `hyperframes/animada.py`** (sempre `an.aplicar()` no
fim, nunca `montar()`), gente em `hyperframes/bonecos.py` (`bo`), arsenal em `hyperframes/arsenal_animada.py` (`ar`,
+ `arsenal_cenas.py`, `arsenal_fundos.py`, `arsenal_info.py`, `arsenal_receitas.py`). **Molde:
`hyperframes/exemplos/animada_gerar.py`**. As docstrings de cada função são o catálogo completo.

## Estrutura do vídeo
- **O vídeo inteiro é animação em TELA CHEIA** com a voz da pessoa narrando (`an.TELA_CHEIA = True`, padrão).
- **Começo**: 5 a 10 s de animação. Depois a pessoa entra em tela cheia numa frase INTEIRA e volta pra animação; isso
  se repete a cada ~10–15 s, sempre em fronteira de frase. As cenas da pessoa são as de `pessoa_gl={...}` no
  `configurar()` e valem pros 4 formatos.
- **Que frase vai pra pessoa**: de conversa ou pessoal ("se isso soa familiar", "deixa eu te contar"), em que a figura não
  perde força. A frase com número, objeto ou imagem forte fica na animação.
- **Legenda** só nas cenas da pessoa (simples, 1 linha, altura padrão de cada formato; desce só pra sair do rosto).
  Quebra manual: `an.LEG_PESSOA = {'c08': 'Deixa eu te contar|como é|um dia normal'}`; senão, a `frases` revisada do
  básico do mesmo vídeo (`work/basico/cfg/<id>.py`) ou automática pelo sentido. Confira o "legenda cNN (...)" que o
  `an.aplicar()` imprime.
- **Corte seco do vídeo x pessoa cheia** é tratado sozinho (`pessoa_cheio.cortes_quadros`): a pessoa entra/sai no quadro
  do corte; corte no meio da frase = punch-in leve.
- **Sempre tem ação na tela**: câmera com paralaxe e zoom, cenário com vida, objetos entrando. Toda cena tem pelo menos
  1 objeto ou peça além do letreiro. Cena só de texto, nunca.

## Peças principais
- **`an.cenario(cena(...), tipo)`**: o fundo. Cenas seguidas com o mesmo tipo viram um plano contínuo; trocar de tipo dá
  transição. Tipos: `cidade`, `cidade_noite`, `dia`, `tarde`, `noite`, `escritorio`, `escritorio_noite`, `escritorio2`
  (`topo='relogio'|'quadros'|'prateleira'`), `reuniao`, `sala_noite`, `quarto_noite`, `rua`, `rua_tarde`, `rua_noite`,
  `recepcao`, `deposito`, `copa`, `sala_dono`, `celular`, `pergaminho`, `campo`, `campo_tarde`, `porto`, `fabrica`,
  `loja`, `cafe`, `transito` (`parado=True`), `aereo`, `corte`, `preto`, `tunel`, `casa`, `parque`,
  `capitulo_vermelho`/`capitulo_verde` (só como passagem com letreiro falado + número/ação). **Nenhum ambiente em mais
  de 3 cenas.**
- `an.data(c, '23h', ts(i), legenda='ONZE DA NOITE')` — número falado em serifa grande (escrito como foi falado).
- `an.rotulo(c, 'TÍTULO', 'sub', ts(i))` — lower-third com relógio de bolso (hora ou lugar falado), 2–3 por vídeo.
- `an.risca(c, t, linha=-1)` — traço de pincel riscando uma linha do letreiro ("~~não é pequeno~~").
- **Gente (`bo`)**: `bo.escritorio(c, t, acoes=(...))`, `bo.fachada`, `bo.pote`, `bo.crescimento_predio`,
  `bo.sala_noite`, `bo.casa_fora`, `bo.ponto_onibus`, `bo.campanhas`, `bo.chegada`, `bo.sala_reuniao`, `bo.operacao`,
  `bo.quarto_ia`, `bo.copa`, `bo.recepcao`, `bo.deposito`, `bo.dono`, `bo.videochamada`, `bo.grafico_pergaminho`,
  `bo.mapa` (cidade FICTÍCIA), `bo.muda_pose`. Peças soltas: `bo.corpo`, `bo.pos`, `bo.anda/vive/digita/gesticula`.
- **Arsenal (`ar`)**, todas `ar.x(c, t, ...)` dentro do `monta`:
  - planos fechados: `close_rosto`, `vendedor_telefone`, `notebook_grafico`, `caixa_registradora`, `carteira`,
    `celular_mao`, `agenda`, `mao_escreve`, `de_costas`, `celulares_pergunta`;
  - dia a dia: `entregador`, `balcao`, `reuniao_em_pe`, `cafe_maquina`, `transito_preso`, `fabrica_linha`,
    `escritorio_aberto`, `predio_corte`, `contraluz`, `familia_jantar`, `parque_passeio`, `viagem`, `porto_carga`, `caravana`;
  - montagem: `ar.picotado(c, [(t1, lambda: ...), (t2, lambda: ...)])` (2–4 quadros rápidos numa frase), `ar.clima`;
  - infográficos (só número FALADO): `pizza`, `grafico_linha`, `contador`, `fluxo`, `mapa_rotas`, `funil`,
    `pictograma`, `balanca`, `antes_depois`, `grade_objetos`, `linha_tempo`;
  - metáforas: `iceberg`, `malabarista`, `domino`, `escada`, `foguete`, `barco_furado`, `engrenagens`, `cabo_guerra`,
    `semente`, `torre_blocos`, `ima`, `lampada`, `corrida`, `relogio_rapido`, `janelas`, `construcao`;
  - cartelas/rótulos: `pincel`, `nome`, `selo_canto`, `definicao`, `manchete` (jornal FICTÍCIO), `placa_valor`,
    `citacao`, `numeros`, `carimbo`;
  - transições na ENTRADA da cena: `ar.transicao(c, 'tinta'|'pagina'|'iris'|'zoom'|'persiana'|'chicote'|'mancha'|'auto')`
    — uma a cada 2–3 trocas de lugar, nunca entrando/saindo da pessoa (lá é corte seco);
  - câmera: `ar.camera(c, 'push'|'pull'|'tilt_baixo'|'tilt_cima'|'pan_dir'|'pan_esq'|'dolly', forca)`, `ar.tremor`;
  - variedade: `ar.escolhe('A:ideia', [...])` foge do que o vídeo (e os vídeos anteriores, histórico em
    `hyperframes/_arsenal_historico.json`) já usou; `bo.variante('ideia', (...), base=...)`.
- Peças do `pecas.py` (`ic`, `linha`, `chat`, `calendario`, `barras`, `grafico_linha`, `engrenagens`, `passos`) já vêm
  redesenhadas no estilo.

## Regras do estilo
- **NÃO REPETIR**: varie o TIPO DE PLANO (close, plano médio, objeto/POV, de costas, aéreo, corte, contraluz,
  panorâmica, cartela), no máximo 2 cenas seguidas no mesmo tipo; nenhuma peça duas vezes; peças antigas do `bo`
  (cartões/bustos pequenos) no máximo em 1/3 das cenas.
- **Gancho no 1º segundo**: o quadro 0 já tem ação forte e o 1º letreiro COMEÇA COM A LINHA GROSSA
  (`'{100}A sua *empresa|{140}*cresceu'`), nunca só com a fina (o `an.aplicar()` avisa).
- **Sem "Capítulo"** na tela (`an.capitulo()` não desenha nada). Sem botão, cursor, QR ou "link" na tela: "clica no link
  aqui embaixo" vira cena de ação (polegar respondendo, pessoa acenando).
- **Dado vira cena, não cartão**: número falado = `an.data` grande + uma cena que mostra o que ele significa. Gráfico só
  dentro de um quadro/TV do cenário. Nunca número que não foi dito.
- **Física da cena**: gente sentada à mesa fisicamente possível (tampo a ~200 na escala 1, ombros e cabeça acima do
  tampo, cadeira na mesma escala), ninguém flutuando ou atravessando objeto, adulto nunca em escala de criança, nada na
  frente de rosto. Celular sempre na mão de alguém dentro de um cenário.
- **Texto**: linha montando palavra a palavra centralizada; largura máx. 840 px; texto de peça ≥ 48 px.
- **Look** (automático, só na animação): dessaturado e quente, luz baixa da esquerda, sombra dura, vinheta, grão.
  A pessoa nunca fica embaixo dessas camadas. **A cor da pessoa nunca muda** (recortes em BT.601 via
  `hyperframes/cor_pessoa.py`; o snapshot não mostra o defeito — conferir no MP4).
- **Final**: a última cena segue com ação até o último quadro e escurece de leve depois da última palavra (automático).
- **Sons** automáticos (banco do Earshot em `remotion/public/sfx-animada/`): whoosh macio na troca, pop nos objetos,
  tique no relógio, impacto na data. Nunca música por cima da voz sem pedido.

## MARGEM SEGURA — e a checagem automática
O que é animação importante ou texto tem que ficar dentro da caixa segura em qualquer instante (câmera, zoom, entradas):

| formato | caixa segura (px da tela) | texto |
|---|---|---|
| RL 1080×1920 | x 100–980, y 220–1500 | y 320–1500 |
| IN 1080×1350 | x 100–980, y 80–1270 | y ≥ 200 |
| GL 1080×1080 / YT (painel 1080×1080 à esquerda) | x 100–980, y 80–1000 | y ≥ 160 |

- Pode sangrar: cenário de fundo, gente de corpo inteiro no chão, braço/mão entrando pela borda, folhas voando.
- Por construção: `bo.faixa()` (faixa do mundo que cabe no formato), `bo.encaixa(svg, caixa, apoio=)`, balões/etiquetas
  puxados pra dentro sozinhos, `data-imp` no objeto que carrega a ideia (tabela `bo.IMP`).
- **Checagem**: roda sozinha no fim do `revisar.py <id>-animada <FMT>` (linha "MARGEM FMT: N elemento(s) fora"); os 4
  formatos: `./py hyperframes/checar_margem.py <id>-animada` (~15 s por formato; `--trans` lista também as de transição).
  **Meta: 0 em todos os formatos antes do render.** Se uma peça sair, corrija a peça ou a posição, nunca afrouxe a caixa.

## Armadilhas (GSAP/SVG)
- Peça nova roda dentro do `monta()`, antes de a cena seguinte existir: use `bo._fim(c)` pro fim da cena, nunca
  `motor.CENAS[k+1]`.
- Nunca anime `x`/`y` num `<g>` que já tem `transform="translate(...)"`: translate no `<g>` de fora, animação no de dentro.
- Nunca escala (`scale` + `transformOrigin`) e move (`x`/`y`) no MESMO `<g>`; barra que cresce: `attr:{y,height}`, nunca `scaleY`.
- `fromTo` com `scale`: o mesmo `transformOrigin` nos dois lados.
- Prefixo de id de peça própria não pode repetir um da tabela `bo.IMP`.
- `revisar.py ... --antes 0.4` nas animadas com transições do arsenal (com o padrão a foto cai dentro da transição).

## Passo a passo (MONTAR)
1. `./py .claude/skills/video-dividido-hyperframes/scripts/preparar.py <id> <id>-animada --formatos` (se já existir
   `<id>-hf` ou `<id>-vox`, dá pra copiar de lá os vídeos da pessoa, voz, vendor e fontes).
2. `hyperframes/<id>-animada/gerar.py` a partir do molde: `configurar(... pessoa_gl={frases a cada ~10–15 s})`, uma cena
   por frase com `an.cenario` e peças, 3–5 `ar.transicao` e 2–4 `ar.camera`, `an.aplicar()` no fim.
3. `./py hyperframes/<id>-animada/gerar.py phosphor RL` e `./py .claude/skills/video-dividido-hyperframes/scripts/revisar.py <id>-animada RL --antes 0.4`;
   abrir a `revisao-RL.png` e corrigir sozinho (margem 0, texto cortado, objeto em cima do texto, cena sem objeto,
   física da cena, pessoa cortada no meio de frase). Depois `checar_margem.py <id>-animada` pros 4 formatos.
4. **Não renderizar.** Comando pro Gerente: `HF_SOBREPOSICAO_OK=1 ./py .claude/skills/video-dividido-hyperframes/scripts/renderizar.py <id>-animada saidas/<id>-animada-v1 RL`
   e, depois do OK, `YT,IN,GL`.

## Formatos
- **RL**: 1080×1920, tudo em tela cheia.
- **GL e IN**: a animação ocupa o quadro inteiro (o ambiente encolhe pra caber texto em cima e ação embaixo) e a pessoa
  entra nas mesmas cenas.
- **YT**: animação quadrada à esquerda + pessoa à direita; pessoa em tela cheia 16:9 nas cenas dela.
