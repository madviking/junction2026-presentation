.PHONY: install dev test up down logs build prod

PY := .venv/bin/python
DEV_COMPOSE := docker compose -f compose.yaml -f compose.dev.yaml

install:          ## local venv with runtime + test dependencies
	uv venv -q .venv --python 3.12
	uv pip install -q --python $(PY) -r requirements-dev.txt

dev:              ## run without Docker on :8400 with auto-reload
	set -a; [ -f .env ] && . ./.env; set +a; $(PY) -m uvicorn app.main:app --reload --reload-dir app --reload-dir content --port 8400

test:
	$(PY) -m pytest -q

up:               ## Docker, local mode: content/ and app/ mounted live
	$(DEV_COMPOSE) up -d --build

prod:             ## Docker, production mode: content baked into the image, team area needs TEAM_PASSWORD
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f site

build:
	docker compose build
