// Entrada PRÓPRIA do YouTube dinâmico (menu 11), como a da Animação viral: não passa pelo src/Root.tsx e usa uma pasta
// public enxuta POR VÍDEO, remotion/public-yt/<id>/ (edl.json + mix.wav + fontes + logo, escrita pelo work/yt/montar.py).
// O EDL é lido do public na hora (calculateMetadata): vídeo novo não precisa ser registrado aqui.
//   render final: bash work/yt/render.sh <id>
//   revisão     : bash work/yt/folha.sh <id> folha|trans | trecho <a>-<b> | still <quadro>
import React from 'react';
import {CalculateMetadataFunction, Composition, registerRoot, staticFile} from 'remotion';
import {GrafLista, Grafismos} from './YTDinamico';
import type {EDL} from './tipos';

type P = {edl: EDL | null};
type PL = {edl: EDL | null; lista: 'folha' | 'trans'};
const lerEDL = async (): Promise<EDL> => (await fetch(staticFile('edl.json'))).json();
const meta: CalculateMetadataFunction<P> = async () => {
  const edl = await lerEDL();
  return {durationInFrames: edl.frames, fps: edl.fps, props: {edl}};
};
const metaLista =
  (lista: 'folha' | 'trans'): CalculateMetadataFunction<PL> =>
  async () => {
    const edl = await lerEDL();
    return {durationInFrames: Math.max(1, edl[lista].length), fps: edl.fps, props: {edl, lista}};
  };
const G: React.FC<P> = ({edl}) => (edl ? <Grafismos edl={edl} /> : null);
const GL: React.FC<PL> = ({edl, lista}) => (edl ? <GrafLista edl={edl} lista={lista} /> : null);

const Root: React.FC = () => (
  <>
    <Composition id="graf" component={G} width={1920} height={1080} defaultProps={{edl: null}} calculateMetadata={meta} />
    <Composition
      id="graf-folha"
      component={GL}
      width={1920}
      height={1080}
      defaultProps={{edl: null, lista: 'folha' as const}}
      calculateMetadata={metaLista('folha')}
    />
    <Composition
      id="graf-trans"
      component={GL}
      width={1920}
      height={1080}
      defaultProps={{edl: null, lista: 'trans' as const}}
      calculateMetadata={metaLista('trans')}
    />
  </>
);

registerRoot(Root);
