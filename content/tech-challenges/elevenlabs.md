---
title: Best Use of ElevenLabs
partner: ElevenLabs
organiser: MLH
logo: /media/logos/mlh.png
logo_alt: MLH logo
summary: ElevenLabs reads every card and instruction aloud in four languages and turns spoken answers into text where speech recognition is good enough.
order: 20
criteria_source: brain/challenges/tech/mlh-elevenlabs.md
---

## What the challenge asks

- Give the hack a voice with ElevenLabs: natural, human-sounding, expressive AI audio.
- The organiser's text asks for "fully autonomous audio experiences" in the project, from voice apps to narration.
- Prize: wireless earbuds, one overall winner (`brain/challenges/tech/mlh-elevenlabs.md`).

## How Silta uses ElevenLabs

Many people Silta is for read Finnish poorly, and some read their own language poorly too. So every line in the resident app has a play button, and residents can answer by speaking. The backend module `backend/voice/` is the only place that calls ElevenLabs.

- **Text-to-speech for every card and instruction.** Symptom cards, route cards, outcome cards and visit-card next steps play aloud in English, Finnish, Somali and Arabic. One model (`eleven_v4`) and one multilingual voice cover all four languages (`backend/voice/capabilities.ts`).
- **Generated once, then cached.** A clip is made the first time a text is played, stored in the database and keyed by a hash of the exact text. When an admin edits a text, the old clip is never played again (`backend/voice/service.ts`, `backend/voice/README.md`).
- **Speech-to-text for answers.** A resident taps "Tap to speak", says what they noticed ("I found a lump in my breast"), and ElevenLabs Scribe turns it into text. The text goes through the same read-back as typed text: Silta asks "Did you mean: a new lump or swelling?" and nothing is chosen until the person taps Yes (`backend/voice/stt.ts`, `frontend/src/features/voice/`).
- **Language by language, based on measured quality.** We checked ElevenLabs' published coverage before building. Scribe is rated excellent for Finnish and English and good for Arabic, but only moderate for Somali (25–50% word error rate) (`brain/sources/2026-11-13-elevenlabs-language-coverage.md`). So:
  - English, Finnish and Arabic: voice in and voice out.
  - Somali: audio out only. Voice input is refused on purpose, and Somali speakers use the cards.
- **Human recordings win.** In the admin, a native speaker's recording can be uploaded for any text. Once approved it replaces the generated clip. Generated Somali audio can never be marked approved; only a human recording can (`backend/voice/admin.ts`).
- **Spend under control.** Every call writes a usage row with characters, seconds and cost. A spend cap stops new calls; stored audio keeps playing (`backend/voice/providers.config.ts`). After the overnight build, the usage page showed about $0.016 of ElevenLabs spend in the development database (`brain/notes/2026-11-14-0735-silta-app-walkthrough.md`).

## Architecture

- Resident taps play → `GET /api/voice/clip` → stored clip if one exists for this exact text, otherwise ElevenLabs text-to-speech once → stored in PostgreSQL → served with long cache headers.
- Resident taps the microphone → `POST /api/voice/transcribe` → ElevenLabs Scribe → transcript → `POST /api/cards/match` → read-back question → the person confirms.
- Admin → upload a human recording → listen → approve → residents now hear the human voice.

| Language | Voice input | Audio output | Generated audio starts as |
| --- | --- | --- | --- |
| English, Finnish | yes | yes | approved |
| Arabic | yes | yes | unchecked |
| Somali | no, cards instead | yes | unchecked, never approvable |

## What is live vs planned

Live (local app and tests):
- Text-to-speech in all four languages, one real round trip per language, with caching (`docs/proof/2026-11-14/voice.md`).
- Speech-to-text for English and Finnish with real calls; the Somali request is refused as designed (same file).
- Spoken input through to the read-back in the browser tests, using a test clip made with ElevenLabs text-to-speech (`frontend/e2e/`, `brain/notes/2026-11-14-0735-silta-app-walkthrough.md`).
- Admin upload, approval and the rule that an approved human recording wins.

Planned or not yet done:
- Running on the deployed app; today this runs locally.
- Audio for texts built from several pieces (the door title with the place, time limits, the code line).
- Native-speaker review of the Somali and Arabic texts and audio, and human Somali recordings. Nobody has yet listened to the generated clips to check pronunciation.
- Kurdish, which ElevenLabs does not offer as voice output (`brain/sources/2026-11-13-elevenlabs-language-coverage.md`); planned cards-first with human recordings.
- Zero-retention processing. It is enterprise-only, so ElevenLabs may keep request logs (`backend/voice/README.md`).

## Why it matters for the people we serve

Reading aloud lets someone with little Finnish, or limited reading skills in any language, follow every step in their own language. Speaking an answer is easier than typing it on a phone in a second language. We only offer voice input where it works well enough. Recordings and transcripts are never stored, and every spoken answer is read back for the person to confirm.
