---
title: Best Use of Aiven
partner: Aiven
organiser: Aiven
logo: /media/logos/aiven.png
summary: Aiven for PostgreSQL in Finland is Silta's single store for content, audio, anonymous visits and county figures.
order: 10
criteria_source: brain/challenges/tech/aiven-best-use.md
---

## What the challenge asks

- Use at least one Aiven service as a meaningful part of the project and show what it enables.
- One well-executed service can be as strong as several combined.
- Judging: meaningful use of Aiven 40%, technical implementation 30%, impact on the overall solution 20%, creativity 10%.
- Prizes: €1,000, €750 and €500 (`brain/challenges/tech/aiven-best-use.md`).

## How Silta uses Aiven

Silta has one database, `silta`, and in the cloud it is **Aiven for PostgreSQL** with the **pgvector** extension. We chose one well-used service over several thin ones. Everything the product must remember lives there:

- **Published content.** Every text in every language is one versioned document. Admins edit a draft, publish a new version or roll back; residents only ever see the published version (`backend/content/`, decision `docs/decisions/0003-versioned-content-document.md`).
- **Audio clips.** Read-aloud clips are stored as `bytea` rows next to the text they belong to, keyed by a hash of the exact text. A changed text never plays old audio. Aiven has no object storage, so we kept audio in Postgres on purpose (`backend/voice/`, migration `5_voice`).
- **Anonymous visits.** A resident gets a random visit code. Only its hash is stored, never the code itself, and no names, ID numbers, phone numbers or emails. Each tap is one row with card ids only, never free text (`backend/visits/`, migration `6_visits`).
- **County view.** Public county figures sit next to anonymous counts of where people are in the journey, by language (`backend/regions/`, migration `7_county_figures`).
- **Cost and audit.** Every paid AI or voice call writes a usage row with its cost, and every admin change writes an audit row (`backend/llm/`, `backend/voice/`, `backend/admin/`).

Why Aiven:
- **Stored data stays in Finland.** The service runs on Google Cloud `europe-north1` (Finland) (`docs/deployment.md`). For people asked to share worries about cancer, where their data is kept matters.
- **Plain PostgreSQL.** Encore.ts runs the same migrations locally and in tests. Against Aiven they run as forward-only SQL files with golang-migrate, so local and cloud schemas match (`backend/db/README.md`).
- **Same region as the app.** Our rule is that the app and the database run in the same cloud and region; Aiven Runtime can host the API next to the database (`docs/decisions/0002-encore-ts-on-aiven.md`).

## Architecture

| Step | What happens | Where |
| --- | --- | --- |
| 1 | Push to `main` runs the full readiness gate | `.github/workflows/readiness.yml` |
| 2 | CI builds the self-hosted Encore image and applies migrations to Aiven first | same workflow, job `image` |
| 3 | Aiven Runtime builds from `compose.aiven.yaml`, which wraps that image | `compose.aiven.yaml`, `deploy/aiven/Dockerfile` |
| 4 | The API connects to Aiven for PostgreSQL over TLS; secrets come from environment variables, not the repo | `backend/infra.config.json` |
| 5 | `/api/health` checks the database round trip and that pgvector is installed | `backend/health/` |

## What is live vs planned

Live:
- The Aiven for PostgreSQL service in `europe-north1`, with the `vector` extension installed and the first Silta migrations applied (`docs/deployment.md`). CI is set up to apply new migrations on every push to `main`.
- The self-hosted image, run from a laptop against Aiven, answered `/api/health` with Postgres and pgvector OK over TLS (verified 14 Nov, `docs/deployment.md`).
- The CI pipeline that builds the image and migrates Aiven (`.github/workflows/readiness.yml`).
- All the tables above, working end to end in the local app and in tests (`brain/notes/2026-11-14-0735-silta-app-walkthrough.md`).

In progress or planned:
- Running the API on Aiven Runtime next to the database. The manifest is ready; the first Runtime deploy is not yet recorded in the docs. The demo currently runs locally on Encore's own Postgres.
- Deploying the frontend (`docs/deployment.md`, "Open").
- Using pgvector for retrieval over public Finnish health sources. The extension is installed, but no embeddings table exists yet (`backend/db/migrations/2_init_silta.up.sql`).
- Deleting expired visits. Visits stop being readable after their expiry date and a resident can delete their own visit, but no job removes expired rows yet.
- Small-number suppression in the county view (`brain/notes/2026-11-14-0735-silta-app-walkthrough.md`, "Known gaps").

## Why it matters for the people we serve

Language minorities are asked to trust a new tool with worries about cancer. Keeping the data in one Finnish-region database that holds no names or contact details, only hashed codes and card ids, makes that promise simple to keep and simple to check. The same database gives counties anonymous, by-language numbers on where people get stuck, without tracking anyone.
