---
title: Junction submission text
description: Name, punchline and description as entered on the Junction Platform, 15 Nov.
tags: [submission]
author: Claude
updated: 2026-11-15
---

**Punchline:** Equal cancer care for minorities in Finland starts before the first appointment. Silta guides people from a symptom or screening letter to the right service, in 14 languages, no login.

**Silta** (Finnish for "bridge") takes a person from a cancer symptom or a screening letter to the right service, and a visit both sides understand, in their own language and without logging in.

## The problem
Goal 3 of the National Cancer Strategy 2026–2035 asks for equal and effective cancer care. For people with another native language, the gap opens before the first contact, where no register looks:
- They attend breast, cervical and colorectal screening **20–22 percentage points less often** (Finnish Cancer Registry, 2024). Closing that gap would mean about **16,500 more people screened a year**.
- In lung cancer, over 50 of about 155 days pass before the first contact with care (UEF, reported by Yle MOT).

## What we built
A mobile web app, a phone line and a county view, live on Aiven:
- **14 languages, all read aloud**, including Arabic and Persian right to left, Somali, Cantonese and Thai. An Urgent help button (112 / 116117) is on every screen.
- **Describe what you noticed** with a tappable body map and picture cards, by typing, or by speaking. Free text and speech are matched to one card and read back ("Did you mean: a new lump or swelling?"). Nothing is chosen until the person taps Yes.
- **The right service** for their situation and area (county health station, student or occupational care, volunteer clinic for people without residence), with **the words to say in Finnish**, their meaning and audio.
- **A visit card** with a one-screen Finnish summary for the clinician, and what happens next, including when to call if nothing arrives.
- **Screening letters with a QR code** to a picture-and-audio guide in the resident's language (example letters in 14 languages).
- **A phone line** for people who do not read: +1 878 425 5777. Press a key or say your language; an agent finds the right service in your area.
- **County view**: anonymous counts by journey stage, outcome and language next to public county figures. Never a person.
- **Admin**: versioned texts per language, review status, human recordings that replace generated audio, spend and audit log. View-only demo login: demo@silta.test / silta-demo-viewer.

## Safe to use today
No names, ID numbers, phone numbers or emails are ever asked for or stored (GDPR Art. 9). Silta does not diagnose or rate urgency, so it stays outside EU MDR Rule 11 and works without a county contract. Next step: a pilot with a county (QR on screening letters, clinic summary, county view).

## Tech challenges
**Aiven — Best use of Aiven.** One Aiven for PostgreSQL database with pgvector (europe-west4) holds all content, versioned per language, read-aloud audio, anonymous visits (hashed codes, card ids only), county figures, cost and audit rows. The API and resident app run on Aiven Runtime in the same region. CI migrates Aiven and redeploys on every green push to main; /api/health checks the database and pgvector.

**ElevenLabs (MLH).** Text-to-speech for every card and instruction in 14 languages, generated once and cached by a hash of the exact text. Scribe speech-to-text with Finnish health-care key terms (Kela-kortti, terveysasema, lähete) and read-back; voice input is offered only where measured quality is good enough (Somali uses cards on purpose). The phone line is an ElevenLabs agent that calls live Silta endpoints as tools. Approved native-speaker recordings win over generated audio.

**Google DeepMind — Gemini API.** Gemini matches a resident's own words to exactly one card from a fixed set (symptoms, routes, outcomes) with a JSON schema, so Silta asks instead of guessing and the model makes no urgency decisions. Gemini 2.5 Flash is the brain of the phone agent, and Gemini reads a photo of a letter: what it is, the facts as printed and what to do, in the person's language. Identifiers are removed before text leaves the backend.

**Stack:** Encore.ts, React + Mantine, PostgreSQL + pgvector on Aiven, Gemini API, ElevenLabs.

## Links
- Project site (deck, data, video, all links): https://mostly-awaited-flounder.eur-1.aiven.app/
- Try it (app, letters, phone line, county view, admin): https://mostly-awaited-flounder.eur-1.aiven.app/try
- Resident app: https://fond-useful-corgi.eur-1.aiven.app/

Team: Timo Railo (product, architecture, pitch), Mea Railo (backend, data), Milla Railo (UX, design, video, data storytelling).
