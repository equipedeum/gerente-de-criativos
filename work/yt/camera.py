"""YouTube dinâmico (menu 11): a "câmera" (planos, punch-in, deslize junto com o painel) feita direto da gravação em YUV,
SEM passar por RGB: a cor da pessoa sai idêntica à do bruto (só reamostragem). Os grafismos vêm do Remotion como PNG
transparente e o ffmpeg sobrepõe em YUV (matriz bt709) + o mix.wav. Sai em bt709 marcado.

Por que não o Remotion inteiro: o OffthreadVideo lendo 4K é muito lento (5,5 min pra 5 s de vídeo) e o MP4 saía com a
cor codificada em BT.601 mas marcada bt709 (rosto mais vermelho). Aqui o vídeo nunca vira RGB.

  ./py work/yt/camera.py <id> final  <saida.mp4> <pasta_png_grafismos>
  ./py work/yt/camera.py <id> trecho <a> <b> <saida.mp4> <pasta_png_grafismos>   (quadros a..b, no máximo ~10 s)
  ./py work/yt/camera.py <id> folha  <pasta_png_folha> <saida_prefixo> [folha|trans]
  ./py work/yt/camera.py <id> still  <quadro> <png_grafismo> <saida.png>         (foto de 1 quadro, sem render)
O enquadramento usa a mesma matemática de remotion/src/yt-dinamico (painel 640 px, easings iguais).
"""
import glob, json, os, re, subprocess, sys
import av, cv2, numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "work"))
import sistema  # noqa: E402

FF = sistema.FF
W, H, PAINEL_W = 1920, 1080, 640


class Bezier:   # mesmo algoritmo do Easing.bezier do Remotion (bezier-easing)
    def __init__(s, x1, y1, x2, y2): s.p = (x1, y1, x2, y2)
    @staticmethod
    def _a(a1, a2): return 1.0 - 3.0 * a2 + 3.0 * a1
    @staticmethod
    def _b(a1, a2): return 3.0 * a2 - 6.0 * a1
    @staticmethod
    def _c(a1): return 3.0 * a1
    def _calc(s, t, a1, a2): return ((s._a(a1, a2) * t + s._b(a1, a2)) * t + s._c(a1)) * t
    def _slope(s, t, a1, a2): return 3.0 * s._a(a1, a2) * t * t + 2.0 * s._b(a1, a2) * t + s._c(a1)
    def __call__(s, x):
        x1, y1, x2, y2 = s.p
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        t = x
        for _ in range(8):
            d = s._calc(t, x1, x2) - x; sl = s._slope(t, x1, x2)
            if abs(d) < 1e-7 or abs(sl) < 1e-6: break
            t -= d / sl
        if not (0 <= t <= 1) or abs(s._calc(t, x1, x2) - x) > 1e-5:   # subdivisão
            a, b = 0.0, 1.0; t = x
            for _ in range(40):
                v = s._calc(t, x1, x2)
                if abs(v - x) < 1e-7: break
                if v > x: b = t
                else: a = t
                t = (a + b) / 2
        return s._calc(t, y1, y2)


easeOut = Bezier(0.2, 0.8, 0.2, 1); easeInOut = Bezier(0.65, 0, 0.35, 1)
c01 = lambda x: max(0.0, min(1.0, x))


def _hex(c):
    c = c.lstrip("#"); return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


class Camera:
    def __init__(s, id_):
        s.id = id_
        s.pub = f"remotion/public-yt/{id_}"
        s.e = json.load(open(f"{s.pub}/edl.json", encoding="utf-8"))
        s.base = f"work/{id_}/base_h.mov"
        c = av.open(s.base); v = c.streams.video[0]; s.SW, s.SH = v.width, v.height; c.close()
        s.esc0 = max(W / s.SW, H / s.SH)   # escala do plano aberto (z = 1): a gravação cobre o quadro 1920x1080
        # papel da marca em YUV bt709 (tv) pra área fora do vídeo (sempre embaixo do painel/cartão)
        r, g, b = _hex(s.e["marca"]["papel"])
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        s.papel = (16 + 219 * y, 128 + 224 * (b - y) / 1.8556, 128 + 224 * (r - y) / 1.5748)

    def desloc(s, f):
        p = 0.0
        for pn in s.e["paineis"]:
            fim = pn["o1"] + (40 if pn["ate_capitulo"] else 0)
            if f < pn["o0"] or f >= fim: continue
            ent = easeOut(min(1.0, (f - pn["o0"]) / 10))
            sai = 1.0 if pn["ate_capitulo"] else 1 - easeInOut(c01((f - (pn["o1"] - 9)) / 9))
            p = max(p, min(ent, sai))
        return p

    def plano(s, f):
        ps = s.e["planos"]
        for pl in reversed(ps):
            if f >= pl["o0"]: return pl
        return ps[0]

    def enquadra(s, f):
        pl = s.plano(f); dur = max(1, pl["o1"] - pl["o0"] - 1)
        z = pl["z0"] + (pl["z1"] - pl["z0"]) * easeInOut(c01((f - pl["o0"]) / dur))
        sc = s.esc0 * z; p = s.desloc(f)
        tx = W / 2 + (PAINEL_W / 2) * p - pl["fx"] * sc      # rosto no centro (ou no centro da área livre com painel)
        tx = min(PAINEL_W * p, max(W - s.SW * sc, tx))       # nunca mostra a borda da gravação
        return sc, tx

    def fonte(s, f):
        for sg in s.e["segs"]:
            if sg["o0"] <= f < sg["o1"]: return sg["f0"] + f - sg["o0"]
        return None

    def compoe(s, planos_yuv, f):
        """planos_yuv = (Y, U, V) da gravação (yuv420p) -> (Y, U, V) 1920x1080. Zoom ancorado no topo (a cabeça desce)."""
        sc, tx = s.enquadra(f)
        out = []
        for i, pl in enumerate(planos_yuv):
            k = 1 if i == 0 else 0.5            # croma tem metade da resolução
            ow, oh = int(W * k), int(H * k)
            t = tx * k
            x0 = max(0, int(np.floor(-t / sc)) - 6); x1 = min(pl.shape[1], int(np.ceil((ow - t) / sc)) + 6)
            y1 = min(pl.shape[0], int(np.ceil(oh / sc)) + 6)
            crop = pl[0:y1, x0:x1]
            sig = 0.5 * np.sqrt(max(0.0, 1 / sc ** 2 - 1))        # anti-serrilhado da redução
            if sig > 0.2: crop = cv2.GaussianBlur(crop, (0, 0), sig)
            M = np.float32([[sc, 0, t + sc * x0 + 0.5 * sc - 0.5], [0, sc, 0.5 * sc - 0.5]])   # centro de pixel CSS -> OpenCV
            out.append(cv2.warpAffine(crop, M, (ow, oh), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=float(s.papel[i])))
        return out

    def vazio(s):
        return [np.full((H, W), s.papel[0], np.uint8), np.full((H // 2, W // 2), s.papel[1], np.uint8), np.full((H // 2, W // 2), s.papel[2], np.uint8)]

    def quadros(s, a, b):
        """gera (f, Y, U, V) de a até b-1 lendo a gravação em ordem (pulando o que foi cortado)."""
        c = av.open(s.base); vs = c.streams.video[0]; vs.thread_type = "AUTO"
        tb = vs.time_base; fr = vs.average_rate
        SW, SH = s.SW, s.SH
        precisa = [(f, s.fonte(f)) for f in range(a, b)]
        ultimo = None; cache = None; gen = None; idx = -1

        def abre(n):
            nonlocal gen, idx
            c.seek(int(max(0, (n - 2) / fr / tb)), stream=vs, backward=True, any_frame=False)
            gen = c.decode(vs); idx = -1

        def pega(n):
            nonlocal idx, cache
            if gen is None or n < idx or n - idx > 45: abre(n)
            while idx < n:
                fr_ = next(gen)
                idx = int(round(fr_.pts * tb * fr))
                if idx >= n:
                    arr = fr_.to_ndarray(format="yuv420p")
                    cache = (arr[:SH], arr[SH:SH + SH // 4].reshape(SH // 2, SW // 2), arr[SH + SH // 4:].reshape(SH // 2, SW // 2))
            return cache

        for f, n in precisa:
            if n is None: yield (f, *s.vazio()); continue
            if ultimo is not None and n <= ultimo: yuv = cache        # pad (repete, fica embaixo do cartão)
            else: yuv = pega(n); ultimo = n
            yield (f, *s.compoe(yuv, f))
        c.close()


def pngs(pasta):
    """{quadro: arquivo} das PNG do Remotion (o nome traz o número do quadro)."""
    fs = {int(re.findall(r"(\d+)", os.path.basename(f))[-1]): f for f in glob.glob(os.path.join(pasta, "*.png"))}
    assert fs, f"sem PNG em {pasta}"
    return fs


def encoda(cam, a, b, saida, graf, com_audio=True):
    """câmera (pipe yuv420p) + grafismos PNG (overlay em YUV, matriz bt709) + mix.wav -> MP4 bt709 tv"""
    fs = pngs(graf); k0 = min(fs)            # render parcial do Remotion numera a partir do 1º quadro pedido
    fq = cam.e["fps_q"]; num, den = (int(x) for x in fq.split("/"))
    lista = os.path.join(graf, "_lista.txt")
    with open(lista, "w", encoding="utf-8") as L:
        for f in range(a, b):
            p = fs.get(f, fs.get(f - a + k0))
            L.write(f"file '{os.path.abspath(p).replace(chr(92), '/')}'\nduration {den / num:.9f}\n")
    cmd = [FF, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{W}x{H}", "-r", fq, "-i", "-",
           "-f", "concat", "-safe", "0", "-i", lista]
    if com_audio: cmd += ["-ss", f"{a * den / num:.6f}", "-t", f"{(b - a) * den / num:.6f}", "-i", f"{cam.pub}/mix.wav"]
    cmd += ["-filter_complex",
            f"[1:v]fps={fq},scale={W}:{H}:out_color_matrix=bt709:out_range=tv,format=yuva420p[g];"
            "[0:v]setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv[c];"
            "[c][g]overlay=format=yuv420:eof_action=pass,format=yuv420p[v]",
            "-map", "[v]"]
    if com_audio: cmd += ["-map", "2:a", "-c:a", "aac", "-b:a", "320k"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
            "-frames:v", str(b - a), "-movflags", "+faststart", saida]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = 0
    for f, Y, U, V in cam.quadros(a, b):
        p.stdin.write(Y.tobytes()); p.stdin.write(U.tobytes()); p.stdin.write(V.tobytes()); n += 1
        if n % 300 == 0: print(f"  {n}/{b - a}", flush=True)
    p.stdin.close(); p.wait()
    assert p.returncode == 0, "ffmpeg falhou"


def para_rgb(Y, U, V):
    """YUV 420 (bt709, tv) -> imagem RGB, só pra folha/foto de revisão (o vídeo final nunca passa por aqui)."""
    from PIL import Image
    Uu = cv2.resize(U, (W, H), interpolation=cv2.INTER_LINEAR); Vu = cv2.resize(V, (W, H), interpolation=cv2.INTER_LINEAR)
    yf = (Y.astype(np.float32) - 16) * (255 / 219); uf = (Uu.astype(np.float32) - 128) * (255 / 224); vf = (Vu.astype(np.float32) - 128) * (255 / 224)
    rgb = np.stack([yf + 1.5748 * vf, yf - 0.1873 * uf - 0.4681 * vf, yf + 1.8556 * uf], -1).clip(0, 255).astype(np.uint8)
    return Image.fromarray(rgb).convert("RGBA")


def quadro_rgb(cam, t):
    it = cam.quadros(t, t + 1); _, Y, U, V = next(it); it.close()
    return para_rgb(Y, U, V)


def folha(cam, graf, prefixo, tipo):
    """folha de revisão 3x3 por página: câmera (da gravação) + PNG transparente do Remotion."""
    from PIL import Image, ImageDraw, ImageFont
    tempos = cam.e[tipo]; fs = pngs(graf); assert len(fs) >= len(tempos), (len(fs), len(tempos))
    chaves = sorted(fs)
    fonte = ImageFont.truetype("ferramentas/fontes/Inter-Regular.ttf", 22)
    quadros = []
    for i, t in enumerate(tempos):
        base = quadro_rgb(cam, t)
        base.alpha_composite(Image.open(fs[chaves[i]]).convert("RGBA"))
        tile = base.convert("RGB").resize((640, 360), Image.LANCZOS)
        d = ImageDraw.Draw(tile)
        tt = t / cam.e["fps"]; txt = f"{int(tt // 60)}:{tt % 60:04.1f}  q{t}"
        d.rectangle([6, 360 - 34, 14 + d.textlength(txt, font=fonte), 360 - 6], fill=(245, 239, 228)); d.text((10, 360 - 33), txt, fill=(28, 26, 23), font=fonte)
        quadros.append(tile)
    saidas = []
    for pg in range(0, len(quadros), 9):
        fl = Image.new("RGB", (1920, 1080), (28, 26, 23))
        for j, q in enumerate(quadros[pg:pg + 9]): fl.paste(q, ((j % 3) * 640, (j // 3) * 360))
        nome = f"{prefixo}-{pg // 9 + 1:02d}.png"; fl.save(nome); saidas.append(nome)
    print("\n".join(saidas))


def still(cam, t, png, saida):
    from PIL import Image
    base = quadro_rgb(cam, t)
    base.alpha_composite(Image.open(png).convert("RGBA"))
    base.convert("RGB").save(saida); print(saida)


if __name__ == "__main__":
    id_, modo = sys.argv[1], sys.argv[2]
    cam = Camera(id_)
    if modo == "final":
        encoda(cam, 0, cam.e["frames"], sys.argv[3], sys.argv[4])
    elif modo == "trecho":
        a, b = int(sys.argv[3]), int(sys.argv[4]); assert b - a <= int(10.1 * cam.e["fps"]), "trecho de no máximo 10 s"
        encoda(cam, a, b, sys.argv[5], sys.argv[6])
    elif modo == "folha":
        folha(cam, sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "folha")
    elif modo == "still":
        still(cam, int(sys.argv[3]), sys.argv[4], sys.argv[5])
