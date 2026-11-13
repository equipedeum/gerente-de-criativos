// demo — MOLDE do Editor Paper (menu 6), feito com o vídeo de demonstração (roteiro em exemplos/demo/roteiro.txt,
// fonte VERTICAL de celular). Copiar pra <id>.tsx, trocar tudo e registrar em index.ts.
// Tempos = segundos do work/<id>/words_cut.json (ver a saída do preparar_paper.py). Arquivos gerados por vídeo:
//   <id>-blocos.txt (legenda revisada) -> scripts/legenda_paper.py -> <id>-legenda.json
//   scripts/sfx_auto.py <id> -> <id>-auto.json (sons + trechos do GL com a pessoa em tela cheia)
//   scripts/trilha_cheio.py <id> -> <id>-cheio.json (só fonte 16:9: trilha do rosto pra pessoa cheia do RL)
// Regras: conteúdo do papel de y ~330 a 860 (nada lá em cima: o Instagram tampa); ≥ 100 px das laterais; sem título;
// sem etiqueta de seção; um elemento novo por frase entrando ~0,1 s antes da palavra; nunca inventar número.
import React from 'react';
import {COR} from '../estilo';
import {Botao, Calendario, Carimbo, Cupom, Doc, Etiqueta, Icone, IconeRotulo, ItemLista, Mao, Peca, Pessoa, Pizza, Seta, Xis} from '../pecas';
import {Secao, type BlocoLeg, type VideoPapel} from '../PaperVideo';
import legenda from './demo-legenda.json';
import auto from './demo-auto.json'; // sons e trechos do GL gerados por scripts/sfx_auto.py

const T = 6;

const Cenas: React.FC = () => (
  <>
    {/* 01 — 12 horas por dia e a semana atrasada */}
    <Secao s={0} e={5.42} tag="Rotina" num={1} total={T}>
      <Peca x={300} y={470} t={0.1}>
        <Icone nome="clock" tam={200} />
      </Peca>
      <Peca x={300} y={680} t={0.82} entrada="carimbo" rot={-3}>
        <Etiqueta txt="12 horas" cor="destaque" tam={46} />
      </Peca>
      <Peca x={760} y={480} t={3.98} rot={3}>
        <Calendario num="SEX" topo="SEMANA" />
      </Peca>
      <Peca x={760} y={480} t={4.4} entrada="nada" sombra={false}>
        <Xis t0={4.4} tam={170} cor={COR.alerta} />
      </Peca>
      <Peca x={760} y={680} t={4.45} rot={-2}>
        <Etiqueta txt="Atrasado" cor="navy" tam={34} />
      </Peca>
    </Secao>

    {/* 02 — O teste: anotei tudo durante cinco dias (cupom imprimindo os dias) */}
    <Secao s={5.42} e={11.2} tag="O teste" num={2} total={T}>
      <Peca x={540} y={600} t={5.55} entrada="nada">
        <Cupom t0={5.6} w={520} h={540} titulo="Teste · 5 dias">
          <ItemLista t={7.88} txt="Segunda" marcador="caixa" tCheck={8.38} tam={34} />
          <ItemLista t={8.6} txt="Terça" marcador="caixa" tCheck={9.0} tam={34} />
          <ItemLista t={9.12} txt="Quarta" marcador="caixa" tCheck={9.5} tam={34} />
          <ItemLista t={9.56} txt="Quinta" marcador="caixa" tCheck={9.9} tam={34} />
          <ItemLista t={9.94} txt="Sexta" marcador="caixa" tCheck={10.5} tam={34} />
        </Cupom>
      </Peca>
    </Secao>

    {/* 03 — O resultado assustou: 70% do tempo em tarefas que outra pessoa podia fazer */}
    <Secao s={11.2} e={23.3} tag="Resultado" num={3} total={T}>
      <Peca x={300} y={470} t={13.2}>
        <Pizza d={300} ate={70} t0={13.32} t1={14.9} cor={COR.alerta} txt="70%" />
      </Peca>
      <Peca x={300} y={700} t={14.8} rot={-2}>
        <Etiqueta txt="do meu tempo" tam={32} />
      </Peca>
      <Peca x={760} y={420} t={16.86}>
        <Pessoa cor="kraft" tam={0.7} />
      </Peca>
      <Peca x={760} y={590} t={18.7}>
        <IconeRotulo ic="chat-text" txt="Mensagem" tam={30} />
      </Peca>
      <Peca x={760} y={680} t={20.3}>
        <IconeRotulo ic="file-text" txt="Orçamento" tam={30} />
      </Peca>
      <Peca x={760} y={770} t={21.82}>
        <IconeRotulo ic="credit-card" txt="Pagamento" tam={30} />
      </Peca>
    </Secao>

    {/* 04 — Passei pro time, com passo a passo escrito */}
    <Secao s={23.3} e={28.1} tag="Time" num={4} total={T}>
      <Peca x={200} y={470} t={25.6}>
        <Pessoa cor="kraft" tam={0.6} />
      </Peca>
      <Peca x={330} y={470} t={25.68}>
        <Pessoa cor={COR.navy} tam={0.6} />
      </Peca>
      <Peca x={460} y={470} t={25.76}>
        <Pessoa cor="kraft" tam={0.6} />
      </Peca>
      <Peca x={330} y={680} t={25.72} rot={-2}>
        <Etiqueta txt="O meu time" tam={34} />
      </Peca>
      <Peca x={790} y={470} t={26.74} rot={4}>
        <Doc w={170} />
      </Peca>
      <Peca x={790} y={700} t={27.6} entrada="carimbo" rot={-4}>
        <Carimbo txt="Passo a passo" tam={42} />
      </Peca>
    </Secao>

    {/* 05 — Hoje 8 horas, entrego o dobro, sobra tempo pra crescer */}
    <Secao s={28.1} e={36.6} tag="Hoje" num={5} total={T}>
      <Peca x={270} y={460} t={29.58} entrada="carimbo" rot={-3}>
        <Etiqueta txt="8 horas" cor="destaque" tam={46} />
      </Peca>
      <Peca x={270} y={650} t={31.16} rot={2}>
        <Etiqueta txt="O dobro" cor="navy" tam={40} />
      </Peca>
      <Seta x1={430} y1={560} x2={620} y2={560} t0={32.8} dur={0.3} cor={COR.destaque} esp={10} />
      <Peca x={790} y={480} t={33.26}>
        <Icone nome="hourglass-low" tam={170} />
      </Peca>
      <Peca x={790} y={700} t={35.56}>
        <IconeRotulo ic="trend-up" txt="Crescer" cor="destaque" corIc={COR.destaque} tam={32} />
      </Peca>
    </Secao>

    {/* 06 — CTA: o modelo da lista, clica aqui embaixo (sem "link" escrito no papel) */}
    <Secao s={36.6} e={43.2} tag="Modelo" num={6} total={T}>
      <Peca x={320} y={500} t={37.58} rot={-4}>
        <Doc w={180} />
      </Peca>
      <Peca x={320} y={720} t={37.7} rot={2}>
        <Etiqueta txt="O modelo" tam={36} />
      </Peca>
      <Peca x={760} y={560} t={40.34}>
        <Botao txt="Quero a lista" tClique={41.2} tam={40} />
      </Peca>
      <Peca x={860} y={660} t={40.6} entrada="fade" sombra={false}>
        <Mao tClique={41.2} tam={130} />
      </Peca>
      <Seta x1={760} y1={700} x2={760} y2={830} t0={41.5} dur={0.25} cor={COR.destaque} esp={10} />
    </Secao>
  </>
);

export const demo: VideoPapel = {
  nome: 'paper-demo',
  duracao: 43.2, // duração do preparar_paper.py + 0,4 s parado no último quadro
  video: 'brutos/demo-metade.mp4',
  voz: 'brutos/demo-voz.m4a',
  // fonte vertical (celular): vídeo já recortado 1080x980 seguindo o rosto; outra janela pros formatos; o vertical
  // inteiro pra pessoa em tela cheia nos 3 modos do RL. Fonte 16:9: tire estes 3 campos e use rosto {x, y} do 16:9
  // + `rostoCheio: cheio` (import cheio from './<id>-cheio.json').
  recortado: true,
  rosto: {x: 540, y: 392},
  formatosVideo: {video: 'brutos/demo-metade45.mp4', rostoY: 441},
  cheioVertical: {video: 'brutos/demo-cheio.mp4', rostoY: 599},
  sfx: auto.sfx as VideoPapel['sfx'],
  // GL: trechos com a pessoa em tela cheia — FRASE INTEIRA, a cada ~10 s (REGRA: a pessoa aparece em todo formato).
  // O sfx_auto.py sugere (auto.pessoaGL); num vídeo curto ele acha pouco, então aqui vai à mão.
  pessoaGL: [[0, 2.4], [11.18, 13.15], [23.38, 26.25]],
  // punch-in leve em 2–4 frases de impacto (fronteira de frase, nunca duas seguidas)
  punch: [
    {s: 11.38, e: 12.9, zoom: 1.08},
    {s: 28.2, e: 31.9, zoom: 1.08},
  ],
  legenda: legenda as BlocoLeg[],
  Cenas,
};
