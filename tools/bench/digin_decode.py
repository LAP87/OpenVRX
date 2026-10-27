#!/usr/bin/env python3
"""Decode an M7 digital-input probe dump (Core gateware/top/m7_digin_probe.v): the 6-bit samples C5VRX puts on
the bus, 40 MS/s. Prints the level histogram, the low pulses (width and spacing in samples and microseconds) and
writes <prefix>_digin.png with the samples over time and the histogram.

    digin_decode.py dump.txt [prefix] [fs_hz]

A dump holds one or more captures: a header line "DIGIN <n>", hex lines (two digits per sample) and "END".
Incomplete captures (the port was opened mid-dump) are skipped. Levels expected by cvbs_capture.v: sync about
4 codes, blanking about 20 (its slicer starts at 12) and it never looks above code 63.
"""
import sys
from pathlib import Path

import numpy as np


def captures(text, clocks=None):
    """The complete captures as arrays; clocks (a list) gets the bus clock in Hz per capture (None without CLK)."""
    out, cur, n, fclk = [], None, 0, None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('DIGIN'):
            cur = []
            w = line.split()
            try:
                n = int(w[1], 16) if len(w) >= 3 and w[2] == 'CLK' else int(w[1])   # hex since the 65 536-sample probe
            except (IndexError, ValueError):
                n = 0
            fclk = int(w[3], 16) * 65536 if len(w) >= 4 and w[2] == 'CLK' else None
        elif line == 'END':
            if cur is not None and n and len(cur) == n:
                out.append(np.array(cur, dtype=np.int32))
                if clocks is not None:
                    clocks.append(fclk)
            cur = None
        elif cur is not None and line:
            try:
                cur.extend(int(line[i:i + 2], 16) for i in range(0, len(line) - len(line) % 2, 2))
            except ValueError:
                cur = None
    return out


def runs_below(x, thr):
    """(start, width) of runs of samples below thr."""
    low = x < thr
    d = np.diff(np.concatenate(([0], low.astype(np.int8), [0])))
    starts, ends = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    return list(zip(starts, ends - starts))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = Path(argv[1])
    prefix = argv[2] if len(argv) > 2 else str(path.with_suffix(''))
    fs = float(argv[3]) if len(argv) > 3 else 40e6
    text = path.read_text(errors='replace')
    clocks = []
    caps = captures(text, clocks)
    print(f'{path.name}: {len(caps)} complete capture(s)')
    if not caps:
        return 1
    if clocks[0] and len(argv) <= 3:
        fs = clocks[0]
    print('bus clock per capture (Hz, resolution 65 536): ' + ', '.join(str(c) for c in clocks) + f'; using fs = {fs:.0f}')
    for k, x in enumerate(caps):
        hist = np.bincount(x, minlength=64)
        top = np.argsort(hist)[::-1][:8]
        print(f'-- capture {k}: n={len(x)} min={x.min()} max={x.max()} mean={x.mean():.2f} sd={x.std():.2f}')
        print('   most common codes: ' + ', '.join(f'{c}:{hist[c] / len(x) * 100:.1f}%' for c in top))
        print('   histogram (code:count, nonzero): ' + ' '.join(f'{c}:{hist[c]}' for c in range(64) if hist[c]))
        # sync pulses: runs below a slicer between the lowest common level and the next hump
        lo = int(np.percentile(x, 2))
        thr = lo + max(2, (int(np.percentile(x, 50)) - lo) // 2)
        r = runs_below(x, thr)
        wide = [(s, w) for s, w in r if w >= 20]
        print(f'   slicer {thr}: {len(r)} low runs, {len(wide)} of them >= 20 samples')
        for s, w in wide[:12]:
            print(f'     start {s:6d}  width {w:4d} samples = {w / fs * 1e6:5.2f} us  level in pulse {x[s:s + w].mean():.1f}')
        if len(wide) > 1:
            sp = np.diff([s for s, _ in wide])
            print('   spacing between wide pulses (samples): ' + ' '.join(str(int(v)) for v in sp)
                  + f'   ({np.median(sp) / fs * 1e6:.2f} us median; NTSC line 63.56 us = {63.556e-6 * fs:.0f} samples)')
    # picture of the first capture
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib missing: no picture')
        return 0
    x = caps[0]
    t = np.arange(len(x)) / fs * 1e6
    fig, ax = plt.subplots(3, 1, figsize=(14, 9))
    ax[0].plot(t, x, lw=0.5)
    ax[0].set_title(f'{path.name}: all {len(x)} samples ({len(x) / fs * 1e6:.0f} us)')
    ax[0].set_xlabel('us'); ax[0].set_ylabel('code')
    n1 = min(len(x), int(70e-6 * fs))
    ax[1].plot(t[:n1], x[:n1], lw=0.7)
    ax[1].set_title('first 70 us'); ax[1].set_xlabel('us'); ax[1].set_ylabel('code')
    ax[2].bar(np.arange(64), np.bincount(x, minlength=64))
    ax[2].set_title('level histogram'); ax[2].set_xlabel('code (0..63)'); ax[2].set_ylabel('samples')
    for a in ax:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(prefix + '_digin.png', dpi=110)
    print('wrote', prefix + '_digin.png')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
