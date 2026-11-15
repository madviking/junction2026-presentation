---
title: Pitch video — voice-over for the record cut
description: One continuous narration for /presentation/record, read at about 2.7 words a second over the 15-slide default cut, ending before 2:00. 268 words. Slide cues inline, timings, recording steps and what not to say.
tags: [video, voice-over, script, record]
author: Claude with the Silta team
updated: 2026-11-15
---

# Pitch video: voice-over for the record cut

**Hard limit 2:00.** One voice (Mea), about **2.7 words a second**, talking straight through. Pauses come at the ends of sentences, never between fragments. **268 words.**
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
> **[→ `pathway-simple`]** Of the three ways into cancer care, only screening is measured by language, and the gap opens at its first step. That's where Silta works.
>
> **[→ `silta`]** Silta is Finnish for bridge.
>
> **[→ `letter`]** A translated letter alone made no difference in a Norwegian trial. So Hodan scans the code on her letter, **[→ once: the letter shrinks into the guide]** and Silta explains the screening in Somali, read aloud: what happens, that she can ask for a woman to take the sample, and what to say at the desk in Finnish.
>
> **[→ Film: Olga]** The second way in is a symptom. Olga is fifty-eight and has found a lump.
> **[→ `noticed`, as the film ends]** She taps where it is, in Russian. Silta never rates her symptoms.
> **[→ `door`]** It shows each of them the right service in their county and the Finnish sentences to say.
> **[→ `visit`]** At the visit, the doctor reads Olga's answers in Finnish, on her own phone, with a request for a professional interpreter.
>
> **[→ `county`]** A county can start without an IT project: one printed code on the letters it already sends, measured with the registry's attendance by native language.
> **[→ `safe`]** Silta gives no diagnosis and stores no names.
> **[→ `running`]** It already runs in fourteen languages.
>
> **[→ `close`]** We propose a pilot in Helsinki. Silta works before the first appointment, from today.
> **[→ `team`]** Timo, Milla and Mea Railo.

## Timing check (at 2.7 words a second)

| Starts | Slide | Words |
| --- | --- | --- |
| 0:00 | Film: Hodan (15 s; the voice starts at 0:02) | 28 |
| 0:15 | `hodan` | 10 |
| 0:19 | `gap` | 28 |
| 0:31 | `pathway-simple` | 25 |
| 0:42 | `silta` | 5 |
| 0:45 | `letter` | 49 |
| 1:05 | Film: Olga (8 s) | 15 |
| 1:13 | `noticed` | 12 |
| 1:18 | `door` | 16 |
| 1:25 | `visit` | 21 |
| 1:33 | `county` | 25 |
| 1:43 | `safe` | 8 |
| 1:47 | `running` | 6 |
| 1:52 | `close` | 14 |
| 1:57 | `team` | 5 |
| **about 1:59** | **end** | **268** |

**If a take runs over 2:00,** cut "It already runs in fourteen languages." first and let the screen reel speak for itself (about 3 s). If it is still over, cut "on her own phone" (about 1 s).

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
| Only screening is measured by language; the gap opens at its first step | Pathway slide, findings and limitations |
| A translated letter made no difference | Randomised trial, Norway, n = 11,347: 46.5% vs 47.4% (`letter` → For the county) |
| A woman to take the sample; a professional interpreter | Silta app: cervical guide, rights part; visit summary (`visit`) |
| No diagnosis, no names | EU MDR Rule 11 · GDPR Art. 9 (`safe`) |
| 14 languages | Silta app, counted 14 Nov 2026 (`running`) |
