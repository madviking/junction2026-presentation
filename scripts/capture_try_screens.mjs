// Captures the extra screens for the "Try the app" page (/try) from a running Silta app.
// Uses the Playwright install in ../tech/frontend (no new dependency here).
//
//   node scripts/capture_try_screens.mjs                      # app at http://localhost:5300
//   SILTA_APP_URL=https://... node scripts/capture_try_screens.mjs
//
// Signs in to admin with the public view-only demo account (the sign-in page's
// "Sign in as demo viewer" button), so nothing is changed. No paid model calls.
// Output: content/media/screens/try/*.png
import { mkdirSync } from 'node:fs'
import { createRequire } from 'node:module'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const require = createRequire(path.join(here, '../../tech/frontend/package.json'))
const { chromium } = require('playwright')

const base = (process.env.SILTA_APP_URL ?? 'http://localhost:5300').replace(/\/$/, '')
const out = path.join(here, '../content/media/screens/try')
mkdirSync(out, { recursive: true })

const browser = await chromium.launch()
const desk = await browser.newContext({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1.5 })
const page = await desk.newPage()

async function shot(name) {
  await page.waitForLoadState('networkidle')
  await page.waitForTimeout(500)
  await page.screenshot({ path: path.join(out, `${name}.png`) })
  console.log(name)
}

// County view: the public figures (first screen only). Its content column is narrow, so a
// narrow viewport fills the frame.
const narrow = await browser.newContext({ viewport: { width: 760, height: 560 }, deviceScaleFactor: 2 })
const countyPage = await narrow.newPage()
await countyPage.goto(`${base}/county/helsinki`)
await countyPage.waitForLoadState('networkidle')
await countyPage.waitForTimeout(500)
await countyPage.screenshot({ path: path.join(out, 'county.png') })
console.log('county')

// Admin: sign in as the view-only demo viewer, then the home and the content editor.
await page.goto(`${base}/admin/sign-in?next=%2Fadmin%2Fcontent`)
await page.getByRole('button', { name: 'Sign in as demo viewer' }).click()
await page.waitForURL(/\/admin\/content/)
await shot('admin-content')

await browser.close()
