"""Decode a halbb LA-mode dump (one 16-hex-digit word per dmesg line) and show its bit-field structure.

    python3 la_decode.py <capture.txt> [out_prefix] [sample_rate_hz]

Prints the word count, per-bit toggle and ones counts (which bits carry data), stats for the candidate
12-bit signed fields of DMA type 1 (two streams x I/Q, 12 bit each) and the 16-bit top field. With numpy and
matplotlib available it also writes <out_prefix>_time.png (first 1024 samples of each field) and
<out_prefix>_spec.png (averaged spectrum of the field pairs taken as I+jQ at the given sample rate).
"""
import re
import statistics as st
import sys

path = sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else path.rsplit('.', 1)[0]
fs = float(sys.argv[3]) if len(sys.argv) > 3 else 80e6

pat = re.compile(r'\[BB\]([0-9a-f]{16})\s*$')
words = []
for line in open(path, errors='replace'):
    m = pat.search(line)
    if m:
        words.append(int(m.group(1), 16))
n = len(words)
print(f'{n} words from {path}')
if n < 2:
    sys.exit(1)

tog = [0] * 64
for a, b in zip(words, words[1:]):
    x = a ^ b
    for i in range(64):
        if x >> i & 1:
            tog[i] += 1
ones = [sum(w >> i & 1 for w in words) for i in range(64)]
print('bit      ' + ' '.join(f'{i:5d}' for i in range(63, -1, -1)))
print('toggles  ' + ' '.join(f'{tog[i]:5d}' for i in range(63, -1, -1)))
print('ones     ' + ' '.join(f'{ones[i]:5d}' for i in range(63, -1, -1)))
print('first 12 words split 16|12|12|12|12:')
for w in words[:12]:
    print(f'  {w >> 48:04x} {w >> 36 & 0xfff:03x} {w >> 24 & 0xfff:03x} {w >> 12 & 0xfff:03x} {w & 0xfff:03x}')


def s12(v):
    return v - 4096 if v & 0x800 else v


fields = {
    'f0[11:0]': [s12(w & 0xfff) for w in words],
    'f1[23:12]': [s12(w >> 12 & 0xfff) for w in words],
    'f2[35:24]': [s12(w >> 24 & 0xfff) for w in words],
    'f3[47:36]': [s12(w >> 36 & 0xfff) for w in words],
}
for k, v in fields.items():
    print(f'{k}: mean {st.fmean(v):8.2f} sd {st.pstdev(v):8.2f} min {min(v):5d} max {max(v):5d}  first {v[:8]}')
top = [w >> 48 for w in words]
print(f'top[63:48]: distinct {len(set(top))}, first {[hex(t) for t in top[:8]]}')

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except Exception as e:  # noqa: BLE001
    print('no plots:', e)
    sys.exit(0)

import os

F = {k: np.array(v, dtype=float) for k, v in fields.items()}
names = list(F)
print('cross-correlation between fields (zero mean):')
for i in range(4):
    print('  ' + f'{names[i]:10s}' + ' '.join(f'{np.corrcoef(F[names[i]], F[names[j]])[0, 1]:7.3f}' for j in range(4)))
print('autocorrelation lags 1..4 per field (near 0 = white, near 1 = band-limited):')
for k in names:
    x = F[k] - F[k].mean()
    print('  ' + f'{k:10s}' + ' '.join(f'{np.dot(x[:-l], x[l:]) / np.dot(x, x):7.3f}' for l in range(1, 5)))

fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
for ax, (k, v) in zip(axes, fields.items()):
    ax.plot(v[:1024], lw=0.6)
    ax.set_ylabel(k)
axes[-1].set_xlabel(f'sample (fs = {fs / 1e6:g} MHz)')
fig.suptitle(f'LA capture {os.path.basename(path)}: first 1024 of {n} words')
fig.tight_layout()
fig.savefig(prefix + '_time.png', dpi=100)

fig, axes = plt.subplots(2, 1, figsize=(12, 7))
for ax, (a, b) in zip(axes, (('f0[11:0]', 'f1[23:12]'), ('f2[35:24]', 'f3[47:36]'))):
    z = np.array(fields[a], dtype=float) + 1j * np.array(fields[b], dtype=float)
    z -= z.mean()
    seg = 1024
    acc = np.zeros(seg)
    k = 0
    for s in range(0, n - seg + 1, seg):
        acc += np.abs(np.fft.fftshift(np.fft.fft(z[s:s + seg] * np.hanning(seg)))) ** 2
        k += 1
    f = np.fft.fftshift(np.fft.fftfreq(seg, 1 / fs)) / 1e6
    ax.plot(f, 10 * np.log10(acc / max(k, 1) + 1e-9), lw=0.8)
    ax.set_ylabel('dB')
    ax.set_title(f'{a} + j {b}  ({k} x {seg}-point FFT, Hann)')
    ax.grid(True, alpha=0.3)
axes[-1].set_xlabel('MHz offset from centre')
fig.tight_layout()
fig.savefig(prefix + '_spec.png', dpi=100)
print('wrote', prefix + '_time.png', prefix + '_spec.png')
