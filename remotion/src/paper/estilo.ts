// Estilo "papel" (Editor Paper): papel creme amassado em cima com recortes animados, a pessoa embaixo e a legenda
// karaokê na borda rasgada. Medidas e regras na skill .claude/skills/editor-paper.

export const COR = {
  navy: '#1C1A2B', // texto, etiquetas de seção, figuras (medido #1c1829)
  // Cor de destaque: palavra falada na legenda, número da seção, cabeçalhos, carimbos, setas, barras.
  // Na referência é vermelho-alaranjado (#E2402D); em 08/10/2026 o usuário pediu "trocar o laranja pelo verde".
  // Esmeralda da marca no tom 600 (o #10B981 do site fica com contraste 2,2:1 sobre o creme; este, 3,3:1).
  destaque: '#059669',
  destaqueEscuro: '#065F46', // sombra do Botao (par do destaque)
  azul: '#2D52A0', // segundo destaque (carimbo "DADO VERDADEIRO", blocos PIB)
  amarelo: '#F0BE2E', // moedas, régua, lâmpada
  creme: '#F6F0E2', // cartões e faixa da legenda (medido #f6f0e2)
  branco: '#FBF8F1',
  kraft: '#C6AB80', // recortes de papelão (textura em paper/kraft.jpg)
  cinza: '#8C8578',
  // Regras de 08/10/2026 (feedback dos criativos 53/54): dinheiro é VERDE (a nota azul vinha da referência) e objeto que tem
  // cor "de verdade" mantém essa cor — sirene/alerta, coração e fogo em vermelho; o verde fica nos detalhes.
  dinheiro: '#0E9F6E',
  dinheiroClaro: '#8EDDB9',
  alerta: '#E23B2E',
};

export const FONTE = {
  pesada: 'Montserrat', // 900 na legenda e etiquetas, 800 nos cartões
  mono: 'MonoPaper', // rótulos pequenos de eixo/legenda (JetBrains Mono Bold, OFL)
};

export const LAYOUT = {
  largura: 1080,
  altura: 1920,
  divisoria: 960, // borda rasgada do papel (a referência fica entre 955 e 975)
  etiquetaX: 24, // etiqueta de seção no canto (medido 24, 143)
  etiquetaY: 143,
};

// Sombra dos recortes: papel colado, luz de cima.
export const SOMBRA = 'drop-shadow(0px 6px 4px rgba(45,35,20,0.30))';
export const SOMBRA_CARTAO = '0 8px 14px rgba(45,35,20,0.28), 0 2px 3px rgba(45,35,20,0.18)';
