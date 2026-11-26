import { chromium } from 'playwright';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const expected = await readFile('/tmp/quartz-g39-native.bin');
const browser = await chromium.launch({headless:true});
try {
 const page = await browser.newPage();
 await page.goto('http://127.0.0.1:8765/');
 const bytes = await page.evaluate(async () => {
  const m = await import('/pkg/quartz_kernel.js');
  await m.default();
  return Array.from(m.g39_fixture());
 });
 const actual=Buffer.from(bytes);
 if(expected.length!==36436 || !actual.equals(expected)) throw new Error('G39 parity mismatch: '+expected.length+' / '+actual.length);
 console.log(JSON.stringify({bytes:actual.length,sha256:createHash('sha256').update(actual).digest('hex'),parity:true}));
} finally {await browser.close();}
