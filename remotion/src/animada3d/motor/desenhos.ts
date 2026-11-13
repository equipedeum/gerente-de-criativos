// Desenhos 2D extras do estilo "Animada 3D" (NOSSOS, feitos com a caneta `Pen` do toon.ts da skill): o robô da IA,
// e os efeitos de negócio (X, check, balão, celular, calendário, folha, sino, placa com texto, gráfico, planta).
// Tudo no mesmo traço: preenchimento chapado + contorno ameixa grosso. Cada função diz o tamanho do canvas que espera.
import { Pen, INK, shade, mix } from "./toon";

type P2 = [number, number];
const rad = (d: number) => (d * Math.PI) / 180;
export const rr = (x0: number, y0: number, x1: number, y1: number, r: number, n = 8): P2[] => {
  const pts: P2[] = [];
  for (const [cx, cy, a] of [[x1 - r, y0 + r, -90], [x1 - r, y1 - r, 0], [x0 + r, y1 - r, 90], [x0 + r, y0 + r, 180]])
    for (let i = 0; i <= n; i++) pts.push([cx + r * Math.cos(rad(a + (90 * i) / n)), cy + r * Math.sin(rad(a + (90 * i) / n))]);
  return pts;
};
/** texto centrado em (x, y) com a fonte do projeto (TikTok Sans, carregada antes do primeiro quadro) */
export const texto = (p: Pen, s: string, x: number, y: number, px: number, cor = INK, peso = 800) => {
  const g = p.g;
  g.font = `${peso} ${px}px "TikTok Sans", "Helvetica Neue", Arial, sans-serif`;
  g.textAlign = "center"; g.textBaseline = "middle"; g.fillStyle = cor;
  g.fillText(s, x, y);
};

export type RoboOpts = {
  /** olhos: feliz (arcos), normal (pontos), uau (círculos grandes), foco (traços) */
  olho?: "feliz" | "normal" | "uau" | "foco";
  /** ângulo de cada braço em graus: 0 = caído, 90 = esticado pro lado, 160 = pra cima. [esquerdo da tela, direito] */
  bracos?: [number, number];
  /** 0..1: chama do propulsor (pulsa) */
  chama?: number;
  /** inclinação do corpo em graus */
  tilt?: number;
  /** 0..1 antena acesa */
  antena?: number;
};
/** Robô da IA, flutuando, num canvas 600 x 1000 (pés/chama terminam em ~y 950). Peito com o selo "IA". */
export const robo = (p: Pen, o: RoboOpts = {}) => {
  const { olho = "feliz", bracos = [20, 20], chama = 0.5, tilt = 0, antena = 1 } = o;
  const cx = 300, CASCO = "#eef2f6", SOMBRA = "#c3ccd8", VISOR = "#1f2b45", CIANO = "#7af0ff", LAR = "#ff9838";
  p.ol = 12;
  // chama do propulsor (não gira com o corpo)
  const fh = 70 + 50 * chama;
  p.poly([[cx - 44, 800], [cx + 44, 800], [cx + 14, 800 + fh], [cx, 800 + fh + 26], [cx - 14, 800 + fh]], "#ffb347", 8);
  p.poly([[cx - 22, 800], [cx + 22, 800], [cx, 800 + fh * 0.6]], "#fff3b0", 0);
  p.rot = tilt ? [rad(tilt), cx, 760] : null;
  // antena
  p.stroke([[cx, 250], [cx, 175]], 16);
  p.ell(cx, 158, 26, 26, antena > 0.5 ? LAR : "#b9836a", 10);
  // braços atrás do corpo
  const ombroY = 560;
  bracos.forEach((ang, i) => {
    const s = i ? 1 : -1, sx = cx + s * 118, a = rad(ang);
    const cot: P2 = [sx + s * Math.sin(a) * 95, ombroY + Math.cos(a) * 95];
    const a2 = a + rad(ang > 60 ? 18 : -10);
    const mao: P2 = [cot[0] + s * Math.sin(a2) * 90, cot[1] + Math.cos(a2) * 90];
    p.line([[sx, ombroY], cot, mao], SOMBRA, 26);
    p.ell(mao[0], mao[1], 30, 30, CASCO, 10);
  });
  // corpo (barril) + cintura do propulsor
  p.poly(rr(cx - 62, 740, cx + 62, 812, 20), "#8f9bb0", 10);
  const corpo = rr(cx - 130, 500, cx + 130, 760, 70);
  p.gradFill(corpo, CASCO, SOMBRA, rad(-120));
  p.poly(corpo, null, 12);
  // selo IA no peito
  p.ell(cx, 640, 62, 62, LAR, 10);
  texto(p, "IA", cx, 644, 70, "#ffffff", 800);
  // cabeça
  const cab = rr(cx - 150, 250, cx + 150, 480, 80);
  p.gradFill(cab, CASCO, SOMBRA, rad(-120));
  p.poly(cab, null, 12);
  for (const s of [-1, 1]) p.ell(cx + s * 158, 365, 22, 40, "#8f9bb0", 10);
  p.poly(rr(cx - 112, 300, cx + 112, 430, 52), VISOR, 8);
  for (const s of [-1, 1]) {
    const ex = cx + s * 50, ey = 365;
    if (olho === "feliz") p.arc(ex, ey + 14, 26, 24, 200, 340, 16, CIANO);
    else if (olho === "uau") { p.ell(ex, ey, 26, 26, CIANO, 0); p.ell(ex, ey, 10, 10, VISOR, 0); }
    else if (olho === "foco") p.stroke([[ex - 26, ey - s * 6], [ex + 26, ey + s * 6]], 16, CIANO);
    else p.ell(ex, ey, 17, 22, CIANO, 0);
  }
  p.rot = null;
};

/** X vermelho (canvas 300 x 300) */
export const xis = (p: Pen) => {
  for (const [a, b] of [[[50, 50], [250, 250]], [[250, 50], [50, 250]]] as [P2, P2][]) { p.stroke([a, b], 74, INK); p.stroke([a, b], 50, "#e23b3b"); }
};
/** selo verde com check (canvas 300 x 300) */
export const check = (p: Pen) => {
  p.ell(150, 150, 125, 125, "#35b56a", 14);
  p.stroke([[88, 156], [134, 200], [214, 108]], 34, "#ffffff");
};
/** balão de conversa (canvas 420 x 340). lado -1 = rabo pra esquerda. tipo: pontos (…), check, coracao */
export const balao = (p: Pen, cor: string, lado: number, tipo: "pontos" | "check" | "interrogacao") => {
  const corpo = rr(24, 24, 396, 250, 70);
  const tx = lado < 0 ? 110 : 310;
  p.poly([[tx - 40, 230], [tx + 40, 230], [tx + lado * 70, 322]], cor, 12);
  p.poly(corpo, cor, 12);
  p.poly([[tx - 32, 226], [tx + 32, 226], [tx + lado * 40, 270]], cor, 0);
  const claro = cor === "#ffffff";
  if (tipo === "pontos") for (const dx of [-80, 0, 80]) p.ell(210 + dx, 137, 24, 24, claro ? "#7b8494" : "#ffffff", 0);
  else if (tipo === "check") p.stroke([[130, 140], [190, 196], [296, 82]], 36, claro ? "#35b56a" : "#ffffff");
  else texto(p, "?", 210, 142, 170, claro ? "#7b8494" : "#ffffff");
};
/** celular na mão (canvas 240 x 400), tela acesa */
export const celular = (p: Pen, aceso = true) => {
  p.poly(rr(30, 20, 210, 380, 34), "#2a2f3d", 12);
  p.poly(rr(48, 50, 192, 340, 14), aceso ? "#dff5e6" : "#55607a", 0);
  if (aceso) { p.poly(rr(60, 70, 150, 120, 18), "#ffffff", 0); p.poly(rr(90, 140, 180, 190, 18), "#35b56a", 0); p.poly(rr(60, 210, 140, 260, 18), "#ffffff", 0); }
};
/** folha de calendário (canvas 300 x 340): topo vermelho, grade de dias; marcado = um dia circulado */
export const calendario = (p: Pen, marcado = false) => {
  p.poly(rr(20, 30, 280, 320, 24), "#fbf7ee", 12);
  p.clip(rr(20, 30, 280, 320, 24), () => p.poly([[0, 0], [300, 0], [300, 104], [0, 104]], "#e2453c", 0));
  p.stroke([[20, 104], [280, 104]], 10);
  for (const x of [90, 210]) { p.stroke([[x, 14], [x, 62]], 22, INK); p.stroke([[x, 14], [x, 62]], 10, "#d9dde0"); }
  for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) p.ell(68 + c * 55, 152 + r * 55, 13, 13, "#c8c2b4", 0);
  if (marcado) { p.ell(178, 207, 15, 15, "#e2453c", 0); p.arc(178, 207, 34, 34, 0, 360, 11, "#e2453c"); }
  p.poly(rr(20, 30, 280, 320, 24), null, 12);
};
/** folha de papel com linhas (canvas 240 x 300) */
export const folha = (p: Pen, carimbo = false) => {
  p.poly([[24, 20], [216, 20], [216, 280], [24, 280]], "#fdfbf5", 10);
  for (let i = 0; i < 5; i++) p.stroke([[52, 70 + i * 40], [i % 2 ? 160 : 188, 70 + i * 40]], 10, "#b9bfcc");
  if (carimbo) { p.ell(160, 226, 34, 34, null, 9); p.stroke([[142, 228], [156, 242], [180, 212]], 10, "#35b56a"); }
};
/** sino tocando (canvas 320 x 320); k = -1..1 balanço */
export const sino = (p: Pen, k: number) => {
  p.rot = [rad(22 * k), 160, 60];
  p.ell(160, 268, 26, 26, "#b8791f", 9);
  p.poly([[160, 50], [214, 80], [236, 190], [268, 244], [52, 244], [84, 190], [106, 80]], "#ffc93c", 12);
  p.ell(160, 46, 20, 20, "#ffc93c", 9);
  p.rot = null;
  for (const s of [-1, 1]) { p.arc(160 + s * 150, 130, 26, 60, s > 0 ? -60 : 120, s > 0 ? 60 : 240, 12); }
};
/** placa/etiqueta com texto (canvas 600 x 180), fundo creme ou colorido */
export const placa = (p: Pen, s: string, fundo = "#fbf4e4", cor = INK, px = 84) => {
  p.poly(rr(14, 14, 586, 166, 34), fundo, 12);
  texto(p, s, 300, 94, px, cor);
};
/** painel da campanha (canvas 800 x 560): linha de resultado subindo até k (0..1) */
export const painelCampanha = (p: Pen, k: number) => {
  p.poly(rr(16, 16, 784, 544, 30), "#fbf7ee", 14);
  for (let i = 1; i < 4; i++) p.stroke([[80, 80 + i * 110], [730, 80 + i * 110]], 5, "#d9d3c4");
  p.stroke([[80, 70], [80, 470], [730, 470]], 12);
  const pts: P2[] = [[100, 430], [200, 380], [290, 400], [390, 300], [480, 320], [580, 190], [700, 110]];
  const n = Math.max(2, Math.round(2 + k * (pts.length - 2)));
  const vis = pts.slice(0, n);
  p.stroke(vis, 34, INK); p.stroke(vis, 20, "#35b56a");
  const [ex, ey] = vis[vis.length - 1];
  p.ell(ex, ey, 24, 24, "#ffffff", 10);
  for (let i = 0; i < 3; i++) p.poly(rr(110 + i * 70, 500 - 0, 160 + i * 70, 520, 6), i === 0 ? "#3f6fb5" : "#c8c2b4", 0);
};
/** planta do projeto (canvas 800 x 560), azul: engrenagens ligadas a um robozinho, sem texto */
export const planta = (p: Pen) => {
  p.poly(rr(16, 16, 784, 544, 20), "#2f66b8", 14);
  const g = p.g; g.strokeStyle = "rgba(255,255,255,.22)"; g.lineWidth = 3;
  for (let x = 76; x < 784; x += 60) { g.beginPath(); g.moveTo(x, 22); g.lineTo(x, 538); g.stroke(); }
  for (let y = 76; y < 544; y += 60) { g.beginPath(); g.moveTo(22, y); g.lineTo(778, y); g.stroke(); }
  const W = "#ffffff";
  const eng = (cx: number, cy: number, r: number) => {
    for (let i = 0; i < 8; i++) { const a = rad(i * 45); p.stroke([[cx + r * Math.cos(a), cy + r * Math.sin(a)], [cx + (r + 22) * Math.cos(a), cy + (r + 22) * Math.sin(a)]], 20, W); }
    p.arc(cx, cy, r, r, 0, 360, 12, W); p.arc(cx, cy, r * 0.35, r * 0.35, 0, 360, 10, W);
  };
  eng(170, 170, 62); eng(170, 400, 48);
  p.stroke([[262, 170], [420, 170], [420, 250]], 10, W); p.stroke([[240, 400], [420, 400], [420, 330]], 10, W);
  p.stroke(rr(360, 250, 480, 330, 20).concat([[480, 270]]), 10, W);
  p.stroke([[480, 290], [560, 290]], 10, W);
  p.poly([[560, 262], [610, 290], [560, 318]], W, 0);
  p.stroke(rr(630, 220, 740, 300, 26).concat([[740, 246]]), 10, W);
  p.stroke(rr(646, 312, 724, 390, 20).concat([[724, 332]]), 10, W);
  p.stroke([[685, 220], [685, 190]], 10, W); p.ell(685, 180, 12, 12, W, 0);
  for (const s of [-1, 1]) p.ell(685 + s * 24, 260, 9, 11, W, 0);
};
/** lupa (canvas 300 x 300) */
export const lupa = (p: Pen) => {
  p.stroke([[196, 196], [270, 270]], 44, INK); p.stroke([[200, 200], [266, 266]], 24, "#b5653f");
  p.arc(126, 126, 96, 96, 0, 360, 34, INK); p.arc(126, 126, 96, 96, 0, 360, 14, "#e8ecf2");
  p.arc(126, 126, 62, 62, 200, 260, 12, "#ffffff");
};
/** moeda de frente (canvas 200 x 200) */
export const moeda2d = (p: Pen) => {
  p.ell(100, 100, 84, 84, "#ffc93c", 12);
  p.arc(100, 100, 58, 58, 0, 360, 9, "#d99a1c");
  p.stroke([[100, 66], [100, 134]], 14, "#d99a1c");
};
/** riscos de velocidade (canvas 400 x 300), horizontais */
export const riscos = (p: Pen, seed = 0) => {
  for (let i = 0; i < 5; i++) { const y = 40 + i * 55, x0 = 30 + ((i * 97 + seed * 53) % 120), x1 = 240 + ((i * 61 + seed * 31) % 130); p.stroke([[x0, y], [x1, y]], 14, "#ffffff"); }
};
/** estrelinha de brilho de 4 pontas (canvas 200 x 200) */
export const brilho = (p: Pen, cor = "#fff3b0") => {
  const c = 100, pts: P2[] = [];
  for (let k = 0; k < 8; k++) { const r = k % 2 ? 22 : 88, a = rad(k * 45 - 90); pts.push([c + r * Math.cos(a), c + r * Math.sin(a)]); }
  p.poly(pts, cor, 9);
};
/** seta gorda apontando pra baixo (canvas 300 x 400); pra cima = girar a carta */
export const seta = (p: Pen, cor: string) => {
  p.poly([[110, 24], [190, 24], [190, 230], [268, 230], [150, 376], [32, 230], [110, 230]], cor, 14);
};
/** mostrador de relógio (canvas 512 x 512), sem ponteiros */
export const mostrador = (g: CanvasRenderingContext2D) => {
  g.fillStyle = "#f7f1e1"; g.strokeStyle = "#241726"; g.lineWidth = 26;
  g.beginPath(); g.arc(256, 256, 232, 0, 7); g.fill(); g.stroke();
  g.lineCap = "round";
  for (let i = 0; i < 12; i++) { const a = (i * Math.PI) / 6; g.lineWidth = i % 3 ? 10 : 18; g.beginPath(); g.moveTo(256 + 170 * Math.cos(a), 256 + 170 * Math.sin(a)); g.lineTo(256 + 200 * Math.cos(a), 256 + 200 * Math.sin(a)); g.stroke(); }
};

// ---------------- escritório (12/11/2026, caso real c01; servem pra qualquer cena de escritório) ----------------
const cl01 = (x: number) => Math.max(0, Math.min(1, x));
export type TelaTipo = "texto" | "chat" | "grafico" | "lista" | "agenda";
/** tela de computador acesa (canvas 320 x 200), sem marca nem texto legível; k 0..1 = andamento:
 *  "texto" linhas sendo digitadas com o cursor · "chat" balões entrando (rola) · "grafico" barras crescendo e a linha
 *  subindo · "lista" tarefas ganhando check · "agenda" grade da semana enchendo de blocos coloridos. Vai numa carta com yaw na frente do monitor (carta não tem luz: tela acesa). */
export const telaPC = (p: Pen, tipo: TelaTipo, k: number) => {
  k = cl01(k);
  p.poly(rr(8, 8, 312, 192, 14), "#1c2333", 8);
  p.poly(rr(20, 20, 300, 40, 6), "#2f3b55", 0);
  ["#e2453c", "#f0b429", "#35b56a"].forEach((c, i) => p.ell(34 + i * 16, 30, 5, 5, c, 0));
  if (tipo === "texto") {
    p.poly(rr(44, 50, 276, 184, 6), "#fbf8f0", 0);
    const L = 6, tot = k * L;
    let cx = 64, cy = 68;
    for (let i = 0; i < L; i++) {
      const f = cl01(tot - i), y = 68 + i * 20;
      if (f <= 0) break;
      const w = (i % 3 === 2 ? 118 : 184) * f;
      p.stroke([[64, y], [64 + w, y]], 9, "#7b8494");
      cx = 64 + w + 9; cy = y;
    }
    p.stroke([[cx, cy - 9], [cx, cy + 9]], 5, "#3f6fb5");
  } else if (tipo === "chat") {
    const n = Math.floor(k * 7), ini = Math.max(0, n - 4);
    for (let i = ini; i < n; i++) {
      const y = 52 + (i - ini) * 34, dir = i % 2 === 1;
      p.poly(dir ? rr(136, y, 296, y + 26, 12) : rr(24, y, 196, y + 26, 12), dir ? "#35b56a" : "#ffffff", 0);
      p.stroke(dir ? [[150, y + 13], [250, y + 13]] : [[38, y + 13], [150, y + 13]], 6, dir ? "#d7f5e2" : "#b9bfcc");
    }
  } else if (tipo === "grafico") {
    p.stroke([[40, 54], [40, 176], [290, 176]], 6, "#8a93a8");
    const hs = [0.32, 0.5, 0.42, 0.7, 0.92];
    hs.forEach((h, i) => { const x = 60 + i * 46, hh = 112 * h * cl01(k * 1.4 - i * 0.08); if (hh > 2) p.poly(rr(x, 174 - hh, x + 30, 174, 4), i === 4 ? "#35b56a" : "#3f9be0", 0); });
    const pts: [number, number][] = [[60, 150], [106, 128], [152, 136], [198, 100], [244, 70], [290, 52]];
    const nv = Math.max(2, Math.round(2 + k * (pts.length - 2)));
    p.stroke(pts.slice(0, nv), 7, "#ffb36b");
    const [ex, ey] = pts[nv - 1];
    p.ell(ex, ey, 7, 7, "#ffffff", 0);
  } else if (tipo === "agenda") {
    const cores = ["#3f9be0", "#ffb36b", "#35b56a", "#c77dff"], n = Math.floor(k * 12.999);
    for (let c = 0; c < 5; c++) p.poly(rr(30 + c * 54, 50, 74 + c * 54, 62, 3), "#3b4a66", 0);
    for (let i = 0; i < 12; i++) {
      const c = (i * 3) % 5, r = Math.floor(i / 3) % 4, x = 30 + c * 54, y = 70 + r * 28;
      p.poly(rr(x, y, x + 44, y + 22, 5), i < n ? cores[i % 4] : "#2a3448", 0);
    }
  } else {
    const n = Math.floor(k * 4.999);
    for (let i = 0; i < 4; i++) {
      const y = 56 + i * 32;
      p.poly(rr(34, y, 58, y + 24, 5), i < n ? "#35b56a" : "#ffffff", 0);
      if (i < n) p.stroke([[39, y + 12], [45, y + 18], [53, y + 6]], 5, "#ffffff");
      p.stroke([[74, y + 12], [i % 2 ? 210 : 260, y + 12]], 8, i < n ? "#8a93a8" : "#d9dde6");
    }
  }
};
/** painel de parede (TV) com a porcentagem (canvas 800 x 440): "n0%" grande, 10 blocos (n acesos) e, com ia > 0, o selo
 *  laranja "COM IA" (ia 0..1 = pop). A chave da carta deve começar com "placa|" pro motor conferir a faixa do texto. */
export const painelPct = (p: Pen, n: number, ia: number) => {
  p.poly(rr(10, 10, 790, 430, 28), "#1f2633", 14);
  p.poly(rr(32, 32, 768, 408, 16), "#26364d", 0);
  texto(p, `${n * 10}%`, 400, 118, 176, n >= 8 ? "#7af0ff" : "#ffffff", 900);
  for (let i = 0; i < 10; i++) { const x = 66 + i * 68; p.poly(rr(x, 198, x + 56, 234, 9), i < n ? "#7af0ff" : "#3b4a5c", 6); }
  if (ia > 0) {
    const w = 236 * ia, h = 56 * ia;
    p.poly(rr(400 - w, 318 - h, 400 + w, 318 + h, Math.max(4, 48 * ia)), "#e8792c", 9);
    texto(p, "COM IA", 400, 322, 100 * ia, "#ffffff", 900);
  }
};
/** quadro de tarefas na parede (canvas 600 x 380): 3 colunas (a fazer / fazendo / feito, só por cor, sem texto) e 6
 *  bilhetes que andam, um de cada vez, da 1ª pra 3ª coluna conforme k (0..1); o que está andando dá um pulinho. */
export const quadroTarefas = (p: Pen, k: number) => {
  p.poly(rr(10, 10, 590, 370, 18), "#fbf8f0", 12);
  ["#e2453c", "#f0b429", "#35b56a"].forEach((c, i) => { const x = 30 + i * 186; p.poly(rr(x, 30, x + 168, 58, 8), c, 0); if (i) p.stroke([[x - 9, 30], [x - 9, 352]], 4, "#d9d3c4"); });
  const cor = ["#ffd84a", "#ff9bb3", "#8fd3ff", "#b6f0a0", "#ffd84a", "#ff9bb3"];
  const N = 6, pos = cl01(k) * N * 2;
  for (let j = 0; j < N; j++) {
    const xb = (c: number) => 48 + c * 186 + (j >= 3 ? 70 : 0);
    const a = cl01(pos - 2 * j), b = cl01(pos - 2 * j - 1), u = a < 1 ? a : b;
    const x = a < 1 ? xb(0) + (xb(1) - xb(0)) * a : xb(1) + (xb(2) - xb(1)) * b;
    const y = 76 + (j % 3) * 92 - (u > 0 && u < 1 ? 30 * Math.sin(Math.PI * u) : 0);
    p.poly(rr(x, y, x + 62, y + 62, 6), cor[j], 6);
  }
};
/** relógio de parede (canvas 240 x 240); m 0..1 = volta do ponteiro grande (o pequeno anda 1/12 disso) */
export const relogio = (p: Pen, m: number) => {
  p.ell(120, 120, 104, 104, "#fbf7ee", 12);
  for (let i = 0; i < 12; i++) { const a = rad(i * 30); p.stroke([[120 + 78 * Math.cos(a), 120 + 78 * Math.sin(a)], [120 + 90 * Math.cos(a), 120 + 90 * Math.sin(a)]], i % 3 ? 5 : 9); }
  const am = rad(m * 360 - 90), ah = rad((m / 12) * 360 + 60);
  p.stroke([[120, 120], [120 + 52 * Math.cos(ah), 120 + 52 * Math.sin(ah)]], 12);
  p.stroke([[120, 120], [120 + 76 * Math.cos(am), 120 + 76 * Math.sin(am)]], 8, "#e2453c");
  p.ell(120, 120, 10, 10, INK, 0);
};
export { shade, mix };

// ---------------- vídeos curtos / criativos (12/11/2026, piloto rf01; servem pra qualquer vídeo sobre conteúdo) ----------------
const CORES_VID = ["#3f6fb5", "#e2453c", "#35b56a", "#7b5ac9", "#e8792c", "#22a7b6"];
/** cartão de vídeo vertical (canvas 200 x 320): miniatura colorida com o botão de play; feio = torto e borrado (feito às pressas) */
export const cartaoVideo = (p: Pen, cor = 0, feio = false) => {
  const c = CORES_VID[cor % CORES_VID.length];
  p.poly(rr(14, 14, 186, 306, 18), feio ? mix(c, "#8a8a8a", 0.55) : c, 10);
  p.poly(rr(30, 40, 170, 200, 10), feio ? "#b9b4a8" : mix(c, "#ffffff", 0.35), 0);
  if (feio) { p.stroke([[40, 60], [160, 180]], 12, "#7b7468"); p.stroke([[150, 56], [52, 170]], 10, "#7b7468"); }
  else { p.ell(100, 120, 40, 40, "#ffffff", 8); p.poly([[88, 98], [122, 120], [88, 142]], c, 0); }
  p.stroke([[34, 236], [feio ? 120 : 150, 236]], 12, "#ffffff"); p.stroke([[34, 268], [110, 268]], 10, feio ? "#d0cbc0" : "rgba(255,255,255,0.7)");
};
/** celular grande em pé (canvas 420 x 760) mostrando o feed de vídeos curtos rolando (k = rolagem contínua, em telas);
 *  com `anuncio` > 0 entra por cima um vídeo de anúncio (selo laranja com o alto-falante, sem texto) */
export const celularFeed = (p: Pen, k: number, anuncio = 0) => {
  p.poly(rr(16, 16, 404, 744, 56), "#22262f", 14);
  const tela = rr(40, 64, 380, 700, 26);
  p.clip(tela, () => {
    p.poly([[0, 0], [420, 0], [420, 760], [0, 760]], "#111318", 0);
    const H = 636, off = (k % 1) * H, i0 = Math.floor(k);
    for (let j = -1; j < 2; j++) {
      const y0 = 64 + j * H - off, c = CORES_VID[(((i0 + j) % 6) + 6) % 6];
      p.poly([[40, y0], [380, y0], [380, y0 + H], [40, y0 + H]], mix(c, "#1a1d24", 0.15), 0);
      p.ell(210, y0 + 250, 92, 92, mix(c, "#ffffff", 0.3), 0);
      p.ell(150, y0 + 520, 34, 34, "#ffffff", 0); p.stroke([[198, y0 + 508], [330, y0 + 508]], 16, "#ffffff"); p.stroke([[198, y0 + 540], [290, y0 + 540]], 12, "rgba(255,255,255,0.7)");
      for (let q2 = 0; q2 < 3; q2++) p.ell(350, y0 + 330 + q2 * 70, 18, 18, "rgba(255,255,255,0.85)", 0);
    }
    if (anuncio > 0) {
      const y = 64 + 636 * (1 - Math.min(1, anuncio));
      p.poly([[40, y], [380, y], [380, y + 636], [40, y + 636]], "#ffcf3f", 0);
      p.poly(rr(90, y + 150, 330, y + 390, 30), "#e8792c", 10);
      p.poly([[150, y + 240], [190, y + 240], [240, y + 196], [240, y + 344], [190, y + 300], [150, y + 300]], "#ffffff", 0);
      for (let a = 0; a < 2; a++) p.arc(250, y + 270, 40 + 30 * a, 40 + 30 * a, -45, 45, 12, "#ffffff");
      p.poly(rr(80, y + 470, 340, y + 540, 34), "#e2453c", 8);
    }
  });
  p.poly(tela, null, 8);
  p.poly(rr(170, 34, 250, 48, 7), "#3b3f4a", 0);
};
/** folhinha de calendário com texto grande (canvas 300 x 340): mês ("JAN"), ano ("2024") ou dia */
export const folhinha = (p: Pen, txt: string, cor = "#e2453c") => {
  p.poly(rr(20, 30, 280, 320, 24), "#fbf7ee", 12);
  p.clip(rr(20, 30, 280, 320, 24), () => p.poly([[0, 0], [300, 0], [300, 118], [0, 118]], cor, 0));
  p.stroke([[20, 118], [280, 118]], 10);
  texto(p, txt, 150, 78, txt.length > 3 ? 58 : 66, "#ffffff", 900);
  for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) p.ell(68 + c * 55, 168 + r * 52, 13, 13, "#c8c2b4", 0);
  p.poly(rr(20, 30, 280, 320, 24), null, 12);
};
/** quadro branco de parede (canvas 800 x 500) com rabiscos de conta (k 0..1 = quanto já foi rabiscado), sem texto legível */
export const quadroBranco = (p: Pen, k = 0) => {
  p.poly(rr(10, 10, 790, 490, 16), "#c3ccd8", 12);
  p.poly(rr(34, 34, 766, 466, 8), "#fbfcfd", 0);
  const linhas: [number, number, number][] = [[90, 120, 330], [90, 210, 280], [90, 300, 360], [480, 380, 700]];
  linhas.forEach(([x, y, x2], i) => { const u = Math.max(0, Math.min(1, k * 4 - i)); if (u > 0) p.stroke([[x, y], [x + (x2 - x) * u, y + 6 * Math.sin(u * 9)]], 9, i === 3 ? "#35b56a" : "#3f6fb5"); });
  p.poly(rr(300, 470, 500, 490, 6), "#8f9bb0", 0);
};
/** lâmpada acesa (canvas 240 x 300): a ideia/dica */
export const lampada = (p: Pen) => {
  for (let i = 0; i < 7; i++) { const a = rad(195 + i * 25); p.stroke([[120 + 86 * Math.cos(a), 118 + 86 * Math.sin(a)], [120 + 112 * Math.cos(a), 118 + 112 * Math.sin(a)]], 12, "#ffd84a"); }
  p.ell(120, 120, 62, 62, "#fff3b0", 10);
  p.poly(rr(92, 174, 148, 228, 10), "#8f9bb0", 9);
  p.stroke([[96, 192], [144, 192]], 6); p.stroke([[96, 208], [144, 208]], 6);
};
