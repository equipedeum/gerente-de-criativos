// Selo (círculo na cor de destaque), cartão de capítulo, cartão final e marca d'água (símbolo da marca, se houver).
import React from 'react';
import {Img, staticFile} from 'remotion';
import type {Cap, EDL, Selo} from './tipos';
import {clamp01, easeIn, easeInOut, easeOut, H, ITALICO, M, PAINEL_W, SANS, SERIF, useQuadro, W} from './marca';
import {Rico} from './Painel';

const voltaAoTamanho = (k: number) => (k < 0.7 ? (k / 0.7) * 1.07 : 1.07 - 0.07 * ((k - 0.7) / 0.3));

export const SeloV: React.FC<{s: Selo}> = ({s}) => {
  const f = useQuadro();
  if (f < s.o0 || f > s.o1) return null;
  const ke = clamp01((f - s.o0) / 11), ks = easeIn(clamp01((f - (s.o1 - 8)) / 8));
  const esc = voltaAoTamanho(easeOut(ke)) * (1 - ks);
  const kl = easeOut(clamp01((f - s.o0 - 7) / 9)) * (1 - ks);
  const D = 300, cx = 272, cy = 470;
  return (
    <>
      <div style={{position: 'absolute', left: cx - D / 2, top: cy - D / 2, width: D, height: D, borderRadius: D / 2, background: M.destaque,
        transform: `scale(${esc}) rotate(${(1 - easeOut(ke)) * -8}deg)`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{fontFamily: ITALICO, fontWeight: 400, color: M.branco, fontSize: s.tam,
          lineHeight: 0.98, textAlign: 'center', letterSpacing: '-0.01em'}}>
          {s.texto.split('\n').map((l, i) => <div key={i}>{l}</div>)}
        </div>
      </div>
      {s.legenda ? (
        <div style={{position: 'absolute', left: cx - 200, width: 400, top: cy + D / 2 + 22, display: 'flex', justifyContent: 'center',
          opacity: kl, transform: `translateY(${(1 - kl) * 16}px)`}}>
          <div style={{background: M.papel, border: `3px solid ${M.tinta}`, borderRadius: 999, padding: '8px 22px 10px', fontFamily: SANS, fontWeight: 600,
            fontSize: 35, color: M.tinta, whiteSpace: 'nowrap'}}>{s.legenda}</div>
        </div>
      ) : null}
    </>
  );
};

// Cartão de capítulo: o papel cresce da esquerda (do painel, se tiver um na tela) até cobrir tudo e recolhe pra esquerda.
export const CapituloV: React.FC<{edl: EDL; c: Cap}> = ({edl, c}) => {
  const f = useQuadro();
  if (f < c.o0 || f >= c.o1) return null;
  const temPainel = edl.paineis.some((p) => p.ate_capitulo && c.o0 >= p.o1 - 12 && c.o0 <= p.o1 + 12);
  const w0 = temPainel ? PAINEL_W : 0;
  const ke = easeOut(clamp01((f - c.o0) / 9));
  const ks = easeIn(clamp01((f - (c.o1 - 9)) / 9));
  const largura = w0 + (W - w0) * ke;
  const kc = clamp01((f - c.o0 - 5) / 10), kt = easeOut(clamp01((f - c.o0 - 7) / 10));
  const escC = voltaAoTamanho(easeOut(kc));
  const linhas = c.titulo.split('\n');
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: largura, height: H, background: M.papel, overflow: 'hidden', transform: `translateX(${-ks * W}px)`}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 70}}>
        <div style={{width: 240, height: 240, borderRadius: 120, background: M.destaque, flex: 'none',
          transform: `scale(${escC})`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <div style={{fontFamily: ITALICO, fontWeight: 400, color: M.branco, fontSize: 124, lineHeight: 1,
            letterSpacing: '-0.02em', marginTop: -6}}>{c.num}</div>
        </div>
        <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
          <div style={{fontFamily: SANS, fontWeight: 700, fontSize: 31, letterSpacing: '0.12em', textTransform: 'uppercase', color: M.destaque, marginBottom: 18,
            opacity: kt, transform: `translateY(${(1 - kt) * 14}px)`}}>Capítulo {parseInt(c.num, 10)}</div>
          {linhas.map((l, i) => {
            const k = easeOut(clamp01((f - c.o0 - 8 - i * 2) / 10));
            return (
              <div key={i} style={{fontFamily: SERIF, fontWeight: 600, fontSize: 124, lineHeight: 1.0, letterSpacing: '-0.01em',
                color: M.tinta, opacity: k, transform: `translateY(${(1 - k) * 30}px)`, whiteSpace: 'nowrap'}}><Rico texto={l} /></div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export const FimV: React.FC<{edl: EDL}> = ({edl}) => {
  const f = useQuadro();
  const c = edl.fim;
  if (f < c.o0) return null;
  const ke = easeOut(clamp01((f - c.o0) / 10));
  const kl = easeOut(clamp01((f - c.o0 - 9) / 12)), kt = easeOut(clamp01((f - c.o0 - 16) / 12));
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: W * ke, height: H, background: M.papel, overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
        {edl.marca.logo ? (
          <Img src={staticFile(edl.marca.logo)} style={{width: 760, maxHeight: 360, objectFit: 'contain', opacity: kl, transform: `translateY(${(1 - kl) * 24}px)`}} />
        ) : (
          <div style={{fontFamily: SERIF, fontWeight: 700, fontSize: 150, lineHeight: 1, color: M.tinta, opacity: kl, transform: `translateY(${(1 - kl) * 24}px)`}}>
            {edl.marca.nome}
          </div>
        )}
        <div style={{marginTop: 44, fontFamily: SANS, fontWeight: 500, fontSize: 36, color: M.cinza, opacity: kt, transform: `translateY(${(1 - kt) * 14}px)`}}>
          {edl.marca.slogan}
        </div>
      </div>
    </div>
  );
};

export const MarcaDagua: React.FC<{edl: EDL}> = ({edl}) => {
  const f = useQuadro();
  const r = edl.marca_dagua.find(([a, b]) => f >= a && f < b);
  if (!r || !edl.marca.simbolo) return null;
  const k = Math.min(clamp01((f - r[0]) / 8), clamp01((r[1] - f) / 5));
  return <Img src={staticFile(edl.marca.simbolo)} style={{position: 'absolute', left: W - 64 - 68, top: 54, width: 68, height: 68, opacity: 0.92 * easeInOut(k)}} />;
};
