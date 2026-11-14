import base64

import pytest
from fastapi.testclient import TestClient

from app import charts, content
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
        ("/dashboard", "Where in the screening pathway the gap appears"),
        ("/presentation", 'class="reveal"'),
        ("/video", "The video is not up yet"),
        ("/try", "Demo path"),
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


def test_dashboard_shows_every_figure_table_and_implications(client):
    html = client.get("/dashboard").text
    for section in content.dashboard()["sections"]:
        if section.get("figure"):
            assert f'data-chart="{section["figure"]["chart"]}"' in html
    assert "Implications for Silta" in html
    assert "Table 1. Attendance at each step" in html


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
        "numbers:\n  - value: '3'\n    label: steps touched\nlive: [Card matching]\nplanned: [Somali input]\n---\n\n"
        "## Details\n\nBody.\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONTENT_DIR", str(tmp_path / "content"))
    text = client.get("/tech/zz-glance").text
    assert "Turns words into a card" in text and "Holds every step" in text
    assert 'data-step="describe" data-used="true"' in text
    assert 'data-step="county" data-used="false"' in text
    assert "steps touched" in text and "Card matching" in text and "Somali input" in text
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
