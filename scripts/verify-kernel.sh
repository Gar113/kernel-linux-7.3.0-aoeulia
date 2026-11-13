#!/usr/bin/env bash
# Verify that the installed kernel has PSI and the Darling prerequisites this
# repo builds for. Run on the PS4 after installing bzImage and rebooting.
set -uo pipefail

ok()   { printf '  \033[32mOK\033[0m   %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; }
info() { printf '       %s\n' "$1"; }
fail=0

echo "== kernel =="
info "uname -r : $(uname -r)"
info "uname -v : $(uname -v)"
case "$(uname -r)" in
    *Gar113-NoLTO) ok "kernel version string sesuai build" ;;
    *) bad "kernel version string bukan 7.3.0-Gar113-NoLTO (kernel lama masih terpasang?)"; fail=1 ;;
esac

echo "== PSI (pressure stall information) =="
if [ -r /proc/pressure/cpu ] && [ -r /proc/pressure/io ] && [ -r /proc/pressure/memory ]; then
    ok "/proc/pressure/{cpu,io,memory} tersedia"
    info "$(head -1 /proc/pressure/memory)"
else
    bad "/proc/pressure tidak lengkap"; fail=1
fi
[ -r /sys/fs/cgroup/memory.pressure ] && ok "cgroup v2 memory.pressure tersedia" || bad "memory.pressure tidak ada"

echo "== Darling prerequisites =="
for s in namespaces binfmt_misc binderfs; do :; done
check_sysctl() { # name expected
    local cur; cur="$(sysctl -n "$1" 2>/dev/null || echo '?')"
    if [ "$cur" = "$2" ]; then ok "$1 = $cur"; else bad "$1 = $cur (harusnya $2)"; fail=1; fi
}
check_sysctl vm.mmap_min_addr 0
info "vm.max_map_count = $(sysctl -n vm.max_map_count 2>/dev/null)"

# mmap at 0x1000: the exact case that breaks old Mach-O binaries.
low_test=/tmp/lowmmap.$$
if command -v gcc >/dev/null; then
    cat > "$low_test.c" <<'EOF'
#include <sys/mman.h>
#include <stdio.h>
int main(void) {
    void *p = mmap((void *)0x1000, 4096, PROT_READ | PROT_WRITE,
                   MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    return p == MAP_FAILED;
}
EOF
    if gcc -o "$low_test" "$low_test.c" 2>/dev/null && "$low_test"; then
        ok "mmap() di alamat 0x1000 berhasil"
    else
        bad "mmap() di 0x1000 gagal (mmap_min_addr belum 0?)"; fail=1
    fi
    rm -f "$low_test" "$low_test.c"
else
    info "gcc tidak ada, tes mmap 0x1000 dilewati"
fi

if [ -d /sys/fs/cgroup ]; then
    grep -q overlay /proc/filesystems && ok "overlayfs didukung" || bad "overlayfs tidak ada"
fi

echo "== Darling runtime (opsional) =="
if command -v darling >/dev/null; then
    if out="$(timeout 180 darling exec /usr/bin/basename /a/b/c.txt 2>&1 | tail -1)" && [ "$out" = "c.txt" ]; then
        ok "darling exec menjalankan binary Mach-O"
    else
        info "darling exec belum siap (cold start launchd bisa >90 detik); coba lagi manual:"
        info "darling exec /usr/bin/basename /a/b/c.txt"
    fi
else
    info "Darling tidak terpasang, bagian ini dilewati"
fi

echo
if [ "$fail" = "0" ]; then
    echo "Semua cek wajib lolos."
else
    echo "Ada cek yang gagal — lihat baris FAIL di atas."
fi
exit "$fail"
