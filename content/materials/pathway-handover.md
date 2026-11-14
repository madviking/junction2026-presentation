---
title: Pathway page — handover for a new chat
description: State of the /pathway data page and the routes-into-care mock-up, decisions made, data rules and next steps. Paste or point a new Claude chat at this file.
tags: [pathway, handover, data, mockup]
author: Claude, for the Silta team
updated: 2026-11-14
---

# Pathway page: handover

Paste this file into a new chat (or say "read `content/materials/pathway-handover.md`") to continue.

## Goal

One data page for judges, showing where in the cancer care pathway people whose native language is not Finnish, Swedish or Sámi drop out. For each step it shows the evidence and what Silta and the county do about it. The judging criteria in focus are **Insight (25%)** and **Data quality & transparency (20%)**. Cost estimates come later.

## Where things are

| What | Path / URL | State |
| --- | --- | --- |
| Live data page | `/pathway` — `app/templates/pathway.html`, `_pathway.html`, `app/static/pathway.js`, data `content/data/pathway.json` | Timeline version, committed and merged (`d785ca4`), **not pushed** |
| Old report page | `/pathway/archive` — `content/dashboard_archive.yaml`; `/dashboard` redirects to `/pathway` | Kept for reference |
| Charts | `app/charts/*.py`; shown on a step via its `charts` list in `pathway.json` | `screening_by_language`, `gap_trend` on "Attends"; `digital_clinic_use` (teammate) and `symptom_to_treatment` on symptom step B |
| **New direction (mock-up)** | `content/materials/routes-into-care.html` = https://claude.ai/artifact/8bFR7XtQhwcEvXsNX4bmy1 (private) | Version 1, awaiting feedback |
| Earlier mock-up | `content/materials/pathway-timeline.html` = https://claude.ai/artifact/NfPLegAC3ENt1iewKgvazM | Superseded |
| Sources (brain repo `../junction2026`) | `sources/2026-11-14-cancerregistry-screening-by-language.md`, `…-europepmc-unmet-need-and-access-by-origin.md`, `…-espoo-equity-talk-kuitunen.md` (**uncommitted**), `…-aalto-digital-clinic-users-register-study.md`, PDF `sources/data/Equility in Cancer Care_Espoo 13.11.26_distribution.pdf` | |

## Feedback from the user on the current /pathway (to fix in the rebuild)

- Too many colours, too much text, too busy, not clear.
- Data only exists for the first few steps. Make that the point (we measure the door, then go blind), not a weakness.
- Don't copy charts from slides. Use the information instead (the symptom-route fork, below). The `symptom_to_treatment` chart now on `/pathway` should go in the rebuild.
- **Don't report differences that are not statistically significant.**
- Combine breast, cervical and colorectal into one view; show per-programme numbers on click.
- Show the different **routes in**: screening letter, symptom, doctor's suggestion.
- Headline info above the timeline is wanted, but avoid the clunkiness of detail panels changing above the map.
- Light theme only. Mobile not needed.

## The mock-up (routes-into-care) — what it does

- Headline: "Three ways in, and we can only see one".
- Three numbers on top: **−21 pp** attendance (2024, all programmes), **+84 days** to treatment via a public health centre (one lymphoma study), **3 of 11** steps measured by native language.
- Route map (SVG): screening letter → attends → follow-up; symptom → first contact → fork (public health centre / private or occupational) → doctor visit, referral; doctor's suggestion (visit for something else → test ordered). All three merge at the diagnostic exam, then treatment. A Silta band sits at the start of all routes.
- Two colours: ink for structure, coral only for gaps. Line style shows evidence: solid = by native language, dotted = another way (origin, care sector, county), dashed grey = not measured.
- Clicking a step shows a heading, 1–2 sentences, a small table, what Silta does and what the county can do, and the source.

## Numbers in use (all significant or a registry count)

- Attendance 2024, Finnish/Swedish/Sámi vs other language: breast 83.2 / 60.8 (−22.4), cervical 76.2 / 56.3 (−19.9), colorectal 74.5 / 53.4 (−21.1). Pooled from invitee counts: 77.8 / 57.0 (−20.8). Invited: 979,412 vs 78,914.
- Colonoscopy after a positive stool test, pooled 2022–24: 77.1 / 68.3 (−8.8, 95% CI 6.3–11.3).
- Missed a colorectal round: ~18% return, against 91–93% of previous attenders.
- Kuitunen et al., Cancer Medicine 2026;15:e71920 (lymphoma, 160 patients, 2014–2020, grouped by first provider, **not language**). Days from onset, private/occupational vs public: doctor 43 vs 94, referral 77 vs 147, treatment 123 vs 207.
- Maamu (THL 2010–12): 95% of Somali-origin women last saw a doctor at a municipal health centre, against ~20% of the general population. Unmet need: Somali 5.5%, Russian 15.2%, Kurdish 28.8%, vs 1.5% overall.

**Left out by the significance rule:**

- Cervical colposcopy +2.3 (not significant).
- Helsinki waiting times (county medians, never tested by language).
- Digital-clinic contacts 0.12 vs 0.20 (descriptive, no tests). Ask the user whether it goes back in.

## Next steps

1. Get the user's feedback on the routes-into-care mock-up and iterate.
2. Once approved, rebuild `/pathway` from it. Restructure `pathway.json` into routes with combined programmes; drop `symptom_to_treatment` (and its CSV) unless the user wants to keep it; update tests (`tests/test_site.py`), `AGENTS.md` and `content/data/README.md`.
3. Later: step 0 "before the letter" (outreach: community groups, migration and health services, AI-assistant answers); cost estimates (THL unit costs 2023–24); an emergency-presentation route only if a Finnish source is found.

## Rules (from AGENTS.md)

- Commit, push and branch only with the user's explicit approval for that exact action. A push to `main` redeploys the live site.
- Every number traces to a source file in the brain repo; keep wording as careful as the source.
- Run `make test` (40 pass now). Local site: `make dev` on port 8400 (a dev server was also running on 8401).
