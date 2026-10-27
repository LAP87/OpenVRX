"""Measure video timing in a demodulated LA capture in SAMPLES, with no sample-rate assumption: sync-pulse
starts, widths and spacing, plus the colour-burst frequency in cycles per sample. Comparing with NTSC (sync
4.7 us, line 63.6 us, burst 3.58 MHz) or PAL (4.7 us, 64 us, 4.43 MHz) gives the true sample rate.

    py -3 -I la_lines.py <capture.txt> [pair 01|23]
"""
import re
import sys

import numpy as np

path = sys.argv[1]
pair = sys.argv[2] if len(sys.argv) > 2 else '23'
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

seg = 1024
acc = np.zeros(seg)
for s in range(0, n - seg + 1, seg):
    acc += np.abs(np.fft.fftshift(np.fft.fft(z[s:s + seg] * np.hanning(seg)))) ** 2
fr = np.fft.fftshift(np.fft.fftfreq(seg))
fc = float(fr[np.argmax(acc)])
zb = z * np.exp(-2j * np.pi * fc * np.arange(n))
taps = 63
k = np.arange(taps) - (taps - 1) / 2
h = np.sinc(2 * 0.1 * k) * np.hamming(taps)   # +-0.1 cycles/sample around the carrier
h /= h.sum()
zb = np.convolve(zb, h, mode='same')
fi = np.angle(zb[1:] * np.conj(zb[:-1])) / (2 * np.pi)   # cycles/sample
fi -= np.median(fi)
m = 7
fi_lp = np.convolve(fi, np.ones(m) / m, mode='same')
lo = float(np.percentile(fi_lp, 1))
thr = 0.5 * lo
low = fi_lp < thr
d = np.diff(low.astype(int))
starts = np.flatnonzero(d == 1) + 1
ends = np.flatnonzero(d == -1) + 1
print(f'{n} samples, pair {pair}, carrier peak {fc:+.4f} cycles/sample, sync level {lo:+.4f} cycles/sample')
segs = []
for s in starts:
    e = ends[ends > s]
    if len(e):
        segs.append((int(s), int(e[0])))
segs = [(s, e) for s, e in segs if e - s > 20]
print('sync pulses (start, width) in samples:', [(s, e - s) for s, e in segs])
if len(segs) > 1:
    print('sync spacing in samples:', [segs[i + 1][0] - segs[i][0] for i in range(len(segs) - 1)])
for s, e in segs:
    wdt = e - s
    sb = fi[e + wdt // 4: e + 3 * wdt]      # after the breezeway, through the burst
    if len(sb) < 32:
        continue
    sp = np.abs(np.fft.rfft((sb - sb.mean()) * np.hanning(len(sb))))
    fb = np.fft.rfftfreq(len(sb))
    cps = fb[np.argmax(sp[1:]) + 1]
    print(f'burst after sync at {s}: {cps:.4f} cycles/sample -> fs {3.579545e6 / cps / 1e6:.1f} MHz if NTSC burst, '
          f'{4.43361875e6 / cps / 1e6:.1f} MHz if PAL burst')
for s, e in segs[:2]:
    print(f'fs from sync width {e - s} samples at 4.7 us: {(e - s) / 4.7e-6 / 1e6:.1f} MHz')
if len(segs) > 1:
    sp0 = segs[1][0] - segs[0][0]
    print(f'fs from line spacing {sp0} samples: {sp0 / 63.556e-6 / 1e6:.1f} MHz if NTSC, {sp0 / 64e-6 / 1e6:.1f} MHz if PAL')
