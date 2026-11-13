---
name: shorts
description: "\"Shorts\": o usuário joga um vídeo vertical (Reel, story, gravação do celular) e recebe título de YouTube Shorts, descrição curta estilo rede social e tags baseadas em buscas reais (autocompletar do YouTube); corta o vídeo só se precisar. Usar quando ele mandar um .mp4 vertical solto pedindo título/descrição/tags, ou chamar de \"Shorts\"."
---

# Shorts

Entrega **título, descrição breve e tags**. Corte só se precisar; senão o vídeo fica como está.

## Fluxo
1. **Formato e duração** (`ffprobe`): vertical e **até 3:00** (limite dos Shorts). Passou disso, avisar e propor onde cortar.
2. **Transcrever**: `./py work/pipeline/preparar.py <id> "<arquivo>" --sem-corte --sem-tratar-audio` e ler
   `work/<id>/words_cut.json`. Corrigir na leitura o que o whisper erra (nomes, números).
3. **Olhar o vídeo**: folha de quadros (`ffmpeg -i <arq> -vf "fps=1/8,scale=240:-1,tile=7x3" folha.png`) + começo e fim.
   Números que aparecem na tela valem mais que os da transcrição.
4. **Corte**: `silencedetect=n=-38dB:d=0.4`. Cortar sozinho só ar morto no começo/fim (> ~0,5 s) ou tropeço óbvio; corte
   que mude o conteúdo, propor antes. Nunca mexer no original; saída em `saidas/<nome>-v1.mp4`.
5. **Tags com buscas reais** (autocompletar do YouTube pt-BR, sem login):
   ```bash
   ./py work/shorts_tags.py buscar "termo 1" "termo 2" ...
   ./py work/shorts_tags.py contar "tag 1, tag 2, ..."
   ```
   15 a 20 termos-semente do assunto. Usar só sugestões que aparecerem e combinarem com o vídeo; começar pelas mais
   específicas e terminar nas amplas + o nome da pessoa (`projeto.json`). Limite 500 caracteres (o `contar` confere).

## Entrega (no chat, em blocos de código)
- **Título**: 1 principal + 2 alternativas, até ~50 caracteres, gancho + palavra-chave. Sem travessão, sem clickbait.
- **Descrição**: 2 a 3 frases em primeira pessoa, só fatos da fala/tela, 3 hashtags no fim (link em descrição de Short
  não é clicável).
- **Tags**: uma linha, separadas por vírgula, sem hashtag.
- Uma linha dizendo se cortou ou não e por quê.
