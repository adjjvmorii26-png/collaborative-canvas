const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(String(e)));

  await page.goto('http://127.0.0.1:4000/', { waitUntil: 'networkidle' });
  await page.waitForSelector('.msg', { timeout: 5000 });
  await page.screenshot({ path: 'artifacts/synthhall-lobby.png' });
  console.log('lobby loaded, messages:', await page.locator('.msg').count());

  // Enter Story Forge
  await page.getByRole('button', { name: /Story Forge/ }).click();
  await page.waitForFunction(() => document.getElementById('roomname').textContent.includes('Story Forge'));
  await page.waitForSelector('.agent', { timeout: 5000 });
  console.log('agents visible:', await page.locator('.agent').count());

  // Send a message
  await page.fill('#composer', 'A garden where every flower grows from a memory a human and AI planted together.');
  await page.click('#send');
  await page.waitForFunction(() => document.querySelectorAll('#messages .msg').length >= 5, { timeout: 8000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'artifacts/synthhall-story-forge.png' });
  const msgs = await page.locator('#messages .msg .who').allTextContents();
  console.log('message feed:');
  msgs.slice(-6).forEach((w) => console.log('  -', w));
  console.log('console errors:', errors.length ? errors : 'none');
  await browser.close();
})();
