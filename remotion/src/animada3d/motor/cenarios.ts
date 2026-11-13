// Cenários prontos do estilo "Animação viral" (12/11/2026, piloto só de animação). Peças de cenário reutilizáveis que
// antes ficavam dentro do cena.ts de cada vídeo: cada função só ACRESCENTA geometria num Batch (e objetos dinâmicos no
// `dyn`, quando pedidos), em qualquer posição do mundo. Nada aqui muda o comportamento dos vídeos antigos.
//   chao()        piso retangular com textura (madeira, carpete, pedra, concreto, grama)
//   sala()        cômodo em corte (sem teto, aberto na frente): parede do fundo, laterais curtas, rodapé, faixa
//   janela()      janela pintada na parede do fundo (céu lá fora)
//   mesaPC()      mesa de escritório com monitor (a TELA é carta: ver telaPC em desenhos.ts) e teclado; devolve onde
//                 fica quem trabalha e o monitor
//   estante()     estante de livros encostada na parede
//   pracinha()    praça de pedra com casas em volta, árvores, bancos e postes
//   festa()       festa de fim de ano: varais de bandeirinhas e de luzinhas acesas (bloom), palco baixo e mesas
import * as THREE from "three";
import { Batch, boxGeo, quad, V, lam, house, prop } from "./build";
import { ctex, planksHD, cobbleHD, grassHD } from "./paint";
import { tinta } from "./mundo";

const up = (x0: number, x1: number, z0: number, z1: number, y: number, tile: number) =>
  quad(V(x0, y, z1), V(x1, y, z1), V(x1, y, z0), V(x0, y, z0), (x1 - x0) / tile, (z1 - z0) / tile);

/** carpete de placas de 50 cm em dois tons (cor base) */
export const carpeteTex = (a = "#9aa6ba", b2 = "#a6b1c3") => ctex("carpete" + a + b2, 512, 512, (g, r) => {
  const n = 4, s = 512 / n;
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { g.fillStyle = (i + j) % 2 ? a : b2; g.fillRect(i * s, j * s, s, s); }
  for (let k = 0; k < 2600; k++) { g.fillStyle = r() < 0.5 ? "rgba(255,255,255,0.08)" : "rgba(40,50,70,0.08)"; g.fillRect(r() * 512, r() * 512, 2, 2); }
  g.fillStyle = "rgba(60,70,90,0.28)"; for (let i = 0; i <= n; i++) { g.fillRect(i * s - 1, 0, 2, 512); g.fillRect(0, i * s - 1, 512, 2); }
});
/** janela pintada (céu de dia com nuvens) */
export const janelaTex = () => ctex("janelaCen", 256, 320, (g) => {
  g.fillStyle = "#f4f1ea"; g.fillRect(0, 0, 256, 320);
  const gr = g.createLinearGradient(0, 18, 0, 302); gr.addColorStop(0, "#8fc6ef"); gr.addColorStop(1, "#d7eefb");
  g.fillStyle = gr; g.fillRect(18, 18, 220, 284);
  g.fillStyle = "rgba(255,255,255,0.92)"; g.beginPath(); g.ellipse(84, 92, 40, 15, 0, 0, 7); g.ellipse(112, 84, 28, 17, 0, 0, 7); g.ellipse(176, 210, 34, 12, 0, 0, 7); g.fill();
  g.fillStyle = "#f4f1ea"; g.fillRect(122, 18, 12, 284); g.fillRect(18, 152, 220, 12);
  g.strokeStyle = "#241726"; g.lineWidth = 8; g.strokeRect(4, 4, 248, 312); g.lineWidth = 5; g.strokeRect(18, 18, 220, 284);
});
const livrosTex = () => ctex("livrosCen", 512, 256, (g, r) => {
  g.fillStyle = "#6e4b33"; g.fillRect(0, 0, 512, 256);
  const cores = ["#3f6fb5", "#e2453c", "#35b56a", "#f0b429", "#7b5ac9", "#22a7b6", "#e8792c", "#8c3b4a", "#fbf4e4"];
  for (const y0 of [8, 136]) {
    let x = 10;
    while (x < 500) {
      const w = 14 + r() * 22, h = 70 + r() * 46;
      if (r() < 0.12) { x += w; continue; }
      g.fillStyle = cores[Math.floor(r() * cores.length)]; g.fillRect(x, y0 + 118 - h, w, h);
      g.strokeStyle = "#241726"; g.lineWidth = 3; g.strokeRect(x, y0 + 118 - h, w, h);
      x += w + 2;
    }
    g.fillStyle = "#8a5a34"; g.fillRect(0, y0 + 116, 512, 12);
  }
});

export type Piso = "madeira" | "carpete" | "pedra" | "grama" | { cor: string };
const pisoMat = (p: Piso) =>
  p === "madeira" ? lam("planksHD", () => ({ map: planksHD() })) :
  p === "carpete" ? lam("carpeteCen", () => ({ map: carpeteTex() })) :
  p === "pedra" ? lam("cobbleHD", () => ({ map: cobbleHD() })) :
  p === "grama" ? lam("grassHD", () => ({ map: grassHD() })) : tinta(p.cor);

/** piso retangular (x0..x1, z0..z1) em y */
export const chao = (b: Batch, x0: number, x1: number, z0: number, z1: number, piso: Piso, y = 0, tile = 2) => b.add(up(x0, x1, z0, z1, y, tile), pisoMat(piso));

/** cômodo em corte: parede do fundo em z = zb (de x0 a x1, altura h), laterais de `lat` m vindo pra frente, rodapé,
 *  faixa colorida no alto (opcional) e piso de zb até z1 */
export const sala = (b: Batch, o: { x0: number; x1: number; zb: number; z1: number; h: number; parede: string; faixa?: string; piso: Piso; lat?: number; rodape?: string }) => {
  const { x0, x1, zb, z1, h, parede, faixa, piso, lat = 3.2, rodape = "#8a5a34" } = o;
  b.add(up(x0, x1, zb, z1, 0.012, 2), pisoMat(piso));
  const pm = tinta(parede);
  b.add(boxGeo(V(x0 - 0.2, 0, zb - 0.2), V(x1 + 0.2, h, zb)), pm);
  for (const sx of [x0 - 0.2, x1]) b.add(boxGeo(V(sx, 0, zb), V(sx + 0.2, h, zb + lat)), pm);
  if (faixa) {
    b.add(boxGeo(V(x0 - 0.26, h - 0.36, zb - 0.26), V(x1 + 0.26, h + 0.08, zb + 0.04)), tinta(faixa));
    for (const sx of [x0 - 0.26, x1 - 0.06]) b.add(boxGeo(V(sx, h - 0.36, zb), V(sx + 0.32, h + 0.08, zb + lat + 0.06)), tinta(faixa));
  }
  b.add(boxGeo(V(x0, 0, zb), V(x1, 0.14, zb + 0.04)), tinta(rodape));
};
/** janela pintada na parede do fundo (centro x, base y0, largura w, altura h) */
export const janela = (b: Batch, zb: number, x: number, y0: number, w: number, h: number) =>
  b.add(quad(V(x - w / 2, y0, zb + 0.012), V(x + w / 2, y0, zb + 0.012), V(x + w / 2, y0 + h, zb + 0.012), V(x - w / 2, y0 + h, zb + 0.012)), lam("janelaCen", () => ({ map: janelaTex() })));
/** estante de livros encostada na parede do fundo (centro x, largura w, altura h) */
export const estante = (b: Batch, zb: number, x: number, w: number, h: number) => {
  b.add(boxGeo(V(x - w / 2, 0, zb), V(x + w / 2, h, zb + 0.36)), tinta("#8a5a34"));
  b.add(quad(V(x - w / 2 + 0.06, 0.12, zb + 0.37), V(x + w / 2 - 0.06, 0.12, zb + 0.37), V(x + w / 2 - 0.06, h - 0.08, zb + 0.37), V(x - w / 2 + 0.06, h - 0.08, zb + 0.37)), lam("livrosCen", () => ({ map: livrosTex() })));
};

export type Posto = { x: number; z: number; quem: [number, number]; mon: [number, number]; telaY: number };
/** mesa de escritório (tampo w x d a 0,72 m) com monitor; lado = de que lado da mesa fica quem trabalha (-1 esquerda,
 *  1 direita, 0 meio); o monitor fica do outro lado. A tela do monitor é uma carta (telaPC) em (mon, telaY). */
export const mesaPC = (b: Batch, x: number, z: number, o: { lado?: number; w?: number; d?: number; tampo?: string; monitor?: number; caneca?: string } = {}): Posto => {
  const { lado = -1, w = 1.3, d = 0.72, tampo = "#e8d2a6", monitor = 1, caneca } = o;
  const x0 = x - w / 2, x1 = x + w / 2, z0 = z - d / 2, z1 = z + d / 2;
  b.add(boxGeo(V(x0, 0.72, z0), V(x1, 0.77, z1), 0, true), tinta(tampo));
  for (const sx of [x0 + 0.04, x1 - 0.09]) for (const sz of [z0 + 0.04, z1 - 0.09]) b.add(boxGeo(V(sx, 0, sz), V(sx + 0.05, 0.72, sz + 0.05)), tinta("#55607a"));
  b.add(boxGeo(V(x0 + 0.09, 0.36, z1 - 0.1), V(x1 - 0.09, 0.72, z1 - 0.07)), tinta("#5d6b82"));
  const mx = lado === 0 ? x : x - lado * 0.3, mz = z - 0.14, k = monitor;
  b.add(boxGeo(V(mx - 0.15, 0.77, mz - 0.12), V(mx + 0.15, 0.795, mz + 0.06)), tinta("#3b3f4a"));
  b.add(boxGeo(V(mx - 0.035, 0.79, mz - 0.08), V(mx + 0.035, 0.98, mz - 0.04)), tinta("#3b3f4a"));
  b.add(boxGeo(V(mx - 0.37 * k, 0.95, mz - 0.04), V(mx + 0.37 * k, 0.95 + 0.46 * k, mz + 0.03)), tinta("#2a2f3d"));
  const qx = lado === 0 ? x : x + lado * 0.32;
  b.add(boxGeo(V(qx - 0.21, 0.77, z + 0.02), V(qx + 0.21, 0.79, z + 0.17)), tinta("#3b3f4a"));
  if (caneca) b.add(new THREE.CylinderGeometry(0.06, 0.055, 0.13, 14).translate(x1 - 0.18, 0.835, z + 0.12), tinta(caneca));
  return { x, z, quem: [qx, z0 - 0.22], mon: [mx, mz + 0.04], telaY: 0.95 + 0.23 * k };
};

/** praça de pedra (centro cx, cz; meia-largura hx, meia-profundidade hz) com casas atrás (fachada pra +z) e do outro lado,
 *  árvores, arbustos, bancos e postes. `livre` = intervalos de x onde não pôr casa no fundo. */
export const pracinha = (b: Batch, cx: number, cz: number, hx: number, hz: number, o: { livre?: [number, number][]; bancos?: [number, number, number][] } = {}) => {
  chao(b, cx - hx, cx + hx, cz - hz, cz + hz, "pedra", 0, 4);
  let x = cx - hx, k = 0;
  while (x < cx + hx) {
    const w = [7, 9, 7, 9, 9][k % 5], h = [7, 8.4, 9.8, 7, 8.4][(k * 3) % 5], hc = x + w / 2;
    if (!(o.livre ?? []).some(([a, c]) => hc > a && hc < c)) house(b, hc, cz - hz - 4.5, 0, w, 8, h, k, 0);
    x += w + (k % 3 === 1 ? 2.6 : 0.3); k++;
  }
  x = cx - hx; k = 3;
  while (x < cx + hx) { const w = [9, 7, 9][k % 3]; house(b, x + w / 2, cz + hz + 12, Math.PI, w, 8, [8.4, 7, 9.8][k % 3], k + 2, 0); x += w + 0.4; k++; }
  for (let i = 0; i < 7; i++) {
    const tx = cx - hx + 4 + ((hx * 2 - 8) * i) / 6 + (i % 2 ? 1.3 : -0.8), tz = cz - hz + 1.6 + (i % 3) * 0.5;
    prop(b, {}, ["tree_oak", "tree_fat", "tree-high-round"][i % 3], tx, 0, tz, 5 + (i % 3) * 0.6, tx);
    prop(b, {}, "plant_bushLarge", tx + 2.4, 0, tz + 0.4, 1.2, tx);
  }
  for (const [bx, bz, yaw] of o.bancos ?? []) banco(b, bx, bz, yaw);
  for (let i = 0; i < 4; i++) poste(b, cx - hx * 0.75 + (hx * 1.5 * i) / 3, cz - hz + 0.8);
};
/** banco de praça de madeira, assento a 0,45 m (yaw 0 = virado pra +z) */
export const banco = (b: Batch, x: number, z: number, yaw = 0) => {
  const m = new THREE.Matrix4().makeRotationY(yaw).setPosition(x, 0, z), mad = tinta("#b5733f"), fer = tinta("#3b3f4a");
  for (let i = 0; i < 3; i++) b.add(boxGeo(V(-0.9, 0.42, -0.2 + i * 0.14), V(0.9, 0.46, -0.08 + i * 0.14)), mad, m);
  for (let i = 0; i < 2; i++) b.add(boxGeo(V(-0.9, 0.58 + i * 0.16, -0.26), V(0.9, 0.7 + i * 0.16, -0.22)), mad, m);
  for (const s of [-0.75, 0.75]) { b.add(boxGeo(V(s - 0.04, 0, -0.24), V(s + 0.04, 0.42, 0.2)), fer, m); b.add(boxGeo(V(s - 0.04, 0.42, -0.26), V(s + 0.04, 0.9, -0.22)), fer, m); }
};
/** poste de luz de praça */
export const poste = (b: Batch, x: number, z: number) => {
  b.add(new THREE.CylinderGeometry(0.06, 0.09, 3.6, 10).translate(x, 1.8, z), tinta("#2f3a4a"));
  b.add(new THREE.CylinderGeometry(0.22, 0.12, 0.36, 12).translate(x, 3.75, z), tinta("#2f3a4a"));
  b.add(new THREE.SphereGeometry(0.17, 12, 10).translate(x, 3.62, z), tinta("#fff3c4"));
};

/** varal (catenária) de x0 a x1 em z, pontas na altura y, flecha `sag` */
const varal = (x0: number, x1: number, y: number, z: number, sag: number, u: number): [number, number, number] =>
  [x0 + (x1 - x0) * u, y - sag * 4 * u * (1 - u), z];
const BANDEIRAS = ["#e2453c", "#f0b429", "#35b56a", "#3f6fb5", "#e8792c", "#7b5ac9", "#fbf4e4"];
/** festa: postes nos cantos, varais de bandeirinhas (triângulos coloridos) e de luzinhas acesas (emissivas: brilham com
 *  o bloom), palco baixo de madeira no fundo e mesas com toalha. Centro (cx, cz). */
export const festa = (b: Batch, cx: number, cz: number, o: { largura?: number; prof?: number } = {}) => {
  const L = o.largura ?? 11, P = o.prof ?? 8;
  chao(b, cx - L / 2 - 3, cx + L / 2 + 3, cz - P / 2 - 2, cz + P / 2 + 2, "grama", 0.004, 4);
  chao(b, cx - L / 2, cx + L / 2, cz - P / 2, cz + P / 2, "madeira", 0.01, 2);
  const postes: [number, number][] = [[cx - L / 2, cz - P / 2], [cx + L / 2, cz - P / 2], [cx - L / 2, cz + P / 2 - 1], [cx + L / 2, cz + P / 2 - 1]];
  for (const [px, pz] of postes) b.add(new THREE.CylinderGeometry(0.07, 0.09, 3.6, 10).translate(px, 1.8, pz), tinta("#6e4b33"));
  const luz = new THREE.MeshBasicMaterial({ color: new THREE.Color(3.2, 2.4, 1.2), toneMapped: false });
  const luz2 = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.4, 2.6, 3.0), toneMapped: false });
  const fio = tinta("#3b3f4a");
  const linhas: [number, number, number, number, number][] = [
    [cx - L / 2, cx + L / 2, 3.45, cz - P / 2, 0.45], [cx - L / 2, cx + L / 2, 3.7, cz + P / 2 - 1, 0.3],
    [cx - L / 2 + 1, cx + L / 2 - 1, 3.25, cz - P / 2 - 0.12, 0.35],
  ];
  linhas.forEach(([x0, x1, y, z, sag], li) => {
    const n = 26;
    for (let i = 0; i < n; i++) {
      const a = varal(x0, x1, y, z, sag, i / n), c = varal(x0, x1, y, z, sag, (i + 1) / n);
      const len = Math.hypot(c[0] - a[0], c[1] - a[1]), ang = Math.atan2(c[1] - a[1], c[0] - a[0]);
      b.add(new THREE.BoxGeometry(len, 0.025, 0.025).rotateZ(ang).translate((a[0] + c[0]) / 2, (a[1] + c[1]) / 2, z), fio);
      if (li !== 1) {   // o varal da frente (li 1) só tem luzinhas: bandeira na frente da câmera tampa rosto
        // bandeirinha pendurada (triângulo dupla face)
        const m = varal(x0, x1, y, z, sag, (i + 0.5) / n), w = 0.17;
        const g = new THREE.BufferGeometry().setFromPoints([V(m[0] - w, m[1], z), V(m[0] + w, m[1], z), V(m[0], m[1] - 0.36, z)]);
        g.computeVertexNormals();
        b.add(g, tinta(BANDEIRAS[(i + li * 3) % BANDEIRAS.length], { side: THREE.DoubleSide }));
      }
      if (li !== 2 && i % 2 === 0) {
        const m = varal(x0, x1, y, z, sag, (i + 0.25) / n);
        b.add(new THREE.SphereGeometry(0.06, 10, 8).translate(m[0], m[1] - 0.08, z), (i / 2) % 3 === 1 ? luz2 : luz);
      }
    }
  });
  // palco baixo no fundo + painel
  b.add(boxGeo(V(cx - 2.6, 0, cz - P / 2 + 0.2), V(cx + 2.6, 0.32, cz - P / 2 + 2.2), 2), lam("planksHD", () => ({ map: planksHD() })));
  // painel do palco claro (creme quente) com faixa de lâmpadas acesas em cima: o fundo da festa fica iluminado
  b.add(boxGeo(V(cx - 2.8, 0, cz - P / 2 - 0.1), V(cx + 2.8, 2.9, cz - P / 2 + 0.2)), tinta("#f6deb0"));
  b.add(boxGeo(V(cx - 2.9, 2.9, cz - P / 2 - 0.12), V(cx + 2.9, 3.1, cz - P / 2 + 0.24)), tinta("#e2453c"));
  for (let i = 0; i < 12; i++) b.add(new THREE.SphereGeometry(0.075, 10, 8).translate(cx - 2.6 + (5.2 * i) / 11, 2.78, cz - P / 2 + 0.26), luz);
  for (const s of [-1, 1]) for (let j = 0; j < 6; j++) b.add(new THREE.SphereGeometry(0.07, 10, 8).translate(cx + s * 2.68, 0.45 + 0.42 * j, cz - P / 2 + 0.26), j % 2 ? luz2 : luz);
  // mesas com toalha e bolo
  for (const [tx, tz] of [[cx - L / 2 + 1.4, cz + 0.4], [cx + L / 2 - 1.4, cz + 0.4]] as const) {
    b.add(boxGeo(V(tx - 0.7, 0, tz - 0.45), V(tx + 0.7, 0.74, tz + 0.45)), tinta("#fbf4e4"));
    b.add(boxGeo(V(tx - 0.72, 0.6, tz - 0.47), V(tx + 0.72, 0.62, tz + 0.47)), tinta("#e2453c"));
    b.add(new THREE.CylinderGeometry(0.22, 0.22, 0.22, 20).translate(tx - 0.2, 0.85, tz), tinta("#f7c6d9"));
    b.add(new THREE.CylinderGeometry(0.05, 0.05, 0.16, 10).translate(tx + 0.3, 0.82, tz + 0.1), tinta("#ffd84a"));
    b.add(new THREE.CylinderGeometry(0.05, 0.05, 0.16, 10).translate(tx + 0.45, 0.82, tz - 0.1), tinta("#8fd3ff"));
  }
};
