// Captures the phone screenshots for the landing-page slider from a running Silta app.
// Uses the Playwright install in ../tech/frontend (no new dependency here).
//
//   node scripts/capture_screens.mjs                      # app at http://localhost:5300
//   SILTA_APP_URL=https://... node scripts/capture_screens.mjs
//
//   node scripts/capture_screens.mjs --with-matching      # also the Gemini read-back screens
//
// Every run starts new anonymous visits in that app's database (local: test data).
// --with-matching types three answers into "Describe in your own words", i.e. three paid
// card-matching calls (Gemini Decision 1, well under one cent in total).
// Output: content/media/screens/slider-*.png and partner-*.png (375x812 CSS px at 2x).
import { createRequire } from 'node:module'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const require = createRequire(path.join(here, '../../tech/frontend/package.json'))
const { chromium } = require('playwright')

const base = (process.env.SILTA_APP_URL ?? 'http://localhost:5300').replace(/\/$/, '')
const out = path.join(here, '../content/media/screens')

async function text(lang, key) {
  const res = await fetch(`${base}/api/content/live?lang=${lang}`)
  const bundle = await res.json()
  const value = bundle.texts[key]?.text
  if (!value) throw new Error(`no text for ${key} in ${lang}`)
  return value
}

const browser = await chromium.launch()
const context = await browser.newContext({ viewport: { width: 375, height: 812 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true })
const page = await context.newPage()

/** Screenshot of the viewport: from the top, or with `focus` scrolled to the middle. */
async function shot(name, focus) {
  if (focus) await focus.evaluate((el) => el.scrollIntoView({ block: 'center' }))
  else await page.evaluate(() => window.scrollTo(0, 0))
  await page.waitForTimeout(300)
  const file = name.startsWith('partner-') ? `${name}.png` : `slider-${name}.png`
  await page.screenshot({ path: path.join(out, file) })
  console.log(file)
}

async function describe(words) {
  await page.getByLabel('Describe in your own words').fill(words)
  await page.getByRole('button', { name: 'Check', exact: true }).click()
}

async function startVisit(lang) {
  await page.goto(`${base}/r/${lang}`)
  await page.getByText(await text(lang, 'ui.journey.start.button'), { exact: true }).click()
  await page.waitForURL(/\/v\//)
}

// 1. Language picker: the first screen.
await page.goto(`${base}/`)
await page.waitForLoadState('networkidle')
await shot('01-language')

// 2-3. Picture symptom picker in English, then a body part and a card chosen.
await startVisit('en')
await page.getByRole('button', { name: 'I have a symptom that worries me' }).click()
await page.getByRole('group', { name: 'Where do you feel it?' }).waitFor()
await shot('02-body-map')
await page.getByRole('button', { name: 'Chest, breast and armpit' }).click()
await page.getByRole('button', { name: 'A cough for over 3 weeks' }).click()
await shot('03-body-map-chosen')

// 4-5. Where the person gets care, then the door with the Finnish call script.
await page.getByRole('button', { name: 'Continue', exact: true }).click()
await page.getByRole('button', { name: 'I live in Finland and have a home municipality' }).waitFor()
await shot('04-route')
await page.getByRole('button', { name: 'I live in Finland and have a home municipality' }).click()
await page.waitForLoadState('networkidle')
await page.waitForTimeout(800)
await shot('05-door')

// 6. The same picture picker in Arabic (right to left).
await startVisit('ar')
const symptomCard = await text('ar', 'journey.outcome.describe.symptom.card')
await page.getByRole('button', { name: symptomCard }).click()
await page.getByRole('group', { name: await text('ar', 'ui.journey.body.label') }).waitFor()
await shot('06-body-map-ar')

if (process.argv.includes('--with-matching')) {
  // Gemini Decision 1: own words -> read-back of one card; a question -> a reviewed answer card.
  await startVisit('en')
  await page.getByRole('button', { name: 'I have a symptom that worries me' }).click()
  await describe('I found a hard lump in my left breast last week')
  const symptomReadback = page.getByRole('group', { name: /^Did you mean/ })
  await symptomReadback.waitFor({ timeout: 30000 })
  await shot('partner-gemini-symptom', page.getByLabel('Describe in your own words'))
  await symptomReadback.getByRole('button', { name: 'Yes' }).click()
  await page.getByRole('button', { name: 'Continue', exact: true }).click()

  await page.getByRole('button', { name: 'I live in Finland and have a home municipality' }).waitFor()
  await describe('I study at the University of Helsinki')
  const routeReadback = page.getByRole('group', { name: /^Did you mean/ })
  await routeReadback.waitFor({ timeout: 30000 })
  await shot('partner-gemini-route', page.getByLabel('Describe in your own words'))
  await routeReadback.getByRole('button', { name: 'No' }).click()

  await describe("They asked for my Kela card. I don't know what it is.")
  const answer = page.getByRole('status').getByRole('group')
  await answer.waitFor({ timeout: 30000 })
  await shot('partner-gemini-question', page.getByLabel('Describe in your own words'))
}

await browser.close()
