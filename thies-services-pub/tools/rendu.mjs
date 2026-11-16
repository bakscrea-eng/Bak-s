// Rendu image par image dans Chromium headless.
//   node tools/rendu.mjs stills 3,6.2,20 out/      -> PNG de contrôle
//   node tools/rendu.mjs video <debut> <fin> out.mp4  -> segment vidéo (images [debut, fin[ à 30 i/s)
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';

const [mode, a, b, c] = process.argv.slice(2);
const PORT = process.env.PORT || 8123, FPS = 30;
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.setDefaultTimeout(0);
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('[page]', m.text()); });
page.on('pageerror', e => console.error('[pageerror]', e.message));
await page.goto(`http://localhost:${PORT}/${process.env.PAGE || 'index.html'}?render`, { waitUntil: 'commit' });
await page.waitForFunction(() => window.ready === true, null, { timeout: 600000 });
const shot = async (t, f) => { await page.evaluate(([t, f]) => window.renderAt(t, f), [t, f]); return page.screenshot({ type: mode === 'stills' ? 'png' : 'jpeg', quality: mode === 'stills' ? undefined : 95 }); };

if (mode === 'stills') {
  const fs = await import('node:fs');
  for (const t of a.split(',').map(Number)) { const img = await shot(t, Math.round(t * FPS)); fs.writeFileSync(`${b}/still_${t.toFixed(2)}.png`, img); console.log('ok', t); }
} else {
  const f0 = Number(a), f1 = Number(b);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', c], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    const img = await shot(f / FPS, f);
    if (!ff.stdin.write(img)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 30 === 0) console.log(`${c}: image ${f} (${((Date.now() - t0) / (f - f0 + 1) / 1000).toFixed(2)} s/img)`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await browser.close();
