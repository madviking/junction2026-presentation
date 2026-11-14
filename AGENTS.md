# AGENTS.md — Silta project site (junction2026-presentation)

The team's public face and shared shelf for Junction 2026: the landing page, the
pathway data page, the deck, the video, printouts, links to the app, and the team's
internal materials. Python (FastAPI + Jinja), Tabler UI kit, Plotly charts, one
Docker image. The product itself lives in `../tech` (`junction2026tech`); the
knowledge base lives in `../brain` (`junction2026`).

## Artefacts go here by default

Anything an agent or teammate makes **for the team to look at** goes into this
repo unless the user says otherwise: HTML pages, reports, analyses, diagrams,
one-pagers, charts, mock-ups, exports, PDFs.

- Internal material → `content/materials/` (any file; subfolders fine). It shows
  up at `/team`. Describe it: Markdown gets frontmatter (`title`, `description`,
  `tags`, `author`, `updated`); a standalone HTML page gets
  `<meta name="description|tags|author|updated" content="...">`.
- A chart or data story for the public → a chart module in `app/charts/` with its
  data in `content/data/` (see below).
- Something to print → `content/printouts/`.
- If you also publish a claude.ai Artifact (or the thing only exists in Google
  Docs, Figma, ...), still add a line to `content/materials/_links.yaml` so the
  team can find it.
- Knowledge (facts, sources, decisions, notes) still goes to the brain repo, not
  here. Link to it.

## Map

| Path | What | URL |
| --- | --- | --- |
| `content/site.yaml` | Name, punchline, facts, app links, video URL, team | everywhere |
| `content/landing.md` | One-page project description | `/` |
| `content/presentation.md` | Slides (`---` between slides, `Note:` for speaker notes) | `/presentation` (PDF: `/presentation?print-pdf`) |
| `content/printouts/*.md` | A4 pages; frontmatter `qr: consumer` adds a QR code, `layout: sign` for a big sign | `/printouts` |
| `content/tech-challenges/<slug>.md` | One page per tech challenge we enter (frontmatter: `title`, `partner`, `organiser`, `logo`, `summary`, `order`, plus the glance fields in "Tech-partner pages" below) | `/tech`, `/tech/<slug>` |
| `content/materials/` | Team-internal artefacts + `_links.yaml` for external ones | `/team` (password) |
| `content/media/` | Public images and video used by pages and slides | `/media/...` |
| `content/data/*.csv` | Dashboard data, each traced to a brain source (`content/data/README.md`) | — |
| `content/data/pathway.json` | The pathway page: steps, evidence levels, findings, actions, page text; `charts` per step | `/pathway` |
| `app/charts/*.py` | One module per chart, auto-discovered; shown on a pathway step via `charts` | `/pathway`, `/pathway/archive` |
| `content/dashboard_archive.yaml` | The earlier report-style data page, kept for reference | `/pathway/archive` (`/dashboard` redirects to `/pathway`) |
| `app/main.py` | Routes. `app/content.py` loads content, `app/auth.py` guards `/team` | — |
| `compose.aiven.yaml` | Aiven Runtime manifest (hosting); `compose.yaml` = plain Docker host; `local.compose.yaml` = live-edit overlay | — |
| `app/templates/`, `app/static/` | Jinja templates, Silta CSS on top of Tabler, deck and print CSS | — |

## Build for judges: glance first, then drill down

Judges have a few minutes per team, and each one looks for something different:
a partner's technology, health impact, the build, the business case. We have far
more data than they can take in. Every page, slide and printout is therefore built
in two layers:

1. **Glance.** The top of the page makes one point visually (a chart, the journey
   diagram, a key number, a screenshot) with one sentence that states the takeaway.
   A judge who reads only this layer still gets the point.
2. **Drill down.** Method, caveats, the full data and the reasoning sit below it or
   behind it: collapsed panels, linked pages, the pathway page, the brain repo. Nothing
   is hidden, but none of it comes first.

How we write:

- **Narrative, backed by data.** Tell it through a resident, a clinic or a county.
  Every claim carries its number and a link to its source (brain file, `../tech`
  path, external reference).
- **Focused.** One message per page or slide. Cut any section that serves neither
  the glance nor a drill-down someone would actually open.
- **No AI slop.** No filler openers or summaries, no hype words ("seamless",
  "revolutionary", "leverage", "empower"), no lists of generic benefits, no emoji
  decoration. Use concrete nouns, real numbers and short sentences. If a sentence
  could describe another team's project, rewrite or delete it.
- **Check before done:** in one minute, can a judge say what this page shows? In
  ten minutes, can they find the evidence behind it?

The tech-partner pages below are the reference implementation of this pattern.

## Tech-partner pages

Each page is read by the partner's judges. They must see **within one minute,
mostly visually, how their technology fits into Silta**, and can then drill down.

- **Keep them current.** When Silta's use of a partner grows, shrinks or changes
  (in `../tech` or anywhere else), update that partner's page in the same task:
  `summary`, `fit.steps`, `numbers`, `live`/`planned` and the use-case text in the
  details. A new partner gets a new page. Every claim points to a file in `../tech`
  or `../brain`; an item moves from `planned` to `live` only with proof.
- **Glance (frontmatter, rendered as visuals at the top):**
  - `summary`: one sentence, partner technology → what it does for residents.
  - `fit.steps`: map of journey step id → what the partner does at that step, at
    most ~8 words. Step ids and labels come from `journey` in `content/site.yaml`;
    steps the partner does not touch are greyed out automatically.
  - `fit.foundation` (optional): one line for a partner that sits under every step
    (e.g. the database); drawn as a band beneath the journey.
  - `numbers`: up to three `{value, label}` facts, each traceable to a source.
  - `live` / `planned`: up to four short phrases each.
  - optional `screenshot` (`/media/...`) and `screenshot_alt`.
- **Details (Markdown body):** each `##` section becomes a collapsed drill-down
  panel, in this order: how Silta uses it, architecture, what is live vs planned,
  what the challenge asks, why it matters. Keep the body as careful as its sources.

## Adding a chart

1. Put the data in `content/data/<name>.csv` and add a row to `content/data/README.md` naming its source.
   Real, sourced numbers only; sample data must be called `sample_*.csv` and say so in the subtitle.
2. Copy an existing module in `app/charts/` to `app/charts/<name>.py`: `CHART` dict (`title`,
   `subtitle` = the takeaway, `source`, `order`, optional `wide`, `height`) and `build(p)` returning
   `(figure, table)`. Start from `new_figure(p)` and use only palette keys (`p["lake"]`,
   `p["coral"]`, `p["reference"]`, ...), never raw colors, so light and dark both work.
3. One axis per chart, a legend for two or more series, a data table, a hover template.
4. To show it on the pathway page, add its module name to a step's `charts` list in `content/data/pathway.json`.
5. `make test`, then look at `/pathway` in both themes.

## Run

```bash
make install   # .venv with dependencies (uv)
make dev       # http://localhost:8400, auto-reload, no Docker
make test
make up        # Docker, local mode: content/ and app/ mounted live
make prod      # Docker, production mode: content baked in, /team needs TEAM_PASSWORD
```

Port 8400. `APP_ENV=local` leaves `/team` open without a password; any other value
fails closed (503) until `TEAM_PASSWORD` is set. Link URLs in `site.yaml` can be
overridden per deployment with `SILTA_<KEY>_URL` (e.g. `SILTA_CONSUMER_URL`).

Hosted on Aiven Runtime from `compose.aiven.yaml` (steps in `README.md`). Every push to
`main` runs the tests and redeploys through `.github/workflows/deploy.yml` (secret `AIVEN_TOKEN`). Changing the Runtime
application, its variables or any Aiven service needs the user's approval.

## Live URLs

Checked 2026-11-14. The same table is in the `AGENTS.md` of all three repos
(`junction2026`, `junction2026tech`, `junction2026-presentation`); update all three together.

| What | URL | Notes |
| --- | --- | --- |
| Project site: landing, data, deck, video, printouts, tech-partner pages | https://mostly-awaited-flounder.eur-1.aiven.app | Aiven Runtime app `site` from `junction2026-presentation`; redeploys on every push to `main`; `/team` needs the team password (any username) |
| Silta API | https://easily-smart-aphid.eur-1.aiven.app | Aiven Runtime app `silta-api` from `junction2026tech`; health check `/api/health`; redeploy by hand (Runtime → Deploy latest commit) |
| Silta app for residents, clinic, county view, admin (frontend) | not deployed yet | Local only: http://localhost:5300 (`/`, `/clinic/<code>`, `/county/helsinki`, `/admin`). When it is deployed, add it here and set `SILTA_CONSUMER_URL`, `SILTA_COUNTY_URL`, `SILTA_ADMIN_URL` on the `site` app |
| Database | Aiven for PostgreSQL `silta-pg`, Google `europe-west4` | Connection details: password manager / `.env`, never in a repo |
| Aiven console | https://console.aiven.io, project `appzio-d111` | Runtime apps and the database; trial credit |
| Code (app) | https://github.com/madviking/junction2026tech | |
| Knowledge base (brain) | https://github.com/madviking/junction2026 | |
| Project site source | https://github.com/madviking/junction2026-presentation | |
| Local ports | site `8400`, frontend `5300`, backend `8300`, Encore dashboard `9400` | |

## Rules

- **Git.** Read-only inspection is fine. Commit, push, branch and every other
  state-changing command need the user's explicit approval for that exact action.
- **Secrets and personal data.** None in this repo: no passwords, keys, test-user
  credentials, phone numbers or private emails. Write "see password manager".
  `.env` is gitignored; `.env.example` lists names only.
- **Numbers.** Every figure on a public page traces to a source in the brain repo.
  Keep wording as careful as the source (e.g. county-level correlations are not
  individual-level facts).
- **Dependencies.** Exact pins in `requirements.txt`; CDN assets pinned to an exact version.
- **Proof.** Report what ran (tests, Docker, browser) and at which level.
