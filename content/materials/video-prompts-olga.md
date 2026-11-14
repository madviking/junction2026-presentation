---
title: Olga — video prompts for Google AI Studio (Veo)
description: Five shot prompts for Olga's symptom route ("I noticed something"), matching deck v3's noticed and visit slides, with the character block, negative prompt, settings and the real Silta screens to lay over the blank phone screens in Descript.
tags: [video, pitch, prompts, olga]
author: Milla Railo
updated: 2026-11-14
---

# Olga — video prompts

**From the deck (v3, slides `noticed` and `visit`):** Olga, 58, has found a lump. She taps where
it is, or says it in her own words, in Russian. Silta never rates her symptoms. It shows her the right
door and the Finnish words, and at the visit she shows the doctor a Finnish summary on her own phone.
Olga is a composite person.

**Her barriers (master narrative):** she doesn't know whether to call the health station, her
employer's clinic or 116117; she would prefer a female doctor; it's a sensitive thing to say out loud.

**In the 2-minute video:** a short second way in, about 12–15 s, after Hodan's rights scene. Shots
2 + 3 + 5 are enough; 1 and 4 are extras.

## Settings for every shot

- Model: Veo (latest in AI Studio), **16:9**, **8 s**, highest resolution available.
- Audio: generate without dialogue; mute it in Descript and use room tone.
- Paste the **character block** and the **look block** into every prompt unchanged, so Olga stays the
  same person.

**Character block**
> Olga, a Russian-speaking woman aged 58, short ash-blonde hair, thin-rimmed reading glasses, navy knit
> cardigan over a light grey blouse, dark trousers, a calm, private, practical person.

**Look block**
> Soft natural winter daylight in Espoo, Finland. Muted warm neutral colours, off-white walls, light wood.
> 16:9, shallow depth of field, slow steady handheld camera, no zooms. No readable text anywhere, no
> logos, no other identifiable people.

**Negative prompt (every shot)**
> text, subtitles, readable writing, app interface, user interface on screen, logos, brand names,
> signage, red or orange clothing or props, nudity, undressing, medical examination, hospital bed,
> needles, dramatic crying, fast camera movement, zoom

## Shot 1 · She notices (extra, 5 s)

> [Character block] In her bedroom in the morning, fully dressed, she finishes buttoning her cardigan in
> front of a wardrobe mirror. She pauses, her hand resting still over her upper chest on top of the
> cardigan, and her expression turns quietly worried. She lowers her hand and looks away from the mirror.
> [Look block]

Discreet on purpose: the hand rests over clothing, nothing more.

## Shot 2 · Who do I even call? (4–5 s)

> [Character block] At her kitchen table, she holds her phone in both hands and looks at it, unsure,
> then glances at a paper calendar on the wall and back at the phone. A cup of tea beside her, steam
> rising. The phone screen faces away from the camera. [Look block]

## Shot 3 · She taps where it is (4 s) — lay the real screen over it

> [Character block] Over-the-shoulder close-up: she holds her phone low over the kitchen table and taps
> the screen once with her index finger, then waits. The phone screen is plain, evenly lit, pure white,
> with nothing on it. Her face is soft in the background. [Look block]

In Descript, put the real Silta screen on the white phone screen (track it if the hand moves):
`content/media/screens/v3/olga-cards-ru.png` (her symptom screen in Russian, chest chosen,
"A new lump or swelling" ticked). Alternatives: `content/media/screens/slider-02-body-map.png`,
`content/media/screens/partner-gemini-symptom.png` (the Gemini "did you mean…" read-back).

## Shot 4 · The call, with the Finnish words (extra, 5 s)

> [Character block] Standing by a bright window, she holds her phone to her ear and speaks slowly and
> carefully, glancing down at a second phone or tablet lying on the windowsill, whose screen faces away
> from the camera. She nods once, relieved. [Look block]

Pairs with `content/media/screens/v3/path-script.png` as a cut-in.

## Shot 5 · At the visit (5 s) — lay the real screen over it

> [Character block] In a calm, ordinary consultation room with a desk, a window and a plant, seen over
> her shoulder, she turns her phone around and holds it out across the desk toward a female doctor in a
> white coat, who is out of focus, leans in and nods. The phone screen is plain, evenly lit, pure white,
> with nothing on it. No medical equipment in view. [Look block]

Overlay: `content/media/screens/v3/olga-summary-fi.png` (the Finnish summary: interpreter needed,
"Uusi kyhmy tai turvotus", the route to care, the visit date).

## Voice-over for the Olga beat (≈ 35 words)

> A second way in. Olga, fifty-eight, has found a lump. She taps where it is, in Russian. Silta never
> rates her symptoms. It shows her the right door, and at the visit, the doctor reads it in Finnish.

## Before export

- Caption or end-card line: *"Hodan and Olga are composite people. Scenes are AI-generated and
  illustrative."*
- Every Silta screen in shot is a real capture laid over a blank screen, never one the model drew.
- If Veo draws text or a UI on the phone anyway, regenerate or cover it fully with the overlay.
