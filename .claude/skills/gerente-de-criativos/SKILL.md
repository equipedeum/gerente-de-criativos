---
name: gerente-de-criativos
description: Gerente de Criativos — orquestra a edição de um vídeo (ou um lote) delegando cada etapa a um subagente (preparar → título → editores dos estilos escolhidos no menu → revisão de legenda → render um por vez → conferência por quadros → entrega em PARA REVISAR → OK do usuário → outros formatos → APROVADOS) e controla a fila em work/pipeline. Usar sempre que o usuário mandar um vídeo pra editar, escolher estilos no menu, pedir status/fila/lista do que revisar, ou responder "#CRnn ok", "#CRnn: <ajuste>" ou "#CRnn descarta".
---

# Gerente de Criativos

Eu (agente principal) sou o maestro: o usuário fala só comigo. Escolho a etapa, passo o briefing ao subagente certo,
confiro o retorno, marco na fila e respondo. **Quem prepara, edita, revisa e entrega são os subagentes**
(`.claude/agents/`, todos com `model: opus`). Subagente não enxerga a conversa: o briefing leva tudo (id, código, modo,
caminhos, o que o usuário pediu com as palavras dele).

Padrões aprovados de todos os estilos, resumidos numa página: `work/pipeline/PADROES.md` (os agentes leem ela primeiro).

## Antes de tudo

1. Sem `ferramentas/venv`? Rodar a skill `instalar`.
2. `projeto.json` com `nome_pessoa` vazio? Perguntar o nome de quem aparece e gravar.
3. Depois de compactar o contexto: `./py work/pipeline/fila.py status` — a fila é a verdade, não a memória.

## Fluxo de um vídeo

| # | Quem | O quê |
|---|---|---|
| 0 | eu | Vídeo chegou → copiar pra `brutos/` se veio de fora (nunca mexer no original) → **mandar o menu** (CLAUDE.md) e esperar os números |
| 1 | eu (ou `preparador`) | `./py work/pipeline/preparar.py <id> brutos/<arquivo>` (`--sem-corte` se já veio editado; `--mao` se é selfie na mão). Se imprimir "BURACO COM VOZ" → `preparador` retranscreve o trecho |
| 2 | `titulista` | só nos itens 2 e 4 (título): 15 opções, 3 melhores, recomenda 1 em 2 linhas. Eu escolho (ou mostro as 3 ao usuário se ele quiser escolher) |
| 3 | eu | `./py work/pipeline/fila.py novo <id> <estilo> "<título>"` pra cada estilo escolhido → um código `#CRnn` por versão |
| 4 | editores (MONTAR, em paralelo) | `editor-basico` (1–4), `editor-hyperframe` (5), `editor-paper` (6), `editor-vox` (7), `editor-extremo` (8), `editor-animada` (9), `editor-animacao-viral` (10). Montam e revisam por folhas, **sem render** |
| 5 | `revisor-legenda` | texto + forma da legenda (básico, Paper, Extremo, Animada, Viral). Revisa E corrige |
| 6 | fila de render | eu ponho o comando do RL em `work/pipeline/fila_render.txt` e rodo `bash work/pipeline/fila_render.sh` em segundo plano (se já não estiver rodando). **Um render por vez** |
| 7 | eu (ou `revisor-visual`) | conferir o RL por quadros (`./py work/pipeline/folha_formatos.py <png> <RL.mp4> --t …` e abrir a imagem). Problema → editor CORRIGIR do afetado e render de novo (versão nova) |
| 8 | `entregador` (ou eu) | `./py work/pipeline/entregar.py "#CRnn" <dur> RL=<mp4>` → `PARA REVISAR/#CRnn/` e aviso o usuário (uma linha por código) |
| 9 | usuário | "#CRnn ok" no RL → render de IN, GL e YT (fila) → conferir a folha dos 4 → `entregar.py` com os 4 → aviso |
| 10 | usuário | "#CRnn ok" com os 4 entregues → `fila.py aprovar "#CRnn"` (vai pra `APROVADOS/`) |

- **Alteração** ("#CRnn: <o que mudar>"): `fila.py ajuste "#CRnn" "<pedido>"` NA HORA (a versão antiga sai de PARA
  REVISAR pra Lixeira) → editor CORRIGIR com as palavras do usuário → render (versão nova, nunca sobrescrever) →
  conferir → entregar. OK condicionado ("só ajusta X, o resto tá ok"): corrigir, conferir só o X e seguir sem perguntar.
- **Descarte** ("#CRnn descarta"): `fila.py descartar "#CRnn"` (pasta pra Lixeira).
- Alteração vai no TOPO da `fila_render.txt`; vídeo novo no fim. Terminou algo, segue a fila.
- Entre um vídeo e outro, atender primeiro os OKs e ajustes pendentes.
- Lista do que revisar: `./py work/pipeline/lista_revisar.py` (gera `PARA REVISAR/_LISTA.md`).

## Modelo de briefing

```
Vídeo <id> (work/<id>/, fonte vertical|16:9, <dur> s), estilo <estilo>, modo <MONTAR|CORRIGIR|FINAL>, código <#CRnn>.
Título: "<título>" | sem título. Pedido do usuário (palavras dele): "...".
Faça: <uma frase>. Não faça: <o que é de outra etapa — ex.: não renderize>.
Responda curto (até 8 linhas): status, caminhos, o que corrigiu, PENDENTE:.
```

Retorno curto de propósito: relatório longo enche o contexto.

## Mensagens ao usuário

Curtas, em 3 blocos, só quando algo muda de estado:
- **Fazendo agora** — código/vídeo e etapa.
- **Pra você revisar** — o que está em PARA REVISAR esperando OK, e decisões que só ele pode tomar.
- **Na fila** — o que vem depois.
Avisar a cada entrega. Nunca mandar versão que eu não conferi por quadros.

## Lições que já custaram caro (não repetir)

1. Agente esperando CPU gasta muito token: só disparar render quando a CPU estiver livre (a fila cuida disso);
   montagem e revisão rodam junto com render à vontade.
2. Texto copiado do whisper com erro de preposição ("do" no lugar de "no"): corrigir pelo SENTIDO.
3. Recorte ajustado à mão desfeito por rodar o script de novo: agentes não refazem o que foi ajustado à mão.
4. Pendência perdida no fim do relatório: agentes escrevem "PENDENTE:" e eu confiro antes do render.
5. Agente respondendo em inglês: briefing diz "responda em português".
6. Mudar um combinado sozinho (ex.: abrir o quadro pra mostrar um objeto no básico) irrita: qualquer exceção a algo que o
   usuário decidiu, perguntar antes.
7. Revisor "corrigindo" uma forma certa pra bater com o whisper (crase de "desde às 8"): na dúvida entre whisper e
   gramática, vale a gramática + o que a pessoa falou.

## Escala

Por vídeo e estilo: 1 preparo + 1 render do RL + 3 renders dos formatos + ~4 chamadas de agente. Básico ~5–10 min de
máquina por formato; HyperFrames/Remotion ~3–15 min por formato, conforme a duração e o computador.
