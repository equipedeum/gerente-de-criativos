// Registro dos vídeos no estilo papel. A composição recebe só o nome (props do Remotion precisam ser JSON).
// Vídeo novo: criar <id>.tsx (molde: demo.tsx), importar aqui e pôr na lista PAPEIS.
//   import {demo} from './demo';
//   export const PAPEIS: VideoPapel[] = [demo];
import type {VideoPapel} from '../PaperVideo';

export const PAPEIS: VideoPapel[] = [];
export const papelPorNome = (nome: string) => {
  const v = PAPEIS.find((p) => p.nome === nome);
  if (!v) throw new Error(`vídeo papel não registrado: ${nome}`);
  return v;
};
