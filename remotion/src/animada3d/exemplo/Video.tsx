// EXEMPLO da Animação viral: só os DADOS do vídeo. A montagem dos 3 modos (T = pessoa cheia com legenda, D = dividida
// com a animação em cima, A = animação cheia) é do motor (../motor/Viral.tsx). Tempos de outro vídeo: troque tudo
// pelos da fala do seu vídeo (work/<id>/words_cut.json). Registrar em ../index.tsx como "<id>-animada3d".
import React from "react";
import { AnimacaoViral, DadosViral, Trecho } from "../motor/Viral";
import { FILME, TOTAL } from "./cena";

export const EXEMPLO_FRAMES = TOTAL;

/** modos por trecho: corte a cada 3–5 s, sempre em início/fim de frase (ou de item de lista falada), nunca o mesmo modo
 *  duas vezes seguidas, ~1/3 do tempo cada, CTA em T. Trecho com "link"/"Direct" na fala não pode ser T. */
const TRECHOS: Trecho[] = [
  [0, 5.07, "D"], [5.07, 7.93, "A"], [7.93, 10.27, "T"], [10.27, 14.33, "A"], [14.33, 18.07, "D"],
  [18.07, 21.17, "T"], [21.17, 23.27, "A"], [23.27, 26.27, "D"], [26.27, 30.4, "A"], [30.4, 33.0, "T"],
  [33.0, 37.8, "A"], [37.8, 43.4, "T"], [43.4, 46.13, "A"], [46.13, 48.47, "T"], [48.47, 50.8, "D"],
  [50.8, 53.1, "A"], [53.1, 57.3, "D"], [57.3, 59.1, "T"], [59.1, 62.43, "D"], [62.43, 65.03, "T"],
];

/** legenda SÓ dos trechos T: blocos de até 4 palavras, 1 linha, com os tempos da fala (aqui, texto de exemplo) */
const LEGENDA: [number, number, string][] = [
  [8.12, 9.2, "Deixa eu te contar"], [9.2, 10.25, "o que mudou."],
  [18.28, 19.34, "E o melhor"], [19.34, 21.1, "veio depois."],
  [30.54, 32.06, "O resultado apareceu"], [32.06, 32.96, "em dois lugares."],
  [38.0, 40.3, "A equipe parou"], [40.3, 43.1, "de perder tempo."],
  [46.24, 47.14, "Se você tem"], [47.14, 48.45, "uma empresa,"],
  [57.32, 59.06, "a gente te mostra"],
  [62.56, 63.56, "Fechado?"], [63.56, 64.95, "Te vejo lá."],
];

/** efeitos sonoros: [segundo, arquivo em sfx/, volume]. Só onde algo acontece na tela (os de trecho T o motor descarta). */
const SFX: [number, string, number][] = [
  [2.26, "impacto", 0.22], [4.3, "brilho", 0.14], [10.3, "whoosh_lento", 0.2], [11.0, "shimmer", 0.2],
  [14.95, "pop2", 0.16], [16.84, "swish", 0.24], [22.62, "pop", 0.14], [26.9, "glock", 0.2], [35.22, "impacto", 0.22],
  [43.6, "tique", 0.12], [49.3, "brilho", 0.18], [52.68, "shimmer", 0.18], [55.58, "pop2", 0.18], [60.96, "brilho", 0.22],
];

const DADOS: DadosViral = {
  filme: FILME, trechos: TRECHOS, legenda: LEGENDA, sfx: SFX,
  // arquivos em remotion/public-animada3d/ (passo 1 da skill): pessoa cheia 1080x1920, pessoa dividida, voz
  pessoaCheio: "exemplo-pessoa-cheio.mp4", pessoaDividido: "exemplo-pessoa-dividido.mp4", voz: "exemplo-voz.m4a",
  // fonte em close (rosto enchendo a faixa): animação 0–820, pessoa 820–1920 (1080x1100). Padrão: 960.
  divY: 820,
};

export const ExemploAnimada3D: React.FC = () => <AnimacaoViral d={DADOS} />;
