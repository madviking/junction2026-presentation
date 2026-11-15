// Exports the site's deck (/presentation, content/presentation-v3.yaml) to PDF through reveal.js
// print mode. ?print-pdf also adds a page after the opener and per-slide links that point readers
// to the interactive deck online (app/main.py, presentation_v3.html).
// Uses the Playwright install in ../tech/frontend (no new dependency here).
//
//   node scripts/export_deck_pdf.mjs                                  # site at http://localhost:8400
//   SITE_URL=https://... OUT=/path/deck.pdf node scripts/export_deck_pdf.mjs
//
// Output: content/materials/silta-presentation.pdf
import { createRequire } from 'node:module'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const require = createRequire(path.join(here, '../../tech/frontend/package.json'))
const { chromium } = require('playwright')

const base = (process.env.SITE_URL ?? 'http://localhost:8400').replace(/\/$/, '')
const out = process.env.OUT ?? path.join(here, '../content/materials/silta-presentation.pdf')

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } })
await page.goto(`${base}/presentation?print-pdf`, { waitUntil: 'networkidle' })
// reveal lays out the print pages after 'ready'; give fonts, images and the embeds time to settle.
await page.waitForFunction(() => window.Reveal?.isReady?.() && document.querySelector('.pdf-page'))
await page.evaluate(() => document.fonts.ready)
await page.waitForTimeout(2500)
await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true })
await browser.close()
console.log(out)
