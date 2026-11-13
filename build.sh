#!/usr/bin/env bash
# Build PS4-Linux "Strawberry" kernel for Aeolia with PSI enabled (for Android lmkd)
# and optional Darling (macOS layer) prerequisites.
# Source: https://github.com/striker91n/ps4-linux-7.3
# Author: GAR 113 (https://github.com/Gar113)
# Usage: [LTO=none|thin] [DARLING=0|1] [KNAME="custom-name"] ./ps4-kernel-build.sh
#   KNAME overrides the version suffix, e.g. KNAME="Gar113-NoLTO" -> uname -r
#   becomes "7.3.0-Gar113-NoLTO" (PSI/Darling tags are dropped in that case).
set -euo pipefail

SRC=/home/qba/ps4-linux-7.3
OUT="${OUT:-/home/qba/ps4-build-out}"
LOG="${LOG:-/home/qba/ps4-build.log}"
JOBS="${JOBS:-6}"
LTO="${LTO:-none}"
DARLING="${DARLING:-1}"
KNAME="${KNAME:-}"

case "$LTO" in
    thin) LTO_CFG=configs/lto-thin.cfg; LTO_LABEL=ThinLTO ;;
    none|nolto) LTO_CFG=configs/lto-none.cfg; LTO_LABEL=NoLTO ;;
    *) echo "LTO must be none|thin"; exit 1 ;;
esac

cd "$SRC"
[ -f Makefile ] && grep -q KERNELRELEASE Makefile || { echo "source not ready"; exit 1; }

mkdir -p "$OUT"

export KCFLAGS="-march=btver2 -mtune=btver2 -O3"
export KAFLAGS="-march=btver2 -mtune=btver2"
export HOSTCFLAGS="-Wno-error=incompatible-pointer-types-discards-qualifiers"
# LOCALVERSION set (even to an empty value) stops scripts/setlocalversion from
# appending "+" for a tree with uncommitted changes, so `uname -r` matches
# CONFIG_LOCALVERSION exactly.
export LOCALVERSION=""

cp -f config .config

apply_cfg() {
    local f="$1" action name value
    while read -r action name value; do
        [[ -z "$action" || "$action" == \#* ]] && continue
        case "$action" in
            enable)  scripts/config --enable  "$name" ;;
            disable) scripts/config --disable "$name" ;;
            set-val) scripts/config --set-val "$name" "$value" ;;
            set-str) scripts/config --set-str "$name" "$value" ;;
        esac
    done < "$f"
}

echo "[*] applying $LTO_LABEL + base + General profile"
apply_cfg "$LTO_CFG"
if [ "$LTO_LABEL" = NoLTO ]; then
    # configs/lto-none.cfg only turns off THIN/FULL; the Kconfig choice then falls
    # through to LTO_CLANG_THIN_DIST. Force LTO_NONE explicitly.
    scripts/config --enable  CONFIG_LTO_NONE
    scripts/config --disable CONFIG_LTO_CLANG
    scripts/config --disable CONFIG_LTO_CLANG_THIN_DIST
    scripts/config --disable CONFIG_LTO
fi
scripts/config --disable CONFIG_LOCALVERSION_AUTO
apply_cfg configs/base.cfg
apply_cfg configs/tuning-general.cfg

# Version suffix shown by `uname -r`. KNAME wins over the auto-generated tag.
LV="-Strawberry-General-${LTO_LABEL}-PSI"
[ "$DARLING" = "1" ] && LV="$LV-Darling"
[ -n "$KNAME" ] && LV="-$KNAME"
scripts/config --set-str CONFIG_LOCALVERSION "$LV"

echo "[*] forcing PSI on (overrides tuning-general) and trimming build cost"
scripts/config --enable  CONFIG_PSI
scripts/config --disable CONFIG_PSI_DEFAULT_DISABLED
scripts/config --disable CONFIG_WERROR

if [ "$DARLING" = "1" ]; then
    echo "[*] applying Darling (macOS layer) prerequisites"
    apply_cfg configs/darling.cfg
fi
# BTF wajib: SCHED_CLASS_EXT (sched_ext / scx_*) butuh DEBUG_INFO_BTF, dan
# EXT_GROUP_SCHED + EXT_SUB_SCHED bergantung pada SCHED_CLASS_EXT.
scripts/config --enable  CONFIG_DEBUG_INFO
scripts/config --enable  CONFIG_DEBUG_INFO_BTF
scripts/config --disable CONFIG_DEBUG_INFO_BTF_MODULES

echo "[*] embedding required PS4 SD8797 firmware"
scripts/config --set-str CONFIG_EXTRA_FIRMWARE_DIR "$SRC/extra_firmware"
cur="$(sed -n 's/^CONFIG_EXTRA_FIRMWARE="\(.*\)"/\1/p' .config || true)"
case " $cur " in
    *" mrvl/sd8797_uapsta.bin "*) ;;
    *) scripts/config --set-str CONFIG_EXTRA_FIRMWARE "${cur:+$cur }mrvl/sd8797_uapsta.bin" ;;
esac

echo "[*] olddefconfig"
make LLVM=1 ARCH=x86_64 HOSTCFLAGS="$HOSTCFLAGS" olddefconfig

grep -q '^CONFIG_PSI=y' .config || { echo "ERROR: CONFIG_PSI did not survive olddefconfig"; exit 1; }
grep -q '^CONFIG_ANDROID_BINDERFS=y' .config || { echo "ERROR: binderfs missing"; exit 1; }
if [ "$DARLING" = "1" ]; then
    grep -q '^CONFIG_USERFAULTFD=y' .config || { echo "ERROR: USERFAULTFD missing"; exit 1; }
    grep -q '^CONFIG_OVERLAY_FS=y' .config || { echo "ERROR: overlayfs missing"; exit 1; }
    grep -q '^CONFIG_DEFAULT_MMAP_MIN_ADDR=0$' .config || { echo "ERROR: mmap_min_addr not 0"; exit 1; }
fi
echo "[*] PSI=$(grep '^CONFIG_PSI=' .config)  LOCALVERSION=$(grep '^CONFIG_LOCALVERSION=' .config)  LTO=$(grep -E '^CONFIG_LTO_CLANG_(THIN|FULL)=|^# CONFIG_LTO is not set' .config | tr '\n' ' ')"

cp .config "$OUT/.config"
echo "[*] building bzImage with -j$JOBS (nice)"
nice -n 10 make LLVM=1 ARCH=x86_64 HOSTCFLAGS="$HOSTCFLAGS" -j"$JOBS" bzImage 2>&1 | tee "$LOG"

cp arch/x86/boot/bzImage "$OUT/bzImage"
cp .config "$OUT/.config"
cp System.map "$OUT/System.map" 2>/dev/null || true
echo "[*] done: $OUT/bzImage"
ls -lh "$OUT/bzImage"
