// Captures the admin and county screens for the "Already running" slide's spinning screen reel.
// Uses the Playwright install in ../tech/frontend (no new dependency here).
//
//   node scripts/capture_running_screens.mjs                      # app at http://localhost:5300
//   SILTA_APP_URL=https://... node scripts/capture_running_screens.mjs
//
// Signs in to admin with the public view-only demo account (the sign-in page's
// "Sign in as demo viewer" button), so nothing is changed. No paid model calls.
// The journey editor only shows when the app runs with VITE_FEATURE_JOURNEY_EDITOR=true; it is
// skipped when missing. Output: content/media/screens/running/*.png (1280 × 800 at 1.5×).
import { mkdirSync } from 'node:fs'
import { createRequire } from 'node:module'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const require = createRequire(path.join(here, '../../tech/frontend/package.json'))
const { chromium } = require('playwright')

const base = (process.env.SILTA_APP_URL ?? 'http://localhost:5300').replace(/\/$/, '')
const out = path.join(here, '../content/media/screens/running')
mkdirSync(out, { recursive: true })

const browser = await chromium.launch()
const desk = await browser.newContext({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1.5 })
const page = await desk.newPage()

// The demo account's "View-only demo" banner is hidden in the shots: the reel is about the screens.
async function hideDemoBanner() {
  await page.evaluate(() => {
    const title = [...document.querySelectorAll('body *')].find((el) => el.childElementCount === 0 && el.textContent.trim() === 'View-only demo')
    let box = title
    while (box?.parentElement && box.parentElement.textContent.length < 220) box = box.parentElement
    if (box) box.style.display = 'none'
  })
}

async function shot(name, route) {
  if (route) await page.goto(`${base}${route}`)
  await page.waitForLoadState('networkidle')
  await page.waitForTimeout(800)
  await hideDemoBanner()
  if (/sign-in/.test(page.url())) { console.log(`${name}: skipped (sign-in)`); return }
  await page.screenshot({ path: path.join(out, `${name}.png`) })
  console.log(name)
}

await page.goto(`${base}/admin/sign-in?next=%2Fadmin%2Fservice-paths`)
await page.getByRole('button', { name: 'Sign in as demo viewer' }).click()
await page.waitForURL(/\/admin\/service-paths/)
await shot('admin-service-paths')

await page.getByRole('tab', { name: 'Compare' }).click()
await shot('admin-service-paths-compare')

// One area's service path: its doors, the steps stage by stage, and the measured waits.
await page.goto(`${base}/admin/service-paths`)
await page.getByText('Helsingin kaupunki', { exact: false }).first().click()
await page.waitForURL(/\/admin\/service-paths\/[^/]+$/)
await shot('admin-area-doors')
for (const [name, tab] of [['admin-area-steps', 'Steps'], ['admin-area-screening', 'Screening'], ['admin-area-metrics', 'Measured values']]) {
  await page.getByRole('tab', { name: tab }).click()
  await shot(name)
}

for (const [name, route] of [
  ['admin-journey', '/admin/journey'],
  ['admin-content', '/admin/content'],
  ['admin-audio', '/admin/audio'],
  ['admin-versions', '/admin/versions'],
]) {
  await page.goto(`${base}${route}`)
  await page.waitForLoadState('networkidle')
  if (page.url().endsWith(route)) await shot(name)
  else console.log(`${name}: skipped (redirected to ${page.url()})`)
}

await shot('county-helsinki', '/county/helsinki')
await browser.close()
