---
name: gerente-de-criativos
description: Instala, abre ou atualiza o Gerente de Criativos — um editor de vídeos curtos (Reels, Shorts, TikTok, anúncios) com um gerente que conversa com você e 15 subagentes (preparador, titulista, 8 editores de estilo, revisores de legenda e de imagem, entregador), menu com 11 estilos (inclusive YouTube dinâmico 16:9) e entrega nos formatos RL, IN, GL e YT. Baixa a pasta completa do GitHub e instala tudo (Python, ffmpeg, Node, Whisper, Remotion, HyperFrames) no Mac ou no Windows. Usar quando o usuário pedir "instala o gerente de criativos", "quero editar vídeo com o gerente", "atualiza o gerente de criativos" ou chamar esta skill.
---

# Gerente de Criativos — instalador

Esta skill só **instala e prepara** o Gerente de Criativos. O Gerente de verdade (o processo, os 15 subagentes, os
motores de cada estilo e as regras) mora numa **pasta de projeto** que esta skill baixa do GitHub. Ele só funciona
com o Claude Code aberto **nessa pasta**.

Regras: pedir OK ao usuário antes de instalar qualquer programa no computador e antes de downloads grandes; nunca
digitar a senha do computador ou do GitHub pelo usuário (ele digita quando o instalador pedir).

## 1. Onde fica

Pasta padrão: `~/gerente-de-criativos` (na pasta pessoal do usuário; **sem espaço no nome**, os scripts quebram com
espaço). Se o usuário preferir outro lugar, usar o que ele disser, desde que não tenha espaço no caminho.

- Se a pasta **já existe** e tem `CLAUDE.md` + `.claude/agents/`: é atualização → `git -C ~/gerente-de-criativos pull`
  e pular pro passo 3.
- Se existe e é outra coisa: perguntar outro nome.

## 2. Baixar

1. Conferir o git: `git --version`.
   - Mac sem git: `xcode-select --install` (abre uma janela do sistema; o usuário confirma) — ou `brew install git`
     se já tiver Homebrew.
   - Windows sem git: `winget install Git.Git` e abrir um terminal novo.
2. Clonar:
   ```bash
   git clone https://github.com/rafaelextremo/gerente-de-criativos.git ~/gerente-de-criativos
   ```
3. Se der erro de rede ou de acesso: conferir a internet e tentar de novo. O repositório é público, não precisa de
   login no GitHub.

## 3. Instalar as ferramentas

Ler `~/gerente-de-criativos/.claude/skills/instalar/SKILL.md` e seguir **todos** os passos dela, rodando os comandos
**de dentro da pasta** (`cd ~/gerente-de-criativos` antes de cada um, ou caminhos completos). Ela confere o que já
tem, instala o que falta (pedindo OK), cria o ambiente Python, baixa o modelo de transcrição, prepara o Remotion e o
HyperFrames e faz um vídeo de teste curto.

## 4. Abrir o Gerente

No fim, dizer ao usuário, em linguagem simples:

- **App do Claude:** abrir uma conversa nova do Claude Code escolhendo a pasta `gerente-de-criativos` (na pasta
  pessoal). **Terminal:** `cd ~/gerente-de-criativos && claude`.
- A partir daí ele conversa só com o Gerente nessa conversa: manda o vídeo, escolhe os estilos pelo número no menu,
  revisa em `Área de Trabalho/CRIATIVOS/PARA REVISAR/` e responde `#CR01 ok`, `#CR01: <ajuste>` ou `#CR01 descarta`.
- Na primeira conversa o Gerente pergunta o nome de quem aparece nos vídeos.

Se o usuário pedir pra editar um vídeo **nesta** conversa (fora da pasta), explicar que o Gerente só funciona com o
Claude Code aberto na pasta `gerente-de-criativos` e orientar a abrir lá.
