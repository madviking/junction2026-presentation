"""Loads everything under content/: site config, landing text, slides, materials, printouts.

Content is read on every request, so editing a file under content/ shows up on reload.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import markdown as md
import yaml

from app import settings

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SLIDE_BREAK = re.compile(r"^---\s*$", re.MULTILINE)

KIND_BY_SUFFIX = {
    ".md": "page",
    ".html": "html",
    ".htm": "html",
    ".pdf": "pdf",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".gif": "image",
    ".svg": "image",
    ".mp4": "video",
    ".webm": "video",
    ".csv": "data",
    ".json": "data",
    ".xlsx": "data",
    ".pptx": "slides",
    ".key": "slides",
    ".docx": "doc",
}
ICON_BY_KIND = {
    "page": "file-text",
    "html": "world-www",
    "pdf": "file-type-pdf",
    "image": "photo",
    "video": "movie",
    "data": "table",
    "slides": "presentation",
    "doc": "file-word",
    "link": "external-link",
    "file": "file",
}


def render_markdown(text: str) -> str:
    return md.markdown(text, extensions=["tables", "fenced_code", "attr_list", "sane_lists", "md_in_html"])


def split_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    return (meta if isinstance(meta, dict) else {}), text[match.end():]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --- site config -----------------------------------------------------------------


def site() -> dict:
    data = yaml.safe_load(_read(settings.content_dir() / "site.yaml")) or {}
    for key, link in (data.get("links") or {}).items():
        override = settings.link_override(key)
        if override:
            link["url"] = override
    data["video"] = {**(data.get("video") or {}), **video_embed((data.get("video") or {}).get("url", ""))}
    return data


def link_url(site_data: dict, key_or_url: str) -> str:
    """Resolve a link key from site.yaml (e.g. `consumer`) or return a literal URL."""
    link = (site_data.get("links") or {}).get(key_or_url)
    return link["url"] if link else key_or_url


def video_embed(url: str) -> dict:
    """Turn a YouTube/Vimeo/file URL into something a template can embed."""
    url = (url or "").strip()
    if not url:
        return {"kind": "none", "src": ""}
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.").removeprefix("m.")
    if host in ("youtube.com", "youtube-nocookie.com"):
        video_id = parse_qs(parsed.query).get("v", [""])[0] or parsed.path.rstrip("/").split("/")[-1]
        return {"kind": "iframe", "src": f"https://www.youtube-nocookie.com/embed/{video_id}"}
    if host == "youtu.be":
        return {"kind": "iframe", "src": f"https://www.youtube-nocookie.com/embed/{parsed.path.strip('/')}"}
    if host == "vimeo.com":
        return {"kind": "iframe", "src": f"https://player.vimeo.com/video/{parsed.path.strip('/').split('/')[0]}"}
    if parsed.path.lower().endswith((".mp4", ".webm")):
        return {"kind": "file", "src": url}
    return {"kind": "link", "src": url}


# --- landing and slides ------------------------------------------------------------


def landing() -> dict:
    meta, body = split_frontmatter(_read(settings.content_dir() / "landing.md"))
    return {"meta": meta, "html": render_markdown(body)}


@dataclass
class Slide:
    html: str
    notes: str = ""
    classes: str = ""


def slides() -> tuple[dict, list[Slide]]:
    """content/presentation.md: slides separated by a line with only `---`.

    A line `Note:` starts speaker notes (press S in the deck). A first line
    `<!-- class: name -->` adds a CSS class to that slide (e.g. `title`, `statement`).
    """
    meta, body = split_frontmatter(_read(settings.content_dir() / "presentation.md"))
    out: list[Slide] = []
    for chunk in SLIDE_BREAK.split(body):
        chunk = chunk.strip()
        if not chunk:
            continue
        classes = ""
        class_match = re.match(r"<!--\s*class:\s*([\w -]+?)\s*-->\s*", chunk)
        if class_match:
            classes, chunk = class_match.group(1), chunk[class_match.end():]
        notes = ""
        note_split = re.split(r"^Note:\s*$", chunk, maxsplit=1, flags=re.MULTILINE)
        if len(note_split) == 2:
            chunk, notes = note_split
        out.append(Slide(render_markdown(chunk), render_markdown(notes) if notes.strip() else "", classes))
    return meta, out


# --- materials (team area) and printouts ---------------------------------------------


@dataclass
class Item:
    path: str  # relative to its folder; "" for external links
    title: str
    kind: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    author: str = ""
    updated: str = ""
    url: str = ""
    meta: dict = field(default_factory=dict)

    @property
    def icon(self) -> str:
        return ICON_BY_KIND.get(self.kind, "file")


def _title_from(path: Path, meta: dict, body: str) -> str:
    if meta.get("title"):
        return str(meta["title"])
    heading = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if heading:
        return heading.group(1).strip()
    if path.suffix.lower() in (".html", ".htm"):
        title = re.search(r"<title>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
        if title:
            return title.group(1).strip()
    return path.stem.replace("-", " ").replace("_", " ").strip().capitalize()


def _as_date(value, fallback: float) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()[:10]
    if value:
        return str(value)[:10]
    return datetime.fromtimestamp(fallback).date().isoformat()


def _describe(root: Path, path: Path) -> Item:
    kind = KIND_BY_SUFFIX.get(path.suffix.lower(), "file")
    meta, body = {}, ""
    if kind in ("page", "html"):
        text = _read(path)
        meta, body = split_frontmatter(text) if kind == "page" else ({}, text)
    if kind == "html":
        meta = _html_meta(body)
    return Item(
        path=path.relative_to(root).as_posix(),
        title=_title_from(path, meta, body),
        kind=kind,
        description=str(meta.get("description", "")),
        tags=[str(t) for t in (meta.get("tags") or [])],
        author=str(meta.get("author", "")),
        updated=_as_date(meta.get("updated"), path.stat().st_mtime),
        meta=meta,
    )


def _html_meta(html: str) -> dict:
    """Read <meta name="description|author|tags|updated" content="..."> from a standalone page."""
    meta = {}
    for name, value in re.findall(
        r'<meta\s+name="(description|author|tags|updated)"\s+content="([^"]*)"', html, re.IGNORECASE
    ):
        meta[name.lower()] = value
    if "tags" in meta:
        meta["tags"] = [t.strip() for t in meta["tags"].split(",") if t.strip()]
    return meta


def _visible_files(root: Path):
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if path.is_file() and not any(part.startswith((".", "_")) for part in rel.parts) and path.name != "README.md":
            yield path


def materials() -> list[Item]:
    root = settings.content_dir() / "materials"
    items = [_describe(root, p) for p in _visible_files(root)]
    links_file = root / "_links.yaml"
    if links_file.exists():
        for entry in yaml.safe_load(_read(links_file)) or []:
            items.append(
                Item(
                    path="",
                    title=str(entry["title"]),
                    kind="link",
                    description=str(entry.get("description", "")),
                    tags=[str(t) for t in entry.get("tags") or []],
                    author=str(entry.get("author", "")),
                    updated=_as_date(entry.get("updated"), links_file.stat().st_mtime),
                    url=str(entry["url"]),
                )
            )
    return sorted(items, key=lambda i: i.updated, reverse=True)


def printouts() -> list[Item]:
    root = settings.content_dir() / "printouts"
    return [_describe(root, p) for p in _visible_files(root)]


def safe_file(folder: str, rel_path: str) -> Path | None:
    """Resolve a path inside content/<folder>/ or return None (blocks traversal and hidden files)."""
    root = (settings.content_dir() / folder).resolve()
    target = (root / rel_path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        return None
    if any(part.startswith((".", "_")) for part in target.relative_to(root).parts):
        return None
    return target


def describe(folder: str, path: Path) -> Item:
    return _describe((settings.content_dir() / folder).resolve(), path)


def page_body(path: Path) -> str:
    _, body = split_frontmatter(_read(path))
    return render_markdown(body)


SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def tech_challenges() -> list[dict]:
    """content/tech-challenges/<slug>.md, one per tech challenge we enter, sorted by `order`."""
    root = settings.content_dir() / "tech-challenges"
    pages = []
    for path in sorted(root.glob("*.md")) if root.is_dir() else []:
        if path.name == "README.md" or not SLUG.match(path.stem):
            continue
        meta, body = split_frontmatter(_read(path))
        pages.append({"slug": path.stem, "meta": meta, "html": render_markdown(body)})
    return sorted(pages, key=lambda p: (int(p["meta"].get("order", 100)), p["slug"]))


def tech_challenge(slug: str) -> dict | None:
    return next((p for p in tech_challenges() if p["slug"] == slug), None)


def _inline_markdown(text: str) -> str:
    return render_markdown(text).removeprefix("<p>").removesuffix("</p>")


def dashboard() -> dict:
    """The /dashboard report (content/dashboard.yaml), with Markdown fields rendered to HTML."""
    data = yaml.safe_load(_read(settings.content_dir() / "dashboard.yaml")) or {}
    for section in data.get("sections", []):
        if section.get("details"):
            section["details_html"] = render_markdown(section["details"])
        if section.get("list"):
            section["list_html"] = [_inline_markdown(item) for item in section["list"]]
        if section.get("aside", {}).get("body"):
            section["aside"]["body_html"] = render_markdown(section["aside"]["body"])
    return data


def data_path(name: str) -> Path:
    return settings.content_dir() / "data" / name
