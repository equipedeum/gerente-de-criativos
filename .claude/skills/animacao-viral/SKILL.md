---
name: animacao-viral
description: Animação viral (menu 10) — o vídeo vira um desenho 3D estilo short viral (personagens 2D "cabeça de feijão" com contorno a tinta num mundo 3D pintado, câmera em travelling, desfoque de lente), em Remotion + three.js. Alterna 3 modos com corte a cada 3–5 s em fim de frase: pessoa em tela cheia (único com legenda simples de 1 linha), tela dividida (animação em cima, pessoa embaixo) e animação em tela cheia; CTA na pessoa. Usar quando o usuário escolher "Animação viral" no menu, pedir "animação 3D", "bonequinho 3D", ou quando o gerente delegar.
---

# Animação viral

Motor em `remotion/src/animada3d/motor/` (adaptado da skill `mromidev/claude-animated-shorts`, MIT — licença em
`motor/LICENSE-claude-animated-shorts.txt`). **Molde: `remotion/src/animada3d/exemplo/`** (`roteiro.md`, `cena.ts`,
`Video.tsx`; os tempos são de outro vídeo — troque tudo). Entrada própria: `remotion/src/animada3d/index.tsx` (não usar
`src/Root.tsx`), pasta pública própria `remotion/public-animada3d/`.

## Estrutura: 3 MODOS alternando
- **T** = pessoa em tela cheia (sem zoom novo), com legenda simples de 1 linha (branca, sombra leve, sem animação, abaixo
  do queixo, y ≈ 1196 no RL). É o ÚNICO modo com legenda.
- **D** = tela dividida: animação 3D em cima (1080 × divY), pessoa embaixo, sem legenda. `divY` por vídeo (padrão 960;
  fonte em close, rosto enchendo a faixa: `divY: 820`).
- **A** = animação 3D em tela cheia, sem legenda.
- Corte a cada 3–5 s, SEMPRE em início/fim de frase (ou de item de lista falada). Nunca o mesmo modo duas vezes seguidas;
  ~1/3 do tempo em cada; começa em D ou A; CTA final em T. Trecho cuja fala tem "link", "link na bio", "Direct" NÃO pode
  ser T (a legenda mostraria a palavra): vira D ou A. Frase longa sem ponto de corte pode passar um pouco de 5 s.
- O vídeo só entrega DADOS (`TRECHOS: [início, fim, 'T'|'D'|'A'][]`, legenda, sons, arquivos) → `<AnimacaoViral d={...} />`.
  O motor confere a regra e escreve no log `[animacao-viral] T x s · D y s · A z s · AVISOS: ...`.
- **Câmera da dividida:** toda tomada que cai em D precisa de `camD` (fov vertical da FAIXA 1080 × divY; fov 28–36 e o
  alvo ~0,2 m abaixo do rosto). Sem `camD`, a dividida mostra o miolo apertado do enquadramento vertical.
- Sons que caem em trecho T são descartados pelo motor (sem evento visível). Banco em `public-animada3d/sfx/` (cópia de
  `remotion/public/sfx-animada/`), volume 0,10–0,24. Sem trilha.
- **A COR DA PESSOA NÃO MUDA**: nenhum filtro em cima do vídeo dela; render SEMPRE com `--color-space=bt709` e quadros
  PNG (já no `remotion.config.ts` e no `render_a3d.sh`). Conferir no MP4: `yuv420p, tv, bt709`, e um quadro T contra o bruto.

## Passo a passo
1. **Material** em `remotion/public-animada3d/` (sem tratamento de cor):
   - `<id>-voz.m4a` (loudnorm −16): `ffmpeg -i work/<id>/voice.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:a aac -b:a 192k remotion/public-animada3d/<id>-voz.m4a`;
   - pessoa cheia 1080×1920 e pessoa dividida 1080 × (1920 − divY):
     - fonte vertical (`work/<id>/base.mov`): `./py remotion/scripts/pessoa_dividido_animada3d.py <id> remotion/public-animada3d/<id>-pessoa-dividido.mp4 --alt 1100 --rosto 0.50`
       (largura inteira, janela seguindo o rosto, só crop + scale, tags bt709); a cheia =
       `ffmpeg -i work/<id>/base.mov -an -vf scale=1080:1920:flags=lanczos -c:v libx264 -crf 17 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv remotion/public-animada3d/<id>-pessoa-cheio.mp4`;
     - fonte 16:9 (`base_h.mov`): `./py remotion/scripts/pessoa_formatos_animada3d.py <id>` (gera também os recortes dos
       formatos IN/GL/YT);
   - `sfx/` e `fontes/` (copiar `remotion/public/sfx-animada/*.wav` pra `public-animada3d/sfx/`; a fonte já está lá).
   Conferir num quadro de 3 momentos que a cabeça não é cortada.
2. **Roteiro** `remotion/src/animada3d/<id>/roteiro.md`: tabela de MODOS, depois uma linha por frase com o que acontece
   em 3D e a câmera.
3. **Cena** `cena.ts` (tomadas com `cam` e, nas que caem em D, `camD`) e `Video.tsx` (só DADOS), copiando o molde.
   Registrar `<id>-animada3d` em `remotion/src/animada3d/index.tsx`. Peça que serve pra outros vídeos vai pro
   `motor/desenhos.ts`; cenários prontos em `motor/cenarios.ts` (`sala`, `janela`, `estante`, `mesaPC`, `pracinha`,
   `banco`, `poste`, `festa`).
4. **Fotos e folha** (dentro de `remotion/`), 3–4 rodadas:
   ```
   node scripts/fotos_animada3d.mjs <id>-animada3d <pasta> 1.2 4.6 6.9 ...
   ../py scripts/folha_animada3d.py <pasta> src/animada3d/<id>/revisao-RL.png 7 380
   ```
   Rodar as fotos com `A3D_LOG=1` varrendo as tomadas com placa e zerar os avisos `[texto-fora]`.
5. **Render** (fila do Gerente, um por vez): `bash remotion/render_a3d.sh <id>-animada3d:../saidas/<id>-animada3d-v1.mp4`.
   No Mac, se o `--gl=angle` der problema: `GL_REMOTION=swangle bash remotion/render_a3d.sh ...`.
6. Conferir o MP4 (duração, áudio, cor bt709, quadros dos 3 modos; num quadro T comparar a pessoa com o bruto).

## Formatos (depois do OK do RL)
IN 1080x1350, GL 1080x1080 e YT 1920x1080 com os MESMOS trechos/legenda/sons. Geometria em `FMT` (`motor/Viral.tsx`):
D do IN = animação 0–702 + pessoa 1080x648; D do GL = 0–560 + pessoa 1080x520; D do YT = animação à esquerda 1170x1080 +
pessoa à direita 750x1080; legenda do T em y 1040 (IN) / 905 (GL) / 960 (YT). A animação usa a `camD` enquadrada
"contain" na banda. Pessoa por formato: `pessoa_formatos_animada3d.py <id>` (fonte 16:9) → no `Video.tsx`
`formatos: {...}` e o componente com prop `formato`; no `index.tsx`, composições `<id>-animada3d-IN|GL|YT`.
Fonte vertical ainda não tem recorte por formato (só RL).

## Regras
- Nada de QR, URL, link na bio ou Direct na tela; sem rótulo de capítulo. Texto só em placas curtas, em português.
- Texto e peça importante a ≥ 100 px das laterais em QUALQUER instante (cuidado com placa durante movimento de câmera).
- **Faixa do texto**: nunca lá em cima, nunca baixo demais, nunca na altura do rosto. RL: topo ≥ 320 px e base acima de
  ~1500; na D, entre y 320 e divY − 60 da faixa de cima. O motor confere toda carta `placa|...`.
- Imagem nunca parada > 4 s. Troca de tomada só em início/fim de frase. Nada na frente do rosto dos personagens.
- NÃO REPETIR: variar cenário, enquadramento e gesto.
- Não usar `@react-three/postprocessing` (`<EffectComposer>` sai vazio no Remotion); o compositor usa `postprocessing` direto.

## Limitações conhecidas
Personagens só têm frente, 3/4 e perfil andando, e um gesto (aceno): sem sentado, de costas ou segurando objeto. Poucos
cenários; objetos 3D simples. Melhorar é evolução do motor, não gambiarra na cena.

## Só animação (sem a pessoa)
`DadosViral.soAnimacao: true` (sem `trechos`, `pessoaCheio`, `pessoaDividido`) + `frases: [início, fim][]` da fala; o
motor confere as tomadas. `legendaEmA: true` (+ `legendaAY`) = legenda também na animação. Boneco com barba/careca:
`Outfit.beard`, `Outfit.brow`, `hat: "shaved"`.
