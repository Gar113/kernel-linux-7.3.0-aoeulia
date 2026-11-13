# PS4 Linux 7.3 kernel — PSI + Darling prerequisites

Kernel build untuk **PlayStation 4 (Aeolia, AMD Jaguar 8-core, 8 GB GDDR5 shared
dengan GPU)** yang menjalankan distro Linux PS4 (root ext4 di `/dev/sda2`).
Repo ini bukan salinan source kernel: isinya hanya skrip build, fragmen config,
config hasil build, dan alat verifikasi — plus rilis `bzImage` yang siap dipasang.

Dua tujuan build:

1. **PSI (Pressure Stall Information)** — supaya `lmkd` Android (Waydroid) bisa
   memakai pressure-based killing, bukan cuma `lowmemorykiller` berbasis ambang.
2. **Prasyarat Darling** (layer kompatibilitas macOS) — namespace, overlayfs
   prefix, `mmap_min_addr=0`, `userfaultfd`, dan kawan-kawannya.

## Hasil build

| Item | Nilai |
|---|---|
| `uname -r` | `7.3.0-Gar113-NoLTO` |
| `uname -v` | `#2 SMP PREEMPT_DYNAMIC Fri Nov 13 13:46:23 WIB 2026` |
| Source | [`striker91n/ps4-linux-7.3`](https://github.com/striker91n/ps4-linux-7.3) commit `f56b8a7c2` (Linux 7.3.0 "Strawberry") |
| Compiler | clang 19.1.7 / LLD 19.1.7 (`LLVM=1`) |
| Target | `-march=btver2 -mtune=btver2 -O3` |
| LTO | none |
| `bzImage` | ±19 MB — `sha256 9c2f74b47aa54d37790b49d9ae9e76c4f3027006386b5906ea81553080c1ca78` |
| `.config` | `e843ef21789e7919df1e29ba83f29a53be7d376c144204801f24d61c63e1a414` |
| Waktu build | ±2 jam, `-j6`, nice 10, di console itu sendiri |

`LOCALVERSION` di-override jadi `-Gar113-NoLTO` (flag `KNAME`), dan `LOCALVERSION=""`
di-export saat build supaya `scripts/setlocalversion` tidak menempelkan `+` pada
tree yang punya perubahan belum di-commit.

## Kenapa PSI

Android memakai PSI untuk `lmkd` (`ro.lmk.psi_compat_mode`, `pressure` di
`lmkd`). Tanpa `CONFIG_PSI`, kernel jatuh ke mode ambang memori lama yang lebih
cepat salah bunuh proses di mesin 8 GB dengan memori dipakai bersama GPU.
Kernel PSI sebelumnya sudah dipakai sejak build 23 Okt 2026; build ini
mempertahankannya.

## Kenapa prasyarat Darling

Darling 0.1+ tidak lagi memakai kernel module: XNU/Mach diemulasi di userspace
(`darlingserver` + `mldr`). Yang tetap butuh dukungan kernel:

- Prefix `~/.darling` = `overlayfs` (lower = `/usr/libexec/darling`, upper = prefix)
  di dalam mount + PID namespace baru → butuh `CONFIG_NAMESPACES` (`*_NS`) dan
  `CONFIG_OVERLAY_FS`, plus `CONFIG_TMPFS_XATTR` kalau upper-nya tmpfs.
- `darlingserver` memakai `memfd_create()` dan `process_vm_readv()`.
- Aplikasi Mach-O lama memetakan segmen `__TEXT` di `0x1000`; dengan
  `mmap_min_addr` default 4096+ muncul error
  `Cannot mmap segment __TEXT at 0x1000: Operation not permitted`.
  Karena itu `CONFIG_DEFAULT_MMAP_MIN_ADDR=0` (lihat catatan keamanan di bawah).
- App 32-bit: `CONFIG_IA32_EMULATION` + `CONFIG_COMPAT_32BIT_TIME`.
- Image/DMG: `CONFIG_FUSE_FS` + `CONFIG_BLK_DEV_LOOP`.

Fragmen config lengkap: [`configs/darling.cfg`](configs/darling.cfg).

### Catatan keamanan

`vm.mmap_min_addr=0` mematikan satu mitigasi (NULL-pointer-deref exploitation di
kernel lama). Di console ini trade-off-nya diterima karena dibutuhkan Darling.
Kalau tidak sedang butuh Darling, bisa dikembalikan runtime:
`sudo sysctl -w vm.mmap_min_addr=4096` (tanpa rebuild).

## Config penting di build ini

| Symbol | Nilai | Alasan |
|---|---|---|
| `CONFIG_PSI` | `y` | `lmkd` Android / Waydroid |
| `CONFIG_PSI_DEFAULT_DISABLED` | `n` | PSI aktif sejak boot |
| `CONFIG_DEFAULT_MMAP_MIN_ADDR` | `0` | Mach-O lama (`__TEXT` di 0x1000) |
| `CONFIG_USERFAULTFD` | `y` | kompat tambahan (sebelumnya mati) |
| `CONFIG_NAMESPACES` + `*_NS`, `CONFIG_OVERLAY_FS` | `y` | prefix Darling |
| `CONFIG_MEMFD_CREATE`, `CONFIG_CROSS_MEMORY_ATTACH`, `CONFIG_KCMP` | `y` | `darlingserver` |
| `CONFIG_BINFMT_MISC`, `CONFIG_SECCOMP_FILTER` | `y` | loader / sandbox |
| `CONFIG_IA32_EMULATION`, `CONFIG_COMPAT_32BIT_TIME` | `y` | app 32-bit |
| `CONFIG_FUSE_FS`, `CONFIG_BLK_DEV_LOOP` | `y` | image / DMG |
| `CONFIG_DEBUG_INFO_BTF` | `y` | dibutuhkan `sched_ext` (`scx_*`) |
| `CONFIG_SCHED_CLASS_EXT` | `y` | scheduler userspace |
| `CONFIG_LRU_GEN` | `y` | multi-gen LRU, penting di 8 GB |
| `CONFIG_ZRAM`, `CONFIG_ZSWAP` | `y` | swap terkompresi |
| `CONFIG_ANDROID_BINDERFS` | `y` | Waydroid |
| `CONFIG_NTSYNC` | `y` | sinkronisasi thread ala Windows (Wine/Proton) |
| `CONFIG_HZ` / `CONFIG_PREEMPT_DYNAMIC` | `250` / `y` | latency vs overhead |
| `CONFIG_DEFAULT_IOSCHED` / `CONFIG_DEFAULT_NET_SCH` | `bfq` / `fq_codel` | storage + jaringan |
| `CONFIG_TCP_CONG_BBR` | `y` | congestion control |

Config hasil build utuh: [`config/kernel-7.3.0-Gar113-NoLTO.config`](config/kernel-7.3.0-Gar113-NoLTO.config).

## Cara build

Butuh source kernel 7.3 di `~/ps4-linux-7.3` (clone `striker91n/ps4-linux-7.3`,
firmware SD8797/MT7668 di `extra_firmware/`), clang/LLD 19, dan ±30 GB disk.

```bash
# default: PSI + Darling, LTO none
./build.sh

# tanpa prasyarat Darling (kernel PSI saja)
DARLING=0 ./build.sh

# nama kernel custom -> uname -r = 7.3.0-<nama>
KNAME="Gar113-NoLTO" ./build.sh

# varian lain
LTO=thin JOBS=8 OUT=~/out LOG=~/build.log ./build.sh
```

Build panjang sebaiknya dijalankan sebagai systemd user unit supaya aman logout:

```bash
systemd-run --user --unit=ps4-kernel-build --collect \
  --property=Nice=10 --property=WorkingDirectory="$HOME" \
  --setenv=DARLING=1 --setenv=KNAME=Gar113-NoLTO \
  --setenv=OUT="$HOME/ps4-build-out" --setenv=LOG="$HOME/ps4-build.log" \
  ./build.sh
```

## Cara pasang (di console)

```bash
sudo mkdir -p /mnt/ps4boot
sudo mount /dev/sda1 /mnt/ps4boot
sudo cp /mnt/ps4boot/bzImage /mnt/ps4boot/bzImage.backup
sudo cp bzImage /mnt/ps4boot/bzImage
sync && sudo umount /mnt/ps4boot
# reboot console
```

Rollback: pasang lagi `bzImage.backup` dari partisi boot, atau pakai backup
kernel sebelumnya + `restore-*.sh`.

## Verifikasi setelah reboot

```bash
./scripts/verify-kernel.sh
```

Cek manual minimal:

```bash
uname -r                      # 7.3.0-Gar113-NoLTO
cat /proc/pressure/memory
sysctl vm.mmap_min_addr       # 0
darling exec /usr/bin/basename /a/b/c.txt   # -> c.txt
```

Bukti dari console yang sama setelah kernel ini dipasang:

- `uname -r` → `7.3.0-Gar113-NoLTO`, `#2 SMP PREEMPT_DYNAMIC`
- `mmap((void*)0x1000, 4096, ...)` → berhasil (sebelumnya `EPERM`)
- `/proc/pressure/{cpu,io,memory}` dan `cgroup memory.pressure` tersedia
- `darling exec /usr/bin/basename /a/b/c.txt` → `c.txt`
- di dalam namespace Darling:
  `overlay on /home/qba/.darling ... lowerdir=/usr/libexec/darling, upperdir=/home/qba/.darling`
- `journalctl -k -b` bersih dari oops/BUG (hanya warning firmware EDID yang sudah ada sebelumnya)

## Catatan / known issues

- **Cold start Darling lambat**: run pertama setelah boot bisa >90 detik
  (launchd start), run berikutnya instan. Bukan hang.
- **`amdgpu: Direct firmware load for edid/my_edid.bin failed`**: EDID custom PS4
  belum ada di `/lib/firmware/edid/`. Tidak fatal kalau display normal.
- **`EXT4-fs (sda2): error count since last fsck: 8`**: error filesystem lama di
  root ext4, perlu fsck saat maintenance (butuh unmount/reboot rescue).
- **Bukan kernel**: Quadra (AppImage Roblox launcher) membawa GTK 4.18.6 yang
  segfault di Wayland native Plasma 6 + mesa 25.1 (`segfault ... in libgtk-4.so.1`).
  Solusinya jalankan lewat XWayland (`GDK_BACKEND=x11`), bukan rebuild kernel.

## Struktur repo

```
build.sh                                  # skrip build (PSI + Darling, KNAME, LTO, OUT/LOG)
configs/darling.cfg                       # fragmen config prasyarat Darling
config/kernel-7.3.0-Gar113-NoLTO.config   # .config hasil build (reproduksi)
scripts/verify-kernel.sh                  # cek PSI + prasyarat Darling di kernel terpasang
```

## Lisensi

Kernel dan turunannya (config, `System.map`, `bzImage`) mengikuti lisensi source
kernel: **GPL-2.0** (dengan pengecualian yang berlaku di tree upstream). Skrip di
repo ini disediakan apa adanya, tanpa garansi.
