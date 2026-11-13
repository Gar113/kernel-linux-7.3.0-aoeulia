#!/usr/bin/env python3
"""Generate docs/logo.svg and docs/hero.svg for the GAR 113 branding.

Usage: build-branding.py <avatar.png> <outdir> [username]

Avatar harus PNG persegi (disarankan 200x200, 8-bit palette) supaya base64-nya
kecil. Skrip ini dipanggil oleh scripts/update-logo.sh.
"""

import base64
import random
import sys

AVATAR, OUTDIR = sys.argv[1], sys.argv[2]
WHO = sys.argv[3] if len(sys.argv) > 3 else "GAR 113"
B64 = base64.b64encode(open(AVATAR, "rb").read()).decode()

# ---------------------------------------------------------------- logo.svg

LOGO = """<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240" viewBox="0 0 240 240" role="img" aria-label="Logo WHO">
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
"""

# ---------------------------------------------------------------- hero.svg

W, H = 1200, 440
CHIP_COLORS = [
    ("#0f2417", "#2ea043", "#3fb950"),
    ("#0d1f33", "#1f6feb", "#58a6ff"),
    ("#1a1430", "#8957e5", "#a371f7"),
    ("#241a0d", "#d29922", "#e3b341"),
]


def chips_row(items, x0, y, size=13, pad=13, gap=12, height=30):
    """Baris chip statis; lebar dihitung dari panjang teks (monospace)."""
    out, x = [], x0
    for i, label in enumerate(items):
        w = round(len(label) * size * 0.602) + pad * 2
        bg, border, fg = CHIP_COLORS[i % len(CHIP_COLORS)]
        out.append(
            f'      <rect x="{x}" y="{y}" width="{w}" height="{height}" rx="{height // 2}" '
            f'fill="{bg}" stroke="{border}"/>\n'
            f'      <text x="{x + pad}" y="{y + height // 2 + 5}" fill="{fg}" '
            f'font-family="monospace" font-size="{size}">{label}</text>'
        )
        x += w + gap
    return "\n".join(out), x - gap


def marquee(items, size=15, pad=14, gap=26):
    """Satu salinan isi marquee; mengembalikan (svg, lebar total)."""
    out, x = [], 0
    for i, label in enumerate(items):
        w = round(len(label) * size * 0.602) + pad * 2
        fg = CHIP_COLORS[i % len(CHIP_COLORS)][2]
        out.append(
            f'        <text x="{x + pad}" y="34" fill="{fg}" font-family="monospace" '
            f'font-size="{size}">{label}</text>\n'
            f'        <text x="{x + pad + w}" y="34" fill="#2b3b5c" font-family="monospace" '
            f'font-size="{size}">|</text>'
        )
        x += w + gap
    return "\n".join(out), x


MARQUEE_ITEMS = [
    "PSI", "Darling 0.1", "overlayfs", "binderfs", "MGLRU", "zram", "zswap",
    "sched_ext", "BTF", "PREEMPT_DYNAMIC", "HZ 250", "BFQ", "fq_codel", "BBR",
    "NTSYNC", "userfaultfd", "no blobs", "NO NVIDIA",
]

marq_svg, marq_w = marquee(MARQUEE_ITEMS)

random.seed(7)
stars = []
for _ in range(26):
    x, y = random.randint(20, W - 20), random.randint(20, 300)
    r = random.choice([1, 1, 1.5, 2])
    color = random.choice(["#2b3b5c", "#58a6ff", "#8957e5", "#3fb950"])
    delay = round(random.uniform(0, 3), 2)
    stars.append(
        f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" class="tw" '
        f'style="animation-delay:{delay}s"/>'
    )
STARS = "\n".join(stars)

HERO = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="440" viewBox="0 0 1200 440" role="img" aria-label="Linux x PlayStation - GAR 113">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#070b14"/>
      <stop offset="45%" stop-color="#0d1526"/>
      <stop offset="100%" stop-color="#0a1220"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#3fb950"/>
      <stop offset="50%" stop-color="#58a6ff"/>
      <stop offset="100%" stop-color="#8957e5"/>
    </linearGradient>
    <linearGradient id="stamp" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#f85149"/>
      <stop offset="100%" stop-color="#ff9b8a"/>
    </linearGradient>
    <linearGradient id="titleGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#e6edf3"/>
      <stop offset="55%" stop-color="#58a6ff"/>
      <stop offset="100%" stop-color="#a371f7"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#58a6ff" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="#58a6ff" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="#16223a" stroke-width="1"/>
    </pattern>
    <clipPath id="round"><circle cx="150" cy="160" r="88"/></clipPath>
    <clipPath id="band"><rect x="0" y="306" width="1200" height="54"/></clipPath>
    <clipPath id="credit"><rect x="1072" y="386" width="0" height="20">
      <animate attributeName="width" values="0;0;92;92;92;0;0"
               keyTimes="0;0.1;0.55;0.85;0.9;0.94;1" dur="6.5s" repeatCount="indefinite"/>
    </rect></clipPath>
    <filter id="soft" x="-20%" y="-40%" width="140%" height="180%">
      <feGaussianBlur stdDeviation="8" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .spin   {{ animation: spin 9s linear infinite;  transform-origin: 150px 160px; }}
      .spin-r {{ animation: spin 14s linear infinite reverse; transform-origin: 150px 160px; }}
      .pulse  {{ animation: pulse 3.2s ease-in-out infinite; transform-origin: 150px 160px; }}
      .breathe{{ animation: breathe 3.4s ease-in-out infinite; }}
      .tw     {{ animation: tw 3s ease-in-out infinite; }}
      .glitch {{ animation: glitch 2.6s steps(2, end) infinite; }}
      .t  {{ font-family: 'Helvetica Neue', Arial, sans-serif; fill: #e6edf3; }}
      .m  {{ font-family: monospace; fill: #9fb0cc; }}
      @keyframes spin   {{ to {{ transform: rotate(360deg); }} }}
      @keyframes pulse  {{ 0%,100% {{ opacity: .5; }} 50% {{ opacity: 1; }} }}
      @keyframes breathe{{ 0%,100% {{ opacity: .3; }} 50% {{ opacity: .85; }} }}
      @keyframes tw     {{ 0%,100% {{ opacity: .12; }} 50% {{ opacity: .9; }} }}
      @keyframes bob    {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-3px); }} }}
      @keyframes psglow {{ 0%,100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
      .bob {{ animation: bob 3.6s ease-in-out infinite; }}
      .ps  {{ animation: psglow 2.8s ease-in-out infinite; }}
      @keyframes glitch {{
        0%,100% {{ transform: translate(0, 0); }}
        20%     {{ transform: translate(-1.6px, 1px); }}
        40%     {{ transform: translate(1.6px, -1px); }}
        60%     {{ transform: translate(-1px, -1.2px); }}
        80%     {{ transform: translate(1.2px, 1.2px); }}
      }}
    </style>
  </defs>

  <rect width="1200" height="440" fill="url(#bg)"/>
  <rect width="1200" height="440" fill="url(#grid)" opacity="0.5"/>
  <ellipse cx="980" cy="60" rx="420" ry="220" fill="url(#glow)"/>
  <ellipse cx="120" cy="330" rx="300" ry="160" fill="url(#glow)" opacity="0.5"/>

  <!-- bintang berkelip -->
{STARS}

  <!-- logo beranimasi -->
  <g class="breathe">
    <circle cx="150" cy="160" r="118" fill="url(#glow)"/>
  </g>
  <g class="spin" filter="url(#soft)">
    <circle cx="150" cy="160" r="104" fill="none" stroke="url(#accent)" stroke-width="5"
            stroke-linecap="round" stroke-dasharray="300 353" opacity="0.95"/>
  </g>
  <g class="spin-r">
    <circle cx="150" cy="160" r="96" fill="none" stroke="url(#accent)" stroke-width="2"
            stroke-linecap="round" stroke-dasharray="120 484" opacity="0.75"/>
  </g>
  <g class="spin">
    <circle cx="150" cy="56" r="4" fill="#3fb950"/>
    <circle cx="254" cy="160" r="3" fill="#58a6ff"/>
  </g>
  <g class="spin-r">
    <circle cx="150" cy="264" r="3" fill="#a371f7"/>
  </g>
  <g clip-path="url(#round)">
    <image href="data:image/png;base64,{B64}" x="62" y="72" width="176" height="176"
           preserveAspectRatio="xMidYMid slice"/>
    <circle cx="150" cy="160" r="88" fill="none" stroke="#0b1020" stroke-width="2" opacity="0.85"/>
  </g>
  <circle cx="150" cy="160" r="88" fill="none" stroke="url(#accent)" stroke-width="1.5"
          class="pulse" opacity="0.6"/>

  <!-- judul: Tux + LINUX x PLAYSTATION + tombol PlayStation -->
  <g transform="translate(318 104)">
    <g class="bob">
      <ellipse cx="-22" cy="2" rx="5" ry="13" fill="#101827" stroke="#3d4f73" stroke-width="1.2"
               transform="rotate(-12 -22 2)"/>
      <ellipse cx="22" cy="2" rx="5" ry="13" fill="#101827" stroke="#3d4f73" stroke-width="1.2"
               transform="rotate(12 22 2)"/>
      <ellipse cx="-9" cy="30" rx="8" ry="3.5" fill="#f0883e"/>
      <ellipse cx="9" cy="30" rx="8" ry="3.5" fill="#f0883e"/>
      <ellipse cx="0" cy="0" rx="24" ry="30" fill="#101827" stroke="#3d4f73" stroke-width="1.5"/>
      <ellipse cx="0" cy="4" rx="16" ry="21" fill="#dfe7f2"/>
      <ellipse cx="-8" cy="-11" rx="5.5" ry="6.5" fill="#ffffff"/>
      <ellipse cx="8" cy="-11" rx="5.5" ry="6.5" fill="#ffffff"/>
      <circle cx="-7" cy="-10.5" r="2.3" fill="#0b1020"/>
      <circle cx="9" cy="-10.5" r="2.3" fill="#0b1020"/>
      <path d="M-6.5 -2 L6.5 -2 L0 7 Z" fill="#f0883e"/>
    </g>
  </g>

  <text x="362" y="124" textLength="660" lengthAdjust="spacingAndGlyphs"
        font-family="'Helvetica Neue', Arial, sans-serif" font-size="58" font-weight="800"
        letter-spacing="0.5" fill="#e6edf3">LINUX <tspan fill="#3fb950">&#215;</tspan> <tspan fill="url(#titleGrad)">PLAYSTATION</tspan></text>

  <!-- tombol PlayStation 2x2 -->
  <g transform="translate(1046 72)" fill="none" stroke-width="3.5" stroke-linejoin="round">
    <g class="ps">
      <path d="M15 6 L24 22 L6 22 Z" fill="#3fb950" stroke="#3fb950"/>
    </g>
    <g class="ps" style="animation-delay:.4s">
      <circle cx="49" cy="14" r="8.5" fill="none" stroke="#f85149"/>
    </g>
    <g class="ps" style="animation-delay:.8s">
      <path d="M9 43 L21 55 M21 43 L9 55" stroke="#58a6ff" stroke-linecap="round"/>
    </g>
    <g class="ps" style="animation-delay:1.2s">
      <rect x="42" y="42" width="14" height="14" rx="1.5" fill="none" stroke="#db61a2"/>
    </g>
  </g>

  <text x="302" y="158" textLength="836" lengthAdjust="spacingAndGlyphs" class="m"
        font-size="15" letter-spacing="3" fill="#8b9bb8">PS4 AEOLIA &#183; AMD JAGUAR 8C &#183; RADEON GCN2 &#183; MESA RADEONSI &#183; NO BLOBS</text>

  <!-- chip versi -->
  <g>
{chips_row(["7.3.0-Gar113-NoLTO", "PSI=y", "Darling 0.1", "mmap_min=0"], 302, 176)[0]}
  </g>

  <!-- stempel -->
  <g transform="translate(880 250) rotate(-7)">
    <rect x="-208" y="-34" width="416" height="68" rx="10" fill="#2a0b0e" stroke="#f85149"
          stroke-width="3" opacity="0.95"/>
    <rect x="-200" y="-26" width="400" height="52" rx="6" fill="none" stroke="#f85149"
          stroke-width="1" opacity="0.5"/>
    <g class="glitch">
      <text x="2" y="13" text-anchor="middle" font-family="'Helvetica Neue', Arial, sans-serif"
            font-size="34" font-weight="800" fill="#58a6ff" opacity="0.55">FUCK YOU NVIDIA</text>
      <text x="-2" y="11" text-anchor="middle" font-family="'Helvetica Neue', Arial, sans-serif"
            font-size="34" font-weight="800" fill="#f85149" opacity="0.5">FUCK YOU NVIDIA</text>
    </g>
    <text x="0" y="12" text-anchor="middle" font-family="'Helvetica Neue', Arial, sans-serif"
          font-size="34" font-weight="800" fill="url(#stamp)">FUCK YOU NVIDIA</text>
    <text x="0" y="30" text-anchor="middle" font-family="monospace" font-size="11"
          letter-spacing="3" fill="#ff9b8a" opacity="0.85">NO BLOBS &#183; NO PROPRIETARY DRIVER</text>
  </g>

  <!-- marquee fitur -->
  <rect x="0" y="306" width="1200" height="54" fill="#0a1221" opacity="0.92"/>
  <path d="M0 306H1200M0 360H1200" stroke="#1d2b45"/>
  <g clip-path="url(#band)">
    <g transform="translate(0 306)" font-family="monospace" font-size="15">
      <g>
        <animateTransform attributeName="transform" type="translate"
                          values="0 0;-{marq_w} 0" dur="26s" repeatCount="indefinite"/>
{marq_svg}
        <g transform="translate({marq_w} 0)">
{marq_svg}
        </g>
      </g>
    </g>
  </g>

  <!-- footer -->
  <text x="40" y="398" class="m" font-size="12" fill="#6e7f9e">dibangun &amp; diuji di console sendiri &#183; clang 19.1.7 &#183; LTO none &#183; -j6 nice 10</text>
  <text x="1160" y="400" text-anchor="end" font-family="monospace" font-size="13"
        fill="#8b9bb8" clip-path="url(#credit)">by <tspan fill="#3fb950" font-weight="700">GAR 113</tspan></text>
  <rect x="1163" y="389" width="2.5" height="13" fill="#3fb950">
    <animate attributeName="opacity" values="1;1;0;1;1;0" dur="1.05s" repeatCount="indefinite"/>
  </rect>

  <!-- scanline -->
  <rect x="0" y="0" width="1200" height="2" fill="url(#accent)" opacity="0.5">
    <animate attributeName="y" values="0;438;0" dur="11s" repeatCount="indefinite"/>
  </rect>
</svg>
"""

open(f"{OUTDIR}/logo.svg", "w").write(LOGO.replace("WHO", WHO).replace("BASE64HERE", B64))
open(f"{OUTDIR}/hero.svg", "w").write(HERO)
print(f"    {OUTDIR}/logo.svg")
print(f"    {OUTDIR}/hero.svg")
