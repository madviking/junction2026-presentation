---
title: Best Use of ElevenLabs
partner: ElevenLabs
organiser: MLH
logo: /media/logos/mlh.png
logo_alt: MLH logo
summary: ElevenLabs reads Silta aloud in 14 languages, listens where speech recognition is good enough, and answers the phone line in the caller's language.
order: 20
criteria_source: brain/challenges/tech/mlh-elevenlabs.md
# Glance: rendered as visuals at the top of the page (see AGENTS.md, Tech-partner pages).
fit:
  steps:
    language: On the phone, press a key or say your language
    describe: Picture cards read aloud; spoken answers become text
    route: Route cards read aloud
    visit: Visit-card next steps read aloud
    after: Outcome cards read aloud
    admin: A native speaker's recording replaces generated audio
numbers:
- value: '14'
  label: 'languages read aloud, from Finnish and Swedish to Russian, Arabic, Somali, Persian, Chinese, Cantonese, Vietnamese, Thai and Bulgarian'
- value: '13'
  label: languages built for voice input; Somali answers by cards on purpose
- value: 1×
  label: each clip generated once and cached; an edited text never plays old audio
live:
- Phone line on a real number; an agent answers in the caller's language
- Text-to-speech in all 14 languages, cached, one real clip per language
- Speech-to-text with read-back, biased towards Finnish health care words
- Admin upload and approval of human recordings
screenshots:
- src: /media/screens/slider-02-body-map.png
  alt: "'What worries you?' with a body figure and big picture cards, each with a speaker button."
  caption: For people who read little, every picture card has a speaker button that plays ElevenLabs audio.
- src: /media/screens/slider-04-route.png
  alt: "'Where do you get health care?' with a speaker button on each route card and a microphone button next to the text box."
  caption: Every card plays aloud. The microphone sends a spoken answer to ElevenLabs Scribe.
- src: /media/screens/slider-05-door.png
  alt: "The call script: each Finnish sentence and its meaning, each with its own speaker button."
  caption: The sentence to say on the phone. One button plays the Finnish, the other its meaning.
- src: /media/screens/slider-06-body-map-ar.png
  alt: "The same picture symptom screen in Arabic, right to left, with speaker buttons."
  caption: The same cards in Arabic. Generated Arabic audio stays unchecked until a native speaker reviews it.
---
## How Silta uses ElevenLabs

Many people Silta is for read Finnish poorly, and some read their own language poorly too. So every line in the resident app has a play button, and residents can answer by speaking. The backend module `backend/voice/` is the only place that calls ElevenLabs.

- **Text-to-speech for every card and instruction.** Symptom cards, route cards, outcome cards and visit-card next steps play aloud in 14 languages: English, Finnish, Swedish, Russian, Estonian, Ukrainian, Arabic, Somali, Persian, Mandarin, Cantonese, Vietnamese, Thai and Bulgarian. One model (`eleven_v4`) and one multilingual voice cover them all (`backend/voice/capabilities.ts`). The symptom step opens in a picture version for people who read little: a body figure to tap where it is, and big picture cards, each with the same play button (`frontend/src/features/journey/components/SymptomBodyPicker.tsx`).
- **Generated once, then cached.** A clip is made the first time a text is played, stored in the database and keyed by a hash of the exact text. When an admin edits a text, the old clip is never played again (`backend/voice/service.ts`, `backend/voice/README.md`).
- **Speech-to-text for answers.** A resident taps "Tap to speak", says what they noticed ("I found a lump in my breast"), and ElevenLabs Scribe turns it into text. The text goes through the same read-back as typed text: Silta asks "Did you mean: a new lump or swelling?" and nothing is chosen until the person taps Yes (`backend/voice/stt.ts`, `frontend/src/features/voice/`).
- **Finnish health care words.** Every transcription sends Scribe our glossary as key terms (Kela-kortti, terveysasema, lähete, OmaKanta …, in Finnish and the person's language), so "Kela card" is not written as "Kellogg card". Known mishearings left in the transcript are fixed before matching (`backend/voice/stt.ts`, `backend/care_paths/domain/glossary.ts`). Key terms cost 20% more per transcription, counted in the usage rows.
- **Language by language, based on measured quality.** We checked ElevenLabs' published coverage before building. Scribe is rated excellent for Finnish, English, Swedish, Russian, Estonian, Ukrainian, Vietnamese and Bulgarian, high for Persian, Mandarin and Cantonese, good for Arabic and Thai, but only moderate for Somali (25–50% word error rate) (`brain/sources/2026-11-13-elevenlabs-language-coverage.md`, `backend/voice/capabilities.ts`). So:
  - Every language except Somali: voice in and voice out.
  - Somali: audio out only. Voice input is refused on purpose, and Somali speakers use the cards.
- **Human recordings win.** In the admin, a native speaker's recording can be uploaded for any text. Once approved it replaces the generated clip. Generated Somali audio can never be marked approved; only a human recording can (`backend/voice/admin.ts`).
- **A phone line for people without the app.** The greeting first says the caller can just say their language or wait for the menu; the keypad then reaches all 14 languages (nine direct, five more behind 0), each line spoken in its own language. An ElevenLabs agent with Gemini as its brain then talks with the caller in that language and calls two live Silta endpoints as tools: compose the care path, and look up the doors, hours and interpreter rules in the caller's area. It reads the Finnish sentence slowly so the caller can repeat it to the health station. Voice recording is off (`scripts/phone_agent.py`).
- **Spend under control.** Every ElevenLabs request writes a usage row with characters, seconds and cost. A spend cap stops new calls; stored audio keeps playing (`backend/voice/providers.config.ts`). After the overnight build, the usage page showed about $0.016 of ElevenLabs spend in the development database (`brain/notes/2026-11-14-0735-silta-app-walkthrough.md`).

## Architecture

- Resident taps play → `GET /api/voice/clip` → stored clip if one exists for this exact text, otherwise ElevenLabs text-to-speech once → stored in PostgreSQL → served with long cache headers.
- Resident taps the microphone → `POST /api/voice/transcribe` → ElevenLabs Scribe → transcript → `POST /api/cards/match` → read-back question → the person confirms.
- Admin → upload a human recording → listen → approve → residents now hear the human voice.

| Language | Voice input | Audio output | Generated audio starts as |
| --- | --- | --- | --- |
| English, Finnish | yes | yes | approved |
| Swedish, Russian, Estonian, Ukrainian, Arabic, Persian, Mandarin, Cantonese, Vietnamese, Thai, Bulgarian | yes | yes | unchecked |
| Somali | no, cards instead | yes | unchecked, never approvable |

## What is live

- The phone line, +1 878 425 5777. A real call on 14 Nov went the whole way: the caller pressed 3 for English, described irregular bowel movements, said they have no residence in Finland; the agent called `compose_care_path` on the deployed API, named the county necessary-care route or a volunteer clinic and the free interpreter, then answered a question about cost (108 s, ElevenLabs conversation `conv_2001m7d35dngfm4a2h32nbwwnfdx`). On another call a keypad press switched the agent to Finnish, and the voice started about 1.6 s after the caller stopped speaking. Simulated callers in Russian, Arabic (chosen by keypad), Ukrainian and Bulgarian (chosen by voice) passed end to end (`docs/proof/2026-11-14/phone-agent.md`).
- Text-to-speech in all 14 languages, one real round trip per language, with caching (`docs/proof/2026-11-14/voice.md`).
- Speech-to-text for English and Finnish with real API calls; the Somali request is refused as designed (same file). One live English call with the glossary key terms on `scribe_v3` returned "Kela card" (local backend, 14 Nov); whether the key terms improve accuracy on real speech is not yet measured.
- Spoken input through to the read-back in the browser tests, using a test clip made with ElevenLabs text-to-speech (`frontend/e2e/`, `brain/notes/2026-11-14-0735-silta-app-walkthrough.md`).
- Admin upload, approval and the rule that an approved human recording wins.

## Why it matters for the people we serve

Reading aloud lets someone with little Finnish, or limited reading skills in any language, follow every step in their own language. Speaking an answer is easier than typing it on a phone in a second language. We only offer voice input where it works well enough. Recordings and transcripts are never stored, and every spoken answer is read back for the person to confirm.
