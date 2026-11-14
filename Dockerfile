# Silta project site: one small image, content baked in. Content is plain files, so the
# container never writes to disk.
FROM python:3.12.8-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_ENV=production \
    PORT=8400

WORKDIR /srv
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app ./app
COPY content ./content

RUN useradd --system --uid 10001 --no-create-home site
USER site

EXPOSE 8400
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8400\")}/healthz', timeout=2)"

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
