---
title: Pitch video — voice-over for the record cut
description: One continuous narration for /presentation/record, read at about 2.8 words a second over the 15-slide default cut, ending before 2:00. 290 words, with the technology behind it (ElevenLabs, Gemini, Aiven). Slide cues inline, timings, recording steps and what not to say.
tags: [video, voice-over, script, record]
author: Claude with the Silta team
updated: 2026-11-15
---

# Pitch video: voice-over for the record cut

**Hard limit 2:00.** One voice (Mea), about **2.8 words a second**, talking straight through. Pauses come at the ends of sentences, never between fragments. **290 words.**
The same lines are in `content/presentation-video.yaml`, in each slide's `notes`, so they also show in the speaker view (press **S** while the cut plays).

## The cut

The default cut is the **15 entries** below. The picker's **Default cut** button gives exactly these. Left out (`skip: true`):
- `earlier`: the judges know that early detection matters.
- `routes`: it shows 57% vs 78% right after the voice says 27%, and 78 − 57 = 21 reads as an error.
- `pathway`: the data-heavy map. The simple map plays instead.
- `reach` and `ways-in`: the discovery part.

## Read-through

Read it as one text. **[→ slide]** marks where the next slide comes in. Keep talking through slide changes and through the headings that fly in; don't wait for them.

> **[Film: Hodan. Start about 2 s in, as she opens the envelope.]**
> This is Hodan. She is fifty-four, has lived in Helsinki for years, and her language is Somali. This is her second invitation to cervical cancer screening, in Finnish.
> **[→ `hodan`, as the film ends]** She puts it in a drawer, and she doesn't go.
>
> **[→ `gap`]** She is not alone. People whose native language isn't Finnish or Swedish get the same letters, and twenty-seven percent fewer of them come, in every screening programme.
>
> **[→ `pathway-simple`]** People reach cancer care in three ways, and the gap opens at the start, before anyone in health care has met them. That's where Silta works.
>
> **[→ `silta`]** Silta is Finnish for bridge.
>
> **[→ `letter`]** Hodan scans the code on her letter, **[→ once: the letter shrinks into the guide]** and Silta explains the screening in Somali, read aloud: what happens, that she can ask for a woman to take the sample, and what to say at the visit, in Finnish.
>
> **[→ Film: Olga]** The second way in is a symptom. Olga is fifty-eight and has found a lump.
> **[→ `noticed`, as the film ends]** She taps where it is, in Russian. Silta never rates her symptoms.
> **[→ `door`]** It shows each of them the right service and the Finnish sentences to say.
> **[→ `visit`]** At the visit, the doctor reads Olga's answers in Finnish, on her own phone.
>
> **[→ `county`]** A county needs no IT project to join. It adds one printed code to the letters it already sends, and the registry's figures by native language show whether more people come.
> **[→ `safe`]** Silta gives no diagnosis and stores no names.
> **[→ `running`]** It already runs in fourteen languages. ElevenLabs reads it aloud, turns speech into text, and runs a phone line in the caller's language. Gemini matches a person's words to a card and asks first. It all runs on Aiven, in the EU.
>
> **[→ `close`]** We propose a pilot in Helsinki. Silta works before the first appointment, from today.
> **[→ `team`]** Timo, Milla and Mea Railo.

## Timing check (at 2.8 words a second)

| Starts | Slide | Words |
| --- | --- | --- |
| 0:00 | Film: Hodan (15 s; the voice starts at 0:02) | 28 |
| 0:15 | `hodan` | 10 |
| 0:19 | `gap` | 27 |
| 0:29 | `pathway-simple` | 26 |
| 0:39 | `silta` | 5 |
| 0:42 | `letter` | 38 |
| 0:56 | Film: Olga (8 s) | 15 |
| 1:04 | `noticed` | 12 |
| 1:09 | `door` | 14 |
| 1:14 | `visit` | 14 |
| 1:20 | `county` | 32 |
| 1:32 | `safe` | 8 |
| 1:35 | `running` | 42 |
| 1:51 | `close` | 14 |
| 1:57 | `team` | 5 |
| **about 1:59** | **end** | **290** |

This needs a brisk 2.8 words a second; at 2.7 the same text runs to about 2:02. **If a take runs over 2:00, cut in this order:**
1. The spoken names on `team` (about 2 s; the names are on the slide).
2. "Gemini matches a person's words to a card and asks first." (about 4 s)
3. "on her own phone" (about 1 s)

## What the voice doesn't say

- **"Once people are inside, follow-up is equal."** Breast follow-up isn't measured by language, and after a positive bowel test there is a gap (68% vs 77% have the colonoscopy).
- **"Silta works at the door."** The deck's close says "before the first appointment".
- **"Human-recorded" Somali audio.** The Somali audio is generated and marked unchecked.
- **Lives saved, savings, or that language causes the gap.**

## Recording

1. Open `/presentation/record` (the **Record the video** card on the team page). Click **Default cut**, leave the footer and the drill-in buttons unticked, then click Start.
2. Record the screen at 1080p. Press → at each **[→]**. The films move on by themselves.
3. Record the voice in one take, in a quiet room, reading the text above. Then nudge the slide cuts to the voice, not the other way round.
4. **The disclaimer must be in the video** (the record cut leaves it out): *"Hodan and Olga are composite people. Scenes are AI-generated and illustrative."* A small caption on the Hodan film or an end card both work.
5. Export, check the length is **under 2:00**, then put the link in `content/site.yaml` → `video.url`.

## Sources for what is said

| Said | Source |
| --- | --- |
| 27% fewer, in every programme | Finnish Cancer Registry, screening by native language, 2024 (`gap`) |
| The gap opens at the start | Pathway slide: the measured gap is largest at attendance, the first step |
| A woman to take the sample; the Finnish summary at the visit | Silta app: cervical guide, rights part; visit summary (`visit`) |
| No diagnosis, no names | EU MDR Rule 11 · GDPR Art. 9 (`safe`) |
| 14 languages; ElevenLabs reads aloud, turns speech into text, runs the phone line; Gemini matches words to a card and asks; Aiven, in the EU | Silta app; `running` → Gemini, ElevenLabs and Aiven drill-ins |
