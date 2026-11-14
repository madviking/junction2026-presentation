"""Shared-password gate for the team area (HTTP Basic; any username, password = TEAM_PASSWORD)."""

import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app import settings

_basic = HTTPBasic(auto_error=False, realm="Silta team")


def require_team(credentials: HTTPBasicCredentials | None = Depends(_basic)) -> None:
    password = settings.team_password()
    if not password:
        if settings.app_env() == "local":
            return
        # Fail closed when hosted: never serve internal material without a password.
        raise HTTPException(503, "Team area is locked: TEAM_PASSWORD is not set on this deployment.")
    if credentials is None or not secrets.compare_digest(
        credentials.password.encode(), password.encode()
    ):
        raise HTTPException(
            401, "Team password required.", headers={"WWW-Authenticate": 'Basic realm="Silta team"'}
        )
