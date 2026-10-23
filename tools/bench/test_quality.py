"""Tests for tools/bench/quality.py on synthetic captures (no grabber needed).

Synthetic pictures are built the way M4/M6 show a field: 720 luma samples per source line widened to the 960-pixel
4:3 window, each source line on three rows, grey ramps beside it, YCbCr turned into full-range RGB. Negative
controls: a dark but textured picture is not black, a constant hue gives no hue spread, a clean picture has no
repeated line, M0's bars shifted by 20 fail the calibration, a PNG with a broken CRC is refused.

    python -m unittest discover -s tools/bench -p 'test_*.py'
"""
import math
import os
import random
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import quality as q  # noqa: E402

CORE = Path(os.environ.get('OPENVRX_CORE', HERE.parents[2] / 'OpenVRX-Core'))


def rgb(y, cb, cr):
    c, d, e = y - 16, cb - 128, cr - 128
    clip = lambda v: max(0, min(255, int(round(v))))  # noqa: E731
    return clip(1.164 * c + 1.596 * e), clip(1.164 * c - 0.392 * d - 0.813 * e), clip(1.164 * c + 2.017 * d)


def picture(line_fn, cb=128, cr=128, lines=240, repeat=None):
    """line_fn(line) -> 720 luma samples. repeat: a source line shown again in place of the next one."""
    rows = []
    for ln in range(lines):
        src = line_fn(repeat if repeat is not None and ln == repeat + 1 else ln)
        row = bytearray()
        for x in range(1280):
            if 160 <= x < 1120:
                row += bytes(rgb(src[(x - 160) * 720 // 960], cb, cr))
            else:
                row += bytes([ln % 64] * 3)
        rows += [bytes(row)] * (720 // lines)
    return 1280, 720, rows


def noisy(sigma, base=120, seed=1):
    rnd = random.Random(seed)
    return lambda ln: [max(16, min(235, int(base + rnd.gauss(0, sigma)))) if sigma else base for _ in range(720)]


class Measures(unittest.TestCase):
    def test_snow_follows_noise(self):
        snow = [q.frame_metrics(*picture(noisy(s)))['snow'] for s in (0, 4, 12)]
        self.assertEqual(snow[0], 0)
        self.assertTrue(snow[0] < snow[1] < snow[2], snow)

    def test_black_and_dark_textured(self):
        self.assertTrue(q.frame_metrics(*picture(noisy(0, base=16)))['black'])
        self.assertFalse(q.frame_metrics(*picture(noisy(6, base=22)))['black'], 'negative control: texture')

    def test_hue_drift_and_constant_hue(self):
        def frames(degs):
            out = []
            for d in degs:
                cb = 128 + round(40 * math.cos(math.radians(d)))
                cr = 128 + round(40 * math.sin(math.radians(d)))
                out.append(q.frame_metrics(*picture(noisy(0), cb, cr, lines=60), color_window=(400, 200, 300, 200)))
            return q.series(out)
        drift = frames([0, 30, 60, 90])
        still = frames([45, 45, 45, 45])
        self.assertGreater(drift['hue_std'], 20)
        self.assertLess(still['hue_std'], 1, 'negative control: constant hue')
        self.assertAlmostEqual(q.frame_metrics(*picture(noisy(0), 128 + 28, 128 + 28, lines=60))['hue'], 45, delta=3)

    def test_repeated_line(self):
        fn = lambda ln: [16 + (ln * 7 + x) % 200 for x in range(720)]  # noqa: E731  every line different
        self.assertEqual(q.frame_metrics(*picture(fn, repeat=100))['repeated_lines'], 1)
        clean = q.frame_metrics(*picture(fn))
        self.assertEqual((clean['repeated_lines'], clean['source_lines'], clean['usual_run']), (0, 240, 3))

    def test_series_black_share(self):
        f = [q.frame_metrics(*picture(noisy(0, base=16), lines=60)), q.frame_metrics(*picture(noisy(5), lines=60))]
        s = q.series(f)
        self.assertEqual((s['pictures'], s['black_share']), (2, 0.5))

    @unittest.skipUnless((CORE / 'gateware' / 'model' / 'bt656.py').is_file(), 'needs the Core checkout')
    def test_hf_is_the_mixers(self):
        """The same line through Core's BT.656 model gives the same HF energy."""
        sys.path.insert(0, str(CORE / 'gateware' / 'model'))
        import bt656
        luma = noisy(10, seed=7)(0)
        active = bytes(v for y in luma for v in (128, y))
        rx = bt656.Receiver()
        rx.feed(bt656.line_bytes('ntsc', 30, active) * 2)
        self.assertEqual(rx.records[0].hf_energy, q.hf_energy(luma))


def m0_picture(shift=0):
    rows = []
    for y in range(720):
        row = bytearray()
        for x in range(1280):
            if 300 <= x < 364 and 500 <= y < 564:
                px = (0xFF, 0x80, 0x00)                     # the bouncing square
            elif 160 <= x < 1120 and (x in (160, 1119) or y in (0, 719)):
                px = (255, 255, 255)
            elif 160 <= x < 1120:
                px = tuple(min(255, v + shift) for v in q.m0_bar((x - 160) // 120))
            else:
                px = ((y & 0xFF) >> 3,) * 3
            row += bytes(px)
        rows.append(bytes(row))
    return 1280, 720, rows


class Calibration(unittest.TestCase):
    def test_m0_bars(self):
        self.assertTrue(q.calibrate(*m0_picture())['ok'])
        r = q.calibrate(*m0_picture(shift=20))
        self.assertFalse(r['ok'], 'negative control: colours off by 20')


class Png(unittest.TestCase):
    def encode(self, w, h, rows, filt):
        bpp, out, prev = 3, b'', bytes(3 * w)
        for r in rows:
            line = bytearray()
            for i, v in enumerate(r):
                a = r[i - bpp] if i >= bpp else 0
                b, c = prev[i], prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = [0, a, b, (a + b) >> 1, a if pa <= pb and pa <= pc else b if pb <= pc else c][filt]
                line.append((v - pred) & 0xFF)
            out += bytes([filt]) + bytes(line)
            prev = r

        def chunk(tag, body):
            return struct.pack('>I', len(body)) + tag + body + struct.pack('>I', zlib.crc32(tag + body) & 0xFFFFFFFF)
        return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(out)) + chunk(b'IEND', b''))

    def test_all_filters_and_broken_crc(self):
        rnd = random.Random(3)
        rows = [bytes(rnd.randrange(256) for _ in range(3 * 17)) for _ in range(5)]
        with tempfile.TemporaryDirectory() as d:
            for f in range(5):
                p = Path(d) / f'f{f}.png'
                p.write_bytes(self.encode(17, 5, rows, f))
                self.assertEqual(q.read_png(p), (17, 5, rows), f)
            bad = bytearray(self.encode(17, 5, rows, 4))
            bad[40] ^= 1
            (Path(d) / 'bad.png').write_bytes(bytes(bad))
            with self.assertRaises(ValueError):
                q.read_png(Path(d) / 'bad.png')

    def test_measure_cli_writes_report_and_sheet(self):
        with tempfile.TemporaryDirectory() as d:
            for k, s in enumerate((0, 8)):
                w, h, rows = picture(noisy(s), lines=60)
                q.write_png(Path(d) / f'frame_{k:03d}.png', w, h, rows)
            out, sheet = Path(d) / 'r.json', Path(d) / 'sheet.png'
            self.assertEqual(q.main(['measure', d, '--out', str(out), '--sheet', str(sheet)]), 0)
            self.assertIn('"snow_mean"', out.read_text())
            self.assertEqual(q.read_png(sheet)[:2], (1280, 180))


if __name__ == '__main__':
    unittest.main()
