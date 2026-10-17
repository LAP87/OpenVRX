"""RS-1: a weak receiver (RSSI warning) can never take over from a current receiver whose lines
are all bad when the two are out of step.

Stimulus: Core sim/test_mixer.py, test_unlocked_current_channel_out_of_step (A current after
reset, decoder unlocked = every line bad, A five and a third lines ahead of B; B good), with
receiver B weak for the whole run (rssi_adc.v warns for B: B's RSSI is low, A's is not). RTL
(tb_mixer.v) and model (line_mixer_ref.py) are run on the same streams and must agree on every
decision and word (check() asserts that); the counts below come from the decision trace.

  E1   B weak:          does B ever become current, how many of B's lines are shown
  E1c  B not weak:      the same streams without the warning (test_mixer's own expectation:
                        B takes over at its eighth line)
  E1p  B weak, in step: the channels pair; B's lines win every pair against A's bad ones

Usage: OPENVRX_CORE=/path/to/OpenVRX-Core .venv/bin/python review2_mixer_weak.py
"""
import os
import sys
from pathlib import Path

CORE = Path(os.environ.get('OPENVRX_CORE', '.')).resolve()
sys.path.insert(0, str(CORE / 'gateware' / 'sim'))
sys.path.insert(0, str(CORE / 'gateware' / 'model'))
import test_mixer as tm  # noqa: E402
import line_mixer_ref as ref  # noqa: E402


def summary(tag, m):
    shown_b = sum(1 for u, p, *_ in m.trace if p == 0b10 and u == ref.USE_B)
    lone_b = sum(1 for _, p, *_ in m.trace if p == 0b10)
    shown_a = sum(1 for u, p, *_ in m.trace if p == 0b01 and u == ref.USE_A)
    lone_a = sum(1 for _, p, *_ in m.trace if p == 0b01)
    pairs = sum(1 for _, p, *_ in m.trace if p == 0b11)
    omitted = sum(1 for o in m.omitted if o)
    first_b = m.curs.index(1) if 1 in m.curs else None
    print(f'{tag}: decisions {len(m.trace)}, pairs {pairs}; B lines {lone_b}, shown {shown_b}; '
          f'A lines {lone_a} (all bad), shown {shown_a}, left out {omitted}; '
          f'current B from decision {first_b}; final current {"B" if m.cur else "A"}')
    return dict(shown_b=shown_b, shown_a=shown_a, first_b=first_b, pairs=pairs)


def streams(lag_lines=5):
    LINE, VBI, LINES = tm.LINE, tm.VBI, tm.LINES
    a = tm.Stream(1).field(0, amp=60).field(1, amp=60).field(2, amp=60).field(3, amp=60).done()
    a = a[lag_lines * LINE:][:(3 * (VBI + LINES) + 1) * LINE]
    b = tm.Stream(2).field(0, amp=3).field(1, amp=3).field(2, amp=3).done()
    return a, b


def main():
    a, b = streams()
    kw = {'START_A': tm.START_A + tm.LINE_NS / 3}
    ev_kw = {k.lower(): v for k, v in kw.items()}
    weak = tm.check('review2_e1_weak_b', a, b, {'EXTA_ON': 0, 'WEAKB_ON': 0, **kw}, ev_kw=ev_kw,
                    ext=lambda ev: (True, False), weak=lambda ev: (False, True))
    e1 = summary('E1  B weak, out of step', weak)
    ctrl = tm.check('review2_e1c_control', a, b, {'EXTA_ON': 0, **kw}, ev_kw=ev_kw, ext=lambda ev: (True, False))
    e1c = summary('E1c B not weak, out of step', ctrl)
    a2 = tm.Stream(1).field(0, amp=60).field(1, amp=60).field(2, amp=60).done()
    b2 = tm.Stream(2).field(0, amp=3).field(1, amp=3).field(2, amp=3).done()
    paired = tm.check('review2_e1p_in_step', a2, b2, {'EXTA_ON': 0, 'WEAKB_ON': 0},
                      ext=lambda ev: (True, False), weak=lambda ev: (False, True))
    e1p = summary('E1p B weak, in step', paired)
    print('RTL equals the model in all three runs (decisions, current channel, every word).')
    verdict = e1['first_b'] is None and e1['shown_b'] == 0 and e1c['first_b'] is not None
    print('RS-1 reproduced' if verdict else 'RS-1 NOT reproduced')
    return 0 if verdict else 1


if __name__ == '__main__':
    sys.exit(main())
