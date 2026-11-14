"""Runtime settings, read from the environment on every call so tests can change them."""

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
REPO_DIR = APP_DIR.parent


def content_dir() -> Path:
    return Path(os.environ.get("CONTENT_DIR", REPO_DIR / "content")).resolve()


def app_env() -> str:
    """`local` (default) or `production`. Only `local` may run the team area without a password."""
    return os.environ.get("APP_ENV", "local").strip().lower()


def team_password() -> str:
    return os.environ.get("TEAM_PASSWORD", "")


def link_override(key: str) -> str:
    """Env override for a link in site.yaml, e.g. `consumer` -> SILTA_CONSUMER_URL."""
    return os.environ.get(f"SILTA_{key.upper()}_URL", "").strip()
