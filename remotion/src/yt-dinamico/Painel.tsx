// Painel papel à esquerda (cartão de cor sólida da marca, SEM faixa escura nem sombra no texto).
// Rótulo em caixa alta na cor de destaque + itens que entram no tempo da fala. Cores e fontes da marca: marca.ts.
import React from 'react';
import {Img, staticFile} from 'remotion';
import type {EDL, Item, Painel as TPainel} from './tipos';
import {clamp01, easeIn, easeInOut, easeOut, H, ITALICO, M, PAINEL_W, SANS, SERIF, useQuadro} from './marca';

// "texto com *destaque*" -> destaque na serifa itálica, na cor de destaque da marca
export const Rico: React.FC<{texto: string}> = ({texto}) => (
  <>
    {texto.split('*').map((t, i) =>
      i % 2 === 1 ? (
        <span key={i} style={{fontFamily: ITALICO, fontWeight: 400, color: M.destaque}}>{t}</span>
      ) : (
        <span key={i}>{t}</span>
      ),
    )}
  </>
);

const LOGO = {arq: '', nome: ''};
const entra = (f: number, o: number, d = 9) => easeOut(clamp01((f - o) / d));

const Risco: React.FC<{f: number; o?: number; atraso?: number}> = ({f, o, atraso = 0}) => {
  if (o === undefined) return null;
  const k = easeInOut(clamp01((f - o - atraso) / 7));
  if (k <= 0) return null;
  return (
    <div style={{position: 'absolute', left: -8, top: '54%', height: 9, borderRadius: 5, background: M.destaque,
      width: `calc(${k * 100}% + ${16 * k}px)`, transform: 'translateY(-50%) rotate(-2deg)', transformOrigin: 'left center'}} />
  );
};

const apagado = (f: number, risco?: number) => (risco === undefined ? 1 : 1 - 0.5 * clamp01((f - risco - 4) / 8));

const Check: React.FC = () => (
  <svg width={56} height={56} viewBox="0 0 54 54" style={{flex: 'none'}}>
    <circle cx={27} cy={27} r={27} fill={M.destaque} />
    <path d="M15 28 L24 37 L40 19" fill="none" stroke={M.branco} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const ItemV: React.FC<{it: Item; f: number; ultimoPasso: boolean; primeiroPasso: boolean}> = ({it, f, ultimoPasso, primeiroPasso}) => {
  const k = entra(f, it.o);
  const base: React.CSSProperties = {opacity: k, transform: `translateY(${(1 - k) * 26}px)`};
  const serif: React.CSSProperties = {fontFamily: SERIF, fontWeight: 600, letterSpacing: '-0.01em', color: M.tinta};
  switch (it.tipo) {
    case 'logo': // logo do projeto.json; sem logo, o nome da marca em serifa grande
      return (
        <div style={base}>
          {LOGO.arq ? (
            <Img src={staticFile(LOGO.arq)} style={{width: 430, maxHeight: 260, objectFit: 'contain', objectPosition: 'left center', display: 'block'}} />
          ) : (
            <div style={{...serif, fontWeight: 700, fontSize: 92, lineHeight: 1}}>{LOGO.nome}</div>
          )}
        </div>
      );
    case 'titulo': {
      const linhas = (it.texto ?? '').split('\n');
      return (
        <div style={{...base, ...serif, fontSize: it.tam ?? 88, lineHeight: 1.02, opacity: k * apagado(f, it.risco)}}>
          {linhas.map((l, i) => (
            <div key={i} style={{position: 'relative', display: 'table'}}>
              <Rico texto={l} />
              <Risco f={f} o={it.risco} atraso={i * 3} />
            </div>
          ))}
        </div>
      );
    }
    case 'numero': {
      const n = parseInt(it.texto ?? '0', 10);
      const c = Math.round(n * easeOut(clamp01((f - it.o) / 14)));
      return (
        <div style={{...base, ...serif, opacity: k * apagado(f, it.risco)}}>
          <div style={{position: 'relative', display: 'table', fontWeight: 700, fontSize: 210, lineHeight: 0.92}}>
            {c}
            <Risco f={f} o={it.risco} />
          </div>
          <div style={{position: 'relative', display: 'table', fontSize: 76, lineHeight: 1.1}}>
            {it.sufixo}
            <Risco f={f} o={it.risco} atraso={3} />
          </div>
        </div>
      );
    }
    case 'check': {
      const kc = easeOut(clamp01((f - it.o) / 8));
      return (
        <div style={{display: 'flex', alignItems: 'center', gap: 18, opacity: k}}>
          <div style={{transform: `scale(${0.4 + 0.6 * kc})`}}><Check /></div>
          <div style={{...serif, fontSize: 61, lineHeight: 1.05, whiteSpace: 'nowrap', transform: `translateX(${(1 - k) * 18}px)`}}><Rico texto={it.texto ?? ''} /></div>
        </div>
      );
    }
    case 'chip':
      return (
        <div style={{display: 'inline-flex', opacity: k, transform: `scale(${0.82 + 0.18 * k})`, transformOrigin: 'left center',
          border: `3px solid ${M.tinta}`, borderRadius: 999, padding: '10px 26px 12px', fontFamily: SANS, fontWeight: 600, fontSize: 41, color: M.tinta, lineHeight: 1.1}}>
          {it.texto}
        </div>
      );
    case 'infinito': {
      const kc = easeOut(clamp01((f - it.o - 3) / 8));
      return (
        <div style={{display: 'flex', alignItems: 'center', gap: 18, opacity: k, transform: `translateY(${(1 - k) * 20}px)`}}>
          <div style={{...serif, fontSize: 64, lineHeight: 1.05}}>{it.texto}</div>
          <div style={{width: 68, height: 68, borderRadius: 34, background: M.destaque, color: M.branco, display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: SANS, fontWeight: 700, fontSize: 48, lineHeight: 1, transform: `scale(${kc})`, flex: 'none'}}>∞</div>
        </div>
      );
    }
    case 'passo': {
      const kl = easeInOut(clamp01((f - it.o + 2) / 8));
      return (
        <div style={{position: 'relative', display: 'flex', alignItems: 'center', gap: 26, height: 108}}>
          {!primeiroPasso && (
            <div style={{position: 'absolute', left: 10, top: 54 - 108 + 14, width: 4, height: (108 - 28) * kl, borderRadius: 2, background: M.cinza, opacity: 0.6}} />
          )}
          <div style={{width: 24, height: 24, borderRadius: 12, background: ultimoPasso ? M.destaque : M.tinta, flex: 'none',
            transform: `scale(${easeOut(clamp01((f - it.o) / 7))})`}} />
          <div style={{...serif, fontSize: 68, lineHeight: 1, opacity: k, transform: `translateX(${(1 - k) * 18}px)`}}><Rico texto={it.texto ?? ''} /></div>
        </div>
      );
    }
    case 'seta': {
      const kd = easeInOut(clamp01((f - it.o) / 10));
      return (
        <div style={{height: 96, display: 'flex', alignItems: 'center', paddingLeft: 6}}>
          <svg width={60} height={84} viewBox="0 0 60 84">
            <path d="M30 4V76M6 52L30 76L54 52" fill="none" stroke={M.tinta} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round"
              pathLength={1} strokeDasharray={1} strokeDashoffset={1 - kd} />
          </svg>
        </div>
      );
    }
  }
  return null;
};

export const PainelV: React.FC<{edl: EDL; pn: TPainel}> = ({edl, pn}) => {
  LOGO.arq = edl.marca.logo;
  LOGO.nome = edl.marca.nome;
  const f = useQuadro();
  if (f < pn.o0 - 1 || f > pn.o1 + (pn.ate_capitulo ? 40 : 0)) return null;
  const ent = easeOut(clamp01((f - pn.o0) / 10));
  const sai = pn.ate_capitulo ? 1 : 1 - easeIn(clamp01((f - (pn.o1 - 9)) / 9));
  const p = Math.min(ent, sai);
  // fundindo no cartão de capítulo: o conteúdo some enquanto o papel cresce
  const cap = pn.ate_capitulo ? edl.caps.find((c) => c.o0 >= pn.o1 - 12 && c.o0 <= pn.o1 + 12) : undefined;
  const fade = cap ? 1 - clamp01((f - cap.o0) / 6) : 1;
  const kr = entra(f, pn.o0 + 4);
  // agrupa chips seguidos numa linha
  const blocos: (Item | Item[])[] = [];
  for (const it of pn.itens) {
    const ult = blocos[blocos.length - 1];
    if (it.tipo === 'chip') {
      if (Array.isArray(ult)) ult.push(it); else blocos.push([it]);
    } else blocos.push(it);
  }
  const passos = pn.itens.filter((i) => i.tipo === 'passo');
  const ultimoVisivel = passos.filter((i) => f >= i.o).slice(-1)[0];
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: PAINEL_W, height: H, background: M.papel, transform: `translateX(${-(1 - p) * PAINEL_W}px)`}}>
      <div style={{position: 'absolute', left: 96, right: 44, top: 110, bottom: 150, display: 'flex', flexDirection: 'column', justifyContent: 'center', opacity: fade}}>
        {pn.rotulo ? (
          <div style={{fontFamily: SANS, fontWeight: 700, fontSize: 30, letterSpacing: '0.12em', textTransform: 'uppercase', color: M.destaque, lineHeight: 1.25,
            marginBottom: 30, opacity: kr, transform: `translateY(${(1 - kr) * 14}px)`}}>{pn.rotulo}</div>
        ) : null}
        <div style={{display: 'flex', flexDirection: 'column', gap: 26}}>
          {blocos.map((b, i) =>
            Array.isArray(b) ? (
              <div key={i} style={{display: 'flex', flexWrap: 'wrap', gap: 14}}>
                {b.map((c, j) => <ItemV key={j} it={c} f={f} ultimoPasso={false} primeiroPasso={false} />)}
              </div>
            ) : (
              <div key={i} style={{marginTop: b.tipo === 'passo' && passos[0] !== b ? -26 : 0}}>
                <ItemV it={b} f={f} ultimoPasso={b === ultimoVisivel} primeiroPasso={passos[0] === b} />
              </div>
            ),
          )}
        </div>
      </div>
    </div>
  );
};
