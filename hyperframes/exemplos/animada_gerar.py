# -*- coding: utf-8 -*-
"""MOLDE da Edição animada (menu 9) — copiar para hyperframes/<id>-animada/gerar.py e trocar tudo pelo vídeo real.
Exemplo feito com o vídeo de demonstração (roteiro em exemplos/demo/roteiro.txt, 42,8 s).

Animação em TELA CHEIA com a voz da pessoa; ela entra em tela cheia numa frase de conversa a cada ~10–15 s
(`pessoa_gl`). Uma cena por frase, sempre com `an.cenario(...)` e pelo menos uma peça de ação. Skill edicao-animada.
Antes: ./py .claude/skills/video-dividido-hyperframes/scripts/preparar.py <id> <id>-animada --formatos
Uso: ./py hyperframes/<id>-animada/gerar.py phosphor RL|YT|IN|GL      (termina com an.aplicar(), nunca montar())
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from motor import *  # noqa: E402,F401,F403

configurar(
    pasta=Path(__file__).resolve().parent,
    palavras='work/demo/words_cut.json',
    duracao=42.77,
    composicao='demo-animada',
    nome='#CR05 Trabalhava 12 horas e não rendia [Animada]',
    pessoa_gl={'c04', 'c08'},          # frases de conversa (a 1ª depois de 5–10 s de animação), a cada ~10–15 s
    correcoes={32: '70%', 33: ''},
)
from pecas import *  # noqa: E402,F401,F403
import animada as an  # noqa: E402
import bonecos as bo  # noqa: E402
import arsenal_animada as ar  # noqa: E402

# ================================================================ GANCHO (quadro 0 já com ação; 1º letreiro começa na linha GROSSA)
c = an.cenario(cena(0, 5, 'Relógio girando rápido: 12 horas por dia'), 'escritorio_noite')
monta(c, '{120}*12 *horas|{64f}por dia', ar.relogio_rapido(c, 0.0))

c = an.cenario(cena(6, 12, 'Agenda sendo riscada: a semana atrasada'), 'sala_dono')
ar.transicao(c, 'tinta')
monta(c, '{64f}e terminava a semana|{110}*atrasado', ar.agenda(c, 6, 'riscando', tempos=[ts(9), ts(11), ts(12)]))

c = an.cenario(cena(13, 27, 'Mão escrevendo: anotei tudo durante cinco dias'), 'copa')
ar.camera(c, 'push', 0.6)
monta(c, '{64f}anotei tudo o que eu fazia|{110}durante *cinco *dias',
      ar.mao_escreve(c, 13, linhas=('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'), t_fim=ts(27)))

# c04 pessoa: "O resultado me assustou." (frase de conversa)
c = an.cenario(cena(28, 31, 'O resultado assustou (pessoa)'), 'copa')
monta(c, '{64f}O resultado|{120}me *assustou')

c = an.cenario(cena(32, 44, '70% do tempo: número contando'), 'pergaminho')
ar.transicao(c, 'pagina')
monta(c, '{64f}do meu tempo ia para tarefas que|{110}outra *pessoa', ar.contador(c, ts(32), 70, sufixo='%', rotulo='DO MEU TEMPO'))

c = an.cenario(cena(45, 50, 'Escritório: mensagem, orçamento, pagamento'), 'escritorio')
ar.camera(c, 'pan_dir', 0.6)
monta(c, '{64f}mensagem, orçamento,|{110}*pagamento', bo.escritorio(c, 45, acoes=('digita', 'telefone', 'celular')))

c = an.cenario(cena(51, 64, 'Escada de passos: passei pro time com passo a passo'), 'reuniao')
ar.transicao(c, 'iris', ponto=(50, 60))
monta(c, '{64f}passei essas tarefas para o|{110}meu *time',
      ar.escada(c, 51, degraus=('Passo 1', 'Passo 2', 'Passo 3'), tempos=[ts(60), ts(62), ts(64)]))

# c08 pessoa: "Hoje eu trabalho 8 horas e entrego o dobro."
c = an.cenario(cena(65, 73, 'Hoje: 8 horas e o dobro (pessoa)'), 'reuniao')
monta(c, '{64f}Hoje eu trabalho 8 horas|{110}e entrego o *dobro')

c = an.cenario(cena(74, 86, 'Foguete: sobra tempo pra fazer a empresa crescer'), 'campo')
ar.transicao(c, 'chicote')
ar.camera(c, 'push', 0.8)
monta(c, '{64f}sobra tempo para pensar|{104}a empresa *crescer', ar.foguete(c, 74, t_lanca=ts(85)))

# CTA: nada de botão, cursor ou "link" na tela — a frase vira cena de ação
c = an.cenario(cena(87, 103, 'Lâmpada: o modelo da lista'), 'sala_dono')
ar.transicao(c, 'auto')
monta(c, '{64f}o modelo que eu uso|{110}essa *lista', ar.lampada(c, 87, t_acende=ts(97)))

an.aplicar()
