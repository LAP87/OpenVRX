#!/usr/bin/env bash
# Copy the Pi's capture files (logs/la-*.txt) into $OPI5_LOGD. Optional argument: a name pattern without the
# extension, e.g. "la-ch5805-*" or "la-cad-*". Default: everything.
set -u
HOST="${OPI5_HOST:-opi5}"; LOGD="${OPI5_LOGD:-./opi5-logs}"; REMOTE="${OPI5_REMOTE:-/root/openvrx-rtl8852be}"
pat="${1:-la-*}"
mkdir -p "$LOGD"
timeout 300 scp -q -o BatchMode=yes "$HOST:$REMOTE/logs/$pat.txt" "$LOGD/" 2>/dev/null
echo "capture files in $LOGD: $(ls "$LOGD"/la-*.txt 2>/dev/null | wc -l)"
