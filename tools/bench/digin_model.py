#!/usr/bin/env python3
"""Run M7 probe captures (digin_decode.py format) through Core's cvbs_capture model, bit-exact with the RTL:
where does the line flywheel lock and unlock, which lines come out and with which bad flags and lengths.

    digin_model.py <core tree> dump.txt [sync_init blank_init] [capture index]

sync_init/blank_init replace the model's bootstrap levels (SYNC_INIT/BLANK_INIT, 4 and 20 codes); the bench
experiment of 2026-10-27 used 23 and 31, what the probe measured on the C5VRX bus.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import digin_decode  # noqa: E402


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    core, dump = Path(argv[1]), Path(argv[2])
    sys.path.insert(0, str(core / 'gateware' / 'model'))
    import cvbs_capture_ref as m  # noqa: E402
    if len(argv) >= 5:
        m.SYNC_INIT, m.BLANK_INIT = int(argv[3]), int(argv[4])
    which = int(argv[5]) if len(argv) >= 6 else 0
    clocks = []
    caps = digin_decode.captures(dump.read_text(errors='replace'), clocks)
    if not caps:
        print('no complete capture')
        return 1
    x = caps[which]
    print(f'{dump.name} capture {which}: {len(x)} samples, bootstrap sync {m.SYNC_INIT} blank {m.BLANK_INIT}, '
          f'H_NOM {m.H_NOM} +- {m.H_TOL}')
    cap = m.Capture()
    cap.run([int(v) for v in x])
    print('lock trace (sample, locked): ' + ', '.join(f'{i}:{int(l)}' for i, l in cap.lock_trace))
    locked_samples = 0
    prev_i, prev_l = 0, False
    for i, l in cap.lock_trace + [(len(x), None)]:
        if prev_l:
            locked_samples += i - prev_i
        prev_i, prev_l = i, l
    print(f'locked {locked_samples / len(x) * 100:.1f} % of the capture; final sync {cap.sync} blank {cap.blank} '
          f'hp {cap.hp}')
    markers = [e for e in cap.entries if e[0] == 'marker']
    words = sum(1 for e in cap.entries if e[0] == 'word')
    print(f'{len(markers)} line markers, {words} words ({words / max(1, len(markers)):.1f} per line)')
    for e in markers[:40]:
        _, field, line, hf, bad, length = e
        print(f'  field {field} line {line:3d} hf {hf:6d} bad {bad} length {length}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
