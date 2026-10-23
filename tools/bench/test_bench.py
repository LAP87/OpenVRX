"""Tests for the bench rig's parsers and checks (no board needed).

    python -m unittest discover -s tools/bench -p 'test_*.py'      # from the hub, in WSL (termios)
"""
import hashlib
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bench  # noqa: E402
import m3probe  # noqa: E402

PROBE_OK = 'A sclk 27000064 tog FF hi FF len 1716-1716 ln 14565 fld 060 xe 0000 i2c 5C st 000E ri 00'
PROBE_DEAD = 'B sclk 00000000 no SCLK' + ' ' * 44 + ' i2c -- st ---- ri 00'
# the bench of 2026-10-22 (BANK_2026-10-22.md): 5D module, H and V lock without colour lock
PROBE_5D = 'A sclk 27007488 tog FF hi FF len 1716-1716 ln 14563 fld 060 xe 0000 i2c 5D st 1006 ri 00'


class M3Probe(unittest.TestCase):
    def test_bringup_example(self):
        r = m3probe.parse(PROBE_OK + '\r\n')
        self.assertEqual((r['ch'], r['sclk'], r['tog'], r['hi']), ('A', 27000064, 0xFF, 0xFF))
        self.assertEqual((r['len_min'], r['len_max'], r['ln'], r['fld'], r['xe']), (1716, 1716, 14565, 60, 0))
        self.assertEqual((r['i2c'], r['addr'], r['st'], r['ri']), ('5C', '5C', 0x000E, 0))
        self.assertTrue(r['h_lock'] and r['v_lock'] and r['color_lock'] and r['locked'])
        self.assertFalse(r['weak_signal'] or r['field_50hz'])

    def test_no_colour_lock(self):
        r = m3probe.parse(PROBE_5D)
        self.assertEqual(r['addr'], '5D')
        self.assertTrue(r['locked'])
        self.assertFalse(r['color_lock'])

    def test_dead_line(self):
        r = m3probe.parse(PROBE_DEAD)
        self.assertEqual((r['ch'], r['sclk_ok'], r['i2c'], r['addr'], r['st'], r['locked']),
                         ('B', False, '--', None, None, None))

    def test_no_lines(self):
        r = m3probe.parse(PROBE_OK.replace('len 1716-1716 ln 14565', 'len --------- ln 00000'))
        self.assertIsNone(r['len_min'])
        self.assertEqual(r['ln'], 0)

    def test_negative_control_damaged_lines(self):
        """Every single-byte loss and every changed byte of a field must be refused."""
        for i in range(len(PROBE_OK)):
            self.assertIsNone(m3probe.parse(PROBE_OK[:i] + PROBE_OK[i + 1:]), f'lost byte {i}')
        for i, c in enumerate(PROBE_OK):
            bad = PROBE_OK[:i] + ('#' if c != '#' else '$') + PROBE_OK[i + 1:]
            self.assertIsNone(m3probe.parse(bad), f'changed byte {i}')
        for i in range(len(PROBE_DEAD)):
            self.assertIsNone(m3probe.parse(PROBE_DEAD[:i] + PROBE_DEAD[i + 1:]), f'dead line, lost byte {i}')


class Devices(unittest.TestCase):
    def test_lsusb(self):
        text = ('Bus 001 Device 002: ID 0403:6010 Future Technology Devices International, Ltd FT2232C/D/H\n'
                'Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub\n')
        u = bench.parse_lsusb(text)
        self.assertEqual(u[0][:4], ('001', '002', '0403', '6010'))
        self.assertEqual(bench.KNOWN[(u[0][2], u[0][3])], 'tang')

    def test_sysfs_walk(self):
        """A fake sysfs: ttyUSB1 on interface 01 of 0403:6010, by-id link; the UART is found."""
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            dev = t / 'sys/devices/usb1/1-1'
            iface = dev / '1-1:1.1'
            (iface / 'ttyUSB1').mkdir(parents=True)
            (dev / 'idVendor').write_text('0403\n')
            (dev / 'idProduct').write_text('6010\n')
            (dev / 'serial').write_text('2025030317\n')
            (iface / 'bInterfaceNumber').write_text('01\n')
            (t / 'sys/class/tty/ttyUSB1').mkdir(parents=True)
            os.symlink(iface / 'ttyUSB1', t / 'sys/class/tty/ttyUSB1/device')
            (t / 'dev/serial/by-id').mkdir(parents=True)
            (t / 'dev/ttyUSB1').write_text('')
            link = t / 'dev/serial/by-id/usb-SIPEED_USB_Debugger_2025030317-if01-port0'
            os.symlink(t / 'dev/ttyUSB1', link)
            nodes = bench.tty_nodes(str(t / 'sys'), str(t / 'dev'))
            self.assertEqual(len(nodes), 1)
            n = nodes[0]
            self.assertEqual((n['vid'], n['pid'], n['interface'], n['serial']), ('0403', '6010', '01', '2025030317'))
            self.assertEqual(n['by_id'], str(link))
            self.assertEqual(bench.tang_uart(nodes, str(t / 'dev')), str(link))
            os.unlink(link)
            self.assertEqual(bench.tang_uart(nodes, str(t / 'dev')), n['tty'])


class Manifest(unittest.TestCase):
    def make(self, d, top='m6_puck_proto', extra=None):
        fs = d / f'{top}.fs'
        fs.write_bytes(b'bitstream bytes')
        arts = {fs.name: hashlib.sha256(fs.read_bytes()).hexdigest(), f'{top}.pnr.log': '0' * 64}
        rec = {'format_version': 1, 'completed_utc': '2026-10-23T00:00:00+00:00', 'top': top, 'bitstream': fs.name,
               'artifacts': arts, 'git': {'commit': 'abc1234', 'dirty': False},
               'options': dict({'tvp_addr': '5C'}, **(extra or {}))}
        (d / f'{top}.build.json').write_text(json.dumps(rec))
        return fs

    def test_bitstream_hash_level(self):
        with tempfile.TemporaryDirectory() as t:
            fs = self.make(Path(t))
            rec, level = bench.check_manifest(fs)
            self.assertEqual((rec['top'], level), ('m6_puck_proto', 'bitstream'))
            self.assertEqual(bench.uart_baud(rec), 115200)

    def test_negative_control_changed_bitstream(self):
        with tempfile.TemporaryDirectory() as t:
            fs = self.make(Path(t))
            fs.write_bytes(b'bitstream bytez')
            with self.assertRaises(ValueError):
                bench.check_manifest(fs)

    def test_missing_manifest(self):
        with tempfile.TemporaryDirectory() as t:
            fs = Path(t) / 'x.fs'
            fs.write_bytes(b'x')
            with self.assertRaises(ValueError):
                bench.check_manifest(fs)

    def test_resolve_and_baud(self):
        with tempfile.TemporaryDirectory() as t:
            fs = self.make(Path(t), 'm6_puck_proto_devcmd', {'uart_baud': '921600'})
            self.assertEqual(bench.resolve_bitstream('m6_puck_proto_devcmd', [t]), fs)
            rec, _ = bench.check_manifest(fs)
            self.assertEqual(bench.uart_baud(rec), 921600)
            with self.assertRaises(FileNotFoundError):
                bench.resolve_bitstream('m3_probe', [t])

    def test_family(self):
        self.assertEqual([bench.family(t) for t in ('m3_probe', 'm6_puck_proto', 'm4_dual_mix')], ['m3', 'm6', None])


@unittest.skipUnless(hasattr(os, 'openpty'), 'needs a pty')
class Capture(unittest.TestCase):
    def test_pty_lines_parsed_and_stamped(self):
        """Probe lines written into a pty arrive parsed, stamped, in JSONL; a damaged one is kept as None."""
        master, slave = os.openpty()
        name = os.ttyname(slave)
        lines = [PROBE_OK, PROBE_OK[:30] + PROBE_OK[31:], PROBE_DEAD]

        def feed():
            time.sleep(0.3)
            for ln in lines:
                os.write(master, (ln + '\r\n').encode())
                time.sleep(0.05)

        th = threading.Thread(target=feed)
        th.start()
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / 'probe.jsonl'
            rows = bench.capture(name, 115200, 1.5, m3probe.parse, str(out))
            th.join()
            recs = [json.loads(x) for x in out.read_text().splitlines()]
        os.close(master)
        os.close(slave)
        self.assertEqual([raw for _, raw, _ in rows], lines)
        self.assertEqual([r['rec'] is not None for r in recs], [True, False, True])
        self.assertTrue(all(r['t'].endswith('+00:00') for r in recs))
        s = bench.summarize('m3', [r for _, _, r in rows])
        self.assertEqual((s['parsed'], s['damaged'], s['A']['i2c'], s['B']['sclk_ok']), (2, 1, '5C', False))


if __name__ == '__main__':
    unittest.main()
