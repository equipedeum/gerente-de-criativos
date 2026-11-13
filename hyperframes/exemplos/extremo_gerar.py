# -*- coding: utf-8 -*-
"""MOLDE do Editor Extremo (menu 8) — copiar para hyperframes/<id>-extremo/gerar.py e trocar tudo pelo vídeo real.
Exemplo feito com o vídeo de demonstração (roteiro em exemplos/demo/roteiro.txt, fonte VERTICAL de celular, 42,8 s).

Estilo: hyperframes/extremo.py (processo na skill .claude/skills/editor-extremo). Modos por cena:
D = dividida (gráfico em cima, pessoa embaixo) / G = gráfico em tela cheia / T = pessoa em tela cheia (close, com legenda).
- Uma cena por frase (~3–4 s), D↔G alternando, T numa frase de conversa/virada a cada ~10 s.
- Fonte vertical: no IN/GL toda D vira G -> `modos={'IN': 'T', 'GL': 'T'}` em cenas D pra a pessoa aparecer a cada ~10 s
  também nesses formatos (REGRA: a pessoa aparece em todo formato).
- "clica no link aqui embaixo" fica numa cena G (nada de "link" escrito na tela; o botão diz "Clica aqui embaixo").
Uso: ./py hyperframes/<id>-extremo/gerar.py [phosphor] RL|IN|GL|YT
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import extremo as X  # noqa: E402

X.ZOOM_D = False                    # pessoa sem zoom na dividida (faixa inteira, escala mínima). Nunca num "cartão"/quadro.
X.ALVO_V[('GL', 'T')] = (420, 0.06)  # fonte vertical: no GL a pessoa cheia sobe um pouco (legenda cabe abaixo do queixo)

X.configurar(
    pasta=Path(__file__).resolve().parent,
    palavras='work/demo/words_cut.json',
    duracao=42.77,                   # mín(voice.wav, base), 2 casas pra baixo
    composicao='demo-extremo',
    nome='#CR03 Trabalhava 12 horas e não rendia [Extremo]',
    # correções do whisper (as mesmas do cfg do básico, revisadas pelo sentido)
    repl={18: (1, ['simples:']), 31: (1, ['assustou.']), 32: (2, ['70%']), 44: (1, ['fazer:']), 76: (1, ['melhor:'])},
    # legenda simples de 1 linha (só aparece no T): blocos de 1–4 palavras por unidade de sentido
    frases="""Eu trabalhava | 12 horas por dia | e mesmo assim | terminava a semana | atrasado. |
Aí eu fiz | um teste simples: | anotei tudo | o que eu fazia | durante cinco dias. |
O resultado | me assustou. |
70% do meu tempo | ia para tarefas | que outra pessoa | podia fazer: | responder mensagem, | montar orçamento, | conferir pagamento. |
Eu passei | essas tarefas | para o meu time, | com um passo a passo | escrito. |
Hoje eu trabalho | 8 horas | e entrego | o dobro. |
E o melhor: | sobra tempo | para pensar | no que faz | a empresa crescer. |
Se você quer | o modelo | que eu uso | para fazer | essa lista, | clica no link | aqui embaixo.""",
)
from extremo import (alerta, barras, cena, chapeu, checkcard, cta, equipe, icone, lista, numero,  # noqa: E402,F401
                     passo, pilula, riscado, semana, som, titulo)

# ================================================================ GANCHO (já abre em D com peça no 1º quadro)
c = cena(0, 12, 'D', '12 horas por dia', modos={'IN': 'T', 'GL': 'T'})
numero(c, 0, 12, 1, dur=0.5, suf=' horas', rotulo='POR DIA', tam=150)
titulo(c, 'e a semana|*atrasada*', 11)

c = cena(13, 27, 'G', 'O teste de cinco dias')
chapeu(c, 'Um teste simples', 13)
semana(c, 19, dias=('SEG', 'TER', 'QUA', 'QUI', 'SEX'), icone='note-pencil')
titulo(c, 'anotei *tudo*', 20)

c = cena(28, 31, 'T', 'Pessoa: o resultado me assustou', modos={'YT': 'D'})
titulo(c, 'me *assustou*', 31)

# ================================================================ MIOLO
c = cena(32, 44, 'G', '70% do tempo')
numero(c, 0, 70, 32, dur=0.8, suf='%', rotulo='DO MEU TEMPO', barra=33)
titulo(c, 'outra pessoa|podia *fazer*', 43)

c = cena(45, 50, 'D', 'Mensagem, orçamento, pagamento')
checkcard(c, [('Responder *mensagem*', 45, 46), ('Montar *orçamento*', 47, 48), ('Conferir *pagamento*', 49, 50)], larg=740)

c = cena(51, 64, 'G', 'Passei pro time com passo a passo')
equipe(c, 3, 52, rotulo='O MEU TIME')
passo(c, 1, 'Passo a passo|*escrito*', 61, icone='list-numbers')

c = cena(65, 73, 'T', 'Pessoa: hoje trabalho 8 horas e entrego o dobro', modos={'YT': 'D'})
titulo(c, 'entrego o *dobro*', 73)

c = cena(74, 86, 'D', 'Sobra tempo pra crescer', modos={'IN': 'T', 'GL': 'T'})
chapeu(c, 'E o melhor', 74)
icone(c, 'trend-up', 85, rotulo='A empresa cresce')

# ================================================================ CTA (sem "link" escrito)
c = cena(87, 98, 'G', 'O modelo da lista')
chapeu(c, 'O modelo que eu uso', 87)
icone(c, 'list-checks', 97, rotulo='A lista pronta')

c = cena(99, 103, 'G', 'Clica aqui embaixo')
cta(c, 'Clica aqui embaixo', 99, 102, icone='arrow-down')

X.aplicar()
