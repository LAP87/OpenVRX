#!/usr/bin/env bash
# Local side of the LA probe (WSL or Linux): copies la_remote.sh to the Pi and runs one of its sub-commands there,
# logging the output under $OPI5_LOGD.
#
#   tools/opi5/la.sh chan 5805             tune a plain 20 MHz channel (LO = centre); "chan 5745 80 5775" for a block
#   tools/opi5/la.sh cap20 5805 2          one capture on that channel, rate idx 2 = 20 MHz (0 = 80 MHz)
#   tools/opi5/la.sh cap2 0 0 0            one capture with the current tuning (buf, rate idx, timeout idx)
#   tools/opi5/la.sh sweep                 one capture per block over 5490-5835 MHz, power per block
#   tools/opi5/la.sh cad 20 2 cca 404      cadence run: N captures, rate idx, tmo|cca|bb:<bit>, trigger time us
#   tools/opi5/la.sh dbg 2002              one capture with that debug port, to look at its bits
#
# Env: OPI5_HOST (ssh alias, default opi5), OPI5_LOGD (default ./opi5-logs), OPI5_IF (default wlP4p65s0),
#      OPI5_REMOTE (default /root/openvrx-rtl8852be), T (ssh timeout in s, default 150)
set -u
DIR=$(cd "$(dirname "$0")" && pwd)
HOST="${OPI5_HOST:-opi5}"; LOGD="${OPI5_LOGD:-./opi5-logs}"; REMOTE="${OPI5_REMOTE:-/root/openvrx-rtl8852be}"; IF="${OPI5_IF:-wlP4p65s0}"
step="${1:?usage: la.sh <sub-command> [args]  (see the header)}"; shift
mkdir -p "$LOGD"
tr -d '\r' < "$DIR/la_remote.sh" > /tmp/la_remote.sh
timeout 30 scp -q -o BatchMode=yes /tmp/la_remote.sh "$HOST:$REMOTE/la_remote.sh" || { echo "scp to $HOST failed"; exit 1; }
timeout "${T:-150}" ssh -n -o ConnectTimeout=8 -o BatchMode=yes "$HOST" "OPI5_IF=$IF REMOTE=$REMOTE TT=${TT:-404} DBGP=${DBGP:-} bash $REMOTE/la_remote.sh $step $*" 2>&1 \
  | tee -a "$LOGD/opi5-la-$(date +%Y%m%d)-$step.txt"
