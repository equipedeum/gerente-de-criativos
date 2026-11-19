---
name: instalar
description: Instala e confere tudo o que o Gerente de Criativos precisa no computador (Mac ou Windows) — Homebrew/winget, Python 3.12, ffmpeg, Node.js, git, venv com os pacotes do requirements.txt, modelo de transcrição, Remotion e HyperFrames — e faz um teste curto de ponta a ponta. Usar na primeira vez nesta pasta (não existe ferramentas/venv), quando o usuário pedir "instala", "configura", "confere a instalação", ou quando algum comando falhar por falta de ferramenta.
---

# Instalar o Gerente de Criativos

Regra: **pedir OK ao usuário antes de instalar cada programa no sistema** (Homebrew, Python, ffmpeg, Node, git) e antes
de cada download grande (modelo de transcrição ~480 MB, pacotes do Node ~300 MB). Explicar em uma frase o que é e por
que precisa. Nunca digitar senha pelo usuário: se o instalador pedir a senha do computador, ele digita.

## 1. Conferir o que já tem
```bash
python3 work/pipeline/conferir_instalacao.py      # Mac
py work/pipeline/conferir_instalacao.py           # Windows (ou python)
```
Só usa a biblioteca padrão: roda mesmo sem o venv. Lista `[ok]` e `[FALTA]` com o comando de cada coisa.

## 2. Programas do sistema (só o que faltar)

**Mac** (Apple Silicon ou Intel):
1. Homebrew (se não tiver; o usuário digita a senha do Mac quando pedir):
   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
   e depois seguir as 2 linhas "Next steps" que ele imprime (põem o `brew` no PATH).
2. `brew install python@3.12 ffmpeg node git`
3. Chrome: se o `hyperframes doctor` pedir, `brew install --cask google-chrome`.

**Windows** (PowerShell): `winget install Python.Python.3.12 Gyan.FFmpeg OpenJS.NodeJS.LTS Git.Git` e abrir um terminal
novo. O Claude Code no Windows usa o Git Bash — o `./py` e os `.sh` rodam nele.

## 3. Projeto
```bash
python3.12 -m venv ferramentas/venv                # Windows: py -3.12 -m venv ferramentas/venv
./py -m pip install --upgrade pip
./py -m pip install -r requirements.txt
./py -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8', download_root='models')"
cd remotion && npm ci && cd ..
npx -y hyperframes@0.8.76 doctor                   # baixa o HyperFrames; mostra o que falta (Chrome, ffmpeg). Docker NÃO é necessário (ignorar o ✗ dele)
```
- `./py` acha o Python do venv no Mac (`ferramentas/venv/bin/python`) e no Windows (`ferramentas/venv/Scripts/python.exe`)
  e cria `ferramentas/ffmpeg_path.txt` com o ffmpeg do PATH na primeira vez.
- Se `pip install` falhar num pacote por versão (Python diferente do 3.12), instalar a versão mais nova dele
  (`./py -m pip install <pacote>`) e avisar no fim.
- Telemetria do HyperFrames sempre desligada (`DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1`; o `./py` já põe).

## 4. Emoji do título (opcional)
- **Mac**: nada a fazer — usa a Apple Color Emoji do próprio sistema.
- **Windows**: usa a Segoe UI Emoji. Se o usuário quiser outro visual, dá pra baixar PNGs livres (Twemoji, CC-BY 4.0,
  com atribuição em `TERCEIROS.md`) pra `ferramentas/emoji/<codepoint>.png` — pedir permissão antes do download.

## 5. Dados do projeto
Perguntar e gravar em `projeto.json`: `nome_pessoa` (quem aparece nos vídeos; vai na transcrição e nos textos),
`marca` (empresa/produto, se houver), `termos_transcricao` (nomes e palavras que o whisper costuma errar). `pasta_entrega`
(padrão `~/Desktop/CRIATIVOS/PARA REVISAR`) e `prefixo_codigo` (padrão `CR` → `#CR01`) só se o usuário quiser mudar.
Marca (opcional; usado no Paper e no YouTube dinâmico): `cor_destaque` (cor principal da marca, padrão verde `#059669`),
`cor_papel` e `cor_tinta` (fundo claro e texto dos painéis), `logo` e `logo_simbolo` (caminho de um SVG/PNG) e
`slogan` (frase do cartão final). Vazio = padrão.

## 6. Teste de ponta a ponta
```bash
./py work/pipeline/conferir_instalacao.py --teste
```
Gera uma voz sintética (`say` no Mac, voz Maria no Windows), um vídeo de cores com ela, roda o preparo (corte +
transcrição + rosto) e renderiza um básico RL de ~6 s em `saidas/basico/Teste de instalacao/`. Abrir o MP4 e conferir que
tem a legenda e o som. Depois mandar os arquivos de teste pra Lixeira (`work/teste-instalacao`,
`work/basico/cfg/teste-instalacao.py`, a pasta da saída).

Teste opcional do HyperFrames e do Remotion (quando o usuário tiver um vídeo de verdade): seguir o fluxo normal do
Gerente com um estilo de cada motor.

## Problemas conhecidos
- **Vídeo HDR do iPhone**: o preparo converte pra SDR se o ffmpeg tiver `zscale` (o do Homebrew tem). Sem ele, a cor
  pode sair lavada: desligar "Vídeo HDR" na câmera do iPhone (Ajustes > Câmera > Gravar Vídeo).
- **Remotion no Mac**: o render da Animação viral usa `--gl=angle`; se der erro de WebGL, `GL_REMOTION=swangle`.
- **Pastas com espaço no caminho** quebram os scripts `.sh`: o projeto deve ficar num caminho sem espaço.
