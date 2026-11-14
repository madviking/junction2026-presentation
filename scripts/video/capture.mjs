// Captures real Silta screens (Somali + English) from the live app for the pitch video.
// Uses Google Chrome through the Playwright install in ../junction2026tech/frontend.
//   node scripts/video/capture.mjs
// One run makes one Gemini letter-reading call on the live app (the example letter, no personal data).
// Output: content/materials/video-assets/screens/*.png (390x844 CSS px at 3x; *-full.png = whole page).
import { createRequire } from 'node:module'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const require = createRequire(path.join(here, '../../../junction2026tech/frontend/package.json'))
const { chromium } = require('playwright')
const base = (process.env.SILTA_APP_URL ?? 'https://fond-useful-corgi.eur-1.aiven.app').replace(/\/$/, '')
const out = path.join(here, '../../content/materials/video-assets/screens')

const browser = await chromium.launch({ channel: 'chrome' })

// 1. The example letter (Finnish) as a prop: the sheet with its QR block, and the same sheet without it.
const lctx = await browser.newContext({ viewport: { width: 900, height: 3000 }, deviceScaleFactor: 2 })
const lp = await lctx.newPage()
await lp.goto(`${base}/letter/cervical/fi`, { waitUntil: 'domcontentloaded', timeout: 90000 }); await lp.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {}); await lp.waitForTimeout(1500)
await lp.emulateMedia({ media: 'print' })
await lp.addStyleTag({ content: 'header, nav, [class*="sticky"], [style*="sticky"] { position: static !important; }' })
const sheet = await lp.evaluateHandle(() => {
  const all = [...document.querySelectorAll('main *')]
  const fits = all.filter((el) => el.innerText?.includes('Hodan Warsame') && el.innerText.includes('Ystävällisin'))
  return fits[fits.length - 1]
})
await sheet.evaluate((el) => el.scrollIntoView({ block: 'start' }))
await sheet.screenshot({ path: path.join(out, 'letter-fi-with-qr.png') })
await lp.evaluate(() => {
  const q = [...document.querySelectorAll('main *')].filter((e) => e.children.length === 0 && e.textContent.startsWith('Kysyttävää kirjeestä'))[0]
  let el = q; while (el && !(getComputedStyle(el).borderStyle.includes('dashed'))) el = el.parentElement
  if (el) el.style.display = 'none'
})
await sheet.screenshot({ path: path.join(out, 'letter-fi-no-qr.png') })
console.log('letters')

// 2. Phone screens.
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true })
const page = await ctx.newPage()
async function shot(name, { full = false, focusText } = {}) {
  await page.waitForTimeout(600)
  if (focusText) await page.getByText(focusText, { exact: false }).first().evaluate((el) => el.scrollIntoView({ block: 'start' }))
  else await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(400)
  // In whole-page shots, fixed and sticky bars would be painted mid-page: let them flow with the content.
  const undo = full ? await page.addStyleTag({ content: '*{}' }).then(() => page.evaluate(() => {
    const changed = []
    for (const el of document.querySelectorAll('body *')) {
      const pos = getComputedStyle(el).position
      if (pos === 'fixed' || pos === 'sticky') { changed.push([el, el.style.position]); el.style.position = 'static' }
    }
    window.__undoFixed = () => changed.forEach(([el, v]) => { el.style.position = v })
  })) : null
  await page.screenshot({ path: path.join(out, `${name}.png`), fullPage: full })
  if (full) await page.evaluate(() => window.__undoFixed?.())
  console.log(name)
}
async function go(u) { await page.goto(base + u, { waitUntil: 'domcontentloaded', timeout: 90000 }); await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {}); await page.waitForTimeout(800) }

for (const lang of ['so', 'en']) {
  await go(`/r/${lang}`); await shot(`${lang}-01-home`)
  await go(`/r/${lang}/learn/cervical`); await shot(`${lang}-04-guide`); await shot(`${lang}-04-guide-full`, { full: true })
  for (const [n, part] of [['05', 'why'], ['06', 'visit'], ['07', 'rights'], ['08', 'after'], ['09', 'faq']]) {
    await go(`/r/${lang}/learn/cervical?part=${part}`)
    await shot(`${lang}-${n}-${part}`); await shot(`${lang}-${n}-${part}-full`, { full: true })
  }
  await go(`/r/${lang}/learn/cervical?part=rights`)
  await shot(`${lang}-07-rights-desk`, { focusText: 'Toivoisin' })
}

// 3. Letter photo → explanation in Somali (Gemini), on the live app.
await go('/r/so/letter'); await shot('so-02-letter')
await page.locator('input[type=file]').last().setInputFiles(path.join(out, 'letter-fi-no-qr.png'))
await page.waitForFunction(() => !document.body.innerText.includes('Dooro sawir'), null, { timeout: 60000 }).catch(() => {})
await page.waitForTimeout(300); await shot('so-03a-letter-reading')
// Wait until the "reading your letter" spinner is gone and the explanation is on screen.
await page.waitForFunction(() => !document.body.innerText.includes('waa la akhrinayaa') && document.body.innerText.includes('Warqaddaada waxaa ku qoran'), null, { timeout: 120000 })
await page.waitForTimeout(1500)
await shot('so-03-letter-result'); await shot('so-03-letter-result-full', { full: true })
console.log(page.url())
await browser.close()
