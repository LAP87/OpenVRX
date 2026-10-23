"""Tests for tools/bench/c5.py: the T parser on the three saved console logs, and the daemon against a pretend
C5VRX on a pty (no board). Negative control: a damaged line of a known kind raises ParseError.

    python -m unittest discover -s tools/bench -p 'test_*.py'      # in WSL
"""
import json
import os
import socket
import sys
import tempfile
import threading
import time
import tty
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c5  # noqa: E402

FIX = HERE / 'fixtures'
LOG_1150 = FIX / 'c5vrx-2026-10-22T11-50-16-884Z.log'        # 5.0.363, T after start, A1, no camera
LOG_1214 = FIX / 'c5vrx-2026-10-22T12-14-37-907Z.log'        # FIELD_TRACE flood with dropouts (Chrome's 120 kB cap)
LOG_0951 = FIX / 'c5vrx-2026-10-23T09-51-47-430Z.log'        # 5.0.402, first-start filter calibration, E2


def lines(p):
    return p.read_text(encoding='utf-8', errors='replace').split('\n')


class Parser(unittest.TestCase):
    def test_status_after_start_no_camera(self):
        s = c5.status(lines(LOG_1150))
        self.assertEqual((s['fw'], s['channel'], s['freq'], s['afc_locked'], s['detected']),
                         ('5.0.363', 'A1', 5865, 0, 'none'))
        self.assertEqual((s['cn_db'], s['carrier_dbm'], s['output_level']), (-99.0, -94.1, 1.0))
        self.assertEqual((s['stage'], s['startup'], s['busy'], s['hb_t_s']), ('ready', 0, 0, 140))
        self.assertEqual((s['filter']['bw'], s['filter']['code'], s['filter']['state']), ('BW40', -1, 'carrier_detected'))

    def test_status_during_filter_calibration(self):
        s = c5.status(lines(LOG_0951))
        self.assertEqual((s['fw'], s['channel'], s['freq'], s['detected'], s['cn_db'], s['carrier_dbm']),
                         ('5.0.402', 'E2', 5685, 'NTSC', 26.8, -69.9))
        self.assertEqual((s['startup'], s['busy'], s['menu']), (1, 1, 1))
        self.assertEqual(s['filter_cal_count'], 14)
        self.assertTrue(all(c['bw'] == 'BW40' and isinstance(c['nbw_khz'], int) for c in s['filter_cal']))

    def test_field_diag_events_and_flood(self):
        ls = lines(LOG_1214)
        s = c5.status(ls)
        self.assertEqual(s['last_field_diag_event'], {'event': 'recovered', 't': 1597, 'category': 'CALIBRATION_OR_PHY',
                                                      'duration_s': '5'})
        self.assertIsNone(s['channel'])                    # no T in that log
        trace = [ln for ln in ls if c5.is_trace(ln)]
        self.assertEqual(len(trace), 242)
        self.assertFalse(any(c5.is_trace(ln) for ln in ls if ln.startswith('FIELD_DIAG_EVENT')))

    def test_value_running_over_words_and_comment(self):
        d = c5.kv('CONTROL channel=A1 mode=DEFAULT 12MHZ KP0.85 kp_auto=2 (a comment=1)')
        self.assertEqual(d, {'channel': 'A1', 'mode': 'DEFAULT 12MHZ KP0.85', 'kp_auto': '2'})

    def test_negative_control_damaged_lines(self):
        good = lines(LOG_0951)
        for kind, old, new in (('CONTROL', 'freq=5685', 'freq=56#5'), ('CONTROL', 'channel=E2', 'channel=E9'),
                               ('RX_LEVEL', 'cn_db=26.8', 'cn_db=2.6.8'), ('HB', 'startup=1', 'startup=x'),
                               ('OUTPUT', 'level=1.0x', 'level=1.0'), ('FIRMWARE', 'version=5.0.402', 'version=5.0'),
                               ('CONTROL', 'afc_locked=0 ', 'afc_lockd=0 ')):
            bad = [ln.replace(old, new, 1) if ln.startswith(kind + ' ') else ln for ln in good]
            self.assertNotEqual(bad, good, (kind, old))
            with self.assertRaises(c5.ParseError, msg=(kind, old)):
                c5.status(bad)
        with self.assertRaises(c5.ParseError):
            c5.parse_line('FIELD_DIAG_EVENT recovered t=15x7 category=X')


T_BLOCK = [ln for ln in lines(LOG_0951) if ln.split(' ', 1)[0] in c5.FIELDS or ln.startswith(('C5VRX5', 'GAIN'))]


def pretend_c5(master, stop):
    """Answers T with LOG_0951's status lines (channel and level as set by b / c / g), sends a FIELD_TRACE line
    and a heartbeat now and then."""
    bands, ch, band, level = 'ABEFRL', 2, 2, 1.0
    os.set_blocking(master, False)
    n = 0
    while not stop.is_set():
        try:
            for b in os.read(master, 64):
                k = chr(b)
                if k == 'b':
                    band = (band + 1) % len(bands)
                elif k == 'c':
                    ch = ch % 8 + 1
                elif k == 'g':
                    level = 0.5 if level >= 5.0 else level + 0.5
                elif k == 'T':
                    for ln in T_BLOCK:
                        ln = ln.replace('channel=E2', f'channel={bands[band]}{ch}').replace('level=1.0x', f'level={level}x')
                        os.write(master, (ln + '\r\n').encode())
        except BlockingIOError:
            pass
        n += 1
        if n % 10 == 0:
            os.write(master, b'FIELD_TRACE t=1 t_ms=1000 sync_valid_pct=0\r\n')
            os.write(master, f'HB t_s={n} stage=ready gain=83 menu=0 startup=0 busy=0\r\n'.encode())
        time.sleep(0.02)


@unittest.skipUnless(hasattr(socket, 'AF_UNIX') and hasattr(os, 'openpty'), 'needs a pty and Unix sockets')
class DaemonOnPty(unittest.TestCase):
    def test_status_workflows_and_logs(self):
        master, slave = os.openpty()
        tty.setraw(slave)
        stop = threading.Event()
        threading.Thread(target=pretend_c5, args=(master, stop), daemon=True).start()
        with tempfile.TemporaryDirectory() as d:
            dm = c5.Daemon(os.ttyname(slave), d)
            threading.Thread(target=dm.serve, daemon=True).start()
            for _ in range(50):
                if (Path(d) / 'c5.sock').exists():
                    break
                time.sleep(0.05)
            r = c5.request(d, {'op': 'status'})
            self.assertTrue(r['ok'], r)
            self.assertEqual((r['status']['channel'], r['status']['output_level']), ('E2', 1.0))
            c5.step_until(d, 'c', lambda s: s['channel'], 'E4', 8)
            c5.step_until(d, 'b', lambda s: s['channel'][0], 'R', 8)
            c5.step_until(d, 'g', lambda s: s['output_level'], 2.0, 10)
            r = c5.request(d, {'op': 'status'})
            self.assertEqual((r['status']['channel'], r['status']['output_level']), ('R4', 2.0))
            with self.assertRaises(SystemExit):                     # E9 does not exist: gives up after 8
                c5.step_until(d, 'c', lambda s: s['channel'], 'R9', 8)
            time.sleep(0.5)
            full = (Path(d) / 'full.log').read_text()
            short = (Path(d) / 'short.log').read_text()
            self.assertIn('FIELD_TRACE', full)
            self.assertNotIn('FIELD_TRACE', short)
            self.assertIn('CONTROL channel=R4', short)
            stop.set()
        os.close(master)
        os.close(slave)


if __name__ == '__main__':
    unittest.main()
