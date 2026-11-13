// Checagem de MARGEM SEGURA da Edição animada (08/11/2026, regra do usuário: "o que é animação importante ou escrita
// na tela tem que estar dentro da margem").
//
//   node hyperframes/checar_margem.mjs <pasta public> <FMT> <saida.json> [passo_s]
//
// Abre o index.html num Chrome headless (o mesmo do HyperFrames), percorre o vídeo inteiro de `passo` em `passo`
// segundos (padrão 0,1 s: pega movimento de câmera, zoom, paralaxe e o pico das entradas com back.out) e mede com
// getBoundingClientRect, já com todas as transformações aplicadas:
//   - TODO texto visível (nó de texto HTML e <text> de SVG): letreiro, capítulo, data, rótulo, balão, etiqueta, placa,
//     manchete, número de infográfico...;
//   - todo elemento marcado como importante (atributo data-imp: o objeto que carrega a ideia — celular, carteira,
//     gráfico, infográfico, placa...).
// Fora da caixa segura do formato = problema. Cenas da pessoa (vídeo) ficam de fora. Amostras em que o tema inteiro
// está transformado por uma TRANSIÇÃO (entrada/saída da cena) saem marcadas "trans" e contam à parte.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import os from 'node:os';

const [, , PUB_, FMT = 'RL', SAIDA = 'margem.json', PASSO_ = '0.1'] = process.argv;
const PASSO = parseFloat(PASSO_);
const PUB = path.resolve(PUB_);
// caixa segura (x0, y0, x1, y1) em px do quadro final. RL: interface do Reels/TikTok cobre o alto e o pé.
const CAIXA = {
  RL: [100, 220, 980, 1500],
  IN: [100, 80, 980, 1270],
  GL: [100, 80, 980, 1000],
  YT: [100, 80, 980, 1000],   // YT = animação quadrada à esquerda (0–1080) + pessoa à direita: margem do painel
};
// 12/11/2026 — REGRA DO USUÁRIO (caso real/caso real): título, legenda, letreiro e QUALQUER TEXTO nunca lá em cima (o
// Instagram tampa), nunca baixo demais e nunca na altura do rosto. RL: topo do texto a ≥ 320 px e base acima de ~1500;
// nos outros formatos longe do topo também (~15 % da altura; antes o letreiro da animada ficava a ~12 %). Vale pra
// texto; peça sem texto segue a CAIXA de cima. MARGEM_SO_VERTICAL=1 ignora as laterais (Editor Extremo, cujo YT tem
// 1920 de largura útil).
const CAIXA_TEXTO = {
  RL: [100, 320, 980, 1500],
  IN: [100, 200, 980, 1270],
  GL: [100, 160, 980, 1000],
  YT: [100, 160, 980, 1000],
};
const SO_VERTICAL = process.env.MARGEM_SO_VERTICAL === '1';
const VIEW = { RL: [1080, 1920], IN: [1080, 1350], GL: [1080, 1080], YT: [1920, 1080] };
const PAINEL = { RL: [0, 0, 1080, 1920], IN: [0, 0, 1080, 1350], GL: [0, 0, 1080, 1080], YT: [0, 0, 1080, 1080] };

function acha(globo) {
  const out = [];
  // cache do npx: Windows %LOCALAPPDATA%/npm-cache/_npx; Mac/Linux ~/.npm/_npx
  const raizes = [path.join(process.env.LOCALAPPDATA || '', 'npm-cache', '_npx'), path.join(os.homedir(), '.npm', '_npx')];
  for (const raiz of raizes) {
    for (const d of fs.existsSync(raiz) ? fs.readdirSync(raiz) : []) {
      const p = path.join(raiz, d, 'node_modules', globo, 'package.json');
      if (fs.existsSync(p)) out.push(p);
    }
  }
  return out[0];
}
const require_ = createRequire(acha('puppeteer-core') || import.meta.url);
const puppeteer = require_('puppeteer-core');
function chrome() {
  const base = path.join(os.homedir(), '.cache', 'hyperframes', 'chrome', 'chrome-headless-shell');
  // pasta do HyperFrames: <versão>/chrome-headless-shell-<win64|mac-arm64|mac-x64|linux64>/chrome-headless-shell[.exe]
  for (const v of (fs.existsSync(base) ? fs.readdirSync(base) : []).sort().reverse()) {
    for (const sub of ['chrome-headless-shell-win64', 'chrome-headless-shell-mac-arm64', 'chrome-headless-shell-mac-x64', 'chrome-headless-shell-linux64']) {
      for (const nome of ['chrome-headless-shell.exe', 'chrome-headless-shell']) {
        const exe = path.join(base, v, sub, nome);
        if (fs.existsSync(exe)) return exe;
      }
    }
  }
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  throw new Error('chrome-headless-shell do HyperFrames não encontrado');
}

const TIPOS = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.ttf': 'font/ttf', '.woff2': 'font/woff2',
  '.otf': 'font/otf', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json' };
const srv = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  const f = path.join(PUB, u === '/' ? 'index.html' : u);
  if (!f.startsWith(path.resolve(PUB)) || !fs.existsSync(f) || /\.(mp4|m4a|wav|mov|mp3)$/i.test(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TIPOS[path.extname(f).toLowerCase()] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});
await new Promise((r) => srv.listen(0, '127.0.0.1', r));
const porta = srv.address().port;

const html = fs.readFileSync(path.join(PUB, 'index.html'), 'utf-8');
const marcas = [...html.matchAll(/\/\/ (c\d+) \[([\d.]+)–([\d.]+)\]( pessoa)?/g)].map((m) => ({ id: m[1], t0: +m[2], t1: +m[3], pessoa: !!m[4] }));
const comp = (html.match(/data-composition-id="([^"]+)"/) || [])[1];

const nav = await puppeteer.launch({ executablePath: chrome(), headless: true, args: ['--no-sandbox', '--mute-audio', '--autoplay-policy=no-user-gesture-required'] });
const pg = await nav.newPage();
const [vw, vh] = VIEW[FMT];
pg.on('pageerror', (e) => console.error('pageerror:', String(e).slice(0, 300)));
await pg.evaluateOnNewDocument(() => { window.__timelines = window.__timelines || {}; });
await pg.setViewport({ width: vw, height: vh, deviceScaleFactor: 1 });
await pg.goto(`http://127.0.0.1:${porta}/index.html`, { waitUntil: 'load', timeout: 120000 });
await pg.evaluate(async () => { await document.fonts.ready; });
await pg.waitForFunction((c) => !!(window.__timelines && window.__timelines[c]), { timeout: 60000 }, comp);

const LEG_CAIXA = { RL: CAIXA_TEXTO.RL, IN: CAIXA_TEXTO.IN, GL: CAIXA_TEXTO.GL, YT: [100, 160, 1820, 1000] };
const achados = await pg.evaluate((comp, marcas, PASSO, CAIXA, PAINEL, CAIXA_TEXTO, SO_VERTICAL, LEG_CAIXA) => {
  const tl = window.__timelines[comp];
  const clips = [...document.querySelectorAll('[data-start][data-duration]')].filter((e) => !/^(VIDEO|AUDIO|IMG)$/.test(e.tagName) && e.id !== 'root');
  const [PX0, PY0, PX1, PY1] = PAINEL;
  const res = [];
  // tema "parado" = matriz ~identidade (o GSAP deixa matrix(1,0,0,1,0,0.0001) etc. no fim das transições)
  const ident = (tr) => {
    if (!tr || tr === 'none') return true;
    const m = tr.match(/matrix\(([^)]+)\)/);
    if (!m) return false;
    const [a, b, c, d, e, f] = m[1].split(',').map(Number);
    return Math.abs(a - 1) < 0.003 && Math.abs(d - 1) < 0.003 && Math.abs(b) < 0.003 && Math.abs(c) < 0.003 && Math.abs(e) < 2 && Math.abs(f) < 2;
  };
  // clip-path da íris: só é transição enquanto o círculo não cobre a tela (raio < 100 %); depois fica circle(150%)
  const clipAtivo = (cp) => {
    if (!cp || cp === 'none') return false;
    const m = cp.match(/circle\(([\d.]+)%/);
    return m ? +m[1] < 100 : true;
  };
  for (const m of marcas) {
    if (m.pessoa) continue;
    const cena = document.getElementById(m.id);
    if (!cena) continue;
    const tema = document.getElementById(`${m.id}-tema`);
    for (let t = m.t0 + 0.02; t < m.t1 - 0.01; t += PASSO) {
      tl.seek(t, false);
      for (const e of clips) {
        const s = +e.dataset.start, d = +e.dataset.duration;
        e.style.visibility = t >= s && t < s + d ? 'visible' : 'hidden';
      }
      const op = new Map();
      const visivel = (el) => {   // opacidade acumulada até a cena (0 = invisível)
        let a = 1;
        for (let n = el; n && n !== document.body; n = n.parentElement) {
          let o = op.get(n);   // cache da opacidade PRÓPRIA de cada nó (a conta sobe a cadeia inteira sempre)
          if (o === undefined) {
            const cs = getComputedStyle(n);
            o = cs.display === 'none' || cs.visibility === 'hidden' ? 0 : +cs.opacity;
            if (n instanceof SVGElement && n.getAttribute('opacity') != null && cs.opacity === '1') o *= +n.getAttribute('opacity');
            op.set(n, o);
          }
          a *= o;
          if (a < 0.08) return 0;
        }
        return a;
      };
      // transição: o tema inteiro (ou um véu/arx do arsenal) mexido = amostra de transição
      const trTema = tema ? getComputedStyle(tema) : null;
      let trans = !!(trTema && (!ident(trTema.transform) || clipAtivo(trTema.clipPath)));
      // overlay de transição do arsenal (.arx) só conta enquanto MOSTRA algo: fundo próprio visível, ou alguma forma de
      // dentro (pincelada, barra da persiana, mancha, folha) com tamanho na tela. Depois da transição ele continua no
      // DOM (barras com scaleX 0, mancha com scale 0) e não pode marcar a cena inteira como transição.
      const dentro = (r) => r.width > 40 && r.height > 40 && r.right > PX0 && r.left < PX1 && r.bottom > PY0 && r.top < PY1;
      for (const ov of cena.querySelectorAll('.arx')) {
        if (visivel(ov) < 0.08 || trans) continue;
        const bg = getComputedStyle(ov).backgroundColor;
        if (bg && !/rgba\(0, 0, 0, 0\)|transparent/.test(bg) && dentro(ov.getBoundingClientRect())) { trans = true; continue; }
        for (const f of ov.querySelectorAll('path,rect,circle,i,div')) {
          if (visivel(f) < 0.08) continue;
          if (getComputedStyle(f).backgroundColor === 'rgba(0, 0, 0, 0)' && f.tagName === 'DIV') continue;
          if (dentro(f.getBoundingClientRect())) { trans = true; break; }
        }
      }
      const veu = cena.querySelector('.veu');
      if (veu && +getComputedStyle(veu).opacity > 0.25) trans = true;
      const add = (el, r, rot, tipo) => {
        if (r.width < 2 || r.height < 2) return;
        if (r.right <= PX0 || r.left >= PX1 || r.bottom <= PY0 || r.top >= PY1) return;   // fora do quadro inteiro = não aparece
        const [X0, Y0, X1, Y1] = tipo === 'texto' ? CAIXA_TEXTO : CAIXA;   // 12/11: texto tem caixa própria (longe do topo)
        const fora = {};
        if (!SO_VERTICAL && r.left < X0 - 1) fora.esq = Math.round(X0 - r.left);
        if (!SO_VERTICAL && r.right > X1 + 1) fora.dir = Math.round(r.right - X1);
        if (r.top < Y0 - 1) fora.topo = Math.round(Y0 - r.top);
        if (r.bottom > Y1 + 1) fora.base = Math.round(r.bottom - Y1);
        const lados = el.getAttribute && el.getAttribute('data-lados');
        if (lados) for (const k of Object.keys(fora)) if (!lados.includes(k)) delete fora[k];
        if (!Object.keys(fora).length) return;
        let chave = el.id || '';
        for (let n = el; !chave && n && n !== cena; n = n.parentElement) if (n.id) chave = n.id;
        res.push({ cena: m.id, t: Math.round(t * 100) / 100, tipo, rot: rot.slice(0, 40), el: chave, fora, trans,
          caixa: [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)] });
      };
      // 1) texto HTML (por nó de texto: a caixa da letra, não a da div)
      const w = document.createTreeWalker(cena, NodeFilter.SHOW_TEXT);
      const rg = document.createRange();
      for (let n = w.nextNode(); n; n = w.nextNode()) {
        const txt = n.nodeValue.trim();
        if (!txt || !n.parentElement || n.parentElement.closest('svg')) continue;
        if (visivel(n.parentElement) < 0.08) continue;
        rg.selectNodeContents(n);
        const r = rg.getBoundingClientRect();
        add(n.parentElement, r, txt, 'texto');
      }
      // 2) texto SVG
      for (const el of cena.querySelectorAll('text')) {
        const txt = (el.textContent || '').trim();
        if (!txt || visivel(el) < 0.08) continue;
        add(el, el.getBoundingClientRect(), txt, 'texto');
      }
      // 3) peça importante marcada
      // (a caixa é a união das formas VISÍVEIS de dentro: folha que já sumiu ou cartão ainda transparente não conta)
      const FORMAS = 'path,rect,circle,ellipse,polygon,polyline,line,text,use,image';
      for (const el of cena.querySelectorAll('[data-imp]')) {
        if (visivel(el) < 0.08) continue;
        let r = null;
        const folhas = el.matches(FORMAS) ? [el] : el.querySelectorAll(FORMAS);
        for (const f of folhas) {
          if (f.closest('clipPath,defs,mask') || visivel(f) < 0.08) continue;
          const b = f.getBoundingClientRect();
          if (b.width < 1 && b.height < 1) continue;
          r = r ? { left: Math.min(r.left, b.left), top: Math.min(r.top, b.top), right: Math.max(r.right, b.right), bottom: Math.max(r.bottom, b.bottom) } : { left: b.left, top: b.top, right: b.right, bottom: b.bottom };
        }
        if (!r) continue;
        r.width = r.right - r.left; r.height = r.bottom - r.top;
        add(el, r, el.getAttribute('data-imp') || el.id, 'peca');
      }
    }
  }
  // 12/11/2026: legenda padrão da pessoa em tela cheia (#legpessoa .lt, fora das cenas: o loop acima não a vê). Mesma
  // caixa de texto do formato; no YT a pessoa cheio é 16:9 inteiro, então a caixa é o quadro todo (LEG_CAIXA).
  const rgl = document.createRange();
  for (const el of document.querySelectorAll('#legpessoa .lt')) {
    const a = +el.dataset.ini, b = +el.dataset.fim;
    for (let t = a + 0.02; t < b - 0.01; t += PASSO) {
      tl.seek(t, false);
      if (+getComputedStyle(el).opacity < 0.08 || !el.firstChild) continue;
      rgl.selectNodeContents(el.firstChild);
      const r = rgl.getBoundingClientRect();
      const [X0, Y0, X1, Y1] = LEG_CAIXA;
      const fora = {};
      if (r.left < X0 - 1) fora.esq = Math.round(X0 - r.left);
      if (r.right > X1 + 1) fora.dir = Math.round(r.right - X1);
      if (r.top < Y0 - 1) fora.topo = Math.round(Y0 - r.top);
      if (r.bottom > Y1 + 1) fora.base = Math.round(r.bottom - Y1);
      if (Object.keys(fora).length) res.push({ cena: el.dataset.cena, t: Math.round(t * 100) / 100, tipo: 'texto',
        rot: el.textContent.slice(0, 40), el: el.id, fora, trans: false,
        caixa: [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)] });
    }
  }
  return res;
}, comp, marcas, PASSO, CAIXA[FMT], PAINEL[FMT], CAIXA_TEXTO[FMT], SO_VERTICAL, LEG_CAIXA[FMT]);

await nav.close();
srv.close();
fs.writeFileSync(SAIDA, JSON.stringify({ comp, fmt: FMT, caixa: CAIXA[FMT], caixa_texto: CAIXA_TEXTO[FMT], achados }, null, 1));
console.log(`margem ${FMT}: ${achados.length} amostras fora`);
