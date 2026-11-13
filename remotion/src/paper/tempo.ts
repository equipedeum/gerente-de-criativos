import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

// Tudo no estilo papel trabalha em SEGUNDOS ABSOLUTOS da composição (o mesmo relógio da transcrição cortada).
export const useT = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return {t: frame / fps, frame, fps};
};

export type Mola = {damping: number; stiffness: number; mass?: number};

export const MOLAS = {
  pop: {damping: 11, stiffness: 190, mass: 0.7}, // entra com um pouco de sobra (os recortes "pulam" na referência)
  suave: {damping: 18, stiffness: 140, mass: 0.9}, // deslizar / reposicionar
  queda: {damping: 9, stiffness: 150, mass: 0.8}, // etiqueta de seção caindo girada
  firme: {damping: 22, stiffness: 240, mass: 0.8}, // saída
};

// 0 antes de t0; depois sobe com a mola até ~1.
export const mola = (frame: number, fps: number, t0: number, cfg: Mola = MOLAS.pop) => {
  const f0 = Math.floor(t0 * fps);
  if (frame < f0) return 0;
  return spring({frame: frame - f0, fps, config: cfg});
};

// Rampa 0→1 entre t0 e t0+dur.
export const rampa = (t: number, t0: number, dur: number, ease: (x: number) => number = Easing.out(Easing.cubic)) =>
  interpolate(t, [t0, t0 + dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});

export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;

// Gerador pseudoaleatório determinístico (mesmo resultado em todo render).
export const rng = (seed: number) => {
  let s = seed | 0;
  return () => {
    s = (s + 0x6d2b79f5) | 0;
    let x = Math.imul(s ^ (s >>> 15), 1 | s);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
};

// Linha rasgada: pontos (x, y) de 0 a largura em torno de y0.
export const linhaRasgada = (largura: number, y0: number, seed: number, amp = 7, passoMin = 7, passoMax = 18) => {
  const r = rng(seed);
  const pts: [number, number][] = [[0, y0 + (r() - 0.5) * amp]];
  let x = 0;
  while (x < largura) {
    x = Math.min(largura, x + passoMin + r() * (passoMax - passoMin));
    const dente = r() < 0.12 ? (r() - 0.3) * amp * 2.2 : (r() - 0.5) * amp;
    pts.push([x, y0 + dente]);
  }
  return pts;
};

// clip-path de um cartão com a borda de baixo rasgada (px).
export const recorteRasgado = (w: number, h: number, seed: number, amp = 6) => {
  const pts = linhaRasgada(w, h - amp, seed, amp, 6, 14).reverse();
  return `polygon(0px 0px, ${w}px 0px, ${pts.map(([x, y]) => `${x.toFixed(1)}px ${y.toFixed(1)}px`).join(', ')})`;
};

// Largura de texto medida no próprio Chrome do render (fontes já carregadas pelo delayRender do Root).
let ctx: CanvasRenderingContext2D | null = null;
const cache = new Map<string, number>();
export const larguraTexto = (txt: string, fonte: string) => {
  const k = fonte + '|' + txt;
  const c = cache.get(k);
  if (c !== undefined) return c;
  if (!ctx) ctx = document.createElement('canvas').getContext('2d');
  if (!ctx) return txt.length * 50;
  ctx.font = fonte;
  const w = ctx.measureText(txt).width;
  cache.set(k, w);
  return w;
};
