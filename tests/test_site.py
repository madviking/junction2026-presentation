import base64
import re

import pytest
from markupsafe import escape
from fastapi.testclient import TestClient

from app import charts, content, settings
from app.main import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.delenv("TEAM_PASSWORD", raising=False)
    return TestClient(app)


def basic(password: str) -> dict:
    return {"Authorization": "Basic " + base64.b64encode(f"team:{password}".encode()).decode()}


@pytest.mark.parametrize(
    "path, expected",
    [
        ("/healthz", "ok"),
        ("/", "Silta"),
        ("/presentation/pathway", "Where people fall out of cancer care"),
        ("/pathway/archive", "Where in the screening pathway the gap appears"),
        ("/presentation", 'class="reveal"'),
        ("/presentation/v2", "Same letter. Twenty points fewer come."),
        ("/team/m/master-narrative.html", "Silta Master Narrative"),
        ("/team/m/silta-design-system.html", "Silta Design System"),
        ("/presentation", "Meet Hodan."),
        ("/presentation/v1", "A bridge to cancer care"),
        ("/video", "The video is not up yet"),
        ("/try", "For residents"),
        ("/printouts", "one-page summary"),
        ("/printouts/one-pager.md", "<svg"),
        ("/team", "Shared materials"),
        ("/team/m/concept/silta-v2.html", "Silta concept v2"),
    ],
)
def test_pages_render(client, path, expected):
    response = client.get(path)
    assert response.status_code == 200, response.text[:300]
    assert expected in response.text


def test_try_page_lists_phone_line_and_screening_letter(client):
    html = client.get("/try").text
    assert 'href="tel:+18784255777"' in html
    assert "+1 878 425 5777" in html
    assert "/letter/cervical/en" in html
    assert "/r/en/learn/cervical" in html


def test_admin_demo_login_is_shown_on_try_page(client):
    demo = content.site()["links"]["admin"]["demo_login"]
    assert demo["email"] == "demo@silta.test"
    html = client.get("/try").text
    assert demo["email"] in html and demo["password"] in html
    assert "View-only demo account" in html


def test_landing_shows_where_silta_fits_and_no_try_section(client):
    html = client.get("/").text
    assert 'class="silta-fit-map"' in html
    for step in content.site()["paths_fit"]["steps"]:
        assert step["title"] in html
    for item in content.site()["paths_fit"]["planned"]["items"]:
        assert item in html
    assert "<h2>Try it</h2>" not in html
    assert "One journey, five steps" not in html
    assert "Only 3 of 11 pathway steps" not in html


def test_team_link_sits_apart_on_the_right(client):
    html = client.get("/").text
    right = html.index('navbar-nav ms-md-auto')
    assert html.index('href="/try"') < right < html.index('href="/team"')


def test_try_page_groups_links(client):
    html = client.get("/try").text
    residents, county = html.index("For residents"), html.index("For the county")
    tech = html.index("Technical information")
    # the hero's jump list names the cards too, so look from the residents' section on
    assert residents < html.index("Silta phone line", residents) < county < html.index("Admin", county) < tech
    assert tech < html.index("github.com/madviking/junction2026tech")
    assert "mostly-awaited-flounder" not in html  # no card for the site itself


def test_try_page_is_visual(client):
    site = content.site()
    html = client.get("/try").text
    assert f'<iframe src="{site["links"]["consumer"]["url"]}"' in html  # the live app in the hero
    assert "data-live-toggle" in html and "/static/try-live.js" in html  # maximise for a demo
    assert "<svg" in html  # QR code to the app
    for lang in site["languages"]:  # chips for the letter and the guide
        assert f'/letter/cervical/{lang["code"]}"' in html
        assert f'/r/{lang["code"]}/learn/cervical"' in html
    for item in site["links"]["phone"]["menu"]:  # the phone line's keypad menu
        assert f"<b>{item['key']}</b>" in html
    for key in ["screening_letter", "screening_guide", "phone", "county", "admin"]:
        assert f'href="#try-{key}"' in html and f'id="try-{key}"' in html


def test_screening_letter_printout_links_every_language(client):
    assert "Example cervical cancer screening letter" in client.get("/printouts").text
    response = client.get("/printouts/cervical-screening-letter.md")
    assert response.status_code == 200
    assert "<svg" in response.text  # QR code to the guide
    for lang in ["fi", "sv", "en", "ru", "et", "uk", "ar", "so", "fa", "zh", "yue", "vi", "th", "bg"]:
        assert f"/letter/cervical/{lang}" in response.text
        assert f"/r/{lang}/learn/cervical" in response.text


def test_team_requires_password_when_set(client, monkeypatch):
    monkeypatch.setenv("TEAM_PASSWORD", "s3cret-test")
    assert client.get("/team").status_code == 401
    assert client.get("/team", headers=basic("wrong")).status_code == 401
    assert client.get("/team", headers=basic("s3cret-test")).status_code == 200
    assert client.get("/team/m/concept/silta-v2.html").status_code == 401


def test_team_fails_closed_in_production_without_password(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    assert client.get("/team").status_code == 503
    assert client.get("/").status_code == 200  # public pages stay up


@pytest.mark.parametrize("path", ["/team/m/../site.yaml", "/team/m/_links.yaml", "/printouts/../site.yaml"])
def test_no_access_outside_folders_or_to_hidden_files(client, path):
    assert client.get(path).status_code == 404


@pytest.mark.parametrize("rel", ["../site.yaml", "../../app/main.py", "_links.yaml", "concept/../../site.yaml"])
def test_safe_file_blocks_traversal_and_hidden(rel):
    # HTTP clients normalise `..` before sending, so test the resolver directly too.
    assert content.safe_file("materials", rel) is None


def test_link_override_from_env(client, monkeypatch):
    monkeypatch.setenv("SILTA_CONSUMER_URL", "https://silta.example.test/")
    assert content.site()["links"]["consumer"]["url"] == "https://silta.example.test/"
    assert "https://silta.example.test/" in client.get("/printouts/demo-qr-sign.md").text


def test_materials_include_files_and_external_links():
    items = content.materials()
    kinds = {i.kind for i in items}
    assert {"html", "link"} <= kinds
    assert all(i.path != "README.md" for i in items)


def test_slides_split_with_notes_and_classes():
    _, slides = content.slides()
    assert len(slides) >= 5
    assert slides[0].classes == "title"
    assert slides[0].notes


@pytest.mark.parametrize(
    "url, kind, src",
    [
        ("", "none", ""),
        ("https://www.youtube.com/watch?v=abc123", "iframe", "https://www.youtube-nocookie.com/embed/abc123"),
        ("https://youtu.be/abc123", "iframe", "https://www.youtube-nocookie.com/embed/abc123"),
        ("https://vimeo.com/987654", "iframe", "https://player.vimeo.com/video/987654"),
        ("https://cdn.example.test/pitch.mp4", "file", "https://cdn.example.test/pitch.mp4"),
    ],
)
def test_video_embed(url, kind, src):
    assert content.video_embed(url) == {"kind": kind, "src": src}


def test_every_chart_renders_both_themes_and_a_table():
    found = charts.discover()
    assert found
    for chart in found:
        rendered = chart.render()
        assert set(rendered["figures"]) == {"light", "dark"}
        assert rendered["table"]["columns"] and rendered["table"]["rows"]


def test_dashboard_story_is_complete():
    sections = content.dashboard()["sections"]
    assert len(sections) == 9  # summary + 8 numbered sections
    available = charts.by_id()
    for section in sections:
        assert section.get("title"), section["id"]
        if section.get("figure"):
            assert section["figure"]["chart"] in available, section["figure"]["chart"]
            assert section["figure"].get("caption"), section["id"]
        if not section.get("placeholder"):
            assert section.get("source"), f"{section['id']} has no source"


@pytest.mark.parametrize("old", ["/pathway", "/dashboard"])
def test_old_data_urls_redirect_to_pathway_slide(client, old):
    response = client.get(old, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/presentation#/pathway"


def test_pathway_is_a_deck_slide_not_a_menu_item(client):
    deck = client.get("/presentation").text
    assert '<section class="l-embed" id="pathway">' in deck
    assert 'src="/presentation/pathway"' in deck
    landing = client.get("/").text
    assert 'href="/pathway"' not in landing
    embed = client.get("/presentation/pathway").text
    assert "silta-nav" not in embed and "theme-toggle" not in embed
    assert '<base target="_blank">' in embed


def test_pathway_embeds_data_and_step_charts(client):
    html = client.get("/presentation/pathway").text
    assert 'id="pathway-data"' in html
    assert "/static/pathway.js" in html
    assert "Limitations" in html
    available = charts.by_id()
    wanted = [c for step in content.pathway()["steps"].values() for row in step.get("charts", []) for c in row]
    assert wanted
    for chart in wanted:
        assert chart in available, chart
        assert f'id="pw-fig-{chart}"' in html


def test_archive_shows_every_figure_table_and_implications(client):
    html = client.get("/pathway/archive").text
    for section in content.dashboard()["sections"]:
        if section.get("figure"):
            assert f'data-chart="{section["figure"]["chart"]}"' in html
    assert "Implications for Silta" in html
    assert "Table 1. Attendance at each step" in html


def test_pathway_data_is_complete():
    data = content.pathway()
    steps = data["steps"]
    assert {n["id"] for n in data["nodes"]} == set(steps)
    for sid, step in steps.items():
        assert step["level"] in data["levels"], sid
        assert step.get("title") and step.get("text") and step.get("src") and step.get("silta"), sid
        for table in step.get("tables", []):
            assert all(len(row) == len(table["head"]) for row in table["rows"]), sid
    for band in data["bands"]:
        assert set(band["steps"]) <= set(steps), band["id"]
        assert band.get("text"), band["id"]
    assert data["page"]["limitations"] and data["page"]["sources"]


def test_pathway_impact_view_is_complete_and_rendered(client):
    data = content.pathway()
    impact = data["impact"]
    assert impact["prompt"] and impact["caveat"] and impact["sources"]
    assert set(impact["steps"]) <= set(data["steps"])
    for sid, step in impact["steps"].items():
        assert step.get("title") and step.get("text") and step.get("src"), sid
    assert len(impact["findings"]) == 4
    for f in impact["findings"]:
        assert f.get("step") and f.get("value") and f.get("label") and f.get("text")
    for table in (impact["table"], impact["groups"]):
        assert all(len(row) == len(table["head"]) for row in table["rows"])
    assert impact["groups"]["title"] and impact["groups"]["note"]
    html = client.get("/presentation/pathway").text
    assert impact["groups"]["title"].replace("'", "&#39;") in html
    assert 'data-pw-mode="analysis"' in html and 'data-pw-mode="impact"' in html
    assert "Key findings" in html and impact["findings"][0]["label"] in html
    # Plain wording instead of "pp" on both views of the map
    assert " pp" not in html


def test_tech_challenge_pages(client, tmp_path, monkeypatch):
    import shutil

    from app import settings

    shutil.copytree(settings.content_dir(), tmp_path / "content")
    folder = tmp_path / "content" / "tech-challenges"
    folder.mkdir(exist_ok=True)
    (folder / "zz-test-partner.md").write_text(
        "---\ntitle: Best use of Testpartner\npartner: Testpartner\nsummary: We test.\norder: 999\n---\n\n## How Silta uses Testpartner\n\nBody.\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONTENT_DIR", str(tmp_path / "content"))
    assert "Best use of Testpartner" in client.get("/tech").text
    page = client.get("/tech/zz-test-partner")
    assert page.status_code == 200 and "How Silta uses Testpartner" in page.text
    assert '<details class="silta-drill"' in page.text  # each ## section is a drill-down panel
    assert client.get("/tech/does-not-exist").status_code == 404
    assert client.get("/tech/..%2Fsite").status_code == 404


def test_tech_page_glance_shows_journey_fit(client, tmp_path, monkeypatch):
    import shutil

    from app import settings

    shutil.copytree(settings.content_dir(), tmp_path / "content")
    (tmp_path / "content" / "tech-challenges" / "zz-glance.md").write_text(
        "---\ntitle: Best use of Glance\npartner: Glance\nsummary: We glance.\norder: 999\n"
        "fit:\n  steps:\n    describe: Turns words into a card\n  foundation: Holds every step\n"
        "numbers:\n  - value: '3'\n    label: steps touched\nlive: [Card matching]\n---\n\n"
        "## Details\n\nBody.\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONTENT_DIR", str(tmp_path / "content"))
    text = client.get("/tech/zz-glance").text
    assert "Turns words into a card" in text and "Holds every step" in text
    assert 'data-step="describe" data-used="true"' in text
    assert 'data-step="county" data-used="false"' in text
    assert "steps touched" in text and "Card matching" in text
    assert "> Next</h2>" not in text  # no planned box in the glance
    assert 'data-step="describe" data-used="true"' in client.get("/tech").text  # mini strip on the index card


def test_every_tech_page_has_a_glance():
    from app import content

    steps = {s["id"] for s in content.site()["journey"]}
    for page in content.tech_challenges():
        meta = page["meta"]
        used = set((meta.get("fit") or {}).get("steps") or {})
        assert used or (meta.get("fit") or {}).get("foundation"), page["slug"]
        assert used <= steps, (page["slug"], used - steps)
        assert 1 <= len(meta.get("numbers") or []) <= 3, page["slug"]
        assert meta.get("live"), page["slug"]


def test_landing_screen_slider_shows_every_screen(client):
    screens = content.site()["hero_screens"]
    assert len(screens) >= 3
    html = client.get("/").text
    assert 'class="silta-slider"' in html
    for i, screen in enumerate(screens, start=1):
        assert (settings.content_dir() / screen["src"].removeprefix("/")).is_file(), screen["src"]
        assert f'src="{screen["src"]}"' in html
        assert str(escape(screen["alt"])) in html
        assert f'aria-label="{i} / {len(screens)}"' in html


@pytest.mark.parametrize("slug", ["elevenlabs", "gemini"])
def test_partner_page_screen_slider(client, slug):
    page = next(p for p in content.tech_challenges() if p["slug"] == slug)
    screens = page["meta"]["screenshots"]
    html = client.get(f"/tech/{slug}").text
    assert 'class="silta-slider"' in html and "/static/slider.js" in html
    for screen in screens:
        assert (settings.content_dir() / screen["src"].removeprefix("/")).is_file(), screen["src"]
        assert f'src="{screen["src"]}"' in html
        assert str(escape(screen["alt"])) in html


def test_every_printout_has_a_short_description():
    for item in content.printouts():
        assert item.description, f"{item.path} has no description"
        assert len(item.description) <= 80, f"{item.path}: description too long"


def test_deck_v3_uses_one_layout_system(client):
    """Deck v3: every slide renders, every image exists, every chip opens its own sheet."""
    deck = content.deck_v3()
    html = client.get("/presentation").text
    assert "/static/deck-v3.css" in html and "/static/deck-v3.js" in html
    assert html.count("<section") == len(deck["slides"])
    allowed = {"opener", "number", "stages", "embed", "intro", "morph", "screens", "cards", "safe", "facts", "close", "team"}
    for slide in deck["slides"]:
        assert slide["layout"] in allowed, slide["id"]
        assert f'id="{slide["id"]}"' in html
        assert not re.search(r"brain |sources/|backend/|\.md\b", slide.get("source", "")), slide["id"]
        images = [slide.get("letter"), slide.get("qr"), (slide.get("from") or {}).get("src"), (slide.get("head_image") or {}).get("src")]
        images += [s["src"] for s in slide.get("screens", [])] + [l["src"] for l in slide.get("logos", [])]
        images += slide.get("reel", [])
        for src in filter(None, images):
            assert (settings.content_dir() / src.removeprefix("/")).is_file(), src
        for i, drill in enumerate(slide.get("drills", []), start=1):
            assert drill["kind"] in {"person", "county", "euro", "data"}
            sheet = f'{slide["id"]}-{i}'
            assert f'data-drill="{sheet}"' in html and f'id="{sheet}"' in html
            if drill.get("image"):
                assert (settings.content_dir() / drill["image"]["src"].removeprefix("/")).is_file()
            for item in drill.get("items", []):
                assert item.get("source"), f"{sheet}: an item has no source"
                assert not re.search(r"brain |sources/|backend/|\.md|\.ya?ml", item["source"]), f"{sheet}: internal reference in {item['source']!r}"


def test_v3_is_the_default_deck_and_old_decks_stay(client):
    assert client.get("/presentation/v3", follow_redirects=False).headers["location"] == "/presentation"
    assert "/static/deck-v3.css" in client.get("/presentation").text
    assert "/static/deck.css" in client.get("/presentation/v1").text
    assert "/static/deck.css" in client.get("/presentation/v2").text


def test_record_cut_covers_every_deck_slide_once():
    """presentation-video.yaml: every `use` names a deck slide; unlisted deck slides follow, unticked."""
    main_ids = [s["id"] for s in content.deck_v3()["slides"]]
    cut = content.deck_video()["slides"]
    ids = [s["id"] for s in cut]
    assert len(ids) == len(set(ids))
    assert set(main_ids) <= set(ids)
    for slide in cut:
        info = slide["video"]
        assert info["label"], slide["id"]
        if info["origin"] == "video":
            assert slide["id"] not in main_ids
        if info.get("unlisted"):
            assert info["on"] is False


def test_record_page_has_picker_and_no_chrome(client):
    deck = content.deck_video()
    html = client.get("/presentation/record").text
    assert 'id="record-picker"' in html and "/static/deck-record.js" in html and "data-record" in html
    assert 'class="deck-home"' not in html
    assert 'id="rp-foot"' in html and 'id="rp-drills"' in html  # footer and drill-ins: options, off by default
    assert 'id="rp-foot" checked' not in html
    assert html.count('class="rp-row"') == len(deck["slides"])
    for slide in deck["slides"]:
        assert f'id="{slide["id"]}"' in html and f'data-id="{slide["id"]}"' in html
        if slide["layout"] == "film":
            src = slide["src"]
            folder = "materials" if src.startswith("/team/m/") else "media"
            rel = src.removeprefix("/team/m/").removeprefix("/media/")
            assert content.safe_file(folder, rel) is not None, src
    # The simple routes map plays by default; the data-heavy pathway stays available, unticked.
    on = {s["id"]: s["video"]["on"] for s in deck["slides"]}
    assert on["pathway-simple"] is True and on["pathway"] is False
    assert 'class="fit-map"' in html and 'pathLength="1"' in html
    # The main deck keeps its chrome and has no picker.
    main = client.get("/presentation").text
    assert 'class="deck-home"' in main and "record-picker" not in main


def test_record_film_clip_is_served_with_ranges(client):
    slide = next(s for s in content.deck_video()["slides"] if s["layout"] == "film")
    response = client.get(slide["src"], headers={"Range": "bytes=0-99"})
    assert response.status_code == 206 and len(response.content) == 100


def test_both_decks_carry_the_event_line_in_the_foot(client):
    event = content.site()["event"]
    for path in ("/presentation", "/presentation/record"):
        html = client.get(path).text
        assert html.count(f'<p class="event">{escape(event)}</p>') == html.count('<footer class="foot') > 0, path


def test_landing_keeps_the_routes_map(client):
    html = client.get("/").text
    assert 'class="silta-fit-map"' in html and "pathLength" not in html


def test_hodan_still_only_in_the_main_deck(client):
    assert "/media/photos/hodan-opens-letter.webp" in client.get("/presentation").text
    assert "/media/photos/hodan-opens-letter.webp" not in client.get("/presentation/record").text
