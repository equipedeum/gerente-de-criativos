# -*- coding: utf-8 -*-
"""MOLDE do Hyperframe (menu 5, tela dividida) — copiar para hyperframes/<id>-hf/gerar.py e trocar tudo pelo vídeo real.
Exemplo feito com o vídeo de demonstração (roteiro em exemplos/demo/roteiro.txt, 42,8 s).

Pessoa embaixo, painel preto em cima: tudo o que ela fala vira lettering palavra por palavra (Inter Bold + Montserrat
Light) + um ícone/widget que é a metáfora literal da frase. Sem legenda, sem título (só se pedirem).
Antes: ./py .claude/skills/video-dividido-hyperframes/scripts/preparar.py <id> <id>-hf --formatos
Uso: ./py hyperframes/<id>-hf/gerar.py phosphor RL|YT|IN|GL
API: .claude/skills/video-dividido-hyperframes/references/cenas.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from motor import *  # noqa: E402,F401,F403

configurar(
    pasta=Path(__file__).resolve().parent,
    palavras='work/demo/words_cut.json',
    duracao=42.77,
    composicao='demo-hf',
    nome='#CR02 Trabalhava 12 horas e não rendia [Hyperframe]',
    # GL (e o RL nos 3 modos): cenas com a pessoa em tela cheia — frase de conversa INTEIRA, ~1 pessoa : 2 animadas
    pessoa_gl={'c02', 'c05', 'c08', 'c11'},
    # palavra -> texto revisado ('' some). Mesma ortografia da legenda revisada.
    correcoes={32: '70%', 33: ''},
)
from pecas import *  # noqa: E402,F401,F403

# '{64f}texto' = linha fina (Montserrat Light); '{104}texto' = linha bold (Inter Bold); '*palavra' = palavra-chave verde
c = cena(0, 5, '12 horas por dia')
monta(c, '{64f}Eu trabalhava|{120}*12 *horas', linha(c, [ic('clock', 210, t=2, anim='pop')]))

c = cena(6, 12, 'Semana atrasada')
monta(c, '{64f}e mesmo assim terminava|{104}a semana *atrasada', linha(c, [ic('calendar-x', 210, 'verde', t=12, anim='pop')]))

c = cena(13, 18, 'Um teste simples')
monta(c, '{64f}Aí eu fiz um|{120}teste *simples', linha(c, [ic('flask', 200, t=17)]))

c = cena(19, 27, 'Anotei cinco dias')
monta(c, '{64f}anotei tudo o que eu fazia|{104}durante *cinco *dias', calendario(c, 27, rotulo='5 dias'), gap=30)

c = cena(28, 31, 'O resultado assustou')
monta(c, '{64f}O resultado|{120}me *assustou', linha(c, [ic('warning', 200, 'verde', t=31, anim='pop')]))

c = cena(32, 44, '70% em tarefas dos outros')
monta(c, '{64f}do meu tempo ia para tarefas|{120}*70%|{60f}que outra pessoa podia fazer',
      comparacao(c, 32, antes='Meu tempo', depois='Delegável', de=100, ate=70, t_muda=40), gap=30)

c = cena(45, 50, 'Mensagem, orçamento, pagamento')
monta(c, '{64f}mensagem, orçamento,|{104}*pagamento',
      linha(c, [ic('chat-text', 150, t=46), ic('file-text', 150, t=48), ic('credit-card', 150, 'verde', t=50, anim='pop')]))

c = cena(51, 64, 'Passei pro time com passo a passo')
monta(c, '{64f}passei essas tarefas para o|{110}meu *time', passos(c, [60, 62, 64]), gap=40)

c = cena(65, 73, 'Oito horas, o dobro')
monta(c, '{64f}Hoje eu trabalho 8 horas|{110}e entrego o *dobro', barras(c, 70, 'Entrega', t_seta=73), gap=30)

c = cena(74, 86, 'Tempo pra crescer')
monta(c, '{64f}sobra tempo para pensar no que faz|{104}a empresa *crescer', grafico_linha(c, 84, 'rocket-launch'), gap=30)

c = cena(87, 98, 'O modelo da lista')
monta(c, '{64f}o modelo que eu uso para fazer|{110}essa *lista', linha(c, [ic('list-checks', 210, t=97, anim='pop')]))

c = cena(99, 103, 'Clica aqui embaixo')
monta(c, '{64f}Clica|{110}aqui *embaixo', cta(c, 101, texto='Quero o modelo', seta_t=102), gap=34)

montar()
