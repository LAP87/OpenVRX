"""RS-2: the RSSI warning has no margin between the two receivers. Run on model/rssi_ref.py, which
Core's sim/test_rssi_adc.py holds equal to rtl/rssi_adc.v round by round.

Both receivers calibrated over the same range (0..1000 codes). Each round A reads a fixed
calibrated value and B reads its value plus uniform noise of +-k percent points; 20 000 rounds
(about 5.5 minutes of fields). Printed: the share of rounds in which A warns (the mixer then
takes B in every pair, without blending, whatever the two pictures look like) and in which
neither warns.

Usage: OPENVRX_CORE=/path/to/OpenVRX-Core python review2_rssi_margin.py
"""
import os
import random
import sys
from pathlib import Path

CORE = Path(os.environ.get('OPENVRX_CORE', '.')).resolve()
sys.path.insert(0, str(CORE / 'gateware' / 'model'))
import rssi_ref  # noqa: E402

ROUNDS = 20_000


def share(pct_a, pct_b, noise_b, seed=1):
    rng = random.Random(seed)
    m = rssi_ref.Rssi()
    m.load(0, 1000, 0, 1000)
    warn_a = warn_b = 0
    for _ in range(ROUNDS):
        b = pct_b + rng.uniform(-noise_b, noise_b)
        r = m.round((int(pct_a * 10), int(max(0.0, b) * 10)))
        warn_a += r['warn'][0]
        warn_b += r['warn'][1]
    return warn_a / ROUNDS, warn_b / ROUNDS


def main():
    print('A pct | B pct +- noise | A warned | B warned')
    rows = [(19, 21, 0), (10, 21, 0), (15, 20, 2), (15, 21, 2), (12, 22, 4), (5, 25, 8), (18, 19, 0)]
    out = {}
    for a, b, k in rows:
        wa, wb = share(a, b, k)
        out[(a, b, k)] = wa
        print(f'{a:5} | {b:5} +- {k:<5}  | {wa:7.1%}  | {wb:7.1%}')
    # the point: 19 against 21 (two points apart, both near the floor) warns all the time
    # (the first N_LOW - 1 rounds cannot warn)
    ok = out[(19, 21, 0)] > 0.999 and out[(18, 19, 0)] == 0.0
    print('RS-2 reproduced' if ok else 'RS-2 NOT reproduced')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
