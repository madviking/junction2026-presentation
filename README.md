# junction2026-presentation

The project site for **Silta** (Junction 2026, AstraZeneca — Equal Care Across Finland):
landing page, data dashboard, deck, video, printouts, app links and the team's shared materials.

| Page | URL |
| --- | --- |
| Landing page | `/` |
| Data dashboard | `/dashboard` |
| Presentation (PDF export: `?print-pdf`) | `/presentation` |
| Video | `/video` |
| Printouts | `/printouts` |
| Links to the resident app, county view, admin, source | `/try` |
| Team materials (password when hosted) | `/team` |

## Run locally

```bash
cp .env.example .env
make up          # Docker on http://localhost:8400, edits to content/ and app/ show on reload
```

Without Docker: `make install && make dev`. Tests: `make test`.

## Host on Aiven Runtime

Aiven Runtime builds the `Dockerfile` from this repository using `compose.aiven.yaml`.
The container serves plain HTTP on 8400, Aiven terminates TLS and serves it on HTTPS 443.
The image writes nothing to disk and needs no database.

One-time setup (Aiven project `appzio-d111`, the same as the app backend):

1. Push this repository's `main` to GitHub (`madviking/junction2026-presentation`).
2. Aiven Console → Runtime → Deploy application → GitHub account `madviking`,
   repository `junction2026-presentation`, branch `main`, manifest **`compose.aiven.yaml`**.
   Live since 2026-11-14: application `site`, Google Cloud `europe-west4` (Netherlands; Runtime
   offered no Finland region), plan Startup-20-512 (~$12/month),
   https://mostly-awaited-flounder.eur-1.aiven.app
3. Application → environment variables:

   | Variable | Value |
   | --- | --- |
   | `TEAM_PASSWORD` | shared team password (password manager). Without it `/team` answers 503. |
   | `SILTA_SITE_URL` | this application's public URL (used by printout QR codes) |
   | `SILTA_CONSUMER_URL`, `SILTA_COUNTY_URL`, `SILTA_ADMIN_URL` | the deployed app's URLs, once it is deployed |

4. Check `https://<public-url>/healthz` answers `ok` and `/team` asks for the password.

Updates: a push does not redeploy. Runtime → application → Actions → **Deploy latest commit**.
Content (texts, slides, charts, materials) is baked into the image, so every content
change needs a push and a redeploy. Pin the exact commit you show to judges.

## Host on any Docker host

```bash
TEAM_PASSWORD=... SILTA_SITE_URL=https://... docker compose up -d --build
```

`compose.yaml` binds `127.0.0.1:8400`; put it behind the host's TLS proxy, or set
`SITE_BIND=0.0.0.0`. Health check: `/healthz`.

## Edit

Everything editable is under `content/` — see [AGENTS.md](AGENTS.md) for what goes where and
how to add a chart.
