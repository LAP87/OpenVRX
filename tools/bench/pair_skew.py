#!/usr/bin/env python3
"""Per-bit pair skew statistics for the C5VRX sample bus (hub issue #6, Twotoz's D3 question).

    pair_skew.py [--json] <dump-or-hex> [...]

C5VRX sends every 6-bit code twice at 40 MS/s (pairs [D, D]). A bus bit whose edge arrives
up to one clock (25 ns) late shows up as set in only one sample of a pair. The tool finds
the pair phase (which sample-index parity starts a pair), counts per bit how many pairs
have the bit set only in the first or only in the second sample, counts whole-code
mismatches, and prints one table per capture plus a one-line verdict per bit:
symmetric / late-rise / early-fall. Verdict mapping, from the 2026-10-27/28 bench captures
(bit 2 on GPIO11 was set only in the second sample of 5-8 % of the pairs and never only in
the first; its rising edge is late, the falling edge on time): set only in the SECOND
sample = late-rise, set only in the FIRST sample = early-fall.

Input: an M7 probe dump (header "DIGIN <n> [CLK <t>]", hex lines, "END"; one table per
complete capture, read like tools/bench/digin_decode.py) or a plain hex file with one
sample per line (Core gateware/vectors/*.hex). Stdlib only, no hardware needed.

    python tools/bench/pair_skew.py ../OpenVRX-Core/gateware/vectors/digin_bench_2026-10-28_1251.hex
    python tools/bench/pair_skew.py --json ../bench-logs/<day>/digin-probe.txt
"""
import json
import sys
from pathlib import Path

N_BITS = 6
MIN_PAIRS = 64          # below this many pairs no verdicts are given
# Pair structure is declared when the chosen parity's mismatch share is under 50 % and
# either it is nearly clean (<= 1 %, a clean paired stream has 0 on both parities) or the
# other parity mismatches at least 2x as often. Measured: fixture 2026-10-28 10.9 % vs
# 56.3 %; random codes ~98 % on both parities (no structure).
STRUCT_MAX_SHARE = 0.5
STRUCT_CLEAN_SHARE = 0.01
STRUCT_RATIO = 2.0
# A bit gets a verdict above 0.5 % of pairs (clean bits measure 0.000 % on the fixture,
# the skewed bit 5-11 %) with the dominant direction at least 4x the other (the known
# pattern has the other direction at 0).
VERDICT_SHARE = 0.005
VERDICT_RATIO = 4.0


def read_captures(path):
    """[(name, samples)]: one entry per complete DIGIN capture in a dump, or one entry for
    a plain hex file (one sample per line, packed hex pairs also accepted)."""
    text = Path(path).read_text(errors='replace')
    lines = [l.strip() for l in text.splitlines()]
    name = Path(path).name
    if any(l.startswith('DIGIN') for l in lines):
        out, cur, n = [], None, 0
        for line in lines:
            if line.startswith('DIGIN'):
                cur, n = [], 0
                w = line.split()
                try:
                    n = int(w[1], 16) if len(w) >= 3 and w[2] == 'CLK' else int(w[1])
                except (IndexError, ValueError):
                    n = 0
            elif line == 'END':
                if cur is not None and n and len(cur) == n:
                    out.append((f'{name} capture {len(out)}', cur))
                cur = None
            elif cur is not None and line:
                try:
                    cur.extend(int(line[i:i + 2], 16) for i in range(0, len(line) - len(line) % 2, 2))
                except ValueError:
                    cur = None  # non-hex line inside a capture: incomplete (port opened mid-dump), skip it
        return out
    samples = []
    for line in lines:
        if not line:
            continue
        try:
            samples.extend(int(line[i:i + 2], 16) for i in range(0, len(line) - len(line) % 2, 2))
        except ValueError:
            raise SystemExit(f'{path}: not a hex line: {line!r}')
    return [(name, samples)] if samples else []


def _mismatch_share(s, phase):
    npairs = (len(s) - phase) // 2
    if npairs <= 0:
        return 1.0
    mm = sum(1 for i in range(phase, len(s) - 1, 2) if s[i] != s[i + 1])
    return mm / npairs


def analyze(name, s):
    """Pair phase, per-bit first-only/second-only counts and verdicts for one capture."""
    shares = {ph: _mismatch_share(s, ph) for ph in (0, 1)}
    phase = 0 if shares[0] <= shares[1] else 1
    npairs = (len(s) - phase) // 2
    other = 1 - phase
    structure = (npairs >= MIN_PAIRS and shares[phase] <= STRUCT_MAX_SHARE
                 and (shares[phase] <= STRUCT_CLEAN_SHARE or shares[other] >= STRUCT_RATIO * shares[phase]))
    first_only, second_only, code_mm = [0] * N_BITS, [0] * N_BITS, 0
    for i in range(phase, len(s) - 1, 2):
        a, b = s[i], s[i + 1]
        if a != b:
            code_mm += 1
            d = a ^ b
            for k in range(N_BITS):
                if (d >> k) & 1:
                    if (b >> k) & 1:
                        second_only[k] += 1  # set only in the second sample: late rise
                    else:
                        first_only[k] += 1   # set only in the first sample: early fall
    div = npairs if npairs else 1
    bits = []
    for k in range(N_BITS):
        fo, so = first_only[k], second_only[k]
        f, sk = fo / div, so / div
        if not structure:
            v = 'none'
        elif max(f, sk) < VERDICT_SHARE:
            v = 'symmetric'
        elif sk >= VERDICT_SHARE and sk >= VERDICT_RATIO * max(f, 1.0 / div):
            v = 'late-rise'
        elif f >= VERDICT_SHARE and f >= VERDICT_RATIO * max(sk, 1.0 / div):
            v = 'early-fall'
        else:
            v = 'asymmetric'
        bits.append({'bit': k, 'first_only': fo, 'second_only': so, 'verdict': v})
    return {'name': name, 'samples': len(s), 'pairs': npairs, 'phase': phase,
            'structure': structure, 'mismatch_share': shares[phase], 'other_share': shares[other],
            'code_mismatch': code_mm, 'bits': bits}


def analyze_file(path):
    return [analyze(name, s) for name, s in read_captures(path)]


def format_text(path, caps):
    out = []
    for c in caps:
        if c['structure']:
            head = (f"{c['name']}: {c['samples']} samples, {c['pairs']} pairs, pair phase {c['phase']} "
                    f"(sample {c['phase']} starts a pair); pair structure detected "
                    f"(code mismatch {c['mismatch_share'] * 100:.3f}% here vs {c['other_share'] * 100:.3f}% "
                    f"on the other parity)")
        elif c['pairs'] < MIN_PAIRS:
            head = (f"{c['name']}: {c['samples']} samples, {c['pairs']} pairs, pair phase {c['phase']}; "
                    f"too few pairs (< {MIN_PAIRS}) - no verdicts")
        else:
            head = (f"{c['name']}: {c['samples']} samples, {c['pairs']} pairs, pair phase {c['phase']}; "
                    f"NO pair structure (code mismatch {c['mismatch_share'] * 100:.3f}% vs "
                    f"{c['other_share'] * 100:.3f}% on the other parity) - no verdicts")
        out.append(head)
        if c['structure']:
            out.append('  bit  set only in 1st  set only in 2nd  max share  verdict')
            for b in c['bits']:
                share = max(b['first_only'], b['second_only']) / c['pairs'] * 100
                out.append(f"  {b['bit']:>3}  {b['first_only']:>15}  {b['second_only']:>15}  "
                           f"{share:>8.3f}%  {b['verdict']}")
        out.append(f"  code mismatches: {c['code_mismatch']} of {c['pairs']} pairs "
                   f"({c['code_mismatch'] / c['pairs'] * 100:.3f}%)" if c['pairs'] else '  no pairs')
    return '\n'.join(out)


def main(argv):
    args = [a for a in argv[1:] if a != '--json']
    as_json = '--json' in argv[1:]
    if not args:
        print(__doc__)
        return 2
    result = []
    for path in args:
        caps = analyze_file(path)
        if not caps:
            print(f'{path}: no complete capture', file=sys.stderr)
            continue
        if as_json:
            result.append({'file': str(path), 'captures': caps})
        else:
            print(format_text(path, caps))
    if as_json:
        print(json.dumps(result, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
