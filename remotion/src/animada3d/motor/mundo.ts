// Mundo genérico do estilo "Animada 3D": céu, sol relativo à câmera (congelado por tomada), névoa, nuvens, luz em dois
// tons, e a pose de tudo a cada quadro (função pura do quadro). ADAPTADO de templates/bridge/world.ts da skill
// claude-animated-shorts (MIT, Mr omi): o rig de luz, o céu e a colocação das cartas são os dele; o cenário e a história
// vêm de fora, num `Filme` (tomadas + construir), pra cada vídeo novo só escrever a cena.
import * as THREE from "three";
import { cloudHD } from "./paint";
import { Pen, Outfit, Expr, FrontOpts, SideOpts, Prop } from "./toon";
import { LIGHTS, LOOK, LightPreset } from "./lights";
import { TONE, CHAR, untone, twoTone } from "./shade";
import { NOINK } from "./ink";
import { Pool, Actor, Fx, Stage, CamInfo, V3, FPS, person, blob, lidAt, glide, clamp01, Quem, tier, q } from "./elenco";

export type Luz = "day" | "golden";
export type Cam = { pos: V3; look: V3; fov: number; roll?: number };
export type ChaveCam = Cam & { f: number };

/** trilho de câmera: desliza (smootherstep) de uma chave pra outra; `cut: true` na chave = corte seco nela.
 *  `empurra` = fração por quadro que a câmera anda na direção do alvo o tempo todo (nenhum plano fica parado). */
export const trilho = (chaves: (ChaveCam & { cut?: boolean })[], empurra = 0.0012) => (f: number): Cam => {
  let i = 0;
  while (i < chaves.length - 1 && f >= chaves[i + 1].f) i++;
  const a = chaves[i], b = chaves[Math.min(i + 1, chaves.length - 1)];
  const u = b === a || b.cut ? 0 : glide((f - a.f) / Math.max(1, b.f - a.f));
  const L = (x: number, y: number) => x + (y - x) * u;
  const pos: V3 = [L(a.pos[0], b.pos[0]), L(a.pos[1], b.pos[1]), L(a.pos[2], b.pos[2])];
  const look: V3 = [L(a.look[0], b.look[0]), L(a.look[1], b.look[1]), L(a.look[2], b.look[2])];
  const k = Math.min(0.25, empurra * (f - chaves[0].f));
  for (let j = 0; j < 3; j++) pos[j] += (look[j] - pos[j]) * k;
  return { pos, look, fov: L(a.fov, b.fov), roll: L(a.roll ?? 0, b.roll ?? 0) };
};

/** enquadra um alvo: câmera a `dist` metros dele, girada `az` graus (0 = de frente, olhando pra -z; negativo = câmera à
 *  esquerda) e erguida `el` graus (negativo = câmera baixa olhando pra cima). O alvo fica no centro do quadro.
 *  Conta rápida do vertical: altura visível = 2·dist·tan(fov/2); largura = 0,5625 × isso. */
export const mira = (alvo: V3, dist: number, az: number, el: number, fov: number, roll = 0): Cam => {
  const a = (az * Math.PI) / 180, e = (el * Math.PI) / 180;
  return { pos: [alvo[0] + dist * Math.sin(a) * Math.cos(e), alvo[1] + dist * Math.sin(e), alvo[2] + dist * Math.cos(a) * Math.cos(e)], look: alvo, fov, roll };
};
/** chave de trilho: quadro + enquadramento */
export const K = (f: number, c: Cam, cut = false): ChaveCam & { cut?: boolean } => ({ f, ...c, cut });

/** formatos fora do RL (IN 1080x1350, GL 1080x1080, YT 1920x1080; 12/11/2026): qw x qh = canvas do formato; bw x bh = banda
 *  onde a animação aparece, no MIOLO do canvas (= canvas no modo A; faixa de cima no D do IN/GL; coluna da esquerda no
 *  D do YT); faixaRL = divY do RL (a camD foi desenhada pra faixa 1080 x faixaRL). */
export type GeoFmt = { qw: number; qh: number; bw: number; bh: number; faixaRL: number };

export type Tomada = {
  id: string; a: number; b: number; luz: Luz;
  cam: (f: number) => Cam;
  /** câmera da TELA DIVIDIDA (animação na faixa 1080x960 de cima): mesmo formato, mas o fov é o vertical DA FAIXA
   *  (altura visível = 2·dist·tan(fov/2); largura = 1,125 × isso: cabe coisa lado a lado). Sem camD, a dividida mostra
   *  o miolo (metade da altura) do enquadramento vertical. */
  camD?: (f: number) => Cam;
  /** desfoque de lente: cInf em px a 1080 (0 = tudo nítido). Foco = `foco` ou o alvo da câmera. */
  dof?: number; foco?: (f: number) => V3;
  /** sol relativo à câmera: az 0 = contraluz, +90 = vindo da direita da tela; el = elevação */
  sunAz?: number; sunEl?: number;
  /** trancos de impacto (quadros): a câmera treme invertendo o sinal a cada quadro por 7 quadros */
  trancos?: number[];
  /** (opcional, vídeo só animação) segundos em que entra uma ação nova na tomada: o motor confere que nenhuma tomada
   *  longa (> 5,7 s) fica mais de 4 s sem ação nova (ver conferirTomadas em Viral.tsx) */
  acoes?: number[];
  /** (opcional, 17/11/2026) multiplica a distância da névoa (perto e longe) só nesta tomada: > 1 pra zoom out bem
   *  aberto (ex.: 3 = névoa 3x mais longe), sem lavar o fundo */
  nevoa?: number;
  palco: (c: Ctx) => void;
};

export type OpGente = {
  modo?: FrontOpts["mode"]; expr?: Expr; olhar?: number; fase?: number; tilt?: number; cabeca?: number; aceno?: number; prop?: Prop;
  /** frente (padrão), 3/4 pra direita/esquerda da tela, ou perfil andando pra direita/esquerda */
  vista?: "frente" | "3/4D" | "3/4E" | "perfilD" | "perfilE";
  modoPerfil?: SideOpts["mode"]; pose?: number; passo?: number;
  escala?: number; sombra?: boolean; trocas?: number[]; lift?: number;
};

export type Ctx = {
  t: number; f: number; tom: Tomada; cam: CamInfo; st: Stage;
  /** personagem do elenco (cabeça de feijão) em pé no chão em (x, y, z) */
  gente: (who: Quem, x: number, y: number, z: number, o?: OpGente) => void;
  /** personagem desenhado à mão (robô etc.) numa carta 600 x 1000 iluminada pela cena */
  boneco: (key: string, draw: (p: Pen) => void, x: number, y: number, z: number, o?: { escala?: number; espelho?: boolean; sombra?: boolean; roll?: number }) => void;
  /** carta de efeito 2D (sem luz) de frente pra câmera; flat = deitada no chão; soft = translúcida */
  carta: (key: string, cw: number, ch: number, draw: (p: Pen) => void, x: number, y: number, z: number, w: number, h: number, o?: { flat?: boolean; rot?: number; soft?: boolean; yaw?: number }) => void;
  sombra: (x: number, y: number, z: number, sc?: number, k?: number) => void;
  /** objeto 3D dinâmico registrado em `construir` (fica visível só nos quadros em que é pedido) */
  obj: (nome: string) => THREE.Object3D;
};

export type Filme = {
  total: number;
  tomadas: Tomada[];
  /** monta o cenário fixo em `root` e registra os objetos dinâmicos em `dyn` (por nome) */
  construir: (root: THREE.Group, dyn: Record<string, THREE.Object3D>) => void;
};

export const tomadaEm = (filme: Filme, f: number) => filme.tomadas.find((s) => f >= s.a && f < s.b) ?? null;

const discTex = () => {
  const c = document.createElement("canvas"); c.width = c.height = 128;
  const g = c.getContext("2d")!;
  const gr = g.createRadialGradient(64, 64, 58, 64, 64, 64); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
};

/** material fosco em dois tons (cor chapada) pra objetos dinâmicos e cenário simples */
const matCache = new Map<string, THREE.MeshLambertMaterial>();
export const tinta = (cor: string, extra: THREE.MeshLambertMaterialParameters = {}) => {
  const key = cor + JSON.stringify(Object.keys(extra));
  let m = matCache.get(key);
  if (!m || extra.map) { m = twoTone(new THREE.MeshLambertMaterial({ color: cor, ...extra })); if (!extra.map) matCache.set(key, m); }
  return m;
};
/** malha dinâmica com sombra (caixa, cilindro...) */
export const peca = (geo: THREE.BufferGeometry, mat: THREE.Material) => {
  const m = new THREE.Mesh(geo, mat);
  m.castShadow = true; m.receiveShadow = true;
  return m;
};

export class Mundo {
  root = new THREE.Group();
  dyn: Record<string, THREE.Object3D> = {};
  private pool = new Pool();
  private actors: Actor[] = [];
  private fxs: Fx[] = [];
  private hemi: THREE.HemisphereLight; private sun: THREE.DirectionalLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#bccbec", 25, 420);
  private sunDisc: THREE.Sprite;
  private sunCache = new Map<string, THREE.Vector3>();
  private cloudMaps: Record<Luz, THREE.Texture[]>;
  private clouds: THREE.Mesh[] = [];
  private frustum = new THREE.Frustum();
  private m4 = new THREE.Matrix4(); private v = new THREE.Vector3(); private sph = new THREE.Sphere();

  constructor(private filme: Filme) {
    const R = this.root;
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() },
        c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el));
          c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el));
          c = mix(c, c4, smoothstep(e.z, e.w, el));
          gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(1100, 48, 24), this.skyMat);
    this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK);
    R.add(this.sky);
    this.sunDisc = new THREE.Sprite(new THREE.SpriteMaterial({ map: discTex(), color: new THREE.Color(6.0, 4.4, 2.4), fog: false, depthWrite: false }));
    this.sunDisc.renderOrder = -0.5; this.sunDisc.frustumCulled = false; this.sunDisc.layers.set(NOINK); R.add(this.sunDisc);
    this.hemi = new THREE.HemisphereLight("#cfe6ff", "#6c5c8c", 1.1);
    this.sun = new THREE.DirectionalLight("#fff0d6", 2.6);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(4096, 4096);
    R.add(this.hemi, this.sun, this.sun.target);
    this.cloudMaps = { day: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.day.cloud)), golden: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.golden.cloud)) };
    for (let i = 0; i < 9; i++) {
      const a = (i / 9) * Math.PI * 2 + 0.3, d = 620 + (i % 3) * 60;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: this.cloudMaps.day[i % 4], color: new THREE.Color(1.1, 1.1, 1.1), transparent: true, depthWrite: false, fog: false }));
      const w = 130 + (i % 4) * 30;
      m.position.set(Math.cos(a) * d, 120 + (i % 4) * 38, Math.sin(a) * d); m.scale.set(w, w / 2, 1);
      m.layers.set(NOINK);
      this.clouds.push(m); R.add(m);
    }
    filme.construir(R, this.dyn);
    for (const o of Object.values(this.dyn)) { o.visible = false; if (!o.parent) R.add(o); }
  }

  /** sol relativo à câmera, congelado por tomada: direção média da tomada girada de az pra direita da tela, erguida de el */
  private shotSun(s: Tomada, L: LightPreset, comD: boolean) {
    const chave = s.id + (comD && s.camD ? "|D" : ""), camDe = comD && s.camD ? s.camD : s.cam;
    let v = this.sunCache.get(chave);
    if (v) return v;
    let fx = 0, fz = 0;
    for (let f = s.a; f < s.b; f += 3) {
      const c = camDe(f), x = c.look[0] - c.pos[0], z = c.look[2] - c.pos[2], n = Math.hypot(x, z) || 1;
      fx += x / n; fz += z / n;
    }
    const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
    const az = THREE.MathUtils.degToRad(s.sunAz ?? L.az), el = THREE.MathUtils.degToRad(s.sunEl ?? L.el);
    const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
    v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize();
    this.sunCache.set(chave, v);
    return v;
  }

  /** REGRA DO USUÁRIO (12/11/2026): texto nunca lá em cima (o Instagram tampa), nunca baixo demais. No RL o topo de
   *  qualquer placa fica a >= 320 px do topo e a base acima de 1500 px; na dividida, entre y 320 e (faixa - 60) da faixa de cima;
   *  e a >= 100 px das laterais. Placa = carta cuja chave começa com "placa|". Avisa no console (fotos com A3D_LOG=1).
   *  IN/GL/YT (12/11): topo >= 200 (IN) / 160 (GL, YT), base a >= 150 px do pé (60 na dividida), 100 px das laterais da banda.
   *  Fora do RL a banda mostra mais dos lados do que foi desenhado: placa CORTADA pela borda da banda some (texto pela
   *  metade na borda parece erro; a que fica inteira fora já não aparece). */
  private conferirTexto(st: Stage, cam: THREE.PerspectiveCamera, g: GeoFmt, f: number) {
    const div = g.bw < g.qw || g.bh < g.qh, rl = g.qw === 1080 && g.qh === 1920;
    const topo = rl ? 320 : g.qh >= 1300 ? 200 : 160, pe = rl && !div ? 1500 : g.bh - (div ? 60 : 150);
    const cortadas = new Set<object>();
    for (const p of st.fx) {
      if (!p.key.startsWith("placa|")) continue;
      const yaw = p.yaw ?? 0, ex = Math.cos(yaw), ez = -Math.sin(yaw);
      let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
      for (const [a, b] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) {
        this.v.set(p.x + (a * p.w * ex) / 2, p.y + (b * p.h) / 2, p.z + (a * p.w * ez) / 2).project(cam);
        const px = ((this.v.x + 1) / 2) * g.qw - (g.qw - g.bw) / 2, py = ((1 - this.v.y) / 2) * g.qh - (g.qh - g.bh) / 2;
        x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py);
      }
      const ruim = y0 < topo || y1 > pe || x0 < 100 || x1 > g.bw - 100;
      const corta = (a: number, b: number, lim: number) => a < lim && b > lim;
      if (!rl && (corta(x0, x1, 0) || corta(x0, x1, g.bw) || corta(y0, y1, 0) || corta(y0, y1, g.bh))) { cortadas.add(p); continue; }
      if (ruim) console.warn(`[texto-fora] q${f} ${p.key.split("|")[1]} ${div ? "D" : "A"} ${g.qw}x${g.qh} topo ${Math.round(y0)} base ${Math.round(y1)} esq ${Math.round(x0)} dir ${Math.round(g.bw - x1)}`);
    }
    if (cortadas.size) st.fx.splice(0, st.fx.length, ...st.fx.filter((p) => !cortadas.has(p)));
  }

  private actor(i: number) { while (this.actors.length <= i) this.actors.push(new Actor(this.root)); return this.actors[i]; }
  private fx(i: number) { while (this.fxs.length <= i) this.fxs.push(new Fx(this.root)); return this.fxs[i]; }

  /** posa tudo pro quadro f; devolve o ponto de foco (ou null fora das tomadas: trecho do apresentador).
   *  dividida = a animação vai aparecer só na faixa 1080x960 do MEIO do canvas (o Filme3D sobe essa faixa pro topo):
   *  usa a camD da tomada e abre o fov do canvas pra faixa do meio ter exatamente o fov pedido. */
  update(f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene, faixa = 0, geo?: GeoFmt): { foco: THREE.Vector3; tom: Tomada } | null {
    // faixa = altura em px da animação na dividida (960 padrão; 820 quando a pessoa precisa de mais altura); 0 = tela cheia
    // geo (IN/GL/YT, 12/11): canvas e banda do formato; aí `faixa` é ignorada (ver GeoFmt)
    const dividida = geo ? geo.bw < geo.qw || geo.bh < geo.qh : faixa > 0;
    const s = tomadaEm(this.filme, f);
    if (!s) return null;
    const t = f / FPS, L = LIGHTS[s.luz], K = LOOK[s.luz];
    // ---- câmera ----
    const comD = (geo ? true : dividida) && !!s.camD, c = (comD ? s.camD! : s.cam)(f);
    const tg = (deg: number) => Math.tan(THREE.MathUtils.degToRad(deg) / 2), ang = (x: number) => THREE.MathUtils.radToDeg(2 * Math.atan(x));
    let fov: number, largura = 1;
    if (geo) {
      // fora do RL: o enquadramento desenhado (camD: faixa 1080 x faixaRL; cam: 1080x1920) cabe INTEIRO na banda
      // ("contain": banda mais larga mostra mais dos lados, mais estreita mostra mais em cima/embaixo) e o canvas abre o
      // fov pra banda (o miolo do canvas) ter esse fov
      const aDes = comD ? 1080 / geo.faixaRL : 1080 / 1920, r = geo.bw / geo.bh;
      fov = ang(tg(c.fov) * (r >= aDes ? 1 : aDes / r) * (geo.qh / geo.bh));
      largura = Math.max(1, r / aDes);
    } else {
      // camD: c.fov é o vertical da FAIXA -> o canvas inteiro (1920) precisa de um fov maior na proporção 1920/faixa
      fov = comD ? ang((1920 / faixa) * tg(c.fov)) : c.fov;
    }
    let roll = c.roll ?? 0, dy = 0;
    for (const k of s.trancos ?? []) { const n = f - k; if (n >= 0 && n < 7) { const a = (1 - n / 7) * (n % 2 ? -1 : 1); roll += 0.012 * a; dy += 0.05 * a; } }
    cam.position.set(c.pos[0], c.pos[1] + dy, c.pos[2]); cam.up.set(0, 1, 0); cam.lookAt(c.look[0], c.look[1] + dy, c.look[2]); cam.rotateZ(roll);
    cam.fov = fov; cam.near = 0.2; cam.far = 1500; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const focus = new THREE.Vector3(...c.look), dist = cam.position.distanceTo(focus);
    cam.layers.enable(NOINK);
    // ---- luz: sol relativo à câmera, dois tons, sombra ajustada ao plano ----
    const sunDir = this.shotSun(s, L, comD);
    this.hemi.color.set(L.sky); this.hemi.groundColor.set(L.ground); this.hemi.intensity = L.hemiI;
    this.sun.color.set(L.sunCol); this.sun.intensity = L.sunI;
    let Rr = THREE.MathUtils.clamp((dist * 1.15 + 7) * largura, 12, 95 * largura);   // largura > 1: banda mostra mais dos lados
    if (s.luz === "golden") Rr = Math.max(Rr, 30);
    this.sun.position.copy(focus).addScaledVector(sunDir, 220); this.sun.target.position.copy(focus);
    const sc = this.sun.shadow.camera;
    sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 20; sc.far = 480; sc.updateProjectionMatrix();
    this.sun.shadow.bias = L.bias; this.sun.shadow.normalBias = L.normalBias * (Rr / 12);
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad;
    CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    // ---- céu, névoa (cor do horizonte), sol, nuvens ----
    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg));
    su.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky.position.copy(cam.position);
    untone(L.fog, this.fog.color); this.fog.near = L.fogNear * (s.nevoa ?? 1); this.fog.far = L.fogFar * (s.nevoa ?? 1);
    scene.fog = this.fog; scene.background = null;
    this.sunDisc.visible = s.luz === "golden";
    if (this.sunDisc.visible) {
      this.sunDisc.position.copy(cam.position).addScaledVector(sunDir, 900);
      this.sunDisc.scale.setScalar(2 * 900 * Math.tan(THREE.MathUtils.degToRad(1.7)));
    }
    for (let i = 0; i < this.clouds.length; i++) {
      const m = this.clouds[i], mat = m.material as THREE.MeshBasicMaterial;
      m.lookAt(cam.position.x, m.position.y, cam.position.z);
      mat.map = this.cloudMaps[s.luz][i % 4];
    }
    // ---- palco: objetos dinâmicos, elenco e efeitos ----
    for (const o of Object.values(this.dyn)) o.visible = false;
    const right = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0);
    const info: CamInfo = { pos: cam.position, right };
    defSolDe(sunDir, s.luz);
    const st: Stage = { places: [], fx: [] };
    const ctx: Ctx = {
      t, f, tom: s, cam: info, st,
      gente: (who, x, y, z, o = {}) => {
        const vista = o.vista ?? "frente", side = vista.startsWith("perfil");
        const blink = lidAt(t, who.i, o.trocas);
        const fo: FrontOpts = { mode: o.modo ?? "stand", expr: o.expr ?? "neutral", look: o.olhar ?? 0, blink, phase: o.fase ?? 0, tilt: o.tilt ?? 0,
          headTilt: o.cabeca ?? 0, wave: o.aceno, prop: o.prop ?? null, facing: vista === "3/4D" ? 1 : vista === "3/4E" ? -1 : 0, lift: o.lift ?? 60 };
        const so: SideOpts = { mode: o.modoPerfil ?? "stand", expr: o.expr ?? "neutral", blink, phase: o.fase ?? 0, pose: o.pose ?? 0, stride: o.passo ?? 1, stomp: 1 };
        st.places.push(person(info, who, x, y, z, { side, mirror: vista === "perfilE" }, fo, so, o.escala ?? 1));
        if (o.sombra !== false) blob(st, x, y, z, o.escala ?? 1);
      },
      boneco: (key, draw, x, y, z, o = {}) => {
        const esc = o.escala ?? 1, d = cam.position.distanceTo(this.v.set(x, y + 1.2, z)) / esc;
        st.places.push({ key: `B|${key}`, draw, x, y, z, scale: esc, mirror: o.espelho, roll: o.roll, size: tier(d) });
        if (o.sombra !== false) blob(st, x, y, z, esc);
      },
      carta: (key, cw, ch, draw, x, y, z, w, h, o = {}) => { st.fx.push({ key, cw, ch, draw, x, y, z, w, h, ...o }); },
      sombra: (x, y, z, sc2 = 1, k = 1) => blob(st, x, y, z, sc2, k),
      obj: (nome) => { const o = this.dyn[nome]; if (!o) throw new Error(`animada3d: objeto dinâmico "${nome}" não registrado`); o.visible = true; return o; },
    };
    s.palco(ctx);
    this.conferirTexto(st, cam, geo ?? { qw: 1080, qh: 1920, bw: 1080, bh: dividida ? faixa : 1920, faixaRL: faixa || 960 }, f);
    this.frustum.setFromProjectionMatrix(this.m4.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
    let ai = 0;
    const used: Actor[] = [];
    for (const p of st.places) {
      const sc2 = p.scale ?? 1;
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(p.x, p.y + 1.1 * sc2, p.z), 3.5 * sc2))) continue;
      const a = this.actor(ai++);
      const [w, h, k] = p.size ?? [300, 500, 0.5];
      a.r = this.pool.req(p.key, w, h, k, p.draw);
      a.mesh.visible = true;
      a.mesh.position.set(p.x, p.y, p.z);
      a.mesh.rotation.set(0, p.yaw ?? Math.atan2(cam.position.x - p.x, cam.position.z - p.z), p.roll ?? 0);
      a.mesh.scale.set(p.mirror ? -sc2 : sc2, sc2, sc2);
      a.mesh.castShadow = L.actorShadow;
      used.push(a);
    }
    for (let i = ai; i < this.actors.length; i++) this.actors[i].mesh.visible = false;
    let fi = 0;
    const fused: Fx[] = [];
    for (const p of st.fx) {
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(p.x, p.y, p.z), Math.max(p.w, p.h)))) continue;
      const e2 = this.fx(fi++);
      e2.r = this.pool.req(p.key, p.cw, p.ch, 1, p.draw);
      e2.use(!!p.soft);
      e2.mesh.visible = true;
      e2.mesh.position.set(p.x, p.y, p.z);
      if (p.flat) e2.mesh.rotation.set(-Math.PI / 2, 0, p.rot ?? 0);
      else if (p.yaw !== undefined) e2.mesh.rotation.set(0, p.yaw, p.rot ?? 0);
      else { e2.mesh.quaternion.copy(cam.quaternion); e2.mesh.rotateZ(p.rot ?? 0); }
      e2.mesh.scale.set(p.w, p.h, 1);
      fused.push(e2);
    }
    for (let i = fi; i < this.fxs.length; i++) this.fxs[i].mesh.visible = false;
    this.pool.flush();
    for (const a of used) a.bind();
    for (const e2 of fused) e2.bind();
    return { foco: s.foco ? new THREE.Vector3(...s.foco(f)) : focus, tom: s };
  }
}

import { defSol } from "./elenco";
const defSolDe = (d: THREE.Vector3, l: Luz) => defSol(d, l);
export { clamp01, q };
export type { Outfit };
