"""Tests for pair_skew.py (hub issue #6). Synthetic streams only, stdlib only, no board.

    python -m unittest discover -s tools/bench -p 'test_pair_skew.py'      # from the hub

The fixture test at the bottom runs when the Core checkout sits next to the hub and
records the numbers measured on it 2026-11-03: pair phase 0, bit 2 set only in the second
sample in 3557 of 32768 pairs (10.855 %), never only in the first, all other bits 0
mismatches, all 3557 code mismatches on bit 2.
"""
import contextlib
import io
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pair_skew  # noqa: E402


def paired(unique):
    """The bus form: every code sent twice, pairs (even, odd)."""
    out = []
    for u in unique:
        out += [u, u]
    return out


def late_rise(unique, bit):
    """The known 2026-10-27/28 pattern: the rising edge of `bit` arrives one sample late
    (first sample of the pair keeps the old value), the falling edge on time."""
    s = []
    prev = 0
    for u in unique:
        a = u & ~(1 << bit) if ((u >> bit) & 1) and not ((prev >> bit) & 1) else u
        s += [a, u]
        prev = u
    return s


def late_fall(unique, bit):
    """Mirror pattern: the falling edge arrives one sample late (the first sample of the
    pair keeps the old 1, so the bit is set only in the first sample)."""
    s = []
    prev = 0
    for u in unique:
        a = u | (1 << bit) if not ((u >> bit) & 1) and ((prev >> bit) & 1) else u
        s += [a, u]
        prev = u
    return s


class PairSkew(unittest.TestCase):
    def test_clean_paired_stream(self):
        rng = random.Random(7)
        unique = [rng.randrange(64) for _ in range(2048)]
        c = pair_skew.analyze('synthetic', paired(unique))
        self.assertTrue(c['structure'])
        self.assertEqual(c['phase'], 0)
        self.assertEqual(c['code_mismatch'], 0)
        self.assertEqual([b['verdict'] for b in c['bits']], ['symmetric'] * 6)

    def test_late_rise_bit_reported_with_direction(self):
        # bit 2 toggles every other unique code: 1023 rises in 2048 pairs
        unique = [(k & 0x3B) | ((k & 1) << 2) for k in range(2048)]  # bit 2 = k&1, other bits vary
        c = pair_skew.analyze('synthetic', late_rise(unique, 2))
        self.assertTrue(c['structure'])
        b2 = c['bits'][2]
        self.assertEqual(b2['verdict'], 'late-rise')
        self.assertGreater(b2['second_only'], 0)
        self.assertEqual(b2['first_only'], 0)
        self.assertEqual(b2['second_only'], c['code_mismatch'])  # every code mismatch is bit 2
        for k in (0, 1, 3, 4, 5):
            self.assertEqual(c['bits'][k]['verdict'], 'symmetric')
            self.assertEqual(c['bits'][k]['first_only'] + c['bits'][k]['second_only'], 0)

    def test_late_fall_bit_reported_with_direction(self):
        unique = [(k & 0x3B) | ((k & 1) << 2) for k in range(2048)]
        c = pair_skew.analyze('synthetic', late_fall(unique, 2))
        b2 = c['bits'][2]
        self.assertEqual(b2['verdict'], 'late-fall')
        self.assertGreater(b2['first_only'], 0)
        self.assertEqual(b2['second_only'], 0)

    @staticmethod
    def _with_events(second_only, first_only, pairs=512, bit=2):
        """A clean paired stream of varying codes with `bit` clear, and the given number
        of pairs where `bit` is set only in the second / only in the first sample."""
        rng = random.Random(11)
        s = paired([rng.randrange(64) & ~(1 << bit) for _ in range(pairs)])
        for i in range(second_only):
            s[2 * (10 + i) + 1] |= 1 << bit
        for i in range(first_only):
            s[2 * (200 + i)] |= 1 << bit
        return s

    def test_three_events_and_no_opposite_are_too_few(self):
        # 3 of 512 pairs is 0.586 %, over the 0.5 % share, but under MIN_EVENTS
        c = pair_skew.analyze('synthetic', self._with_events(3, 0))
        self.assertTrue(c['structure'])
        self.assertEqual(c['bits'][2]['second_only'], 3)
        self.assertEqual(c['bits'][2]['verdict'], 'too-few')

    def test_four_events_and_no_opposite_give_a_direction(self):
        c = pair_skew.analyze('synthetic', self._with_events(4, 0))
        self.assertEqual(c['bits'][2]['verdict'], 'late-rise')
        c = pair_skew.analyze('synthetic', self._with_events(0, 4))
        self.assertEqual(c['bits'][2]['verdict'], 'late-fall')

    def test_both_directions_under_the_ratio_are_asymmetric(self):
        # 12 against 4 is 3x, under the 4x ratio; 16 against 4 is 4x and gets a direction
        c = pair_skew.analyze('synthetic', self._with_events(12, 4))
        self.assertEqual(c['bits'][2]['verdict'], 'asymmetric')
        c = pair_skew.analyze('synthetic', self._with_events(16, 4))
        self.assertEqual(c['bits'][2]['verdict'], 'late-rise')

    def test_main_fails_when_no_capture_is_complete(self):
        with tempfile.TemporaryDirectory() as d:
            dump = Path(d) / 'probe.txt'
            dump.write_text('DIGIN 8\n0a\n0a\nEND\n')  # 2 of 8 samples: the port opened mid-dump
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = pair_skew.main(['pair_skew.py', '--json', str(dump)])
            self.assertEqual(rc, 1)
            self.assertEqual(json.loads(out.getvalue()), [])
            self.assertIn('no complete capture', err.getvalue())

    def test_negative_control_no_pair_structure(self):
        rng = random.Random(1)
        s = [rng.randrange(64) for _ in range(4096)]  # no pair structure at all
        c = pair_skew.analyze('random', s)
        self.assertFalse(c['structure'])
        self.assertEqual([b['verdict'] for b in c['bits']], ['none'] * 6)
        self.assertIn('NO pair structure', pair_skew.format_text('random', [c]))

    def test_read_captures_dump_and_plain_hex(self):
        with tempfile.TemporaryDirectory() as d:
            dump = Path(d) / 'probe.txt'
            dump.write_text('CAP 1 2 3\nDIGIN 4\n0a\n0a\n1c\n1c\nEND\nDIGIN 8\n0a\nEND\n')
            caps = pair_skew.read_captures(dump)
            self.assertEqual(len(caps), 1)  # the second capture is incomplete (2 of 8): skipped
            self.assertEqual(caps[0][1], [0x0A, 0x0A, 0x1C, 0x1C])
            hexf = Path(d) / 'plain.hex'
            hexf.write_text('1a\n1a\n18\n1c\n')
            caps = pair_skew.read_captures(hexf)
            self.assertEqual(len(caps), 1)
            self.assertEqual(caps[0][1], [0x1A, 0x1A, 0x18, 0x1C])

    def test_main_json(self):
        rng = random.Random(3)
        unique = [rng.randrange(64) for _ in range(512)]
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 's.hex'
            f.write_text('\n'.join(f'{v:02x}' for v in late_rise(unique, 5)))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = pair_skew.main(['pair_skew.py', '--json', str(f)])
            self.assertEqual(rc, 0)
            data = json.loads(buf.getvalue())
            self.assertEqual(data[0]['captures'][0]['bits'][5]['verdict'], 'late-rise')


FIXTURE_CANDIDATES = [
    Path(__file__).resolve().parents[2] / '..' / 'OpenVRX-Core' / 'gateware' / 'vectors' / 'digin_bench_2026-10-28_1251.hex',
    Path(__file__).resolve().parents[2] / '..' / 'github__LAP87__OpenVRX-Core' / 'gateware' / 'vectors' / 'digin_bench_2026-10-28_1251.hex',
]
FIXTURE = next((p for p in FIXTURE_CANDIDATES if p.exists()), None)


@unittest.skipUnless(FIXTURE, 'Core fixture digin_bench_2026-10-28_1251.hex not next to the hub')
class Fixture(unittest.TestCase):
    def test_bench_fixture_2026_10_28_1251(self):
        # measured 2026-11-03: phase 0, bit 2 second-only 3557/32768 (10.855 %), rest 0
        c = pair_skew.analyze_file(str(FIXTURE))[0]
        self.assertEqual((c['samples'], c['pairs'], c['phase']), (65536, 32768, 0))
        self.assertTrue(c['structure'])
        self.assertEqual(c['code_mismatch'], 3557)
        b2 = c['bits'][2]
        self.assertEqual((b2['first_only'], b2['second_only'], b2['verdict']), (0, 3557, 'late-rise'))
        for k in (0, 1, 3, 4, 5):
            self.assertEqual(c['bits'][k]['verdict'], 'symmetric')
            self.assertEqual(c['bits'][k]['first_only'] + c['bits'][k]['second_only'], 0)


if __name__ == '__main__':
    unittest.main()
