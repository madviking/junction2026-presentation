// Renders scripts/video/scenes.html to MP4 clips, last-frame stills and transparent overlay PNGs.
//   swiftc -O scripts/video/encode.swift -o /tmp/silta-encode
//   ENCODER=/tmp/silta-encode node scripts/video/render.mjs [scene-id ...]
// Output: content/materials/video-assets/{clips,stills,overlays}/
import { createRequire } from 'node:module'
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const require = createRequire(path.join(here, '../../../junction2026tech/frontend/package.json'))
const { chromium } = require('playwright')
const assets = path.join(here, '../../content/materials/video-assets')
const encoder = process.env.ENCODER
if (!encoder) throw new Error('set ENCODER to the compiled encode.swift binary')
const FPS = Number(process.env.FPS ?? 30)
const url = pathToFileURL(path.join(here, 'scenes.html')).href

const browser = await chromium.launch({ channel: 'chrome' })
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })
const page = await ctx.newPage()
await page.goto(url); await page.evaluate(() => window.ready)
const scenes = await page.evaluate(() => window.SCENES)
const overlays = await page.evaluate(() => window.OVERLAYS)
const only = process.argv.slice(2)

for (const [id, dur] of Object.entries(scenes)) {
  if (only.length && !only.includes(id) && !only.includes('scenes')) continue
  await page.goto(`${url}?scene=${id}`); await page.evaluate(() => window.ready); await page.waitForTimeout(300)
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), `silta-${id}-`))
  const n = Math.round(dur * FPS)
  for (let i = 0; i < n; i++) {
    await page.evaluate((t) => window.render(t), i / FPS)
    await page.screenshot({ path: path.join(dir, `frame_${String(i).padStart(5, '0')}.png`) })
  }
  fs.copyFileSync(path.join(dir, `frame_${String(n - 1).padStart(5, '0')}.png`), path.join(assets, 'stills', `${id}.png`))
  console.log(execFileSync(encoder, [dir, String(FPS), path.join(assets, 'clips', `${id}.mp4`)]).toString().trim())
  fs.rmSync(dir, { recursive: true })
}

if (!only.length || only.includes('overlays')) {
  for (const id of overlays) {
    await page.goto(`${url}?overlay=${id}`); await page.evaluate(() => window.ready); await page.waitForTimeout(200)
    const el = page.locator('#ov > *').first()
    await page.evaluate(() => { document.documentElement.style.background = 'transparent' })
    const ctx2 = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 })
    const p2 = await ctx2.newPage(); await p2.goto(`${url}?overlay=${id}`); await p2.evaluate(() => window.ready); await p2.waitForTimeout(200)
    await p2.locator('#ov > *').first().screenshot({ path: path.join(assets, 'overlays', `${id}.png`), omitBackground: true })
    await ctx2.close()
    console.log('overlay', id, await el.count())
  }
}
await browser.close()
