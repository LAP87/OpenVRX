#!/usr/bin/env bash
# Re-run the review experiments against an OpenVRX-Core checkout. Needs that checkout's .venv
# (pip install -r requirements.txt) and Icarus Verilog 12 on PATH. One job at a time; about 45 min.
#   OPENVRX_CORE=/path/to/OpenVRX-Core ./run_all.sh
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
export OPENVRX_CORE="${OPENVRX_CORE:-$HOME/openvrx-review/OpenVRX-Core}"
PY="$OPENVRX_CORE/.venv/bin/python"
cd "$OPENVRX_CORE/gateware/sim"

echo "== the project's own mixer test with VBI = 20 instead of 2 (expected: test_dead_channel_switches fails)"
sed 's/^LINES, VBI, FIELDS = 10, 2, 5$/LINES, VBI, FIELDS = 10, 20, 5/' test_mixer.py > test_review_vbi20.py
"$PY" -m pytest -q -p no:cacheprovider test_review_vbi20.py || true
rm -f test_review_vbi20.py

echo "== E1-E5: mixer2, unmodified RTL"
"$PY" "$here/review_mixer.py" e1 e2 e2b e3 e3b e3c e4 e4d e5 e5b
"$PY" "$here/review_tail_lines.py"

echo "== E6: low-latency mode, alternating field lengths"
cp "$here/test_review_ll.py" . && "$PY" -m pytest -q -p no:cacheprovider test_review_ll.py; cat build/review_ll.txt; rm -f test_review_ll.py

echo "== E7, E7b: triple-buffer invariant"
cp "$here/test_review_tb3.py" . && "$PY" test_review_tb3.py slow fast | grep -E "^input|^pass|^delay"; rm -f test_review_tb3.py

echo "== bank 5: does an output on pin 25 change the TMDS clock pair?"
"$PY" "$here/review_lvds_bank.py"
( cd "$OPENVRX_CORE" && for t in m0_testpattern m4_dual_mix m6_puck_proto; do bash gateware/build.sh "$t"; done )
"$PY" "$here/review_tmds_fuses.py"
