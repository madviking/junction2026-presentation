// Captures the site screenshots used by README.md into docs/readme/raw/ (gitignored).
// Normally run through `bash scripts/readme_images.sh`, which also composes docs/readme/*.png.
// Uses the Playwright install in ../tech/frontend (no new dependency here).
//
//   node scripts/capture_readme_screens.mjs                    # site at http://localhost:8400
//   SITE_URL=https://... node scripts/capture_readme_screens.mjs
//
// Read-only: GET requests only, no sign-in, no paid model calls. The /try page embeds the
// live resident app, so its phone shows whatever app the site's `consumer` link points at.
import { createRequire } from 'node:module'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const require = createRequire(path.join(here, '../../tech/frontend/package.json'))
const { chromium } = require('playwright')

const base = (process.env.SITE_URL ?? 'http://localhost:8400').replace(/\/$/, '')
const out = path.join(here, '../docs/readme/raw')
fs.mkdirSync(out, { recursive: true })

const browser = await chromium.launch()

async function shot(name, url, { width = 1440, height = 900, before, wait = 2500 } = {}) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1.5 })
  await page.goto(`${base}${url}`, { waitUntil: 'networkidle' })
  await page.evaluate(() => document.fonts.ready)
  if (before) await before(page)
  await page.waitForTimeout(wait)
  await page.screenshot({ path: path.join(out, `${name}.png`) })
  await page.close()
  console.log(name)
}

// Deck slides: 1280x720 is the deck's own size; charts and reels animate in on arrival.
const slide = (id, opts = {}) =>
  shot(`deck-${id}${opts.suffix ?? ''}`, `/presentation#/${id}`, {
    width: 1280,
    height: 720,
    wait: 3500,
    ...opts,
    before: async (page) => {
      await page.waitForFunction(() => window.Reveal?.isReady?.())
      if (opts.drill) {
        await page.waitForTimeout(1500)
        await page.click(`[data-drill="${opts.drill}"]`)
      }
    },
  })

await shot('landing', '/')
await shot('try', '/try', { wait: 5000 })
await shot('tech-aiven', '/tech/aiven')
await shot('printouts', '/printouts')
await shot('record', '/presentation/record')
await shot('video', '/video')
await slide('hodan')
await slide('gap')
await slide('gap', { drill: 'gap-1', suffix: '-drill' })
await slide('pathway', { wait: 5000 })
await slide('ways-in', { wait: 5000 })
await slide('running', { wait: 4000 })
await slide('county')

await browser.close()
