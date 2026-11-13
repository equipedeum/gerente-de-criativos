---
name: revisar-legenda-texto
description: Revisão 1 da legenda de um vídeo — confere o TEXTO contra o que foi falado (words_cut.json), achando erros do whisper, ortografia, acentos, crase, nomes (os do projeto.json), siglas, números e pontuação, e CORRIGE no arquivo da legenda. Usar a pedido do gerente-de-criativos antes do render, ou quando o usuário pedir pra revisar o texto de uma legenda.
---

# Revisar legenda — texto

Revisa E CORRIGE (no arquivo da legenda) e grava o que mudou. Não renderiza.

## Entrada
- Transcrição: `work/<id>/words_cut.json` (`[{w,s,e,p}]`; `p` = confiança do whisper, desconfiar de `p < 0,6`).
- Legenda: básico `work/basico/cfg/<id>.py` (`frases`, `repl`, `titulo`); Paper `remotion/src/paper/videos/<id>-blocos.txt`
  (+ `<id>-legenda.json`); Extremo `frases`/`repl` do `hyperframes/<id>-extremo/gerar.py`; Hyperframe/VOX/Animada
  `correcoes` do `gerar.py` (texto da tela).
- Nomes e marcas: `projeto.json` (`nome_pessoa`, `marca`, `termos_transcricao`).

## O que conferir
1. **Fidelidade**: cada bloco diz o que foi falado, na ordem. Nada acrescentado, omitido ou reescrito "pra ficar bonito".
   Gagueira repetida pode sair; outra mudança de palavra, não (sinalizar e deixar o usuário decidir).
2. **Erros típicos do whisper**: siglas lidas como letras soltas ("soluções de A prontas" → "IA prontas"), nomes
   próprios, marcas, palavras parecidas. **Pelo SENTIDO**: preposição/artigo curto que não faz sentido (do/no, da/na,
   a/há, e/é) é erro de transcrição. Trecho dúbio: usar a probabilidade e o contexto; se não der, "confirmar com o usuário".
3. **Ortografia, acentuação, concordância, crase**: "desde às 8", "às X horas", "à noite", "à tarde", "à vista"; sem
   crase antes de verbo, palavra masculina, "uma" e em "a partir de". Nunca trocar uma forma certa por errada pra bater
   com o whisper. Buscar no fim: `desde as `, ` as \d`, `a noite`, `a tarde`.
4. **Pontuação**: ponto/vírgula/interrogação onde a fala pede.
5. **Números e siglas**: "R$", "%", "10 mil"; nunca inventar número.
6. **Título** (básico 2/4): ortografia; não prometer o que o vídeo não diz.
7. Sem travessão (— ou –) no texto da tela.

## Saída
Corrigir no arquivo e gravar `work/pipeline/revisoes/<id>-<estilo>-texto.md`:
```
# <id> — <estilo> — revisão de TEXTO
Veredito: APROVADO | CORRIGIDO (N itens)
1. "<antes>" (palavras i–j) -> "<depois>" | motivo | certeza: alta|média|confirmar
Dúvidas para o usuário: ...
```
Responder ao Gerente em até 6 linhas.
