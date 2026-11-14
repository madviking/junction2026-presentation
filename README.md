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

## Run

```bash
cp .env.example .env
make up          # Docker on http://localhost:8400, edits to content/ and app/ show on reload
```

Without Docker: `make install && make dev`. Tests: `make test`.

## Host

```bash
TEAM_PASSWORD=... SILTA_CONSUMER_URL=https://... SILTA_SITE_URL=https://... docker compose up -d --build
```

`compose.yaml` builds one image with the content inside (`APP_ENV=production`). It serves
plain HTTP on port 8400 and writes nothing to disk; put it behind the host's TLS proxy. Set
`SITE_BIND=0.0.0.0` if the proxy is not on the same host. Health check: `/healthz`.

## Edit

Everything editable is under `content/` — see [AGENTS.md](AGENTS.md) for what goes where and
how to add a chart.
