// Composição do estilo papel (Editor Paper): papel amassado em cima com recortes animados, o apresentador embaixo
// (16:9 recortado 1080x960 na escala 1:1), borda rasgada na divisória e legenda karaokê sobre ela.
import React, {createContext, useContext} from 'react';
import {AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, staticFile, useVideoConfig} from 'remotion';
import {COR, FONTE, LAYOUT} from './estilo';
import {Etiqueta, EtiquetaSecao, Peca} from './pecas';
import {larguraTexto, linhaRasgada, rampa, rng, useT} from './tempo';
import {papelPorNome} from './videos';
import AJUSTE_EARSHOT from './sfx-earshot.json';

export type PalavraLeg = {w: string; l: number; s: number; e: number};
export type BlocoLeg = {s: number; e: number; txt: string; palavras: PalavraLeg[]};

export type VideoPapel = {
  nome: string;
  duracao: number; // s
  video: string; // em public/: 16:9 1920x1080 já cortado (sem áudio)
  voz: string; // em public/: voz tratada
  rosto: {x: number; y: number}; // centro do rosto no 16:9
  topoRecorte?: number; // linha do 16:9 que encosta na divisória (padrão 40)
  // Gravação de celular (vertical): `video` já vem recortado em 1080x980 seguindo o rosto (preparar_paper.py) e é
  // colado direto embaixo; `rosto.y` = altura do rosto no recorte (392 = 40 % no padrão; selfie bem perto usam 559 = 57 %).
  recortado?: boolean;
  // Só recortado: outra janela do mesmo vídeo pros formatos YT/IN/GL (rosto mais alto, legenda fora do queixo), com o y do rosto nela.
  formatosVideo?: {video: string; rostoY: number};
  // IN: y onde começa a pessoa (padrão 655). Selfie bem perto (selfie bem perto): a pessoa precisa de mais altura pra caber
  // inteira em escala 1 sem fundo desfocado; o papel encolhe junto.
  divisaoIN?: number;
  // RL: y da borda rasgada (padrão LAYOUT.divisoria = 960) e altura do vídeo recortado (padrão 980). Selfie bem perto
  // (selfie bem perto): borda em 880 e recorte 1080x1060, pra sobrar cabelo abaixo da legenda; o papel encolhe junto.
  divisaoRL?: number;
  // IN igual ao GL (selfie bem perto, 22/10/2026, usuário: "faz esse similar a como faz com o GL"): papel em tela cheia alternando
  // com a pessoa em tela cheia nos trechos `pessoaGL`; `video` = recorte 1080x1350 (escala natural) com o rosto em `rostoY`.
  inComoGL?: {video: string; rostoY: number};
  altoRL?: number;
  // ênfase: corte seco com zoom no rosto. `origem: 'topo'` amplia a partir da linha de cima do vídeo (a cabeça desce em
  // vez de subir) — usar em plano já fechado, onde o zoom no rosto empurra o cabelo pra baixo da borda.
  punch?: {s: number; e: number; zoom?: number; origem?: 'rosto' | 'topo'}[];
  // Trechos em que o vídeo desce `dy` px no RL (máx. ~50: acima disso aparece o fundo sob a borda). Tratado 16:9 de
  // estúdio com plano fechado embutido deixa o cabelo colado na borda/legenda (t1, 12/10/2026).
  desce?: {s: number; e: number; dy: number}[];
  // Só nos formatos YT/IN/GL: px extras de descida (somados ao `desce` convertido), onde a pessoa se inclina e o
  // cabelo some sob o rasgo/borda apesar do RL estar ok (t1 IN, final).
  desceFormatos?: {s: number; e: number; dy: number}[];
  // Só no IN (faixa da pessoa ~675 px): escala `s` do 16:9, `topo` = y (na caixa) da linha de cima do vídeo e teto do
  // punch-in. Tratado sem folga em cima (t1): a pessoa encolhe pra caber testa→peito abaixo da legenda e a sobra entre
  // o rasgo e o topo do vídeo é preenchida com o próprio vídeo ampliado e desfocado (t1 IN v3, 12/10/2026).
  // `fonte` (só recortado): outro arquivo pro IN, com o y do rosto e a altura dele (selfie bem perto usam o mesmo do RL).
  formatoIN?: {s: number; topo: number; zoomMax?: number; fonte?: {video: string; rostoY: number; alto: number}};
  legenda: BlocoLeg[];
  semLegenda?: boolean;
  // Etiqueta de seção no canto ("06/10 NA PRÁTICA"): DESLIGADA por padrão desde 08/10/2026 ("tira isso",
  // regra geral do usuário). Só ligar se ele pedir.
  etiquetas?: boolean;
  // Efeitos sonoros (teste de 08/10/2026 no Criativo 52: "volume baixo pra não chamar mais atenção do que deveria, a
  // voz é o principal"). `som` = arquivo na pasta do kit (`kitSfx`, abaixo); `vol` multiplica o ganho do som.
  sfx?: {t: number; som: Som; vol?: number}[];
  // Pasta do kit em public/ (08/11/2026): padrão 'sfx-earshot' (kit do Earshot, scripts/sfx_earshot.py); os vídeos que
  // já existiam em 08/11 (KIT_ANTIGO) continuam no kit antigo 'sfx' (scripts/sfx.py), pra correção não mudar o som aprovado.
  kitSfx?: KitSfx;
  volumeSfx?: number; // ganho geral dos efeitos (padrão 0.18 ≈ −15 dB; picos ~−18 a −22 dBFS, bem abaixo da voz)
  // GL (quadrado): trechos em que a pessoa aparece em tela cheia (no resto, o papel em tela cheia). scripts/sfx_auto.py
  // escolhe esses trechos nas pausas entre animações, pra nenhum recorte entrar escondido.
  pessoaGL?: [number, number][];
  // Inserto da plataforma (13/10/2026, cola do lote): vídeo sem áudio (em public/) no lugar da pessoa de `s` a `e`
  // (RL/YT/IN: recorte centrado na caixa da pessoa; GL: tela cheia), corte seco; a voz e a legenda continuam.
  inserto?: {s: number; e: number; src: string};
  // 3 MODOS no RL (26/10/2026, regra do usuário pra Hyperframe/Paper/VOX): tela dividida (padrão), pessoa em TELA CHEIA
  // numa frase de conversa e papel em TELA CHEIA numa seção. `pessoa`: nº da seção (1 = a 1ª <Secao> das Cenas) ou
  // trecho [s, e] em segundos; `papel`: nºs de seção. Sem `modos` (ou sem uma das listas) = automático: pessoa cheia
  // nos trechos do `pessoaGL` (uma frase cada, fora da 1ª seção e das 2 últimas, até ~1 a cada 4 seções) e papel cheio
  // ~1 a cada 5 seções (3ª, 8ª, 13ª… sem abertura/CTA, sem bater com pessoa cheia nem com o inserto). `desligado` = só dividida.
  // `papel` também aceita trecho [s, e] em segundos (02/11/2026: papel cheio onde o vídeo tem texto gravado).
  modos?: {desligado?: boolean; pessoa?: (number | [number, number])[]; papel?: (number | [number, number])[]};
  // Trilha do rosto (cx no 16:9) pro pessoa cheia do RL: scripts/trilha_cheio.py <id> → <id>-cheio.json. Sem ela, rosto.x fixo.
  rostoCheio?: {dt: number; cx: number[]};
  // Centro da legenda na pessoa em TELA CHEIA do RL (padrão Y_LEG_CHEIO.pessoa = 1330). Plano aberto (12/11/2026, regra: legenda
  // nunca baixo demais) usa 1195 -> base do texto ≤ ~1235 (65 % = 1248), no peito. Opcional: vídeos antigos não mudam.
  yLegPessoa?: number;
  // Só recortado (celular, selfie na mão, 27/10/2026): o vertical INTEIRO 1080x1920 pro pessoa em TELA CHEIA do RL (a janela 9:16
  // do 16:9 não existe na selfie); `rostoY` = y do rosto nele. Com ele, a pessoa cheio automático vale também pro recortado.
  cheioVertical?: {video: string; rostoY: number};
  // Sem zoom nenhum na pessoa (selfie na mão, 27/10/2026, usuário: gravação já feita na mão, a câmera já se mexe): desliga o
  // zoom leve contínuo em todos os formatos; os 3 modos do RL continuam.
  semZoom?: boolean;
  // Plano ABERTO (02/11/2026: pessoa sentada à mesa, rosto pequeno no 16:9). Só no RL dividido: o recorte
  // amplia `zoom` (base, × punch × zoom leve) e segue a `trilha` do rosto (cx, cy no 16:9 a cada dt s, suavizada), com o
  // topo da cabeça (= cy − `cabeca`) sempre `folga` px abaixo da borda rasgada; o zoom parte do topo da cabeça, então
  // punch-in nunca esconde a cabeça sob o rasgo. Campo opcional: vídeos antigos não mudam.
  aberto?: {zoom: number; cabeca: number; folga?: number; trilha: {dt: number; cx: number[]; cy: number[]}};
  // Cor de destaque da marca (19/11/2026): karaokê, carimbos, setas, botão etc. `escuro` = sombra do Botao. Sem o campo =
  // verde padrão. O molde preenche com o `cor_destaque` do projeto.json (escuro = a mesma cor ~35 % mais escura).
  destaque?: {cor: string; escuro: string};
  // IN com os 3 MODOS do RL (19/11/2026; regras "3 modos" e "a pessoa aparece cheia em todo formato"): o IN segue o mesmo
  // plano de modos do RL (planoModos) — pessoa em TELA CHEIA 1080x1350 (16:9 ampliado 1,25x, zoom leve, legenda em
  // `yLegPessoa`), papel em TELA CHEIA (painel 1080x960 em `dyPapel`, legenda em `yLegPapel`) e a tela dividida de sempre
  // no resto. Sons mudos na pessoa cheia. Só fonte 16:9 (não recortado). Campo opcional: vídeos antigos não mudam.
  modosIN?: {yLegPessoa?: number; dyPapel?: number; yLegPapel?: number};
  // x do centro da legenda na pessoa em TELA CHEIA do RL (padrão 540): microfone de um lado = legenda um pouco pro outro.
  xLegPessoa?: number;
  // Só no IN dividido: escala `s` e y `dy` do painel 1080x960 (centrado na horizontal). Padrão 0,85 e −164 (o painel do
  // y 190 pra baixo). Use quando peças perto do topo do painel (y ~140) saírem cortadas no IN. Opcional: o RL não muda.
  papelIN?: {s: number; dy: number};
  Cenas: React.FC;
};
const DESTAQUE_PADRAO = {cor: COR.destaque, escuro: COR.destaqueEscuro};

// Zoom leve contínuo na pessoa (RL e YT; 26/10/2026): 1,00 ↔ 1,06 num ciclo de 7 s, senoidal — nunca para mais de 4 s.
export const zoomLeve = (t: number) => 1 + 0.03 * (1 - Math.cos((2 * Math.PI * t) / 7));

export type Som = 'pop' | 'clique' | 'whoosh' | 'ping' | 'papel' | 'carimbo' | 'tesoura' | 'tique';
// Ganho relativo de cada som (equaliza o que "pesa" mais no ouvido).
const GANHO: Record<Som, number> = {papel: 0.9, pop: 0.55, clique: 0.8, whoosh: 0.45, ping: 0.4, carimbo: 1.0, tesoura: 0.75, tique: 0.6};

// Kit de sons (08/11/2026, usuário: "se temos ele OK, use essa skill também com o paper"): mesmos nomes nas duas pastas.
// Trocar o padrão de volta = KIT_SFX = 'sfx'. public/sfx/ fica como reserva, não apagar.
export type KitSfx = 'sfx' | 'sfx-earshot';
export const KIT_SFX: KitSfx = 'sfx-earshot';
// Vídeos que devem seguir no kit antigo (public/sfx) se forem re-renderizados: pôr 'paper-<id>' aqui.
const KIT_ANTIGO = new Set<string>([]);
export const kitDe = (v: VideoPapel): KitSfx => v.kitSfx ?? (KIT_ANTIGO.has(v.nome) ? 'sfx' : KIT_SFX);
// Kit Earshot: fator por som que o pico de -1 dBFS não deixou na mesma loudness do antigo (gerado por sfx_earshot.py).
const ajusteKit = (kit: KitSfx, som: Som) => (kit === 'sfx-earshot' ? (AJUSTE_EARSHOT as Partial<Record<Som, number>>)[som] ?? 1 : 1);

const Efeitos: React.FC<{v: VideoPapel; mudo?: [number, number][]}> = ({v, mudo = []}) => {
  const {fps} = useVideoConfig();
  const geral = v.volumeSfx ?? 0.18;
  const kit = kitDe(v);
  // no GL, animação escondida atrás da pessoa não faz barulho
  // regra (Extremo → Paper, 08/11/2026): som só quando algo aparece/marca/muda NA TELA daquele formato — nos trechos em
  // que o papel não aparece (pessoa cheia no RL, pessoa/inserto em tela cheia no GL) fica mudo. "papel" vetado (12/10).
  const lista = (v.sfx ?? []).filter((e) => !mudo.some(([a, b]) => e.t >= a && e.t < b) && !(kit === 'sfx-earshot' && e.som === 'papel'));
  return (
    <>
      {lista.map((e, i) => (
        <Sequence key={i} from={Math.max(0, Math.round(e.t * fps))} durationInFrames={Math.round(1.4 * fps)} layout="none">
          <Audio src={staticFile(`${kit}/${e.som}.wav`)} volume={geral * GANHO[e.som] * ajusteKit(kit, e.som) * (e.vol ?? 1)} />
        </Sequence>
      ))}
    </>
  );
};

// Inserto numa caixa (objectFit cover, centrado), só entre inserto.s e inserto.e; o vídeo começa do 0 em inserto.s.
const InsertoCaixa: React.FC<{v: VideoPapel; c: Caixa}> = ({v, c}) => {
  const {fps} = useVideoConfig();
  if (!v.inserto) return null;
  const {s, e, src} = v.inserto;
  return (
    <Sequence from={Math.round(s * fps)} durationInFrames={Math.round((e - s) * fps)} layout="none">
      <div style={{position: 'absolute', left: c.x, top: c.y, width: c.w, height: c.h, overflow: 'hidden', background: '#111'}}>
        <OffthreadVideo src={staticFile(src)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </div>
    </Sequence>
  );
};
const mudoInserto = (v: VideoPapel): [number, number][] => (v.inserto ? [[v.inserto.s, v.inserto.e]] : []);

const Y_BORDA = LAYOUT.divisoria + 8; // a borda rasgada oscila em torno daqui

// ---------- apresentador ----------

// trilha amostrada a cada dt s -> valor interpolado em t
const naTrilha = (l: number[], dt: number, t: number) => {
  const i = Math.max(0, Math.min(l.length - 1.001, t / dt));
  const i0 = Math.floor(i);
  return l[i0] + (l[Math.min(l.length - 1, i0 + 1)] - l[i0]) * (i - i0);
};

// Plano aberto (ver VideoPapel.aberto): recorte ampliado seguindo o rosto, topo da cabeça fixo abaixo da borda.
const ApresentadorAberto: React.FC<{v: VideoPapel}> = ({v}) => {
  const {t} = useT();
  const ab = v.aberto!;
  const div = v.divisaoRL ?? LAYOUT.divisoria;
  const caixaTopo = div - 20;
  const cx = naTrilha(ab.trilha.cx, ab.trilha.dt, t);
  const cy = naTrilha(ab.trilha.cy, ab.trilha.dt, t);
  const yCab = div - caixaTopo + (ab.folga ?? 60); // topo da cabeça na caixa
  const p = (v.punch ?? []).find((q) => t >= q.s && t < q.e);
  const z = ab.zoom * (p ? p.zoom ?? 1.12 : 1) * (v.semZoom ? 1 : zoomLeve(t));
  return (
    <div style={{position: 'absolute', left: 0, top: caixaTopo, width: 1080, height: LAYOUT.altura - caixaTopo, overflow: 'hidden', background: '#111'}}>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${z})`, transformOrigin: `540px ${yCab}px`}}>
        <OffthreadVideo src={staticFile(v.video)} muted style={{position: 'absolute', left: 540 - cx, top: yCab - (cy - ab.cabeca), width: 1920, height: 1080}} />
      </div>
    </div>
  );
};

const Apresentador: React.FC<{v: VideoPapel}> = ({v}) => {
  const {t} = useT();
  if (v.aberto) return <ApresentadorAberto v={v} />;
  const topo = v.topoRecorte ?? 40;
  const cx = v.rosto.x;
  const div = v.divisaoRL ?? LAYOUT.divisoria;
  const caixaTopo = div - 20; // começa um pouco atrás da borda
  const left = 540 - cx;
  const top = div - caixaTopo - topo;
  const p = (v.punch ?? []).find((q) => t >= q.s && t < q.e);
  const z = (p ? p.zoom ?? 1.2 : 1) * (v.modos?.desligado || v.semZoom ? 1 : zoomLeve(t));
  const dy = (v.desce ?? []).find((q) => t >= q.s && t < q.e)?.dy ?? 0;
  const ox = 540;
  const oy = p?.origem === 'topo' ? (v.recortado ? 0 : top) : v.recortado ? v.rosto.y : top + v.rosto.y;
  return (
    <div style={{position: 'absolute', left: 0, top: caixaTopo, width: 1080, height: LAYOUT.altura - caixaTopo, overflow: 'hidden', background: '#111'}}>
      <div style={{position: 'absolute', inset: 0, transform: `${dy ? `translateY(${dy}px) ` : ''}scale(${z})`, transformOrigin: `${ox}px ${oy}px`}}>
        {v.recortado ? (
          <OffthreadVideo src={staticFile(v.video)} muted style={{position: 'absolute', left: 0, top: 0, width: 1080, height: v.altoRL ?? 980}} />
        ) : (
          <OffthreadVideo src={staticFile(v.video)} muted style={{position: 'absolute', left, top, width: 1920, height: 1080}} />
        )}
      </div>
    </div>
  );
};

// ---------- papel e borda rasgada ----------

const bordaPadrao = linhaRasgada(1080, Y_BORDA, 4242, 9, 8, 20);

const Papel: React.FC<{div?: number; children: React.ReactNode}> = ({div, children}) => {
  const yb = div === undefined ? Y_BORDA : div + 8;
  const pontosBorda = div === undefined ? bordaPadrao : linhaRasgada(1080, yb, 4242, 9, 8, 20);
  const pontosFibra = pontosBorda.map(([x, y], i) => [x, y + 4 + ((i * 37) % 7)] as [number, number]);
  // painel 1080x960 encolhido pra caber acima da borda quando ela sobe (centrado na horizontal)
  const sp = div === undefined ? 1 : Math.min(1, div / LAYOUT.divisoria);
  const clip = `polygon(0px 0px, 1080px 0px, ${[...pontosBorda].reverse().map(([x, y]) => `${x.toFixed(1)}px ${y.toFixed(1)}px`).join(', ')})`;
  const fibra = `M0,0 ${pontosFibra.map(([x, y]) => `L${x.toFixed(1)},${y.toFixed(1)}`).join(' ')} L1080,0 Z`;
  return (
    <>
      {/* sombra que o papel projeta no vídeo + fibra branca do rasgo */}
      <svg width={1080} height={yb + 60} style={{position: 'absolute', left: 0, top: 0}}>
        <defs>
          <filter id="sombraBorda" x="-10%" y="-10%" width="120%" height="140%">
            <feGaussianBlur stdDeviation="7" />
          </filter>
        </defs>
        <path d={fibra} transform="translate(0,10)" fill="rgba(0,0,0,0.55)" filter="url(#sombraBorda)" />
        <path d={fibra} fill="#FBF9F3" />
      </svg>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: yb + 20, clipPath: clip, overflow: 'hidden'}}>
        <Img src={staticFile('paper/papel.jpg')} style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1000}} />
        <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 960, transform: sp < 1 ? `translate(${(1080 * (1 - sp)) / 2}px, 0px) scale(${sp})` : undefined, transformOrigin: '0px 0px'}}>{children}</div>
      </div>
    </>
  );
};

// ---------- legenda karaokê ----------

const LegendaPapel: React.FC<{blocos: BlocoLeg[]; cx?: number; cy?: number; escala?: number}> = ({blocos, cx = 540, cy = LAYOUT.divisoria, escala = 1}) => {
  const {t} = useT();
  const ANTES = 0.04;
  let i = -1;
  for (let k = 0; k < blocos.length; k++) {
    if (t >= blocos[k].s - ANTES) i = k;
    else break;
  }
  if (i < 0) return null;
  const b = blocos[i];
  if (t > b.e + 0.9) return null; // pausa longa: some
  const r = rng(i * 7 + 3);
  const rot = (r() - 0.5) * 4.4;
  const dx = (r() - 0.5) * 18;
  const dy = (r() - 0.5) * 10;
  const linhas = b.txt.split('|').map((l) => l.trim().toUpperCase());
  const maior = Math.max(...linhas.map((l) => larguraTexto(l, `900 100px ${FONTE.pesada}`)));
  // ≥ ~100 px de cada lateral (usuário, 23/10/2026): texto ≤ 780 px + padding (0,72·tam) + jitter ≈ 850 px no máximo
  const tam = Math.min(84, (780 / maior) * 100);
  const ativa = [...b.palavras].reverse().find((p) => t >= p.s - 0.02) ?? b.palavras[0];
  const pop = 0.86 + 0.14 * rampa(t, b.s - ANTES, 0.1, Easing.out(Easing.back(2)));
  return (
    <div
      style={{
        position: 'absolute',
        left: cx + dx,
        top: cy + dy,
        transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${pop * escala})`,
        background: COR.creme,
        padding: `${tam * 0.17}px ${tam * 0.36}px ${tam * 0.1}px`,
        boxShadow: '0 8px 18px rgba(0,0,0,0.38), 0 2px 3px rgba(0,0,0,0.2)',
        fontFamily: FONTE.pesada,
        fontWeight: 900,
        fontSize: tam,
        lineHeight: 1.02,
        letterSpacing: '0.005em',
        textAlign: 'center',
        whiteSpace: 'nowrap',
      }}
    >
      {linhas.map((_, li) => (
        <div key={li}>
          {b.palavras
            .filter((p) => p.l === li)
            .map((p, k) => (
              <span key={k} style={{color: p === ativa ? COR.destaque : COR.navy}}>
                {k > 0 ? ' ' : ''}
                {p.w.toUpperCase()}
              </span>
            ))}
        </div>
      ))}
    </div>
  );
};

// ---------- seções ----------

// Uma seção: etiqueta no canto (cai girando; numerada "01/08" quando há `num`) + recortes que se acumulam.
// Na troca (refs de 08/10/2026), a cena que sai ENCOLHE e escorrega pra baixo à esquerda em 0,32 s enquanto a
// seção nova já começa por cima.
const SAIDA_SECAO = 0.3;
const EtiquetasCtx = createContext(false);
// Formato em render (RL/YT/IN/GL): permite ajuste fino de posição por formato dentro das Cenas de um vídeo.
const FormatoCtx = createContext<Formato>('RL');
export const useFormato = () => useContext(FormatoCtx);
// `saidaCentro` (26/10/2026): a cena que sai só encolhe pro centro (sem escorregar pra fora da tela) — usar quando
// peças perto da borda esquerda sairiam cortadas na troca (regra dos ~100 px das laterais).
export const Secao: React.FC<{s: number; e: number; tag?: string; num?: number; total?: number; corTag?: 'navy' | 'destaque' | 'azul'; saidaCentro?: boolean; children?: React.ReactNode}> = ({
  s, e, tag, num, total, corTag = 'navy', saidaCentro, children,
}) => {
  const {t} = useT();
  const comEtiqueta = useContext(EtiquetasCtx);
  if (t < s || t >= e + SAIDA_SECAO) return null;
  const p = t >= e ? rampa(t, e, SAIDA_SECAO, Easing.inOut(Easing.cubic)) : 0;
  return (
    <>
      {comEtiqueta && tag && t < e ? (
        <Peca x={LAYOUT.etiquetaX} y={LAYOUT.etiquetaY} t={s} entrada="cai" rot={-1.2} ancora="topoEsq" z={50}>
          {num !== undefined ? <EtiquetaSecao txt={tag} num={num} total={total} /> : <Etiqueta txt={tag} cor={corTag} tam={30} />}
        </Peca>
      ) : null}
      <div style={{position: 'absolute', inset: 0, transformOrigin: saidaCentro ? '50% 55%' : '15% 90%', transform: p > 0 ? (saidaCentro ? `scale(${1 - 0.6 * p})` : `translate(${-560 * p}px, ${360 * p}px) scale(${1 - 0.6 * p})`) : undefined, opacity: 1 - p * p}}>
        {children}
      </div>
    </>
  );
};

// ---------- outros formatos (YT 1920x1080, IN 1080x1350, GL 1080x1080) ----------
// Mesma lógica aprovada no formato antigo (skill video-dividido-hyperframes): YT = papel e pessoa lado a lado (rasgo
// vertical), IN = dividido no meio, GL = sem divisão, alternando pessoa em tela cheia e papel em tela cheia.
export type Formato = 'RL' | 'YT' | 'IN' | 'GL';
export const DIM: Record<Formato, [number, number]> = {RL: [1080, 1920], YT: [1920, 1080], IN: [1080, 1350], GL: [1080, 1080]};
type Caixa = {x: number; y: number; w: number; h: number};

// Pessoa numa caixa: o rosto (âncora) do vídeo fonte cai em (fx, fy) da caixa, na escala s; punch-in em volta dele.
// `kDesce`: quanto do `desce` do RL vale nesta caixa (limitado à sobra de vídeo acima, pra não mostrar fundo preto);
// `punchTopo` (IN, YT): todo punch amplia do topo, senão o cabelo some sob o rasgo. Punch com `origem: 'topo'` amplia a partir da linha de cima do vídeo, como no RL (t1, 12/10/2026).
const PessoaCaixa: React.FC<{v: VideoPapel; c: Caixa; s: number; fx: number; fy: number; kDesce?: number; punchTopo?: boolean; zoomMax?: number; fundo?: boolean; leve?: boolean; fonte?: {video: string; rostoY: number; alto: number}}> = ({
  v, c, s, fx, fy, kDesce = 1, punchTopo = false, zoomMax = 9, fundo = false, leve = false, fonte,
}) => {
  const {t} = useT();
  const p = (v.punch ?? []).find((q) => t >= q.s && t < q.e);
  const z = (p ? Math.min(zoomMax, p.zoom ?? 1.2) : 1) * (leve && !v.modos?.desligado && !v.semZoom ? zoomLeve(t) : 1);
  const fv = v.recortado ? fonte ?? v.formatosVideo : undefined;
  const src = fv?.video ?? v.video;
  const [nw, nh, ax, ay] = v.recortado ? [1080, fonte?.alto ?? 980, 540, fv?.rostoY ?? v.rosto.y] : [1920, 1080, v.rosto.x, v.rosto.y];
  const topoVid = fy - ay * s;
  const d0 = (v.desce ?? []).find((q) => t >= q.s && t < q.e)?.dy ?? 0;
  const d1 = (v.desceFormatos ?? []).find((q) => t >= q.s && t < q.e)?.dy ?? 0;
  const dy = d0 || d1 ? Math.max(0, Math.min(-topoVid, d0 * kDesce + d1)) : 0;
  const oy = p?.origem === 'topo' || punchTopo ? Math.max(0, topoVid + dy) : fy;
  return (
    <div style={{position: 'absolute', left: c.x, top: c.y, width: c.w, height: c.h, overflow: 'hidden', background: '#111'}}>
      {fundo ? (
        // sobra acima do vídeo: o próprio vídeo ampliado 1,6x e desfocado (parede escura), em vez de faixa preta
        <OffthreadVideo
          src={staticFile(src)}
          muted
          style={{position: 'absolute', left: fx - ax * s * 1.6, top: fy - ay * s * 1.6, width: nw * s * 1.6, height: nh * s * 1.6, filter: 'blur(28px) brightness(0.8)'}}
        />
      ) : null}
      <div style={{position: 'absolute', inset: 0, transform: `${dy ? `translateY(${dy}px) ` : ''}scale(${z})`, transformOrigin: `${fx}px ${oy}px`}}>
        <OffthreadVideo src={staticFile(src)} muted style={{position: 'absolute', left: fx - ax * s, top: fy - ay * s, width: nw * s, height: nh * s}} />
      </div>
    </div>
  );
};

// Papel numa caixa, com rasgo embaixo, à direita ou sem rasgo; o painel 1080x960 entra escalado/deslocado.
const PapelCaixa: React.FC<{c: Caixa; rasgo: 'baixo' | 'direita' | null; s: number; dx: number; dy: number; children: React.ReactNode}> = ({c, rasgo, s, dx, dy, children}) => {
  let clip: string | undefined;
  let fibra: string | null = null;
  let sombra = '';
  if (rasgo === 'baixo') {
    const pts = linhaRasgada(c.w, c.h - 6, 4242, 9, 8, 20);
    clip = `polygon(0px 0px, ${c.w}px 0px, ${[...pts].reverse().map(([x, y]) => `${x.toFixed(1)}px ${y.toFixed(1)}px`).join(', ')})`;
    fibra = `M0,0 ${pts.map(([x, y], i) => `L${x.toFixed(1)},${(y + 4 + ((i * 37) % 7)).toFixed(1)}`).join(' ')} L${c.w},0 Z`;
    sombra = 'translate(0,10)';
  } else if (rasgo === 'direita') {
    const pts = linhaRasgada(c.h, c.w - 6, 5151, 9, 8, 20).map(([a, b]) => [b, a] as [number, number]);
    clip = `polygon(0px 0px, ${pts.map(([x, y]) => `${x.toFixed(1)}px ${y.toFixed(1)}px`).join(', ')}, 0px ${c.h}px)`;
    fibra = `M0,0 ${pts.map(([x, y], i) => `L${(x + 4 + ((i * 37) % 7)).toFixed(1)},${y.toFixed(1)}`).join(' ')} L0,${c.h} Z`;
    sombra = 'translate(10,0)';
  }
  return (
    <div style={{position: 'absolute', left: c.x, top: c.y, width: c.w + 60, height: c.h + 60}}>
      {fibra ? (
        <svg width={c.w + 60} height={c.h + 60} style={{position: 'absolute', left: 0, top: 0}}>
          <defs>
            <filter id="sombraBordaF" x="-10%" y="-10%" width="120%" height="140%">
              <feGaussianBlur stdDeviation="7" />
            </filter>
          </defs>
          <path d={fibra} transform={sombra} fill="rgba(0,0,0,0.55)" filter="url(#sombraBordaF)" />
          <path d={fibra} fill="#FBF9F3" />
        </svg>
      ) : null}
      <div style={{position: 'absolute', left: 0, top: 0, width: c.w, height: c.h, clipPath: clip, overflow: 'hidden'}}>
        <Img src={staticFile('paper/papel.jpg')} style={{position: 'absolute', left: 0, top: 0, width: c.w, height: c.h, objectFit: 'cover'}} />
        <div style={{position: 'absolute', left: dx, top: dy, width: 1080, height: 960, transform: `scale(${s})`, transformOrigin: '0 0'}}>{children}</div>
      </div>
    </div>
  );
};

const PaperFormato: React.FC<{v: VideoPapel; f: Exclude<Formato, 'RL'>}> = ({v, f}) => {
  const {t} = useT();
  const {Cenas} = v;
  const cenas = (
    <FormatoCtx.Provider value={f}>
      <EtiquetasCtx.Provider value={v.etiquetas ?? false}>
        <Cenas />
      </EtiquetasCtx.Provider>
    </FormatoCtx.Provider>
  );
  // YT/GL: rosto em y=432, mas se o rosto está alto no 16:9 o topo do vídeo ficava abaixo da caixa (faixa #111 de
  // ~41 px no t9, rosto.y 354; 14/10/2026). Sobe o necessário pro vídeo cobrir o topo.
  const fyCheio = v.recortado ? Math.floor(((v.formatosVideo?.rostoY ?? v.rosto.y) * 1080) / 980) : Math.min(432, Math.floor((v.rosto.y * 1080) / 980));
  const leg = (cx: number, cy: number, escala: number) => (v.semLegenda ? null : <LegendaPapel blocos={v.legenda} cx={cx} cy={cy} escala={escala} />);
  if (f === 'YT') {
    return (
      <AbsoluteFill style={{background: '#111'}}>
        <PessoaCaixa v={v} c={{x: 940, y: 0, w: 980, h: 1080}} s={1080 / 980} fx={520} fy={fyCheio} punchTopo leve />
        <InsertoCaixa v={v} c={{x: 940, y: 0, w: 980, h: 1080}} />
        <Audio src={staticFile(v.voz)} />
        <Efeitos v={v} />
        <PapelCaixa c={{x: 0, y: 0, w: 968, h: 1080}} rasgo="direita" s={0.87} dx={14} dy={57}>
          {cenas}
        </PapelCaixa>
        {leg(960, 905, 0.92)}
      </AbsoluteFill>
    );
  }
  if (f === 'IN' && v.inComoGL) {
    const pessoaIN = (v.pessoaGL ?? []).some(([a, b]) => t >= a && t < b);
    return (
      <AbsoluteFill style={{background: '#111'}}>
        <PapelCaixa c={{x: 0, y: 0, w: 1080, h: 1350}} rasgo={null} s={1} dx={0} dy={150}>
          {cenas}
        </PapelCaixa>
        {pessoaIN ? (
          <PessoaCaixa v={v} c={{x: 0, y: 0, w: 1080, h: 1350}} s={1} fx={540} fy={v.inComoGL.rostoY} fonte={{...v.inComoGL, alto: 1350}} />
        ) : null}
        <InsertoCaixa v={v} c={{x: 0, y: 0, w: 1080, h: 1350}} />
        <Audio src={staticFile(v.voz)} />
        <Efeitos v={v} mudo={[...(v.pessoaGL ?? []), ...mudoInserto(v)]} />
        {leg(540, 1090, 0.95)}
      </AbsoluteFill>
    );
  }
  if (f === 'IN') {
    const dIN = v.divisaoIN ?? 655;
    const hPap = dIN + 28;
    // divisão mais alta (selfie): conteúdo do painel (y 190–860) cabe entre 40 px do topo e a faixa da legenda
    const sPap = dIN < 655 ? (dIN - 90) / 670 : (0.85 * hPap) / 683;
    // 3 modos no IN (VideoPapel.modosIN): mesmo plano do RL; sem o campo = sempre dividido (como antes)
    const mi = v.modosIN && !v.recortado ? v.modosIN : undefined;
    let modoIN: 'dividido' | 'pessoa' | 'papel' = 'dividido';
    let mudoIN: Trecho[] = [];
    if (mi) {
      const secs: Trecho[] = [];
      coletarSecoes((Cenas as (p: object) => React.ReactNode)({}), secs);
      const plano = planoModos(v, secs);
      const dentro = (l: Trecho[]) => l.some(([a, b]) => t >= a && t < b);
      modoIN = dentro(plano.pessoa) ? 'pessoa' : dentro(plano.papel) ? 'papel' : 'dividido';
      mudoIN = plano.pessoa;
    }
    if (mi && modoIN !== 'dividido') {
      const sT = 1350 / 1080;
      return (
        <AbsoluteFill style={{background: '#111'}}>
          {modoIN === 'pessoa' ? (
            // zoom leve a partir da linha de cima (punchTopo): a cabeça desce em vez de sair por cima
            <PessoaCaixa v={v} c={{x: 0, y: 0, w: 1080, h: 1350}} s={sT} fx={540} fy={v.rosto.y * sT} punchTopo leve />
          ) : (
            <PapelCaixa c={{x: 0, y: 0, w: 1080, h: 1350}} rasgo={null} s={1} dx={0} dy={mi.dyPapel ?? 150}>
              {cenas}
            </PapelCaixa>
          )}
          <Audio src={staticFile(v.voz)} />
          <Efeitos v={v} mudo={[...mudoIN, ...mudoInserto(v)]} />
          {leg(540, modoIN === 'pessoa' ? mi.yLegPessoa ?? 1000 : mi.yLegPapel ?? 1090, 0.95)}
        </AbsoluteFill>
      );
    }
    return (
      <AbsoluteFill style={{background: '#111'}}>
        {v.formatoIN ? (
          <PessoaCaixa
            v={v}
            c={{x: 0, y: dIN, w: 1080, h: 1350 - dIN}}
            s={v.formatoIN.s}
            fx={540}
            fy={v.formatoIN.topo + (v.recortado ? v.formatoIN.fonte?.rostoY ?? v.formatosVideo?.rostoY ?? v.rosto.y : v.rosto.y) * v.formatoIN.s}
            fonte={v.recortado ? v.formatoIN.fonte : undefined}
            kDesce={0}
            punchTopo
            zoomMax={v.formatoIN.zoomMax ?? 1.04}
            fundo
          />
        ) : (
          <PessoaCaixa v={v} c={{x: 0, y: dIN, w: 1080, h: 1350 - dIN}} s={1} fx={540} fy={300} kDesce={2.3} punchTopo />
        )}
        <InsertoCaixa v={v} c={{x: 0, y: dIN, w: 1080, h: 1350 - dIN}} />
        <Audio src={staticFile(v.voz)} />
        <Efeitos v={v} mudo={mudoIN} />
        <PapelCaixa
          c={{x: 0, y: 0, w: 1080, h: hPap}}
          rasgo="baixo"
          s={v.papelIN?.s ?? sPap}
          dx={(1080 - 1080 * (v.papelIN?.s ?? sPap)) / 2}
          dy={v.papelIN ? v.papelIN.dy : dIN < 655 ? 40 - 190 * sPap : hPap - 31 - 960 * sPap}
        >
          {cenas}
        </PapelCaixa>
        {leg(540, dIN + 20, 0.92)}
      </AbsoluteFill>
    );
  }
  // GL
  const pessoa = (v.pessoaGL ?? []).some(([a, b]) => t >= a && t < b);
  return (
    <AbsoluteFill style={{background: '#111'}}>
      <PapelCaixa c={{x: 0, y: 0, w: 1080, h: 1080}} rasgo={null} s={1} dx={0} dy={-55}>
        {cenas}
      </PapelCaixa>
      {pessoa ? <PessoaCaixa v={v} c={{x: 0, y: 0, w: 1080, h: 1080}} s={1080 / 980} fx={540} fy={fyCheio} /> : null}
      <InsertoCaixa v={v} c={{x: 0, y: 0, w: 1080, h: 1080}} />
      <Audio src={staticFile(v.voz)} />
      <Efeitos v={v} mudo={[...(v.pessoaGL ?? []), ...mudoInserto(v)]} />
      {leg(540, 975, 0.95)}
    </AbsoluteFill>
  );
};

// ---------- 3 modos do RL (26/10/2026) ----------
type Trecho = [number, number];
// Seções [s, e] na ordem em que aparecem nas Cenas (procura <Secao> dentro dos fragmentos).
const coletarSecoes = (n: React.ReactNode, out: Trecho[]) => {
  React.Children.forEach(n, (c) => {
    if (!React.isValidElement(c)) return;
    const pr = c.props as {s?: number; e?: number; children?: React.ReactNode};
    if (c.type === Secao) out.push([pr.s as number, pr.e as number]);
    else if (c.type === React.Fragment) coletarSecoes(pr.children, out);
  });
};
const bate = (a: Trecho, b: Trecho) => a[0] < b[1] && b[0] < a[1];

export const planoModos = (v: VideoPapel, secs: Trecho[]): {pessoa: Trecho[]; papel: Trecho[]} => {
  if (v.modos?.desligado) return {pessoa: [], papel: []};
  const n = secs.length;
  const sec = (k: number): Trecho => secs[Math.max(0, Math.min(n - 1, k - 1))];
  const ins: Trecho[] = v.inserto ? [[v.inserto.s, v.inserto.e]] : [];
  let pessoa: Trecho[] = [];
  if (v.modos?.pessoa) pessoa = v.modos.pessoa.map((x) => (typeof x === 'number' ? sec(x) : x));
  else if ((!v.recortado || v.cheioVertical) && n >= 4) {
    // celular (recortado) não tem fonte 16:9 pra encher 1080x1920 sem ampliar demais: sem pessoa cheia automático
    const ini = secs[0][1];
    const cta = secs[n - 2][0];
    const cand = (v.pessoaGL ?? []).filter(([a, b]) => a >= ini && b <= cta && !ins.some((i) => bate([a, b], i)));
    const max = Math.max(1, Math.round(n / 4));
    pessoa = cand.length <= max ? cand : Array.from({length: max}, (_, i) => cand[Math.floor(((i + 0.5) * cand.length) / max)]);
  }
  let papel: Trecho[] = [];
  if (v.modos?.papel) papel = v.modos.papel.map((x) => (typeof x === 'number' ? sec(x) : x));
  else {
    // seção livre: fora da abertura e das 2 últimas, ≥ 1,5 s, sem inserto e sem frase de pessoa cheia no miolo
    const livre = (k: number) =>
      k >= 1 && k <= n - 3 && secs[k][1] - secs[k][0] >= 1.5 && !ins.some((x) => bate(x, secs[k])) && !pessoa.some((x) => bate(x, [secs[k][0] + 1, secs[k][1] - 1]));
    for (let k = 2; k <= n - 3; k += 5) {
      const ok = [k, k + 1, k - 1, k + 2, k - 2].find((j) => livre(j) && !papel.some((p) => Math.abs(secs.indexOf(p) - j) < 3));
      if (ok !== undefined) papel.push(secs[ok]);
    }
  }
  // sem "piscar" a tela dividida por < 1 s entre dois modos cheios: a borda do papel cheio encosta na frase da pessoa
  papel = papel.map(([a, b]) => {
    const antes = pessoa.find(([, y]) => y > a - 1 && y < b);
    const depois = pessoa.find(([x]) => x > a && x < b + 1);
    return [antes ? antes[1] : a, depois ? depois[0] : b] as Trecho;
  });
  return {pessoa, papel};
};

// pessoa em tela cheia 1080x1920: janela 9:16 (607,5x1080) do 16:9 seguindo o rosto, ampliada 1,78x; zoom leve contínuo.
const PessoaCheio: React.FC<{v: VideoPapel}> = ({v}) => {
  const {t} = useT();
  if (v.recortado && v.cheioVertical) {
    const cv = v.cheioVertical;
    return (
      <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, overflow: 'hidden', background: '#111'}}>
        <div style={{position: 'absolute', inset: 0, transform: `scale(${v.semZoom ? 1 : zoomLeve(t)})`, transformOrigin: `540px ${cv.rostoY}px`}}>
          <OffthreadVideo src={staticFile(cv.video)} muted style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920}} />
        </div>
      </div>
    );
  }
  const k = 1920 / 1080;
  const rc = v.rostoCheio;
  let cx = v.rosto.x;
  if (rc && rc.cx.length) {
    const i = Math.max(0, Math.min(rc.cx.length - 1.001, t / rc.dt));
    const i0 = Math.floor(i);
    cx = rc.cx[i0] + (rc.cx[Math.min(rc.cx.length - 1, i0 + 1)] - rc.cx[i0]) * (i - i0);
  }
  const jan = 1080 / k;
  const x0 = Math.max(0, Math.min(1920 - jan, cx - jan / 2));
  const left = -x0 * k;
  const z = v.semZoom ? 1 : zoomLeve(t);
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, overflow: 'hidden', background: '#111'}}>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${z})`, transformOrigin: `${(cx - x0) * k}px ${v.rosto.y * k}px`}}>
        <OffthreadVideo src={staticFile(v.video)} muted style={{position: 'absolute', left, top: 0, width: 1920 * k, height: 1920}} />
      </div>
    </div>
  );
};

// Papel em tela cheia 1080x1920: textura repetida (2ª cópia espelhada) e o painel 1080x960 descido pro meio.
export const DY_PAPEL_CHEIO = 280;
const Y_LEG_CHEIO = {papel: 1240, pessoa: 1330}; // legenda nos modos cheios: papel ≤ 65 % da altura; pessoa cheia mais baixo (rosto ampliado 1,78x, fora do queixo)
const PapelCheio: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1920, overflow: 'hidden'}}>
    <Img src={staticFile('paper/papel.jpg')} style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 1000}} />
    <Img src={staticFile('paper/papel.jpg')} style={{position: 'absolute', left: 0, top: 960, width: 1080, height: 1000, transform: 'scaleY(-1)'}} />
    <div style={{position: 'absolute', left: 0, top: DY_PAPEL_CHEIO, width: 1080, height: 960}}>{children}</div>
  </div>
);

const PaperRL: React.FC<{v: VideoPapel}> = ({v}) => {
  const {t} = useT();
  const {Cenas} = v;
  const secs: Trecho[] = [];
  // chamada direta pra ler as <Secao> (os hooks das Cenas rodam aqui, sempre na mesma ordem)
  coletarSecoes((Cenas as (p: object) => React.ReactNode)({}), secs);
  const plano = planoModos(v, secs);
  const dentro = (l: Trecho[]) => l.some(([a, b]) => t >= a && t < b);
  const modo = dentro(plano.pessoa) ? 'pessoa' : dentro(plano.papel) ? 'papel' : 'dividido';
  const cenas = (
    <EtiquetasCtx.Provider value={v.etiquetas ?? false}>
      <Cenas />
    </EtiquetasCtx.Provider>
  );
  const div = v.divisaoRL ?? LAYOUT.divisoria;
  return (
    <AbsoluteFill style={{background: '#111'}}>
      <Audio src={staticFile(v.voz)} />
      <Efeitos v={v} mudo={plano.pessoa} />
      {modo === 'pessoa' ? (
        <PessoaCheio v={v} />
      ) : modo === 'papel' ? (
        <PapelCheio>{cenas}</PapelCheio>
      ) : (
        <>
          <Apresentador v={v} />
          <InsertoCaixa v={v} c={{x: 0, y: div - 20, w: 1080, h: LAYOUT.altura - (div - 20)}} />
          <Papel div={v.divisaoRL}>{cenas}</Papel>
        </>
      )}
      {v.semLegenda ? null : <LegendaPapel blocos={v.legenda} cx={modo === 'pessoa' ? v.xLegPessoa ?? 540 : 540} cy={modo === 'dividido' ? div : modo === 'pessoa' ? v.yLegPessoa ?? Y_LEG_CHEIO.pessoa : Y_LEG_CHEIO.papel} />}
    </AbsoluteFill>
  );
};

export const PaperVideo: React.FC<{nome: string; formato?: Formato}> = ({nome, formato = 'RL'}) => {
  const v = papelPorNome(nome);
  // as peças leem COR.destaque na hora de desenhar: cada composição põe a cor do seu vídeo antes dos filhos
  COR.destaque = v.destaque?.cor ?? DESTAQUE_PADRAO.cor;
  COR.destaqueEscuro = v.destaque?.escuro ?? DESTAQUE_PADRAO.escuro;
  if (formato !== 'RL') return <PaperFormato v={v} f={formato} />;
  return <PaperRL v={v} />;
};
