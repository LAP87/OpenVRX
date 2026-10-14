#!/usr/bin/env bash
# The second adversarial review's runs, against an untouched OpenVRX-Core checkout with its .venv
# and Icarus Verilog 12 on PATH:
#   OPENVRX_CORE=/path/to/OpenVRX-Core ./run_all.sh | tee results.txt
# The scripts change no RTL; testbenches and logs go to $OPENVRX_CORE/gateware/sim/build/review2_*.
# About two minutes. results.txt is from Core 072dbde.
set -u
here="${REPRO_DIR:-$(cd "$(dirname "$0")" && pwd)}"
core="${OPENVRX_CORE:?set OPENVRX_CORE to an OpenVRX-Core checkout}"
py="$core/.venv/bin/python"
echo "Core: $(git -C "$core" rev-parse --short HEAD 2>/dev/null || echo 'no git'), $(date -I)"
for s in review2_mixer_weak.py review2_rssi_margin.py review2_flash_interrupted.py review2_scan_ties.py \
         review2_hdmi_independent.py review2_vinterp_full.py; do
    echo
    echo "=== $s"
    (cd "$core" && OPENVRX_CORE="$core" "$py" "$here/$s"); echo "exit $?"
done
