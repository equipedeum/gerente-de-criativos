# -*- coding: utf-8 -*-
"""MOLDE do Editor VOX (menu 7) — copiar para hyperframes/<id>-vox/gerar.py e trocar tudo pelo vídeo real.
Exemplo feito com o vídeo de demonstração (roteiro em exemplos/demo/roteiro.txt, 42,8 s).

Motor: hyperframes/motor.py + peças hyperframes/pecas.py + estilo hyperframes/vox.py (foto em retícula da própria
pessoa, bilhete com checklist, número cortado, carimbo, cenas escuras, câmera empurrando, sons leves). Skill editor-vox.
Antes: ./py .claude/skills/video-dividido-hyperframes/scripts/preparar.py <id> <id>-vox --formatos
Uso: ./py hyperframes/<id>-vox/gerar.py phosphor RL|YT|IN|GL      (termina com vox.aplicar(), nunca montar())
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from motor import *  # noqa: E402,F401,F403

configurar(
    pasta=Path(__file__).resolve().parent,
    palavras='work/demo/words_cut.json',
    duracao=42.77,
    composicao='demo-vox',
    nome='#CR04 Trabalhava 12 horas e não rendia [VOX]',
    pessoa_gl={'c03', 'c07', 'c09', 'c11'},   # IN/GL: cenas com a pessoa em tela cheia (frase inteira de conversa)
    correcoes={32: '70%', 33: ''},            # palavra -> texto revisado ('' some); mesma ortografia da legenda revisada
)
from pecas import *  # noqa: E402,F401,F403
import vox  # noqa: E402

# ================================================================ GANCHO
c = cena(0, 5, '12 horas por dia')
monta(c, '{64f}Eu trabalhava|{120}*12 *horas', linha(c, [ic('clock', 210, t=2, anim='pop')]))

c = vox.escura(cena(6, 12, 'Semana atrasada'))
monta(c, '{64f}e mesmo assim terminava|{110}a semana *atrasada', vox.carimbo(c, 'ATRASADO', ts(12)), gap=50)

c = cena(13, 27, 'O teste de cinco dias')
monta(c, '{64f}Aí eu fiz um|{110}teste *simples',
      vox.nota(c, 'Anotei tudo', ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'], [20, 22, 24, 25, 27]), gap=34)

c = cena(28, 31, 'O resultado me assustou (foto da pessoa)')
monta(c, '{64f}O resultado|{110}me *assustou', vox.foto(c, ts(29), 11.5, larg=400, rot=-3, legenda='EU, NA SEMANA'), gap=40)

# ================================================================ MIOLO
c = vox.escura(cena(32, 44, '70% do tempo'))
monta(c, '{64f}do meu tempo ia para tarefas', vox.numero(c, '70%', ts(32), tam=300, cor='#F5D90A'),
      linha(c, [ic('users', 150, 'verde', t=42, anim='pop')]), gap=30)

c = cena(45, 50, 'Mensagem, orçamento, pagamento')
monta(c, '{64f}conferir|{100}*pagamento',
      vox.nota(c, 'Tarefa de outra pessoa', ['Mensagem', 'Orçamento', 'Pagamento'], [46, 48, 50], larg=600), gap=34)

c = cena(51, 58, 'Passei pro time')
monta(c, '{64f}Eu passei essas tarefas|{110}para o meu *time',
      linha(c, [ic('list-checks', 170, t=53), ic('users-three', 200, 'verde', t=57, anim='pop')]))

c = cena(59, 64, 'Passo a passo escrito')
monta(c, '{64f}com um|{110}passo a *passo', passos(c, [60, 62, 64]), gap=40)

c = cena(65, 73, 'Oito horas, o dobro')
monta(c, '{64f}Hoje eu trabalho 8 horas|{110}e entrego o *dobro',
      linha(c, [ic('clock', 170, t=68), ic('chart-line-up', 200, 'verde', t=73, anim='pop')]))

c = vox.escura(cena(74, 86, 'Tempo pra crescer'))
monta(c, '{64f}sobra tempo para pensar|{104}a empresa *crescer',
      grafico_linha(c, 84, 'rocket-launch'), gap=30)

# ================================================================ CTA (sem "link" escrito na tela)
c = cena(87, 98, 'O modelo da lista')
monta(c, '{64f}o modelo que eu uso|{110}para fazer essa *lista', linha(c, [ic('note-pencil', 210, t=97, anim='pop')]))

c = cena(99, 103, 'Clica aqui embaixo')
monta(c, '{64f}Clica|{110}aqui *embaixo', cta(c, 101, texto='Quero o modelo', seta_t=102), gap=34)

vox.aplicar()
