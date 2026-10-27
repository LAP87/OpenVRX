#!/usr/bin/env bash
# Find the Orange Pi on a /24 after a reboot (its DHCP lease may change): one TCP connect to port 22 per address,
# then a key-only ssh asking for the hostname. Prints the addresses that answer with the expected name.
#   tools/opi5/find.sh 192.168.1          (the first three octets of the network)
# Env: OPI5_KEY (default ~/.ssh/openvrx_opi5_ed25519), OPI5_NAME (default orangepi5), OPI5_USER (default root)
set -u
NET="${1:?usage: find.sh <three octets of the /24>}"
KEY="${OPI5_KEY:-$HOME/.ssh/openvrx_opi5_ed25519}"; NAME="${OPI5_NAME:-orangepi5}"; USR="${OPI5_USER:-root}"
tmp=$(mktemp)
for i in $(seq 1 254); do
  ( timeout 1 bash -c "exec 3<>/dev/tcp/$NET.$i/22" 2>/dev/null && echo "$NET.$i" ) &
done | sort -t. -k4 -n > "$tmp"
wait
echo "port 22 open: $(tr '\n' ' ' < "$tmp")"
while read -r ip; do
  h=$(timeout 10 ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -i "$KEY" "$USR@$ip" hostname 2>/dev/null)
  [ "$h" = "$NAME" ] && echo "$ip -> $h  (update HostName in ~/.ssh/config for the alias)"
done < "$tmp"
rm -f "$tmp"
