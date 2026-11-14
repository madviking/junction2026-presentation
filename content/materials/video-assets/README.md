---
title: Pitch video assets for Descript
description: Rendered motion-graphic clips, real Silta screens in Somali and English, transparent overlays and app audio for "The letter in the drawer". Drop the folders into Descript in timeline order.
tags: [video, pitch, assets, descript]
author: Milla Railo
updated: 2026-11-14
---

# Pitch video assets

Everything here is built from Silta's real screens and the site's palette and fonts. The storyline
is `../video-strategy.html` ("The letter in the drawer"). All clips are 1920×1080, 30 fps, H.264
MP4, without sound; the voice-over and music are added in Descript.

## Timeline: which clip goes where

| Video time | Clip (`clips/`) | Length | Voice-over over it |
| --- | --- | --- | --- |
| 0:00–0:15 | *Table top: letter lands, drawer* (film) → `01-questions.mp4` | 11 s | none; room tone |
| 0:15–0:40 | `02-one-in-nine.mp4` → `03-bars.mp4` → `04-cervical-gap.mp4` → `05-somali.mp4` | 5.5 + 8.5 + 5.5 + 6 s | "One in nine people …" |
| | `06-pathway.mp4` | 9 s | "The gap opens at the door …" |
| 0:40–0:55 | `07-two-paths.mp4` | 13 s | "We could have built for the county …" |
| 0:55–1:33 | *Table top: photographing the letter* (film) → `08-phone-letter.mp4` → `09-phone-visit.mp4` → `10-phone-rights.mp4` | 8.5 + 10 + 11 s | "Hodan photographs her letter …" |
| 1:33–1:50 | `11-ladder.mp4` | 14 s | "Every step the health system takes …" |
| 1:50–2:00 | *Table top: letter out, empty drawer* (film) → `12-end.mp4` | 8 s | "Silta stores no names …" |

The clips add up to about 110 s; trim them in Descript to fit the voice-over. Each scene builds,
then holds its last frame for a moment, so cutting the tail is safe. `stills/` has the last frame
of every clip as a PNG, for freeze-frames, thumbnails or a slower cut.

## Other folders

- **`screens/`**: real app screens from the live Silta app, 390×844 CSS px at 3×.
  `so-*` in Somali, `en-*` the same screens in English (use them to write the subtitles).
  `*-full.png` is the whole page, for your own pan in Descript.
  `so-03-letter-result*.png` is a real Gemini reading of the example letter, captured on 14 Nov.
  `letter-fi-no-qr.png` / `letter-fi-with-qr.png` are the example letter, to print as the prop
  or to use full screen.
- **`overlays/`**: transparent PNGs at 2× to lay over filmed shots. They are the five questions
  (`q1` … `q5`, plus `-answered` versions with a tick), `name-hodan`, the partner chips, the
  composite-persona note and the source lines.
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
- Ask Timo whether the Somali guide audio is human-recorded or ElevenLabs, and keep the
  "ElevenLabs reads it aloud" chip only on the Finnish desk sentences if it's human.
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
