---
title: Silta master narrative for Junction 2026
description: The screening equity story, evidence, live demo, partner proof and proposed Helsinki pilot behind Silta’s video and pitch.
tags: [pitch, video, screening, evidence]
author: Silta team
updated: 2026-11-14
---

# Silta master narrative for Junction 2026

## The story in one minute

> In Finland’s 2024 cervical screening programme, 76 in 100 invitees whose native language was Finnish, Swedish or Sámi attended. Among the remaining invitees, 56 in 100 attended. Breast and bowel screening show gaps of roughly the same size.
>
> Amina, a Somali-speaking Muslim woman in Helsinki, has a screening appointment printed on her letter. She wants to go. She’s unsure what the exam involves, whether she can ask for a woman to take the sample, and how to ask for an interpreter or change the time.
>
> With Silta, she can open a picture guide on her phone, listen in Somali, and hear the Finnish words she needs to ask those questions. She can start today with an existing invitation and the public app. The screening provider can then add one link to its invitations and measure whether more people complete screening.

**The ask.** We’re looking for a Helsinki screening partner and a community organisation to test Silta on one cervical screening invitation batch. Review the Somali guidance with residents and screening staff, add a link to the existing invitation, and compare completed screens per 100 invitees with a comparable batch using the existing invitation alone.

[Finnish Cancer Registry screening statistics][registry] · [City of Helsinki screening process][helsinki] · [Example invitation][letter] · [Somali guide][somali-guide]

## Where the screening gap opens

| Programme | Finnish, Swedish or Sámi | Other or missing native language | Gap |
| --- | ---: | ---: | ---: |
| **Cervical** | **76.2%** | **56.3%** | **19.9 percentage points** |
| Breast | 83.2% | 60.8% | 22.4 percentage points |
| Colorectal | 74.5% | 53.4% | 21.1 percentage points |

The denominator is invitees in each national programme in 2024. The registry reports one combined rate for people whose native language is outside the first group and people whose native language is missing from the data. For cervical screening, that group included 34,391 invitees, of whom 19,374 attended. Applying the first group’s attendance rate to that group gives a benchmark of about **6,800 additional cervical screens** in 2024. That is the scale of the disparity under equal attendance. The cervical gap widened from 15.6 percentage points in 2020 to 19.9 in 2024, and the preliminary 2025 figures put it at 19.7. [Cervical annual tables][cervical] · [Breast annual tables][breast] · [Colorectal annual tables][colorectal] · [Preliminary cervical figures for 2025][prelim]

The biggest measured cervical gap is **between invitation and screening**. Among those referred for colposcopy in 2024, 84.8% and 87.1% attended in the respective groups. Bowel screening gives us a second place to act. Among residents with a positive stool test in 2024, 67.8% attended colonoscopy in Helsinki, compared with 72.7% nationally and 81.8% in South Ostrobothnia. Those are area-wide figures across all language groups. They make the follow-up step visible and give each area a place to start investigating. [Cervical annual tables][cervical] · [Colorectal annual tables][colorectal]

## Amina’s decision

Amina is a fictional composite. Show her noticing that the appointment clashes with a shift, finding the time on the letter, and tapping to hear what happens during the exam. She wants privacy and feels embarrassed about asking for a woman to take the sample. She plays the Finnish phrase so she can ask, then finds the official number to change the appointment. End with her taking that next step. The change we can show is that she now knows whom to contact and what to say.

A Finnish register study of organised cervical screening in 2008–2012 found age-adjusted participation of **19% among Somali-origin women and 67% in the Finnish comparison group**. Use this in the deck notes or Q&A, with the study years on screen if it appears. It measures country of origin in the study population. An Oslo interview study describes how embarrassment, language and concerns around intimate examinations can affect some Somali and Pakistani women. Keep those concerns personal to Amina. [Finnish register study][idehen] · [Oslo interview study][oslo] · [Helsinki booking guidance][helsinki]

**A second screening case for Q&A.** Mikael, a fictional Russian-speaking resident, receives a positive stool-test result and wants to know what a colonoscopy is and whom to call. Use him to explain the proposed follow-up pilot and show the registry’s regional comparison. For the symptom route, reserve a short product shot of the body map and Finnish call script. The cervical screening journey carries the main story.

## What the judges can see working

1. **Use the invitation.** Photograph the team’s fictional Finnish invitation and show Gemini’s explanation with the date, place and phone in distinct fields. The resident can also go straight to the Somali guide. A QR code in an official invitation is a proposed distribution channel. [Letter feature and proof][gemini] · [Example Finnish invitation][letter] · [Somali guide][somali-guide]
2. **Make the appointment usable.** Open the guide’s visit and rights sections. Show a picture, play one line, and reveal the Finnish phrase for asking for an interpreter or a female sample-taker. The guide points to HUS appointment options. Silta’s public guide opens without a download, account or bank ID. Use a native-speaker-checked Somali line for filming. The app’s Somali audio workflow accepts approved human recordings, and Somali answers use taps. [Screening feature][screening-code] · [Voice proof][voice-proof] · [Helsinki booking guidance][helsinki]
3. **Prove the handoff separately.** Use a prepared demo visit code to open the Finnish clinic view. Show the interpreter line, then send one next-step card to the resident view. This handoff runs in the navigation journey. Staff can open it in a browser. [Clinic view][clinic] · [Clinician feature][clinic-code]
4. **Put the evidence beside the build.** Open the Helsinki county view for public figures and counts of Silta activity by language and stage. Then show the structured service-path API. We mapped Helsinki, Länsi-Uusimaa, Kymenlaakso, Etelä-Pohjanmaa and Pohjois-Pohjanmaa in reusable data. It records contact points by access route, pathway steps, screening programmes, measured waits and bottlenecks with sources. Published facts require a source and verification date. [County view][county] · [Service-path API][paths-live] · [Service-path schema and seeds][paths-code]

The documented build includes a deployed resident app and API, a working clinic handoff, content versioning and rollback, and live provider tests. The team recorded a real end-to-end phone call. In the core story, show the guide on a phone, then let the working handoff and service-path data substantiate the build. Use a capture of the same flow for the video and as a stage backup. [App][app] · [API health][health] · [Deployment proof][aiven] · [Phone proof][phone-proof]

## How the safeguards work

| What to show | What we can say |
| --- | --- |
| The machine-generated label and a check against the original invitation | The letter tool explains a photo and surfaces logistics. Silta sends the image to its AI provider during the request and keeps the photo and answer out of its own storage and logs. Use the fictional letter on camera. |
| Card confirmation, a choice of cards when the model is unsure, and the emergency link | In the web flow, Gemini proposes a predefined card and the resident confirms it. Published rules select the route. Clinicians retain clinical decisions. The separate phone agent uses the model to select a route before calling Silta’s API. Its documented provider configuration disables call recording and keeps transcripts for seven days. Review the intended use of both flows before a pilot, including medical-device software qualification and AI disclosures. |
| A demo visit code and the interpreter line | Silta stores a keyed hash of the code with selected journey events. The code expires after 90 days and can be used to delete the visit. Treat the code as sensitive because possession gives access. The interpreter line helps staff arrange professional interpretation under the provider’s process. |
| Published content and the county view | Aiven hosts the app and database in the EU. Before handling resident data in a pilot, agree controller and processor roles, provider terms and transfers, the legal basis for health data, and disclosure controls for small counts. Review the need for a DPIA and have native speakers check pilot content and audio. |

[Letter processing][letters-code] · [Visit storage and access][visits-code] · [Phone provider configuration][phone-proof] · [MDCG software guidance][mdcg] · [GDPR][gdpr] · [EU AI Act][ai-act] · [Finnish Patient Act §§3 and 5][patient-act]

## What a wellbeing services area can adopt

Residents can use the public guidance today. The existing invitation, booking service, and care pathway are enough for that starting point. No area IT integration, list of residents or staff rollout is needed. Community groups can share the existing guide. The immediate value is a resident who can find the appointment information and prepare a question before contacting staff.

| Increment | Who does what | What it adds and how to measure it |
| --- | --- | --- |
| **Add the guide to one invitation batch** | The screening programme and its invitation provider add a short link or QR code after local language review. | Put practical help where invitees first encounter the appointment. Compare completed screens per 100 invitees and participation by language. Use opens and guide completion to understand reach. |
| **Try the visit code at one clinic** | Staff open a resident-shared code in a browser after agreeing how it will be handled. | Make the interpreter need and resident’s account visible at the start of the visit. Track codes opened, interpreter arrangements made before the visit where applicable, and staff-reported preparation time. |
| **Test HPV self-sampling when appropriate** | An authorised screening partner offers a kit at an existing visit to eligible residents under its protocol, with follow-up for positive results. | Add a more private option for people overdue for screening. Track offers, completed screens, positive-result follow-up and incremental cost per extra completed screen. This is a proposed pilot workflow. |
| **Support bowel screening follow-up** | A screening provider adds an approved explainer and contact route to positive-result communications. | Help residents understand the next step. Track colonoscopy completion and time from positive test to procedure, including regional differences. |
| **Integrate after showing value** | The area owns local content and, when ready, connects eligibility or referral events through approved systems. | Trigger help when people are due or waiting and check whether they complete the next step. Measure the added lift against the simpler rollout. |

**Why test these steps?** A Norwegian randomised trial found similar **breast screening** attendance with a bilingual invitation and the standard letter (46.5% versus 47.4%). Our pilot pairs information in the resident’s language with booking instructions and phrases they can use. A 2025 UK trial reported cervical self-sample returns of 5.6% in GP practices offering kits during visits versus 1.9% in the comparison group without that visit-based offer, in the study’s primary analysis. Fimlab is studying home HPV self-sampling in five Finnish areas in 2026. These results justify testing the interventions locally. Silta’s effect on completed screens and cost per extra screen is a pilot outcome. [Norway invitation trial][norway] · [UK cervical self-sampling trial][uk] · [Fimlab study][fimlab]

For scale, a five-percentage-point lift would mean 50 extra completed screens per 1,000 invitees. Use that as an illustrative scenario when discussing the pilot budget. The screening partner can divide added launch and operating costs by the extra completed screens estimated against the comparison batch.

## AstraZeneca and the technology challenges

**AstraZeneca’s Equal Care Across Finland.** The entry identifies the gap, locates it at screening attendance, and gives a screening provider a first intervention it can measure. Make the pilot ask explicit for **actionability (30%)**, show where the gap emerges for **insight (25%)**, show register denominators and study years for **data quality (20%)**, run the actual app for **execution (15%)**, and return to Amina’s decision for **clarity (10%)**. [Captured AstraZeneca brief][az]

**National Cancer Strategy.** Language parity in participation is sub-objective 1.3. Goal 2 targets 80% participation for each programme in each area. For the challenge’s **Goal 3** requirement, put national cancer mortality on the evidence slide. The strategy targets a 10% reduction. The Cancer Registry recorded 13,490 cancer deaths in Finland in 2024. The colorectal example shows a diagnostic step an area can act on and monitor through completion and wait time. Those measures are upstream of Goal 3’s treatment-timing and mortality outcomes. [National Cancer Strategy, goals and indicators][strategy] · [Cancer Registry 2024 cancer statistics][mortality] · [Colorectal annual tables][colorectal]

| Partner and challenge | What to say | What to show |
| --- | --- | --- |
| **Google DeepMind · Best Use of Gemini API** | Gemini reads a Finnish letter photo and returns a structured explanation in the resident’s language. It can also match free-form input to a known choice, with a confirmation or a fallback to cards. The checked-in app routes these two features through OpenRouter. Separate smoke tests exercise the direct Gemini API adapter. Show that direct integration for the partner brief. | Camera → labelled explanation → cervical guide. Show confirm versus fallback in the partner cut. Use the team’s fictional invitation, which is the documented Somali and Arabic photo-demo input. [Brief][gemini-brief] · [Implementation and proof][gemini] · [Provider configuration][llm-code] |
| **MLH · Best Use of ElevenLabs** | Voice makes the guide usable for people who read with difficulty. ElevenLabs powers read-aloud in 14 languages, speech input in 13, and a phone agent that calls the running Silta API. Somali uses taps for answers. | Play a guide line. For the autonomous audio experience, capture a fresh demo call using fictional details. The team already completed a real call with an English-speaking tester. TTS round trips covered all 14 languages. The documented real transcription tests were in Finnish and English. [Brief][eleven-brief] · [Voice proof][voice-proof] · [Phone proof][phone-proof] |
| **Aiven · Best Use of Aiven** | Aiven Runtime hosts the app and API. Aiven for PostgreSQL stores versioned guidance, audio, visit events and area data. A shared database makes the browser-to-clinic handoff possible and lets the team manage content without redeploying the app. | Open the same demo visit on two screens, show the API health check and show publish or rollback in the admin demonstration. This demonstrates meaningful use, implementation and impact on the overall solution. [Brief][aiven-brief] · [Implementation and proof][aiven] |

## How the video and deck inherit the story

| Beat | Video brief, up to 2 minutes | Deck or live pitch, up to 3 minutes |
| --- | --- | --- |
| **Locate the gap** | 0:00–0:14. Put 76.2% and 56.3% on screen with the year and the two population labels. Cut from the gap to the date on the invitation. | 0:00–0:25. Show all three programmes. Highlight invitation → attendance. |
| **Give Amina a decision** | 0:14–0:36. She discovers the appointment clashes with her shift. Let her ask what will happen and whom she can call. Label the scene as a fictional composite. | 0:25–0:50. Show the invitation and explain why the first step is hard for her. |
| **Show the working product** | 0:36–1:15. Real screen capture of the photo explanation, guide and spoken phrase. Close the scene on her next action. Briefly show the clinic view and put partner names on the features they enable. | 0:50–1:55. Run the invitation demo. Open the prepared visit code to prove the clinic handoff. Keep the symptom route to one sentence or an optional screen. |
| **Show safeguards and area data** | 1:15–1:35. Show the AI label, then one cut to the county view or sourced map. | 1:55–2:30. Show the safeguards, five-area data and Goal 3 evidence. Name each partner where its technology appears. |
| **Ask for one pilot** | 1:35–1:55. End with a Helsinki invitation batch and one measure, completed screens per 100 invitees. Leave five seconds for a source and demo card. | 2:30–3:00. Describe what residents can do today, what the partner adds, and how we’ll measure it. Leave the remaining adoption steps for Q&A. |

The video’s final human image is Amina ready to make the call. The final live slide can carry the team’s ask in one sentence. **“Help us put Silta on one cervical screening invitation batch and measure how many more people complete screening.”** [Junction judging and timings][judging]

[registry]: https://cancerregister.fi/statistics/screening-statistics/
[cervical]: https://stats.cancerregistry.fi/joukkistilastot/livmoderhals.html
[breast]: https://stats.cancerregistry.fi/joukkistilastot/breast.html
[colorectal]: https://stats.cancerregistry.fi/joukkistilastot/colorectal.html
[prelim]: https://stats.cancerregistry.fi/joukkistilastot/ennakkotilastot/cervix_preliminary.html
[helsinki]: https://www.hel.fi/en/health-and-social-services/health-care/other-health-care-services/cervical-cancer-screening
[idehen]: https://pubmed.ncbi.nlm.nih.gov/33126544/
[oslo]: https://pmc.ncbi.nlm.nih.gov/articles/PMC5505544/
[norway]: https://portal.research.lu.se/en/publications/effect-of-invitation-letter-in-language-of-origin-on-screening-at/
[uk]: https://doi.org/10.1016/j.eclinm.2025.103357
[fimlab]: https://fimlab.fi/wp-content/uploads/2026/01/HPV-omanaytteenotto_2026.pdf
[strategy]: https://fican.fi/wp-content/uploads/2026/01/National_Cancer_Strategy_2026-2035_Finland.pdf
[mortality]: https://cancerregister.fi/rapporter-och-publikationer/statistikrapport-om-cancerfall/
[mdcg]: https://health.ec.europa.eu/latest-updates/update-mdcg-2019-11-rev1-qualification-and-classification-software-regulation-eu-2017745-and-2025-06-17_en
[gdpr]: https://eur-lex.europa.eu/eli/reg/2016/679/oj
[ai-act]: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
[patient-act]: https://www.finlex.fi/en/legislation/1992/785
[judging]: https://github.com/madviking/junction2026/blob/main/event/rules-and-judging.md
[az]: https://github.com/madviking/junction2026/blob/main/challenges/main/astrazeneca-equal-care-across-finland.md
[gemini-brief]: https://hackjunction.app/participate/45/tech-challenges/48
[eleven-brief]: https://hackjunction.app/participate/45/tech-challenges/50
[aiven-brief]: https://hackjunction.app/participate/45/tech-challenges/43
[gemini]: /tech/gemini
[aiven]: /tech/aiven
[app]: https://fond-useful-corgi.eur-1.aiven.app/
[letter]: https://fond-useful-corgi.eur-1.aiven.app/letter/cervical/fi
[somali-guide]: https://fond-useful-corgi.eur-1.aiven.app/r/so/learn/cervical
[clinic]: https://fond-useful-corgi.eur-1.aiven.app/clinic
[county]: https://fond-useful-corgi.eur-1.aiven.app/county/helsinki
[health]: https://easily-smart-aphid.eur-1.aiven.app/api/health
[paths-live]: https://easily-smart-aphid.eur-1.aiven.app/api/service-paths/areas
[screening-code]: https://github.com/madviking/junction2026tech/tree/main/frontend/src/features/screening
[clinic-code]: https://github.com/madviking/junction2026tech/tree/main/frontend/src/features/clinician
[paths-code]: https://github.com/madviking/junction2026tech/tree/main/backend/service_paths
[letters-code]: https://github.com/madviking/junction2026tech/tree/main/backend/letters
[visits-code]: https://github.com/madviking/junction2026tech/tree/main/backend/visits
[llm-code]: https://github.com/madviking/junction2026tech/blob/main/backend/llm/integrations.ts
[phone-proof]: https://github.com/madviking/junction2026tech/blob/main/docs/proof/2026-11-14/phone-agent.md
[voice-proof]: https://github.com/madviking/junction2026tech/blob/main/docs/proof/2026-11-14/voice.md
