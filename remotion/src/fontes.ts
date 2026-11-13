import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Todas OFL (licenças em ferramentas/fontes/; aqui em public/fontes ficam cópias).
export const carregarFontes = () =>
  Promise.all([
    loadFont({family: 'TikTokSans', url: staticFile('fontes/TikTokSans-Variable.ttf'), weight: '300 900'}),
    loadFont({family: 'Inter', url: staticFile('fontes/Inter-Regular.ttf'), weight: '400'}),
    loadFont({family: 'Inter', url: staticFile('fontes/Inter-Bold.ttf'), weight: '700'}),
    // estilo papel (Editor Paper)
    loadFont({family: 'Montserrat', url: staticFile('fontes/Montserrat-Light.ttf'), weight: '300'}),
    loadFont({family: 'Montserrat', url: staticFile('fontes/Montserrat-Bold.ttf'), weight: '700'}),
    loadFont({family: 'Montserrat', url: staticFile('fontes/Montserrat-ExtraBold.ttf'), weight: '800'}),
    loadFont({family: 'Montserrat', url: staticFile('fontes/Montserrat-Black.ttf'), weight: '900'}),
    loadFont({family: 'MonoPaper', url: staticFile('fontes/JetBrainsMono-700.woff2'), weight: '700'}),
  ]);
