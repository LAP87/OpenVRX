#!/usr/bin/env bash
# One capture per plain 20 MHz channel (LO = channel centre), then fetch the files.
#   tools/opi5/cal.sh <rate_idx> <MHz>...        rate idx 0 = 80 MHz (102 us), 2 = 20 MHz (410 us)
# Always read the channel back in the output (cur_ch in rf_info): the radio rejects some frequencies silently.
set -u
DIR=$(cd "$(dirname "$0")" && pwd)
rate="${1:?usage: cal.sh <rate_idx> <MHz>...}"; shift
for f in "$@"; do T=200 bash "$DIR/la.sh" cap20 "$f" "$rate"; done
bash "$DIR/fetch.sh" "la-ch*"
