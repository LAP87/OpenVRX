#!/usr/bin/env bash
# Capture cadence: N back-to-back captures on the Pi, then the stop-to-stop intervals from the kernel timestamps
# and the per-capture totals (what phase D of task 70 measured on 2026-10-27).
#   tools/opi5/cadence.sh [N] [rate_idx] [mode tmo|cca|bb:<bit>] [trigger time us]
set -u
DIR=$(cd "$(dirname "$0")" && pwd)
LOGD="${OPI5_LOGD:-./opi5-logs}"
N="${1:-20}"; rate="${2:-2}"; mode="${3:-cca}"; tt="${4:-404}"
mkdir -p "$LOGD"
out="$LOGD/opi5-cadence-$(date +%Y%m%d-%H%M%S)-$mode-tt$tt.txt"
T=900 bash "$DIR/la.sh" cad "$N" "$rate" "$mode" "$tt" | tee "$out" | cut -c1-150
echo "== stop-to-stop intervals (s) from the kernel stop timestamps:"
grep -o 'kstop=[0-9.]*' "$out" | cut -d= -f2 | awk 'NR>1{d=$1-p; printf "%.3f ", d; s+=d; n++; if(d>mx)mx=d; if(mn==0||d<mn)mn=d} {p=$1} END{if(n)printf "\nn=%d mean=%.3f min=%.3f max=%.3f\n", n, s/n, mn, mx}'
echo "== script totals (s) per capture:"
grep -o 'total=[0-9.]*' "$out" | cut -d= -f2 | awk '{s+=$1; n++; if($1>mx)mx=$1; if(mn==0||$1<mn)mn=$1} END{if(n)printf "n=%d mean=%.3f min=%.3f max=%.3f\n", n, s/n, mn, mx}'
echo "== words per capture:"
grep -o 'hex=[0-9]*' "$out" | cut -d= -f2 | sort | uniq -c | sort -rn | head -5
bash "$DIR/fetch.sh" "la-cad-*"
