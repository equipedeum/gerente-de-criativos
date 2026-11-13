# -*- coding: utf-8 -*-
"""Cor da pessoa nos vídeos que entram numa composição HyperFrames.

REGRA DO USUÁRIO (12/11/2026, caso real "cor alterada" / caso real "cor da pessoa tá amarelada — não muda a cor dele"),
vale pra sempre: a cor da pessoa NUNCA muda — nenhum filtro, grade, LUT, sépia, saturação, vinheta ou luz por cima
dele, e o MP4 final sai com a mesma cor do vídeo de origem.

Por que este módulo existe (medido em 12/11 com render de teste de 1 s, rosto/camiseta do g22):
- O render do HyperFrames 0.8.76 NÃO deixa o Chrome decodificar o <video>: ele extrai os quadros com o ffmpeg pra JPG
  (`--video-frame-format auto` = jpg) copiando o YUV como está, e todo decodificador de JPEG (o Chrome inclusive) lê
  YUV como BT.601. Os nossos recortes vêm do celular/estúdio em BT.709 → a pele perde vermelho e o laranja do fundo
  puxa pro amarelo: no caso real testa (247,176,144) -> (240,171,142), bochecha (218,148,115) -> (209,143,114),
  dif. média da pessoa (-6,9, -4,0, -1,4). A folha de revisão (snapshot) não mostra isso: o snapshot deixa o Chrome
  decodificar o vídeo (ele respeita a marca bt709), então a folha parecia certa e o MP4 saía amarelado.
- Correção: todo vídeo da pessoa de uma composição HF é gravado em matriz BT.601 (marca smpte170m, faixa tv,
  primárias/transferência bt709). As cores (RGB) são as MESMAS da fonte (conversão 709 -> 601 conferida: 0,1 nível);
  só muda a matriz do YUV — a extração JPG do render e o Chrome (que lê a marca) mostram igual à fonte.
  Medido depois: dif. média (-2,8, -0,3, -3,0), o mesmo viés que o HF põe em QUALQUER cor (amostras CSS: cinza 128 sai
  125/127/127 — arredondamento do ffmpeg 8 ao ler os quadros JPG do Chrome no encode, fora do nosso alcance).
- `--video-frame-format png` NÃO serve: sai pior (-9, -11, -13) e ocupa ~2,3 MB por quadro no cache do HF.

Uso nos geradores de recorte (pessoa_cheio.py, extremo.py, preparar.py):
    vf = f'...,scale=1080:1920:flags=lanczos' + cor_pessoa.vf(base)      # ',' + conversão (ou '' se já for 601)
    subprocess.run([FF, ..., '-vf', vf, ..., *cor_pessoa.ARGS, saida])  # marca smpte170m/bt709/bt709/tv
E antes de cada render/revisão (renderizar.py, revisar.py): `cor_pessoa.garantir(pasta / 'public')` converte os <video>
do index.html que ainda estão em BT.709 (projetos antigos); o arquivo antigo vai pra Lixeira.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FF = (RAIZ / 'ferramentas/ffmpeg_path.txt').read_text().strip()
FFPROBE = next((str(Path(FF).with_name(n)) for n in ('ffprobe.exe', 'ffprobe') if Path(FF).with_name(n).exists()), 'ffprobe')
MATRIZ_601 = ('smpte170m', 'bt470bg')
ARGS = ['-colorspace', 'smpte170m', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv']


def sonda(arq):
    """(matriz, faixa) do 1º vídeo do arquivo; '' quando não marcado."""
    out = subprocess.run([FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=color_space,color_range', '-of', 'json', str(arq)],
                         capture_output=True, text=True).stdout
    s = (json.loads(out or '{}').get('streams') or [{}])[0]
    m, r = s.get('color_space', ''), s.get('color_range', '')
    return ('' if m in ('unknown', 'reserved') else m), ('' if r == 'unknown' else r)


def vf(fonte):
    """Trecho de filtro (começa com ',') que leva o vídeo da fonte pra matriz BT.601 sem mudar a cor; '' se a fonte já
    é 601. Fonte sem marca = vídeo HD (celular/estúdio) = BT.709. A faixa de saída é sempre tv."""
    m, r = sonda(fonte)
    if m in MATRIZ_601:
        return '' if r != 'pc' else ',scale=in_range=pc:out_range=tv:flags=accurate_rnd+full_chroma_int'
    return (f",scale=in_color_matrix=bt709:out_color_matrix=bt601:in_range={'pc' if r == 'pc' else 'tv'}:out_range=tv"
            f":flags=accurate_rnd+full_chroma_int")


def ok(arq):
    return sonda(arq)[0] in MATRIZ_601


def lixeira(arq):
    """Manda um arquivo pra Lixeira (Mac e Windows; regra: nada é apagado de vez)."""
    sys.path.insert(0, str(RAIZ / 'work'))
    import sistema
    return sistema.lixeira(arq)


def converter(arq):
    """Regrava `arq` (mp4 da pessoa em BT.709) em BT.601 com a mesma cor; o original vai pra Lixeira."""
    arq = Path(arq)
    tmp = arq.with_name(arq.stem + '.601-tmp.mp4')
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(arq), '-vf', vf(arq)[1:], '-an', '-c:v', 'libx264', '-crf', '15',
                    '-preset', 'medium', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p', *ARGS,
                    '-movflags', '+faststart', str(tmp)], check=True)
    if not lixeira(arq):
        tmp.unlink()
        raise SystemExit(f'cor_pessoa: não consegui mandar {arq.name} pra Lixeira (aberto em outro programa?)')
    tmp.rename(arq)


def garantir(pub):
    """Antes do render/revisão: todo <video> local do index.html em BT.709 (ou sem marca) é convertido pra BT.601.
    Devolve a lista do que converteu."""
    import re
    pub = Path(pub)
    html = (pub / 'index.html').read_text(encoding='utf-8')
    feitos = []
    # filtro/mistura de cor no próprio vídeo da pessoa é proibido (a regra vale também pro CSS)
    for vid in re.findall(r'<video\b[^>]*\bid="([^"]+)"', html):
        for regra in re.findall(rf'#{re.escape(vid)}\b[^{{]*\{{([^}}]*)\}}', html):
            if re.search(r'(^|;)\s*(filter|mix-blend-mode)\s*:', regra):
                print(f'cor_pessoa: AVISO #{vid} tem filtro/mistura de cor no CSS ({regra.strip()[:80]}) — a cor da pessoa '
                      f'nunca muda (regra 12/11)')
    for src in dict.fromkeys(re.findall(r'<video\b[^>]*\bsrc="([^"]+)"', html)):
        arq = pub / src
        if arq.suffix.lower() != '.mp4' or not arq.exists() or ok(arq):
            continue
        print(f'cor_pessoa: {src} está em BT.709 — o render do HyperFrames ia mudar a cor da pessoa; convertendo pra BT.601 '
              f'(mesma cor, o antigo vai pra Lixeira)')
        converter(arq)
        feitos.append(src)
    return feitos


if __name__ == '__main__':
    # python hyperframes/cor_pessoa.py <pasta do projeto ou public>
    alvo = Path(sys.argv[1])
    print(garantir(alvo if alvo.name == 'public' else alvo / 'public') or 'nada a converter')
