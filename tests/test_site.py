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
        ("/dashboard", "Screening attendance by native language"),
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
