// Biblioteca de recortes do estilo papel. Todas as peças recebem tempos em SEGUNDOS ABSOLUTOS.
// Posição: `Peca` coloca o filho com o centro em (x, y) do painel de cima (1080 x 960).
import React, {useId} from 'react';
import {Easing, staticFile} from 'remotion';
import {COR, FONTE, SOMBRA, SOMBRA_CARTAO} from './estilo';
import {MOLAS, lerp, mola, rampa, recorteRasgado, useT} from './tempo';

export type Entrada = 'pop' | 'desliza' | 'cai' | 'carimbo' | 'cresce' | 'revela' | 'fade' | 'nada';
export type Passo = {t: number; x?: number; y?: number; escala?: number; rot?: number};

type PecaProps = {
  x: number;
  y: number;
  t: number;
  entrada?: Entrada;
  de?: 'esq' | 'dir' | 'cima' | 'baixo';
  rot?: number;
  escala?: number;
  sai?: number;
  saida?: 'encolhe' | 'cai' | 'voa' | 'some';
  sombra?: boolean;
  ancora?: 'centro' | 'base' | 'topoEsq';
  origem?: string; // transform-origin (ex.: '0% 50%' pra placa girar presa no poste)
  move?: Passo[];
  z?: number;
  carimboDe?: number; // escala inicial do 'carimbo' (padrão 2,6); menor perto da borda pra não sair da tela
  children: React.ReactNode;
};

export const Peca: React.FC<PecaProps> = ({
  x, y, t, entrada = 'pop', de = 'baixo', rot = 0, escala = 1, sai, saida = 'encolhe', sombra = true,
  ancora = 'centro', origem, move, z, carimboDe = 2.6, children,
}) => {
  const {t: agora, frame, fps} = useT();
  if (agora < t) return null;
  if (sai !== undefined && saida === 'some' && agora >= sai) return null;

  let cx = x, cy = y, s = escala, r = rot;
  for (const p of move ?? []) {
    if (agora < p.t) break;
    const k = mola(frame, fps, p.t, MOLAS.suave);
    cx = lerp(cx, p.x ?? cx, k);
    cy = lerp(cy, p.y ?? cy, k);
    s = lerp(s, p.escala ?? s, k);
    r = lerp(r, p.rot ?? r, k);
  }

  let dx = 0, dy = 0, sx = 1, sy = 1, op = 1;
  let clip: string | undefined;
  if (entrada === 'pop') {
    const k = mola(frame, fps, t, MOLAS.pop);
    sx = sy = k;
  } else if (entrada === 'desliza') {
    const k = mola(frame, fps, t, MOLAS.suave);
    const d = 160 * (1 - k);
    if (de === 'esq') dx = -d;
    if (de === 'dir') dx = d;
    if (de === 'cima') dy = -d;
    if (de === 'baixo') dy = d;
    op = rampa(agora, t, 0.1);
  } else if (entrada === 'cai') {
    const k = mola(frame, fps, t, MOLAS.queda);
    dy = -110 * (1 - k);
    r += -16 * (1 - k);
    op = rampa(agora, t, 0.06);
  } else if (entrada === 'carimbo') {
    const p = rampa(agora, t, 0.13, Easing.in(Easing.quad));
    sx = sy = lerp(carimboDe, 1, p);
    op = Math.min(1, p * 2.5);
    const pos = agora - (t + 0.13);
    if (pos > 0) sx = sy = 1 - 0.07 * Math.exp(-pos * 16) * Math.cos(pos * 38);
  } else if (entrada === 'cresce') {
    sy = mola(frame, fps, t, {damping: 15, stiffness: 120, mass: 0.9});
  } else if (entrada === 'revela') {
    const p = rampa(agora, t, 0.35);
    clip = `inset(0 ${(1 - p) * 100}% 0 0)`;
  } else if (entrada === 'fade') {
    op = rampa(agora, t, 0.25);
  }

  if (sai !== undefined && agora >= sai) {
    const q = mola(frame, fps, sai, MOLAS.firme);
    if (saida === 'encolhe') {
      sx *= 1 - q;
      sy *= 1 - q;
      if (q > 0.98) return null;
    } else {
      const dt = agora - sai;
      if (saida === 'cai') {
        dy += 1400 * dt * dt + 60 * dt;
        r += 50 * dt;
      } else {
        dy -= 1500 * dt * dt + 200 * dt;
      }
      if (dt > 1.2) return null;
    }
  }

  const tr = ancora === 'topoEsq' ? 'translate(0,0)' : ancora === 'base' ? 'translate(-50%,-100%)' : 'translate(-50%,-50%)';
  const origemPadrao = ancora === 'base' || entrada === 'cresce' ? '50% 100%' : ancora === 'topoEsq' ? '0% 0%' : '50% 50%';
  return (
    <div
      style={{
        position: 'absolute',
        left: cx,
        top: cy,
        zIndex: z,
        transform: `${tr} translate(${dx}px, ${dy}px) rotate(${r}deg) scale(${s * sx}, ${s * sy})`,
        transformOrigin: origem ?? origemPadrao,
        opacity: op,
        clipPath: clip,
        filter: sombra && entrada !== 'carimbo' ? SOMBRA : undefined,
      }}
    >
      {children}
    </div>
  );
};

// ---------- texto ----------

// alerta = vermelho: número ruim, perda, sirene (regras de 08/10/2026); destaque = verde.
type CorNome = 'navy' | 'destaque' | 'azul' | 'creme' | 'kraft' | 'amarelo' | 'branco' | 'alerta';
const fundo = (c: CorNome): React.CSSProperties =>
  c === 'kraft'
    ? {backgroundImage: `url(${staticFile('paper/kraft.jpg')})`, backgroundSize: '256px 256px', color: COR.navy}
    : {background: COR[c], color: c === 'creme' || c === 'amarelo' || c === 'branco' ? COR.navy : '#fff'};

// Etiqueta retangular (a peça mais comum da referência: seção, rótulo, valor).
export const Etiqueta: React.FC<{
  txt: React.ReactNode;
  cor?: CorNome;
  tam?: number;
  mono?: boolean;
  peso?: number;
  corTexto?: string;
  largura?: number;
  alinhar?: 'center' | 'left';
}> = ({txt, cor = 'navy', tam = 34, mono, peso = 900, corTexto, largura, alinhar = 'center'}) => (
  <div
    style={{
      ...fundo(cor),
      ...(corTexto ? {color: corTexto} : {}),
      fontFamily: mono ? FONTE.mono : FONTE.pesada,
      fontWeight: mono ? 700 : peso,
      fontSize: tam,
      lineHeight: 1.05,
      letterSpacing: mono ? 0 : '0.01em',
      textTransform: 'uppercase',
      padding: `${tam * 0.3}px ${tam * 0.5}px ${tam * 0.26}px`,
      whiteSpace: largura ? 'normal' : 'nowrap',
      width: largura,
      textAlign: alinhar,
      boxShadow: '0 3px 6px rgba(30,20,10,0.25)',
    }}
  >
    {txt}
  </div>
);

// Texto solto (sem fundo).
export const Texto: React.FC<{txt: React.ReactNode; tam?: number; cor?: string; mono?: boolean; peso?: number; largura?: number; alinhar?: 'center' | 'left' | 'right'}> = ({
  txt, tam = 34, cor = COR.navy, mono, peso = 900, largura, alinhar = 'center',
}) => (
  <div
    style={{
      fontFamily: mono ? FONTE.mono : FONTE.pesada,
      fontWeight: mono ? 700 : peso,
      fontSize: tam,
      color: cor,
      lineHeight: 1.08,
      textTransform: 'uppercase',
      whiteSpace: largura ? 'normal' : 'nowrap',
      width: largura,
      textAlign: alinhar,
    }}
  >
    {txt}
  </div>
);

// Máquina de escrever: revela o texto letra a letra a partir de t0 (cps = letras por segundo).
export const Digita: React.FC<{txt: string; t0: number; cps?: number}> = ({txt, t0, cps = 32}) => {
  const {t} = useT();
  const n = Math.max(0, Math.min(txt.length, Math.floor((t - t0) * cps)));
  return (
    <span>
      {txt.slice(0, n)}
      <span style={{opacity: 0}}>{txt.slice(n)}</span>
    </span>
  );
};

// Valor que troca em instantes dados (ex.: R$ 30 MIL -> R$ 40 MIL), cada troca com um pulinho.
export const Troca: React.FC<{valores: {t: number; txt: string}[]; render: (txt: string) => React.ReactNode}> = ({valores, render}) => {
  const {t, frame, fps} = useT();
  const atual = [...valores].reverse().find((v) => t >= v.t);
  if (!atual) return null;
  const k = mola(frame, fps, atual.t, MOLAS.pop);
  return <div style={{transform: `scale(${0.7 + 0.3 * k})`}}>{render(atual.txt)}</div>;
};

// Etiqueta de seção numerada (refs raul-13/14, 08/10/2026): caixa vermelha "01/08" + rótulo em papel creme.
const dois = (n: number) => String(n).padStart(2, '0');
export const EtiquetaSecao: React.FC<{txt: string; num?: number; total?: number; tam?: number}> = ({txt, num, total, tam = 30}) => (
  <div style={{display: 'flex', alignItems: 'stretch', boxShadow: '0 4px 8px rgba(30,20,10,0.28)', whiteSpace: 'nowrap'}}>
    {num !== undefined ? (
      <div style={{background: COR.destaque, color: '#fff', fontFamily: FONTE.pesada, fontWeight: 900, fontSize: tam * 1.15, lineHeight: 1, padding: `${tam * 0.28}px ${tam * 0.3}px ${tam * 0.2}px ${tam * 0.42}px`, display: 'flex', alignItems: 'center'}}>
        {dois(num)}
        {total ? <span style={{fontSize: tam * 0.55, marginLeft: 2, marginTop: tam * 0.25}}>/{dois(total)}</span> : null}
      </div>
    ) : null}
    <div style={{background: num !== undefined ? COR.creme : COR.navy, color: num !== undefined ? COR.navy : '#fff', fontFamily: FONTE.pesada, fontWeight: 900, fontSize: tam, lineHeight: 1, textTransform: 'uppercase', padding: `${tam * 0.36}px ${tam * 0.55}px ${tam * 0.28}px`, display: 'flex', alignItems: 'center'}}>
      {txt}
    </div>
  </div>
);

// "Bate" como carimbo em t0 (2,6x -> 1 em 0,13 s + tremidinha), em fluxo — pra usar dentro de cartão/cupom.
export const Bate: React.FC<{t0: number; rot?: number; children: React.ReactNode}> = ({t0, rot = 0, children}) => {
  const {t} = useT();
  if (t < t0) return null;
  const p = rampa(t, t0, 0.13, Easing.in(Easing.quad));
  let s = lerp(2.6, 1, p);
  const pos = t - (t0 + 0.13);
  if (pos > 0) s = 1 - 0.07 * Math.exp(-pos * 16) * Math.cos(pos * 38);
  return <div style={{transform: `rotate(${rot}deg) scale(${s})`, opacity: Math.min(1, p * 2.5)}}>{children}</div>;
};

// Cupom saindo da impressora (ref raul-12, 08/10/2026): fenda azul-marinho com LED vermelho e o papel sendo
// impresso de cima pra baixo a partir de t0. O conteúdo do cupom é o `children` (em fluxo).
export const Cupom: React.FC<{t0: number; w?: number; h: number; titulo: string; children?: React.ReactNode}> = ({t0, w = 520, h, titulo, children}) => {
  const {t} = useT();
  const fenda = rampa(t, t0, 0.25, Easing.out(Easing.cubic));
  const sai = rampa(t, t0 + 0.2, 0.75, Easing.out(Easing.cubic));
  const larg = w + 70;
  return (
    <div style={{position: 'relative', width: larg, height: h + 40}}>
      <div style={{position: 'absolute', left: 35, top: 26, width: w, height: h, overflow: 'hidden', filter: SOMBRA}}>
        <div style={{transform: `translateY(${-(1 - sai) * h}px)`}}>
          <div style={{width: w, height: h, background: '#FBF8F0', clipPath: recorteRasgado(w, h, 77, 7), padding: '34px 30px 0', boxSizing: 'border-box'}}>
            <div style={{fontFamily: FONTE.mono, fontWeight: 700, fontSize: 24, color: COR.navy, textAlign: 'center', textTransform: 'uppercase', letterSpacing: '0.04em'}}>{titulo}</div>
            <div style={{borderTop: `3px dashed ${COR.cinza}`, margin: '16px 0 10px'}} />
            {children}
          </div>
        </div>
      </div>
      <div style={{position: 'absolute', left: 0, top: 0, width: larg, height: 46, borderRadius: 14, background: COR.navy, transform: `scaleX(${fenda})`, boxShadow: '0 6px 10px rgba(30,20,10,0.3)'}}>
        <div style={{position: 'absolute', left: 30, right: 30, top: 26, height: 6, borderRadius: 3, background: '#0B0A12'}} />
        <div style={{position: 'absolute', right: 18, top: 10, width: 12, height: 12, borderRadius: 6, background: COR.destaque, boxShadow: `0 0 8px ${COR.destaque}`}} />
      </div>
    </div>
  );
};

// Sirene vermelha piscando: a luz acende e apaga (~2,4 vezes por segundo) com um brilho vermelho que pulsa em volta.
export const Sirene: React.FC<{tam?: number; hz?: number}> = ({tam = 220, hz = 2.4}) => {
  const {t} = useT();
  const fase = (t * hz) % 1;
  const luz = Math.pow(Math.max(0, Math.sin(fase * Math.PI)), 1.6); // 0 → 1 → 0 a cada piscada
  const raio = tam * (0.95 + 0.35 * luz);
  return (
    <div style={{position: 'relative', width: tam, height: tam}}>
      <div
        style={{
          position: 'absolute',
          left: tam / 2 - raio,
          top: tam * 0.45 - raio,
          width: raio * 2,
          height: raio * 2,
          borderRadius: '50%',
          background: `radial-gradient(circle, rgba(255,70,50,${0.55 * luz}) 0%, rgba(255,70,50,${0.22 * luz}) 38%, rgba(255,70,50,0) 68%)`,
        }}
      />
      <div style={{position: 'relative', filter: `drop-shadow(0 0 ${4 + 18 * luz}px rgba(255,60,40,${0.35 + 0.6 * luz})) brightness(${0.92 + 0.28 * luz})`}}>
        <Icone nome="siren" tam={tam} cor={COR.alerta} />
      </div>
    </div>
  );
};

// Gira o filho continuamente (graus por segundo) e freia até parar em tPara (engrenagem que "para").
export const Gira: React.FC<{vel?: number; tPara?: number; children: React.ReactNode}> = ({vel = 90, tPara, children}) => {
  const {t} = useT();
  let ang = t * vel;
  if (tPara !== undefined && t > tPara) {
    const dt = Math.min(t - tPara, 0.5);
    ang = tPara * vel + vel * (dt - (dt * dt) / 1.0); // desacelera em 0,5 s
  }
  return <div style={{transform: `rotate(${ang}deg)`}}>{children}</div>;
};

// Ícone + rótulo lado a lado (listas de itens da fala). `vertical` empilha o rótulo embaixo do ícone.
export const IconeRotulo: React.FC<{ic: string; txt: string; cor?: CorNome; corIc?: string; tamIc?: number; tam?: number; vertical?: boolean}> = ({
  ic, txt, cor = 'navy', corIc = COR.navy, tamIc = 96, tam = 32, vertical,
}) => (
  <div style={{display: 'flex', flexDirection: vertical ? 'column' : 'row', alignItems: 'center', gap: vertical ? 14 : 20}}>
    <Icone nome={ic} tam={tamIc} cor={corIc} />
    <Etiqueta txt={txt} cor={cor} tam={tam} />
  </div>
);

// Pulsa (batimento): escala oscilando — coração, alerta, sirene.
export const Pulsa: React.FC<{bpm?: number; amp?: number; children: React.ReactNode}> = ({bpm = 110, amp = 0.08, children}) => {
  const {t} = useT();
  const fase = (t * bpm) / 60;
  const f = fase - Math.floor(fase);
  const bate = Math.exp(-f * 9) + 0.6 * Math.exp(-Math.max(0, f - 0.22) * 12) * (f > 0.22 ? 1 : 0);
  return <div style={{transform: `scale(${1 + amp * bate})`}}>{children}</div>;
};

// Pizza (fatia preenchida) que anima de `de` até `ate` (%) entre t0 e t1; texto no meio (rosquinha).
export const Pizza: React.FC<{d?: number; de?: number; ate: number; t0: number; t1: number; cor?: string; txt?: React.ReactNode; tamTxt?: number}> = ({
  d = 260, de = 0, ate, t0, t1, cor = COR.destaque, txt, tamTxt,
}) => {
  const {t} = useT();
  const v = lerp(de, ate, rampa(t, t0, Math.max(0.01, t1 - t0), Easing.inOut(Easing.cubic)));
  return (
    <div style={{width: d, height: d, borderRadius: '50%', background: `conic-gradient(${cor} 0% ${v}%, #E4DCCB ${v}% 100%)`, border: `8px solid ${COR.navy}`, boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
      <div style={{width: d * 0.56, height: d * 0.56, borderRadius: '50%', background: COR.creme, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONTE.pesada, fontWeight: 900, fontSize: tamTxt ?? d * 0.17, color: COR.navy, boxShadow: 'inset 0 3px 6px rgba(0,0,0,0.15)'}}>
        {txt ?? `${Math.round(v)}%`}
      </div>
    </div>
  );
};

// Peso de academia (anilha/kettlebell chapado) com rótulo — "custo pesado", "conta pesada".
export const Peso: React.FC<{txt?: string; w?: number}> = ({txt, w = 260}) => (
  <div style={{position: 'relative', width: w, height: w * 0.95}}>
    <svg width={w} height={w * 0.95} viewBox="0 0 260 247" style={{position: 'absolute'}}>
      <path d="M85,70 C85,20 175,20 175,70" fill="none" stroke={COR.navy} strokeWidth="22" strokeLinecap="round" />
      <path d="M40,95 Q40,70 70,70 H190 Q220,70 220,95 L245,215 Q250,240 222,240 H38 Q10,240 15,215 Z" fill={COR.navy} />
    </svg>
    {txt ? (
      <div style={{position: 'absolute', left: 0, right: 0, top: w * 0.47, textAlign: 'center', fontFamily: FONTE.pesada, fontWeight: 900, fontSize: w * 0.12, color: '#fff', textTransform: 'uppercase', lineHeight: 1.05}}>
        {txt}
      </div>
    ) : null}
  </div>
);

// Selo "ao vivo": bolinha verde pulsando + texto.
export const AoVivo: React.FC<{txt: string; tam?: number}> = ({txt, tam = 34}) => {
  const {t} = useT();
  const pulso = 0.5 + 0.5 * Math.sin(t * 7);
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: tam * 0.4, background: COR.navy, color: '#fff', padding: `${tam * 0.32}px ${tam * 0.55}px ${tam * 0.26}px`, fontFamily: FONTE.pesada, fontWeight: 900, fontSize: tam, textTransform: 'uppercase', whiteSpace: 'nowrap', boxShadow: '0 3px 6px rgba(30,20,10,0.25)'}}>
      <div style={{width: tam * 0.55, height: tam * 0.55, borderRadius: '50%', background: COR.destaque, boxShadow: `0 0 0 ${4 + 6 * pulso}px rgba(5,150,105,${0.35 * (1 - pulso) + 0.1})`}} />
      {txt}
    </div>
  );
};

// Relógio digital de papel (hora + dia), cabeçalho na cor de destaque.
export const Relogio: React.FC<{hora: string; dia: string; w?: number}> = ({hora, dia, w = 300}) => (
  <div style={{width: w, background: COR.creme, boxShadow: SOMBRA_CARTAO}}>
    <div style={{...fundo('destaque'), fontFamily: FONTE.pesada, fontWeight: 900, fontSize: w * 0.09, textAlign: 'center', padding: `${w * 0.04}px 0 ${w * 0.03}px`, textTransform: 'uppercase'}}>{dia}</div>
    <div style={{fontFamily: FONTE.mono, fontWeight: 700, fontSize: w * 0.3, color: COR.navy, textAlign: 'center', lineHeight: 1.15, padding: `${w * 0.04}px 0`}}>{hora}</div>
  </div>
);

// ---------- cartões ----------

export const Cartao: React.FC<{
  w: number;
  h: number;
  cabecalho?: string;
  corCab?: CorNome;
  seed?: number;
  rasgado?: boolean;
  barra?: CorNome; // barra vertical à esquerda (linha de tabela)
  pad?: number;
  children?: React.ReactNode;
}> = ({w, h, cabecalho, corCab = 'destaque', seed = 1, rasgado = true, barra, pad = 0, children}) => (
  <div style={{width: w, height: h, filter: rasgado ? SOMBRA : undefined}}>
    <div
      style={{
        width: w,
        height: h,
        background: COR.creme,
        clipPath: rasgado ? recorteRasgado(w, h, seed) : undefined,
        boxShadow: rasgado ? undefined : SOMBRA_CARTAO,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {barra ? <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 14, ...fundo(barra)}} /> : null}
      {cabecalho ? (
        <div
          style={{
            ...fundo(corCab),
            fontFamily: FONTE.pesada,
            fontWeight: 900,
            fontSize: 26,
            textTransform: 'uppercase',
            textAlign: 'center',
            padding: '14px 10px 11px',
            letterSpacing: '0.02em',
          }}
        >
          {cabecalho}
        </div>
      ) : null}
      <div style={{padding: pad}}>{children}</div>
    </div>
  </div>
);

export const Carimbo: React.FC<{txt: string; cor?: 'destaque' | 'azul'; tam?: number}> = ({txt, cor = 'destaque', tam = 60}) => (
  <div
    style={{
      border: `${Math.round(tam * 0.11)}px solid ${COR[cor]}`,
      color: COR[cor],
      fontFamily: FONTE.pesada,
      fontWeight: 900,
      fontSize: tam,
      lineHeight: 1,
      padding: `${tam * 0.16}px ${tam * 0.3}px ${tam * 0.12}px`,
      textTransform: 'uppercase',
      whiteSpace: 'nowrap',
      letterSpacing: '0.02em',
      background: 'rgba(246,240,226,0.55)',
      mixBlendMode: 'multiply',
      opacity: 0.93,
    }}
  >
    {txt}
  </div>
);

// ---------- figuras ----------

const Kraft: React.FC<{id: string}> = ({id}) => (
  <defs>
    <pattern id={id} patternUnits="userSpaceOnUse" width="256" height="256">
      <image href={staticFile('paper/kraft.jpg')} width="256" height="256" />
    </pattern>
  </defs>
);

const pinta = (cor: string, idKraft: string) => (cor === 'kraft' ? `url(#${idKraft})` : cor);

// Pessoa em silhueta (cabeça + corpo em cápsula), como os bonecos da referência.
export const Pessoa: React.FC<{cor?: string; gravata?: string; tam?: number; rosto?: boolean}> = ({cor = COR.navy, gravata, tam = 1, rosto}) => {
  const id = useId().replace(/:/g, '');
  const f = pinta(cor, id);
  return (
    <svg width={120 * tam} height={240 * tam} viewBox="0 0 120 240">
      <Kraft id={id} />
      <circle cx="60" cy="34" r="30" fill={f} />
      <path d="M12,240 V116 a48,48 0 0 1 48,-48 a48,48 0 0 1 48,48 V240 Z" fill={f} />
      {gravata ? <polygon points="60,72 51,86 60,168 69,86" fill={gravata} /> : null}
      {rosto ? (
        <>
          <circle cx="50" cy="33" r="3.2" fill={COR.creme} />
          <circle cx="70" cy="33" r="3.2" fill={COR.creme} />
        </>
      ) : null}
    </svg>
  );
};

export const Moeda: React.FC<{d?: number}> = ({d = 90}) => (
  <svg width={d} height={d} viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="47" fill={COR.amarelo} stroke="#C99A1E" strokeWidth="5" />
    <circle cx="50" cy="50" r="34" fill="none" stroke="#D9A823" strokeWidth="4" />
    <text x="50" y="62" textAnchor="middle" fontFamily={FONTE.pesada} fontWeight={900} fontSize="34" fill="#8A5F0C">
      R$
    </text>
  </svg>
);

// Nota de dinheiro — verde (regra de 08/10/2026: dinheiro é verde, não azul).
export const Nota: React.FC<{w?: number}> = ({w = 190}) => (
  <svg width={w} height={w * 0.5} viewBox="0 0 200 100">
    <rect x="2" y="2" width="196" height="96" rx="6" fill={COR.dinheiro} />
    <rect x="12" y="12" width="176" height="76" rx="4" fill="none" stroke={COR.dinheiroClaro} strokeWidth="3" />
    <circle cx="100" cy="50" r="24" fill={COR.dinheiroClaro} />
    <text x="100" y="60" textAnchor="middle" fontFamily={FONTE.pesada} fontWeight={900} fontSize="26" fill={COR.dinheiro}>
      R$
    </text>
  </svg>
);

export const Carteira: React.FC<{w?: number}> = ({w = 260}) => {
  const id = useId().replace(/:/g, '');
  return (
    <svg width={w} height={w * 0.66} viewBox="0 0 260 172">
      <Kraft id={id} />
      <rect x="4" y="6" width="252" height="160" rx="16" fill={`url(#${id})`} />
      <rect x="4" y="6" width="252" height="34" rx="12" fill="rgba(60,40,10,0.18)" />
      <rect x="196" y="66" width="60" height="52" rx="10" fill={COR.navy} />
      <circle cx="222" cy="92" r="9" fill={COR.amarelo} />
    </svg>
  );
};

// Bloco de papelão com rótulo (pilhas, "estrutura", tijolos).
export const Bloco: React.FC<{w?: number; h?: number; txt?: string; tam?: number}> = ({w = 300, h = 78, txt, tam = 26}) => (
  <div
    style={{
      width: w,
      height: h,
      ...fundo('kraft'),
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: FONTE.pesada,
      fontWeight: 900,
      fontSize: tam,
      textTransform: 'uppercase',
      color: COR.navy,
      borderRadius: 4,
    }}
  >
    {txt}
  </div>
);

export const Calendario: React.FC<{num: string; topo?: string; w?: number}> = ({num, topo = 'DIA', w = 230}) => (
  <div style={{width: w, background: COR.creme, boxShadow: SOMBRA_CARTAO, position: 'relative'}}>
    <div style={{...fundo('destaque'), fontFamily: FONTE.pesada, fontWeight: 900, fontSize: w * 0.12, textAlign: 'center', padding: `${w * 0.06}px 0 ${w * 0.05}px`}}>{topo}</div>
    <div style={{fontFamily: FONTE.pesada, fontWeight: 900, fontSize: w * 0.5, color: COR.navy, textAlign: 'center', lineHeight: 1.1, padding: `${w * 0.04}px 0 ${w * 0.06}px`}}>{num}</div>
    {[0.3, 0.7].map((p) => (
      <div key={p} style={{position: 'absolute', top: -12, left: w * p - 7, width: 14, height: 30, borderRadius: 7, background: COR.navy}} />
    ))}
  </div>
);

// Grade de dias que vão sendo riscados (X vermelho) de t0 em diante.
export const MesRiscado: React.FC<{t0: number; dur?: number; w?: number}> = ({t0, dur = 0.8, w = 380}) => {
  const {t} = useT();
  const cel = (w - 40) / 6;
  const dias = Array.from({length: 30}, (_, i) => i);
  return (
    <div style={{width: w, background: COR.creme, boxShadow: SOMBRA_CARTAO}}>
      <div style={{...fundo('destaque'), fontFamily: FONTE.pesada, fontWeight: 900, fontSize: 24, textAlign: 'center', padding: '10px 0 8px'}}>O MÊS</div>
      <div style={{display: 'flex', flexWrap: 'wrap', padding: 20, gap: 0}}>
        {dias.map((i) => {
          const p = rampa(t, t0 + (i * dur) / 30, 0.08);
          return (
            <div key={i} style={{width: cel, height: cel * 0.82, position: 'relative', fontFamily: FONTE.mono, fontSize: 18, color: COR.cinza, textAlign: 'center', paddingTop: 8}}>
              {i + 1}
              <svg width={cel} height={cel * 0.82} viewBox="0 0 40 33" style={{position: 'absolute', left: 0, top: 0}}>
                <path d="M10,6 L30,27 M30,6 L10,27" stroke={COR.destaque} strokeWidth="5" strokeLinecap="round" fill="none" strokeDasharray="60" strokeDashoffset={60 * (1 - p)} />
              </svg>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Seta da placa de direção (aponta pra esquerda ou direita), texto branco.
export const SetaPlaca: React.FC<{txt: string; lado: 'esq' | 'dir'; cor?: 'destaque' | 'azul' | 'navy'; w?: number; h?: number; tam?: number}> = ({
  txt, lado, cor = 'destaque', w = 360, h = 96, tam = 26,
}) => {
  const ponta = h * 0.55;
  const pts = lado === 'dir' ? `0,0 ${w - ponta},0 ${w},${h / 2} ${w - ponta},${h} 0,${h}` : `${ponta},0 ${w},0 ${w},${h} ${ponta},${h} 0,${h / 2}`;
  return (
    <div style={{width: w, height: h, position: 'relative'}}>
      <svg width={w} height={h} style={{position: 'absolute'}}>
        <polygon points={pts} fill={COR[cor]} />
      </svg>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          paddingLeft: lado === 'esq' ? ponta * 0.6 : 0,
          paddingRight: lado === 'dir' ? ponta * 0.6 : 0,
          fontFamily: FONTE.pesada,
          fontWeight: 900,
          fontSize: tam,
          lineHeight: 1.05,
          color: '#fff',
          textAlign: 'center',
          textTransform: 'uppercase',
        }}
      >
        {txt}
      </div>
    </div>
  );
};

export const Poste: React.FC<{h?: number}> = ({h = 520}) => (
  <div style={{width: 26, height: h, ...fundo('kraft'), borderRadius: 4}} />
);

// Tesoura: aberta, fecha de uma vez em tCorte (corta) e reabre devagar. Lâminas largas e cabos vermelhos grandes
// pra ler como tesoura (com lâmina fina parecia um compasso).
export const Tesoura: React.FC<{tCorte: number; w?: number}> = ({tCorte, w = 330}) => {
  const {t} = useT();
  const fechar = rampa(t, tCorte - 0.06, 0.07, Easing.in(Easing.quad));
  const reabre = rampa(t, tCorte + 0.25, 0.4);
  const ang = 34 * (1 - fechar) + 18 * reabre;
  const lamina = 'M-6,-24 C80,-26 200,-16 300,-2 C303,1 303,3 300,5 C200,12 80,20 -6,20 Z';
  const cabo = (sinal: number) => (
    <g>
      <path d={`M-6,${-4 * sinal} L-46,${22 * sinal}`} stroke={COR.destaque} strokeWidth="20" strokeLinecap="round" />
      <ellipse cx="-78" cy={34 * sinal} rx="44" ry="32" fill="none" stroke={COR.destaque} strokeWidth="18" />
    </g>
  );
  return (
    <svg width={w} height={w * 0.75} viewBox="-140 -130 460 260" style={{overflow: 'visible'}}>
      <g transform={`rotate(${-ang / 2})`}>
        {cabo(1)}
        <path d={lamina} fill="#9A9DAE" />
        <path d={lamina} fill={COR.navy} transform="scale(1,0.62) translate(0,-6)" />
      </g>
      <g transform={`rotate(${ang / 2}) scale(1,-1)`}>
        {cabo(1)}
        <path d={lamina} fill="#B5B8C6" />
        <path d={lamina} fill="#2E2C40" transform="scale(1,0.62) translate(0,-6)" />
      </g>
      <circle cx="0" cy="0" r="11" fill={COR.amarelo} stroke={COR.navy} strokeWidth="4" />
    </svg>
  );
};

// Etiqueta que é cortada ao meio em tCorte: as duas metades caem girando.
export const EtiquetaCortada: React.FC<{txt: string; tCorte: number; cor?: CorNome; tam?: number}> = ({txt, tCorte, cor = 'destaque', tam = 48}) => {
  const {t} = useT();
  const dt = Math.max(0, t - tCorte);
  const metade = (lado: 'esq' | 'dir') => {
    const sinal = lado === 'esq' ? -1 : 1;
    return (
      <div
        style={{
          position: lado === 'esq' ? 'relative' : 'absolute',
          left: 0,
          top: 0,
          clipPath: lado === 'esq' ? 'inset(0 50% 0 0)' : 'inset(0 0 0 50%)',
          transform: dt > 0 ? `translate(${sinal * 60 * dt}px, ${1300 * dt * dt}px) rotate(${sinal * 45 * dt}deg)` : undefined,
          opacity: dt > 0.9 ? 0 : 1,
        }}
      >
        <Etiqueta txt={txt} cor={cor} tam={tam} />
      </div>
    );
  };
  return (
    <div style={{position: 'relative'}}>
      {metade('esq')}
      {metade('dir')}
    </div>
  );
};

export const ChipIA: React.FC<{d?: number}> = ({d = 250}) => {
  const pinos = [0.28, 0.5, 0.72];
  return (
    <svg width={d} height={d} viewBox="0 0 260 260">
      {pinos.map((p) => (
        <g key={p} fill={COR.navy}>
          <rect x={260 * p - 8} y="8" width="16" height="40" rx="4" />
          <rect x={260 * p - 8} y="212" width="16" height="40" rx="4" />
          <rect y={260 * p - 8} x="8" height="16" width="40" rx="4" />
          <rect y={260 * p - 8} x="212" height="16" width="40" rx="4" />
        </g>
      ))}
      <rect x="38" y="38" width="184" height="184" rx="24" fill={COR.navy} />
      <rect x="56" y="56" width="148" height="148" rx="14" fill="none" stroke="#3A3752" strokeWidth="6" />
      <text x="130" y="160" textAnchor="middle" fontFamily={FONTE.pesada} fontWeight={900} fontSize="86" fill="#fff">
        IA
      </text>
    </svg>
  );
};

// Documento pequeno (papel com linhas) — o "trabalho repetitivo" que voa.
export const Doc: React.FC<{w?: number; cor?: CorNome}> = ({w = 90, cor = 'destaque'}) => (
  <div style={{width: w, height: w * 1.22, background: '#FFFDF7', boxShadow: SOMBRA_CARTAO, padding: w * 0.12, boxSizing: 'border-box'}}>
    <div style={{height: w * 0.1, ...fundo(cor), marginBottom: w * 0.1}} />
    {[0.9, 0.7, 0.85, 0.6].map((l, i) => (
      <div key={i} style={{height: w * 0.05, width: `${l * 100}%`, background: '#9C968A', marginBottom: w * 0.09}} />
    ))}
  </div>
);

// Ícone Phosphor (peso fill) pintado por máscara.
export const Icone: React.FC<{nome: string; tam?: number; cor?: string}> = ({nome, tam = 120, cor = COR.navy}) => {
  const url = `url(${staticFile(`paper/icones/${nome}-fill.svg`)})`;
  return <div style={{width: tam, height: tam, background: cor, WebkitMaskImage: url, maskImage: url, WebkitMaskSize: 'contain', maskSize: 'contain', WebkitMaskRepeat: 'no-repeat', maskRepeat: 'no-repeat', WebkitMaskPosition: 'center', maskPosition: 'center'}} />;
};

export const Botao: React.FC<{txt: string; tClique?: number; tam?: number}> = ({txt, tClique, tam = 52}) => {
  const {t} = useT();
  const aperta = tClique === undefined ? 0 : rampa(t, tClique, 0.06) * (1 - rampa(t, tClique + 0.14, 0.12));
  return (
    <div style={{position: 'relative', paddingBottom: 12}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 12, bottom: 0, background: COR.destaqueEscuro, borderRadius: 22}} />
      <div
        style={{
          position: 'relative',
          transform: `translateY(${aperta * 10}px)`,
          background: COR.destaque,
          color: '#fff',
          borderRadius: 22,
          fontFamily: FONTE.pesada,
          fontWeight: 900,
          fontSize: tam,
          padding: `${tam * 0.42}px ${tam * 0.8}px ${tam * 0.36}px`,
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
        }}
      >
        {txt}
      </div>
    </div>
  );
};

// Mãozinha que chega e clica (o clique é em tClique; chega 0,35 s antes).
export const Mao: React.FC<{tClique: number; tam?: number}> = ({tClique, tam = 150}) => {
  const {t} = useT();
  const aperta = rampa(t, tClique, 0.06) * (1 - rampa(t, tClique + 0.14, 0.12));
  return (
    <div style={{transform: `scale(${1 - 0.12 * aperta}) rotate(-18deg)`, filter: 'drop-shadow(0 0 0 #fff) drop-shadow(3px 6px 3px rgba(0,0,0,0.3))'}}>
      <div style={{filter: 'drop-shadow(0 0 3px #fff) drop-shadow(0 0 3px #fff)'}}>
        <Icone nome="hand-pointing" tam={tam} cor={COR.navy} />
      </div>
    </div>
  );
};

export const Interrogacao: React.FC<{tam?: number; cor?: string}> = ({tam = 150, cor = COR.destaque}) => {
  const {t} = useT();
  return (
    <div style={{fontFamily: FONTE.pesada, fontWeight: 900, fontSize: tam, color: cor, lineHeight: 1, transform: `rotate(${Math.sin(t * 7) * 6}deg)`}}>?</div>
  );
};

// Barra de gráfico (cresce de baixo com a Peca entrada="cresce").
export const Barra: React.FC<{w?: number; h: number; cor?: CorNome}> = ({w = 120, h, cor = 'destaque'}) => <div style={{width: w, height: h, ...fundo(cor)}} />;

// Balão de fala/pensamento.
export const Balao: React.FC<{w: number; h: number; cauda?: 'esq' | 'dir'; children: React.ReactNode}> = ({w, h, cauda = 'esq', children}) => (
  <div style={{width: w, height: h, position: 'relative'}}>
    <svg width={w + 20} height={h + 70} style={{position: 'absolute', left: -10, top: -10, overflow: 'visible'}}>
      <path
        d={
          cauda === 'esq'
            ? `M30,10 H${w - 10} a20,20 0 0 1 20,20 V${h - 10} a20,20 0 0 1 -20,20 H120 L60,${h + 60} L80,${h + 10} H30 a20,20 0 0 1 -20,-20 V30 a20,20 0 0 1 20,-20 Z`
            : `M30,10 H${w - 10} a20,20 0 0 1 20,20 V${h - 10} a20,20 0 0 1 -20,20 H${w - 60} L${w - 20},${h + 60} L${w - 120},${h + 10} H30 a20,20 0 0 1 -20,-20 V30 a20,20 0 0 1 20,-20 Z`
        }
        fill="#FFFDF7"
        stroke={COR.navy}
        strokeWidth="6"
        strokeLinejoin="round"
      />
    </svg>
    <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, boxSizing: 'border-box'}}>{children}</div>
  </div>
);

// Linha de lista/recibo: aparece em t digitando; marcador "−" vermelho (custo) ou caixinha que recebe ✓ em tCheck.
export const ItemLista: React.FC<{t: number; txt: string; tCheck?: number; marcador?: 'menos' | 'caixa'; tam?: number; cps?: number}> = ({
  t, txt, tCheck, marcador = 'menos', tam = 32, cps = 34,
}) => {
  const {t: agora, frame, fps} = useT();
  const altura = tam * 1.75;
  if (agora < t) return <div style={{height: altura}} />;
  const k = mola(frame, fps, t, MOLAS.pop);
  return (
    <div style={{height: altura, display: 'flex', alignItems: 'center', gap: tam * 0.45}}>
      <div style={{transform: `scale(${k})`, flex: 'none'}}>
        {marcador === 'menos' ? (
          <div style={{width: tam * 0.75, height: tam * 0.2, background: COR.destaque, borderRadius: 3}} />
        ) : (
          <div style={{width: tam * 1.05, height: tam * 1.05, border: `${tam * 0.12}px solid ${COR.navy}`, borderRadius: 6, position: 'relative', boxSizing: 'border-box'}}>
            {tCheck !== undefined && agora >= tCheck ? (
              <div style={{position: 'absolute', left: -tam * 0.15, top: -tam * 0.45}}>
                <Check t0={tCheck} tam={tam * 1.3} cor={COR.destaque} />
              </div>
            ) : null}
          </div>
        )}
      </div>
      <div style={{fontFamily: FONTE.pesada, fontWeight: 800, fontSize: tam, color: COR.navy, textTransform: 'uppercase', whiteSpace: 'nowrap'}}>
        <Digita txt={txt} t0={t} cps={cps} />
      </div>
    </div>
  );
};

// ---------- traços que desenham ----------

// Seta desenhada de (x1,y1) a (x2,y2) no painel; `curva` desloca o ponto de controle perpendicular.
export const Seta: React.FC<{x1: number; y1: number; x2: number; y2: number; t0: number; dur?: number; cor?: string; esp?: number; curva?: number; sai?: number}> = ({
  x1, y1, x2, y2, t0, dur = 0.3, cor = COR.navy, esp = 8, curva = 0, sai,
}) => {
  const {t} = useT();
  if (t < t0) return null;
  if (sai !== undefined && t >= sai) return null;
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  const len0 = Math.hypot(x2 - x1, y2 - y1);
  const nx = -(y2 - y1) / len0, ny = (x2 - x1) / len0;
  const cx = mx + nx * curva, cy = my + ny * curva;
  const len = len0 + Math.abs(curva) * 0.6;
  const p = rampa(t, t0, dur, Easing.inOut(Easing.cubic));
  const ang = (Math.atan2(y2 - cy, x2 - cx) * 180) / Math.PI;
  const ponta = rampa(t, t0 + dur * 0.8, 0.08);
  return (
    <svg width={1080} height={960} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', filter: SOMBRA}}>
      <path d={`M${x1},${y1} Q${cx},${cy} ${x2},${y2}`} stroke={cor} strokeWidth={esp} strokeLinecap="round" fill="none" strokeDasharray={len} strokeDashoffset={len * (1 - p)} />
      <g transform={`translate(${x2},${y2}) rotate(${ang}) scale(${ponta})`}>
        <path d={`M${-esp * 3.2},${-esp * 2.4} L0,0 L${-esp * 3.2},${esp * 2.4}`} stroke={cor} strokeWidth={esp} strokeLinecap="round" strokeLinejoin="round" fill="none" />
      </g>
    </svg>
  );
};

export const Check: React.FC<{t0: number; tam?: number; cor?: string}> = ({t0, tam = 90, cor = COR.azul}) => {
  const {t} = useT();
  const p = rampa(t, t0, 0.22, Easing.out(Easing.quad));
  return (
    <svg width={tam} height={tam} viewBox="0 0 100 100">
      <path d="M14,54 L40,80 L88,22" stroke={cor} strokeWidth="15" strokeLinecap="round" strokeLinejoin="round" fill="none" strokeDasharray="120" strokeDashoffset={120 * (1 - p)} />
    </svg>
  );
};

export const Xis: React.FC<{t0: number; tam?: number; cor?: string}> = ({t0, tam = 120, cor = COR.destaque}) => {
  const {t} = useT();
  const a = rampa(t, t0, 0.12);
  const b = rampa(t, t0 + 0.1, 0.12);
  return (
    <svg width={tam} height={tam} viewBox="0 0 100 100">
      <path d="M16,16 L84,84" stroke={cor} strokeWidth="16" strokeLinecap="round" strokeDasharray="100" strokeDashoffset={100 * (1 - a)} />
      <path d="M84,16 L16,84" stroke={cor} strokeWidth="16" strokeLinecap="round" strokeDasharray="100" strokeDashoffset={100 * (1 - b)} />
    </svg>
  );
};

// Sublinhado que desenha embaixo de um valor.
export const Risco: React.FC<{t0: number; w: number; cor?: string; esp?: number}> = ({t0, w, cor = COR.destaque, esp = 8}) => {
  const {t} = useT();
  const p = rampa(t, t0, 0.25);
  return (
    <svg width={w} height={esp * 3} viewBox={`0 0 ${w} ${esp * 3}`}>
      <path d={`M4,${esp * 1.8} Q${w / 2},${esp * 0.6} ${w - 4},${esp * 1.4}`} stroke={cor} strokeWidth={esp} strokeLinecap="round" fill="none" strokeDasharray={w * 1.1} strokeDashoffset={w * 1.1 * (1 - p)} />
    </svg>
  );
};
