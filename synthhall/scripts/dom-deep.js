const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:4000/', { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: /Story Forge/ }).click();
  await page.waitForSelector('.agent');
  await page.waitForTimeout(1500);
  const info = await page.$$eval('.agent', (els) => els.map((e) => ({
    cls: e.className, parent: e.parentElement && e.parentElement.id,
    name: (e.querySelector('.nm') || {}).textContent || null,
  })));
  const cards = info.filter((x) => x.name);
  console.log('total .agent matches:', info.length);
  console.log('named cards:', cards.length);
  console.log('unique card names:', [...new Set(cards.map((c) => c.name))]);
  const withoutName = info.filter((x) => !x.name);
  console.log('unnamed matches sample:', withoutName.slice(0, 6));
  await browser.close();
})();
