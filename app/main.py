"""Silta project site: landing page, deck (with the pathway data slide), video, printouts, app links, team materials."""

from __future__ import annotations

import segno
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup

from app import charts, content, settings
from app.auth import require_team

app = FastAPI(title="Silta project site", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=settings.APP_DIR / "static"), name="static")
# Public images and video for the landing page and slides (content/media/).
app.mount("/media", StaticFiles(directory=settings.content_dir() / "media", check_dir=False), name="media")
templates = Jinja2Templates(directory=settings.APP_DIR / "templates")


def asset(path: str) -> str:
    """URL for a file in app/static/ with its modification time as a version, so browsers fetch new copies after a change."""
    try:
        version = int((settings.APP_DIR / "static" / path).stat().st_mtime)
    except OSError:
        return f"/static/{path}"
    return f"/static/{path}?v={version}"


templates.env.globals["asset"] = asset

NAV = (
    ("home", "/", "Silta", "home"),
    ("presentation", "/presentation", "Presentation", "presentation"),
    ("video", "/video", "Video", "movie"),
    ("printouts", "/printouts", "Printouts", "printer"),
    ("tech", "/tech", "Tech partners", "cpu"),
    ("try", "/try", "Try the app", "device-mobile"),
    ("team", "/team", "Team", "lock"),
)


def render(request: Request, template: str, active: str, **context) -> HTMLResponse:
    return templates.TemplateResponse(
        request, template, {"site": content.site(), "nav": NAV, "active": active, **context}
    )


def qr_svg(url: str) -> Markup:
    return Markup(segno.make(url, error="m").svg_inline(scale=6, border=0, dark="#142028"))


@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> str:
    return "ok"


@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return render(request, "landing.html", "home", landing=content.landing())


# The pathway (routes into cancer care) is a slide in the deck: /presentation#/pathway embeds
# /presentation/pathway, a bare page without the site menu. The old URLs point at that slide.
PATHWAY_SLIDE = "/presentation#/pathway"


@app.get("/presentation/pathway", response_class=HTMLResponse)
def pathway_embed(request: Request):
    data = content.pathway()
    available = charts.by_id()
    wanted = {c for step in data["steps"].values() for row in step.get("charts", []) for c in row}
    rendered = {name: available[name].render() for name in sorted(wanted) if name in available}
    return render(request, "pathway.html", "presentation", pathway=data, charts=rendered, embed=True)


@app.get("/pathway")
def pathway_redirect():
    return RedirectResponse(PATHWAY_SLIDE, status_code=307)


@app.get("/pathway/archive", response_class=HTMLResponse)
def pathway_archive(request: Request):
    """The earlier report-style data page (content/dashboard_archive.yaml), kept for reference."""
    story = content.dashboard()
    available = charts.by_id()
    wanted = [s["figure"]["chart"] for s in story.get("sections", []) if s.get("figure")]
    rendered = {name: available[name].render() for name in wanted if name in available}
    return render(request, "dashboard.html", "presentation", story=story, charts=rendered)


@app.get("/dashboard")
def dashboard_redirect():
    return RedirectResponse(PATHWAY_SLIDE, status_code=307)


@app.get("/presentation", response_class=HTMLResponse)
def presentation(request: Request):
    meta, slides = content.slides()
    return templates.TemplateResponse(
        request, "presentation.html", {"site": content.site(), "meta": meta, "slides": slides}
    )


# Deck v2, built from the master narrative (content/materials/master-narrative.html).
# Both decks stay live until the team picks one.
@app.get("/presentation/v2", response_class=HTMLResponse)
def presentation_v2(request: Request):
    meta, slides = content.slides("presentation-v2.md")
    return templates.TemplateResponse(
        request, "presentation.html", {"site": content.site(), "meta": meta, "slides": slides}
    )


# Deck v3: Hodan's path with drill-ins, one layout system (content/presentation-v3.yaml,
# app/static/deck-v3.css). v1 and v2 stay live until the team picks one.
@app.get("/presentation/v3", response_class=HTMLResponse)
def presentation_v3(request: Request):
    return templates.TemplateResponse(
        request, "presentation_v3.html", {"site": content.site(), "deck": content.deck_v3()}
    )


@app.get("/video", response_class=HTMLResponse)
def video(request: Request):
    return render(request, "video.html", "video")


@app.get("/tech", response_class=HTMLResponse)
def tech_index(request: Request):
    return render(request, "tech_index.html", "tech", pages=content.tech_challenges())


@app.get("/tech/{slug}", response_class=HTMLResponse)
def tech_page(request: Request, slug: str):
    page = content.tech_challenge(slug)
    if page is None:
        raise HTTPException(404)
    return render(request, "tech_page.html", "tech", page=page, pages=content.tech_challenges())


@app.get("/try", response_class=HTMLResponse)
def try_app(request: Request):
    return render(request, "try.html", "try")


@app.get("/printouts", response_class=HTMLResponse)
def printouts(request: Request):
    return render(request, "printouts.html", "printouts", items=content.printouts())


@app.get("/printouts/{rel_path:path}")
def printout(request: Request, rel_path: str):
    path = content.safe_file("printouts", rel_path)
    if path is None:
        raise HTTPException(404)
    item = content.describe("printouts", path)
    if item.kind != "page":
        return FileResponse(path)
    site = content.site()
    qr = item.meta.get("qr")
    qr_url = content.link_url(site, str(qr)) if qr else ""
    return templates.TemplateResponse(
        request,
        "printout.html",
        {"site": site, "item": item, "body": content.page_body(path), "qr_url": qr_url,
         "qr": qr_svg(qr_url) if qr_url else ""},
    )


@app.get("/team", response_class=HTMLResponse, dependencies=[Depends(require_team)])
def team(request: Request):
    items = content.materials()
    tags = sorted({t for i in items for t in i.tags})
    return render(request, "team.html", "team", items=items, tags=tags)


@app.get("/team/m/{rel_path:path}", dependencies=[Depends(require_team)])
def material(request: Request, rel_path: str, download: bool = False):
    path = content.safe_file("materials", rel_path)
    if path is None:
        raise HTTPException(404)
    item = content.describe("materials", path)
    if item.kind == "page" and not download:
        return render(request, "material.html", "team", item=item, body=content.page_body(path))
    disposition = "attachment" if download else "inline"
    return FileResponse(path, filename=path.name, content_disposition_type=disposition)
