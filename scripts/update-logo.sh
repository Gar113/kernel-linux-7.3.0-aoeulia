#!/usr/bin/env bash
# Regenerate docs/logo.svg from the GitHub avatar of GAR 113.
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

echo "[*] tulis docs/logo.svg"
python3 - "$TMP/avatar.png" "$ROOT/docs/logo.svg" "$USER_NAME" <<'PY'
import base64, sys

src, dst, who = sys.argv[1], sys.argv[2], sys.argv[3]
b64 = base64.b64encode(open(src, "rb").read()).decode()

svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240" viewBox="0 0 240 240" role="img" aria-label="Logo WHO">
  <defs>
    <clipPath id="round"><circle cx="120" cy="120" r="88"/></clipPath>
    <linearGradient id="ring1" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#3fb950"/>
      <stop offset="50%" stop-color="#58a6ff"/>
      <stop offset="100%" stop-color="#8957e5"/>
    </linearGradient>
    <linearGradient id="ring2" x1="1" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#8957e5" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#3fb950" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="halo" cx="50%" cy="50%" r="50%">
      <stop offset="60%" stop-color="#58a6ff" stop-opacity="0"/>
      <stop offset="100%" stop-color="#58a6ff" stop-opacity="0.45"/>
    </radialGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .spin   { animation: spin 9s linear infinite; transform-origin: 120px 120px; }
      .spin-r { animation: spin 14s linear infinite reverse; transform-origin: 120px 120px; }
      .pulse  { animation: pulse 3.2s ease-in-out infinite; transform-origin: 120px 120px; }
      .breathe{ animation: breathe 3.2s ease-in-out infinite; }
      @keyframes spin   { to { transform: rotate(360deg); } }
      @keyframes pulse  { 0%,100% { opacity: .55; } 50% { opacity: 1; } }
      @keyframes breathe{ 0%,100% { opacity: .35; } 50% { opacity: .8; } }
    </style>
  </defs>

  <circle cx="120" cy="120" r="112" fill="url(#halo)" class="breathe"/>

  <!-- cincin gradien berputar -->
  <g class="spin" filter="url(#glow)">
    <circle cx="120" cy="120" r="104" fill="none" stroke="url(#ring1)" stroke-width="5"
            stroke-linecap="round" stroke-dasharray="300 353" opacity="0.95"/>
  </g>
  <g class="spin-r">
    <circle cx="120" cy="120" r="96" fill="none" stroke="url(#ring2)" stroke-width="2"
            stroke-linecap="round" stroke-dasharray="120 484" opacity="0.8"/>
  </g>

  <!-- titik orbit -->
  <g class="spin">
    <circle cx="120" cy="16" r="4" fill="#3fb950"/>
    <circle cx="224" cy="120" r="3" fill="#58a6ff"/>
  </g>
  <g class="spin-r">
    <circle cx="120" cy="224" r="3" fill="#a371f7"/>
  </g>

  <!-- logo -->
  <g clip-path="url(#round)">
    <image href="data:image/png;base64,BASE64HERE" x="32" y="32" width="176" height="176"
           preserveAspectRatio="xMidYMid slice"/>
    <circle cx="120" cy="120" r="88" fill="none" stroke="#0b1020" stroke-width="2" opacity="0.8"/>
  </g>

  <!-- aksen dalam berdenyut -->
  <circle cx="120" cy="120" r="88" fill="none" stroke="url(#ring1)" stroke-width="1.5"
          class="pulse" opacity="0.6"/>
</svg>
'''

svg = svg.replace("WHO", who).replace("BASE64HERE", b64)
open(dst, "w").write(svg)
print(f"    {dst} ({len(svg)} bytes)")
PY

echo "[*] selesai. Commit docs/logo.svg kalau mau tampil di GitHub."
