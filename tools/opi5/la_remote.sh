#!/usr/bin/env bash
# Runs ON the Orange Pi (copied there by la.sh). Drives the halbb logic-analyser (LA) capture of the vendor
# driver lwfinger/rtw8852be through /proc/net/rtl8852be/<iface>/odm/phl_cmd and tunes the monitor interface.
#
#   check                        where the PSD output went and the LA enums in the driver source
#   chan <MHz> [bw] [centre]     retune: plain 20 MHz channel (LO = centre) or a 40/80 MHz block
#   cap2 [buf] [rate] [tov]      one trigger-less capture: the MAC timeout (1 s << tov) stops the ring capture,
#                                then "get {finish_ofst} {round_up}" and "print 0" dump it to dmesg
#   cap20 <MHz> [rate]           chan + one capture named la-ch<MHz>-<time>.txt, with the power per field
#   sweep [rate] [tov]           one capture per block over 5490-5835 MHz, power per block (la-sweep-*)
#   cad <N> [rate] [mode] [tt]   N captures back to back with timing per step (mode tmo | cca | bb:<bit>,
#                                tt = trigger time in us, 404 fills the 64 KiB buffer at 20 MHz)
#   dbg <hex> [rate]             one timeout capture with that debug port (its bits 31..16 land in bits 63..48)
#
# Rate index (LA clock): 0 = 80 MHz, 1 = 40 (unreliable timing, do not use), 2 = 20, 3 = 10, 4 = 5, 5 = 2.5,
# 6 = 1.25, 7 = 160 MHz. Lower clocks decimate WITHOUT filtering: keep the signal inside the channel.
# Needs a dmesg -w writing to $LOGS/dmesg-live-*.txt (swap.sh prep starts it). Measured on hardware 2026-10-27.
set -u
IF="${OPI5_IF:-wlP4p65s0}"
BASE="${REMOTE:-/root/openvrx-rtl8852be}"
P=/proc/net/rtl8852be/$IF/odm/phl_cmd
SRC=$BASE/src/rtw8852be
LOGS=$BASE/logs
live() { ls -t "$LOGS"/dmesg-live-*.txt 2>/dev/null | head -1; }
cmd() { echo "$1" > "$P"; sleep "${2:-0.5}"; head -"${3:-12}" "$P" | cut -c1-170; }
tune() { # tune <control MHz> [bw] [centre]
  local fq=$1 bw=${2:-} c=${3:-}
  if [ -n "$bw" ] && [ "$bw" != 20 ]; then iw dev "$IF" set freq "$fq" "$bw" $c 2>&1; else iw dev "$IF" set freq "$fq" 2>&1; fi
  sleep 1.5; iw dev "$IF" info | grep -E "channel" | sed "s/^\s*//"; head -1 "/proc/net/rtl8852be/$IF/rf_info"
}
do_cap() { # do_cap <buf> <rate_idx> <timeout_idx> <file name under logs/> [quiet]
  local buf=$1 rate=$2 tov=$3 out=$LOGS/$4 quiet=${5:-} f n0 line ofst ru i
  f=$(live); [ -n "$f" ] || { echo "no dmesg-live file under $LOGS: run swap.sh prep first"; return 1; }
  n0=$(wc -l < "$f")
  new() { sed -n "$((n0+1)),\$p" "$f"; }
  q() { if [ -z "$quiet" ]; then cat; else cat > /dev/null; fi; }
  { echo "-- reset"; cmd "bb lamode reset" 0.5 3; echo "-- buf $buf"; cmd "bb lamode buf $buf"
    echo "-- cmn 404 0 10205 0 $rate"; cmd "bb lamode cmn 404 0 10205 0 $rate" 0.3 3
    echo "-- tmac 1 $tov"; cmd "bb lamode tmac 1 $tov" 0.3 3; echo "-- trig"; cmd "bb lamode trig" 2 30; } | q
  line=$(new | grep 'rpt=((0x3))' | tail -1)
  ofst=$(echo "$line" | sed -n 's/.*finish_ofst =((\([0-9]*\))).*/\1/p'); ru=$(echo "$line" | sed -n 's/.*round_up =((\([01]\))).*/\1/p')
  if [ -z "$ofst" ]; then echo "no LA_HW_FINISH_TIMEOUT state seen; last poll lines:"; new | grep 'rpt=' | tail -3 | cut -c1-150; return 1; fi
  { echo "-- get $ofst $ru"; cmd "bb lamode get $ofst $ru" 2 10; echo "-- print 0"; cmd "bb lamode print 0" 2 6; } | q
  for i in $(seq 1 90); do [ "$(new | grep -c 'Dump_End')" -ge 2 ] && break; sleep 1; done
  sleep 1; new > "$out"
  echo "saved $out: $(grep -c -E '\][0-9a-f]{16}$' "$out") hex lines (timeout ofst $ofst ru $ru)"
}
one_cap() { # one_cap <mode> <rate_idx> <file name under logs/>; mode tmo | cca | bb:<bit>. One timing line per capture:
  # wall-clock trig / get / print, the kernel timestamps of the stop and the last Dump_End, and the word count.
  local mode=$1 rate=$2 name=$3 out=$LOGS/$3 f n0 line st ofst ru i ta tb tc td kstop kdump hex dbgp
  f=$(live); [ -n "$f" ] || { echo "no dmesg-live file under $LOGS: run swap.sh prep first"; return 1; }
  n0=$(wc -l < "$f")
  new() { sed -n "$((n0+1)),\$p" "$f"; }
  echo "bb lamode reset" > "$P"; echo "bb lamode buf 0" > "$P"
  case "$mode" in
    tmo) dbgp=${DBGP:-10205}; echo "bb lamode cmn ${TT:-404} 0 $dbgp 0 $rate" > "$P"; echo "bb lamode tmac 1 0" > "$P" ;;
    cca) dbgp=${DBGP:-10205}; echo "bb lamode cmn ${TT:-404} 0 $dbgp 0 $rate" > "$P"; echo "bb lamode tmac 0 0" > "$P"; echo "bb lamode mac 0 1 0 0" > "$P" ;;
    bb:*) dbgp=${DBGP:-2002}; echo "bb lamode cmn ${TT:-404} 0 $dbgp 0 $rate" > "$P"; echo "bb lamode tmac 0 0" > "$P"; echo "bb lamode bb 0 0 ${mode#bb:}" > "$P" ;;
    *) echo "unknown mode $mode"; return 2 ;;
  esac
  ta=$(date +%s.%N); echo "bb lamode trig" > "$P"; tb=$(date +%s.%N)
  line=$(new | grep -E 'rpt=\(\(0x[23]\)\)' | tail -1)
  st=$(echo "$line" | sed -n 's/.*rpt=((0x\([23]\))).*/\1/p')
  if [ "$st" = 3 ]; then
    ofst=$(echo "$line" | sed -n 's/.*finish_ofst =((\([0-9]*\))).*/\1/p'); ru=$(echo "$line" | sed -n 's/.*round_up =((\([01]\))).*/\1/p')
    echo "bb lamode get $ofst $ru" > "$P"
  fi
  tc=$(date +%s.%N)
  if [ -z "$st" ]; then echo "$name mode=$mode: no stop state; polls=$(new | grep -c 'rpt=') last=$(new | grep 'rpt=' | tail -1 | cut -c1-90)"; new > "$out"; return 1; fi
  echo "bb lamode print 0" > "$P"; td=$(date +%s.%N)
  for i in $(seq 1 100); do [ "$(new | grep -c 'Dump_End')" -ge 2 ] && break; sleep 0.1; done
  new > "$out"
  kstop=$(grep -m1 -E 'LA HW timeout|LA Query OK' "$out" | sed -n 's/^\[ *\([0-9.]*\)\].*/\1/p')
  kdump=$(grep 'Dump_End' "$out" | tail -1 | sed -n 's/^\[ *\([0-9.]*\)\].*/\1/p')
  hex=$(grep -c -E '\][0-9a-f]{16}$' "$out")
  awk -v n="$name" -v m="$mode" -v s="$st" -v a="$ta" -v b="$tb" -v c="$tc" -v d="$td" -v ks="$kstop" -v kd="$kdump" -v h="$hex" \
    'BEGIN{printf "%s mode=%s state=0x%s trig=%.3f get=%.3f print=%.3f total=%.3f kstop=%s kdump=%s hex=%d\n", n, m, s, b-a, c-b, d-c, d-a, ks, kd, h}'
}
power() { # power <capture file>: standard deviation of the four 12-bit fields (noise is about 35-55)
  python3 - "$1" <<'PY'
import re, sys, statistics as st
pat = re.compile(r'\[BB\]([0-9a-f]{16})\s*$')
w = [int(m.group(1), 16) for m in (pat.search(l) for l in open(sys.argv[1], errors='replace')) if m]
def s12(v): return v - 4096 if v & 0x800 else v
sd = [st.pstdev([s12(x >> s & 0xfff) for x in w]) for s in (0, 12, 24, 36)]
print('   n=%d  sd f0..f3 = %.0f %.0f %.0f %.0f' % (len(w), *sd))
PY
}
case "${1:-}" in
  check)
    f=$(live); echo "== $f: $(wc -l < "$f") lines; psd/BB lines:"; grep -n -i -E "psd|\[BB\]|halbb" "$f" | tail -30 | cut -c1-170
    echo "== proc buffer now"; head -40 "$P" | cut -c1-170
    echo "== enums"; grep -n -A12 -E "enum la_smp_clk|enum la_dma_sel|enum la_dma_type|enum la_dma_data_type|enum la_buf" "$SRC/phl/hal_g6/phy/bb/halbb_la_mode.h" | cut -c1-110 | head -80
    ;;
  cap2) do_cap "${2:-0}" "${3:-0}" "${4:-0}" "la-cap-$(date +%m%d-%H%M%S).txt" ;;
  chan) tune "${2:-5805}" "${3:-}" "${4:-}"; dmesg | tail -2 | cut -c1-140 ;;
  sweep)
    rate="${2:-0}"; tov="${3:-0}"
    for e in "5500 80 5530" "5580 80 5610" "5660 80 5690" "5745 80 5775" "5805 40 5815"; do
      set -- $e; echo "== block $2 MHz centred $3: $(tune "$1" "$2" "$3" | tail -1)"
      name="la-sweep-$(date +%m%d-%H%M%S)-c$3.txt"
      do_cap 0 "$rate" "$tov" "$name" quiet && power "$LOGS/$name"
    done
    ;;
  cap20)
    fq="${2:-5805}"; rate="${3:-2}"; echo "== ch $fq MHz: $(tune "$fq" | tail -1)"
    name="la-ch$fq-$(date +%m%d-%H%M%S).txt"; do_cap 0 "$rate" 0 "$name" quiet && power "$LOGS/$name"
    ;;
  cad)
    N="${2:-8}"; rate="${3:-2}"; mode="${4:-tmo}"; export TT="${5:-${TT:-404}}"; tag=$(date +%m%d-%H%M%S)
    echo "== cadence: $N captures, rate idx $rate, mode $mode, trig time $TT us, tag $tag, $(date +%H:%M:%S)"
    for i in $(seq 1 "$N"); do one_cap "$mode" "$rate" "la-cad-$tag-$mode-$(printf %02d "$i").txt"; done
    ;;
  dbg) DBGP="${2:-2002}" one_cap tmo "${3:-2}" "la-dbg-${2:-2002}-$(date +%m%d-%H%M%S).txt" ;;
  *) echo "usage: la_remote.sh check|chan <MHz> [bw] [centre]|cap2 [buf] [rate] [tov]|cap20 <MHz> [rate]|sweep [rate] [tov]|cad <N> [rate] [mode] [tt]|dbg <hex> [rate]"; exit 2 ;;
esac
