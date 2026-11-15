#!/usr/bin/env bash
# Rebuilds the screenshots in README.md (docs/readme/*.png) from a running site.
#   bash scripts/readme_images.sh                      # site at http://localhost:8400
#   SITE_URL=https://... bash scripts/readme_images.sh
# Needs ImageMagick (`magick`, `montage`); pngquant is used when installed.
# Raw captures go to docs/readme/raw/ (gitignored); only the composed images are committed.
set -euo pipefail
cd "$(dirname "$0")/.."

node scripts/capture_readme_screens.mjs

cd docs/readme
BG='#eef2f4'
frame() { magick "raw/$1.png" -resize 1600x -bordercolor '#c9d3da' -border 1 -bordercolor "$BG" -border 14 -strip "$2.png"; }
frame landing landing
frame try try
frame tech-aiven tech-partner
montage raw/deck-hodan.png raw/deck-gap-drill.png raw/deck-pathway.png raw/deck-ways-in.png \
  raw/deck-running.png raw/deck-county.png -tile 3x2 -geometry 640x360+12+12 \
  -bordercolor '#c9d3da' -border 1 -background "$BG" -strip deck.png
montage raw/record.png raw/printouts.png -tile 2x1 -geometry 800x500+12+12 \
  -bordercolor '#c9d3da' -border 1 -background "$BG" -strip record-printouts.png

if command -v pngquant >/dev/null; then
  for f in landing try tech-partner deck record-printouts; do
    pngquant --force --skip-if-larger --quality 75-92 --output "$f.png" "$f.png" || true
  done
fi
ls -l ./*.png
