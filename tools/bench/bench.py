#!/usr/bin/env python3
"""OpenVRX bench rig, WSL side: what is plugged in, flash a checked bitstream, read the board's log.

    bench.py devices [--json] [--detect]
    bench.py flash m6_puck_proto [--build-dir DIR] [--flash] [--root]
    bench.py flash path/to/m6_puck_proto_devcmd.fs
    bench.py log m6 --seconds 20 --out run.jsonl
    bench.py log m3 --seconds 20 --out probe.jsonl
    bench.py status --json
    bench.py cmd L                      # M6 with DEVCMD=1: a command, prints the log line that shows it (m6ctl.py)
    bench.py cmd '?'                    # the status line: decoder addresses, 88h/89h, 03h
    bench.py dump D                     # field dump of decoder A to PNG under bench-logs (fielddump.py)

Runs with the Core venv's python (stdlib only). Windows side: tools/bench.ps1 keeps WSL awake, attaches the
boards with usbipd and calls this script. docs/BENCH.md in the hub has the whole sequence.

Paths (environment variables override):
  OPENVRX_CORE        Core checkout, for snowlog.py and build_manifest.py (default: ../OpenVRX-Core next to the hub)
  OPENVRX_BUILD       extra directory searched for <top>.fs before <core>/gateware/build
  OPENVRX_BENCH_LOGS  logs and state.json (default: ../bench-logs next to the hub, git-ignored)

flash checks the bitstream against its manifest (<prefix>.build.json): the bitstream's SHA-256 always, and every
other artifact through Core's build_manifest.py verify when they are all present (a bitstream copied to the
bitstreams branch has only the .fs and the manifest). It loads SRAM unless --flash is given, and records what it
loaded in state.json; log and status take the top and the UART rate from there.
"""
import argparse
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import m3probe  # noqa: E402
import serialport  # noqa: E402

HUB = HERE.parents[1]
KNOWN = {('0403', '6010'): 'tang', ('303a', '1001'): 'xiao'}
TANG_UART_GLOB = 'usb-SIPEED_USB_Debugger_*-if01-port0'


def core_dir():
    return Path(os.environ.get('OPENVRX_CORE', HUB.parent / 'OpenVRX-Core'))


def logs_dir():
    d = Path(os.environ.get('OPENVRX_BENCH_LOGS', HUB.parent / 'bench-logs'))
    d.mkdir(parents=True, exist_ok=True)
    return d


def snowlog():
    sys.path.insert(0, str(core_dir() / 'gateware' / 'tools'))
    import snowlog as s  # noqa: E402  Core gateware/tools/snowlog.py
    return s


# ---------------------------------------------------------------- devices

def parse_lsusb(text):
    """[(bus, device, vid, pid, name)] from `lsusb` output."""
    out = []
    for line in text.splitlines():
        m = re.match(r'Bus (\d+) Device (\d+): ID ([0-9a-f]{4}):([0-9a-f]{4}) ?(.*)', line.strip())
        if m:
            out.append((m[1], m[2], m[3], m[4], m[5]))
    return out


def tty_nodes(sys_root='/sys', dev_root='/dev'):
    """[{tty, vid, pid, serial, interface, by_id}] for every ttyUSB/ttyACM, from sysfs."""
    by_id = {}
    sid = Path(dev_root) / 'serial' / 'by-id'
    if sid.is_dir():
        for link in sid.iterdir():
            by_id[os.path.basename(os.path.realpath(link))] = str(link)
    nodes = []
    cls = Path(sys_root) / 'class' / 'tty'
    if not cls.is_dir():
        return nodes
    for tty in sorted(cls.iterdir()):
        if not re.match(r'tty(USB|ACM)\d+$', tty.name):
            continue
        p = Path(os.path.realpath(tty / 'device'))
        iface = None
        while p != p.parent and not (p / 'idVendor').exists():
            if iface is None and (p / 'bInterfaceNumber').exists():
                iface = (p / 'bInterfaceNumber').read_text().strip()
            p = p.parent
        if not (p / 'idVendor').exists():
            continue
        rd = lambda n: (p / n).read_text().strip() if (p / n).exists() else None  # noqa: E731
        nodes.append({'tty': f'{dev_root}/{tty.name}', 'vid': rd('idVendor'), 'pid': rd('idProduct'),
                      'serial': rd('serial'), 'interface': iface, 'by_id': by_id.get(tty.name)})
    return nodes


def detect_fpga(timeout=20):
    try:
        r = subprocess.run(['openFPGALoader', '-b', 'tangnano20k', '--detect'], capture_output=True, text=True,
                           timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {'ok': False, 'error': str(e)}
    text = r.stdout + r.stderr
    model = re.search(r'model\s+(\S+)', text)
    idcode = re.search(r'idcode\s+(0x[0-9a-fA-F]+)', text)
    return {'ok': r.returncode == 0 and bool(idcode), 'model': model[1] if model else None,
            'idcode': idcode[1] if idcode else None}


def devices(args):
    try:
        usb = parse_lsusb(subprocess.run(['lsusb'], capture_output=True, text=True).stdout)
    except OSError:
        usb = []
    found = []
    nodes = tty_nodes()
    for bus, dev, vid, pid, name in usb:
        kind = KNOWN.get((vid, pid))
        if kind:
            found.append({'kind': kind, 'bus': bus, 'device': dev, 'vid': vid, 'pid': pid, 'name': name,
                          'ttys': [n for n in nodes if (n['vid'], n['pid']) == (vid, pid)]})
    res = {'usb': found, 'tang_uart': tang_uart(nodes)}
    if args.detect and any(d['kind'] == 'tang' for d in found):
        res['fpga'] = detect_fpga()
    if args.json:
        print(json.dumps(res, indent=2))
        return 0
    if not found:
        print('no known board in WSL (Tang 0403:6010, XIAO 303a:1001); on Windows: tools/bench.ps1 attach')
    for d in found:
        print(f"{d['kind']:5s} {d['vid']}:{d['pid']} bus {d['bus']} dev {d['device']}  {d['name']}")
        for n in d['ttys']:
            print(f"      if{n['interface']} {n['tty']}  {n['by_id'] or ''}")
    if res['tang_uart']:
        print(f"Tang log port: {res['tang_uart']}")
    if 'fpga' in res:
        f = res['fpga']
        print(f"FPGA: {f.get('model')} {f.get('idcode')}" if f['ok'] else f"FPGA not detected: {f}")
    return 0


def tang_uart(nodes=None, dev_root='/dev'):
    """The Tang Nano 20K's UART (BL616 interface 1): by-id link first, else the sysfs match."""
    sid = Path(dev_root) / 'serial' / 'by-id'
    if sid.is_dir():
        hits = sorted(sid.glob(TANG_UART_GLOB))
        if hits:
            return str(hits[0])
    for n in nodes if nodes is not None else tty_nodes():
        if (n['vid'], n['pid']) == ('0403', '6010') and n['interface'] == '01':
            return n['tty']
    return None


# ---------------------------------------------------------------- flash

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def resolve_bitstream(target, build_dirs):
    p = Path(target)
    if p.suffix == '.fs':
        if not p.is_file():
            raise FileNotFoundError(f'no such bitstream: {p}')
        return p
    for d in build_dirs:
        cand = Path(d) / f'{target}.fs'
        if cand.is_file():
            return cand
    raise FileNotFoundError(f'{target}.fs not found in ' + ', '.join(str(d) for d in build_dirs))


def check_manifest(fs, core=None, root=None):
    """(record, level) for the bitstream `fs`; raises ValueError when it does not match its manifest.

    level 'full': every artifact matched through Core's build_manifest.py verify; 'bitstream': only the .fs
    (the other artifacts are not next to it). root (a Core checkout) also compares the manifest with its sources.
    """
    manifest = fs.with_name(fs.name[:-3] + '.build.json')
    if not manifest.is_file():
        raise ValueError(f'no manifest next to the bitstream: {manifest.name}')
    record = json.loads(manifest.read_text())
    if record.get('format_version') != 1 or not record.get('completed_utc'):
        raise ValueError('not a completed build manifest')
    if record.get('bitstream') != fs.name:
        raise ValueError(f"manifest is for {record.get('bitstream')}, not {fs.name}")
    if sha256(fs) != record.get('artifacts', {}).get(fs.name):
        raise ValueError(f'{fs.name} does not match the hash in its manifest')
    complete = all((fs.parent / n).is_file() for n in record['artifacts'])
    if complete or root:
        tool = Path(core or core_dir()) / 'gateware' / 'tools' / 'build_manifest.py'
        cmd = [sys.executable, str(tool), 'verify', str(manifest)]
        if root:
            cmd += ['--root', str(root)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise ValueError((r.stdout + r.stderr).strip())
    return record, ('full' if complete else 'bitstream') + ('+sources' if root else '')


def family(top):
    for prefix, fam in (('m3_', 'm3'), ('m6_', 'm6'), ('m2a_', 'm2a')):
        if top.startswith(prefix):
            return fam
    return None


def uart_baud(record):
    return int(record.get('options', {}).get('uart_baud') or 115200)


def flash(args):
    dirs = [d for d in (args.build_dir, os.environ.get('OPENVRX_BUILD')) if d] + [core_dir() / 'gateware' / 'build']
    try:
        fs = resolve_bitstream(args.target, dirs)
        record, level = (None, 'skipped') if args.no_verify else check_manifest(fs, root=args.root)
        if args.root:
            level += f' ({args.root})'
    except (OSError, ValueError) as e:
        print(f'refused: {e}', file=sys.stderr)
        return 1
    git = (record or {}).get('git', {})
    print(f"{fs}  top {record['top'] if record else '?'}  commit {str(git.get('commit'))[:7]}"
          f"{' (dirty tree)' if git.get('dirty') else ''}  verified: {level}")
    cmd = ['openFPGALoader', '-b', 'tangnano20k'] + (['-f'] if args.flash else []) + [str(fs)]
    if args.dry_run:
        print(' '.join(cmd))
        return 0
    r = subprocess.run(cmd, capture_output=True, text=True)
    tail = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()][-3:]
    print('\n'.join(tail))
    if r.returncode != 0:
        print(f'openFPGALoader failed ({r.returncode})', file=sys.stderr)
        return r.returncode
    state = {'flashed_utc': serialport.now_iso(), 'file': str(fs), 'sha256': sha256(fs),
             'memory': 'flash' if args.flash else 'sram', 'verified': level,
             'top': record['top'] if record else None, 'options': record.get('options') if record else None,
             'git': git, 'uart_baud': uart_baud(record) if record else 115200}
    (logs_dir() / 'state.json').write_text(json.dumps(state, indent=2) + '\n')
    return 0


def load_state():
    p = logs_dir() / 'state.json'
    return json.loads(p.read_text()) if p.is_file() else {}


# ---------------------------------------------------------------- log, status

def parser_for(fam):
    if fam == 'm3':
        return m3probe.parse
    if fam == 'm6':
        return snowlog().parse
    raise ValueError(f'no parser for {fam!r} (m3 or m6)')


def summarize(fam, recs):
    good = [r for r in recs if r]
    s = {'lines': len(recs), 'parsed': len(good), 'damaged': len(recs) - len(good)}
    if fam == 'm6' and good:
        med = lambda k: (statistics.median(v) if (v := [r[k] for r in good if r.get(k) is not None]) else None)  # noqa: E731
        s.update(snow_a=med('snow_a'), snow_b=med('snow_b'), noise_a=med('noise_a'), noise_b=med('noise_b'),
                 lost_a=sum(1 for r in good if r.get('lost_a')), lost_b=sum(1 for r in good if r.get('lost_b')),
                 sdram=sorted({r.get('sdram') for r in good if r.get('sdram') is not None}),
                 channel=sorted({r['channel'] for r in good}), mode=sorted({r['mode'] for r in good}),
                 filter=sorted({r['filter'] for r in good if r.get('filter')}))
        for k in ('lat', 'hold', 'osd', 'cmd', 'cmd_count'):           # DEVCMD=1 lines (Core task 58)
            vals = [r[k] for r in good if r.get(k) is not None]
            if vals:
                s[k] = vals[-1]
    if fam == 'm3':
        for ch in 'AB':
            rs = [r for r in good if r['ch'] == ch]
            if rs:
                last = rs[-1]
                s[ch] = {k: last.get(k) for k in ('sclk', 'sclk_ok', 'i2c', 'st', 'locked', 'color_lock', 'len_min',
                                                  'len_max', 'fld', 'xe', 'ri')}
                s[ch]['lines'] = len(rs)
    return s


def capture(port, baud, seconds, parse, out=None, stop_when=None):
    """Read `seconds` of lines; [(timestamp, raw, record or None)]; JSONL to `out` as they come."""
    rows = []
    fh = open(out, 'a') if out else None

    def on_line(t, text):
        if not text.strip():
            return
        rec = parse(text)
        rows.append((t, text, rec))
        if fh:
            fh.write(json.dumps({'t': t, 'raw': text, 'rec': rec}) + '\n')
            fh.flush()

    fd = serialport.open_port(port, baud)
    try:
        serialport.read_lines(fd, seconds, on_line, stop=(lambda: stop_when(rows)) if stop_when else None)
    finally:
        os.close(fd)
        if fh:
            fh.close()
    return rows


def pick(args, state):
    fam = args.top or family(state.get('top') or '')
    if fam is None:
        raise ValueError('which log? give m3 or m6 (state.json names no M3/M6 bitstream)')
    port = args.port or tang_uart()
    if not port:
        raise ValueError('no Tang UART in WSL: attach the board (tools/bench.ps1 attach) or give --port')
    same = state.get('top') and family(state['top']) == fam
    baud = args.baud or (state.get('uart_baud') if same else None) or 115200
    return fam, port, baud


def log_cmd(args):
    state = load_state()
    try:
        fam, port, baud = pick(args, state)
        parse = parser_for(fam)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    out = args.out or str(logs_dir() / f"{fam}-{serialport.now_iso().replace(':', '')}.jsonl")
    rows = capture(port, baud, args.seconds, parse, out)
    s = summarize(fam, [r for _, _, r in rows])
    s.update(port=port, baud=baud, out=out, flashed=state.get('file'))
    print(json.dumps(s) if args.json else '\n'.join(f'{k}: {v}' for k, v in s.items()))
    return 0 if s['parsed'] else 2


def status_cmd(args):
    state = load_state()
    try:
        fam, port, baud = pick(args, state)
        parse = parser_for(fam)
    except ValueError as e:
        print(json.dumps({'error': str(e)}) if args.json else e, file=sys.stderr)
        return 1

    def enough(rows):
        good = [r for _, _, r in rows if r]
        if fam == 'm3':
            return {r['ch'] for r in good} >= {'A', 'B'}
        return len(good) >= 2

    rows = capture(port, baud, args.seconds, parse, stop_when=enough)
    good = [(t, raw, r) for t, raw, r in rows if r]
    res = {'top': state.get('top'), 'family': fam, 'port': port, 'baud': baud, 'flashed': state.get('file'),
           'flashed_utc': state.get('flashed_utc'), 'commit': (state.get('git') or {}).get('commit'),
           'lines': len(rows), 'parsed': len(good)}
    if fam == 'm6' and good:
        t, raw, last = good[-1]
        res.update(time=t, raw=raw, last=last, selftest=last.get('sdram'),
                   selftest_ok=last.get('sdram') == 2,
                   lost={'A': last.get('lost_a'), 'B': last.get('lost_b')},
                   video={'A': last.get('snow_a') is not None, 'B': last.get('snow_b') is not None})
    if fam == 'm3':
        for ch in 'AB':
            rs = [(t, raw, r) for t, raw, r in good if r['ch'] == ch]
            if rs:
                t, raw, r = rs[-1]
                res[ch] = {'time': t, 'raw': raw, 'addr': r['addr'], 'i2c': r['i2c'], 'locked': r['locked'],
                           'color_lock': r.get('color_lock'), 'st': None if r['st'] is None else f"{r['st']:04X}",
                           'sclk': r['sclk'], 'sclk_ok': r['sclk_ok']}
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        for k, v in res.items():
            print(f'{k}: {v}')
    return 0 if good else 2


def core_tool(name, args, state):
    """Run a Core tool (gateware/tools/<name>) with the Tang UART and the rate of what was flashed."""
    port = tang_uart()
    if not port:
        print('no Tang UART in WSL: attach the board (tools/bench.ps1 attach)', file=sys.stderr)
        return 1
    if not (state.get('options') or {}).get('devcmd') in ('1', 1):
        print('note: state.json does not name a DEVCMD=1 bitstream; the board may ignore commands', file=sys.stderr)
    cmd = [sys.executable, str(core_dir() / 'gateware' / 'tools' / name), *args, '--port', port,
           '--baud', str(state.get('uart_baud') or 115200)]
    return subprocess.run(cmd).returncode


def cmd_cmd(args):
    return core_tool('m6ctl.py', args.keys, load_state())


def dump_cmd(args):
    out = args.out or str(logs_dir() / f"dump{args.which}-{serialport.now_iso().replace(':', '')}")
    return core_tool('fielddump.py', [args.which, '--out', out], load_state())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('devices', help='boards in WSL, their tty nodes, optionally the FPGA over JTAG')
    d.add_argument('--json', action='store_true')
    d.add_argument('--detect', action='store_true', help='also openFPGALoader --detect')
    f = sub.add_parser('flash', help='check a bitstream against its manifest and load it')
    f.add_argument('target', help='top name (searched in the build directories) or path to a .fs')
    f.add_argument('--build-dir')
    f.add_argument('--flash', action='store_true', help='write the SPI flash (default: SRAM only)')
    f.add_argument('--root', nargs='?', const=str(core_dir()), metavar='CORE',
                   help='also compare the manifest with the sources of this Core checkout (default OPENVRX_CORE)')
    f.add_argument('--no-verify', action='store_true')
    f.add_argument('--dry-run', action='store_true')
    for name in ('log', 'status'):
        p = sub.add_parser(name, help='timestamped, parsed log to JSONL' if name == 'log'
                           else 'last parsed line, self-test, addresses, lock flags')
        if name == 'log':
            p.add_argument('top', nargs='?', choices=['m3', 'm6'])
        else:
            p.add_argument('--top', choices=['m3', 'm6'])
        p.add_argument('--seconds', type=float, default=20 if name == 'log' else 25)
        p.add_argument('--port')
        p.add_argument('--baud', type=int)
        p.add_argument('--json', action='store_true')
        if name == 'log':
            p.add_argument('--out')
    c = sub.add_parser('cmd', help='M6 development commands (DEVCMD=1), each waits for its receipt (m6ctl.py)')
    c.add_argument('keys', nargs='+')
    d = sub.add_parser('dump', help='field dump to PNG (DEVCMD=1, fielddump.py): D decoder A, F field store input')
    d.add_argument('which', choices=['D', 'F'])
    d.add_argument('--out', help='path prefix (default bench-logs/dump<which>-<time>)')
    a = ap.parse_args(argv)
    return {'devices': devices, 'flash': flash, 'log': log_cmd, 'status': status_cmd, 'cmd': cmd_cmd,
            'dump': dump_cmd}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
