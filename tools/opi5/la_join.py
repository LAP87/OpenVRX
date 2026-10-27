"""Check a capture for a time discontinuity at the ring-buffer join: with a strong FM carrier the per-sample
phase increment is steady (video moves it by tens of degrees at most), so a join shows as a one-sample jump.

    py -3 -I la_join.py <capture.txt> <finish_ofst> [pair 01|23]
"""
import re
import sys

import numpy as np

path, ofst = sys.argv[1], int(sys.argv[2])
pair = sys.argv[3] if len(sys.argv) > 3 else '23'
pat = re.compile(r'\[BB\]([0-9a-f]{16})\s*$')
w = np.array([int(m.group(1), 16) for m in (pat.search(l) for l in open(path, errors='replace')) if m],
             dtype=np.uint64)


def s12(v):
    v = (v & np.uint64(0xfff)).astype(np.int64)
    return np.where(v & 0x800, v - 4096, v).astype(float)


f = [s12(w >> np.uint64(s)) for s in (0, 12, 24, 36)]
a, b = (0, 1) if pair == '01' else (2, 3)
z = (f[a] - f[a].mean()) + 1j * (f[b] - f[b].mean())
n = len(z)
join = n - ofst
dphi = np.angle(z[1:] * np.conj(z[:-1]))
res = np.abs(np.angle(np.exp(1j * (dphi - np.median(dphi)))))
mag = np.abs(z)
print(f'n={n}, join index {join} (n - finish_ofst), median |z| {np.median(mag):.0f}, '
      f'median phase step {np.degrees(np.median(dphi)):.1f} deg/sample')
for name, lo, hi in (('around join', max(0, join - 40), min(n - 1, join + 40)), ('global', 0, n - 1)):
    r = res[lo:hi]
    print(f'{name:12s}: mean residual {np.degrees(r.mean()):5.1f} deg, max {np.degrees(r.max()):5.1f} deg at sample {lo + int(np.argmax(r))}')
top = sorted(int(i) for i in np.argsort(res)[-8:])
print('largest phase residuals at samples:', top)
print('|z| around join:', np.round(mag[max(0, join - 6): join + 6]).astype(int).tolist())
print('phase residual (deg) around join:', np.round(np.degrees(res[max(0, join - 6): join + 6])).astype(int).tolist())
