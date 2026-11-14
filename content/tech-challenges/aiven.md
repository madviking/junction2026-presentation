---
title: Best Use of Aiven
partner: Aiven
organiser: Aiven
logo: /media/logos/aiven.png
summary: Aiven runs Silta, with the API and the resident app on Aiven Runtime and everything they must remember in one Aiven for PostgreSQL database.
order: 10
criteria_source: brain/challenges/tech/aiven-best-use.md
# Glance: rendered as visuals at the top of the page (see AGENTS.md, Tech-partner pages).
fit:
  foundation: One Aiven for PostgreSQL database holds everything Silta must remember.
  steps:
    language: Every text in every language, versioned
    describe: Each tap stored as card ids, never free text
    route: Read-aloud audio stored next to its text
    after: Outcomes saved on the anonymous visit
    county: Public figures beside anonymous counts by language
    admin: Draft, publish, roll back; audit and cost rows
numbers:
- value: '1'
  label: database for content, audio, visits and county figures
- value: EU
  label: data stored in the EU, in the same Google Cloud region as the app
- value: '0'
  label: names, ID numbers, phone numbers or emails stored
live:
- Aiven for PostgreSQL with pgvector, same region as the app
- Silta migrations applied; CI migrates on every push
- API and resident app running on Aiven Runtime
- All tables working end to end in the app and tests
---
## How Silta uses Aiven

Silta has one database, `silta`, and in the cloud it is **Aiven for PostgreSQL** with the **pgvector** extension. We chose one well-used service over several thin ones. Everything the product must remember lives there:

- **Published content.** Every text in every language is one versioned document. Admins edit a draft, publish a new version or roll back; residents only ever see the published version (`backend/content/`, decision `docs/decisions/0003-versioned-content-document.md`).
- **Audio clips.** Read-aloud clips are stored as `bytea` rows next to the text they belong to, keyed by a hash of the exact text. A changed text never plays old audio. Aiven has no object storage, so we kept audio in Postgres on purpose (`backend/voice/`, migration `5_voice`).
- **Anonymous visits.** A resident gets a random visit code. Only its hash is stored, never the code itself, and no names, ID numbers, phone numbers or emails. Each tap is one row with card ids only, never free text (`backend/visits/`, migration `6_visits`).
- **County view.** Public county figures sit next to anonymous counts of where people are in the journey, by language (`backend/regions/`, migration `7_county_figures`).
- **Cost and audit.** Every paid AI or voice call writes a usage row with its cost, and every admin change writes an audit row (`backend/llm/`, `backend/voice/`, `backend/admin/`).

Why Aiven:
- **Stored data stays in the EU.** The database runs on Google Cloud `europe-west4` (Netherlands). We created it in Finland, but Aiven Runtime does not run there, so on 14 Nov we moved the database to the app's region (`docs/deployment.md`). For people asked to share worries about cancer, where their data is kept matters.
- **Plain PostgreSQL.** Encore.ts runs the same migrations locally and in tests. Against Aiven they run as forward-only SQL files with golang-migrate, so local and cloud schemas match (`backend/db/README.md`).
- **Same region as the app.** Our rule is that the app and the database run in the same cloud and region. From a laptop about 160 ms away, each query took roughly 350 ms; on Aiven Runtime the API sits next to the database (`docs/decisions/0002-encore-ts-on-aiven.md`, `docs/deployment.md`).

## Architecture

| Step | What happens | Where |
| --- | --- | --- |
| 1 | Push to `main` runs the full readiness gate | `.github/workflows/readiness.yml` |
| 2 | CI builds the self-hosted Encore image and applies migrations to Aiven first | same workflow, job `image` |
| 3 | Aiven Runtime builds from `compose.aiven.yaml`, which wraps that image | `compose.aiven.yaml`, `deploy/aiven/Dockerfile` |
| 4 | The API connects to Aiven for PostgreSQL over TLS; secrets come from environment variables, not the repo | `backend/infra.config.json` |
| 5 | `/api/health` checks the database round trip and that pgvector is installed | `backend/health/` |

## What is live

- The API and the resident app run on Aiven Runtime next to the database. The deployed `/api/health` answers `environment: aiven` with Postgres and pgvector OK (checked 14 Nov; https://easily-smart-aphid.eur-1.aiven.app/api/health).
- The Aiven for PostgreSQL service `silta-pg` in `google-europe-west4`, with the `vector` extension installed and the first Silta migrations applied (`docs/deployment.md`). CI is set up to apply new migrations on every push to `main`.
- The CI pipeline that builds the image, migrates Aiven and redeploys both Runtime apps on every green push to `main` (`.github/workflows/readiness.yml`).
- All the tables above, working end to end in the local app and in tests (`brain/notes/2026-11-14-0735-silta-app-walkthrough.md`).

## Why it matters for the people we serve

Language minorities are asked to trust a new tool with worries about cancer. Keeping the data in one EU database that holds no names or contact details, only hashed codes and card ids, makes that promise simple to keep and simple to check. The same database gives counties anonymous, by-language numbers on where people get stuck, without tracking anyone.
