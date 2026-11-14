---
title: Pitch video assets for Descript
description: Rendered motion-graphic clips, real Silta screens in Somali and English, transparent overlays and app audio for "The letter in the drawer". Drop the folders into Descript in timeline order.
tags: [video, pitch, assets, descript]
author: Milla Railo
updated: 2026-11-14
---

# Pitch video assets

Everything here follows the Silta design system (`../silta-design-system.html`, deck v3): the deck's
frame (rail with kicker and Hodan's path, head and stage, foot with source) at 1920×1080, every deck
size × 1.5, colour by meaning (coral = Hodan and the gap, lake = Silta and facts, moss = money),
300 ms fades and one designed moment per scene. The storyline is `../video-strategy.html`. All clips
are 1920×1080, 30 fps, H.264 MP4, without sound; the voice-over and music are added in Descript.

## Timeline: which clip goes where

| Video time | Clip (`clips/`) | Length | Designed moment |
| --- | --- | --- | --- |
| 0:00–0:18 | *Table top: letter lands* (film) → `01-questions` → `02-drawer` | 10 + 8 s | the letter lands; the letter slides into the drawer |
| 0:18–0:45 | `03-gap-number` → `04-gap-bars` → `05-trend` → `06-somali` | 6 + 8 + 7.5 + 6 s | 27% counts up; bars grow; lines draw |
| 0:45–1:02 | `07-door` → `08-why` | 8.5 + 11 s | the first step turns coral; one path crawls, the other is there at once |
| 1:02–1:35 | *Table top: photographing the letter* (film) → `09-letter-photo` → `10-visit` → `11-rights` | 9 + 10 + 11 s | paper turns into the phone; coral questions turn lake as they are answered |
| 1:35–2:00 | `12-county` → `13-close` | 12 + 9 s | the clinic screen slides in; the letter with its QR strip rises out of the drawer |

The clips add up to about 116 s; trim the holds to fit the voice-over. `stills/` has the last
frame of every clip.

**The headline number is now "27% fewer come"** (a relative drop, as in deck v3), not "about 20
points". Update the voice-over in `../video-strategy.html` to match.

## Other folders

- **`screens/`**: real app screens from the live Silta app, 390×844 CSS px at 3×.
  `so-*` in Somali, `en-*` the same screens in English (use them to write the subtitles).
  `*-full.png` is the whole page, for your own pan in Descript.
  `so-03-letter-result*.png` is a real Gemini reading of the example letter, captured on 14 Nov.
  `letter-fi-no-qr.png` / `letter-fi-with-qr.png` are the example letter, to print as the prop
  or to use full screen.
- **`overlays/`**: transparent PNGs at 2× to lay over filmed shots: the five question plates
  (`q1` … `q5`, plus `-answered` with the lake bar and tick), the lower thirds `lower-third-hodan`
  and `lower-third-silta`, a caption plate, partner tags and source lines.
- **`deck/`**: the deck's own letter, QR strip, clinic screen and partner logos, used by the scenes.
- **`audio/`**: audio the app itself plays, downloaded from the live app. `fi-desk-*` is the
  Finnish sentences for the desk; `so-*` is Somali guide audio. Put `fi-desk-woman-takes-sample.mp3`
  under the end of `10-phone-rights.mp4`, where the play button is visible.

## Still to film or record

1. Table-top shots, about 30 minutes: the letter lands, the drawer with two old envelopes,
   photographing the letter, then the letter out and the empty drawer. Print
   `screens/letter-fi-no-qr.png` as the letter.
2. The voice-over, about 250 words (script in `../video-strategy.html`).
3. A quiet music bed.

## Check before export

- `so-03-letter-result` is machine-made text from a live Gemini call. Re-read it against the
  letter before export; each capture run makes a new reading. `so-03a-letter-reading.png` is the
  "reading your letter…" screen that comes before it.
- The Somali guide audio is human-recorded (deck v3), so the ElevenLabs tag sits only on the
  Finnish desk sentences.
- The ladder shows QR, visit code and kit offer as BUILT, not live in any county.

## Rebuild

```bash
node scripts/video/capture.mjs                      # screens + letter (one Gemini call on the live app)
swiftc -O scripts/video/encode.swift -o /tmp/silta-encode
ENCODER=/tmp/silta-encode node scripts/video/render.mjs           # all clips, stills, overlays
ENCODER=/tmp/silta-encode node scripts/video/render.mjs 03-bars   # one clip
```

The scenes are in `scripts/video/scenes.html`. To preview one in a browser, open
`scenes.html?scene=03-bars&play`. They need Google Chrome and the Playwright install in
`../junction2026tech/frontend`. ffmpeg is not needed: the encoder uses macOS AVFoundation.
