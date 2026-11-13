"""Kit de efeitos sonoros do Paper feito com o Earshot (MIT) -> remotion/public/sfx-earshot/*.wav (desde 08/11/2026).

    ferramentas/earshot-venv/bin/python remotion/scripts/sfx_earshot.py   (Windows: .../Scripts/python.exe; Earshot é opcional — o kit já vem pronto)

Pedido do usuário (08/11/2026): "se temos ele OK, use essa skill também com o paper". Mesmos nomes do kit antigo
(public/sfx/, scripts/sfx.py — fica como reserva), então o sfx_auto.py e o GANHO do PaperVideo não mudam.
Cada som: render do banco do Earshot (sem modelo, sem download) -> mono 48 kHz -> começa no ataque (o kit antigo tinha
até 0,32 s de silêncio antes do som) -> mesma loudness (LUFS em blocos de 0,1 s) do som antigo de mesmo nome, pico
máx. -1 dBFS -> 16 bits. O que o pico não deixou subir (whoosh, tesoura) vira um fator em
remotion/src/paper/sfx-earshot.json, que o PaperVideo multiplica no volume. Também gera remotion/out/comparacao-sons-paper.wav/.mp3 (cada som antigo, 0,5 s, o novo, 1 s).
O "papel" segue VETADO (12/10/2026) e não entra no kit novo.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pyloudnorm
import soundfile as sf

SR = 48000
RAIZ = Path(__file__).resolve().parents[2]
PY = Path(sys.executable)
ANTIGO = RAIZ / 'remotion/public/sfx'
SAIDA = RAIZ / 'remotion/public/sfx-earshot'
AJUSTE = RAIZ / 'remotion/src/paper/sfx-earshot.json'   # fator por som que o PaperVideo multiplica no kit novo
COMP = RAIZ / 'remotion/out/comparacao-sons-paper'

# som -> camadas (id do Earshot, início em s, ganho em dB, semente ou None = a take oficial)
KIT = {
    'pop': [('ui_pop/soft', 0.0, 0, None)],                                    # pop redondo e macio (550 Hz)
    'carimbo': [('knock/desk', 0.0, 0, None), ('pro_pop_in/deep', 0.0, -4, None)],  # batida na mesa + corpo grave
    'whoosh': [('swish/soft', 0.0, 0, None)],                                  # passada de ar suave (seta, X, desliza)
    'clique': [('fit/click/floss_lid', 0.0, 0, None)],                         # clique pequeno de plástico (gravação CC0)
    'tique': [('pro_tap/glass', 0.0, 0, None)],                                # toque de vidro curto (✓)
    'tesoura': [('shutter/quick', 0.0, 0, None), ('shutter/quick', 0.11, -2, 7)],  # dois "snips" mecânicos
    'ping': [('notify/mid_tine', 0.0, 0, None)],                               # ding redondo médio (destaque, ao vivo)
}

medidor = pyloudnorm.Meter(SR, block_size=0.1)


def lufs(x):
    return medidor.integrated_loudness(np.concatenate([x, np.zeros(SR)]))


def render(som, semente, tmp):
    p = Path(tmp) / f"{som.replace('/', '_')}_{semente}.wav"
    cmd = [str(PY), '-m', 'earshot', 'sfx', 'render', som, '-o', str(p)]
    if semente is not None:
        cmd += ['--seed', str(semente)]
    subprocess.run(cmd, check=True, capture_output=True)
    x, sr = sf.read(str(p), always_2d=True)
    assert sr == SR, sr
    return x.mean(1)


def apara(x):
    """Começa 2 ms antes do primeiro ponto acima de -50 dB do pico; tira a cauda abaixo de -60 dB; fade de 10 ms."""
    a = np.abs(x)
    pk = a.max() or 1.0
    viv = np.where(a > pk * 10 ** (-50 / 20))[0]
    x = x[max(0, viv[0] - int(0.002 * SR)):]
    viv = np.where(np.abs(x) > pk * 10 ** (-60 / 20))[0]
    x = x[: viv[-1] + int(0.02 * SR)].copy()
    f = min(len(x), int(0.01 * SR))
    x[-f:] *= np.linspace(1, 0, f)
    return x


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    COMP.parent.mkdir(parents=True, exist_ok=True)
    pares, ajuste = [], {}
    with tempfile.TemporaryDirectory() as tmp:
        for nome, camadas in KIT.items():
            n = max(int((ini + 2.0) * SR) for _, ini, _, _ in camadas)
            x = np.zeros(n)
            for som, ini, db, semente in camadas:
                y = apara(render(som, semente, tmp)) * 10 ** (db / 20)
                k = int(ini * SR)
                x[k:k + len(y)] += y
            x = apara(x)
            velho, _ = sf.read(str(ANTIGO / f'{nome}.wav'))
            alvo = lufs(velho)
            for _ in range(4):   # o portão de -70 LUFS muda a medida com o ganho: converge em 2-3 passos
                x *= 10 ** ((alvo - lufs(x)) / 20)
            pk = np.abs(x).max()
            if pk > 10 ** (-1 / 20):
                x *= 10 ** (-1 / 20) / pk
            sf.write(str(SAIDA / f'{nome}.wav'), x, SR, subtype='PCM_16')
            falta = alvo - lufs(x)   # o que o pico de -1 dBFS não deixou subir: o PaperVideo compensa (sfx-earshot.json)
            ajuste[nome] = round(10 ** (falta / 20), 3)
            print(f'{nome:8s} {len(x) / SR:.2f} s  {lufs(x):6.1f} LUFS (antigo {alvo:6.1f}, compensa x{ajuste[nome]})'
                  f'  pico {20 * np.log10(np.abs(x).max()):5.1f} dBFS  <- {" + ".join(c[0] for c in camadas)}')
            pares.append((velho, x * ajuste[nome]))   # na comparação, o novo já no nível em que vai tocar
    AJUSTE.write_text(json.dumps(ajuste, indent=1) + '\n', encoding='utf-8')
    # comparação: antigo, 0,5 s, novo, 1 s de pausa até o próximo par (na ordem do KIT); o par fica no mesmo ganho
    # relativo do vídeo e a faixa toda é normalizada pra pico de -1 dBFS
    meio, pausa = np.zeros(int(0.5 * SR)), np.zeros(SR)
    trilha = np.concatenate([np.concatenate([v, meio, nv, pausa]) for v, nv in pares])
    trilha *= 10 ** (-1 / 20) / np.abs(trilha).max()
    sf.write(str(COMP.with_suffix('.wav')), trilha, SR, subtype='PCM_16')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(COMP.with_suffix('.wav')), '-c:a', 'libmp3lame', '-b:a', '192k',
                    str(COMP.with_suffix('.mp3'))], check=True)
    print('comparação:', COMP.with_suffix('.mp3'), f'({len(trilha) / SR:.1f} s; ordem: {", ".join(KIT)})')


if __name__ == '__main__':
    main()
