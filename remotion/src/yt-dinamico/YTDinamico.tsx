// YouTube dinâmico (menu 11): grafismos do vídeo 16:9 em PNG TRANSPARENTE (painéis, selos, capítulos, cartão final,
// símbolo da marca). A pessoa (planos, punch-in, deslize junto com o painel) é feita em work/yt/camera.py direto da
// gravação em YUV (cor intacta) e o ffmpeg sobrepõe estes grafismos + o mix.wav.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, useCurrentFrame} from 'remotion';
import type {EDL} from './tipos';
import {carregarFontesYT, QuadroCtx, usarMarca} from './marca';
import {PainelV} from './Painel';
import {CapituloV, FimV, MarcaDagua, SeloV} from './Cartoes';

const useFontes = (edl: EDL) => {
  const [h] = useState(() => delayRender('fontes da marca'));
  useEffect(() => {
    carregarFontesYT(edl.marca).then(() => continueRender(h));
  }, [h, edl]);
};

const Camadas: React.FC<{edl: EDL}> = ({edl}) => (
  <AbsoluteFill style={{overflow: 'hidden'}}>
    {edl.paineis.map((p) => (
      <PainelV key={p.o0} edl={edl} pn={p} />
    ))}
    {edl.selos.map((s) => (
      <SeloV key={s.o0} s={s} />
    ))}
    <MarcaDagua edl={edl} />
    {edl.caps.map((c) => (
      <CapituloV key={c.o0} edl={edl} c={c} />
    ))}
    <FimV edl={edl} />
  </AbsoluteFill>
);

// graf: um quadro por quadro do vídeo (render final)
export const Grafismos: React.FC<{edl: EDL}> = ({edl}) => {
  usarMarca(edl.marca);
  useFontes(edl);
  return <Camadas edl={edl} />;
};

// graf-folha / graf-trans: quadro i = grafismo congelado no tempo edl[lista][i] (folha de revisão)
export const GrafLista: React.FC<{edl: EDL; lista: 'folha' | 'trans'}> = ({edl, lista}) => {
  usarMarca(edl.marca);
  useFontes(edl);
  const f = useCurrentFrame();
  const t = edl[lista][Math.min(f, edl[lista].length - 1)];
  return (
    <QuadroCtx.Provider value={t}>
      <Camadas edl={edl} />
    </QuadroCtx.Provider>
  );
};
