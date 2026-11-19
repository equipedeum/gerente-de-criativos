// Cores e fontes da MARCA do projeto (projeto.json -> edl.json.marca, escrito pelo work/yt/montar.py).
// As peças leem M na hora de desenhar; o componente raiz põe a marca do vídeo antes dos filhos (como o COR do Paper).
import React from 'react';
import {loadFont} from '@remotion/fonts';
import {Easing, staticFile, useCurrentFrame} from 'remotion';
import type {Marca} from './tipos';

export const M = {papel: '#F5EFE4', tinta: '#1C1A17', destaque: '#059669', cinza: '#5F584D', branco: '#FFFFFF'};
export const usarMarca = (m: Marca) => {
  M.papel = m.papel;
  M.tinta = m.tinta;
  M.destaque = m.destaque;
  M.cinza = m.cinza;
};

export const SERIF = 'YTSerif'; // títulos (padrão EB Garamond 400/700, OFL)
export const ITALICO = 'YTItalico'; // *destaque* (padrão Instrument Serif Italic, OFL)
export const SANS = 'YTSans'; // rótulos e chips (padrão Inter 400/700, OFL)

export const W = 1920;
export const H = 1080;
export const PAINEL_W = 640; // painel papel (1/3 da tela); a pessoa desliza 320 px pra direita

let carregadas: Promise<unknown> | null = null;
export const carregarFontesYT = (m: Marca) => {
  if (!carregadas) {
    const f = m.fontes;
    const L: Promise<unknown>[] = [];
    const um = (family: string, arq: string | undefined, weight: string) => {
      if (arq) L.push(loadFont({family, url: staticFile(arq), weight}));
    };
    um(SERIF, f.serif, f.serif_bold ? '400' : '100 900');
    um(SERIF, f.serif_bold, '700');
    um(ITALICO, f.italico, '100 900');
    um(SANS, f.sans, f.sans_bold ? '400' : '100 900');
    um(SANS, f.sans_bold, '700');
    carregadas = Promise.all(L);
  }
  return carregadas;
};

export const easeOut = Easing.bezier(0.2, 0.8, 0.2, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);
export const easeIn = Easing.bezier(0.5, 0, 0.75, 0);
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));

// quadro "da cena": o real, ou o que a folha de revisão manda (o <Freeze> não congela no render de sequência de PNG)
export const QuadroCtx = React.createContext<number | null>(null);
export const useQuadro = () => {
  const real = useCurrentFrame();
  const forcado = React.useContext(QuadroCtx);
  return forcado ?? real;
};
