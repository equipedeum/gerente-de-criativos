# Gerente de Criativos

Um editor de vídeos curtos (Reels, Shorts, TikTok, anúncios) que roda dentro do [Claude Code](https://claude.com/claude-code).
Você conversa com **um** assistente — o Gerente de Criativos — e ele distribui o trabalho pra uma equipe de subagentes:
preparador, titulista, um editor por estilo, revisores de legenda e de imagem e o entregador.

## Instalar (Mac ou Windows)

1. Instale o Claude Code (app ou terminal).
2. Crie uma pasta vazia **sem espaço no nome** (ex.: `~/Documents/gerente-de-criativos`) e abra o Claude Code nela.
3. Cole o link deste repositório e peça: **"clona esse repositório aqui e instala"**.

O Claude baixa o projeto, confere o que falta no computador e pede o seu OK antes de instalar cada programa (Homebrew,
Python 3.12, ffmpeg, Node.js) e antes dos downloads grandes (modelo de transcrição ~480 MB, pacotes ~300 MB). No fim
ele faz um vídeo de teste de poucos segundos. Tudo roda no seu computador.

## Usar

Mande o vídeo (arraste o arquivo pra conversa ou diga o caminho) e peça pra editar. O Gerente responde com o menu:

```
1) Simples com legenda simples
2) Simples com legenda simples + título
3) Simples com legenda animada
4) Simples com legenda animada + título
5) Hyperframe (tela dividida: pessoa embaixo, lettering e ícones em cima)
6) Paper (papel creme com recortes em cima, pessoa embaixo, legenda karaokê)
7) VOX (colagem documental estilo explainer)
8) Extremo (motion design de interface, escuro e laranja)
9) Edição animada (documentário ilustrado em tela cheia)
10) Animação viral (desenho 3D de bonequinho)
```

Responda com os números. Cada versão ganha um código (`#CR01`, `#CR02`…) e aparece primeiro só no formato vertical
(RL) em `Área de Trabalho/CRIATIVOS/PARA REVISAR/`. Aí você responde:

- `#CR01 ok` → ele faz os outros formatos (IN 1080x1350, GL 1080x1080, YT 1920x1080); com o segundo ok, vai pra `APROVADOS`;
- `#CR01: <o que mudar>` → ele corrige e entrega uma versão nova;
- `#CR01 descarta` → vai pra Lixeira.

## O que tem aqui

| pasta | |
|---|---|
| `CLAUDE.md` | quem é o Gerente e as regras de edição |
| `.claude/agents/` | os subagentes |
| `.claude/skills/` | o processo de cada estilo, a instalação e as skills do HyperFrames |
| `work/` | preparo, versão básica e fila (`work/pipeline/`) |
| `hyperframes/` | motores dos estilos em HyperFrames (Hyperframe, VOX, Extremo, Edição animada) e moldes em `exemplos/` |
| `remotion/` | Paper e Animação viral (Remotion) |
| `ferramentas/` | fontes livres (OFL) e ícones Phosphor (MIT) |
| `brutos/`, `saidas/`, `trilhas/`, `referencias/` | seus vídeos e entregas (nunca vão pro GitHub) |

Material de terceiros e licenças: `TERCEIROS.md`.
