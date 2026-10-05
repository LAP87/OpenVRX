"""Adversarial runs of the unmodified mixer2 RTL (review, not part of the project).

Reuses the project's own model (model/bt656.py, model/line_mixer_ref.py) and the
stimulus helpers of sim/test_mixer.py. Each experiment prints a short verdict.

    cd gateware/sim && ../../.venv/bin/python /path/review_mixer.py e1 e2 ...
"""
import os
import random
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

CORE = Path(os.environ.get('OPENVRX_CORE', Path.home() / 'openvrx-review' / 'OpenVRX-Core'))   # a checkout of OpenVRX-Core with .venv
GW = CORE / 'gateware'
SIM = GW / 'sim'
sys.path.insert(0, str(SIM))
sys.path.insert(0, str(GW / 'model'))
import bt656  # noqa: E402
import line_mixer_ref as ref  # noqa: E402
import test_mixer as tm  # noqa: E402

REVIEW = Path(__file__).resolve().parent
T_A, T_B, T_S = 37.0, 37.07, 15.4
LINE_NS = 1716 * T_A
USE = {0b01: 'A', 0b10: 'B', 0b11: 'blend', 0b00: 'drop'}


def hf_of(active):
    luma = active[1::2]
    return sum(abs(x - y) for x, y in zip(luma[1:], luma[:-1]))


def bumped(fld, line, target_rel=0.20):
    """The clean test line with single-pixel luma bumps added until its HF energy is
    `target_rel` above the clean line's, relative to the larger one (deterministic)."""
    clean = tm.active_bytes(fld, line, 0, None)
    out, base, x = bytearray(clean), hf_of(clean), 21
    while (hf_of(out) - base) / hf_of(out) < target_rel:
        out[2 * x + 1] = min(254, out[2 * x + 1] + 10)
        x += 29
    return bytes(out)


def gen_stream(seed, nfields, lines, vbi, amp_fn, f0=0, f_const=None):
    """BT.656 bytes, fields of `vbi` blanking + `lines` active lines. amp_fn(field, line) is
    the snow amplitude of that line, or the string 'bump' for a line 20 % above the clean one."""
    rng = random.Random(seed)
    data = bytearray()
    for fld in range(nfields):
        f = (fld + f0) & 1 if f_const is None else f_const
        for i in range(vbi + lines):
            v = 1 if i < vbi else 0
            amp = None if v else amp_fn(fld, i - vbi)
            act = (bt656.blanking(1440) if v else bumped(fld, i - vbi) if amp == 'bump'
                   else tm.active_bytes(fld, i - vbi, amp, rng))
            data += bytes([0xFF, 0, 0, bt656.xy(f, v, 1)]) + bt656.blanking(1716 - 1440 - 8)
            data += bytes([0xFF, 0, 0, bt656.xy(f, v, 0)]) + act
    return bytes(data)


def run_rtl(a, b, name, start_a=2000.0, start_b=5300.0, timeout=None, ext_a=0, ext_b=0, log_words=0, t_b=None):
    work = SIM / 'build' / name
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    bt656.write_hex(work / 'a.hex', a)
    bt656.write_hex(work / 'b.hex', b)
    rtl = [GW / 'rtl' / n for n in ('bt656_rx.v', 'word_packer.v', 'async_fifo.v', 'dual_clock_ram.v',
                                    'chan_capture.v', 'mix_chan.v', 'line_mixer.v', 'snow_stats.v', 'mixer2.v')]
    p = [f'-Ptb_review_mixer.N_A={len(a)}', f'-Ptb_review_mixer.N_B={len(b)}',
         f'-Ptb_review_mixer.START_A={start_a}', f'-Ptb_review_mixer.START_B={start_b}',
         f'-Ptb_review_mixer.EXT_A={ext_a}', f'-Ptb_review_mixer.EXT_B={ext_b}',
         f'-Ptb_review_mixer.LOG_WORDS={log_words}']
    if timeout is not None:
        p.append(f'-Ptb_review_mixer.TIMEOUT={timeout}')
    if t_b is not None:          # decoder B's byte period in ns (tb default 37.07: 0.19 % slower than A)
        p.append(f'-Ptb_review_mixer.T_B={t_b}')
    subprocess.run(['iverilog', '-g2012', '-o', 'sim.vvp', '-s', 'tb_review_mixer', *p,
                    *map(str, rtl), str(REVIEW / 'tb_review_mixer.v')], cwd=work, check=True)
    subprocess.run(['vvp', '-n', 'sim.vvp'], cwd=work, check=True, capture_output=True)
    dec, end = [], None
    for line in (work / 'dec.txt').read_text().split('\n'):
        q = line.split()
        if not q:
            continue
        if q[0] == 'end':
            end = (int(q[1]), int(q[2]))
        else:
            dec.append(tuple(int(x) for x in q))          # use, pop, field, line, time_ns
    ev = [(q[0], int(q[1]), int(q[2])) for q in
          (l.split() for l in (work / 'ev.txt').read_text().split('\n')) if q]
    return dec, ev, end


def run_model(a, b, start_a=2000.0, start_b=5300.0, **kw):
    evs = [(t, 0, r) for t, r in tm.records_with_times(a, start_a, T_A)]
    evs += [(t, 1, r) for t, r in tm.records_with_times(b, start_b, T_B)]
    m = ref.Mixer(**kw)
    for _, ch, r in sorted(evs, key=lambda e: e[0]):
        m.push(ch, r)
    return m


def fb_publications(dec):
    """How many 'new field' events fb_sdram.v (and the low-latency writer) would see in
    the emitted line sequence: field bit changes or the line number goes backwards."""
    n, have, cf, last = 0, False, 0, 0
    for use, _pop, f, l, *_ in dec:
        if not use:
            continue
        if have and (f != cf or l < last):
            n += 1
        have, cf, last = True, f, l
    return n


def rel_hf(amp_a, amp_b, lines=24, seed=5):
    """Range of (hfA - hfB) / max over a field's lines for two snow amplitudes."""
    ra, rb = random.Random(seed), random.Random(seed + 1)
    out = []
    for l in range(lines):
        la = list(tm.active_bytes(2, l, amp_a, ra)[1::2])
        lb = list(tm.active_bytes(2, l, amp_b, rb)[1::2])
        ea = sum(abs(x - y) for x, y in zip(la[1:], la[:-1]))
        eb = sum(abs(x - y) for x, y in zip(lb[1:], lb[:-1]))
        out.append((ea - eb) / max(ea, eb))
    return min(out), max(out)


# ---------------------------------------------------------------- E1
def e1():
    """Healthy, locked, in-step receivers with a realistic vertical blanking gap (20 lines,
    BT.656 NTSC has 19) instead of the 2 lines sim/test_mixer.py uses. The RTL must still
    match the 'bit-exact' model."""
    lines, vbi, nf = 24, 20, 5
    # field 0: A clean, B snow -> A current. field 1: A snow, B clean -> B current.
    # fields 2-4: A clean, B 20 % more HF energy on every line: no blend (>= 14.8 %), no switch (<= 25 %).
    amp_a = {0: 0, 1: 60, 2: 0, 3: 0, 4: 0}
    amp_b = {0: 60, 1: 0, 2: 'bump', 3: 'bump', 4: 'bump'}
    rels = [(hf_of(bumped(2, l)) - hf_of(tm.active_bytes(2, l, 0, None))) / hf_of(bumped(2, l)) for l in range(lines)]
    assert 0.16 < min(rels) and max(rels) < 0.24, (min(rels), max(rels))
    a = gen_stream(1, nf, lines, vbi, lambda f, l: amp_a[f])
    b = gen_stream(2, nf, lines, vbi, lambda f, l: amp_b[f])
    m = run_model(a, b)
    dec, ev, end = run_rtl(a, b, 'review_e1')
    rtl = [d[:4] for d in dec]
    first = next((i for i, (g, e) in enumerate(zip(rtl, m.trace)) if g != e), None)
    print(f'E1 fields of {lines} lines + {vbi} blanking lines; snow A/B per field: '
          f'{[(amp_a[f], amp_b[f]) for f in range(nf)]}')
    print(f'   decisions: rtl {len(rtl)}, model {len(m.trace)}; first mismatch at index {first}')
    if first is not None:
        print(f'   rtl   {rtl[first]}  (use, pop, field, line)')
        print(f'   model {m.trace[first]}')
    for fld in range(nf):
        r = Counter(USE[d[0]] for d in dec[fld * lines:(fld + 1) * lines])
        mm = Counter(USE[d[0]] for d in m.trace[fld * lines:(fld + 1) * lines])
        print(f'   field {fld}: rtl {dict(r)}  model {dict(mm)}')
    print('   events:', [(n, v, round(t / 1e6, 3)) for n, v, t in ev][:40])
    n_diff = sum(1 for g, e in zip(rtl, m.trace) if g != e)
    print(f'E1 VERDICT: {"MISMATCH" if n_diff else "match"} ({n_diff} of {len(rtl)} decisions differ from the model)')


# ---------------------------------------------------------------- E2 / E3
def _one_dead(name, timeout, bad_is_cur, dead_first=False):
    """One receiver is fine and locked; the other has no signal: its decoder free-runs half a
    field out of step, delivers snow, and its status says 'no lock' (ext_bad)."""
    lines, vbi = 242, 20                         # 262 lines per field (NTSC is 262.5)
    field_ns = (lines + vbi) * LINE_NS
    good = gen_stream(1, 6, lines, vbi, lambda f, l: 0)
    bad = gen_stream(2, 5, lines, vbi, lambda f, l: 60)
    if bad_is_cur:      # A (the reset default `cur`) is the dead one
        a, b, sa, sb, ext = bad, good, 2000.0 + field_ns / 2, 2000.0, dict(ext_a=1)
        if dead_first:  # the dead decoder delivers lines first, as after power-up (tvp_ctrl enables A before B)
            sa, sb = 2000.0, 2000.0 + field_ns / 2
        good_use, bad_use, good_pop = 0b10, 0b01, 0b10
    else:               # B is the dead one
        a, b, sa, sb, ext = good, bad, 2000.0, 2000.0 + field_ns / 2, dict(ext_b=1)
        good_use, bad_use, good_pop = 0b01, 0b10, 0b01
    dec, ev, end = run_rtl(a, b, name, start_a=sa, start_b=sb, timeout=timeout, **ext)
    # judge only while both streams run: from 1 field after the later start to the end of the bad stream
    t0, t1 = 2000.0 + 1.5 * field_ns, 2000.0 + (4.9 if dead_first else 5.4) * field_ns
    win = [d for d in dec if t0 <= d[4] <= t1]
    shown_good = sum(1 for d in win if d[0] == good_use)
    shown_bad = sum(1 for d in win if d[0] == bad_use)
    dropped_good = sum(1 for d in win if d[0] == 0 and d[1] == good_pop)
    blended = sum(1 for d in win if d[0] == 0b11)
    curs = [(v, round(t / 1e6, 2)) for n, v, t in ev if n == 'cur' and t0 <= t <= t1]
    pubs = fb_publications(win)
    real_fields = (t1 - t0) / field_ns
    print(f'{name}: TIMEOUT={timeout or 65536}, dead receiver is {"A (cur at reset)" if bad_is_cur else "B"}; '
          f'window {t0 / 1e6:.1f}..{t1 / 1e6:.1f} ms = {real_fields:.1f} fields')
    print(f'   lines shown from the good receiver: {shown_good}')
    print(f'   lines shown from the dead receiver: {shown_bad}   blended: {blended}')
    print(f'   good lines thrown away:             {dropped_good}')
    print(f'   `cur` changes in the window: {curs}')
    print(f'   field starts fb_sdram would see: {pubs} (real fields in the window: {real_fields:.1f})')
    total_good = shown_good + dropped_good
    print(f'{name} VERDICT: {100 * dropped_good / max(1, total_good):.0f} % of the good receiver\'s lines are '
          f'discarded, {shown_bad} snow lines from the unlocked decoder are displayed instead')


def e2():
    _one_dead('review_e2_default', None, bad_is_cur=False)


def e2b():
    _one_dead('review_e2_long_timeout', 262144, bad_is_cur=False)


def e3():
    _one_dead('review_e3_default', None, bad_is_cur=True)


def e3b():
    _one_dead('review_e3_long_timeout', 262144, bad_is_cur=True)


def e3c():
    _one_dead('review_e3c_long_timeout_dead_first', 262144, bad_is_cur=True, dead_first=True)


# ---------------------------------------------------------------- E4
def _lag(name, lag_lines, timeout):
    """A is locked, clean and current. B's decoder reports no lock, shows snow, and its line
    numbering lags A's by `lag_lines` (same field parity)."""
    lines, vbi = 60, 20
    a = gen_stream(1, 5, lines, vbi, lambda f, l: 0)
    b = gen_stream(2, 4, lines, vbi, lambda f, l: 60)
    field_ns = (lines + vbi) * LINE_NS
    dec, ev, end = run_rtl(a, b, name, start_a=2000.0, start_b=2000.0 + lag_lines * LINE_NS + 3300.0,
                           timeout=timeout, ext_b=1)
    t0, t1 = 2000.0 + 1.0 * field_ns, 2000.0 + 3.9 * field_ns
    win = [d for d in dec if t0 <= d[4] <= t1]
    c = Counter((USE[d[0]], d[1]) for d in win)
    shown_b = sum(1 for d in win if d[0] == 0b10)
    shown_a = sum(1 for d in win if d[0] == 0b01)
    pubs = fb_publications(win)
    ov = [(v, round(t / 1e6, 2)) for n, v, t in ev if n == 'overflow']
    print(f'{name}: B lags A by {lag_lines} lines, TIMEOUT={timeout or 65536}')
    print(f'   decisions (use, pop): {dict(c)}')
    print(f'   shown from A (good, current): {shown_a}; shown from B (unlocked): {shown_b}; '
          f'overflow events: {ov}')
    print(f'   field starts fb_sdram would see: {pubs} (real fields in the window: {(t1 - t0) / field_ns:.1f})')
    print(f'{name} VERDICT: {shown_b} lines from the unlocked decoder displayed, '
          f'{pubs} field boundaries signalled for {(t1 - t0) / field_ns:.1f} real fields')


def e4():
    for lag in (2, 5, 12):
        _lag(f'review_e4_lag{lag}', lag, 262144)


def e4d():
    _lag('review_e4_lag5_default', 5, None)


# ---------------------------------------------------------------- E5
def _fstuck(name, skip_lines):
    """Non-interlaced camera: the TVP5150AM1 forces F = 1 for a nonstandard even line count
    (SLES209E 3.21.20, register 15h default 01h). Both receivers are clean and locked on the
    same picture. Decoder B's output is enabled `skip_lines` lines after decoder A's (tvp_ctrl
    writes 03h to A first, then to B), so B's receiver logic sees its first line later."""
    lines, vbi, nf = 100, 20, 12
    a = gen_stream(1, nf, lines, vbi, lambda f, l: 0, f_const=1)
    b = gen_stream(2, nf, lines, vbi, lambda f, l: 0, f_const=1)
    b = b[skip_lines * 1716:]                   # same picture at the same time, B just starts later
    recs = bt656.Receiver().feed(a)
    nums = [r.line_in_field for r in recs]
    print(f'{name}: {nf} fields of {lines} active + {vbi} blanking lines, F stuck at 1, B enabled {skip_lines} lines after A')
    print(f'   model, decoder A: line numbers {nums[:3]} ... end of field 0: {nums[lines - 1]}, start of field 1: {nums[lines]}, '
          f'max {max(nums)}; numbering restarts {sum(1 for x, y in zip(nums, nums[1:]) if y < x)} times in {nf} fields')
    # two decoders locked to the same camera do not drift apart: give B almost the same byte period
    # (the tb default 37.00 / 37.07 ns would slide B by 2.7 lines over this long run)
    dec, ev, end = run_rtl(a, b, name, start_a=2000.0, start_b=2000.0 + skip_lines * LINE_NS + 3300.0,
                           timeout=262144, t_b=37.001)
    c = Counter((USE[d[0]], d[1]) for d in dec)
    paired = sum(1 for d in dec if d[1] == 0b11)
    print(f'   RTL mixer2 (TIMEOUT raised so that `alive` stays out of it): decisions (use, pop) {dict(c)}')
    print(f'   paired lines: {paired} of {len(dec)} decisions; highest line number emitted: {max(d[3] for d in dec)} '
          f'(a field has {lines} lines)')
    print(f'   field starts fb_sdram / the low-latency trigger would see: {fb_publications(dec)} (real fields: {nf})')
    print(f'{name} VERDICT: {paired} paired decisions of {len(dec)}; {fb_publications(dec)} field starts seen for {nf} real fields')


def e5():
    _fstuck('review_e5_same_start', 10)         # both decoders first see the same active line (line 0 of a field)


def e5b():
    _fstuck('review_e5b_offset', 30)            # B's first line is active line 10 of the field A started on


if __name__ == '__main__':
    for arg in sys.argv[1:] or ['e1']:
        globals()[arg]()
        print()
