---
title: Best Use of ElevenLabs
partner: ElevenLabs
organiser: MLH
logo: /media/logos/mlh.png
logo_alt: MLH logo
summary: ElevenLabs reads every card and instruction aloud in 13 languages and turns spoken answers into text where speech recognition is good enough.
order: 20
criteria_source: brain/challenges/tech/mlh-elevenlabs.md
# Glance: rendered as visuals at the top of the page (see AGENTS.md, Tech-partner pages).
fit:
  steps:
    describe: Picture cards read aloud; spoken answers become text
    route: Route cards read aloud
    visit: Visit-card next steps read aloud
    after: Outcome cards read aloud
    admin: A native speaker's recording replaces generated audio
numbers:
- value: '13'
  label: 'languages read aloud, from Finnish and Swedish to Russian, Arabic, Somali, Persian, Chinese, Cantonese, Vietnamese and Thai'
- value: '12'
  label: languages built for voice input; Somali answers by cards on purpose
- value: 1×
  label: each clip generated once and cached; an edited text never plays old audio
live:
- Text-to-speech in all 13 languages, cached, one real clip per language
- Speech-to-text for English and Finnish, real calls
- Speech-to-text biased towards Finnish health care words
- Spoken answer to read-back, in browser tests
- Admin upload and approval of human recordings
planned:
- Phone line: an ElevenLabs agent answers a real number (simulated call passes)
- Running on the deployed app
- Native-speaker review of the 11 placeholder languages' texts and audio
- Speech-to-text tried for real in the nine added languages
- Human Somali recordings
- Kurdish, cards-first with human recordings
screenshots:
- src: /media/screens/slider-02-body-map.png
  alt: "'What worries you?' with a body figure and big picture cards, each with a speaker button."
  caption: For people who read little, every picture card has a speaker button that plays ElevenLabs audio.
- src: /media/screens/slider-04-route.png
  alt: "'Where do you get health care?' with a speaker button on each question and a Tap to speak microphone."
  caption: Every question plays aloud. Tap to speak sends the answer to ElevenLabs Scribe.
- src: /media/screens/slider-05-door.png
  alt: "The call script: each Finnish sentence and its meaning, each with its own speaker button."
  caption: The sentence to say on the phone. One button plays the Finnish, the other its meaning.
- src: /media/screens/slider-06-body-map-ar.png
  alt: "The same picture symptom screen in Arabic, right to left, with speaker buttons."
  caption: The same cards in Arabic. Generated Arabic audio stays unchecked until a native speaker reviews it.
---
## How Silta uses ElevenLabs

Many people Silta is for read Finnish poorly, and some read their own language poorly too. So every line in the resident app has a play button, and residents can answer by speaking. The backend module `backend/voice/` is the only place that calls ElevenLabs.

- **Text-to-speech for every card and instruction.** Symptom cards, route cards, outcome cards and visit-card next steps play aloud in 13 languages: English, Finnish, Swedish, Russian, Estonian, Ukrainian, Arabic, Somali, Persian, Mandarin, Cantonese, Vietnamese and Thai. One model (`eleven_v4`) and one multilingual voice cover them all (`backend/voice/capabilities.ts`). The symptom step opens in a picture version for people who read little: a body figure to tap where it is, and big picture cards, each with the same play button (`frontend/src/features/journey/components/SymptomBodyPicker.tsx`).
- **Generated once, then cached.** A clip is made the first time a text is played, stored in the database and keyed by a hash of the exact text. When an admin edits a text, the old clip is never played again (`backend/voice/service.ts`, `backend/voice/README.md`).
- **Speech-to-text for answers.** A resident taps "Tap to speak", says what they noticed ("I found a lump in my breast"), and ElevenLabs Scribe turns it into text. The text goes through the same read-back as typed text: Silta asks "Did you mean: a new lump or swelling?" and nothing is chosen until the person taps Yes (`backend/voice/stt.ts`, `frontend/src/features/voice/`).
- **Finnish health care words.** Every transcription sends Scribe our glossary as key terms (Kela-kortti, terveysasema, lähete, OmaKanta …, in Finnish and the person's language), so "Kela card" is not written as "Kellogg card". Known mishearings left in the transcript are fixed before matching (`backend/voice/stt.ts`, `backend/care_paths/domain/glossary.ts`). Key terms cost 20% more per transcription, counted in the usage rows.
- **Language by language, based on measured quality.** We checked ElevenLabs' published coverage before building. Scribe is rated excellent for Finnish, English, Swedish, Russian, Estonian, Ukrainian and Vietnamese, high for Persian, Mandarin and Cantonese, good for Arabic and Thai, but only moderate for Somali (25–50% word error rate) (`brain/sources/2026-11-13-elevenlabs-language-coverage.md`, `backend/voice/capabilities.ts`). So:
  - Every language except Somali: voice in and voice out.
  - Somali: audio out only. Voice input is refused on purpose, and Somali speakers use the cards.
- **Human recordings win.** In the admin, a native speaker's recording can be uploaded for any text. Once approved it replaces the generated clip. Generated Somali audio can never be marked approved; only a human recording can (`backend/voice/admin.ts`).
- **A phone line for people without the app.** The caller presses a number or just says their language (a keypad menu in ten languages, each line spoken in its own language). An ElevenLabs agent with Gemini as its brain then talks with the caller in that language and calls two live Silta endpoints as tools: compose the care path, and look up the doors, hours and interpreter rules in the caller's area. It reads the Finnish sentence slowly so the caller can repeat it to the health station. Voice recording is off. Simulated callers passed end to end against the deployed API in Russian, Arabic (chosen by keypad) and Ukrainian (chosen by voice); a real call from a Finnish mobile reached the agent, the keypad press switched it to Finnish, and the voice started about 1.6 s after the caller stopped speaking (`scripts/phone_agent.py`, `docs/proof/2026-11-14/phone-agent.md`).
- **Spend under control.** Every call writes a usage row with characters, seconds and cost. A spend cap stops new calls; stored audio keeps playing (`backend/voice/providers.config.ts`). After the overnight build, the usage page showed about $0.016 of ElevenLabs spend in the development database (`brain/notes/2026-11-14-0735-silta-app-walkthrough.md`).

## Architecture

- Resident taps play → `GET /api/voice/clip` → stored clip if one exists for this exact text, otherwise ElevenLabs text-to-speech once → stored in PostgreSQL → served with long cache headers.
- Resident taps the microphone → `POST /api/voice/transcribe` → ElevenLabs Scribe → transcript → `POST /api/cards/match` → read-back question → the person confirms.
- Admin → upload a human recording → listen → approve → residents now hear the human voice.

| Language | Voice input | Audio output | Generated audio starts as |
| --- | --- | --- | --- |
| English, Finnish | yes | yes | approved |
| Swedish, Russian, Estonian, Ukrainian, Arabic, Persian, Mandarin, Cantonese, Vietnamese, Thai | yes | yes | unchecked |
| Somali | no, cards instead | yes | unchecked, never approvable |

## What is live vs planned

Live (local app and tests):
- Text-to-speech in all 13 languages, one real round trip per language, with caching (`docs/proof/2026-11-14/voice.md`).
- Speech-to-text for English and Finnish with real calls; the Somali request is refused as designed (same file). One live English call with the glossary key terms on `scribe_v3` returned "Kela card" (local backend, 14 Nov); whether the key terms improve accuracy on real speech is not yet measured.
- Spoken input through to the read-back in the browser tests, using a test clip made with ElevenLabs text-to-speech (`frontend/e2e/`, `brain/notes/2026-11-14-0735-silta-app-walkthrough.md`).
- Admin upload, approval and the rule that an approved human recording wins.

Planned or not yet done:
- Running on the deployed app; today this runs locally.
- Audio for texts built from several pieces (the door title with the place, time limits, the code line).
- Audio for the body figure's question and body-part buttons; today only the picture cards under it play aloud.
- Native-speaker review of the texts and audio in the 11 placeholder languages (all but English and Finnish; the nine added languages are machine-translated), and human Somali recordings. Speech-to-text has not yet been tried for real in the nine added languages. Nobody has yet listened to the generated clips to check pronunciation.
- Kurdish, which ElevenLabs does not offer as voice output (`brain/sources/2026-11-13-elevenlabs-language-coverage.md`); planned cards-first with human recordings.
- Zero-retention processing. It is enterprise-only, so ElevenLabs may keep request logs (`backend/voice/README.md`).

## What the challenge asks

- Give the hack a voice with ElevenLabs: natural, human-sounding, expressive AI audio.
- The organiser's text asks for "fully autonomous audio experiences" in the project, from voice apps to narration.
- Prize: wireless earbuds, one overall winner (`brain/challenges/tech/mlh-elevenlabs.md`).

## Why it matters for the people we serve

Reading aloud lets someone with little Finnish, or limited reading skills in any language, follow every step in their own language. Speaking an answer is easier than typing it on a phone in a second language. We only offer voice input where it works well enough. Recordings and transcripts are never stored, and every spoken answer is read back for the person to confirm.
