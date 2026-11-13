---
name: editor-vox
description: Editor VOX (menu 7) — editar um vídeo no estilo explainer da Vox / colagem documental, em tela dividida HyperFrames (painel animado em cima, pessoa embaixo; YT lado a lado; IN/GL alternando pessoa cheia e animação cheia), com papel creme e fundo escuro alternando, tiras de papel rasgado, marca-texto amarelo, foto da própria pessoa em retícula, bilhete com checklist, número gigante, carimbo, stop-motion e efeitos sonoros leves. Usar quando o usuário escolher "VOX" no menu, pedir "estilo Vox", ou quando o gerente delegar a versão VOX de um vídeo.
---

# Editor VOX

## Arquivos
- `hyperframes/vox.py` — estilo + peças + montagem (`vox.aplicar()` substitui o `montar()` do motor).
- `hyperframes/<id>-vox/gerar.py` — um por vídeo. **Molde: `hyperframes/exemplos/vox_gerar.py`**.
- Motor e peças em comum com o Hyperframe: `hyperframes/motor.py`, `hyperframes/pecas.py` (API em
  `.claude/skills/video-dividido-hyperframes/references/cenas.md`).
- Sons: `remotion/public/sfx/*.wav` (copiados sozinhos pra `public/sfx/`). Fontes: TikTok Sans 900 (manchete) e
  EB Garamond (apoio, recorte de jornal), copiadas sozinhas de `ferramentas/fontes/`.

## Gramática visual
1. Papel creme com grão/vinheta; a cada 4–6 cenas uma `vox.escura(cena(...))` (folha escura amassada) pra virar o ritmo.
2. Manchete em tira de papel rasgado (TikTok Sans 900), apoio em recorte de jornal. `*palavra` = marca-texto amarelo
   pintando quando a pessoa fala.
3. Ícones Phosphor fill viram recorte de papel; o ícone `'verde'` ganha círculo desenhado à mão e cor tijolo.
4. Peças documento (uma a cada 3–4 cenas):
   - `vox.foto(c, t, momento, larg=400, rot=-3, legenda='...')` — quadro da PRÓPRIA pessoa em retícula, fita e sombra.
   - `vox.nota(c, 'Título', ['item', ...], [idx_palavra, ...])` — bilhete com tachinha, ✓ quando ela fala cada item.
   - `vox.jornal(c, 'texto', 'trecho', t, t_marca)` — recorte de jornal com trecho marcado (texto = fala, nunca inventado).
   - `vox.numero(c, '80%', t, tam=300, cor='#F5D90A')` — número cortado ao meio (melhor em cena escura).
   - `vox.carimbo(c, 'NÃO É ISSO', t)` — contraste/negação.
5. Sem régua de progresso (`vox.secoes()` só se pedirem).
6. Movimento: stop-motion a 12 fps, câmera empurrando 3,5 % por cena, bordas "fervendo" a 8 fps. **Letra nunca se mexe**
   (o "boil" fica só na folha).
7. Tudo estilo papel: gráfico, chat, calendário, passos e chips viram papel (nada "moderno" de app). Retícula só cinza e
   apagada. Botão de CTA: depois do clique fica verde, com som de clique.
8. Som (automático + o das peças): whoosh na troca (no máx. 1 a cada 3,5 s), pop nos ícones, papel nas fotos/bilhetes,
   tique nos ✓, carimbo. Volumes baixos; nunca cobrir a voz.
9. 3 modos no RL (motor `TRES_MODOS`): cenas do `pessoa_gl` = pessoa em tela cheia; cenas escuras = animação cheia;
   o resto dividida com zoom leve na pessoa. Troca só em fronteira de frase.

## Passo a passo (MONTAR)
1. `./py .claude/skills/video-dividido-hyperframes/scripts/preparar.py <id> <id>-vox --formatos` (recortes da pessoa,
   voz, fontes; imprime a duração e a transcrição numerada). Se já existir `hyperframes/<id>-hf/`, dá pra copiar o
   `public/` de lá e reaproveitar cenas e correções.
2. `hyperframes/<id>-vox/gerar.py` a partir do molde: uma cena por frase; a cada 3–4 cenas uma peça documento; a cada
   4–6 uma cena escura. Número falado → `vox.numero`; lista falada → `vox.nota`; contraste → `vox.carimbo`;
   "minha empresa/eu" → `vox.foto` com um quadro da própria pessoa. Correções de palavra = texto revisado da legenda.
   `pessoa_gl` = cenas de frase de conversa inteira (ritmo ~1 pessoa : 2 animadas), fora do CTA final.
3. `./py hyperframes/<id>-vox/gerar.py phosphor RL` e `./py .claude/skills/video-dividido-hyperframes/scripts/revisar.py <id>-vox RL`;
   abrir `hyperframes/<id>-vox/revisao-RL.png` e corrigir sozinho (texto estourando, peça cortada, sobreposição, margem
   lateral < 100 px, cena vazia, cena escura ilegível). Depois `GL` e `IN`. O `check` acusa "content_overlap" no número
   cortado (as duas metades são o mesmo texto, de propósito) — esperado.
4. **Não renderizar.** Comandos pro gerente: `./py .claude/skills/video-dividido-hyperframes/scripts/renderizar.py <id>-vox saidas/<id>-vox-v1 RL --crf 20`
   e, depois do OK, `... YT,IN,GL`.

## Formatos
RL e YT tela dividida (YT painel à esquerda, pessoa à direita, sem desfoque); IN e GL alternam pessoa em tela cheia
(`pessoa_gl`, recorte 4:5 no IN) e animação em tela cheia. RL primeiro pra aprovação.

## Regras
Todas do CLAUDE.md, em especial: nada de "link na bio"/QR/URL escrito; texto pelo sentido; pessoa aparece em todo
formato; cor da pessoa intacta; margens ≥ 100 px; nada parado > 4 s.
