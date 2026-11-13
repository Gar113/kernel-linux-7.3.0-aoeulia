#!/usr/bin/env bash
# Regenerate docs/logo.svg + docs/hero.svg from the GitHub avatar of GAR 113.
# Avatar berubah? Jalankan skrip ini, commit, push. Butuh: curl, magick, python3.
set -euo pipefail

USER_NAME="${1:-Gar113}"
SIZE="${2:-200}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "[*] ambil avatar $USER_NAME"
curl -fsSL "https://github.com/${USER_NAME}.png?size=460" -o "$TMP/avatar.png"

echo "[*] perkecil ke ${SIZE}x${SIZE} (8-bit palette, hemat base64)"
magick "$TMP/avatar.png" -resize "${SIZE}x${SIZE}" -depth 8 -strip -colors 256 \
  -define png:compression-level=9 "$TMP/avatar.png"

echo "[*] tulis docs/logo.svg + docs/hero.svg"
python3 "$ROOT/scripts/build-branding.py" "$TMP/avatar.png" "$ROOT/docs" "$USER_NAME"

echo "[*] selesai. Commit docs/*.svg kalau mau tampil di GitHub."
