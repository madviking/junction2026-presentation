---
title: Pitch video — voice-over for the record cut
description: Word-for-word voice-over for /presentation/record, timed slide by slide to stay under 2:00. 216 words. Includes the recommended 16-slide cut (untick earlier, routes, reach), recording steps and what not to say.
tags: [video, voice-over, script, record]
author: Claude with the Silta team
updated: 2026-11-15
---

# Pitch video: voice-over for the record cut

**Hard limit 2:00** (the organisers say they will be strict). Target: **1:57**. **216 words** in all, one calm voice.
The same lines are in `content/presentation-video.yaml` as each slide's `notes`, so the narrator can read them in the speaker view (press **S** while the cut plays).

## The cut: three slides left out

With every slide ticked (19 entries), the cut runs **about 2:09** at a pace a viewer can follow, because the two films alone take 23 s. The default cut therefore leaves these three unticked (`skip: true` in `presentation-video.yaml`), so **Default cut** in the picker gives the 16 slides below:

| Left out | Why it can go |
| --- | --- |
| `earlier` (Found earlier) | The judges know early detection matters. It costs 6 s. |
| `routes` (Three routes, intro) | The simplified map that follows says the same thing. This slide also shows **57% vs 78%** right after the voice says **27%**, and 78 − 57 = 21 looks like an error. |
| `reach` (How do they find Silta?) | The 15-channels map right after it carries the point. |

Open the cut directly:

```
/presentation/record?slides=hodan-film,hodan,gap,pathway-simple,silta,letter,olga-film,noticed,door,visit,county,safe,ways-in,running,close,team
```

## Script

`/` short pause · `//` full pause · **bold** = lean on it · [brackets] = what you do

| Time | Slide | Sec | Voice-over | Words |
| --- | --- | --- | --- | --- |
| 0:00 | **Film: Hodan** | 15 | [Wait about 3 s, until she opens the envelope.] This is Hodan. / Fifty-four, in Helsinki for years. Her language is Somali. / This is her second invitation to cervical cancer screening. | 21 |
| 0:15 | `hodan` | 5 | [The letter slides into the drawer.] She puts it away. // And doesn't go. | 7 |
| 0:20 | `gap` | 11 | She is not alone. / When your native language isn't Finnish or Swedish, the same letter brings **twenty-seven percent** fewer people. / In every programme. | 23 |
| 0:31 | `pathway-simple` | 10 | Three ways lead into cancer care. / The gap opens at the very first step, before any appointment. / That's where Silta works. | 21 |
| 0:41 | `silta` | 4 | Silta. / Finnish for "bridge". | 4 |
| 0:45 | `letter` | 11 | [Press → once after "letter": it shrinks into the guide.] Hodan scans the code on her letter. / Silta explains the screening in Somali, read aloud: / what happens, and her rights. | 20 |
| 0:56 | **Film: Olga** | 8 | A second way in. / Olga, fifty-eight, has found a lump. | 10 |
| 1:04 | `noticed` | 6 | She taps where it is, in Russian. / Silta never rates her symptoms. | 12 |
| 1:10 | `door` | 6 | It shows each of them the right service, / and the Finnish words to say. | 14 |
| 1:16 | `visit` | 6 | At the visit, the doctor reads her answers in Finnish. | 10 |
| 1:22 | `county` | 9 | For a county, it starts with no IT project and no personal data: / one printed code on letters it already sends. | 21 |
| 1:31 | `safe` | 5 | Not a medical device. / No names stored. / AI that asks first. | 11 |
| 1:36 | `ways-in` | 5 | People find it through the letter, / their community, / or their phone. | 11 |
| 1:41 | `running` | 6 | And it's already running, / in fourteen languages. [Let the screen reel play.] | 7 |
| 1:47 | `close` | 8 | Our ask: / a Helsinki pilot, measured with the registry's own numbers. // Silta works before the first appointment. / From today. | 19 |
| 1:55 | `team` | 3 | Timo, Milla and Mea Railo. | 5 |
| **1:58** | | | **Cut the export here, under 2:00.** | **216** |

**Pace:** about 2.2 words a second. Each line ends with room to breathe. On a slide whose heading flies in (`gap`, `door`, `visit`, `county`, `safe`, `running`, `close`), start speaking as the heading lands, not before.

## What the voice does not say, and why

- **"Once people are inside, follow-up is equal"** (in the earlier video plan). Breast follow-up isn't measured by language, and after a positive bowel test there is a gap (68% vs 77% have the colonoscopy). The script says only that the gap opens at the first step.
- **"Silta works at the door"** (in the earlier video plan). The deck's close now reads "before the first appointment".
- **57 vs 78 next to 27%.** That is why `routes` is unticked.
- **"Human-recorded" Somali audio.** The Somali audio is generated and marked unchecked; "read aloud" is accurate.
- **Lives saved, savings, or that language causes the gap.**

## Recording

1. Open the cut URL above. Leave "Show the footer" and "Show the drill-in buttons" unticked. Click Start (it goes full screen).
2. Record the screen at 1080p. Press → on each slide's cue. The films move on by themselves when they end.
3. Record the voice separately, in a quiet room, reading from this table or the speaker view (S). Lay it over the capture and nudge each slide's cut to its line.
4. **The disclaimer must be in the video somewhere** (the record cut leaves it out): *"Hodan and Olga are composite people. Scenes are AI-generated and illustrative."* The end card or a small caption on the Hodan film both work. It doesn't count against the words above, and it is safest on screen rather than spoken.
5. Export, check the length is **under 2:00**, then put the link in `content/site.yaml` → `video.url`.

## Sources for what is said

| Said | Source (on the deck) |
| --- | --- |
| 27% fewer, every programme | Finnish Cancer Registry, screening by native language, 2024 (`gap`) |
| The gap opens at the first step | Pathway slide: only screening is measured by language, and the gap is largest at attendance |
| 14 languages | Silta app, counted 14 Nov 2026 (`running`) |
| Not a medical device, no names, AI asks first | EU MDR Rule 11 · GDPR Art. 9 · EU AI Act (`safe`) |
