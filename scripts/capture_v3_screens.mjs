// Captures the screens for deck v3 (content/presentation-v3.yaml) from a running Silta app.
// Uses the Playwright install in ../tech/frontend (no new dependency here).
//
//   node scripts/capture_v3_screens.mjs                      # app at http://localhost:5300
//   SILTA_APP_URL=https://... node scripts/capture_v3_screens.mjs
//
// Hodan's path is the screening route: the Finnish invitation letter, the Somali cervical
// guide its QR code opens, then "I got a letter I do not understand" → where you get care →
// the door with the Finnish script → appointment → visit card → the clinician's Finnish view.
// The journey screens are captured in English so the audience can read them.
// Every run starts one new anonymous visit in that app's database (local: test data).
// No paid model calls. Output: content/media/screens/v3/*.png
import { mkdirSync } from 'node:fs'
import { createRequire } from 'node:module'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const require = createRequire(path.join(here, '../../tech/frontend/package.json'))
const { chromium } = require('playwright')

const base = (process.env.SILTA_APP_URL ?? 'http://localhost:5300').replace(/\/$/, '')
const out = path.join(here, '../content/media/screens/v3')
mkdirSync(out, { recursive: true })

const browser = await chromium.launch()
const phone = await browser.newContext({ viewport: { width: 375, height: 812 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true })
const desk = await browser.newContext({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 2 })
const page = await phone.newPage()

async function shot(p, name, opts = {}) {
  await p.waitForLoadState('networkidle')
  await p.waitForTimeout(400)
  await p.screenshot({ path: path.join(out, `${name}.png`), ...opts })
  console.log(name)
}

async function tap(name) {
  await page.getByText(name, { exact: true }).first().click()
  await page.waitForLoadState('networkidle')
  await page.waitForTimeout(300)
}

// 1. The invitation letter Hodan receives, in Finnish (the sheet only, full length).
const letterPage = await desk.newPage()
await letterPage.goto(`${base}/letter/cervical/fi`)
await letterPage.waitForLoadState('networkidle')
await letterPage.locator('article').first().screenshot({ path: path.join(out, 'letter-fi.png') })
console.log('letter-fi')

// 2. The Somali cervical guide the letter's QR code opens: start, part 1, part 2.
await page.goto(`${base}/r/so/learn/cervical`)
await shot(page, 'guide-so-start')
await tap('Bilow')
await shot(page, 'guide-so-why')
await tap('Xiga')
await shot(page, 'guide-so-visit')

// 3. The screening route in English.
await page.goto(`${base}/r/en`)
await page.waitForLoadState('networkidle')
await tap('Start')
await page.waitForURL(/\/v\//)
await shot(page, 'path-need')
await tap('I got a letter I do not understand')
await shot(page, 'path-route')
await tap('I live in Finland and have a home municipality')
await page.waitForTimeout(800)
await shot(page, 'path-door')
await page.getByText('SAY THIS IN FINNISH', { exact: false }).first().evaluate((el) => el.scrollIntoView({ block: 'start' }))
await page.waitForTimeout(300)
await page.screenshot({ path: path.join(out, 'path-script.png') })
console.log('path-script')
await tap('I contacted them')
await shot(page, 'path-outcome')
await tap('I got an appointment')
await page.getByLabel('When is your appointment?').fill('2026-12-01')
await tap('Save the date')
await tap('My visit is now')
await shot(page, 'path-visit')
await tap('Show your visit card')
await page.waitForURL(/\/card/)
await shot(page, 'path-card')
const code = page.url().match(/SLT-[0-9A-Z]{4}-[0-9A-Z]{4}/)[0]

// 4. The same route once more in Somali, as Hodan walks it, so the nurse's view asks for a
// Somali interpreter. Labels are looked up through the live content bundle (English → key → Somali).
async function bundle(lang) {
  const res = await fetch(`${base}/api/content/live?lang=${lang}`)
  return (await res.json()).texts
}
const [en, so] = await Promise.all([bundle('en'), bundle('so')])
const keyOf = Object.fromEntries(Object.entries(en).map(([k, v]) => [v.text, k]))
const tr = (english) => {
  const key = keyOf[english]
  if (!key || !so[key]) throw new Error(`no Somali text for "${english}"`)
  return so[key].text
}
await page.goto(`${base}/r/so`)
await page.waitForLoadState('networkidle')
await tap(tr('Start'))
await page.waitForURL(/\/v\//)
await tap(tr('I got a letter I do not understand'))
await tap(tr('I live in Finland and have a home municipality'))
await page.waitForTimeout(800)
await tap(tr('I contacted them'))
await tap(tr('I got an appointment'))
await page.getByLabel(tr('When is your appointment?')).fill('2026-12-01')
await tap(tr('Save the date'))
await tap(tr('My visit is now'))
await tap(tr('Show your visit card'))
await page.waitForURL(/\/card/)
await shot(page, 'path-card-so')
const soCode = page.url().match(/SLT-[0-9A-Z]{4}-[0-9A-Z]{4}/)[0]

// 5. What the nurse sees: the clinician view for Hodan's code, in Finnish.
const clinic = await desk.newPage()
await clinic.goto(`${base}/clinic/${soCode}`)
// The content column only (the page centres a ~640 px column on a 1280 px screen).
await shot(clinic, 'clinic-fi', { clip: { x: 320, y: 0, width: 640, height: 820 }, fullPage: true })
void code

// 6. The county view (desktop).
const county = await desk.newPage()
await county.goto(`${base}/county/helsinki`)
await shot(county, 'county-helsinki', { clip: { x: 320, y: 0, width: 640, height: 820 }, fullPage: true })
const journeysTop = await county.getByRole('heading', { name: 'Silta journeys' }).evaluate((el) => el.getBoundingClientRect().top + window.scrollY)
await shot(county, 'county-journeys', { clip: { x: 320, y: journeysTop - 24, width: 640, height: 820 }, fullPage: true })

await browser.close()
