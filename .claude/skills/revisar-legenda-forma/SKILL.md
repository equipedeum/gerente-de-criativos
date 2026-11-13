---
name: revisar-legenda-forma
description: Revisão 2 da legenda de um vídeo — confere a FORMA e o TEMPO dos blocos (1 a 4 palavras, unidade de sentido, onde corta — nunca terminar em artigo/preposição/conjunção/"que" —, frase nova no meio, bloco que pisca < 0,28 s, sincronia e tamanho na tela) com work/auditar_legenda.py, e CORRIGE a divisão. Usar a pedido do gerente-de-criativos depois da revisão de texto e antes do render.
---

# Revisar legenda — forma e tempo

Exemplo BOM: "A cidade / despertava lentamente / enquanto a chuva fina / cobria as ruas. / No café da esquina, / pessoas
conversavam / sobre planos, / viagens e problemas / que pareciam enormes / naquela manhã."
RUIM: blocos de 5–8 palavras cortados no meio do sentido ("lentamente enquanto a / chuva fina cobria as / ruas. No café da").

## Verificações
1. **Tamanho**: 1 a 4 palavras. Só passa de 4 quando cortar separaria artigo/preposição do nome ("de 5 em 5 minutos").
   Paper: até ~16 caracteres por linha.
2. **Onde corta**: ANTES de conector ("que", "e", "mas", "enquanto"), nunca depois. Nunca terminar em artigo, preposição,
   pronome relativo ou conjunção (de, da, do, a, o, um, e, ou, mas, que, para, pra, com, em, no, na, por, seu, sua, meu,
   se, sem, ao…), salvo pontuação que fecha.
3. **Unidade de sentido**: sujeito | ação | complemento. Ponto e vírgula fecham o bloco. Nunca começar frase nova no meio.
4. **Não piscar**: bloco < ~0,28 s na tela é ilegível; juntar ao vizinho.
5. **Sincronia**: entra na 1ª palavra e sai na última; apontar bloco que fica na tela depois de pausa longa (> 0,6 s).
6. **Cabe na tela**: na zona segura, sem encostar na borda nem cobrir o rosto/título; nunca fonte peso 100.

## Como medir
- Básico: `./py work/auditar_legenda.py work/basico/cfg/<id>.py` e `./py work/basico/render.py <id> --blocos` (não renderiza).
- Paper: `./py remotion/scripts/legenda_paper.py ...` lista o que pede "revisar"; durações no `<id>-legenda.json`.
- Cruzar com `work/<id>/words_cut.json`.

## Saída
Corrigir a divisão no arquivo da legenda e gravar `work/pipeline/revisoes/<id>-<estilo>-forma.md`:
```
# <id> — <estilo> — revisão de FORMA
Veredito: APROVADO | CORRIGIDO (N itens)
1. "<antes>" (t=…s, dur …s) -> "<A | B>" | regra
```
Responder ao Gerente em até 6 linhas.
