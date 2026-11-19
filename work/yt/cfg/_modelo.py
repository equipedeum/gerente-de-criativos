"""Molde do cfg do YouTube dinâmico (menu 11). Copie pra work/yt/cfg/<id>.py e preencha lendo work/<id>/words_cut.json.

TUDO em TEMPO DO PRÉ-CORTE (segundos do work/<id>/voice.wav, igual ao words_cut.json). O montar.py converte.
Texto com *palavra* = itálico na cor de destaque da marca. Texto conferido contra a FALA (corrija o whisper pelo sentido).

limpeza   : (início, fim, "descrição") de cada tropeço/repetição/recomeço que sai. Corte DENTRO de pausa: do fim da
            última palavra boa até o começo da retomada (ou do começo do erro até antes da versão certa). Fica sempre a
            versão mais completa/limpa. Sem limpeza = lista vazia.
capitulos : quebra de capítulo (cartão de tela cheia, ~1,3 s). `pausa` = um instante DENTRO do silêncio antes da 1ª
            palavra do capítulo novo. 1 a cada ~40–70 s de vídeo, quando o assunto muda de verdade. num "01", "02"…
paineis   : painel de papel à esquerda (a pessoa desliza pra direita). Um por ideia forte, ~4–7 s, a cada ~10–20 s.
            itens entram no tempo `t` da palavra; `risco` = quando é riscado (ideia negada). Tipos:
              titulo (texto, tam 70–110) | check (texto) | chip (texto; chips seguidos ficam na mesma linha)
              numero (texto = número, sufixo) | passo (texto; vira uma linha do tempo vertical) | infinito (texto)
              seta (aponta pra baixo, sem texto) | logo (logo da marca, ou o nome dela em texto)
            ate_capitulo=True: o painel cresce e vira o cartão do capítulo seguinte (painel logo antes de um capítulo).
selos     : círculo na cor de destaque flutuando à esquerda, com a pessoa em plano aberto (frase de impacto, número).
enfase    : tempos de frases de virada: punch-in forte no começo da frase mais perto.
aviso     : texto livre que vai no fim do relatório (ex.: fala que não serve pro YouTube, como "link na bio").
ini / fim : (opcionais) onde o vídeo começa e termina; padrão = 0,4 s antes da 1ª palavra / 0,3 s depois da última.
"""

CFG = {
    "titulo": "Título do vídeo",
    "limpeza": [
        # (31.42, 38.45, "\"porque já tem hoje ferramentas,\" (repetição; fica a 2ª)"),
    ],
    "capitulos": [
        # dict(pausa=70.00, num="01", titulo="O que *muda*", alvo=1.30),
    ],
    "paineis": [
        # dict(t0=1.25, t1=7.42, rotulo="Boas-vindas ao", itens=[
        #     dict(tipo="logo", t=1.32),
        #     dict(tipo="chip", texto="soluções", t=5.30),
        #     dict(tipo="chip", texto="ferramentas", t=6.30),
        # ]),
        # dict(t0=39.55, t1=45.42, rotulo="Plataforma com", itens=[
        #     dict(tipo="numero", texto="180", sufixo="aulas", t=39.72, risco=41.15),
        #     dict(tipo="titulo", texto="horas de\nconteúdo", t=42.45, tam=72, risco=44.55),
        # ]),
        # dict(t0=43.50, t1=63.95, rotulo="Você pode", itens=[
        #     dict(tipo="passo", texto="ir *dormir*", t=43.85),
        #     dict(tipo="passo", texto="projeto *pronto*", t=59.65),
        # ]),
    ],
    "selos": [
        # dict(t0=59.55, t1=62.95, texto="no mesmo\ndia", tam=64),
        # dict(t0=85.40, t1=87.62, texto="100%", tam=104, legenda="no meu processo"),
    ],
    "enfase": [],
}
