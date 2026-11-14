# AGENTS.md — Silta project site (junction2026-presentation)

The team's public face and shared shelf for Junction 2026: the landing page, the
data dashboard, the deck, the video, printouts, links to the app, and the team's
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
| `content/tech-challenges/<slug>.md` | One page per tech challenge we enter (frontmatter: `title`, `partner`, `organiser`, `logo`, `summary`, `order`) | `/tech`, `/tech/<slug>` |
| `content/materials/` | Team-internal artefacts + `_links.yaml` for external ones | `/team` (password) |
| `content/media/` | Public images and video used by pages and slides | `/media/...` |
| `content/data/*.csv` | Dashboard data, each traced to a brain source (`content/data/README.md`) | — |
| `app/charts/*.py` | One module per dashboard chart, auto-discovered | `/dashboard` |
| `app/main.py` | Routes. `app/content.py` loads content, `app/auth.py` guards `/team` | — |
| `compose.aiven.yaml` | Aiven Runtime manifest (hosting); `compose.yaml` = plain Docker host; `local.compose.yaml` = live-edit overlay | — |
| `app/templates/`, `app/static/` | Jinja templates, Silta CSS on top of Tabler, deck and print CSS | — |

## Adding a dashboard chart

1. Put the data in `content/data/<name>.csv` and add a row to `content/data/README.md` naming its source.
   Real, sourced numbers only; sample data must be called `sample_*.csv` and say so in the subtitle.
2. Copy an existing module in `app/charts/` to `app/charts/<name>.py`: `CHART` dict (`title`,
   `subtitle` = the takeaway, `source`, `order`, optional `wide`, `height`) and `build(p)` returning
   `(figure, table)`. Start from `new_figure(p)` and use only palette keys (`p["lake"]`,
   `p["coral"]`, `p["reference"]`, ...), never raw colors, so light and dark both work.
3. One axis per chart, a legend for two or more series, a data table, a hover template.
4. `make test`, then look at `/dashboard` in both themes.

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

Hosted on Aiven Runtime from `compose.aiven.yaml` (steps in `README.md`). Pushing to
`main` does not redeploy; redeploy by hand in the Aiven Console. Changing the Runtime
application, its variables or any Aiven service needs the user's approval.

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
