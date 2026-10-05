"""Review: in run E3c only one channel's lines are shown (unpaired, through the `cnt >= 3`
rule of line_mixer.v). When do the last lines of each field leave the mixer?
Reads the decision log of that run (use, pop, field, line, time in ns)."""
import os
from pathlib import Path

CORE = Path(os.environ.get('OPENVRX_CORE', Path.home() / 'openvrx-review' / 'OpenVRX-Core'))
log = CORE / 'gateware' / 'sim' / 'build' / 'review_e3c_long_timeout_dead_first' / 'dec.txt'
rows = [tuple(int(x) for x in l.split()) for l in open(log) if l[:1].isdigit()]
shown = [r for r in rows if r[0] == 1]
prev, n = None, 0
for r in shown:
    if prev and r[3] >= 238 and n < 12:
        print(f'   line {r[3]:3d} of field {r[2]} left the mixer at {r[4] / 1e6:9.3f} ms, '
              f'{(r[4] - prev[4]) / 1e3:8.1f} us after line {prev[3]}')
        n += 1
    prev = r
