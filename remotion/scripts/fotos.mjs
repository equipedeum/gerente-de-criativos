// Fotografa quadros de uma composição (bundle uma vez só) e monta uma folha de revisão.
//   node scripts/fotos.mjs <composição> <pasta-saida> <t1> <t2> ...   (t em segundos)
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';

const [, , id, saida, ...tempos] = process.argv;
fs.mkdirSync(saida, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const comp = await selectComposition({serveUrl, id, inputProps: {}});
for (const t of tempos) {
  const frame = Math.min(comp.durationInFrames - 1, Math.round(parseFloat(t) * comp.fps));
  await renderStill({serveUrl, composition: comp, inputProps: comp.props, output: path.join(saida, `q_${String(t).padStart(6, '0')}.jpg`), frame, imageFormat: 'jpeg', jpegQuality: 85});
  process.stdout.write(`${t} `);
}
console.log('\nok');
