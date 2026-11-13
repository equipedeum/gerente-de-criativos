// Tela 3D do estilo "Animada 3D" (personagens 2D num mundo 3D pintado). ADAPTADO de templates/bridge/Bridge.tsx da
// skill claude-animated-shorts (MIT, Mr omi). Cadeia de pós igual à dele: tinta (contorno do mundo, passe próprio) ->
// desfoque de lente (pre + main) -> bloom (só emissivos) -> tone map NEUTRAL -> grade, MSAA 4.
// Diferenças: um canvas só (sem crossfade entre dois mundos), sem kit Kenney (cenário é todo de código), e o filme
// (tomadas + cenário) entra por prop. Fora das tomadas (trechos do apresentador) o canvas fica parado e escondido.
// Modos (ver Viral.tsx): "A" = animação em tela cheia; "D" = tela dividida, a animação ocupa só a faixa de cima
// (1080 x divY; 960 padrão, 820 quando a pessoa precisa de mais altura): o canvas continua 1080x1920, a câmera abre o fov
// e a faixa do MEIO sobe pro topo (sem espremer e sem barra; contorno e desfoque ficam com a mesma espessura em px);
// "T" = só o apresentador, canvas escondido.
import React, { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { AbsoluteFill, getInputProps, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useFrame, useThree } from "@react-three/fiber";
import { BlendFunction, BloomEffect, EffectComposer, EffectPass, RenderPass, ToneMappingEffect, ToneMappingMode } from "postprocessing";
import { InkPass, noInkFallback } from "./ink";
import { LensBlur } from "./lensblur";
import { GradeEffect, GRADES, GRADE_STRENGTH, gradeFor } from "./grade";
import { Mundo, Filme, GeoFmt, tomadaEm } from "./mundo";

type PostToggles = { pos: boolean; ink: boolean; lens: boolean; bloom: boolean; grade: boolean };
const toggles = (): PostToggles => ({ pos: true, ink: true, lens: true, bloom: true, grade: true, ...((getInputProps() as { post?: Partial<PostToggles> }).post ?? {}) });

const makeBloom = () => {
  const b = new BloomEffect({ blendFunction: BlendFunction.ADD, intensity: 0.5, luminanceThreshold: 1.0, luminanceSmoothing: 0.2, mipmapBlur: true, levels: 6, radius: 0.6 });
  const mip = b.mipmapBlurPass;
  const setSize = mip.setSize.bind(mip);
  // espalhamento fixo em px de "1080 no lado curto" (= 1080x1920 no RL; 12/11: IN/GL/YT com o mesmo bloom)
  mip.setSize = (w: number, h: number) => { const k = 1080 / Math.max(Math.min(w, h), 1); setSize(Math.round(w * k), Math.round(h * k)); };
  return b;
};

const fwd = new THREE.Vector3(), fpt = new THREE.Vector3(), tam = new THREE.Vector2();

const Inner: React.FC<{ filme: Filme; modo: "T" | "D" | "A"; divY: number; geo?: GeoFmt }> = ({ filme, modo, divY, geo }) => {
  const f = useCurrentFrame();
  const { camera, scene, gl } = useThree();
  const aplicado = useRef(new THREE.Vector2(-1, -1));
  const mundo = useMemo(() => new Mundo(filme), [filme]);
  const on = useMemo(toggles, []);
  const fx = useMemo(() => ({
    ink: new InkPass(scene, camera as THREE.PerspectiveCamera),
    lens: new LensBlur({ maxCoC: 24, nearScale: 1.2 }),
    bloom: makeBloom(),
    tone: new ToneMappingEffect({ mode: ToneMappingMode.NEUTRAL }),
    grade: new GradeEffect(GRADES.day, GRADE_STRENGTH.day),
  }), [camera, scene]);
  // Compositor montado NA HORA (useMemo), direto com a biblioteca `postprocessing`: o <EffectComposer> do
  // @react-three/postprocessing 3.2 cria o compositor num efeito assíncrono, e no render do Remotion (um quadro por
  // vez, sem laço de animação) o primeiro quadro de cada aba saía vazio.
  const composer = useMemo(() => {
    const c = new EffectComposer(gl, { multisampling: 4, frameBufferType: THREE.HalfFloatType });
    c.addPass(new RenderPass(scene, camera));
    if (on.ink) c.addPass(fx.ink);
    if (on.lens) { c.addPass(new EffectPass(camera, fx.lens.pre)); c.addPass(new EffectPass(camera, fx.lens.main)); }
    const fim = [on.bloom ? fx.bloom : null, fx.tone, on.grade ? fx.grade : null].filter((e) => e !== null);
    c.addPass(new EffectPass(camera, ...fim));
    return c;
  }, [gl, scene, camera, fx, on]);
  useEffect(() => () => composer.dispose(), [composer]);
  useFrame(() => {
    if (!on.pos) { gl.render(scene, camera); return; }
    gl.getSize(tam);
    if (tam.x !== aplicado.current.x || tam.y !== aplicado.current.y) { composer.setSize(tam.x, tam.y); aplicado.current.copy(tam); }
    gl.autoClear = true;
    composer.render();
  }, 1);
  const cam = camera as THREE.PerspectiveCamera;
  const r = modo === "T" ? null : mundo.update(f, cam, scene, modo === "D" ? divY : 0, geo);
  if (r) {
    noInkFallback(mundo.root);
    cam.getWorldDirection(fwd);
    fpt.copy(r.foco);
    fx.lens.focus = Math.max(0.3, fpt.sub(cam.position).dot(fwd));
    fx.lens.cInf = r.tom.dof ?? 0;
    gradeFor(fx.grade, r.tom.luz);
  }
  return (
    <>
      <primitive object={mundo.root} dispose={null} />
    </>
  );
};

export type Banda = { x: number; y: number; w: number; h: number };

/** A animação 3D: tela cheia no modo "A", faixa de cima no modo "D", invisível no "T" e nos quadros sem tomada.
 *  RL: canvas 1080x1920, a dividida é a faixa 1080 x divY. IN/GL/YT (12/11): canvas largura x altura do formato e
 *  `bandaD` = onde a animação fica na dividida (faixa de cima no IN/GL, coluna da esquerda no YT); a banda mostra o
 *  MIOLO do canvas (o mundo abre o fov pra isso, ver GeoFmt). */
export const Filme3D: React.FC<{ filme: Filme; modo?: "T" | "D" | "A"; divY?: number; largura?: number; altura?: number; bandaD?: Banda }> = ({ filme, modo = "A", divY = 960, largura = 1080, altura = 1920, bandaD }) => {
  const f = useCurrentFrame();
  const ativo = modo !== "T" && !!tomadaEm(filme, f), div = modo === "D";
  const b: Banda = div ? bandaD ?? { x: 0, y: 0, w: largura, h: divY } : { x: 0, y: 0, w: largura, h: altura };
  const geo: GeoFmt | undefined = bandaD ? { qw: largura, qh: altura, bw: b.w, bh: b.h, faixaRL: divY } : undefined;
  return (
    <AbsoluteFill style={{ visibility: ativo ? "visible" : "hidden" }}>
      <div style={{ position: "absolute", left: b.x, top: b.y, width: b.w, height: b.h, overflow: "hidden", background: "#cfe3f2" }}>
        <div style={{ position: "absolute", left: -(largura - b.w) / 2, top: -(altura - b.h) / 2, width: largura, height: altura }}>
          <ThreeCanvas width={largura} height={altura} shadows gl={{ antialias: false, stencil: false, powerPreference: "high-performance", toneMappingExposure: 1.0 }}
            camera={{ fov: 40, near: 0.2, far: 1500 }}>
            <Inner filme={filme} modo={modo} divY={divY} geo={geo} />
          </ThreeCanvas>
        </div>
      </div>
    </AbsoluteFill>
  );
};
