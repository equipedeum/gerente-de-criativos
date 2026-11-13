"""Kit de efeitos sonoros do estilo papel -> remotion/public/sfx/*.wav (48 kHz mono, pico -3 dBFS, sem cauda muda).

    ./py remotion/scripts/sfx.py

- Da biblioteca da skill media-use (Pixabay Content License: uso comercial sem atribuição; créditos em
  .claude/skills/media-use/audio/assets/sfx/CREDITS.md): pop, clique, whoosh, ping.
- Sintetizados aqui (combinam com papel): papel (folha deslizando, troca de seção), carimbo (batida seca),
  tesoura (dois cortes metálicos), tique (✓ marcando).
O volume final é decidido no vídeo (`sfx` do VideoPapel, ganho baixo — a voz é o principal).
"""
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 48000
RAIZ = Path(__file__).resolve().parents[2]
LIB = RAIZ / '.claude/skills/media-use/audio/assets/sfx'
SAIDA = RAIZ / 'remotion/public/sfx'
rng = np.random.default_rng(3)


def grava(nome, x):
    x = np.asarray(x, np.float64)
    # tira a cauda abaixo de -60 dB do pico e normaliza o pico em -3 dBFS
    pk = np.max(np.abs(x)) or 1.0
    vivo = np.where(np.abs(x) > pk * 10 ** (-60 / 20))[0]
    if len(vivo):
        x = x[: vivo[-1] + int(0.02 * SR)]
    x = x / pk * 10 ** (-3 / 20)
    fade = min(len(x), int(0.01 * SR))
    x[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(SAIDA / f'{nome}.wav'), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f'{nome}.wav  {len(x) / SR:.2f} s')


def da_biblioteca(nome, arquivo):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(LIB / arquivo), '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    grava(nome, np.frombuffer(pcm, np.int16) / 32768.0)


def filtra(x, lo, hi):
    """Passa-faixa por FFT (suave)."""
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X = np.fft.rfft(x)
    g = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * g, len(x))


def env(n, ataque, queda):
    t = np.arange(n) / SR
    return np.minimum(1, t / ataque) * np.exp(-np.maximum(0, t - ataque) / queda)


def papel():
    n = int(0.42 * SR)
    ruido = rng.standard_normal(n)
    # varredura: o "sss" de papel sobe e desce de brilho
    a = filtra(ruido, 900, 5500) * env(n, 0.06, 0.12)
    b = filtra(rng.standard_normal(n), 2500, 9000) * env(n, 0.02, 0.05) * 0.5
    grao = (rng.random(n) > 0.997) * rng.standard_normal(n) * 1.5  # estalinhos da fibra
    grao = filtra(grao, 1500, 8000) * env(n, 0.05, 0.15)
    return a + b + grao * 0.6


def carimbo():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    corpo = np.sin(2 * np.pi * (95 * t + 120 * (1 - np.exp(-t * 40)) / 40)) * np.exp(-t / 0.07)
    tapa = filtra(rng.standard_normal(n), 400, 4000) * env(n, 0.001, 0.018)
    return corpo * 0.9 + tapa * 0.8


def tesoura():
    n = int(0.32 * SR)
    x = np.zeros(n)
    for ini, amp in [(0.0, 1.0), (0.11, 0.8)]:
        k = int(ini * SR)
        m = n - k
        corte = filtra(rng.standard_normal(m), 3000, 12000) * env(m, 0.002, 0.025)
        tom = np.sin(2 * np.pi * 4200 * np.arange(m) / SR) * env(m, 0.001, 0.03) * 0.25
        x[k:] += (corte + tom) * amp
    return x


def tique():
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1850 * t) * env(n, 0.001, 0.035) + filtra(rng.standard_normal(n), 2000, 7000) * env(n, 0.001, 0.006) * 0.4


SAIDA.mkdir(parents=True, exist_ok=True)
da_biblioteca('pop', 'pop.mp3')
da_biblioteca('clique', 'click-soft.mp3')
da_biblioteca('whoosh', 'whoosh-short.mp3')
da_biblioteca('ping', 'ping.mp3')
grava('papel', papel())
grava('carimbo', carimbo())
grava('tesoura', tesoura())
grava('tique', tique())
