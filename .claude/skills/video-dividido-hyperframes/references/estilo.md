# Estilo em vigor — formato "tela dividida" (Hyperframe)

## Layout (RL 1080x1920)
- Tela dividida no meio: **painel preto `#060606` em cima (1080x960)**, **pessoa embaixo (1080x960)** recortada na escala
  ~1:1 (rosto ~30 % da largura; não fechar demais no rosto). Linha fina entre os dois (`rgba(255,255,255,0.18)`, 2 px).
  Sem barra de progresso.
- **Sem legenda.** O painel de cima representa tudo o que é dito: lettering + ícone/widget.
- **Nada no alto**: grupo centrado numa faixa baixa (padding do painel 220 em cima, 50 embaixo); topo do conteúdo entre
  y ~229 e 500, base ≤ ~847.
- **3 modos** (motor `TRES_MODOS`): de tempos em tempos uma frase inteira com a pessoa em tela cheia (`pessoa_gl`) e
  algumas cenas com a animação em tela cheia; zoom leve na pessoa da dividida. Troca só em fronteira de frase.

## Título de abertura (estilo Edits) — só se pedirem
- Por padrão os vídeos saem **sem título**.
- Quando pedirem: **TikTok Sans 800**, branco, contorno preto 8 px, sombra leve, **68 px**, 2 linhas, centrado **na
  divisória**, cada linha ocupando ~70–76 % da largura. Do quadro 0 até a troca da cena de no máximo ~9 s; some de uma vez.

## Lettering do painel
- **Inter Bold** para textos grandes e bold; **Montserrat Light** (300) quando precisar de fino; linha fina reduzida
  abaixo de 52 px vira Regular (400). Nunca peso 100 (sai falhada no celular). Padrão: apoio fino 56–80 px + linha
  principal bold 84–124 px. Tracking −0,02 em no bold.
- Palavras pré-posicionadas (sem reflow); **cada palavra entra na hora em que é falada** (0,06 s antes): fade 0,2 s +
  8 px de subida, saindo do cinza `#5A5A5A`.
- **Palavra-chave**: gradiente `#10B981 → #34D399`, **só em linha bold** (em traço fino o verde some).
- Linha que não cabe em 880 px é reduzida automaticamente (≥ 100 px de cada lateral).

## Cores
- Preto `#060606`, branco, esmeralda **`#10B981`**, gradiente `#10B981 → #34D399`. Cinzas de apoio: `#A8A8A8` (rótulo),
  `#262626` (contorno de card), `#1E1E1E` (trilho), `#2E2E2E` (barra cinza). Nada de amarelo, nada de creme.

## Elementos
- **Ícones Phosphor peso regular**: brancos, verdes quando o sentido pede (tendência, raio, IA). Entram com revelação de
  baixo pra cima (clip-path 0,32 s). Marcas que animam (visto, X, risco, gráfico de linha) desenhadas em traço. Ícone
  que gira: no sentido das setas.
- **Cards**: só contorno (borda 2 px `#262626`, raio 40, fundo transparente, sem sombra).
- **Selos** (`.chip`): pílula, fundo esmeralda 16 %, texto `#34D399`, Inter Regular, sem caixa alta. Nunca bloco verde
  chapado com texto preto em caixa alta.
- **Rótulos** (HOJE, ANTES…): caixa alta, 0,14 em, peso regular, `#A8A8A8`.
- **Botão de CTA**: pílula grafite, borda cônica esmeralda girando, faixa diagonal de pontos; no clique vira esmeralda
  com visto. Cursor entra depois do corte e clica na palavra. Texto sem "link"/"bio".

## Tempo e movimento
- Troca de cena **0,20 s antes da 1ª palavra**; **corte seco**; ~2,4 s por cena em média.
- Primeiro elemento 0,1–0,16 s depois do corte; painel nunca vazio mais de ~0,2 s.
- Entradas: `entra` (fade + escala 0,92→1, 0,2 s), `pop` (itens de conjunto, stagger 0,04–0,06), `sobe` (barras),
  `estica` (barras horizontais), `desenha` (traço), `revela` (ícone). Depois de entrar o elemento fica parado; o que
  se mexe é micro-animação com sentido (contador, cursor, digitando, sino).

## O que já foi recusado (não repetir)
- Conteúdo colado no alto do painel.
- Selo em bloco verde chapado, caixa alta.
- Setas em loop girando contra o sentido delas.
- Verde em letra fina.
