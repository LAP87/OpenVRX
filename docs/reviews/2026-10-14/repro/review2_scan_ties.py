"""SC-1: what SCAN keeps when several channels lock. Model: Core model/chan_scan_ref.py, which
sim/test_chan_scan.py holds equal to rtl/chan_scan.v. The noise value is noise_stats.v's count
of luma samples outside 16..235 over 1024 lines; a decoder keeps a clean picture inside that
range, so a clean channel scores 0 or close to it whatever its signal strength.

Cases (channel index = band * 8 + channel, A1 = 0, F4 = 3 * 8 + 3 = 27, R8 = 4 * 8 + 7 = 39):
  1  the pilot's own transmitter on F4, clean (0), another transmitter on A1, also clean (0)
  2  the same, the other transmitter a little noisy (3 samples per 1024 lines)
  3  F4 locked but very noisy (5000), nothing else locks
  4  F4 locked and noisy (5000), R8 clean (0)

Usage: OPENVRX_CORE=/path/to/OpenVRX-Core python review2_scan_ties.py
"""
import os
import sys
from pathlib import Path

CORE = Path(os.environ.get('OPENVRX_CORE', '.')).resolve()
sys.path.insert(0, str(CORE / 'gateware' / 'model'))
import chan_scan_ref as ref  # noqa: E402

NAMES = [f'{b}{c}' for b in 'ABEFRL' for c in range(1, 9)]


def obs(locked):
    """locked: {idx: (noise A, noise B)}; every other channel has no lock."""
    return [(True, locked[i][0], True, locked[i][1]) if i in locked else (False, 0, False, 0) for i in range(48)]


def main():
    start = 27
    cases = [
        ('1 own F4 clean, other on A1 clean', {27: (0, 0), 0: (0, 0)}, 27),
        ('2 own F4 clean, other on A1 slightly noisy', {27: (0, 0), 0: (3, 5)}, 27),
        ('3 F4 locked and noisy, nothing else', {27: (5000, 6000)}, 27),
        ('4 F4 noisy, R8 clean', {27: (5000, 6000), 39: (0, 0)}, 39),
    ]
    tie_to_earlier = False
    for name, locked, want in cases:
        idx, found = ref.scan(obs(locked), start)
        print(f'{name}: keeps {NAMES[idx]} (found {found}); the channel one would want: {NAMES[want]}')
        if name.startswith('1') and idx != want:
            tie_to_earlier = True
    print('SC-1 reproduced: a tie of clean channels goes to the earlier one in the table'
          if tie_to_earlier else 'SC-1 NOT reproduced')
    return 0 if tie_to_earlier else 1


if __name__ == '__main__':
    sys.exit(main())
