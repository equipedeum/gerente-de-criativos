"""Gera as texturas do estilo papel (uma vez só), em remotion/public/paper/:
- papel.jpg: fundo creme "nublado" (manchas suaves, sem vinco marcado), 1080x1000, como nas referências de papel.
- kraft.jpg: papelão kraft granulado (preenchimento dos recortes marrons), 512x512, repete sem emenda visível.

    ./py remotion/scripts/papel.py
"""
from pathlib import Path

import cv2
import numpy as np

rng = np.random.default_rng(11)
SAIDA = Path(__file__).resolve().parents[1] / 'public' / 'paper'


def ruido(h, w, escala, oitavas=4, pers=0.5):
    tot = np.zeros((h, w), np.float32)
    amp, s = 1.0, escala
    for _ in range(oitavas):
        hh, ww = max(2, int(h / s)), max(2, int(w / s))
        n = rng.standard_normal((hh, ww)).astype(np.float32)
        tot += amp * cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
        amp *= pers
        s /= 2
    return (tot - tot.mean()) / tot.std()


def papel(W=1080, H=1000):
    nuvem = ruido(H, W, 340, 5, 0.55)            # manchas grandes, claras e escuras
    nuvem = np.tanh(nuvem * 1.1)
    amassado = ruido(H, W, 140, 3, 0.45)          # relevo suave do amassado
    gx = cv2.Sobel(cv2.GaussianBlur(amassado, (0, 0), 3), cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(cv2.GaussianBlur(amassado, (0, 0), 3), cv2.CV_32F, 0, 1, ksize=5)
    relevo = -(gx * -0.6 + gy * -0.8)
    relevo /= np.abs(relevo).std() * 3
    grao = ruido(H, W, 1.2, 2) * 0.6 + ruido(H, W, 3, 2) * 0.4
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((xx - W / 2) / (W * 0.6), (yy - H * 0.5) / (H * 0.62))
    vin = np.clip(r - 0.45, 0, 1) ** 1.5

    claro = np.array([241, 234, 219], np.float32)   # RGB
    escuro = np.array([222, 213, 197], np.float32)
    canto = np.array([208, 200, 189], np.float32)
    m = (nuvem * 0.5 + 0.5)[..., None]
    img = claro * m + escuro * (1 - m)
    img = img * (1 - vin[..., None]) + canto * vin[..., None]
    img += (relevo * 2.2)[..., None] + (grao * 3.0)[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)


def kraft(N=512):
    def tile(escala, oit):
        # ruído periódico: soma de cópias deslocadas não basta; gera em 2N e recorta o centro com mistura nas bordas
        n = ruido(N * 2, N * 2, escala, oit)
        a = n[:N, :N]; b = n[:N, N:]; c = n[N:, :N]; d = n[N:, N:]
        t = np.linspace(0, 1, N, dtype=np.float32)
        wx = 0.5 - 0.5 * np.cos(np.pi * 2 * t)  # 0 nas bordas, 1 no meio
        top = a * wx[None, :] + b * (1 - wx[None, :])
        bot = c * wx[None, :] + d * (1 - wx[None, :])
        return top * wx[:, None] + bot * (1 - wx[:, None])
    mancha = tile(140, 3)
    fibra = tile(2.0, 2)
    pontos = (rng.random((N, N)) > 0.985).astype(np.float32)
    pontos = cv2.GaussianBlur(pontos, (0, 0), 0.8) * 4
    claros = (rng.random((N, N)) > 0.992).astype(np.float32)
    claros = cv2.GaussianBlur(claros, (0, 0), 0.7) * 4
    base = np.array([198, 171, 128], np.float32)  # RGB kraft
    img = base[None, None, :] + (mancha * 6)[..., None] + (fibra * 9)[..., None] - (pontos * 40)[..., None] + (claros * 25)[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)


SAIDA.mkdir(parents=True, exist_ok=True)
cv2.imwrite(str(SAIDA / 'papel.jpg'), cv2.cvtColor(papel(), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
cv2.imwrite(str(SAIDA / 'kraft.jpg'), cv2.cvtColor(kraft(), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
old = SAIDA / 'vinco.png'
if old.exists():
    old.unlink()
print('ok', SAIDA)
