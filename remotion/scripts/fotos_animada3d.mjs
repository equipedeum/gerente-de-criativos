// Fotos de revisão do estilo "Animada 3D" (bundle uma vez só, GPU via ANGLE).
//   node scripts/fotos_animada3d.mjs <composição> <pasta-saida> <t1> <t2> ...   (t em segundos)
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';

const [, , id, saida, ...tempos] = process.argv;
fs.mkdirSync(saida, {recursive: true});
const chromiumOptions = {gl: 'angle'};
const serveUrl = await bundle({entryPoint: path.resolve('src/animada3d/index.tsx'), publicDir: path.resolve('public-animada3d')});
const inputProps = process.env.A3D_PROPS ? JSON.parse(process.env.A3D_PROPS) : {};
const comp = await selectComposition({serveUrl, id, inputProps, chromiumOptions});
const onBrowserLog = (l) => { if (l.type === 'error' || process.env.A3D_LOG) console.log('[' + l.type + ']', l.text.slice(0, 600)); };
for (const t of tempos) {
  const frame = Math.min(comp.durationInFrames - 1, Math.round(parseFloat(t) * comp.fps));
  const t0 = Date.now();
  await renderStill({serveUrl, composition: comp, inputProps, output: path.join(saida, `q_${parseFloat(t).toFixed(2).padStart(6, '0')}.jpg`), frame,
    imageFormat: 'jpeg', jpegQuality: 88, chromiumOptions, timeoutInMilliseconds: 180000, onBrowserLog});
  process.stdout.write(`${t}(${((Date.now() - t0) / 1000).toFixed(1)}s) `);
}
console.log('\nok');
