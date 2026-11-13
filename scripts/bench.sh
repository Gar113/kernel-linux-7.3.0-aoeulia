#!/usr/bin/env bash
# Benchmark suite untuk PS4 Linux 7.3.0-Gar113-NoLTO.
# Semua hasil ditulis ke satu file teks (default: ~/ps4-bench-<tanggal>.txt).
#
#   ./scripts/bench.sh                 # semua tes (CPU, memori, disk, latency, PSI, GPU)
#   QUICK=1 ./scripts/bench.sh         # tanpa disk + GPU
#   OUT=/path/hasil.txt ./scripts/bench.sh
#
# Butuh: fio, openssl, 7z, zstd, python3, glxinfo/glmark2/vkmark (kalau ada).
set -uo pipefail

OUT="${OUT:-$HOME/ps4-bench-$(date +%F).txt}"
QUICK="${QUICK:-0}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
exec > >(tee "$OUT") 2>&1

have() { command -v "$1" >/dev/null 2>&1; }
sec()  { printf '\n\n===== %s =====\n' "$*"; }
note() { printf '  %s\n' "$*"; }

cfg() {
  local src=""
  if [ -r /proc/config.gz ]; then
    src="$(zcat /proc/config.gz)"
  elif [ -r "$HOME/ps4-build-out-darling/.config" ]; then
    src="$(cat "$HOME/ps4-build-out-darling/.config")"
  fi
  case "$src" in
    *"$1="*) printf '%s\n' "$src" | grep -E "^$1=" | head -1 | cut -d= -f2 ;;
    *"# $1 is not set"*) printf 'n\n' ;;
    *) printf '?\n' ;;
  esac
}

cpu_model="$(lscpu 2>/dev/null | awk -F': *' '/Model name/{print $2; exit}')"
cpu_mhz="$(lscpu 2>/dev/null | awk -F': *' '/CPU max MHz/{print $2; exit}')"

cat <<EOF
PS4 Linux benchmark
tanggal   : $(date -Is)
kernel    : $(uname -r)
build     : $(uname -v)
mesin     : ${cpu_model:-?} @ ${cpu_mhz:-?} MHz, $(nproc) thread
memori    : $(awk '/MemTotal/{printf "%.1f GiB", $2/1048576}' /proc/meminfo) total, $(awk '/SwapTotal/{printf "%.1f GiB", $2/1048576}' /proc/meminfo) swap
cmdline   : $(cat /proc/cmdline)
catatan   : hasil mentah, angka bisa beda tergantung suhu/background load
EOF

# ------------------------------------------------------------------ config
sec "config kernel (fitur yang diuji)"
for s in CONFIG_PSI CONFIG_PSI_DEFAULT_DISABLED CONFIG_DEFAULT_MMAP_MIN_ADDR \
         CONFIG_LRU_GEN CONFIG_ZRAM CONFIG_ZSWAP CONFIG_ANDROID_BINDERFS \
         CONFIG_NTSYNC CONFIG_SCHED_CLASS_EXT CONFIG_DEBUG_INFO_BTF \
         CONFIG_PREEMPT_DYNAMIC CONFIG_HZ CONFIG_HIGH_RES_TIMERS CONFIG_IO_URING \
         CONFIG_OVERLAY_FS CONFIG_USERFAULTFD CONFIG_TCP_CONG_BBR \
         CONFIG_IOSCHED_BFQ CONFIG_DEFAULT_NET_SCH; do
  note "$s=$(cfg "$s")"
done
note "psi        : $(ls /proc/pressure | tr '\n' ' ')"
note "zram       : $(zramctl --noheadings --output NAME,ALGORITHM,DISKSIZE,DATA,COMPR 2>/dev/null | tr -s ' ')"
note "zswap      : $(cat /sys/module/zswap/parameters/enabled 2>/dev/null || echo n/a)"
note "sched_ext  : $(cat /sys/kernel/sched_ext/state 2>/dev/null || echo n/a)"
note "mmap_min   : $(sysctl -n vm.mmap_min_addr 2>/dev/null)"
note "governor   : $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo n/a)"
note "clocksource: $(cat /sys/devices/system/clocksource/clocksource0/current_clocksource 2>/dev/null)"
note "btf        : $([ -e /sys/kernel/btf/vmlinux ] && echo ada || echo tidak)"

# ------------------------------------------------------------------ CPU
sec "CPU"
if have openssl; then
  note "openssl speed, 2 detik per algo (angka = 1000 byte/detik)"
  for algo in aes-256-gcm sha256 chacha20-poly1305; do
    line="$(openssl speed -seconds 2 -evp "$algo" 2>/dev/null | grep -iE "^${algo}[[:space:]]" | tail -1)"
    note "${line:-$algo: gagal}"
  done
fi
if have 7z; then
  note "7z b -mmt$(nproc) (MIPS total)"
  7z b -mmt"$(nproc)" 2>/dev/null | grep -E "Tot:|Avr:|Kernel|7-Zip" | sed 's/^/  /'
fi
if have zstd; then
  note "zstd -b3 / -b19 (MB/s)"
  zstd -b3 -i2 -q 2>&1 | sed 's/^/  /'
  zstd -b19 -i2 -q 2>&1 | sed 's/^/  /'
fi

# ------------------------------------------------------------------ memori
sec "memori"
note "dd /dev/zero -> /dev/null, bs=1M x 4096"
dd if=/dev/zero of=/dev/null bs=1M count=4096 2>&1 | tail -1 | sed 's/^/  /'
if have fio; then
  note "fio tmpfs (/dev/shm) 512M, bs=1M"
  fio --name=ram-read --filename=/dev/shm/fio-bench --size=512M --rw=read \
      --bs=1M --ioengine=psync --direct=0 --runtime=5 --time_based \
      --output-format=json --output="$TMP/ram.json" >/dev/null 2>&1
  fio --name=ram-write --filename=/dev/shm/fio-bench --size=512M --rw=write \
      --bs=1M --ioengine=psync --direct=0 --runtime=5 --time_based \
      --output-format=json --output="$TMP/ramw.json" >/dev/null 2>&1
  rm -f /dev/shm/fio-bench
  python3 - "$TMP/ram.json" "$TMP/ramw.json" <<'PY'
import json, sys
for path, label in ((sys.argv[1], "read "), (sys.argv[2], "write")):
    try:
        j = json.load(open(path))["jobs"][0]
        bw = j.get(label.strip(), {}).get("bw", 0) / 1024
        print(f"  tmpfs {label}: {bw:8.1f} MiB/s")
    except Exception as e:
        print(f"  tmpfs {label}: gagal ({e})")
PY
fi

# ------------------------------------------------------------------ disk
if [ "$QUICK" = "0" ] && have fio; then
  sec "disk (root ext4, HGST HTS545050A7E680 5400rpm)"
  note "rotational: $(cat /sys/block/sda/queue/rotational 2>/dev/null)   scheduler: $(cat /sys/block/sda/queue/scheduler 2>/dev/null)"
  D="$HOME/.fio-bench"
  fio --name=prep --filename="$D" --size=512M --rw=write --bs=1M --ioengine=psync \
      --direct=1 --output-format=json --output="$TMP/prep.json" >/dev/null 2>&1
  note "file uji: $(du -h "$D" 2>/dev/null | cut -f1) (prep 512M, direct=1)"
  for spec in "seqread:read:1M:1:psync" "seqwrite:write:1M:1:psync" \
              "randread:randread:4k:16:libaio" "randwrite:randwrite:4k:16:libaio"; do
    IFS=: read -r name rw bs qd eng <<<"$spec"
    fio --name="$name" --filename="$D" --size=512M --rw="$rw" --bs="$bs" --iodepth="$qd" \
        --ioengine="$eng" --direct=1 --runtime=6 --time_based \
        --output-format=json --output="$TMP/$name.json" >/dev/null 2>&1
    python3 - "$TMP/$name.json" "$name" <<'PY'
import json, sys
try:
    j = json.load(open(sys.argv[1]))["jobs"][0]
    parts = []
    for side in ("read", "write"):
        d = j.get(side, {})
        if d.get("bw", 0) > 0:
            p99 = d.get("clat_ns", {}).get("percentile", {}).get("99.000000", 0) / 1e6
            parts.append(f"{side} {d['bw']/1024:7.1f} MiB/s {d['iops']:7.0f} IOPS "
                         f"lat p99 {p99:6.2f} ms")
    print(f"  {sys.argv[2]:<10} " + "   ".join(parts))
except Exception as e:
    print(f"  {sys.argv[2]:<10} gagal ({e})")
PY
  done
  rm -f "$D"
fi

# ------------------------------------------------------------------ latency
sec "latency / timer granularity (HZ=$(cfg CONFIG_HZ))"
python3 - <<'PY'
import time
for target in (0.0005, 0.001, 0.002, 0.005, 0.010):
    d = []
    for _ in range(400):
        t0 = time.perf_counter_ns()
        time.sleep(target)
        d.append((time.perf_counter_ns() - t0) / 1000)
    d.sort()
    print(f"  sleep({target*1000:5.1f} ms): p50 {d[len(d)//2]:6.0f} us  "
          f"p99 {d[int(len(d)*0.99)]:6.0f} us  max {d[-1]:6.0f} us")
PY
note "jitter sleep(1 ms) saat idle vs 8x beban CPU"
python3 - <<'PY'
import statistics, time
n = 2000
d = []
for _ in range(n):
    t0 = time.perf_counter_ns()
    time.sleep(0.001)
    d.append((time.perf_counter_ns() - t0) / 1000)
d.sort()
q = lambda p: d[min(len(d) - 1, int(len(d) * p))]
print(f"  idle   : avg {statistics.mean(d):6.0f} us  p50 {q(.5):5.0f}  p95 {q(.95):5.0f} "
      f"p99 {q(.99):5.0f}  max {d[-1]:6.0f} us")
PY
for _ in $(seq 1 "$(nproc)"); do (timeout 25 yes >/dev/null &) ; done
sleep 1
python3 - <<'PY'
import statistics, time
n = 2000
d = []
for _ in range(n):
    t0 = time.perf_counter_ns()
    time.sleep(0.001)
    d.append((time.perf_counter_ns() - t0) / 1000)
d.sort()
q = lambda p: d[min(len(d) - 1, int(len(d) * p))]
print(f"  load 8 : avg {statistics.mean(d):6.0f} us  p50 {q(.5):5.0f}  p95 {q(.95):5.0f} "
      f"p99 {q(.99):5.0f}  max {d[-1]:6.0f} us")
PY
pkill -x yes 2>/dev/null

# ------------------------------------------------------------------ PSI
sec "PSI: tekanan CPU (16 proses yes) dan memori (alokasi 2 GiB)"
python3 - <<'PY'
import mmap, subprocess, time

def psi(kind):
    out = {}
    for line in open(f"/proc/pressure/{kind}"):
        f = line.split()
        out[f[0]] = f[1]
    return out

def avg10(kind, key="some"):
    return float(psi(kind)[key].split("=")[1])

def vmstat(key):
    for line in open("/proc/vmstat"):
        if line.startswith(key + " "):
            return int(line.split()[1])
    return 0

print(f"  cpu    sebelum load      : some avg10={avg10('cpu'):5.2f}")
procs = [subprocess.Popen(["yes"], stdout=subprocess.DEVNULL) for _ in range(16)]
peak = 0.0
for _ in range(10):
    time.sleep(0.5)
    peak = max(peak, avg10("cpu"))
for p in procs:
    p.terminate()
print(f"  cpu    puncak saat load : some avg10={peak:5.2f}")
time.sleep(1)

swap_in, swap_out = vmstat("pswpin"), vmstat("pswpout")

def avail():
    for line in open("/proc/meminfo"):
        if line.startswith("MemAvailable"):
            return int(line.split()[1]) * 1024

print(f"  memori sebelum alokasi  : some avg10={avg10('memory'):5.2f}  "
      f"avail {avail()/1024**2:.0f} MiB")
size = 4 * 1024 ** 3
chunk = 64 * 1024 ** 2
m = mmap.mmap(-1, size)
alloc = 0
peak = 0.0
t0 = time.time()
while alloc < size and avail() > 400 * 1024 ** 2:
    for off in range(alloc, alloc + chunk, 4096):
        m[off] = 1
    alloc += chunk
    peak = max(peak, avg10("memory"))
for _ in range(4):
    time.sleep(0.5)
    peak = max(peak, avg10("memory"))
t_alloc = time.time() - t0
print(f"  alokasi                 : {alloc/1024**3:.2f} GiB dalam {t_alloc:.1f} s "
      f"({alloc/t_alloc/1024**2:.0f} MiB/s), sisa avail {avail()/1024**2:.0f} MiB")
print(f"  memori puncak avg10     : some {peak:5.2f}  full {avg10('memory','full'):5.2f}")
print(f"  swap                    : in {vmstat('pswpin') - swap_in} hal, "
      f"out {vmstat('pswpout') - swap_out} hal")
m.close()
PY

# ------------------------------------------------------------------ GPU
if [ "$QUICK" = "0" ]; then
  sec "GPU (radeonsi liverpool, mesa)"
  if have glxinfo; then
    DISPLAY="${DISPLAY:-:1}" glxinfo -B 2>/dev/null | grep -E "Device|Version|Accelerated|Video memory|core profile" | sed 's/^/  /'
  fi
  if have glmark2; then
    note "glmark2 1280x720, 5 scene x 3 detik (XWayland)"
    DISPLAY="${DISPLAY:-:1}" timeout 300 glmark2 -s 1280x720 \
      -b build:duration=3 -b texture:duration=3 -b shading:duration=3 \
      -b jellyfish:duration=3 -b terrain:duration=3 2>/dev/null \
      | grep -E "FPS|glmark2 Score" | sed 's/^/  /'
  fi
  if have vkmark; then
    note "vkmark 1280x720, 3 scene x 3 detik (Wayland)"
    timeout 300 vkmark --size 1280x720 -b vertex:duration=3 -b texture:duration=3 \
      -b shading:duration=3 2>/dev/null | grep -E "FPS|Score|s:" | sed 's/^/  /'
  fi
fi

sec "selesai"
note "hasil mentah: $OUT"
