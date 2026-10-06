#!/usr/bin/env python3
"""Reproduce the review observations from a frozen, named Core commit.

Exit zero means the documented counterexamples and their controls were
reproduced. It does not mean the gateware is accepted. No checkout is edited.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
BASE = 'e5585bab98343fa2289d7a8165752b1e7206b54a'
FB_RTL = ('sdram_burst.v', 'field_phase.v', 'fb_sdram.v', 'dual_clock_ram.v',
          'genlock_timing.v', 'ycbcr2rgb.v', 'fb_display.v', 'fb_backend.v')
CAP_RTL = ('bt656_rx.v', 'word_packer.v', 'chan_capture.v', 'mix_chan.v', 'dual_clock_ram.v')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def snapshot(core, ref, dest, files):
    commit = subprocess.check_output(['git', 'rev-parse', '--verify', ref + '^{commit}'],
                                     cwd=core, text=True).strip()
    for rel in files:
        data = subprocess.check_output(['git', 'show', f'{commit}:{rel}'], cwd=core)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return commit


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--core', required=True, type=Path)
    ap.add_argument('--ref', default=BASE)
    ap.add_argument('--control-ref', help='Optional morning commit for the short-row control')
    ap.add_argument('--skip-fb', action='store_true', help='Run only the small Icarus fixtures')
    args = ap.parse_args()
    core = args.core.resolve()
    bindir = core / '.tools/iverilog/bin'
    env = dict(os.environ)
    if bindir.is_dir():
        env['PATH'] = str(bindir) + os.pathsep + env['PATH']
    require(shutil.which('iverilog', path=env['PATH']) and shutil.which('vvp', path=env['PATH']),
            'Icarus Verilog and vvp are required on PATH or in Core .tools/iverilog/bin')
    os.environ['PATH'] = env['PATH']  # Also used by the existing fb test helper.
    (HERE / 'build').mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='review-', dir=HERE / 'build'))
    src = out / 'source'
    rtl_names = sorted(set((*FB_RTL, *CAP_RTL, 'async_fifo.v', 'tvp_ctrl.v', 'i2c_master.v')))
    files = [f'gateware/rtl/{n}' for n in rtl_names]
    files += ['gateware/sim/test_fb.py', 'gateware/sim/tb_fb.v',
              'gateware/sim/sdram_model.v', 'gateware/model/fb_ref.py']
    commit = snapshot(core, args.ref, src, files)
    # The formal branch extracts the synchronizers into a separate file.
    exists = subprocess.run(['git', 'cat-file', '-e', f'{commit}:gateware/rtl/cdc_sync.v'],
                            cwd=core, capture_output=True).returncode == 0
    if exists:
        snapshot(core, commit, src, ['gateware/rtl/cdc_sync.v'])
    results = {'commit': commit, 'meaning': 'documented observations reproduced', 'cases': {}}

    def run(name, top, tb, rtl, params=(), defines=(), source=src, extra=()):
        sim = out / (name + '.vvp')
        inputs = [source / 'gateware/rtl' / n for n in rtl]
        inputs += [HERE / n for n in (*extra, tb)]
        cp = subprocess.run(['iverilog', '-g2012', '-s', top, '-o', str(sim),
                             *params, *defines, *map(str, inputs)], env=env,
                            capture_output=True, text=True, timeout=60)
        (out / (name + '.compile.log')).write_text(cp.stdout + cp.stderr)
        require(cp.returncode == 0, f'{name}: compile failed, see {out}')
        cp = subprocess.run(['vvp', '-n', str(sim)], env=env, capture_output=True,
                            text=True, timeout=60)
        log = cp.stdout + cp.stderr
        (out / (name + '.log')).write_text(log)
        require(cp.returncode == 0, f'{name}: simulation failed, see {out}')
        results['cases'][name] = log
        return log

    short = run('short_active', 'tb_short_active', 'short_active.v', CAP_RTL, defines=('-DREVIEW',))
    require('ROW n=4 count=1 bad=0 overflow=0 tail=20802080' in short,
            'Short active row counterexample changed')
    if args.control_ref:
        ctrl = out / 'control'
        results['control_commit'] = snapshot(core, args.control_ref, ctrl,
                                             [f'gateware/rtl/{n}' for n in CAP_RTL])
        clean = run('short_active_control', 'tb_short_active', 'short_active.v', CAP_RTL, source=ctrl)
        require('ROW n=4 count=0' in clean, 'Short-row control did not reject the incomplete row')
    poll = run('partial_nack', 'tb', 'tvp_partial_nack.v', ('tvp_ctrl.v',),
               extra=('i2c_completion_stub.v',))
    require('AFTER_NACK88 status_valid=1 dev_err=0 status=000e' in poll,
            'Partial NACK counterexample changed')
    ll_rtl = (*FB_RTL, 'cdc_sync.v') if exists else FB_RTL
    for guard in (0, 1):
        run(f'll_guard{guard}', 'tb_ll_payload', 'll_payload.v', ll_rtl,
            params=(f'-Ptb_ll_payload.GUARD={guard}',))  # Assertions are in the fixture.
    for stuck in (0, 1):
        log = run(f'i2c_stuck{stuck}', 'i2c_tb', 'i2c_held_low.v', ('i2c_master.v',),
                  params=(f'-Pi2c_tb.STUCK={stuck}',))
        expected = 'busy=1 completions=0' if stuck else 'busy=0 completions=1'
        require(expected in log, 'I2C stall observation changed')
    gen = run('genlock', 'genlock_tb', 'genlock.v', ('genlock_timing.v',))
    cycles = list(map(int, re.findall(r'^FRAME (\d+)$', gen, re.MULTILINE)))[1:]
    periods = [b - a for a, b in zip(cycles, cycles[1:])]
    require(len(periods) >= 2 and min(periods) >= 154, 'Genlock minimum frame period failed')
    results['genlock_periods'] = periods

    if not args.skip_fb:
        spec = importlib.util.spec_from_file_location('review_fb', src / 'gateware/sim/test_fb.py')
        fb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fb)
        for name, drop, rt in [('full_rows', set(), 0), ('missing_first', {(1, 0)}, 0),
                               ('missing_first_default', {(1, 0)}, 1)]:
            _, pix = fb.run_sim(name, fb.source(5, drop=drop), RT_EN=rt, TAIL=1_000_000)
            frames = []
            for ev, *v in pix:
                if ev == 'V':
                    frames.append({'pixel_cycle': v[0], 'lines': v[1], 'video': v[2], 'unknown': []})
                elif ev == 'X' and frames and -1 in v:
                    frames[-1]['unknown'].append(v)
            bad = [fr for fr in frames if fr['video'] and fr['unknown']]
            require(bool(bad) == bool(drop), f'{name}: missing-first-row observation changed')
            results['cases'][name] = {'rt_en': rt, 'video_frames_with_unknown_words': bad,
                                     'sdram_protocol_errors': 0}
    (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'Observations reproduced at {commit}; evidence: {out / "results.json"}')


if __name__ == '__main__':
    main()
