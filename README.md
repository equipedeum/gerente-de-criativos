# Gerente de Criativos

![Prévia dos estilos do Gerente de Criativos](docs/previa.png)

Editor de vídeos (Reels, Shorts, TikTok, anúncios e vídeo de YouTube) que roda dentro do
[Claude Code](https://claude.com/claude-code). Você conversa com **um** assistente — o Gerente de Criativos — e ele
distribui o trabalho pra uma equipe de 15 subagentes: preparador, titulista, um editor por estilo, revisores de legenda e
de imagem e o entregador.

## Instalar: cole o link e peça pra instalar

1. Abra o **Claude Code** (a aba de código do app do Claude, ou `claude` no terminal) em qualquer pasta.
2. Cole esta mensagem:

   ```
   https://github.com/rafaelextremo/gerente-de-criativos
   Clona esse repositório na minha pasta pessoal e instala o gerente de criativos.
   ```

3. Responda às perguntas dele. O Claude baixa o projeto pra `~/gerente-de-criativos`, confere o que falta no computador e
   **pede o seu OK antes de instalar cada programa** (Homebrew, Python 3.12, ffmpeg, Node.js, Git) e antes dos downloads
   grandes (modelo de transcrição ~480 MB, pacotes do Remotion ~300 MB). Se o instalador pedir a senha do computador,
   quem digita é você. No fim ele faz um vídeo de teste de poucos segundos.
4. Abra uma **conversa nova** do Claude Code na pasta `gerente-de-criativos` (na sua pasta pessoal) e fale com o Gerente.
   Na primeira conversa ele pergunta o nome de quem aparece nos vídeos e a marca.

Funciona no Mac e no Windows. Tudo roda no seu computador (nada de vídeo vai pra nuvem). Se algo falhar no meio, peça:
**"confere a instalação e me diz o que está faltando"**.

Quem já usa o `npx` pode instalar só a skill instaladora e depois pedir **"instala o gerente de criativos"**:
```bash
npx skills add rafaelextremo/gerente-de-criativos --skill gerente-de-criativos -a claude-code -g
```

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
8) Tech (motion design de interface, escuro e laranja)
9) Edição animada (documentário ilustrado em tela cheia)
10) Animação viral (desenho 3D de bonequinho)
11) YouTube dinâmico (vídeo de canal 16:9: limpeza de tropeço, plano aberto/fechado, painel de texto, capítulos)
```

Responda com os números. Cada versão ganha um código (`#CR01`, `#CR02`…) e aparece primeiro só no formato vertical
(RL) em `Área de Trabalho/CRIATIVOS/PARA REVISAR/`. Aí você responde:

- `#CR01 ok` → ele faz os outros formatos (IN 1080x1350, GL 1080x1080, YT 1920x1080); com o segundo ok, vai pra `APROVADOS`;
- `#CR01: <o que mudar>` → ele corrige e entrega uma versão nova;
- `#CR01 descarta` → vai pra Lixeira.

O **YouTube dinâmico** (11) é pra gravação horizontal de fala (4K de preferência) e sai direto no formato do YouTube
(1920x1080); o primeiro ok já aprova. As cores, fontes e o logo dele vêm do `projeto.json` (`cor_destaque`, `cor_papel`,
`cor_tinta`, `logo`, `slogan`…).

## O que tem aqui

| pasta | |
|---|---|
| `CLAUDE.md` | quem é o Gerente e as regras de edição |
| `.claude/agents/` | os 15 subagentes |
| `skills/gerente-de-criativos/` | a skill instaladora (a que o `npx skills add` instala) |
| `.claude/skills/` | o processo de cada estilo, a instalação e as skills do HyperFrames |
| `work/` | preparo, versão básica, YouTube dinâmico (`work/yt/`) e fila (`work/pipeline/`) |
| `hyperframes/` | motores dos estilos em HyperFrames (Hyperframe, VOX, Tech, Edição animada) e moldes em `exemplos/` |
| `remotion/` | Paper, Animação viral e os grafismos do YouTube dinâmico (Remotion) |
| `ferramentas/` | fontes livres (OFL) e ícones Phosphor (MIT) |
| `brutos/`, `saidas/`, `trilhas/`, `referencias/` | seus vídeos e entregas (ficam só no seu computador) |
| `docs/` | imagens deste README |

Material de terceiros e licenças: `TERCEIROS.md`.
