const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto('http://127.0.0.1:4000/', { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: /Design Pit/ }).click();
  await page.waitForFunction(() => document.getElementById('roomname').textContent.includes('Design Pit'));
  await page.waitForSelector('.agent');
  await page.waitForTimeout(500);
  console.log('agent cards:', await page.locator('.agent').count());
  console.log('messages:', await page.locator('.msg').count());
  console.log('rooms:', await page.locator('button.room').count());
  // Attach a custom bot from the UI
  await page.fill('#botname', 'Zed');
  await page.selectOption('#botrole', 'critic');
  await page.click('#addbot');
  await page.waitForFunction(() => [...document.querySelectorAll('.agent .nm')].some((e) => e.textContent === 'Zed'));
  console.log('after attach, agent cards:', await page.locator('.agent').count());
  await page.screenshot({ path: 'artifacts/synthhall-attach.png' });
  // Send a message and wait for live replies
  await page.fill('#composer', 'Give me the strongest argument this co-pilot should be built.');
  await page.click('#send');
  await page.waitForSelector('.msg.user', { timeout: 5000 });
  const who = await page.locator('#messages .msg .who').allTextContents();
  console.log('feed tail:', who.slice(-6).map((w) => w.replace(/\s*·.*/, '')));
  await browser.close();
})();
