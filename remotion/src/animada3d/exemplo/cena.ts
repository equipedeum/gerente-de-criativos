// EXEMPLO de estrutura da Animação viral (menu 10): cenário + tomadas de um vídeo de ~65 s (tempos de outro vídeo; troque tudo).
// Roteiro em roteiro.md. Tempos em segundos da fala (work/<id>/words_cut.json); F() converte pra quadro (30 fps).
// Lembrete do formato vertical: com fov 40 a tela enxerga só ~0,41 x a distância de largura. Por isso tudo é montado
// em profundidade (fila em diagonal, coisas empilhadas pra cima) e não lado a lado.
import * as THREE from "three";
import { Batch, boxGeo, quad, V, lam, house, prop } from "../motor/build";
import { cobbleHD, grassHD, planksHD, stoneHD, ctex } from "../motor/paint";
import { Pen, Outfit, Expr, SKIN, fxBurst, fxPuff, fxStars } from "../motor/toon";
import { Filme, Tomada, Ctx, trilho, tinta, peca, mira, K } from "../motor/mundo";
import { Quem, FPS, q, hh, clamp01, smooth, easeOut, lerp, pop, rampa } from "../motor/elenco";
import { robo, RoboOpts, xis, check, balao, celular, calendario, folha, sino, placa, painelCampanha, planta, lupa, moeda2d, riscos, brilho, seta, mostrador } from "../motor/desenhos";

export const TOTAL = 1951; // 65,03 s
const F = (t: number) => Math.round(t * FPS);

// ---------------- elenco ----------------
const roupa = (jacket: string, hair: string, skin = SKIN, extra: Partial<Outfit> = {}): Outfit => ({ jacket, pants: "#3b3f52", boots: "#4a3426", hat: "hair", hair, skin, ...extra });
/** o dono: camiseta preta e cabelo curto escuro, como a pessoa */
const DONO: Quem = { i: 3, okey: "dono", o: { jacket: "#30313a", pants: "#3b4a6b", boots: "#f4f1ea", hat: "hair", hair: "#4a3526", skin: SKIN, buttons: "#30313a" } };
const EQUIPE: Quem[] = [
  { i: 11, okey: "eq0", o: roupa("#3f6fb5", "#2a201a", "#f5c9a0") },
  { i: 12, okey: "eq1", o: roupa("#c25a7a", "#7a4b2a", "#ecd0b6", { dress: "#c25a7a" }) },
  { i: 14, okey: "eq2", o: roupa("#5d7a3a", "#2a201a", "#c99067", { hat: "cap", cap: "#e2a13c" }) },
];
const LEADS: Quem[] = [
  { i: 21, okey: "ld0", o: roupa("#b5653f", "#5a3b2a", "#f5c9a0") },
  { i: 22, okey: "ld1", o: roupa("#7b5ac9", "#2a201a", "#c99067", { dress: "#7b5ac9" }) },
  { i: 23, okey: "ld2", o: roupa("#2f5f6a", "#c9a24a", SKIN) },
];
const CONS: Quem[] = [
  { i: 31, okey: "cs0", o: roupa("#1f8a8a", "#2a201a", "#ecd0b6") },
  { i: 32, okey: "cs1", o: roupa("#1f8a8a", "#7a4b2a", "#c99067", { dress: "#1f8a8a" }) },
  { i: 33, okey: "cs2", o: roupa("#1f8a8a", "#4a3526", "#f5c9a0", { moustache: "#4a3526" }) },
];
const LOJA: Quem[] = [
  { i: 41, okey: "lj0", o: roupa("#d9a441", "#2a201a", "#c99067", { hat: "cap", cap: "#3f6fb5" }) },
  { i: 42, okey: "lj1", o: roupa("#8c3b4a", "#5a3b2a", SKIN, { dress: "#8c3b4a" }) },
];

// ---------------- lugares (y = 0 no chão; a câmera olha quase sempre pra -z) ----------------
const BANC = { x0: -3.2, x1: 2.6, z: -6, top: 0.9 };            // bancada das 7 ferramentas
const MAQ_X = (i: number) => -2.8 + 0.8 * i;
const LIXO: [number, number, number] = [3.7, 0, -6];
const MESAS: [number, number][] = [[17, -5], [18.3, -6.6], [19.6, -8.2]]; // equipe, em diagonal
const BAR_C = (i: number) => -19.2 + 0.6 * i, BAR_F = (i: number) => -14.6 + 0.6 * i, BAR_Z = -7;
const MOEDA: [number, number, number] = [-8.9, 0.82, -5.2];     // torre de moedas (preço)
const OURO_X = (i: number) => 6.2 + 0.6 * i;
const TORRE: [number, number, number] = [34, 6.6, -7.4];        // centro do mostrador do relógio
const REUNIAO: [number, number] = [-40, -6.2];
const LOJA_XZ: [number, number] = [50, -13];
const CORES_MAQ = ["#e2453c", "#3f6fb5", "#35b56a", "#f0b429", "#7b5ac9", "#22a7b6", "#e8792c"];
const NOTAS = ["#ffd84a", "#ff9db0", "#8fd3ff", "#a8e6a1", "#ffd84a", "#8fd3ff", "#ff9db0", "#a8e6a1", "#ffd84a"];

const construir = (root: THREE.Group, dyn: Record<string, THREE.Object3D>) => {
  const b = new Batch();
  const up = (x0: number, x1: number, z0: number, z1: number, y: number, tile: number) =>
    quad(V(x0, y, z1), V(x1, y, z1), V(x1, y, z0), V(x0, y, z0), (x1 - x0) / tile, (z1 - z0) / tile);
  const M = {
    grama: lam("grassHD", () => ({ map: grassHD() })),
    pedra: lam("cobbleHD", () => ({ map: cobbleHD() })),
    madeira: lam("planksHD", () => ({ map: planksHD() })),
    muro: lam("copeHD", () => ({ map: stoneHD("copeHD", ["#e6dccd", "#ddd3c3", "#ece4d6", "#d6cbba"], "#aea293") })),
  };
  b.add(up(-900, 900, -900, 900, -0.02, 4), M.grama);
  b.add(up(-70, 70, -15.5, 12, 0, 4), M.pedra);
  // casas ao fundo (fachadas pra câmera) e do outro lado da praça
  let x = -68, k = 0;
  while (x < 66) {
    const w = [7, 9, 7, 9, 9][k % 5], h = [7, 8.4, 9.8, 7, 8.4][(k * 3) % 5];
    const perto = Math.abs(x + w / 2 - LOJA_XZ[0]) < 6.5;
    if (!perto) house(b, x + w / 2, -20, 0, w, 8, h, k, 0);
    x += w + (k % 3 === 1 ? 2.6 : 0.3); k++;
  }
  x = -66; k = 3;
  while (x < 66) { const w = [9, 7, 9][k % 3]; house(b, x + w / 2, 21, Math.PI, w, 8, [8.4, 7, 9.8][k % 3], k + 2, 0); x += w + 0.4; k++; }
  for (const [tx, tz, th] of [[-11.5, -13.5, 5.2], [8, -14, 6], [26.5, -13.6, 5.4], [-31, -13.8, 6.2], [42, -13.5, 5.6], [-52, -13, 6], [58.5, -12.6, 5.2], [12.5, -14.2, 4.6], [-47, -9.5, 4.8]] as const)
    prop(b, {}, ["tree_oak", "tree_fat", "tree-high-round"][Math.abs(Math.round(tx)) % 3], tx, 0, tz, th, tx);
  for (const [hx, hz] of [[-6, -12.6], [5.5, -12.4], [14, -12.8], [23.5, -12.5], [-23, -12.6], [-34, -12.4], [40, -11.8], [-45, -12.4]] as const)
    prop(b, {}, "plant_bushLarge", hx, 0, hz, 1.3, hx);
  // A: bancada + caçamba + base da alavanca
  b.add(boxGeo(V(BANC.x0, 0, BANC.z - 0.5), V(BANC.x1, BANC.top, BANC.z + 0.5), 2), M.madeira);
  b.add(boxGeo(V(BANC.x0 - 0.08, BANC.top, BANC.z - 0.58), V(BANC.x1 + 0.08, BANC.top + 0.08, BANC.z + 0.58), 2), tinta("#8a5a34"));
  const cx = LIXO[0], cz = LIXO[2];
  for (const [x0, x1, z0, z1] of [[-0.75, 0.75, -0.6, -0.5], [-0.75, 0.75, 0.5, 0.6], [-0.75, -0.65, -0.6, 0.6], [0.65, 0.75, -0.6, 0.6]])
    b.add(boxGeo(V(cx + x0, 0, cz + z0), V(cx + x1, 1.15, cz + z1)), tinta("#4f8a5b"));
  b.add(boxGeo(V(cx - 0.82, 1.15, cz - 0.67), V(cx + 0.82, 1.25, cz + 0.67), 0, true), tinta("#3d6e48"));
  b.add(up(cx - 0.66, cx + 0.66, cz - 0.5, cz + 0.5, 0.4, 2), tinta("#1d2b22"));
  // mesa do preço
  b.add(boxGeo(V(MOEDA[0] - 0.55, 0, MOEDA[2] - 0.45), V(MOEDA[0] + 0.55, 0.74, MOEDA[2] + 0.45), 2), M.madeira);
  b.add(boxGeo(V(MOEDA[0] - 0.62, 0.74, MOEDA[2] - 0.52), V(MOEDA[0] + 0.62, 0.82, MOEDA[2] + 0.52)), tinta("#8a5a34"));
  // B: mesas da equipe + postes do quadro de tarefas
  for (const [mx, mz] of MESAS) {
    b.add(boxGeo(V(mx - 0.75, 0.72, mz + 0.25), V(mx + 0.75, 0.8, mz + 1.0)), tinta("#8a5a34"));
    b.add(boxGeo(V(mx - 0.7, 0, mz + 0.3), V(mx + 0.7, 0.72, mz + 0.95), 2), M.madeira);
  }
  // C: base dos gráficos + postes do painel da campanha
  for (const bx of [BAR_C(2), BAR_F(2)]) b.add(boxGeo(V(bx - 1.6, 0, BAR_Z - 0.45), V(bx + 1.6, 0.16, BAR_Z + 0.45), 2), M.muro);
  for (const s of [-1, 1]) b.add(boxGeo(V(-26 + s * 1.3 - 0.07, 0, -7.12), V(-26 + s * 1.3 + 0.07, 1.4, -6.98)), tinta("#6e4b33"));
  // D: torre do relógio
  b.add(boxGeo(V(32.5, 0, -10.5), V(35.5, 9.2, -7.5), 2.5), lam("towerHD", () => ({ map: stoneHD("towerHD") })));
  b.add(boxGeo(V(32.3, 9.2, -10.7), V(35.7, 9.6, -7.3), 2, true), M.muro);
  const cap = new THREE.ConeGeometry(2.5, 2.6, 4); cap.rotateY(Math.PI / 4);
  b.add(cap, tinta("#b8644f"), new THREE.Matrix4().makeTranslation(34, 10.9, -9));
  b.add(new THREE.CircleGeometry(1.45, 40), lam("mostrador", () => ({ map: ctex("mostrador", 512, 512, (g) => mostrador(g)) })), new THREE.Matrix4().makeTranslation(TORRE[0], TORRE[1], TORRE[2] - 0.06));
  b.add(boxGeo(V(33.9, 0, -5.1), V(35.3, 0.8, -4.3), 2), M.madeira);
  // E: mesa de reunião, cadeira vazia, postes da planta
  const [rx, rz] = REUNIAO;
  b.add(boxGeo(V(rx - 1.05, 0.7, rz - 0.5), V(rx + 1.05, 0.8, rz + 0.5)), tinta("#8a5a34"));
  for (const sx of [-0.9, 0.9]) for (const sz of [-0.38, 0.38]) b.add(boxGeo(V(rx + sx - 0.06, 0, rz + sz - 0.06), V(rx + sx + 0.06, 0.7, rz + sz + 0.06)), tinta("#6e4b33"));
  for (const s of [-1, 1]) b.add(boxGeo(V(-36.4 + s * 1.2 - 0.06, 0, -7.52), V(-36.4 + s * 1.2 + 0.06, 1.3, -7.4)), tinta("#6e4b33"));
  // F: a "sua empresa" (loja com toldo)
  house(b, LOJA_XZ[0], LOJA_XZ[1], 0, 8, 6, 5.6, 1, 0);
  for (let i = 0; i < 8; i++) b.add(boxGeo(V(46.4 + i * 0.9, 2.75 - 0, -10), V(47.3 + i * 0.9, 2.95, -8.7), 0, true), tinta(i % 2 ? "#f4efe2" : "#e2453c"));
  b.build(root);

  // ---- objetos dinâmicos ----
  for (let i = 0; i < 7; i++) {
    const g = new THREE.Group();
    const corpo = peca(new THREE.BoxGeometry(0.62, 0.6, 0.56).translate(0, 0.3, 0), tinta(CORES_MAQ[i]));
    const topo = peca(new THREE.BoxGeometry(0.36, 0.2, 0.36).translate(0, 0.7, 0), tinta("#e9e4d8"));
    const visor = peca(new THREE.CylinderGeometry(0.17, 0.17, 0.06, 20).rotateX(Math.PI / 2).translate(0, 0.32, 0.29), tinta("#fbf7ee"));
    const ant = peca(new THREE.CylinderGeometry(0.025, 0.025, 0.3, 8).translate(i % 2 ? 0.1 : -0.1, 0.95, 0), tinta("#55607a"));
    const bola = peca(new THREE.SphereGeometry(0.07, 12, 10).translate(i % 2 ? 0.1 : -0.1, 1.12, 0), tinta("#ffd84a"));
    g.add(corpo, topo, visor, ant, bola);
    dyn["maq" + i] = g;
  }
  const moedaGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.085, 28).translate(0, 0.0425, 0);
  for (let i = 0; i < 12; i++) dyn["moeda" + i] = peca(moedaGeo, tinta(i % 2 ? "#ffc93c" : "#f2b422"));
  const barGeo = new THREE.BoxGeometry(0.46, 1, 0.46).translate(0, 0.5, 0);
  for (let i = 0; i < 5; i++) { dyn["barC" + i] = peca(barGeo, tinta("#e2453c")); dyn["barF" + i] = peca(barGeo, tinta("#35b56a")); }
  const ouroGeo = new THREE.CylinderGeometry(0.27, 0.27, 1, 28).translate(0, 0.5, 0);
  for (let i = 0; i < 5; i++) dyn["ouro" + i] = peca(ouroGeo, lam("ouroPilha", () => ({ map: ctex("ouroPilha", 64, 256, (g) => { for (let y = 0; y < 256; y += 16) { g.fillStyle = (y / 16) % 2 ? "#ffc93c" : "#e9a81c"; g.fillRect(0, y, 64, 16); } }) })));
  const caixaGeo = new THREE.BoxGeometry(0.66, 0.66, 0.66).translate(0, 0.33, 0);
  for (let i = 0; i < 9; i++) dyn["caixa" + i] = peca(caixaGeo, i % 3 === 1 ? tinta("#c9955c") : M.madeira);
  const pilhaGeo = new THREE.BoxGeometry(0.5, 1, 0.38).translate(0, 0.5, 0);
  const papelMat = lam("pilhaPapel", () => ({ map: ctex("pilhaPapel", 64, 256, (g) => { g.fillStyle = "#fbf8f0"; g.fillRect(0, 0, 64, 256); g.fillStyle = "#b9bfcc"; for (let y = 6; y < 256; y += 9) g.fillRect(0, y, 64, 2); }) }));
  for (let i = 0; i < 5; i++) dyn["pilha" + i] = peca(pilhaGeo, papelMat);
  const notaGeo = new THREE.BoxGeometry(0.5, 0.5, 0.03);
  for (let i = 0; i < 9; i++) dyn["nota" + i] = peca(notaGeo, tinta(NOTAS[i]));
  dyn.pontH = peca(new THREE.BoxGeometry(0.16, 0.8, 0.05).translate(0, 0.34, 0), tinta("#241726"));
  dyn.pontM = peca(new THREE.BoxGeometry(0.1, 1.2, 0.05).translate(0, 0.52, 0.03), tinta("#241726"));
  const alav = new THREE.Group();
  alav.add(peca(new THREE.CylinderGeometry(0.05, 0.05, 1.3, 10).translate(0, 0.65, 0), tinta("#8f9bb0")), peca(new THREE.SphereGeometry(0.17, 18, 14).translate(0, 1.35, 0), tinta("#e2453c")));
  dyn.alavanca = alav;
  dyn.alavBase = peca(new THREE.BoxGeometry(0.6, 0.5, 0.6).translate(0, 0.25, 0), tinta("#55607a"));
  const quadro = new THREE.Group();
  for (const s of [-1, 1]) quadro.add(peca(new THREE.BoxGeometry(0.12, 3.7, 0.12).translate(19.9 + s * 1.15, 1.85, -9.5), tinta("#6e4b33")));
  quadro.add(peca(new THREE.BoxGeometry(2.7, 2.2, 0.08).translate(19.9, 2.65, -9.46), tinta("#f4efe2")));
  dyn.quadro = quadro;
  dyn.mesaRobo = peca(new THREE.BoxGeometry(1.3, 0.8, 0.7).translate(0, 0.4, 0), M.madeira);
};

// ---------------- ajudas de palco ----------------
const roboEm = (c: Ctx, x: number, y: number, z: number, o: RoboOpts & { escala?: number; espelho?: boolean } = {}) => {
  const { escala = 0.8, espelho, ...r } = o;
  const opts: RoboOpts = { ...r, chama: q(0.5 + 0.5 * Math.sin(c.t * 23), 4), bracos: r.bracos ? [Math.round(r.bracos[0] / 5) * 5, Math.round(r.bracos[1] / 5) * 5] : undefined, tilt: r.tilt ? Math.round(r.tilt) : 0 };
  c.boneco(`robo|${JSON.stringify(opts)}`, (p) => robo(p, opts), x, y + 0.06 * Math.sin(c.t * 3.1), z, { escala, espelho, sombra: false });
  if (y < 1.2) c.sombra(x, 0, z, 0.8, 0.7);
};
const estouro = (c: Ctx, t0: number, x: number, y: number, z: number, tam = 1.2, dur = 0.3, cor = "#fff3b0") => {
  const u = (c.t - t0) / dur;
  if (u < 0 || u >= 1) return;
  const k = q(u, 20);
  c.carta(`burst${k}${cor}`, 500, 500, (p) => fxBurst(p, k, cor), x, y, z, tam, tam);
};
const poeira = (c: Ctx, t0: number, x: number, y: number, z: number, tam = 1.0) => {
  const u = (c.t - t0) / 0.4;
  if (u < 0 || u >= 1) return;
  const k = q(u, 15);
  c.carta(`puff${k}`, 300, 300, (p) => fxPuff(p, k), x, y, z, tam, tam, { soft: true });
};
const estrela = (c: Ctx, t0: number, x: number, y: number, z: number, tam = 0.5, dur = 0.5, cor = "#fff3b0") => {
  const u = (c.t - t0) / dur;
  if (u < 0 || u >= 1) return;
  const s = tam * Math.sin(Math.PI * u);
  c.carta("brilho" + cor, 200, 200, (p) => brilho(p, cor), x, y, z, s, s, { rot: u * 1.2 });
};
const placaEm = (c: Ctx, txt: string, t0: number, x: number, y: number, z: number, w: number, fundo = "#fbf4e4", cor = "#241726", px = 84, sai = Infinity) => {
  const k = pop(c.t, t0) * (1 - smooth((c.t - sai) / 0.12));
  if (k <= 0) return;
  c.carta(`placa|${txt}|${fundo}`, 600, 180, (p) => placa(p, txt, fundo, cor, px), x, y, z, w * k, w * 0.3 * k, { yaw: 0 });
};
const pulo = (t: number, t0: number, i = 0, alt = 0.22) => (t < t0 ? 0 : alt * Math.abs(Math.sin((t - t0) * 8 + i * 1.3)));
const bancadaVazia = (c: Ctx) => { void c; };

// ---------------- TOMADAS ----------------
const tomadas: Tomada[] = [];
const T = (t: Tomada) => tomadas.push(t);

// ===== c01 0,00–2,77 (frase da pessoa) =====
const T_X = (i: number) => 0.42 + 0.2 * i;
const maquinas = (c: Ctx, cancelando: boolean) => {
  for (let i = 0; i < 7; i++) {
    const x0 = MAQ_X(i), tl = T_X(i) + 0.14, u = cancelando ? (c.t - tl) / 0.5 : -1;
    if (u >= 1) { poeira(c, tl + 0.5, LIXO[0], 1.5, LIXO[2] + 0.2, 1.3); continue; }
    const m = c.obj("maq" + i);
    if (u <= 0) {
      const tr = cancelando && c.t > T_X(i) ? 0.03 * Math.sin(c.t * 90) : 0;
      m.position.set(x0 + tr, BANC.top + 0.08, BANC.z); m.rotation.set(0, 0, 0); m.scale.setScalar(1);
      if (cancelando && c.t > T_X(i)) c.carta("xis", 300, 300, xis, x0, BANC.top + 0.55, BANC.z + 0.45, 0.62 * pop(c.t, T_X(i), 0.1), 0.62 * pop(c.t, T_X(i), 0.1));
    } else {
      const e = u;
      m.position.set(lerp(x0, LIXO[0], e), BANC.top + 0.08 + (1.1 - BANC.top + 0.3) * e + 2.4 * Math.sin(Math.PI * e) * (1 - 0.25 * e), BANC.z);
      m.rotation.set(0, 0, -e * 7); m.scale.setScalar(1 - 0.25 * e);
    }
  }
};
T({
  id: "c01", a: 0, b: F(2.77), luz: "day", trancos: [F(T_X(6) + 0.64)],
  cam: trilho([K(0, mira([-0.3, 1.35, -5.8], 9.2, -60, 7, 42, -0.02)), K(14, mira([-0.3, 1.35, -5.8], 9.2, -60, 7, 42, -0.02)), K(70, mira([0.1, 1.4, -5.8], 8.9, -58, 8, 42, 0.02))]),
  camD: trilho([K(0, mira([-1.7, 1.25, -5.3], 8.6, -32, 6, 32)), K(14, mira([-1.7, 1.25, -5.3], 8.6, -32, 6, 32)), K(70, mira([1.1, 1.3, -5.7], 8.4, -30, 6, 32))]),
  palco: (c) => {
    maquinas(c, true);
    const fim = c.t > T_X(6) + 0.64;
    c.gente(DONO, -3.5, 0, -4.3, { vista: "3/4D", expr: c.t < 0.36 ? "stern" : fim ? "grin" : "smile", aceno: c.t > 0.3 ? q(Math.sin(c.t * 12), 20) : undefined, olhar: 1, trocas: [0.36, T_X(6) + 0.64] });
    estouro(c, T_X(6) + 0.64, LIXO[0], 1.7, LIXO[2] + 0.3, 1.8, 0.35);
  },
});

// ===== c02 2,77–5,07 (frase da pessoa) =====
T({
  id: "c02", a: F(2.77), b: F(5.07), luz: "day", dof: 12,
  cam: trilho([K(F(2.77), mira([-3.5, 1.42, -4.3], 3.5, -20, 2, 34, 0.02)), K(F(5.07), mira([-3.5, 1.45, -4.3], 3.2, -16, 2, 34, 0.02))], 0.0008),
  camD: trilho([K(F(2.77), mira([-3.45, 1.3, -4.3], 3.6, -12, 2, 30)), K(F(5.07), mira([-3.45, 1.3, -4.3], 3.2, -10, 2, 30))], 0),
  palco: (c) => {
    const nada = c.t > 4.2;
    c.gente(DONO, -3.5, 0, -4.3, { vista: "frente", expr: nada ? "grin" : "smile_closed", cabeca: nada ? 6 : 0, aceno: nada ? q(Math.sin(c.t * 10), 20) : undefined, trocas: [4.2] });
    // folhas do calendário passando atrás dele (os últimos meses)
    for (let i = 0; i < 6; i++) {
      const u = (c.t - 2.75 - i * 0.2) / 1.5;
      if (u < 0 || u > 1) continue;
      c.carta("cal", 300, 340, (p) => calendario(p), lerp(0.6, -5.4, u), 1.7 + 0.8 * hh(i, 2) + 0.4 * Math.sin(u * 3.1), -7.4 - 0.3 * i, 0.6, 0.68, { rot: 0.5 * Math.sin(u * 6 + i) });
    }
    estrela(c, 4.3, -2.75, 2.1, -4.4, 0.4); estrela(c, 4.45, -4.2, 2.0, -4.4, 0.34); estrela(c, 4.6, -2.8, 1.2, -4.2, 0.3);
  },
});

// ===== c03 5,07–7,93 (frase da pessoa) =====
const T_CX = (k: number) => 5.3 + 0.24 * k;
const CX_POS = (k: number): [number, number, number] => [k % 2 ? 20.25 : 19.15, 1.06 * (k >> 1), -10.4 - (k % 2 ? 0.1 : 0)];
const equipe = (c: Ctx, expr: (i: number) => Expr, o: (i: number) => { aceno?: number; y?: number; prop?: ["hammer", number]; trocas?: number[] } = () => ({})) =>
  MESAS.forEach(([mx, mz], i) => { const e = o(i); c.gente(EQUIPE[i], mx, e.y ?? 0, mz, { expr: expr(i), aceno: e.aceno, prop: e.prop, trocas: e.trocas }); });
T({
  id: "c03", a: F(5.07), b: F(7.93), luz: "day", trancos: [F(6.86)],
  cam: trilho([K(F(5.07), mira([18.6, 1.6, -7], 9.4, -18, 5, 46)), K(F(5.5), mira([18.6, 1.6, -7], 9.4, -18, 5, 46)), K(F(7.3), mira([19.0, 3.0, -8], 10.6, -14, -2, 46, -0.03))]),
  palco: (c) => {
    const mais = c.t > 6.8;
    equipe(c, (i) => (mais ? (i === 1 ? "laugh" : "grin") : i === 0 ? "smile" : "grin"), (i) => ({ aceno: mais ? q(Math.sin(c.t * 11 + i), 20) : undefined, y: pulo(c.t, 6.86, i, 0.16), trocas: [6.8] }));
    for (let k = 0; k < 9; k++) {
      const u = (c.t - T_CX(k)) / 0.22;
      if (u <= 0) continue;
      const [x, y, z] = CX_POS(k), m = c.obj("caixa" + k), e = easeOut(u);
      m.position.set(x, y + 1.6 * (1 - e), z); m.rotation.set(0, 0.12 * (k % 3 - 1), 0); m.scale.setScalar(1.6);
      poeira(c, T_CX(k) + 0.2, x, y + 0.3, z + 0.6, 1.3);
    }
    estouro(c, 6.86, 19.7, 5.0, -9.6, 3.0, 0.4);
    estrela(c, 7.0, 18.5, 5.4, -9.6, 0.8); estrela(c, 7.2, 20.9, 4.4, -9.6, 0.7); estrela(c, 7.45, 18.4, 3.6, -9.5, 0.65); estrela(c, 7.65, 20.8, 5.6, -9.5, 0.6);
  },
});

// ===== c05 10,27–14,33 (frase da pessoa) =====
T({
  id: "c05", a: F(10.27), b: F(14.33), luz: "day", dof: 6, trancos: [F(11.0)],
  cam: trilho([K(F(10.27), mira([-0.9, 4.0, -5.2], 6.6, -10, -27, 46)), K(F(11.05), mira([-1.2, 1.7, -5.0], 6.8, -8, 2, 44)), K(F(12.0), mira([-1.2, 1.7, -5.0], 6.8, -8, 2, 44)), K(F(13.8), mira([-1.2, 1.8, -5.0], 6.4, -4, 3, 44, 0.03))]),
  foco: () => [-0.5, 1.6, -5.4],
  palco: (c) => {
    bancadaVazia(c);
    const u = easeOut((c.t - 10.3) / 0.7), ry = lerp(8, 0.95, u);
    const faz = c.t > 12.0;
    roboEm(c, -0.5, ry, -5.3, { olho: faz ? "foco" : c.t < 11 ? "normal" : "feliz", bracos: faz ? [100 + 50 * Math.sin(c.t * 9), 100 - 50 * Math.sin(c.t * 9)] : c.t > 11 ? [150, 150] : [30, 30], antena: 1, escala: 0.95 });
    c.sombra(-0.5, BANC.top - 0.9 + 0, -5.3, 0.8 * u, 0.6);
    estouro(c, 11.0, -0.5, 2.0, -5.5, 3.0, 0.4, "#bff6ff");
    c.gente(DONO, -2.0, 0, -4.3, { vista: "3/4D", expr: c.t < 11 ? "shock" : faz ? "laugh" : "grin", olhar: 1, aceno: c.t > 11.2 ? q(Math.sin(c.t * 10), 20) : undefined, cabeca: c.t < 11 ? -8 : 0, trocas: [11, 12], escala: 0.92 });
    // as 7 "ferramentas" viram ícones girando em volta do robô: ele faz o trabalho de todas
    if (faz) for (let i = 0; i < 7; i++) {
      const k = pop(c.t, 12.05 + i * 0.1), a = c.t * 2.6 + (i * Math.PI * 2) / 7;
      if (k <= 0) continue;
      const tipo = i % 4;
      c.carta(`icone${i}`, 200, 200, (p) => {
        p.poly([[30, 30], [170, 30], [170, 170], [30, 170]].map(([x, y]) => [x, y] as [number, number]), CORES_MAQ[i], 12);
        if (tipo === 0) p.stroke([[60, 130], [90, 95], [115, 115], [145, 65]], 16, "#ffffff");
        else if (tipo === 1) { p.poly([[55, 70], [145, 70], [145, 135], [55, 135]], "#ffffff", 0); p.stroke([[55, 72], [100, 108], [145, 72]], 10, CORES_MAQ[i]); }
        else if (tipo === 2) { p.ell(100, 92, 44, 36, "#ffffff", 0); p.poly([[78, 118], [104, 122], [74, 150]], "#ffffff", 0); }
        else for (const [x, h2] of [[66, 40], [100, 66], [134, 90]]) p.poly([[x - 12, 150 - h2], [x + 12, 150 - h2], [x + 12, 150], [x - 12, 150]], "#ffffff", 0);
      }, -0.5 + 0.95 * Math.cos(a), 2.3 + 0.55 * Math.sin(a) + 0.12 * Math.sin(a * 2 + i), -5.3 + 0.7 * Math.sin(a), 0.42 * k, 0.42 * k, { rot: 0.2 * Math.sin(c.t * 4 + i) });
    }
  },
});

// ===== c06 14,33–15,37 (frase da pessoa) =====
T({
  id: "c06", a: F(14.33), b: F(15.37), luz: "day", dof: 15,
  cam: trilho([K(F(14.33), mira([-2.0, 1.58, -4.3], 2.9, 12, 0, 30, 0.07)), K(F(15.37), mira([-2.0, 1.6, -4.3], 2.4, 9, 0, 30, 0.08))], 0),
  camD: trilho([K(F(14.33), mira([-2.0, 1.22, -4.3], 2.9, 10, 0, 28, 0.05)), K(F(15.37), mira([-2.0, 1.24, -4.3], 2.5, 8, 0, 28, 0.06))], 0),
  palco: (c) => {
    const louco = c.t > 14.95;
    c.gente(DONO, -2.0, 0, -4.3, { expr: louco ? "shock" : "smile", olhar: louco ? 0 : 1, cabeca: louco ? 0 : 5, trocas: [14.95], escala: 0.92 });
    roboEm(c, -0.5, 0.95, -5.3, { olho: "feliz", bracos: [30, 30], escala: 0.95 });
    for (let i = 0; i < 3; i++) estrela(c, 15.0 + 0.08 * i, -2.0 + [-0.5, 0.52, 0.4][i], [2.15, 2.1, 1.3][i], -4.2, 0.3, 0.35);
  },
});

// ===== c07 15,37–18,07 (frase da pessoa) =====
const T_CORTE = 16.84;
T({
  id: "c07", a: F(15.37), b: F(18.07), luz: "day", trancos: [F(T_CORTE)],
  cam: trilho([K(F(15.37), mira([-9.35, 1.5, -5.1], 6.0, 6, 5, 40)), K(F(16.6), mira([-9.35, 1.5, -5.1], 5.7, 4, 5, 40)), K(F(17.2), mira([-9.35, 1.45, -5.1], 5.3, 2, 4, 40, -0.03))]),
  camD: trilho([K(F(15.37), mira([-9.4, 1.92, -5.0], 5.0, 3, 1, 30)), K(F(16.6), mira([-9.4, 1.92, -5.0], 4.8, 2, 1, 30)), K(F(17.2), mira([-9.4, 1.92, -5.0], 4.6, 1, 1, 30, -0.02))], 0),
  palco: (c) => {
    const depois = c.t > T_CORTE;
    for (let i = 0; i < 10; i++) {
      const m = c.obj("moeda" + i), jx = 0.03 * (hh(i, 4) - 0.5);
      if (i < 5 || !depois) { m.position.set(MOEDA[0] + jx, MOEDA[1] + i * 0.088, MOEDA[2]); m.rotation.set(0, i, 0); m.scale.setScalar(1); continue; }
      const u = (c.t - T_CORTE - (i - 5) * 0.09) / 0.45;
      if (u >= 1) { m.visible = false; continue; }
      const e = clamp01(u);
      m.position.set(lerp(MOEDA[0], -9.5, e), lerp(MOEDA[1] + i * 0.088, 0.95, e) + 0.12 * Math.sin(Math.PI * e), lerp(MOEDA[2], -4.85, e));
      m.rotation.set(0, i, e * 1.2); m.scale.setScalar(lerp(1, 0.3, e));
    }
    if (depois) { const u = (c.t - T_CORTE) / 0.16; if (u < 1) c.carta("risco0", 400, 300, (p) => riscos(p, 0), MOEDA[0], MOEDA[1] + 0.56, MOEDA[2] + 0.4, 1.6, 0.5); }
    for (let i = 0; i < 4; i++) estrela(c, T_CORTE + 0.4 + 0.1 * i, -9.55 + 0.4 * (hh(i, 6) - 0.5), 0.8 + 0.3 * hh(i, 7), -4.7, 0.26, 0.35, "#ffe27a");
    c.gente(DONO, -9.9, 0, -5.0, { vista: "3/4D", expr: depois ? (c.t > T_CORTE + 0.45 ? "laugh" : "grin") : "neutral", olhar: 1, aceno: depois ? q(Math.sin(c.t * 11), 20) : undefined, y: 0, trocas: [T_CORTE, T_CORTE + 0.45] } as never);
    if (c.t < T_CORTE + 0.12) placaEm(c, "PREÇO", 15.5, MOEDA[0], 1.97, MOEDA[2], 0.9);
    placaEm(c, "METADE", T_CORTE + 0.12, -9.25, 1.97, MOEDA[2], 1.12, "#35b56a", "#ffffff");
  },
});

// ===== c09 21,17–23,27 (frase da pessoa) =====
const LEAD_XZ: [number, number][] = [[-23.5, -5.3], [-22.6, -6.4], [-21.7, -7.5]];
T({
  id: "c09", a: F(21.17), b: F(23.27), luz: "day",
  cam: trilho([K(F(21.17), mira([-26.3, 2.0, -6.8], 8.6, -8, 0, 42)), K(F(22.3), mira([-26.3, 2.0, -6.8], 8.3, -8, 0, 42)), K(F(22.62), mira([-22.6, 1.6, -6.4], 6.8, -10, 2, 42))]),
  palco: (c) => {
    const k = q(rampa(c.t, 21.2, 1.0), 12);
    c.carta(`painel${k}`, 800, 560, (p) => painelCampanha(p, k), -26, 2.5, -7, 3.2, 2.24, { yaw: 0 });
    roboEm(c, -27.35, 0.35, -5.4, { olho: "foco", bracos: [20, 95 + 8 * Math.sin(c.t * 8)] });
    LEAD_XZ.forEach(([x, z], i) => {
      const tk = 22.62 + 0.17 * i, ok = c.t > tk;
      c.gente(LEADS[i], x, 0, z, { expr: ok ? "grin" : "neutral", trocas: [tk] });
      const s = pop(c.t, tk, 0.18);
      if (s > 0) c.carta("check", 300, 300, check, x + 0.05, 2.5, z, 0.62 * s, 0.62 * s);
    });
  },
});

// ===== c10 23,27–26,27 (frase da pessoa) =====
T({
  id: "c10", a: F(23.27), b: F(26.27), luz: "day", dof: 9,
  cam: trilho([K(F(23.27), mira([-22.62, 2.0, -5.4], 5.9, 4, 0, 40)), K(F(26.27), mira([-22.62, 2.1, -5.4], 5.5, 1, 0, 40))], 0),
  camD: trilho([K(F(23.27), mira([-22.75, 1.95, -5.4], 4.8, 3, 0, 36)), K(F(26.27), mira([-22.75, 2.0, -5.4], 4.4, 1, 0, 36))], 0),
  palco: (c) => {
    const resp = c.t > 24.05, feliz = c.t > 24.5;
    c.gente(LEADS[0], -23.3, 0, -5.3, { vista: "3/4D", expr: feliz ? "grin" : resp ? "shock" : "neutral", olhar: 1, trocas: [24.05, 24.5] });
    c.carta("cel", 240, 400, (p) => celular(p), -22.93, 1.02, -5.2, 0.2, 0.33, { rot: -0.15 });
    roboEm(c, -22.2, 0.35, -5.5, { olho: resp ? "feliz" : "normal", bracos: resp ? [150, 30] : [30, 30], espelho: false });
    const b1 = pop(c.t, 23.5), b2 = pop(c.t, 24.05, 0.16);
    if (b1 > 0) c.carta("balaoP", 420, 340, (p) => balao(p, "#ffffff", -1, "interrogacao"), -23.2, 2.75, -5.25, 0.85 * b1, 0.69 * b1);
    if (b2 > 0) c.carta("balaoV", 420, 340, (p) => balao(p, "#35b56a", 1, "check"), -22.3, 2.4, -5.2, 0.95 * b2, 0.77 * b2);
    estouro(c, 24.05, -22.3, 2.4, -5.3, 1.6, 0.25, "#d6ffe4");
    // a conversa segue: mais balões pequenos subindo
    for (let i = 0; i < 3; i++) {
      const tk = 24.9 + i * 0.4, s = pop(c.t, tk, 0.16);
      if (s <= 0) continue;
      const verde = i % 2 === 1, up = 0.25 * (c.t - tk);
      c.carta(verde ? "balaoV2" : "balaoP2", 420, 340, (p) => balao(p, verde ? "#35b56a" : "#ffffff", verde ? 1 : -1, verde ? "check" : "pontos"), verde ? -22.05 : -23.5, 3.05 + 0.3 * i + up, -5.6, 0.45 * s, 0.36 * s);
    }
  },
});

// ===== c11 26,27–30,40 (frase da pessoa) =====
const NOTA_FIM = (i: number): [number, number, number] => [19.1 + 0.8 * (i % 3), 3.3 - 0.62 * Math.floor(i / 3), -9.38];
const T_NOTA = (i: number) => 27.85 + 0.2 * i;
T({
  id: "c11", a: F(26.27), b: F(30.4), luz: "day",
  cam: trilho([K(F(26.27), mira([16.6, 1.5, -4.8], 5.8, -6, 2, 40)), K(F(27.5), mira([16.6, 1.5, -4.8], 5.5, -6, 2, 40)), K(F(28.2), mira([19.6, 2.3, -9], 8.6, -14, 0, 38))]),
  palco: (c) => {
    const cobrou = c.t > 26.9;
    c.obj("quadro");
    equipe(c, (i) => (i === 0 ? (c.t > 27.25 ? "grin" : cobrou ? "shock" : "neutral") : c.t > 29.9 ? "grin" : "smile"), (i) => ({ trocas: [26.9, 27.25, 29.9], aceno: c.t > 29.9 && i > 0 ? q(Math.sin(c.t * 11 + i), 20) : undefined }));
    if (c.t > 27.25) c.carta("cel", 240, 400, (p) => celular(p), 17.42, 1.0, -4.9, 0.2, 0.33, { rot: -0.15 });
    roboEm(c, 16.0, 0.35, -4.6, { olho: "feliz", bracos: [20, cobrou ? 150 : 40] });
    if (cobrou && c.t < 28.3) { const k = q(Math.sin((c.t - 26.9) * 22) * Math.max(0, 1 - (c.t - 26.9) / 1.2), 10); c.carta(`sino${k}`, 320, 320, (p) => sino(p, k), 16.5, 2.0, -4.5, 0.6 * pop(c.t, 26.9, 0.12), 0.6 * pop(c.t, 26.9, 0.12)); }
    for (let i = 0; i < 9; i++) {
      const m = c.obj("nota" + i), [fx, fy, fz] = NOTA_FIM(i);
      const ix = 18.9 + 0.5 * hh(i, 3), iy = 1.85 + 0.35 * hh(i, 4), u = easeOut((c.t - T_NOTA(i)) / 0.3);
      m.position.set(lerp(ix, fx, u), lerp(iy, fy, u) + 0.4 * Math.sin(Math.PI * u), fz + 0.02 * i * (1 - u));
      m.rotation.set(0, 0, lerp((hh(i, 5) - 0.5) * 1.6, 0, u));
    }
    const s = pop(c.t, 29.95, 0.2);
    if (s > 0) c.carta("check", 300, 300, check, 21.0, 3.75, -9.2, 0.8 * s, 0.8 * s);
  },
});

// ===== c13+c14 33,00–37,80 (frase da pessoa) =====
const C0 = [3.2, 3.0, 3.3, 3.1, 3.2], C1 = [2.7, 2.1, 1.6, 1.0, 0.55], F1 = [0.9, 1.4, 2.0, 2.7, 3.5];
T({
  id: "c13", a: F(33.0), b: F(37.8), luz: "day", trancos: [F(35.22), F(36.96)],
  cam: trilho([K(F(33.0), mira([-17.75, 2.5, -6.6], 10.8, -2, 2, 40)), K(F(34.3), mira([-17.75, 2.4, -6.6], 10.4, -2, 2, 40)), K(F(35.3), mira([-17.75, 2.0, -6.6], 10.0, -2, 3, 40, 0.02)), K(F(35.6), mira([-17.75, 2.0, -6.6], 10.0, -2, 3, 40, 0.02)), K(F(36.05), mira([-13.8, 2.2, -6.6], 10.8, 0, 2, 40)), K(F(37.1), mira([-13.8, 2.6, -6.6], 11.1, 0, 0, 40))]),
  palco: (c) => {
    for (let i = 0; i < 5; i++) {
      const u = easeOut((c.t - (33.85 + 0.3 * i)) / 0.28), h = lerp(C0[i], C1[i], u), m = c.obj("barC" + i);
      m.position.set(BAR_C(i), 0.16, BAR_Z); m.scale.set(1, h, 1);
      const v = easeOut((c.t - (36.1 + 0.19 * i)) / 0.26), g = c.obj("barF" + i);
      g.position.set(BAR_F(i), 0.16, BAR_Z); g.scale.set(1, lerp(0.5, F1[i], v), 1);
    }
    placaEm(c, "CUSTO", 33.3, BAR_C(2), 3.9, BAR_Z, 2.0, "#fbf4e4", "#241726", 84, 35.5);
    const ts = (c.t - 34.5) / 0.75;
    if (ts > 0 && c.t < 37) c.carta("setaR", 300, 400, (p) => seta(p, "#e2453c"), BAR_C(4) + 0.25, lerp(3.9, 1.75, easeOut(ts)), BAR_Z + 0.5, 0.9, 1.2, { rot: -0.25 });
    poeira(c, 35.22, BAR_C(4), 0.9, BAR_Z + 0.5, 1.4);
    const anda = clamp01((c.t - 35.62) / 0.6), dxo = lerp(-16.45, -15.25, anda);
    if (anda > 0 && anda < 1) c.gente(DONO, dxo, 0, -5.4, { vista: "perfilD", modoPerfil: "march", fase: q(((c.t - 35.62) * 2.2) % 1, 24), expr: "grin", escala: 0.9 });
    else c.gente(DONO, dxo, anda < 1 ? pulo(c.t, 35.3, 0, 0.14) : pulo(c.t, 37.0, 0, 0.16), -5.4, { expr: c.t > 36.96 ? "laugh" : c.t > 35.2 ? "grin" : "smile", vista: anda < 1 ? "3/4E" : "3/4D", olhar: anda < 1 ? -1 : 1, aceno: c.t > 35.2 ? q(Math.sin(c.t * 11), 20) : undefined, trocas: [35.2, 36.96], escala: 0.9 });
    placaEm(c, "FATURAMENTO", 36.06, BAR_F(2) - 0.2, 4.05, BAR_Z, 2.4, "#fbf4e4", "#241726", 70);
    const subiu = (c.t - 36.3) / 0.7;
    if (subiu > 0) c.carta("setaG", 300, 400, (p) => seta(p, "#35b56a"), BAR_F(0) - 0.3, lerp(1.2, 3.3, easeOut(subiu)), BAR_Z + 0.5, 0.9, 1.2, { rot: Math.PI + 0.25 });
    estouro(c, 36.96, BAR_F(4), 3.9, BAR_Z + 0.4, 2.0, 0.35);
    for (let i = 0; i < 6; i++) {
      const u = (c.t - 36.96 - 0.07 * i) / 0.8;
      if (u < 0 || u > 1) continue;
      c.carta("moeda2d", 200, 200, moeda2d, BAR_F(4) + (hh(i, 1) - 0.6) * 2.2 * u, 3.8 + 1.5 * Math.sin(Math.PI * u * 0.8) - 0.6 * u, BAR_Z + 0.5, 0.36, 0.36, { rot: u * 5 });
    }
  },
});

// ===== c15 37,80–43,40 (frase da pessoa) =====
const T_ROBO = 38.86, ROBO_MESA: [number, number, number] = [20.7, 0, -4.6];
const T_PILHA = (i: number) => 39.45 + 0.42 * i;
T({
  id: "c15", a: F(37.8), b: F(43.4), luz: "day",
  cam: trilho([K(F(37.8), mira([18.4, 1.5, -6.4], 8.4, -24, 5, 44)), K(F(39.0), mira([18.6, 1.5, -6.4], 8.6, -22, 5, 44)), K(F(40.6), mira([19.5, 1.45, -5.6], 8.8, -14, 5, 46)), K(F(43.4), mira([19.6, 1.45, -5.4], 8.2, -10, 4, 46, -0.02))], 0),
  camD: trilho([K(F(37.8), mira([18.6, 1.5, -6.0], 8.2, -16, 6, 36)), K(F(39.0), mira([18.8, 1.5, -6.0], 8.2, -14, 6, 36)), K(F(40.6), mira([19.2, 1.5, -5.6], 8.0, -10, 6, 36)), K(F(43.4), mira([19.3, 1.5, -5.4], 7.4, -8, 5, 36))], 0),
  palco: (c) => {
    const mr = c.obj("mesaRobo"); mr.position.set(ROBO_MESA[0], 0, ROBO_MESA[2]);
    const livre = (i: number) => c.t > T_PILHA(i) + 0.15;
    equipe(c, (i) => (livre(i) ? (c.t > 41.9 ? (i === 1 ? "laugh" : "grin") : "relief") : i === 1 ? "dazed" : "pained"),
      (i) => ({ prop: livre(i) ? undefined : ["hammer", q(0.5 + 0.5 * Math.sin(c.t * 15 + i * 2), 8)], aceno: c.t > 41.9 ? q(Math.sin(c.t * 11 + i), 20) : undefined, y: pulo(c.t, 41.9, i, 0.14), trocas: [T_PILHA(i) + 0.15, 41.9] }));
    // as pilhas de papel saem das mesas e vão pra mesa do robô
    let naMesa = 0;
    MESAS.forEach(([mx, mz], i) => {
      const m = c.obj("pilha" + i), u = clamp01((c.t - T_PILHA(i)) / 0.45), h = 0.75 - 0.08 * i;
      if (u >= 1) { naMesa += 1; m.visible = false; return; }
      m.position.set(lerp(mx - 0.42, ROBO_MESA[0] - 0.3, u), 0.8 + 1.5 * Math.sin(Math.PI * u), lerp(mz + 0.78, ROBO_MESA[2], u)); m.scale.set(1, h * 0.45, 1); m.rotation.set(0, 0, 0);
    });
    // a pilha na mesa do robô: cresce com o que chega e vai sendo carimbada (diminui), folhas prontas voam pra direita
    const carimbando = c.t > 40.0, gasto = carimbando ? 0.2 * (c.t - 40.0) : 0, alt = Math.max(0.06, 0.3 * naMesa - 0.75 * gasto);
    if (naMesa > 0) { const p4 = c.obj("pilha3"); p4.position.set(ROBO_MESA[0] - 0.3, 0.8, ROBO_MESA[2]); p4.scale.set(1, alt, 1); p4.rotation.set(0, 0, 0); }
    if (carimbando) {
      const feito = c.obj("pilha4"); feito.position.set(ROBO_MESA[0] + 0.36, 0.8, ROBO_MESA[2]); feito.scale.set(1, Math.min(1.0, 0.06 + gasto * 1.1), 1); feito.rotation.set(0, 0, 0);
      for (let k = 0; k < 3; k++) {
        const u = ((c.t * 3.2 + k / 3) % 1);
        c.carta("folhaC", 240, 300, (p) => folha(p, true), lerp(ROBO_MESA[0] - 0.3, ROBO_MESA[0] + 0.36, u), 1.0 + alt + 0.6 * Math.sin(Math.PI * u), ROBO_MESA[2] + 0.25, 0.3, 0.37, { rot: u * 3 });
      }
    }
    const ent = easeOut((c.t - T_ROBO) / 0.5), rxo = lerp(24.5, ROBO_MESA[0] - 1.1, ent);
    if (c.t > T_ROBO) roboEm(c, rxo, 0.35, ROBO_MESA[2] + 0.1, { olho: carimbando ? "foco" : "feliz", bracos: carimbando ? [40, 70 + 40 * Math.sin(c.t * 20)] : [150, 150] });
    if (c.t > T_ROBO && c.t < T_ROBO + 0.4) c.carta("risco1", 400, 300, (p) => riscos(p, 1), rxo + 1.2, 1.3, ROBO_MESA[2], 1.6, 1.0);
    estrela(c, 42.0, 17.0, 2.5, -4.8, 0.5); estrela(c, 42.2, 18.6, 2.6, -6.3, 0.5); estrela(c, 42.45, 19.7, 2.6, -7.9, 0.5);
  },
});

// ===== c16 43,40–46,13 (frase da pessoa) =====
T({
  id: "c16", a: F(43.4), b: F(46.13), luz: "day",
  cam: trilho([K(F(43.4), mira([34, 6.3, -7.4], 9.2, -6, -31, 44, 0.04)), K(F(44.5), mira([34, 6.1, -7.4], 8.8, -6, -30, 44, 0.04)), K(F(45.2), mira([34.15, 1.45, -4.8], 5.4, -6, 3, 42))]),
  palco: (c) => {
    const h = c.obj("pontH"), m = c.obj("pontM"), w = (c.t - 43.4);
    h.position.set(TORRE[0], TORRE[1], TORRE[2]); h.rotation.set(0, 0, -w * 2.6 - 1);
    m.position.set(TORRE[0], TORRE[1], TORRE[2]); m.rotation.set(0, 0, -w * 2.6 * 12);
    roboEm(c, 33.35, 0.35, -4.6, { olho: "foco", bracos: [30, 70 + 40 * Math.sin(c.t * 20)] });
    const p0 = c.obj("pilha0"), p1 = c.obj("pilha1"), g = clamp01((c.t - 44.6) / 1.5);
    p0.position.set(34.25, 0.8, -4.7); p0.scale.set(1, lerp(0.7, 0.1, g), 1); p0.rotation.set(0, 0, 0);
    p1.position.set(34.95, 0.8, -4.7); p1.scale.set(1, lerp(0.08, 0.68, g), 1); p1.rotation.set(0, 0, 0);
    for (let k = 0; k < 3; k++) {
      const u = ((c.t * 3.4 + k / 3) % 1);
      c.carta("folhaC", 240, 300, (p) => folha(p, true), lerp(34.25, 34.95, u), 1.6 + 0.5 * Math.sin(Math.PI * u), -4.45, 0.3, 0.37, { rot: u * 3 });
    }
    estrela(c, 45.4, 35.2, 2.2, -4.6, 0.45); estrela(c, 45.65, 34.0, 2.5, -4.8, 0.4);
  },
});

// ===== c18 48,47–50,80 (frase da pessoa) =====
const T_ALAV = 49.14;
T({
  id: "c18", a: F(48.47), b: F(50.8), luz: "day", trancos: [F(T_ALAV + 0.14)],
  cam: trilho([K(F(48.47), mira([0.1, 1.4, -4.8], 6.4, 4, 3, 40, 0.03)), K(F(49.2), mira([0.1, 1.4, -4.8], 6.1, 4, 3, 40, 0.03)), K(F(49.9), mira([0.35, 1.6, -5.2], 6.6, 2, 2, 42, -0.03))]),
  camD: trilho([K(F(48.47), mira([0.3, 1.45, -4.8], 5.6, 4, 3, 32, 0.02)), K(F(49.2), mira([0.3, 1.45, -4.8], 5.4, 4, 3, 32, 0.02)), K(F(49.9), mira([0.45, 1.6, -5.1], 6.0, 2, 2, 34, -0.02))], 0),
  palco: (c) => {
    const u = easeOut((c.t - T_ALAV) / 0.14), a = c.obj("alavanca");
    a.position.set(0.95, 0.45, -4.4); a.rotation.set(0, 0, lerp(0.55, -0.7, u));
    c.obj("alavBase").position.set(0.95, 0, -4.4);
    c.gente(DONO, -0.5, 0, -4.6, { vista: "3/4D", expr: c.t > T_ALAV ? (c.t > 49.8 ? "laugh" : "grin") : "stern", olhar: 1, aceno: q(c.t > T_ALAV ? Math.sin(c.t * 11) : -0.6, 20), tilt: c.t > T_ALAV && c.t < T_ALAV + 0.3 ? 8 : 0, trocas: [T_ALAV, 49.8] });
    estouro(c, T_ALAV + 0.14, 1.5, 1.1, -4.2, 1.4, 0.3);
    if (c.t > T_ALAV + 0.1) {
      const e = easeOut((c.t - T_ALAV - 0.1) / 0.3);
      roboEm(c, 1.2, lerp(-1.6, 1.0, e), -6.6, { olho: "feliz", bracos: [150, 150], escala: 0.95 });
      for (let i = 0; i < 5; i++) estrela(c, T_ALAV + 0.35 + 0.16 * i, 1.0 + 0.9 * Math.cos(i * 1.9), 2.6 + 0.6 * Math.sin(i * 2.3), -6.2, 0.5, 0.45);
    }
    if (c.t > T_ALAV && c.t < T_ALAV + 0.35) c.carta("risco2", 400, 300, (p) => riscos(p, 2), 0.9, 2.0, -4.3, 1.2, 0.75);
  },
});

// ===== c19 50,80–53,10 (frase da pessoa) =====
const O1 = [0.8, 1.3, 1.9, 2.6, 3.4];
T({
  id: "c19", a: F(50.8), b: F(53.1), luz: "day", trancos: [F(52.68)],
  cam: trilho([K(F(50.8), mira([7.75, 1.7, -6.4], 9.6, -4, 3, 42)), K(F(52.6), mira([7.75, 2.4, -6.4], 10.2, -4, -1, 42, -0.03))]),
  palco: (c) => {
    for (let i = 0; i < 5; i++) {
      const u = easeOut((c.t - (51.0 + 0.3 * i)) / 0.3), m = c.obj("ouro" + i);
      m.position.set(OURO_X(i), 0, -6.8); m.scale.set(1, lerp(0.25, O1[i], u), 1);
      estrela(c, 51.3 + 0.3 * i, OURO_X(i), lerp(0.25, O1[i], 1) + 0.25, -6.5, 0.5, 0.4, "#ffe27a");
    }
    c.gente(DONO, 9.3, pulo(c.t, 52.3, 0, 0.18), -5.6, { expr: c.t > 52.2 ? "laugh" : "grin", vista: "3/4E", olhar: -1, aceno: q(Math.sin(c.t * 11), 20), trocas: [52.2], escala: 0.9 });
    for (let i = 0; i < 9; i++) {
      const u = ((c.t - 51.2) * 0.9 + hh(i, 2)) % 1;
      if (c.t < 51.2 + hh(i, 2)) continue;
      c.carta("moeda2d", 200, 200, moeda2d, 6.0 + 3.0 * hh(i, 3), lerp(6.2, 0.4, u), -6.2 - 0.5 * hh(i, 4), 0.32, 0.32, { rot: u * 6 + i });
    }
    placaEm(c, "LUCRO", 52.5, 7.4, 4.3, -6.8, 2.0, "#35b56a", "#ffffff");
    estouro(c, 52.68, OURO_X(4), 3.7, -6.4, 2.0, 0.35);
  },
});

// ===== c20 53,10–57,30 (frase da pessoa) =====
T({
  id: "c20", a: F(53.1), b: F(57.3), luz: "day",
  cam: trilho([K(F(53.1), mira([-39.85, 1.9, -6.2], 7.6, 5, 2, 42)), K(F(57.3), mira([-39.85, 2.0, -6.2], 6.8, 3, 2, 42))], 0),
  camD: trilho([K(F(53.1), mira([-39.6, 1.8, -6.0], 6.6, 4, 2, 34)), K(F(57.3), mira([-39.6, 1.85, -6.0], 5.9, 3, 2, 34))], 0),
  palco: (c) => {
    const [rx, rz] = REUNIAO, agenda = c.t > 55.58;
    const pos: [number, number][] = [[rx - 0.85, rz - 0.75], [rx, rz - 1.25], [rx + 0.85, rz - 0.75]];
    CONS.forEach((w, i) => c.gente(w, pos[i][0], 0, pos[i][1], { expr: i === 1 ? "grin" : "smile", aceno: (c.t + i * 0.5) % 2.4 < 1.5 ? q(Math.sin(c.t * 9 + i * 1.3), 20) : undefined, vista: i === 0 ? "3/4D" : i === 2 ? "3/4E" : "frente" }));
    const k = pop(c.t, 55.58, 0.2);
    if (k > 0) c.carta("calM", 300, 340, (p) => calendario(p, true), rx + 0.05, 3.0 + 0.05 * Math.sin(c.t * 3), rz - 0.6, 0.95 * k, 1.08 * k, { rot: 0.05 * Math.sin(c.t * 2.2) });
    estouro(c, 55.58, rx, 3.0, rz - 0.7, 2.1, 0.3);
    for (let i = 0; i < 3; i++) estrela(c, 55.9 + 0.3 * i, rx + [-0.9, 0.95, 0.75][i], [3.4, 3.25, 2.55][i], rz - 0.5, 0.4, 0.45);
    // o dono chega e para ao lado da cadeira vazia
    const u = clamp01((c.t - 53.5) / 2.0), dx = lerp(-36.6, rx + 0.95, u), andando = u < 1;
    if (andando) c.gente(DONO, dx, 0, rz + 1.9, { vista: "perfilE", modoPerfil: "march", fase: q(((c.t - 53.5) * 1.85) % 1, 24), expr: "smile", escala: 0.9 });
    else c.gente(DONO, dx, 0, rz + 1.9, { vista: "3/4E", expr: agenda ? "grin" : "smile", olhar: -1, aceno: agenda ? q(Math.sin(c.t * 10), 20) : undefined, trocas: [55.8], escala: 0.9 });
  },
});

// ===== c21 57,30–59,10 (frase da pessoa) =====
T({
  id: "c21", a: F(57.3), b: F(59.1), luz: "day", dof: 5,
  cam: trilho([K(F(57.3), mira([-36.75, 2.1, -7], 9.2, -5, 0, 40)), K(F(59.1), mira([-36.7, 2.2, -7], 8.4, -3, 0, 40, 0.02))], 0),
  foco: () => [-36.8, 2, -7],
  palco: (c) => {
    c.carta("planta", 800, 560, planta, -36.4, 2.45, -7.4, 3.2, 2.24, { yaw: 0 });
    c.gente(CONS[0], -38.0, 0, -6.5, { vista: "3/4D", expr: "grin", olhar: 1, aceno: q(0.4 + 0.5 * Math.sin(c.t * 7), 20) });
    const a = (c.t - 57.3) * 2.4;
    c.carta("lupa", 300, 300, lupa, -36.4 + 0.9 * Math.cos(a), 2.5 + 0.5 * Math.sin(a * 1.3), -7.25, 0.95, 0.95);
  },
});

// ===== c22 59,10–62,43 (frase da pessoa) =====
const T_ENTRA = 60.96;
T({
  id: "c22", a: F(59.1), b: F(62.43), luz: "day", trancos: [F(T_ENTRA)],
  cam: trilho([K(F(59.1), mira([49.9, 1.9, -9], 9.0, -8, 0, 42)), K(F(60.9), mira([50, 2.0, -9], 8.4, -5, 0, 42)), K(F(62.0), mira([50, 2.8, -9.5], 11.5, -3, -3, 44, -0.02))]),
  camD: trilho([K(F(59.1), mira([50, 2.72, -9], 8.2, -6, 0, 34)), K(F(60.9), mira([50, 2.72, -9], 7.6, -4, 0, 34)), K(F(62.0), mira([50, 2.85, -9.4], 9.2, -3, -1, 36))], 0),
  palco: (c) => {
    const [lx] = LOJA_XZ, dentro = c.t > T_ENTRA;
    placaEm(c, "SUA EMPRESA", 58, lx, 2.75, -8.55, 2.4, "#fbf4e4", "#241726", 76);
    LOJA.forEach((w, i) => c.gente(w, lx + (i ? 1.3 : -1.3), pulo(c.t, T_ENTRA, i, 0.2), -8.3, { expr: dentro ? (i ? "laugh" : "grin") : c.t > 59.8 ? "shock" : "neutral", olhar: dentro ? 0 : i ? -1 : 1, aceno: dentro ? q(Math.sin(c.t * 11 + i), 20) : undefined, trocas: [59.8, T_ENTRA], vista: i ? "3/4E" : "3/4D" }));
    const u = smooth((c.t - 59.3) / 1.6);
    roboEm(c, lerp(48.7, lx, u), 0.35 + 0.6 * Math.sin(Math.PI * u), lerp(-4.6, -8.7, u), { olho: dentro ? "feliz" : "normal", bracos: dentro ? [150, 150] : [30, 95], escala: 0.9 });
    estouro(c, T_ENTRA, lx, 1.3, -8.4, 2.4, 0.4);
    for (let i = 0; i < 10; i++) estrela(c, T_ENTRA + 0.1 + 0.13 * i, lx + 3.4 * (hh(i, 8) - 0.5), 0.5 + 1.7 * hh(i, 9), -8.4, 0.5, 0.5, i % 2 ? "#fff3b0" : "#bff6ff");
    const k = q(((c.t - T_ENTRA) * 0.9) % 1, 30);
    if (dentro) c.carta(`stars${k}`, 420, 210, (p) => fxStars(p, k), lx, 2.25, -8.4, 1.2, 0.6);
  },
});

export const FILME: Filme = { total: TOTAL, tomadas, construir };
export type { Pen };
