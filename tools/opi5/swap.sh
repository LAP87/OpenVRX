#!/usr/bin/env bash
# Driver swap on the Orange Pi, one step at a time with checks, from the laptop over ssh.
#   tools/opi5/swap.sh pstore     crash evidence from the previous boot (/sys/fs/pstore and systemd's archive)
#   tools/opi5/swap.sh prep       state, and start "dmesg -w" into $OPI5_REMOTE/logs/dmesg-live-<time>.txt
#   tools/opi5/swap.sh unload     unload the in-tree rtw89 modules (refuses if the vendor module is loaded)
#   tools/opi5/swap.sh load       insmod the vendor module once, with rtw_la_mode_en=1 (skips if loaded)
#   tools/opi5/swap.sh monitor    set type monitor BEFORE up, bring up, tune 5805 MHz, read the radio state
#   tools/opi5/swap.sh psd        the driver's PSD (returned a flat 101 on 2026-10-27; kept for the record)
#   tools/opi5/swap.sh reboot     clean reboot: the only way to change the vendor build
# Rule since the kernel hang of 2026-10-26 16:55: the vendor module 8852be is never unloaded.
# Env: OPI5_HOST (default opi5), OPI5_LOGD (default ./opi5-logs), OPI5_IF (default wlP4p65s0),
#      OPI5_REMOTE (default /root/openvrx-rtl8852be), OPI5_KO (default $OPI5_REMOTE/src/rtw8852be/8852be.ko)
set -u
HOST="${OPI5_HOST:-opi5}"; LOGD="${OPI5_LOGD:-./opi5-logs}"; IF="${OPI5_IF:-wlP4p65s0}"
REMOTE="${OPI5_REMOTE:-/root/openvrx-rtl8852be}"; KO="${OPI5_KO:-$REMOTE/src/rtw8852be/8852be.ko}"
S() { timeout "${T:-60}" ssh -n -o ConnectTimeout=8 -o BatchMode=yes "$HOST" "$@"; }
R() { local c="$1"; c="${c//__IF__/$IF}"; c="${c//__KO__/$KO}"; c="${c//__REMOTE__/$REMOTE}"; S "$c"; }
step="${1:-}"
run_pstore() {
  echo "== pstore and previous boot"
  S 'echo "boot: $(who -b | sed "s/^ *//")  now: $(date +%H:%M:%S)  up: $(uptime -p)"; echo "-- /sys/fs/pstore"; ls -la /sys/fs/pstore/ 2>&1 | tail -n +2; echo "-- /var/lib/systemd/pstore (archived by systemd-pstore at boot)"; find /var/lib/systemd/pstore -type f 2>/dev/null | head; for f in /sys/fs/pstore/* $(find /var/lib/systemd/pstore -type f 2>/dev/null); do [ -f "$f" ] || continue; echo "---- $f ($(wc -l < "$f") lines)"; grep -n -m4 -E "Oops|BUG|panic|Call trace|rcu_sched|hung task|Unable to handle" "$f" | cut -c1-160; done; echo "-- boots"; journalctl --list-boots --no-pager 2>/dev/null | tail -3; echo "-- previous boot kernel log tail"; journalctl -b -1 -k --no-pager 2>/dev/null | tail -40 | cut -c1-160'
}
run_prep() {
  echo "== prep"
  R 'echo "up $(uptime -p)"; lsmod | grep -E "^(8852be|rtw89)" | cut -c1-50; ps -eo pid,cmd | grep -E "wpa_supplicant|NetworkManager|iwd" | grep -v grep; ip -br link | grep __IF__; mkdir -p __REMOTE__/logs; pkill -x dmesg 2>/dev/null; setsid nohup dmesg -w > __REMOTE__/logs/dmesg-live-$(date +%m%d-%H%M).txt 2>&1 < /dev/null & sleep 1; echo "dmesg -w running: $(pgrep -x dmesg | wc -l)"; sync'
}
run_unload() {
  echo "== unload rtw89 (in-tree driver)"
  R 'if lsmod | grep -q "^8852be"; then echo "8852be is loaded: never unload it, reboot instead"; exit 3; fi; ip link set __IF__ down 2>&1; sleep 1; for m in rtw89_8852be rtw89_8852b rtw89_pci rtw89_core; do modprobe -r $m 2>&1 && echo "removed $m"; done; echo "rtw89 modules left: $(lsmod | grep -c -E "^rtw89")"; dmesg | tail -3 | cut -c1-140; sync'
}
run_load() {
  echo "== load vendor module (once per boot)"
  R 'if lsmod | grep -q "^8852be"; then echo "8852be already loaded"; lsmod | grep "^8852be" | cut -c1-50; exit 0; fi; K=__KO__; ls -la --time-style=+%H:%M:%S $K | cut -c1-120; modinfo $K | grep -E "^vermagic"; insmod $K rtw_la_mode_en=1 2>&1; sleep 6; lsmod | grep -E "^8852be" | cut -c1-50; ip -br link | grep __IF__; dmesg | tail -4 | cut -c1-140; sync'
}
run_monitor() {
  echo "== monitor mode on 5805 (type before up)"
  R 'iw phy | grep -A8 "Supported interface modes" | grep -c monitor; iw dev __IF__ set type monitor 2>&1; sleep 1; ip link set __IF__ up 2>&1; sleep 3; iw dev __IF__ set freq 5805 2>&1; sleep 2; iw dev __IF__ info | grep -E "type|channel" | sed "s/^\s*//"; head -1 /proc/net/rtl8852be/__IF__/rf_info 2>&1; cat /proc/net/rtl8852be/__IF__/monitor 2>&1; dmesg | tail -5 | cut -c1-140; sync'
}
run_psd() {
  echo "== PSD at ch 161"
  T=90 R 'P=/proc/net/rtl8852be/__IF__/odm/phl_cmd; echo "bb psd 0 1 3 2 512 0 0 161 0" > $P; head -3 $P | cut -c1-120; echo "bb psd 1 0 0 511" > $P; head -140 $P | cut -c1-160'
}
run_reboot() {
  echo "== clean reboot (the only way to change the vendor build)"
  S 'sync; systemctl reboot' 2>&1; echo "reboot requested $(date +%H:%M:%S)"
}
mkdir -p "$LOGD"
case "$step" in
  pstore|prep|unload|load|monitor|psd|reboot) "run_$step" 2>&1 | tee -a "$LOGD/opi5-swap-$(date +%Y%m%d)-$step.txt" ;;
  *) echo "usage: swap.sh pstore|prep|unload|load|monitor|psd|reboot"; exit 2 ;;
esac
