---
title: Data dashboard — implementation plan
description: Plan for rebuilding /dashboard as an 8-block guided story on the discovery phase (Insight + Data quality criteria).
tags: [dashboard, data, plan, judging]
author: Mea + Claude
updated: 2026-11-14
---

# Data dashboard — implementation plan

**Goal:** a judge understands the gap, where it opens and who it hits in under two minutes.
Scope: screening only (no symptom route). Built on the data that exists; Somali is the case study, not the frame.
Scores mainly on **Insight (25%)** and **Data quality & transparency (20%)**, and hands over to Actionability.

## Design rules (less is more)

- **One column, one story.** Blocks stacked top to bottom in `container-xl silta-narrow` (880px). No grid of cards.
- **Every block has the same four parts:**
  1. a number tag + **headline that states the finding** ("The gap opens at the door", not "Pathway analysis");
  2. **one** chart *or* one big number — never two;
  3. **one line** on what it means;
  4. a collapsed **"Details and sources"** (`<details>`, same style as the existing `.silta-table`) with the caveats, CIs, method and the data table.
- **Two colours only:** `lake` = reference group (Finnish/Swedish/Sámi, born in Finland), `coral` = the group Silta serves. `reference` grey = "no gap / context". No new palette keys.
- Existing fonts, Tabler cards and `silta.css` tokens only. A few new classes, all prefixed `.silta-story-*`.
- Large text = the claim. Small `silta-src` mono text = source on every block, always visible.
- Plotly mode bar is hidden on story charts (`displayModeBar: false`); hover stays on.
- Wording is as careful as the source (AGENTS.md rule): "about", "proxy", "area-level", "scenario".

## The 8 blocks

| # | Headline (draft) | Visual | Details (collapsed) | Data |
| --- | --- | --- | --- | --- |
| 0 | **Finland screens most people well. Not everyone.** | Context strip: 3 small facts, then the key message and 3 tiles: −20 to −22 pp · gap widening · ~16,560 missed screenings/yr | Programme ages and intervals; strategy targets (Goal 2: 80% in every county; sub-goal 1.3: language parity) | Cancer Registry deaths/costs 2024; strategy PDF; screening JSON |
| 1 | **Same invitation, about 20 points fewer attend** | Existing `screening_by_language` grouped bars (2024) | n invited per group, 95% CIs, "other" includes unknown language | `screening_by_language.csv` (exists) |
| 2 | **The gap opens at the first step** | **New** `pathway_gap`: horizontal bars of the gap (pp) per step: attend → follow-up, per programme. Coral = significant gap, grey = no gap | Colorectal follow-up pooled 2022–24 −8.8 pp (CI 6.3–11.3); 2024 alone borderline; only ~18% of people who miss a round attend the next one; Helsinki colonoscopy wait 3.4 vs ~1.9 months | **New** `gap_by_step.csv` |
| 3 | **Who is missed, and why: deepest for people born in Africa, and not just education** | Existing `screening_by_birth_region` + one "why" line: *people born in Africa and the Middle East are the least satisfied with access to care: about a third of the general population's odds of contacting care smoothly (THL FinMonik)* | Education gap (63.5% / 50.8% for primary education); regression: language survives controls for breast + colorectal, cervical = unemployment; **self-reported barriers** (FinMonik 2018–19: odds of being satisfied with access 0.28–0.43× for Middle East/North Africa and rest of Africa; Maamu 2010–12: unmet need for a doctor's care Somali 5.5%, Russian 15.2%, Kurdish 28.8% vs 1.5% general population; language difficulties among the top barriers for the Russian and Kurdish groups; limits: ages 18–64, by origin not language, not screening-specific); **Somali case-study callout** (Helsinki #2 language, 16,115 speakers, 85% in Uusimaa, older study 19% cervical, unmet need 5.5% vs 1.5%, 95% of Somali-origin women see a municipal health-centre GP — so the health centre is the place to reach them; speech AI weak → cards-first) | birth-region CSV (exists); **new** `screening_by_education_2024.csv`; survey figures in text only (no chart); brain `sources/2026-11-14-europepmc-unmet-need-and-access-by-origin.md` |
| 4 | **It's growing** | **New** `gap_trend`: line of the gap (pp) per year, 3 programmes | Breast +2.5, cervical +4.2 pp (significant); colorectal flat; 2035 scenario ~31,500–38,600 missed/yr, 80% target slips from demographics alone (labelled scenario) | `screening_by_language.csv` (exists; add 2021/2023 rows if available) |
| 5 | **Half of the people affected live in three counties** | Existing `county_language_vs_breast` scatter | Ecological caveat (municipal r −0.25); Helsinki compound gap: 74.3% breast, 69.6% colorectal, 67.8% colonoscopy after +FIT — all lowest | county CSV (exists) |
| 6 | **Three strategy goals, three indicators counties already get** | HTML table, 3 rows: goal → indicator → what Silta moves | Indicator source per row | strategy PDF; registry |
| 7 | **Expected impact** — *placeholder* | "Being finalised" card, no numbers on screen yet | — | decided later; THL unit costs (2023–24 series) only if the metric involves cost |
| 8 | **How we know** | Compact table: claim · gap · 95% CI · verdict (✓ solid / ⚠ caution) | "What we don't claim" list; **"What isn't measured" list** (symptom-to-diagnosis not collected — strategy 2.5; stage missing for almost half in the lung quality report, 2019–23; no attendance by individual language, only "other/missing"); full source list with links | deep-analysis note §1; brain `sources/2026-11-14-web-research-barriers-and-data-gaps.md` |

Rows in block 6 (draft):

| Strategy goal | Indicator the county already gets | What Silta moves |
| --- | --- | --- |
| Sub-goal 1.3 — screening parity for non-Finnish/Swedish speakers | Cancer Registry attendance by native language | First-invitation attendance |
| Goal 2 — 80% participation in every programme in every county | Sotkanet 3620 / 3621 / 6103 | Attendance in high-minority counties |
| Goal 3 — treatment within target times | Registry: colonoscopy after +FIT, time to colonoscopy | Colorectal follow-through |

## Technical approach

Keep the existing architecture; add a story layer on top of it.

1. **`content/dashboard.yaml` (new)** — the story text, so wording can change without code changes: per block `id`, `n`, `headline`, `takeaway`, `chart` (chart module id or empty), `tiles` / `facts` / `rows` (optional), `details` (Markdown), `source`.
2. **`app/content.py`** — add `dashboard()` that loads the YAML and renders `details` Markdown (same `markdown` lib already used).
3. **`app/charts/__init__.py`** — add `by_id()` (a dict over `discover()`). Charts keep their `CHART` metadata and data table; the story uses the chart's figure and table, and the YAML's headline.
4. **`app/main.py`** — `/dashboard` passes `story=content.dashboard()` and `charts=charts.by_id()`. Chart modules not used in the YAML are not shown.
5. **`app/templates/dashboard.html`** — rewrite: page head → loop over blocks → `_story_block` macro (tag, headline, visual, takeaway, details, source). Keep the existing Plotly loader and theme redraw script unchanged.
6. **`app/static/silta.css`** — add `.silta-story-block`, `.silta-story-n`, `.silta-story-take`, `.silta-tile`, `.silta-callout` (coral left border for Somali). Check at 375px: no horizontal scroll.
7. **New chart modules:** `pathway_gap.py`, `gap_trend.py`. Same pattern as `screening_by_language.py`: `new_figure(p)`, palette keys only, hover template, data table.
8. **New data:** `gap_by_step.csv`, `screening_by_education_2024.csv`, each copied from `brain/sources/data/2026-11-14-screening-equity-by-language.json` and listed in `content/data/README.md`.
9. **`site.yaml` facts** stay as they are (the landing page uses them); the dashboard's own tiles live in `dashboard.yaml`.
10. **Tests** — update `/dashboard` expected text; add a test that every `chart:` in `dashboard.yaml` exists and every block has a `source`.

## Order of work

1. Data: build the two new CSVs from the brain JSON; re-check every number against the source note.
2. Skeleton: YAML + loader + template + CSS, using only the 3 existing charts → page renders end to end.
3. New charts: `pathway_gap` (most important, block 2), then `gap_trend`.
4. Text pass: headlines, one-line takeaways, details, sources; read-aloud test, under 2 minutes for headlines + takeaways only.
5. Checks: `make test`; light and dark; 375px mobile; every number traced to a brain source.

## Open decisions

- **Impact (block 7):** metric and method still open — placeholder until decided. If it involves cost, capture THL national unit costs (2023–24) first.
- **Self-reported barriers (block 3):** confirmed from two peer-reviewed papers (access satisfaction ORs; Maamu unmet need incl. Somali). Still unconfirmed: FinMonik report's own tables on communication with staff (Julkari down, HTTP 500) and whether MoniSuomi 2022 has newer equivalents. Not blocking — block 3 can be built with the confirmed figures.
- **Helsinki numbers:** the registry has no other-language split by county, so Helsinki figures would be estimates (labelled). In or out?
- **Page language:** English only (proposed; judges and AstraZeneca read English).
- **Block 0 vs deck:** dashboard keeps 3 context facts only; the fuller Finnish cancer-care context goes into the pitch deck.

## Sources (brain repo)

- `sources/2026-11-14-cancerregistry-screening-by-language.md` + `sources/data/2026-11-14-screening-equity-by-language.json`
- `notes/2026-11-14-0145-silta-deep-data-analysis.md` + `sources/data/2026-11-14-silta-deep-analysis.json`
- `sources/2026-11-14-europepmc-unmet-need-and-access-by-origin.md` (confirmed figures: Maamu unmet need, FinMonik access ORs)
- `sources/2026-11-14-web-research-barriers-and-data-gaps.md` (FinMonik, MoniSuomi, Maamu, THL unit costs, lung report gaps)
- `sources/2026-11-13-cancer-deaths-costs.md`, `sources/2026-11-13-astrazeneca-challenge-pdfs.md`, `sources/2026-11-13-hva-languages.md`, `sources/2026-11-13-web-research-minorities-screening.md`
- Analysis artifact: https://claude.ai/artifact/Bdht5y4oeboU5qiREMVvU7
