"""Render the Silta printouts into print-ready PDFs and PNG previews.

Usage (from the presentation repo root):
    .venv/bin/python scripts/build_printouts.py            # render all printouts
    .venv/bin/python scripts/build_printouts.py help-card  # render one

The texts are knowledge and live in the brain repo: the ```yaml block of each
../brain/content/printouts/<id>.md, with shared phrases, languages and the QR link base in
../brain/content/printouts/shared-phrases.md ($SILTA_BRAIN overrides the brain path).
Outputs (this repo):
    content/printouts/<id>.pdf              print file, listed at /printouts
    content/media/printouts/<page>.png      one preview per page

Rendering uses Playwright (Chromium) from the tech repo's frontend install
(../tech/frontend/node_modules/playwright) or the path in $SILTA_PLAYWRIGHT. QR codes come
from segno; the page loads Noto Sans and Noto Sans Arabic from Google Fonts, so it needs
network access. Intermediate HTML goes to a temporary folder and is not kept.
"""
from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import segno
import yaml

ROOT = Path(__file__).resolve().parents[1]
BRAIN = Path(os.environ.get("SILTA_BRAIN") or ROOT.parent / "brain")
SRC = BRAIN / "content" / "printouts"
FILES = ROOT / "content" / "printouts"
PREVIEWS = ROOT / "content" / "media" / "printouts"
YAML_RE = re.compile(r"```yaml\n(.*?)\n```", re.S)
LANG_ORDER = ["en", "fi", "so", "ar", "ru", "uk", "fa"]


def load_yaml_block(path: Path) -> dict:
    m = YAML_RE.search(path.read_text(encoding="utf-8"))
    if not m:
        sys.exit(f"{path.relative_to(ROOT)}: no ```yaml block found")
    return yaml.safe_load(m.group(1))


SHARED = load_yaml_block(SRC / "shared-phrases.md")
LANGS = SHARED["languages"]
PHRASES = SHARED["phrases"]


def t(value, lang: str) -> str:
    """Resolve a text: {shared: key} or {lang: text}."""
    if isinstance(value, dict) and "shared" in value:
        value = PHRASES[value["shared"]]
    if isinstance(value, dict):
        return value.get(lang) or value["en"]
    return str(value)


def e(s: str) -> str:
    return html.escape(s, quote=True)


def link(channel: str) -> str:
    return SHARED["link_base"] + channel


def short_link(channel: str) -> str:
    return re.sub(r"^https?://", "", link(channel))


def qr(channel: str, cls: str = "qr") -> str:
    svg = segno.make(link(channel), error="m").svg_inline(border=2, dark="#1b2027", omitsize=True)
    return f'<div class="{cls}">{svg}</div>'


def sample_tag() -> str:
    return '<span class="sample">SAMPLE · link and translations not final</span>'


def band(lang: str, right: str | None = None) -> str:
    right = right if right is not None else LANGS[lang]["name"]
    return f'<header class="band"><span class="brand">{e(t(PHRASES["brand"], lang))}</span><span class="tagline">{e(right)}</span></header>'


def page(inner: str, lang: str, preview: str, cls: str) -> str:
    d = LANGS[lang]["dir"]
    font = "arabic" if d == "rtl" else ""
    return f'<section class="page {cls} {font}" lang="{lang}" dir="{d}" data-preview="{e(preview)}">{inner}{sample_tag()}</section>'


# ---------- templates ----------

def a6_front(spec: dict, lang: str) -> str:
    f = spec["front"]
    parts = [band(lang), f'<h1>{e(t(f["title"], lang))}</h1>']
    if "intro" in f:
        parts.append(f'<p class="intro">{e(t(f["intro"], lang))}</p>')
    if "steps" in f:
        parts.append("<ol class=\"steps\">" + "".join(f"<li>{e(t(s, lang))}</li>" for s in f["steps"]) + "</ol>")
    if "lead" in f:
        parts.append(f'<p class="lead">{e(t(f["lead"], lang))}</p>')
    if "bullets" in f:
        parts.append("<ul class=\"bullets\">" + "".join(f"<li>{e(t(b, lang))}</li>" for b in f["bullets"]) + "</ul>")
    if "body" in f:
        parts.append(f'<p class="body">{e(t(f["body"], lang))}</p>')
    if "field_appointment" in f:
        parts.append(
            '<div class="fields">'
            f'<div class="field"><span>{e(t(f["field_appointment"], lang))}</span><i></i></div>'
            f'<div class="field"><span>{e(t(f["field_code"], lang))}</span><i></i></div>'
            "</div>"
        )
    parts.append(
        f'<div class="qrrow">{qr(spec["channel"])}<div class="qrtext"><b>{e(t(PHRASES["scan"], lang))}</b>'
        f'<span class="link" dir="ltr">{e(short_link(spec["channel"]))}</span></div></div>'
    )
    foot = [t(PHRASES["free"], lang), t(PHRASES["interpreter"], lang)]
    parts.append(
        '<footer class="foot">' + "".join(f"<p>{e(x)}</p>" for x in foot)
        + f'<p class="sos">{e(t(PHRASES["emergency"], lang))}</p></footer>'
    )
    return page("".join(parts), lang, f'{spec["id"]}-{lang}', "a6")


def a6_back(spec: dict) -> str:
    b = spec["back_fi"]
    inner = (
        band("fi", "Henkilökunnalle")
        + f'<h1>{e(b["title"])}</h1>'
        + '<ol class="steps">' + "".join(f"<li>{e(s)}</li>" for s in b["steps"]) + "</ol>"
        + f'<p class="note">{e(b["note"])}</p>'
        + f'<p class="link small" dir="ltr">Kanava: {e(spec["channel"])} · {e(short_link(spec["channel"]))}</p>'
    )
    return page(inner, "fi", f'{spec["id"]}-back-fi', "a6 back")


def a4_multilingual(spec: dict) -> str:
    rows = "".join(
        f'<div class="row" dir="{LANGS[l]["dir"]}" lang="{l}"><span class="lname">{e(LANGS[l]["name"])}</span>'
        f'<span class="rtitle">{e(t(spec["title"], l))}</span><span class="rline">{e(t(spec["line"], l))}</span></div>'
        for l in spec["row_languages"]
    )
    sos = "".join(f'<span dir="{LANGS[l]["dir"]}">{e(t(PHRASES["emergency"], l))}</span>' for l in spec["row_languages"])
    inner = (
        band("en", " · ".join(LANGS[l]["name"] for l in spec["row_languages"]))
        + f'<div class="rows">{rows}</div>'
        + '<div class="mid">'
        + f'<div class="qrbig">{qr(spec["channel"])}<span class="link" dir="ltr">{e(short_link(spec["channel"]))}</span></div>'
        + f'<div class="staff"><b>Suomeksi</b><p>{e(spec["staff_fi"])}</p></div>'
        + "</div>"
        + f'<div class="sosband"><b>112</b><div>{sos}</div></div>'
    )
    return page(inner, "en", spec["id"], "a4 multi")


def a4_community(spec: dict, lang: str) -> str:
    signs = "".join(f"<li>{e(t(s, lang))}</li>" for s in spec["signs"])
    tabs = "".join(
        f'<div class="tab">{qr(spec["channel"], "qr")}<b>{e(t(PHRASES["brand"], lang))}</b><span>{e(t(PHRASES["help_title"], lang))}</span></div>'
        for _ in range(8)
    )
    inner = (
        band(lang)
        + f'<h1 class="huge">{e(t(spec["headline"], lang))}</h1>'
        + f'<p class="sub">{e(t(spec["sub"], lang))}</p>'
        + f'<ul class="signs">{signs}</ul>'
        + f'<p class="screening">{e(t(spec["screening"], lang))}</p>'
        + '<div class="cta">'
        + f'{qr(spec["channel"])}'
        + f'<div><p class="ctatext">{e(t(spec["cta"], lang))}</p><p>{e(t(PHRASES["free"], lang))}</p>'
        + f'<p>{e(t(PHRASES["interpreter"], lang))}</p><p class="link" dir="ltr">{e(short_link(spec["channel"]))}</p><p class="sos">{e(t(PHRASES["emergency"], lang))}</p></div>'
        + "</div>"
        + f'<div class="tabs">{tabs}</div>'
    )
    return page(inner, lang, f'{spec["id"]}-{lang}', "a4 community")


def letter_block(spec: dict) -> str:
    lines = "".join(
        f'<p dir="{LANGS[l]["dir"]}" lang="{l}" class="{"arabic" if LANGS[l]["dir"] == "rtl" else ""}">'
        f'<span class="code">{l.upper()}</span>{e(t(spec["line"], l))}</p>'
        for l in spec["row_languages"]
    )
    inner = (
        f'<div class="lqr">{qr(spec["channel"])}<b>{e(t(PHRASES["brand"], "en"))}</b>'
        f'<span class="link" dir="ltr">{e(short_link(spec["channel"]))}</span></div>'
        f'<div class="llines">{lines}</div>'
    )
    return page(inner, "fi", spec["id"], "letter")


PAGE_SIZES = {"a6-card": "105mm 148mm", "a4-multilingual": "210mm 297mm", "a4-community": "210mm 297mm", "letter-block": "180mm 60mm"}


def render_pages(spec: dict) -> str:
    tpl = spec["template"]
    if tpl == "a6-card":
        return "".join(a6_front(spec, l) for l in LANG_ORDER) + a6_back(spec)
    if tpl == "a4-multilingual":
        return a4_multilingual(spec)
    if tpl == "a4-community":
        return "".join(a4_community(spec, l) for l in LANG_ORDER)
    if tpl == "letter-block":
        return letter_block(spec)
    sys.exit(f"unknown template {tpl}")


CSS = """
:root { --ink:#1b2027; --muted:#5a6470; --petrol:#135f76; --petrol-soft:#e8f3f6; --red:#c42424; --line:#c4cad1; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #fff; color: var(--ink); font-family: "Noto Sans", "Noto Sans Arabic", system-ui, sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.arabic, .arabic * { font-family: "Noto Sans Arabic", "Noto Sans", system-ui, sans-serif; }
.page { position: relative; overflow: hidden; page-break-after: always; break-after: page; display: flex; flex-direction: column; }
.band { display: flex; justify-content: space-between; align-items: baseline; background: var(--petrol); color: #fff; }
.brand { font-weight: 800; letter-spacing: .01em; }
.tagline { opacity: .9; }
.sample { position: absolute; bottom: 1.6mm; left: 50%; transform: translateX(-50%); font: 600 5.5pt "Noto Sans", sans-serif; color: var(--red); letter-spacing: .06em; white-space: nowrap; }
.link { font-family: "Noto Sans Mono", ui-monospace, monospace; color: var(--petrol); }
.qr svg { display: block; width: 100%; height: 100%; }
.sos { color: var(--red); font-weight: 800; }

/* A6 card */
.a6 { width: 105mm; height: 148mm; padding: 0 0 5mm; }
.a6 .band { padding: 3.2mm 6mm; font-size: 9pt; }
.a6 .brand { font-size: 13pt; }
.a6 h1 { font-size: 14.5pt; line-height: 1.15; font-weight: 800; padding: 4mm 6mm 0; }
.a6 .intro, .a6 .lead, .a6 .body { font-size: 9pt; line-height: 1.35; padding: 2mm 6mm 0; }
.a6 .lead { font-weight: 700; }
.a6 .steps, .a6 .bullets { padding: 2mm 6mm 0; list-style: none; display: grid; gap: 1.4mm; counter-reset: s; }
.a6 .steps li, .a6 .bullets li { font-size: 9pt; line-height: 1.3; display: grid; grid-template-columns: 5mm 1fr; gap: 1.6mm; align-items: start; }
.a6 .steps li::before { counter-increment: s; content: counter(s); width: 5mm; height: 5mm; border-radius: 50%; background: var(--petrol); color: #fff; font-size: 7.5pt; font-weight: 700; display: grid; place-items: center; }
.a6 .bullets { gap: 2.2mm; padding-top: 3mm; }
.a6 .bullets li { font-size: 10.5pt; font-weight: 600; border: .35mm solid var(--petrol); border-radius: 2mm; padding: 2.6mm 3mm; grid-template-columns: 3mm 1fr; align-items: center; }
.a6 .bullets li::before { content: ""; width: 2.4mm; height: 2.4mm; border-radius: 50%; background: var(--petrol); }
.a6 .body { padding-top: 3.5mm; font-size: 9.5pt; }
.a6 .fields { padding: 3mm 6mm 0; display: grid; grid-template-columns: 1fr 1fr; gap: 3mm; }
.a6 .field { display: grid; gap: 1mm; font-size: 7.5pt; color: var(--muted); }
.a6 .field i { display: block; height: 7mm; border: .3mm solid var(--line); border-radius: 1.5mm; background: #fafbfc; }
.a6 .qrrow { margin: auto 6mm 0; display: flex; gap: 3.5mm; align-items: center; padding-top: 3mm; }
.a6 .qrrow .qr { width: 27mm; height: 27mm; flex: none; }
.a6 .qrtext { display: grid; gap: 1mm; font-size: 8pt; }
.a6 .qrtext .link { font-size: 6.5pt; }
.a6 .foot { padding: 2.5mm 6mm 0; display: grid; gap: .6mm; font-size: 7.5pt; line-height: 1.3; color: var(--muted); border-top: .3mm solid var(--line); margin: 3mm 6mm 0; padding-left: 0; padding-right: 0; }
.a6 .foot .sos { font-size: 9pt; }
.a6.back h1 { font-size: 12.5pt; }
.a6.back .steps li { font-size: 8.5pt; }
.a6 .note { font-size: 8pt; line-height: 1.35; margin: 3.5mm 6mm 0; padding: 2.5mm 3mm; background: var(--petrol-soft); border-radius: 1.5mm; }
.a6 .small { font-size: 6.5pt; padding: 3mm 6mm 0; margin-top: auto; }

/* A4 multilingual */
.a4 { width: 210mm; height: 297mm; }
.multi .band { padding: 7mm 14mm; font-size: 9.5pt; }
.multi .brand { font-size: 26pt; }
.multi .rows { padding: 5mm 14mm 0; display: grid; gap: 0; }
.multi .row { display: grid; grid-template-columns: 26mm 1fr; column-gap: 5mm; padding: 4.6mm 0; border-bottom: .3mm solid var(--line); }
.multi .row[dir="rtl"] { font-family: "Noto Sans Arabic", "Noto Sans", sans-serif; }
.multi .lname { grid-row: span 2; font-size: 8.5pt; font-weight: 700; color: var(--petrol); text-transform: uppercase; letter-spacing: .05em; padding-top: 1.5mm; }
.multi .rtitle { font-size: 19pt; font-weight: 800; line-height: 1.2; }
.multi .rline { font-size: 11.5pt; line-height: 1.35; color: #2e353e; }
.multi .mid { display: grid; grid-template-columns: 64mm 1fr; gap: 8mm; padding: 7mm 14mm 0; align-items: start; }
.multi .qrbig { display: grid; gap: 2mm; justify-items: center; }
.multi .qrbig .qr { width: 60mm; height: 60mm; }
.multi .qrbig .link { font-size: 8pt; }
.multi .staff { background: var(--petrol-soft); border-radius: 3mm; padding: 5mm; font-size: 9.5pt; line-height: 1.45; display: grid; gap: 2mm; }
.multi .staff b { color: var(--petrol); text-transform: uppercase; font-size: 8pt; letter-spacing: .06em; }
.multi .sosband { margin-top: auto; background: var(--red); color: #fff; display: grid; grid-template-columns: auto 1fr; gap: 6mm; align-items: center; padding: 5mm 14mm 8mm; }
.multi .sosband b { font-size: 34pt; font-weight: 800; }
.multi .sosband div { display: flex; flex-wrap: wrap; gap: 1mm 5mm; font-size: 9pt; font-weight: 600; }
.multi .sosband span[dir="rtl"] { font-family: "Noto Sans Arabic", sans-serif; }
.multi .sample { color: #fff; }

/* A4 community */
.community .band { padding: 7mm 14mm; font-size: 11pt; }
.community .brand { font-size: 26pt; }
.community .huge { font-size: 38pt; line-height: 1.12; font-weight: 800; padding: 13mm 14mm 0; }
.community .sub { font-size: 15pt; line-height: 1.4; padding: 5mm 14mm 0; }
.community .signs { list-style: none; display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; padding: 8mm 14mm 0; }
.community .signs li { border: .5mm solid var(--petrol); border-radius: 3mm; padding: 4.5mm 5mm; font-size: 16pt; font-weight: 700; line-height: 1.25; min-height: 31mm; display: flex; align-items: center; }
.community .screening { margin: 8mm 14mm 0; padding: 5mm 6mm; background: var(--petrol-soft); border-radius: 3mm; font-size: 14pt; line-height: 1.4; }
.community .cta { display: grid; grid-template-columns: 52mm 1fr; gap: 7mm; padding: 9mm 14mm 0; align-items: center; }
.community .cta .qr { width: 52mm; height: 52mm; }
.community .cta div { display: grid; gap: 1.6mm; font-size: 10.5pt; }
.community .ctatext { font-size: 17pt; font-weight: 800; line-height: 1.25; }
.community .cta .link { font-size: 8.5pt; }
.community .cta .sos { font-size: 12pt; }
.community .tabs { margin-top: auto; display: grid; grid-template-columns: repeat(8, 1fr); border-top: .4mm dashed var(--muted); height: 46mm; }
.community .tab { border-inline-start: .4mm dashed var(--muted); display: grid; justify-items: center; align-content: start; gap: 1mm; padding: 3mm 1.5mm 5mm; text-align: center; }
.community .tab:first-child { border-inline-start: 0; }
.community .tab .qr { width: 18mm; height: 18mm; }
.community .tab b { font-size: 8pt; color: var(--petrol); }
.community .tab span { font-size: 6.5pt; line-height: 1.25; }

/* Letter block */
.letter { width: 180mm; height: 60mm; flex-direction: row; gap: 5mm; padding: 4mm 5mm 5mm; border: .4mm solid var(--petrol); border-radius: 3mm; }
.lqr { display: grid; justify-items: center; align-content: start; gap: 1mm; width: 38mm; flex: none; }
.lqr .qr { width: 36mm; height: 36mm; }
.lqr b { font-size: 11pt; color: var(--petrol); }
.lqr .link { font-size: 5.8pt; }
.llines { display: grid; gap: .8mm; align-content: center; flex: 1; min-width: 0; }
.llines p { font-size: 8.4pt; line-height: 1.3; display: flex; gap: 2mm; align-items: baseline; }
.llines .code { font: 700 6.5pt "Noto Sans Mono", monospace; color: var(--petrol); width: 5.5mm; flex: none; }
.letter .sample { bottom: .8mm; }
"""

QR_JS = "document.fonts.ready.then(() => { window.__ready = true; });"


def build_html(spec: dict) -> str:
    size = PAGE_SIZES[spec["template"]]
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700;800&family=Noto+Sans+Arabic:wght@400;600;700;800&family=Noto+Sans+Mono:wght@400;700&display=block">
<style>@page {{ size: {size}; margin: 0; }}{CSS}</style>
</head><body>{render_pages(spec)}<script>{QR_JS}</script></body></html>"""


RENDER_JS = r"""
const { chromium } = require(process.env.PW);
const jobs = JSON.parse(process.env.JOBS);
(async () => {
  const browser = await chromium.launch();
  for (const job of jobs) {
    const page = await browser.newPage({ deviceScaleFactor: 1.5 });
    await page.goto('file://' + job.html, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => window.__ready === true, null, { timeout: 30000 });
    await page.pdf({ path: job.pdf, preferCSSPageSize: true, printBackground: true });
    for (const el of await page.$$('.page')) {
      const name = await el.getAttribute('data-preview');
      await el.screenshot({ path: `${job.previews}/${name}.png` });
    }
    console.log('rendered', job.id);
    await page.close();
  }
  await browser.close();
})().catch((err) => { console.error(err); process.exit(1); });
"""


def main(argv: list[str]) -> None:
    specs = [p for p in sorted(SRC.glob("*.md")) if p.name not in {"shared-phrases.md", "README.md"}]
    if argv:
        specs = [p for p in specs if p.stem in argv]
    pw = os.environ.get("SILTA_PLAYWRIGHT") or str(ROOT.parent / "tech" / "frontend" / "node_modules" / "playwright")
    if not Path(pw).exists():
        sys.exit(f"Playwright not found at {pw}. Install the tech frontend (npm ci) or set SILTA_PLAYWRIGHT.")
    FILES.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        jobs = []
        for p in specs:
            spec = load_yaml_block(p)
            out = Path(tmp) / f"{spec['id']}.html"
            out.write_text(build_html(spec), encoding="utf-8")
            jobs.append({"id": spec["id"], "html": str(out), "pdf": str(FILES / f"{spec['id']}.pdf"), "previews": str(PREVIEWS)})
        script = Path(tmp) / "render.cjs"
        script.write_text(RENDER_JS, encoding="utf-8")
        subprocess.run(["node", str(script)], check=True, env={**os.environ, "PW": pw, "JOBS": json.dumps(jobs)})


if __name__ == "__main__":
    main(sys.argv[1:])
