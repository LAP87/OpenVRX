#!/usr/bin/env python3
"""C5VRX console from WSL (XIAO ESP32-C5 on its USB-serial-JTAG port, cdc_acm): daemon, status as JSON, workflows.

    c5.py parse tools/bench/fixtures/c5vrx-2026-10-23T09-51-47-430Z.log     # status from a saved log
    c5.py daemon [--port /dev/ttyACM0] [--dir DIR]   # hold the port, log everything, take commands on a socket
    c5.py status                                     # send T through the daemon, print the parsed status
    c5.py send T                                     # raw keys through the daemon
    c5.py channel A2                                 # b / c until CONTROL says A2
    c5.py level 1.5                                  # g until OUTPUT says 1.5x
    c5.py calibrate                                  # F with the transmitter off (asks), waits for startup=0 busy=0
    c5.py reboot --i-know / c5.py download --i-know  # drive DTR/RTS (daemon stopped); see the warning they print

The port is opened once and its modem lines are not touched afterwards: Linux's cdc_acm raises DTR and RTS
together when the port opens and, with HUPCL, drops them together when the last handle closes; on the ESP32-C5's
USB-serial-JTAG port equal lines neither reset the chip nor select the download mode. Only `reboot` and `download`
set the lines, on purpose. What is observed and what is assumed about this: hub docs/BENCH.md, "C5VRX-konsolen".

The daemon appends every line to DIR/full.log and the lines without FIELD_TRACE / FIELD_DIAG (but with
FIELD_DIAG_EVENT) to DIR/short.log, each with the arrival time, and answers JSON requests on the Unix socket
DIR/c5.sock, or under /tmp when DIR is a Windows drive under /mnt, which cannot hold a socket (one request per
connection): {"op": "send", "keys": "T"}, {"op": "status"} (sends T and parses the
answer), {"op": "tail", "n": 40}. DIR defaults to the hub's ../bench-logs/c5vrx. Linux only (termios, AF_UNIX);
`parse` works anywhere. Not run against the board yet (hub docs/NATTPASS_2026-10-23.md, task 56).
"""
import argparse
import glob
import json
import os
import re
import socket
import sys
import threading
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

HUB = Path(__file__).resolve().parents[2]
TRACE = ('FIELD_TRACE', 'FIELD_DIAG')                  # flood lines kept only in full.log
KV = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)=("[^"]*"|\S*)')


class ParseError(ValueError):
    pass


def default_dir():
    return Path(os.environ.get('OPENVRX_BENCH_LOGS', HUB.parent / 'bench-logs')) / 'c5vrx'


def sock_path(d):
    """The daemon's socket for the log directory d. A Windows drive under /mnt (DrvFs) cannot hold an AF_UNIX
    socket ("Operation not supported", bench 2026-10-27), so such a directory gets its socket under /tmp."""
    import hashlib
    d = Path(d)
    if str(d).startswith('/mnt/'):
        return Path('/tmp') / f'openvrx-c5vrx-{hashlib.md5(str(d).encode()).hexdigest()[:8]}.sock'
    return d / 'c5.sock'


def is_trace(line):
    k = line.split(' ', 1)[0]
    return k in TRACE


def kv(line):
    """The key=value pairs after the line's first word. A value runs on over following words without '=' (e.g.
    mode=DEFAULT 12MHZ KP0.85); a word starting with '(' begins the firmware's comment and ends the pairs."""
    words = line.split(' ')[1:]
    out, last = {}, None
    for w in words:
        if not w:
            continue
        if w.startswith('('):
            break
        m = KV.fullmatch(w)
        if m:
            last = m[1]
            out[last] = m[2]
        elif last is not None:
            out[last] += ' ' + w
    return {k: v.strip('"') for k, v in out.items()}


def _num(v, kind, key, line, pattern, conv):
    if v is None or not re.fullmatch(pattern, v):
        raise ParseError(f'{kind}: {key}={v!r} in {line[:120]!r}')
    return conv(v)


INT, FLOAT, BIT = (r'-?\d+', int), (r'-?\d+(\.\d+)?', float), (r'[01]', int)
# per line kind: the fields read, with the pattern each must match (a damaged line raises ParseError)
FIELDS = {
    # private builds say version=5.0.0-dev and commit=<sha>-dirty (bench 2026-10-27)
    'FIRMWARE': {'version': (r'\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?', str), 'commit': (r'[0-9a-f]{7,40}(-dirty)?', str),
                 'id': (r'\S+', str)},
    'CONTROL': {'channel': (r'[A-Z][1-8]', str), 'freq': (r'\d{4}', int), 'afc_locked': BIT, 'standard': (r'\w+', str),
                'detected': (r'\w+', str), 'signal': INT, 'menu': BIT, 'busy': BIT, 'cfo_khz': INT,
                'offset_khz': INT},
    'RX_LEVEL': {'carrier_dbm': FLOAT, 'input_dbm': FLOAT, 'noise_dbm': FLOAT, 'cn_db': FLOAT,
                 'above_noise': BIT, 'gains': (r'\d+-\d+', str)},
    'OUTPUT': {'level': (r'\d+(\.\d+)?x', lambda v: float(v[:-1])), 'live': BIT},
    'HB': {'t_s': INT, 'stage': (r'[a-z_]+', str), 'gain': INT, 'menu': BIT, 'startup': INT, 'busy': BIT},
    'FILTER_CAL': {'bw': (r'BW\d+', str), 'code': INT, 'skirt': INT, 'width_khz': INT, 'nbw_khz': INT},
    'FILTER': {'bw': (r'BW\d+', str), 'code': INT, 'calibrated_nbw_khz': INT},
}
OPTIONAL = {'CONTROL': {'busy', 'cfo_khz', 'offset_khz'}, 'OUTPUT': {'live'}, 'FIRMWARE': {'commit', 'id'},
            'FILTER_CAL': {'skirt', 'width_khz', 'nbw_khz'}, 'RX_LEVEL': {'input_dbm', 'above_noise', 'gains'}}


def parse_line(line):
    """(kind, dict) for a line of a known kind, (kind, None) for any other line. Raises ParseError when a known
    line lacks a field or has a value of the wrong form."""
    line = line.rstrip('\r\n')
    kind = line.split(' ', 1)[0]
    if kind == 'FIELD_DIAG_EVENT':
        parts = line.split(' ')
        if len(parts) < 3 or not re.fullmatch(r'[a-z_]+', parts[1]):
            raise ParseError(f'FIELD_DIAG_EVENT: {line[:120]!r}')
        d = kv(line)
        if 't' not in d or not re.fullmatch(r'\d+', d['t']):
            raise ParseError(f'FIELD_DIAG_EVENT: t in {line[:120]!r}')
        rec = {'event': parts[1], 't': int(d['t'])}
        for k in ('category', 'duration_s', 'channel', 'freq', 'sync_valid_pct', 'cn_est_x10'):
            if k in d:
                rec[k] = d[k]
        return kind, rec
    spec = FIELDS.get(kind)
    if spec is None:
        return kind, None
    d = kv(line)
    rec = {}
    for key, (pattern, conv) in spec.items():
        if key not in d and key in OPTIONAL.get(kind, ()):
            continue
        rec[key] = _num(d.get(key), kind, key, line, pattern, conv)
    if kind == 'FILTER':
        rec['state'] = line.split(' ')[1] if len(line.split(' ')) > 1 else None
    return kind, rec


def status(lines):
    """The status a T answer (and the heartbeat lines around it) gives, as one dict; None for fields not seen.

    Uses the last line of each kind. Raises ParseError on a damaged line of a known kind."""
    last, cal, event = {}, [], None
    for ln in lines:
        kind, rec = parse_line(ln)
        if rec is None:
            continue
        if kind == 'FILTER_CAL':
            cal.append(rec)
        elif kind == 'FIELD_DIAG_EVENT':
            event = rec
        else:
            last[kind] = rec
    g = lambda kind, key: last.get(kind, {}).get(key)  # noqa: E731
    return {
        'fw': g('FIRMWARE', 'version'), 'fw_commit': g('FIRMWARE', 'commit'),
        'channel': g('CONTROL', 'channel'), 'freq': g('CONTROL', 'freq'), 'afc_locked': g('CONTROL', 'afc_locked'),
        'standard': g('CONTROL', 'standard'), 'detected': g('CONTROL', 'detected'), 'menu': g('CONTROL', 'menu'),
        'cn_db': g('RX_LEVEL', 'cn_db'), 'carrier_dbm': g('RX_LEVEL', 'carrier_dbm'),
        'noise_dbm': g('RX_LEVEL', 'noise_dbm'), 'gains': g('RX_LEVEL', 'gains'),
        'stage': g('HB', 'stage'), 'startup': g('HB', 'startup'),
        'busy': g('HB', 'busy') if 'HB' in last else g('CONTROL', 'busy'), 'hb_t_s': g('HB', 't_s'),
        'output_level': g('OUTPUT', 'level'),
        'filter': last.get('FILTER'), 'filter_cal': cal[-12:], 'filter_cal_count': len(cal),
        'last_field_diag_event': event,
    }


# ---------------------------------------------------------------- port and daemon

def find_port():
    hits = sorted(glob.glob('/dev/serial/by-id/usb-Espressif*'))
    return hits[0] if hits else '/dev/ttyACM0'


def open_port(path):
    import termios
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY)        # cdc_acm raises DTR and RTS together here
    a = termios.tcgetattr(fd)
    a[0] = a[1] = a[3] = 0
    a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL | (a[2] & termios.HUPCL)
    a[4] = a[5] = termios.B115200                       # ignored by USB-serial-JTAG, kept for form
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 2
    termios.tcsetattr(fd, termios.TCSANOW, a)
    return fd


def now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


class Daemon:
    def __init__(self, port, d):
        self.port, self.dir = port, Path(d)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.lines = deque(maxlen=4000)                 # (seq, time, line)
        self.seq = 0
        self.lock = threading.Lock()
        self.fd = None

    def reader(self):
        full = open(self.dir / 'full.log', 'a')
        short = open(self.dir / 'short.log', 'a')
        buf = b''
        while True:
            try:
                chunk = os.read(self.fd, 4096)
            except OSError:                             # the device went away: reopen when it is back
                os.close(self.fd)
                while True:
                    time.sleep(1)
                    try:
                        self.fd = open_port(self.port)
                        break
                    except OSError:
                        continue
                continue
            buf += chunk
            while b'\n' in buf:
                raw, buf = buf.split(b'\n', 1)
                line = raw.decode('ascii', 'replace').rstrip('\r')
                t = now()
                with self.lock:
                    self.seq += 1
                    self.lines.append((self.seq, t, line))
                full.write(f'{t} {line}\n')
                full.flush()
                if not is_trace(line):
                    short.write(f'{t} {line}\n')
                    short.flush()

    def send(self, keys):
        os.write(self.fd, keys.encode('ascii'))

    def since(self, seq):
        with self.lock:
            return [x for x in self.lines if x[0] > seq]

    def ask_status(self, timeout=6.0, quiet=0.8):
        """Send T, collect lines until `quiet` seconds without a new answer line (or `timeout`), parse them."""
        with self.lock:
            start = self.seq
        self.send('T')
        end, last_n, last_t = time.monotonic() + timeout, 0, time.monotonic()
        while time.monotonic() < end:
            time.sleep(0.05)
            # the answer's lines only: the trace flood and the heartbeat go on all the time
            got = [x for x in self.since(start) if not is_trace(x[2]) and not x[2].startswith('HB ')]
            if len(got) != last_n:
                last_n, last_t = len(got), time.monotonic()
            elif last_n and time.monotonic() - last_t > quiet:
                break
        got = [ln for _, _, ln in self.since(start) if not is_trace(ln)]
        with self.lock:                                 # the latest heartbeat too, if T did not bring one
            hb = [ln for _, _, ln in self.lines if ln.startswith('HB ')][-1:]
        try:
            return {'ok': bool(got), 'status': status(hb + got), 'lines': len(got)}
        except ParseError as e:
            return {'ok': False, 'error': str(e), 'lines': len(got)}

    def serve(self):
        self.fd = open_port(self.port)
        threading.Thread(target=self.reader, daemon=True).start()
        path = sock_path(self.dir)
        if path.exists():
            path.unlink()
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        srv.bind(str(path))
        srv.listen(4)
        print(f'c5 daemon on {self.port}, socket {path}, logs in {self.dir}', flush=True)
        while True:
            conn, _ = srv.accept()
            with conn:
                try:
                    req = json.loads(conn.makefile().readline())
                    op = req.get('op')
                    if op == 'send':
                        self.send(req['keys'])
                        res = {'ok': True}
                    elif op == 'status':
                        res = self.ask_status(float(req.get('timeout', 6)))
                    elif op == 'tail':
                        with self.lock:
                            res = {'ok': True, 'lines': [f'{t} {ln}' for _, t, ln in list(self.lines)
                                                         if not is_trace(ln)][-int(req.get('n', 40)):]}
                    else:
                        res = {'ok': False, 'error': f'unknown op {op!r}'}
                except (ValueError, KeyError, OSError) as e:
                    res = {'ok': False, 'error': str(e)}
                conn.sendall((json.dumps(res) + '\n').encode())


def request(d, req, timeout=30):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(str(sock_path(d)))
    except OSError as e:
        raise SystemExit(f'no c5 daemon at {sock_path(d)} ({e}); start it with: c5.py daemon')
    with s:
        s.sendall((json.dumps(req) + '\n').encode())
        return json.loads(s.makefile().readline())


def step_until(d, key, read, want, limit):
    """Press `key` until read(status) == want, at most `limit` times; the statuses seen."""
    seen = []
    for _ in range(limit + 1):
        r = request(d, {'op': 'status'})
        if not r['ok']:
            raise SystemExit(f"status failed: {r.get('error')}")
        v = read(r['status'])
        seen.append(v)
        if v == want:
            return seen
        request(d, {'op': 'send', 'keys': key})
        time.sleep(0.5)
    raise SystemExit(f'{want!r} not reached after {limit} presses of {key!r}: {seen}')


def set_lines(port, steps):
    """steps: [(dtr, rts, seconds)], each pair set in one TIOCMSET (one control request on cdc_acm)."""
    import fcntl
    import struct
    import termios
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
    try:
        for dtr, rts, sec in steps:
            v = struct.unpack('I', fcntl.ioctl(fd, termios.TIOCMGET, struct.pack('I', 0)))[0]
            v = (v & ~(termios.TIOCM_DTR | termios.TIOCM_RTS)) | (termios.TIOCM_DTR if dtr else 0) | \
                (termios.TIOCM_RTS if rts else 0)
            fcntl.ioctl(fd, termios.TIOCMSET, struct.pack('I', v))
            time.sleep(sec)
    finally:
        os.close(fd)


# Line states as Espressif documents the ESP32 USB-serial-JTAG port's reset and boot logic: RTS asserted alone holds
# the chip in reset, DTR asserted alone pulls the boot strap; equal lines do nothing. Not tried on our XIAO.
REBOOT = [(0, 0, 0.1), (0, 1, 0.1), (0, 0, 0.1)]                    # reset pulse, boot strap released
DOWNLOAD = [(0, 0, 0.1), (1, 0, 0.1), (0, 1, 0.1), (0, 0, 0.1)]      # strap, reset, release: ROM download mode
WARNING = ('This drives DTR/RTS of the XIAO ESP32-C5 on purpose. On 2026-10-23 line changes from Windows left the '
           'chip silent in the ROM download mode until its power was cut (hub docs/BANK_2026-10-23.md). Use it only '
           'with someone at the bench who can unplug the board.')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dir', default=str(default_dir()))
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('parse')
    p.add_argument('log')
    p = sub.add_parser('daemon')
    p.add_argument('--port', default=None)
    sub.add_parser('status')
    p = sub.add_parser('send')
    p.add_argument('keys')
    p = sub.add_parser('tail')
    p.add_argument('-n', type=int, default=40)
    p = sub.add_parser('channel')
    p.add_argument('name', help='e.g. A2')
    p = sub.add_parser('level')
    p.add_argument('x', type=float, help='0.5 .. 5.0 in 0.5 steps')
    p = sub.add_parser('calibrate')
    p.add_argument('--minutes', type=float, default=15)
    for name in ('reboot', 'download'):
        p = sub.add_parser(name)
        p.add_argument('--port', default=None)
        p.add_argument('--i-know', action='store_true')
    a = ap.parse_args(argv)
    if a.cmd == 'parse':
        text = Path(a.log).read_text(encoding='utf-8', errors='replace').split('\n')
        print(json.dumps(status(text), indent=2))
        return 0
    if a.cmd == 'daemon':
        Daemon(a.port or find_port(), a.dir).serve()
        return 0
    if a.cmd == 'status':
        r = request(a.dir, {'op': 'status'})
        print(json.dumps(r, indent=2))
        return 0 if r['ok'] else 1
    if a.cmd == 'send':
        print(json.dumps(request(a.dir, {'op': 'send', 'keys': a.keys})))
        return 0
    if a.cmd == 'tail':
        print('\n'.join(request(a.dir, {'op': 'tail', 'n': a.n})['lines']))
        return 0
    if a.cmd == 'channel':
        if not re.fullmatch(r'[A-Z][1-8]', a.name):
            ap.error('channel like A2')
        step_until(a.dir, 'b', lambda s: (s['channel'] or '?')[0], a.name[0], 8)
        seen = step_until(a.dir, 'c', lambda s: s['channel'], a.name, 8)
        print(json.dumps({'ok': True, 'channel': seen[-1]}))
        return 0
    if a.cmd == 'level':
        if not (0.5 <= a.x <= 5.0 and (a.x * 2).is_integer()):
            ap.error('level 0.5 .. 5.0 in 0.5 steps')
        seen = step_until(a.dir, 'g', lambda s: s['output_level'], a.x, 10)
        print(json.dumps({'ok': True, 'output_level': seen[-1]}))
        return 0
    if a.cmd == 'calibrate':
        print('The filter calibration needs the video transmitter OFF (C5VRX: F, first-start steps again).')
        if input('Is the transmitter off? Type ja: ').strip().lower() != 'ja':
            print('not started')
            return 1
        request(a.dir, {'op': 'send', 'keys': 'F'})
        end = time.monotonic() + a.minutes * 60
        while time.monotonic() < end:
            time.sleep(5)
            r = request(a.dir, {'op': 'status'})
            s = r.get('status') or {}
            print(json.dumps({k: s.get(k) for k in ('stage', 'startup', 'busy', 'hb_t_s', 'filter_cal_count')}),
                  flush=True)
            if s.get('startup') == 0 and s.get('busy') == 0 and s.get('filter_cal_count'):
                print(json.dumps({'ok': True, 'filter_cal': s['filter_cal']}))
                return 0
        print('calibration not finished in time')
        return 1
    if a.cmd in ('reboot', 'download'):
        print(WARNING)
        if not a.i_know:
            print('refused: add --i-know')
            return 1
        if sock_path(a.dir).exists():
            try:
                request(a.dir, {'op': 'tail', 'n': 1}, timeout=2)
                print('refused: the daemon holds the port; stop it first')
                return 1
            except SystemExit:
                pass
        set_lines(a.port or find_port(), REBOOT if a.cmd == 'reboot' else DOWNLOAD)
        print('done')
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
