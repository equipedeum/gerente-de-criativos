// EDL gerado por work/yt/montar.py -> remotion/public-yt/<id>/edl.json (quadros no fps da gravação)
export type Seg = {o0: number; o1: number; f0: number};
export type Plano = {o0: number; o1: number; tipo: string; z0: number; z1: number; fx: number; fy: number};
export type Item = {
  tipo: 'titulo' | 'check' | 'chip' | 'numero' | 'passo' | 'infinito' | 'seta' | 'logo';
  o: number; texto?: string; tam?: number; risco?: number; sufixo?: string;
};
export type Painel = {o0: number; o1: number; rotulo: string; itens: Item[]; ate_capitulo: boolean};
export type Selo = {o0: number; o1: number; texto: string; tam: number; legenda: string};
export type Cap = {o0: number; o1: number; num: string; titulo: string};
export type Marca = {
  papel: string; tinta: string; destaque: string; cinza: string; nome: string; slogan: string;
  logo: string; simbolo: string; fontes: Partial<Record<'serif' | 'serif_bold' | 'italico' | 'sans' | 'sans_bold', string>>;
};
export type EDL = {
  id: string; titulo: string; fps: number; frames: number; fala_fim: number; marca: Marca;
  segs: Seg[]; planos: Plano[]; paineis: Painel[]; selos: Selo[]; caps: Cap[];
  fim: {o0: number; o1: number}; marca_dagua: number[][]; folha: number[]; trans: number[];
};
