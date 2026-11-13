// Fotografa quadros de várias composições com um bundle só (conferência de correções).
//   node scripts/fotos_multi.mjs <pasta-saida> <comp>:<t1>,<t2> <comp2>:<t> ...   (t em segundos)
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';

const [, , saida, ...pedidos] = process.argv;
fs.mkdirSync(saida, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
for (const p of pedidos) {
  const [id, ts] = p.split(':');
  const comp = await selectComposition({serveUrl, id, inputProps: {}});
  for (const t of ts.split(',')) {
    const frame = Math.min(comp.durationInFrames - 1, Math.round(parseFloat(t) * comp.fps));
    await renderStill({serveUrl, composition: comp, inputProps: comp.props, output: path.join(saida, `${id}_${t}.png`), frame, imageFormat: 'png'});
    process.stdout.write(`${id}@${t} `);
  }
}
console.log('\nok');
