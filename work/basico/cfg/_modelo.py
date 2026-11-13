# Modelo de cfg da versão BÁSICA (menu 1–4). Copiar para work/basico/cfg/<id>.py (o <id> é o do preparar.py).
# O exemplo abaixo é o vídeo de demonstração (roteiro em exemplos/demo/roteiro.txt): troque tudo pelo vídeo real.
# Render: ./py work/basico/render.py <id>  (RL primeiro, pra aprovação) e depois --formatos IN,GL,YT.
# Antes do render: ./py work/auditar_legenda.py work/basico/cfg/<id>.py  e  ./py work/basico/render.py <id> --blocos
CFG = dict(
    id="demo",                            # pasta work/<id> (gerada pelo work/pipeline/preparar.py)
    pasta="Título curto do vídeo",        # nome da pasta/arquivo de saída (sem / \ : * ? " < > |)

    # ---- título estilo Edits (menu 2 e 4). Sem título (menu 1 e 3): sem_titulo=True e apague titulo/legenda_desde.
    # 2 linhas curtas (≤ ~24 caracteres cada), 1ª pessoa, gancho de rede social; emoji no máximo 1, só no FIM da frase.
    # O título fica na tela no máximo 6 a 9 s; legenda_desde = índice da última palavra que ele cobre (fim de frase).
    sem_titulo=False,
    titulo=["Trabalhava 12 horas", "e não rendia ⏰"],
    t_titulo=None, legenda_desde=12,
    # gancho_frases="...",                # se a frase do título passa de 9 s: blocos do resto do gancho (viram legenda)

    # ---- legenda
    # correções do whisper (índices do words_cut.json; ver `render.py <id> palavras`): {i: (n_palavras, ["novas"])};
    # (1, []) remove uma hesitação. Corrigir PELO SENTIDO (do/no, a/há, e/é), não só pelo que o whisper ouviu.
    repl={18: (1, ["simples:"]), 31: (1, ["assustou."]), 32: (2, ["70%"]), 44: (1, ["fazer:"]), 76: (1, ["melhor:"])},
    # blocos de 1 a 4 palavras separados por |, uma frase por linha. Nunca terminar bloco em artigo, preposição,
    # conjunção ou "que"; ponto/vírgula fecham o bloco; nada com menos de 0,28 s na tela (conferir com --blocos).
    frases="""Aí eu fiz | um teste simples: | anotei tudo | o que eu fazia | durante cinco dias.
O resultado | me assustou.
70% do meu tempo | ia para tarefas | que outra pessoa | podia fazer: | responder mensagem, | montar orçamento, | conferir pagamento.
Eu passei | essas tarefas | para o meu time, | com um passo a passo | escrito.
Hoje eu trabalho | 8 horas | e entrego | o dobro.
E o melhor: | sobra tempo | para pensar | no que faz | a empresa crescer.
Se você quer | o modelo | que eu uso | para fazer | essa lista, | clica no link | aqui embaixo.""",
    leg_estilo=None,                      # None = legenda simples (1 linha, branca, sombra leve, SEM animação) — PADRÃO
    # leg_estilo="serif", leg_chave=False,  # legenda animada (menu 3/4): frase em até 2 linhas montando palavra por palavra

    # ---- enquadramento (TELA CHEIA sempre; nunca letterbox, faixa desfocada ou quadro)
    enquadro=lambda t: (1.0, 0.33),       # t -> (zoom, altura do rosto 0–1). Punch-in 1,15–1,35 só em fronteira de frase
    # leg_punch_rl=True,                  # punch-in forte no RL: a legenda não cai no queixo
    # mov_amp=0,                          # desliga o movimento leve automático (a imagem nunca fica > 4 s parada)
    # camera_suave=True,                  # (padrão) rastreio do rosto com zona morta e movimento lento
    # titulo_no_peito=True,               # plano aberto (corpo inteiro): título no peito em vez de acima da cabeça
    # Fonte 16:9: leg169=(66, 1260) = corpo e linha de base da legenda no RL (altura FIXA — não mudar pra desviar de objeto)
    # Fonte vertical no YT: yt_zoom_cheio=1.0 (recorte 16:9 cheio em volta do rosto), yt_rosto=0.42
)
