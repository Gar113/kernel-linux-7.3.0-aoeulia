#!/usr/bin/env python3
"""Generate aset visual dokumentasi: hardware.svg, psi.svg, bench.svg.

Semua SVG self-contained (CSS/SMIL, tanpa script, tanpa font eksternal)
supaya tetap beranimasi saat dipasang lewat <img> di GitHub.

Jalankan:  python3 scripts/build-docs-assets.py
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Segoe UI',system-ui,-apple-system,Helvetica,Arial,sans-serif"

BG = "#0d1117"
PANEL = "#161b22"
PANEL2 = "#1c2430"
LINE = "#30363d"
TXT = "#c9d1d9"
DIM = "#8b949e"
GREEN = "#3fb950"
CYAN = "#58a6ff"
PURPLE = "#a371f7"
AMBER = "#e3b341"
ORANGE = "#f0883e"
RED = "#f85149"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def head(w, h, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"
     viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>
  .mono {{ font-family:{MONO}; }}
  .sans {{ font-family:{SANS}; }}
  .t   {{ fill:{TXT}; }}
  .d   {{ fill:{DIM}; }}
  .flow {{ stroke-dasharray:5 7; animation:dash 1.1s linear infinite; }}
  @keyframes dash {{ to {{ stroke-dashoffset:-24; }} }}
  @keyframes pulse {{ 0%,100% {{ opacity:.55 }} 50% {{ opacity:1 }} }}
  @keyframes glow {{ 0%,100% {{ filter:drop-shadow(0 0 2px #3fb95088) }}
                     50% {{ filter:drop-shadow(0 0 9px #3fb950cc) }} }}
  .pulse {{ animation:pulse 2.6s ease-in-out infinite; }}
  .glow  {{ animation:glow 2.8s ease-in-out infinite; }}
</style>
<defs>
  <linearGradient id="gcy" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{CYAN}" stop-opacity=".22"/>
    <stop offset="1" stop-color="{PURPLE}" stop-opacity=".10"/>
  </linearGradient>
  <linearGradient id="ggr" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{GREEN}"/><stop offset="1" stop-color="{CYAN}"/>
  </linearGradient>
  <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
          orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="{DIM}"/>
  </marker>
</defs>
<rect width="{w}" height="{h}" fill="{BG}"/>
'''


def footer(w, h, text="GAR 113 · PS4 Linux 7.3.0-Gar113-NoLTO"):
    return f'''<text x="{w-24}" y="{h-14}" text-anchor="end" class="mono d" font-size="11">{esc(text)}</text>
</svg>
'''


# ---------------------------------------------------------------- hardware
def hardware():
    w, h = 1200, 660
    s = [head(w, h, "Peta hardware PS4 Aeolia")]
    s.append(f'<text x="32" y="46" class="sans t" font-size="26" font-weight="700">'
             f'PS4 Aeolia — peta hardware</text>')
    s.append(f'<text x="32" y="72" class="mono d" font-size="13">'
             f'semua blok di bawah aktif di 7.3.0-Gar113-NoLTO (dibaca dari console)</text>')

    # legend
    s.append(f'<circle cx="905" cy="42" r="5" fill="{GREEN}" class="glow"/>')
    s.append(f'<text x="918" y="46" class="mono d" font-size="12">driver aktif</text>')
    s.append(f'<circle cx="1025" cy="42" r="5" fill="{AMBER}"/>')
    s.append(f'<text x="1038" y="46" class="mono d" font-size="12">terbatas</text>')

    # ---- APU
    s.append(f'<rect x="330" y="108" width="450" height="268" rx="18" fill="url(#gcy)" '
             f'stroke="{CYAN}" stroke-width="1.6"/>')
    s.append(f'<text x="555" y="138" text-anchor="middle" class="sans t" font-size="17" '
             f'font-weight="700">AMD Jaguar APU</text>')
    s.append(f'<text x="555" y="158" text-anchor="middle" class="mono d" font-size="11.5">'
             f'22 nm · 8 core · 1,6 GHz · 2×2 MB L2</text>')

    # CPU
    s.append(f'<rect x="356" y="176" width="190" height="176" rx="12" fill="{PANEL}" stroke="{GREEN}" stroke-width="1.3"/>')
    s.append(f'<text x="451" y="202" text-anchor="middle" class="sans t" font-size="15" font-weight="700">CPU</text>')
    for i, ln in enumerate(["8C / 8T", "800–1600 MHz", "AVX · AES-NI", "tanpa AVX2", "tanpa SHA-NI"]):
        s.append(f'<text x="451" y="{226+i*24}" text-anchor="middle" class="mono d" font-size="12">{ln}</text>')

    # GPU
    s.append(f'<rect x="564" y="176" width="190" height="176" rx="12" fill="{PANEL}" stroke="{PURPLE}" stroke-width="1.3"/>')
    s.append(f'<text x="659" y="202" text-anchor="middle" class="sans t" font-size="15" font-weight="700">GPU Liverpool</text>')
    for i, ln in enumerate(["18 CU · GCN2", "GL 4.6 · VK 1.3", "radeonsi + radv", "HDMI-A-1", "DPM off"]):
        col = AMBER if ln == "DPM off" else DIM
        s.append(f'<text x="659" y="{226+i*24}" text-anchor="middle" class="mono" font-size="12" fill="{col}">{ln}</text>')

    # ---- memory
    s.append(f'<rect x="52" y="182" width="228" height="118" rx="14" fill="{PANEL}" stroke="{AMBER}" stroke-width="1.4"/>')
    s.append(f'<text x="166" y="210" text-anchor="middle" class="sans t" font-size="15" font-weight="700">GDDR5 8 GB</text>')
    s.append(f'<text x="166" y="234" text-anchor="middle" class="mono d" font-size="12">shared CPU + GPU (UMA)</text>')
    s.append(f'<text x="166" y="256" text-anchor="middle" class="mono" font-size="12" fill="{AMBER}">5,8 GiB terlihat Linux</text>')
    s.append(f'<text x="166" y="278" text-anchor="middle" class="mono d" font-size="12">VRAM 2048 MB · GTT 2,9 GiB</text>')

    # memory <-> APU links
    for y, tgt in ((216, "CPU"), (266, "GPU")):
        d = f"M280 {y} H330"
        s.append(f'<path d="{d}" stroke="{AMBER}" stroke-width="2" fill="none" class="flow"/>')
        s.append(f'<circle r="4" fill="{AMBER}">'
                 f'<animateMotion dur="2.2s" repeatCount="indefinite" path="{d}"/></circle>')

    # ---- southbridge
    s.append(f'<rect x="52" y="424" width="1096" height="62" rx="12" fill="{PANEL2}" stroke="{LINE}"/>')
    s.append(f'<text x="600" y="450" text-anchor="middle" class="sans t" font-size="15" font-weight="700">'
             f'Aeolia southbridge · 104d:90a1</text>')
    s.append(f'<text x="600" y="472" text-anchor="middle" class="mono d" font-size="11.5">'
             f'ACPI · SATA AHCI · SDHCI · xHCI · GbE · HDA · DMAC</text>')
    # APU -> southbridge
    s.append(f'<path d="M555 376 V424" stroke="{DIM}" stroke-width="2" fill="none" class="flow"/>')
    s.append(f'<circle r="4" fill="{CYAN}">'
             f'<animateMotion dur="1.8s" repeatCount="indefinite" path="M555 376 V424"/></circle>')

    # ---- peripherals
    per = [
        ("HDMI-A-1", ["1920×1080 @60", "audio HDMI 0/1"], GREEN),
        ("SATA AHCI", ["HDD 500 GB 5400", "85 MiB/s seq"], GREEN),
        ("SDIO · mmc0", ["WiFi SD8797", "-59 dBm 2,4 GHz"], GREEN),
        ("USB xHCI 3.0", ["6 bus · hub · audio", "kbd · mouse · NVMe"], GREEN),
        ("GbE Yukon-2", ["sky2 → eth0", "kabel belum dicolok"], AMBER),
        ("HDA + USB audio", ["snd_hda_intel", "snd_usb_audio"], GREEN),
    ]
    bw, gap = 168, 20
    x = 52
    for name, lines, col in per:
        s.append(f'<rect x="{x}" y="524" width="{bw}" height="92" rx="10" fill="{PANEL}" stroke="{col}" stroke-width="1.1" stroke-opacity=".8"/>')
        s.append(f'<text x="{x+bw/2}" y="550" text-anchor="middle" class="sans t" font-size="12.5" font-weight="600">{esc(name)}</text>')
        for i, ln in enumerate(lines):
            s.append(f'<text x="{x+bw/2}" y="{572+i*19}" text-anchor="middle" class="mono d" font-size="10.8">{esc(ln)}</text>')
        cx = x + bw / 2
        s.append(f'<path d="M{cx} 486 V524" stroke="{col}" stroke-width="1.6" fill="none" class="flow"/>')
        s.append(f'<circle r="3.5" fill="{col}">'
                 f'<animateMotion dur="{1.6 + (x % 7) * 0.12:.2f}s" repeatCount="indefinite" path="M{cx} 486 V524"/></circle>')
        x += bw + gap

    s.append(footer(w, h))
    return "".join(s)


# ---------------------------------------------------------------- PSI
def psi():
    w, h = 1120, 470
    s = [head(w, h, "PSI: dari tekanan memori sampai lmkd")]
    s.append(f'<text x="32" y="46" class="sans t" font-size="26" font-weight="700">'
             f'PSI — Pressure Stall Information</text>')
    s.append(f'<text x="32" y="72" class="mono d" font-size="13">'
             f'lmkd membunuh proses berdasarkan tekanan, bukan ambang MemFree yang buta</text>')

    boxes = [
        ("Proses", ["Android / app", "di Waydroid"], CYAN),
        ("Kernel", ["hitung stall", "some · full"], PURPLE),
        ("/proc/pressure", ["memory", "cpu · io"], AMBER),
        ("lmkd", ["baca avg10", "tiap 1–2 s"], GREEN),
        ("kill", ["proses paling", "banyak makan"], RED),
    ]
    bw, bh, gap = 176, 92, 34
    x = 32
    ys = 150
    centers = []
    for name, lines, col in boxes:
        s.append(f'<rect x="{x}" y="{ys}" width="{bw}" height="{bh}" rx="12" fill="{PANEL}" stroke="{col}" stroke-width="1.4"/>')
        s.append(f'<text x="{x+bw/2}" y="{ys+28}" text-anchor="middle" class="sans t" font-size="14" font-weight="700">{esc(name)}</text>')
        for i, ln in enumerate(lines):
            s.append(f'<text x="{x+bw/2}" y="{ys+50+i*19}" text-anchor="middle" class="mono d" font-size="11.5">{esc(ln)}</text>')
        centers.append(x + bw / 2)
        x += bw + gap

    # arrows
    for i in range(len(boxes) - 1):
        x1 = 32 + i * (bw + gap) + bw
        x2 = x1 + gap
        d = f"M{x1+2} {ys+bh/2} H{x2-6}"
        s.append(f'<path d="{d}" stroke="{DIM}" stroke-width="1.6" fill="none" marker-end="url(#ar)"/>')
        s.append(f'<circle r="3.5" fill="{GREEN}">'
                 f'<animateMotion dur="{1.3 + i*0.15:.2f}s" repeatCount="indefinite" path="{d}"/></circle>')

    # gauge under kernel box
    gx, gy, gw = 32 + bw + gap + 10, 300, 150
    s.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="10" rx="5" fill="{PANEL2}" stroke="{LINE}"/>')
    s.append(f'<rect x="{gx}" y="{gy}" width="66" height="10" rx="5" fill="url(#ggr)">'
             f'<animate attributeName="width" values="4;66;30;66;4" dur="6s" repeatCount="indefinite"/></rect>')
    s.append(f'<text x="{gx}" y="{gy+30}" class="mono d" font-size="11">avg10 = 30,44 saat tekanan</text>')

    # memory bar
    mx, my, mw = 32, 366, 1056
    s.append(f'<text x="{mx}" y="{my-10}" class="mono d" font-size="12">memori terpakai saat tes: 4,00 GiB dialokasikan · swap out 582.753 halaman</text>')
    s.append(f'<rect x="{mx}" y="{my}" width="{mw}" height="16" rx="8" fill="{PANEL2}" stroke="{LINE}"/>')
    s.append(f'<rect x="{mx}" y="{my}" width="620" height="16" rx="8" fill="{AMBER}" opacity=".85">'
             f'<animate attributeName="width" values="60;820;520;820;60" dur="6s" repeatCount="indefinite"/></rect>')

    # some/full explanation
    s.append(f'<rect x="32" y="402" width="1056" height="52" rx="10" fill="{PANEL}" stroke="{LINE}"/>')
    s.append(f'<text x="48" y="424" class="mono" font-size="12" fill="{GREEN}">some</text>')
    s.append(f'<text x="96" y="424" class="mono d" font-size="12">= ada task yang stall</text>')
    s.append(f'<text x="300" y="424" class="mono" font-size="12" fill="{RED}">full</text>')
    s.append(f'<text x="340" y="424" class="mono d" font-size="12">= semua task stall (sistem benar-benar macet)</text>')
    s.append(f'<text x="48" y="444" class="mono d" font-size="11.5">CONFIG_PSI=y · PSI_DEFAULT_DISABLED=n · aktif sejak boot tanpa parameter cmdline</text>')

    s.append(footer(w, h))
    return "".join(s)


# ---------------------------------------------------------------- bench
def bar(x, y, maxw, value, vmax, col, label, sub, delay, unit):
    bw = max(3, maxw * value / vmax)
    out = [f'<rect x="{x}" y="{y}" width="{maxw}" height="22" rx="6" fill="{PANEL2}"/>']
    out.append(f'<rect x="{x}" y="{y}" width="{bw:.1f}" height="22" rx="6" fill="{col}" opacity=".9">'
               f'<animate attributeName="width" from="0" to="{bw:.1f}" dur="1.2s" '
               f'begin="{delay}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect>')
    out.append(f'<text x="{x+8}" y="{y+15}" class="mono t" font-size="11.5">{esc(label)}</text>')
    out.append(f'<text x="{x+maxw-8}" y="{y+15}" text-anchor="end" class="mono" font-size="11.5" fill="{col}">{esc(sub)}</text>')
    out.append(f'<text x="{x+maxw+10}" y="{y+15}" class="mono d" font-size="10.5">{esc(unit)}</text>')
    return "".join(out)


def bench():
    w, h = 1200, 780
    s = [head(w, h, "Benchmark PS4 Linux 7.3.0-Gar113-NoLTO")]
    s.append(f'<text x="32" y="46" class="sans t" font-size="26" font-weight="700">'
             f'Benchmark di console PS4</text>')
    s.append(f'<text x="32" y="72" class="mono d" font-size="13">'
             f'AMD Jaguar 8C @ 1,6 GHz · 5,8 GiB RAM · HDD 5400 rpm · GPU DPM off · HZ=250</text>')

    # panel CPU
    s.append(f'<rect x="32" y="98" width="552" height="286" rx="14" fill="{PANEL}" stroke="{LINE}"/>')
    s.append(f'<text x="52" y="128" class="sans t" font-size="15" font-weight="700">CPU — throughput 16 KiB</text>')
    s.append(f'<text x="52" y="148" class="mono d" font-size="11">OpenSSL speed, 2 detik/algoritma</text>')
    rows = [("AES-256-GCM", 765.5, GREEN), ("ChaCha20-Poly1305", 262.0, CYAN), ("SHA-256", 90.4, AMBER)]
    y = 166
    for name, val, col in rows:
        s.append(bar(52, y, 400, val, 800, col, name, f"{val:,.1f}".replace(",", "."), 0.2 + (y-166)*0.004, "MB/s"))
        y += 44
    s.append(f'<text x="52" y="330" class="mono d" font-size="11">7z b -mmt8: 10.726 MIPS · zstd -3: 43,8 MB/s compress</text>')
    s.append(f'<text x="52" y="352" class="mono d" font-size="11">AES cepat karena AES-NI; SHA lambat karena Jaguar tanpa SHA-NI</text>')

    # panel disk
    s.append(f'<rect x="616" y="98" width="552" height="286" rx="14" fill="{PANEL}" stroke="{LINE}"/>')
    s.append(f'<text x="636" y="128" class="sans t" font-size="15" font-weight="700">Disk — HDD 5400 rpm</text>')
    s.append(f'<text x="636" y="148" class="mono d" font-size="11">fio direct I/O, ext4, mq-deadline</text>')
    drows = [
        ("seq read 1M", 85.3, 100, "85 IOPS · p99 34 ms", GREEN),
        ("seq write 1M", 61.6, 100, "62 IOPS · p99 100 ms", CYAN),
        ("rand read 4K QD16", 0.2, 100, "54 IOPS · p99 472 ms", AMBER),
        ("rand write 4K QD16", 0.6, 100, "151 IOPS · p99 505 ms", AMBER),
    ]
    y = 166
    for name, val, vmax, sub, col in drows:
        s.append(bar(636, y, 330, val, vmax, col, name, sub, 0.4 + (y-166)*0.003, "MiB/s"))
        y += 44
    s.append(f'<text x="636" y="352" class="mono d" font-size="11">random 4K kecil = batas fisik HDD, bukan kernel</text>')

    # panel PSI
    s.append(f'<rect x="32" y="404" width="552" height="286" rx="14" fill="{PANEL}" stroke="{LINE}"/>')
    s.append(f'<text x="52" y="434" class="sans t" font-size="15" font-weight="700">PSI — avg10 saat tekanan</text>')
    s.append(f'<text x="52" y="454" class="mono d" font-size="11">/proc/pressure · naik saat beban, turun lagi setelahnya</text>')
    s.append(bar(52, 474, 400, 45.01, 50, GREEN, "cpu · some (16× yes)", "45,01", 0.5, "%"))
    s.append(bar(52, 518, 400, 30.44, 50, AMBER, "memory · some (4 GiB)", "30,44", 0.7, "%"))
    s.append(bar(52, 562, 400, 30.29, 50, RED, "memory · full", "30,29", 0.9, "%"))
    s.append(f'<text x="52" y="618" class="mono d" font-size="11">swap out 582.753 halaman (~2,2 GiB) selama tes memori</text>')
    s.append(f'<text x="52" y="640" class="mono d" font-size="11">inilah sinyal yang dibaca lmkd Android/Waydroid</text>')

    # panel GPU
    s.append(f'<rect x="616" y="404" width="552" height="286" rx="14" fill="{PANEL}" stroke="{LINE}"/>')
    s.append(f'<text x="636" y="434" class="sans t" font-size="15" font-weight="700">GPU — 18 CU GCN2</text>')
    s.append(f'<text x="636" y="454" class="mono d" font-size="11">Mesa 25.1.0-devel · radeonsi + radv · 1280×720</text>')
    # stat cards
    for i, (name, val, col, note) in enumerate([
        ("glmark2", "3.072", GREEN, "build 3.326 · terrain 663 FPS"),
        ("vkmark", "5.401", PURPLE, "vertex 5.452 FPS · texture 5.385"),
    ]):
        cx = 636 + i * 258
        s.append(f'<rect x="{cx}" y="472" width="240" height="96" rx="12" fill="{PANEL2}" stroke="{col}" stroke-width="1.1"/>')
        s.append(f'<text x="{cx+16}" y="498" class="mono d" font-size="12">{esc(name)}</text>')
        s.append(f'<text x="{cx+16}" y="534" class="sans" font-size="30" font-weight="700" fill="{col}">{esc(val)}</text>')
        s.append(f'<text x="{cx+16}" y="556" class="mono d" font-size="10.5">{esc(note)}</text>')
    s.append(f'<text x="636" y="600" class="mono d" font-size="11">skor diambil dengan amdgpu.dpm=0 → GPU di strap clock</text>')
    s.append(f'<text x="636" y="622" class="mono d" font-size="11">latency timer: lantai 4 ms (HZ=250, clockevent Aeolia)</text>')
    s.append(f'<text x="636" y="644" class="mono d" font-size="11">jitter sleep(1 ms): p99 4,5 ms idle · 4,2 ms saat 8× beban</text>')

    s.append(footer(w, h, "GAR 113 · scripts/bench.sh · log mentah: docs/benchmarks/raw-2026-11-13.txt"))
    return "".join(s)


def main():
    assets = {
        "hardware.svg": hardware(),
        "psi.svg": psi(),
        "bench.svg": bench(),
    }
    for name, svg in assets.items():
        path = OUT / name
        path.write_text(svg + "\n", encoding="utf-8")
        print(f"{path.relative_to(ROOT)}  {len(svg)/1024:.1f} KB")


if __name__ == "__main__":
    main()
