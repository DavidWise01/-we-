import { chromium } from 'playwright';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true});
try {
 const page=await browser.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765/');
 await page.waitForFunction(()=>document.querySelector('#status').textContent==='Rust WASM ready',{},{timeout:30000});
 const journal=()=>page.locator('#journal').inputValue();
 const energy=()=>page.locator('#energy').textContent();
 assert.equal(await journal(),'QJ1 100 100 100\n');
 await page.locator('#shock').click();
 assert.equal(await journal(),'QJ1 100 100 100\nS 0:40\n');
 await page.locator('#recover').click();assert.equal(await energy(),'R / B / G energy: 92 / 92 / 92');
 await page.locator('#recover').click();assert.equal(await energy(),'R / B / G energy: 84 / 84 / 92');
 const final=await journal();
 await page.locator('#cell').fill('62');await page.locator('#shock').click();
 assert.equal(await journal(),final);
 await page.locator('#journal').fill('QJ1 100 100 100\nS 62:1\n');await page.locator('#replay').click();
 assert.match(await page.locator('#status').textContent(),/Rejected/);
 await page.locator('#journal').fill(final);await page.locator('#replay').click();
 assert.equal(await journal(),final);assert.equal(await energy(),'R / B / G energy: 84 / 84 / 92');
 const download=page.waitForEvent('download');await page.locator('#save').click();assert.equal((await download).suggestedFilename(),'quartz.qj1');
 assert.deepEqual(errors,[]);
 const missing=await browser.newPage();await missing.route('**/pkg/quartz_kernel.js',r=>r.abort());await missing.goto('http://127.0.0.1:8765/');
 await missing.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('WASM unavailable'));
 for(const id of ['shock','recover','replay','save'])assert.equal(await missing.locator('#'+id).isDisabled(),true);
 console.log('G9 browser acceptance passed');
}finally{await browser.close();}
