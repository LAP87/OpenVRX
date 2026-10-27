"""FM-demodulate a halbb LA capture (two I/Q streams, 12 bit) and plot what an analog video receiver would see.

    py -3 -I la_fm.py <capture.txt> <out_prefix> <sample_rate_hz> [pair: 01|23|auto] [carrier offset Hz|auto]

Narrow tones (receiver spurs, the unknown tone next to the owner's VTX) are fitted as sinusoids over the whole
record and subtracted first; the FM video carrier is then the broad hump of the cleaned spectrum. Writes
<out_prefix>_fm.png: spectrum before and after tone removal with the carrier marked, instantaneous frequency
(MHz, relative to the carrier) over the whole capture after a video low-pass, and the first 70 us.
"""
import os
import re
import sys

import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

path, prefix, fs = sys.argv[1], sys.argv[2], float(sys.argv[3])
pair = sys.argv[4] if len(sys.argv) > 4 else 'auto'
fc_arg = sys.argv[5] if len(sys.argv) > 5 else 'auto'

pat = re.compile(r'\[BB\]([0-9a-f]{16})\s*$')
w = np.array([int(m.group(1), 16) for m in (pat.search(l) for l in open(path, errors='replace')) if m],
             dtype=np.uint64)


def s12(v):
    v = (v & np.uint64(0xfff)).astype(np.int64)
    return np.where(v & 0x800, v - 4096, v).astype(float)


f = [s12(w >> np.uint64(s)) for s in (0, 12, 24, 36)]
z01 = (f[0] - f[0].mean()) + 1j * (f[1] - f[1].mean())
z23 = (f[2] - f[2].mean()) + 1j * (f[3] - f[3].mean())
p01, p23 = np.mean(np.abs(z01) ** 2), np.mean(np.abs(z23) ** 2)
if pair == 'auto':
    pair = '01' if p01 >= p23 else '23'
z = z01 if pair == '01' else z23
n = len(z)
t = np.arange(n) / fs
print(f'{n} samples, pair {pair}: power 01 = {10 * np.log10(p01):.1f} dB, 23 = {10 * np.log10(p23):.1f} dB')


def spectrum(z, seg=1024):
    acc = np.zeros(seg)
    k = 0
    for s in range(0, len(z) - seg + 1, seg):
        acc += np.abs(np.fft.fftshift(np.fft.fft(z[s:s + seg] * np.hanning(seg)))) ** 2
        k += 1
    return np.fft.fftshift(np.fft.fftfreq(seg, 1 / fs)), 10 * np.log10(acc / max(k, 1) + 1e-9)


def hump(fr, spec, width=1.5e6):
    kb = max(1, int(round(width / (fr[1] - fr[0]))))
    sm = np.convolve(10 ** (spec / 10), np.ones(kb) / kb, mode='same')
    i = int(np.argmax(sm))
    return float(fr[i]), float(10 * np.log10(sm[i]) - np.median(spec))


# Known narrow tones in absolute MHz: the receiver's own spurs (seen without any transmitter on 2026-10-27) and the
# tone that appeared 2.7 MHz above the owner's VTX. They are removed only when the channel centre is given, so the
# FM carrier itself (nearly a tone for a dark picture) is never taken by mistake.
KNOWN_TONES_MHZ = [5796.1, 5800.0, 5801.5, 5805.0, 5811.2, 5822.2, 5830.5, 5831.5]
centre_mhz = float(sys.argv[6]) if len(sys.argv) > 6 else None


def remove_known_tones(z, centre_mhz, search=0.15e6, passes=3):
    """For each known tone inside the band: find the exact frequency within +-search of the nominal one on a
    zero-padded spectrum, fit a complex sinusoid over the whole record by least squares and subtract it.
    Repeated passes catch a slightly unstable tone. Returns the cleaned signal and a report per tone."""
    report = []
    N = 1 << (int(np.ceil(np.log2(len(z)))) + 3)
    win = np.hanning(len(z))
    fgrid = np.fft.fftfreq(N, 1 / fs)
    for tone in KNOWN_TONES_MHZ:
        off = (tone - centre_mhz) * 1e6
        if abs(off) > fs / 2 - 0.3e6:
            continue
        before = None
        total = 0.0
        f_used = off
        for _ in range(passes):
            P = np.abs(np.fft.fft(z * win, N)) ** 2
            sel = np.abs(fgrid - off) <= search
            i = int(np.flatnonzero(sel)[np.argmax(P[sel])])
            if before is None:
                before = P[i]
            f0 = fgrid[i]
            e = np.exp(2j * np.pi * f0 * t)
            a = np.vdot(e, z) / len(z)
            z = z - a * e
            total += abs(a) ** 2
            f_used = f0
        P = np.abs(np.fft.fft(z * win, N)) ** 2
        after = P[np.argmin(np.abs(fgrid - f_used))]
        report.append((tone, f_used, 10 * np.log10(total + 1e-9), 10 * np.log10(before / (after + 1e-9))))
    return z, report


fr, spec_raw = spectrum(z)
hump_raw = hump(fr, spec_raw)
if centre_mhz is not None:
    zc, tones = remove_known_tones(z, centre_mhz)
    for tone, f0, pdb, drop in tones:
        print(f'tone {tone:.1f} MHz removed at {f0 / 1e6:+.3f} MHz offset (power {pdb:.1f} dB, bin dropped {drop:.1f} dB)')
else:
    zc, tones = z, []
fr, spec = spectrum(zc)
hump_f, hump_db = hump(fr, spec)
print(f'broad hump: raw {hump_raw[0] / 1e6:+.3f} MHz, after tone removal {hump_f / 1e6:+.3f} MHz '
      f'({hump_db:.1f} dB over median); sharpest bin now {fr[np.argmax(spec)] / 1e6:+.3f} MHz')


def demod(zc, fc, half_bw):
    zb = zc * np.exp(-2j * np.pi * fc * t)
    if fs > 14e6:
        taps = 63
        k = np.arange(taps) - (taps - 1) / 2
        h = np.sinc(2 * half_bw / fs * k) * np.hamming(taps)
        h /= h.sum()
        zb = np.convolve(zb, h, mode='same')
    return np.angle(zb[1:] * np.conj(zb[:-1])) * fs / (2 * np.pi)


# two passes: a wide band around the hump gives the median video level, the second band is centred on it
fc = float(fc_arg) if fc_arg != 'auto' else hump_f
if fc_arg == 'auto':
    fi1 = demod(zc, fc, 8e6)
    fc = fc + float(np.median(fi1))
fi = demod(zc, fc, 7e6)
m = max(1, int(round(fs / 6e6)))
fi_lp = np.convolve(fi, np.ones(m) / m, mode='same')
dev = np.percentile(fi_lp, [1, 50, 99])
print(f'carrier taken at {fc / 1e6:+.3f} MHz; instantaneous frequency relative to it after low-pass: '
      f'1% {dev[0] / 1e6:+.2f}  50% {dev[1] / 1e6:+.2f}  99% {dev[2] / 1e6:+.2f} MHz (span {(dev[2] - dev[0]) / 1e6:.2f} MHz)')
thr = dev[1] - 0.6 * (dev[1] - dev[0])
low = fi_lp < thr
edges = np.flatnonzero(np.diff(low.astype(int)) == 1)
if len(edges) > 1:
    per = np.diff(edges) / fs * 1e6
    print(f'{len(edges)} dips below threshold; spacing us: {np.round(per, 1)[:12]}')
else:
    print(f'{len(edges)} dips below threshold')

tu = t[1:] * 1e6
fig, ax = plt.subplots(3, 1, figsize=(12, 10))
ax[0].plot(fr / 1e6, spec_raw, lw=0.6, color='0.6', label='raw')
ax[0].plot(fr / 1e6, spec, lw=0.8, label='tones removed')
ax[0].axvline(fc / 1e6, color='r', lw=0.8, ls='--', label='carrier')
ax[0].set_xlabel('MHz offset from channel centre')
ax[0].set_ylabel('dB')
ax[0].set_title(f'{os.path.basename(path)} pair {pair}: spectrum, carrier {fc / 1e6:+.2f} MHz, {len(tones)} tone(s) removed')
ax[0].legend(loc='upper right', fontsize=8)
ax[0].grid(alpha=0.3)
ax[1].plot(tu, fi_lp / 1e6, lw=0.6)
ax[1].set_ylabel('MHz from carrier')
ax[1].set_xlabel('us')
ax[1].set_title('FM demodulated (video low-pass), whole capture')
ax[1].grid(alpha=0.3)
sel = tu <= 70
ax[2].plot(tu[sel], fi_lp[sel] / 1e6, lw=0.8)
ax[2].set_ylabel('MHz from carrier')
ax[2].set_xlabel('us')
ax[2].set_title('first 70 us (one video line is 63.6 us NTSC, 64 us PAL)')
ax[2].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(prefix + '_fm.png', dpi=100)
print('wrote', prefix + '_fm.png')
