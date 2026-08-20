const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:4000/', { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: /Design Pit/ }).click();
  await page.waitForSelector('.agent');
  await page.waitForTimeout(1200);
  const names = await page.$$eval('.agent .nm', (els) => els.map((e) => e.textContent));
  console.log('cards:', names.length, '| names:', JSON.stringify(names));
  await browser.close();
})();
