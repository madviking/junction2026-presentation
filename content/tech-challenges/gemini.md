---
title: Best Use of Gemini API
partner: Google DeepMind
organiser: Google DeepMind
logo: /media/logos/google-deepmind.png
summary: Gemini Decision 1 matches what a resident types or says to one card from a fixed set, with probabilities, so Silta asks instead of guessing.
order: 30
criteria_source: brain/challenges/tech/google-deepmind-gemini-api.md
# Glance: rendered as visuals at the top of the page (see AGENTS.md, Tech-partner pages).
fit:
  steps:
    describe: Your own words → one symptom card, or the cards
    route: “I study at…” → the right route card
    after: “They gave me a time…” → the outcome card
numbers:
- value: '3'
  label: journey steps served by one Gemini Decision 1 call
- value: '0'
  label: urgency or emergency decisions left to the model
- value: 1 tap
  label: by the person before any match changes the journey
live:
- Card matching for symptoms, routes and outcomes (reached through OpenRouter today)
- Read-back when confident, the cards when unsure
- Identifiers removed before text leaves the backend
- Answer cards for 14 Finnish health care words (Kela card, lähete, OmaKanta …)
- Logged evaluation on synthetic English and Finnish input
- Photo of a letter → what it is, the facts as printed and what to do, in the person's language (Gemini 3.1 Flash-Lite, image + JSON schema; reached through OpenRouter today)
planned:
- Phone line: Gemini 2.5 Flash drives the ElevenLabs phone agent (simulated call passes)
- Switch card matching to the direct Gemini API adapter
- Generated answers from public Finnish health sources, with links
- Evaluation in real resident wording, incl. Somali and Arabic
screenshots:
- src: /media/screens/partner-gemini-symptom.png
  alt: "'I found a hard lump in my left breast last week' typed in; Silta asks 'Did you mean: A new lump or swelling?' with Yes and No."
  caption: “I found a hard lump in my left breast last week” → one card, asked back. Nothing is chosen until the person taps Yes.
- src: /media/screens/partner-gemini-route.png
  alt: "'I study at the University of Helsinki' typed in; Silta asks 'Did you mean: I am a university or college student?'"
  caption: The same call finds the route card. “I study at the University of Helsinki” → the student route.
- src: /media/screens/partner-gemini-question.png
  alt: "'They asked for my Kela card. I don't know what it is.' typed in; Silta shows a short reviewed answer to 'What is a Kela card?'"
  caption: A question gets a reviewed answer card, not a guess. The step's cards stay on screen.
---
## How Silta uses Gemini

**The problem.** A person who has found a lump does not think in our card names. They write "I found a hard lump in my left breast last week", "Löysin rinnasta kovan kyhmyn" or "I called three times and nobody picked up". Silta needs to turn that into one of a fixed set of cards, without inventing anything and without making a medical judgement.

**Why a chat model is the wrong tool.** A chat model answers in free text, sounds confident when it is not, and can drift into advice. For a health tool for language minorities that is a safety problem, not a style problem.

**What we use instead: Gemini Decision 1 through the Decisions API.** It is a closed-set classifier: we send the person's words and the list of cards, and it returns one choice plus a probability for every option (`backend/llm/gemini.ts`, `docs/planning/2026-11-14-provider-api-notes.md`). Silta uses those probabilities directly:

- **Confident and clearly ahead:** Silta reads the card back as a question, "Did you mean: a new lump or swelling?". Nothing is chosen until the person taps Yes.
- **Unsure, or two cards close together:** Silta shows the cards instead of guessing. Vague input such as "I just don't feel right" falls back to the cards.
- **A question, not an answer:** "They asked for my Kela card. I don't know what it is." Next to the step's cards, Gemini also sees one answer card per Finnish health care word and a "none of these" option. When the person asks what a word means, Silta shows a short reviewed answer that ends with the Finnish sentence to say, and the step's cards stay on screen. When the person only uses the word in a statement, the situation card still wins (`backend/care_paths/seed/glossary.yaml`, `backend/cards/prompts/match.ts`).
- The thresholds for these rules are in `backend/cards/config.ts`.

**Where it appears in the journey.** The same call serves three steps (`backend/cards/service.ts`):
1. Describe: free text or a voice transcript → a symptom card. The step opens with a body figure and picture cards for people who read little; the "Describe in your own words" box sits under them and makes the same call (`frontend/src/features/journey/components/SymptomPicker.tsx`).
2. Route: "I study at the University of Helsinki" → the right route card for the person's situation.
3. Outcomes: "they gave me a time for next Tuesday" → the outcome card that moves the journey on.

**Safety by design.**
- Gemini only ever picks a card. It never chooses the door, never sets urgency and never sees the emergency options. The emergency screen is the same for everyone and is never decided by the model (`backend/cards/README.md`).
- The options come only from the published, versioned content, in English and in the person's language.
- Before text leaves our backend, `backend/cards/redact.ts` removes visit codes, Finnish personal identity codes, emails, phone numbers, long numbers, self-introduced names and street addresses. The text is never logged or stored.

**One integration point.** All model calls go through one internal service, `backend/llm/`. Each feature names its provider and model in `backend/llm/integrations.ts`, every call writes a usage row with tokens and cost, and a spend cap refuses calls rather than faking an answer. The same service also wraps Gemini `generateContent` for text tasks.

## Architecture

| Step | Component | File |
| --- | --- | --- |
| Resident types or speaks | Free text, or a transcript from ElevenLabs Scribe | `frontend/src/features/journey/components/MatchInput.tsx` |
| Strip identifiers | Redaction | `backend/cards/redact.ts` |
| Build the options | Cards from the live content | `backend/cards/options.ts` |
| Classify | `llm.decide`, feature `cards.match`, Gemini Decision 1 | `backend/llm/service.ts`, `backend/llm/integrations.ts` |
| Decide what to show | Read-back or cards, by confidence and margin | `backend/cards/service.ts` |
| Person confirms | Only a tap changes the journey | `frontend/src/features/journey/` |

## What is live vs planned

Live (local app, tests and one logged evaluation):
- Card matching with Gemini Decision 1 in the running app, for symptoms, routes and outcomes, with the read-back and the fallback to cards (`brain/notes/2026-11-14-0735-silta-app-walkthrough.md`).
- A live evaluation on a labelled set of 48 synthetic English and Finnish inputs: every confident answer was correct, all 5 questions about health care words got the right answer card, and every vague or off-topic input fell back to the cards, for $0.005 (`docs/proof/2026-11-14/classifier-eval.md`). The set was written by the builder, so it shows the wiring and the guard rails, not an independent accuracy figure.
- The direct Gemini API adapter for both Decisions and `generateContent`, each proven with a live smoke call (`backend/llm/README.md`).
- "I got a letter": the person photographs a letter they cannot read; Gemini 3.1 Flash-Lite reads the photo and answers as one JSON object that follows our schema: a letter type from a closed set, the date, place and phone number copied as printed, and a short explanation with steps in the person's language (`backend/letters/`, `backend/llm/service.ts` `extract`). Checked in the running local app on 14 Nov with the app's own Finnish example invitation, in Somali and Arabic (`docs/proof/2026-11-14/letter-result-so.png`, `letter-result-ar.png`). This is generated text, so the screen labels it machine-made and tells the person to check date, time and place against the paper. The photo is sent once and never stored or logged; the model makes no urgency decision. Tried on one example letter only, not evaluated on real letters.

In progress or planned:
- In the current build the `cards.match` feature reaches Gemini Decision 1 through OpenRouter. Switching it to the direct Gemini API adapter is a one-line change of `provider` in `backend/llm/integrations.ts`; it has not been made yet.
- Building the knowledge base from public Finnish health sources (wellbeing services counties, Terveyskylä, THL, Cancer Society of Finland) into checked plain-language pages, with Gemini matching a question to the official source and showing it with a link.
- Help with translation drafts for native-speaker review.
- An evaluation set in real resident wording, including Somali and Arabic input.

## What the challenge asks

- A meaningful, innovative and technically impressive use of the Gemini API, going beyond "adding an LLM to an app".
- The submission should explain the problem, how Gemini is integrated, what makes the use innovative, and why Gemini is important to the solution.
- Prizes: €4,000 plus $1,000 Google Cloud credits per team member, €2,000 and €1,000 (`brain/challenges/tech/google-deepmind-gemini-api.md`).

## Why it matters for the people we serve

People who do not speak Finnish well can say what worries them in their own words and language, instead of finding the right Finnish term. Because Gemini Decision 1 gives probabilities rather than a confident sentence, Silta can admit when it is unsure and show the choices, and the person always has the last word. The model never decides how urgent something is; that stays with the nurse.
