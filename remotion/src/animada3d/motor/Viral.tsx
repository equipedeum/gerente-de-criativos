// Estrutura padrão do estilo "Animação viral" (desde 11/11/2026): o vídeo alterna 3 MODOS, com corte a cada 3–5 s,
// sempre em início/fim de frase:
//   T = pessoa em tela cheia, com legenda simples de 1 linha (a única que tem legenda);
//   D = tela dividida: animação 3D em cima (1080 x divY, com câmera própria `camD` da tomada), pessoa embaixo
//       (1080 x (1920 - divY)), sem legenda. divY = 960 padrão; 820 quando a fonte é um close (rosto enchendo a faixa,
//       cabelo na divisória, sem ombro: g22, igual à GEO_V_RL do Extremo);
//   A = animação 3D em tela cheia, sem legenda.
// Cada vídeo só entrega os DADOS (trechos, arquivos, legenda, sons); a montagem é esta aqui.
// Formatos (12/11/2026): prop `formato` RL (padrão) | IN 1080x1350 | GL 1080x1080 | YT 1920x1080, com os mesmos trechos;
// fora do RL a dividida usa a geometria FMT (IN/GL: animação em cima; YT: animação à esquerda, pessoa à direita) e a
// animação usa a camD da tomada enquadrada "contain" na banda (ver GeoFmt em mundo.ts). Recortes da pessoa por formato:
// remotion/scripts/pessoa_formatos_animada3d.py (fonte 16:9).
// A COR DO PESSOA NÃO MUDA: os vídeos dele entram sem filtro nenhum, e o render leva --color-space=bt709.
// SÓ ANIMAÇÃO (12/11/2026, piloto só de animação): `soAnimacao: true` = o vídeo inteiro é A (sem pessoa, sem trechos);
// a conferência passa a ser das TOMADAS: troca só em início/fim de frase (`frases`) e nenhuma tomada > ~5,7 s sem
// ação nova (`acoes` da tomada). `legendaEmA: true` = legenda simples de 1 linha também na animação (y `legendaAY`).
// Tudo opcional: os vídeos da pessoa (g22, t96, t112, b53b) continuam iguais.
import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, continueRender, delayRender, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/fonts";
import { Filme3D } from "./Filme";
import { Filme } from "./mundo";

export type Modo = "T" | "D" | "A";
/** [início s, fim s, modo]; os trechos têm que cobrir o vídeo inteiro, sem buraco */
export type Trecho = [number, number, Modo];
export type DadosViral = {
  filme: Filme;
  /** obrigatório nos vídeos com a pessoa; no `soAnimacao` o motor usa um trecho A só, do começo ao fim */
  trechos?: Trecho[];
  /** arquivos em remotion/public-animada3d/: pessoa 1080x1920, pessoa 1080 x (1920 - divY) (rosto inteiro com folga
   *  acima do cabelo e ombros; gerar com remotion/scripts/pessoa_dividido_animada3d.py) e a voz */
  pessoaCheio?: string; pessoaDividido?: string; voz: string;
  /** vídeo 100% animação (sem pessoa): tudo A, conferência por tomada (ver conferirTomadas) */
  soAnimacao?: boolean;
  /** [início s, fim s] de cada frase/ideia da fala: a troca de tomada só pode cair fora delas (início/fim/pausa) */
  frases?: [number, number][];
  /** legenda de 1 linha também nos trechos A (no soAnimacao, o vídeo todo), centrada em y = legendaAY (padrão 1430) */
  legendaEmA?: boolean; legendaAY?: number;
  /** legenda (só aparece nos trechos T): [início s, fim s, texto de 1 linha] */
  legenda: [number, number, string][];
  /** efeitos sonoros: [segundo, arquivo em sfx/ sem extensão, volume]; os que caem em trecho T são descartados (sem evento visível) */
  sfx: [number, string, number][];
  /** onde a dividida corta: a animação ocupa 0..divY e a pessoa divY..1920 (padrão 960) */
  divY?: number;
  /** y do centro da legenda na pessoa cheio (abaixo do queixo) */
  legendaY?: number;
  /** IN/GL/YT (12/11/2026): pessoa cheia no tamanho do formato e pessoa da dividida no tamanho do slot (ver FMT), sem filtro.
   *  `trocar`: troca de modo SÓ nesse formato (fonte de celular vertical, rosto ~52 % da largura: a faixa baixa da dividida
   *  do IN/GL vira close e o 16:9 do YT cortaria a cabeça) — ex.: IN/GL {D: "A"} (animação cheia no lugar da dividida);
   *  YT {T: "L"} (lado a lado: a frase da legenda grande à esquerda + a pessoa na coluna da direita). */
  formatos?: Partial<Record<Exclude<Formato, "RL">, { cheio?: string; dividido?: string; trocar?: Partial<Record<Modo, ModoFmt>> }>>;
};
/** modo efetivo num formato: os 3 do RL + "L" (YT lado a lado com a frase grande à esquerda, ver `trocar`) */
export type ModoFmt = Modo | "L";

export type Formato = "RL" | "IN" | "GL" | "YT";
type Ret = { x: number; y: number; w: number; h: number };
/** geometria dos formatos fora do RL (a mesma do Editor Extremo): banda = animação na dividida, slot = pessoa na dividida,
 *  legY/legPx = legenda da pessoa cheio (altura padrão de cada formato: nunca mudar) */
export const FMT: Record<Exclude<Formato, "RL">, { w: number; h: number; banda: Ret; slot: Ret; legY: number; legPx: number }> = {
  IN: { w: 1080, h: 1350, banda: { x: 0, y: 0, w: 1080, h: 702 }, slot: { x: 0, y: 702, w: 1080, h: 648 }, legY: 1040, legPx: 50 },
  GL: { w: 1080, h: 1080, banda: { x: 0, y: 0, w: 1080, h: 560 }, slot: { x: 0, y: 560, w: 1080, h: 520 }, legY: 905, legPx: 46 },
  YT: { w: 1920, h: 1080, banda: { x: 0, y: 0, w: 1170, h: 1080 }, slot: { x: 1170, y: 0, w: 750, h: 1080 }, legY: 960, legPx: 48 },
};

const FPS = 30;
const Q = (t: number) => Math.round(t * FPS);
export const modoEm = (trechos: Trecho[], f: number): Modo => (trechos.find(([a, b]) => f >= Q(a) && f < Q(b)) ?? trechos[trechos.length - 1])[2];

/** confere a regra dos modos e avisa no log do render (não derruba o render) */
export const conferirTrechos = (trechos: Trecho[], total: number) => {
  const av: string[] = [];
  trechos.forEach(([a, b, m], i) => {
    if (i && Q(a) !== Q(trechos[i - 1][1])) av.push(`buraco/sobreposição em ${a}s`);
    if (i && m === trechos[i - 1][2]) av.push(`modo ${m} repetido em ${a}s`);
    if (b - a > 5.7) av.push(`trecho ${a}–${b}s tem ${(b - a).toFixed(1)} s (máx. ~5 s)`);
  });
  if (trechos.length && (Q(trechos[0][0]) !== 0 || Q(trechos[trechos.length - 1][1]) !== total)) av.push("os trechos não cobrem o vídeo inteiro");
  const soma = (m: Modo) => trechos.filter((t) => t[2] === m).reduce((s, t) => s + t[1] - t[0], 0);
  console.log(`[animacao-viral] T ${soma("T").toFixed(1)} s · D ${soma("D").toFixed(1)} s · A ${soma("A").toFixed(1)} s` + (av.length ? " · AVISOS: " + av.join("; ") : ""));
  return av;
};

/** conferência do vídeo SÓ ANIMAÇÃO: as tomadas cobrem o vídeo sem buraco; cada troca de tomada cai fora do miolo das
 *  frases (folga de 0,15 s pra dentro do começo/fim); tomada > 5,7 s só passa com `acoes` sem intervalo > 4 s */
export const conferirTomadas = (filme: Filme, frases: [number, number][]) => {
  const av: string[] = [], tm = filme.tomadas, FOLGA = 0.15;
  tm.forEach((s, i) => {
    if (i && s.a !== tm[i - 1].b) av.push(`buraco/sobreposição na tomada ${s.id}`);
    const t = s.a / FPS;
    if (i && frases.some(([a, b]) => t > a + FOLGA && t < b - FOLGA)) av.push(`troca no meio da frase em ${t.toFixed(2)} s (${s.id})`);
    const dur = (s.b - s.a) / FPS;
    if (dur > 5.7) {
      const m = [s.a / FPS, ...(s.acoes ?? []), s.b / FPS].sort((x, y) => x - y);
      const gap = Math.max(...m.slice(1).map((x, j) => x - m[j]));
      if (gap > 4) av.push(`tomada ${s.id} tem ${dur.toFixed(1)} s e ${gap.toFixed(1)} s sem ação nova (máx. 4 s)`);
    }
  });
  if (tm.length && (tm[0].a !== 0 || tm[tm.length - 1].b !== filme.total)) av.push("as tomadas não cobrem o vídeo inteiro");
  const maior = Math.max(...tm.map((s) => s.b - s.a)) / FPS;
  console.log(`[animacao-viral] só animação · ${tm.length} tomadas · maior ${maior.toFixed(1)} s` + (av.length ? " · AVISOS: " + av.join("; ") : ""));
  return av;
};

type TrechoF = [number, number, ModoFmt];
const modoFEm = (trechos: TrechoF[], f: number): ModoFmt => (trechos.find(([a, b]) => f >= Q(a) && f < Q(b)) ?? trechos[trechos.length - 1])[2];

/** YT lado a lado ("L"): a frase da legenda grande no painel da esquerda (céu claro do mundo 3D), entrando com um pop curto */
const PainelFrase: React.FC<{ d: DadosViral; trechos: TrechoF[] }> = ({ d, trechos }) => {
  const f = useCurrentFrame(), t = f / FPS;
  if (modoFEm(trechos, f) !== "L") return null;
  const b = d.legenda.find(([a, e]) => t >= a && t < e);
  const ban = FMT.YT.banda;
  const k = b ? Math.min(1, (t - b[0]) / 0.18) : 1, e = 1 - Math.pow(1 - k, 3);
  return (
    <div style={{ position: "absolute", left: ban.x, top: ban.y, width: ban.w, height: ban.h, background: "linear-gradient(180deg, #cfe3f2 0%, #e9f2f8 55%, #f6efe2 100%)" }}>
      {b && <div style={{ position: "absolute", left: 110, right: 110, top: "50%", transform: `translateY(-50%) scale(${0.92 + 0.08 * e})`, opacity: e, textAlign: "center",
        fontFamily: '"TikTok Sans", sans-serif', fontWeight: 800, fontSize: 84, lineHeight: 1.12, color: "#16202c", letterSpacing: -1 }}>{b[2]}</div>}
    </div>
  );
};

const Legenda: React.FC<{ d: DadosViral; formato: Formato; trechos: TrechoF[] }> = ({ d, formato, trechos }) => {
  const f = useCurrentFrame(), t = f / FPS;
  if (modoFEm(trechos, f) !== "T") return null;
  const b = d.legenda.find(([a, e]) => t >= a && t < e);
  if (!b) return null;
  const g = formato === "RL" ? null : FMT[formato];
  return (
    <div style={{ position: "absolute", left: g ? g.w / 2 : 540, top: g ? g.legY : d.legendaY ?? 1196, transform: "translate(-50%, -50%)", whiteSpace: "nowrap", fontFamily: '"TikTok Sans", sans-serif',
      fontWeight: 650, fontSize: g ? g.legPx : 54, lineHeight: 1.1, color: "#fff", textShadow: "0 2px 10px rgba(0,0,0,.55), 0 1px 2px rgba(0,0,0,.5)" }}>
      {b[2]}
    </div>
  );
};

/** legenda nos trechos A (opcional, `legendaEmA`): 1 linha, branca, sombra leve, sem animação, abaixo dos personagens */
const LegendaA: React.FC<{ d: DadosViral; trechos: TrechoF[] }> = ({ d, trechos }) => {
  const f = useCurrentFrame(), t = f / FPS;
  if (!d.legendaEmA || modoFEm(trechos, f) !== "A") return null;
  const b = d.legenda.find(([a, e]) => t >= a && t < e);
  if (!b) return null;
  return (
    <div style={{ position: "absolute", left: 540, top: d.legendaAY ?? 1430, transform: "translate(-50%, -50%)", whiteSpace: "nowrap", fontFamily: '"TikTok Sans", sans-serif',
      fontWeight: 650, fontSize: 54, lineHeight: 1.1, color: "#fff", textShadow: "0 2px 10px rgba(0,0,0,.6), 0 1px 3px rgba(0,0,0,.55)" }}>
      {b[2]}
    </div>
  );
};

export const AnimacaoViral: React.FC<{ d: DadosViral; formato?: Formato }> = ({ d, formato = "RL" }) => {
  const f = useCurrentFrame();
  const base: Trecho[] = d.soAnimacao ? [[0, d.filme.total / FPS, "A"]] : d.trechos ?? [];
  const [pronto, setPronto] = useState(false);
  const [h] = useState(() => delayRender("fonte animacao-viral"));
  useEffect(() => {
    if (d.soAnimacao) conferirTomadas(d.filme, d.frases ?? []);
    else conferirTrechos(base, d.filme.total);
    loadFont({ family: "TikTok Sans", url: staticFile("fontes/TikTokSans-Variable.ttf"), weight: "300 900" })
      .then(() => { setPronto(true); continueRender(h); });
  }, [h, d]);
  if (!pronto) return null;
  const divY = d.divY ?? 960;
  const g = formato === "RL" ? null : FMT[formato], arq = g ? d.formatos?.[formato as Exclude<Formato, "RL">] : null;
  if (g && !arq) throw new Error(`animacao-viral: faltam os vídeos da pessoa do formato ${formato} (DadosViral.formatos)`);
  const trocar = arq?.trocar ?? {};
  const trechos: TrechoF[] = base.map(([a, b, m]) => [a, b, trocar[m] ?? m]);
  const usados = new Set(trechos.map((x) => x[2]));
  const cheio = arq ? arq.cheio : d.pessoaCheio, dividido = arq ? arq.dividido : d.pessoaDividido;
  if ((usados.has("T") && !cheio) || ((usados.has("D") || usados.has("L")) && !dividido)) throw new Error(`animacao-viral: falta o vídeo da pessoa (cheio/dividido) do formato ${formato}`);
  const modoF = modoFEm(trechos, f), modo: Modo = modoF === "L" ? "T" : modoF;   // "L": sem animação 3D (painel da frase)
  const W = g ? g.w : 1080, H = g ? g.h : 1920, slot = g ? g.slot : { x: 0, y: divY, w: 1080, h: 1920 - divY };
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Filme3D filme={d.filme} modo={modo} divY={divY} largura={W} altura={H} bandaD={g ? g.banda : undefined} />
      <PainelFrase d={d} trechos={trechos} />
      {trechos.map(([a, b, m]) => m === "A" ? null : (
        <Sequence key={a} from={Q(a)} durationInFrames={Q(b) - Q(a)}>
          {m === "T"
            ? <OffthreadVideo src={staticFile(cheio!)} trimBefore={Q(a)} muted style={{ position: "absolute", left: 0, top: 0, width: W, height: H }} />
            : <OffthreadVideo src={staticFile(dividido!)} trimBefore={Q(a)} muted style={{ position: "absolute", left: slot.x, top: slot.y, width: slot.w, height: slot.h }} />}
        </Sequence>
      ))}
      <Legenda d={d} formato={formato} trechos={trechos} />
      <LegendaA d={d} trechos={trechos} />
      <Audio src={staticFile(d.voz)} />
      {d.sfx.filter(([s]) => !["T", "L"].includes(modoFEm(trechos, Q(s)))).map(([s, nome, vol], i) => (
        <Sequence key={i} from={Q(s)}>
          <Audio src={staticFile(`sfx/${nome}.wav`)} volume={vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
