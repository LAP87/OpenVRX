#!/usr/bin/env python3
"""Picture quality from HDMI captures (PNG, 1280 x 720), as numbers that compare between builds and days.

    quality.py measure capture_dir/ --out report.json --sheet sheet.png
    quality.py measure a.png b.png --color-window 520,300,240,120
    quality.py calibrate m0.png                   # M0's colour bars through the grabber, within a tolerance

Per picture, inside the 4:3 window where M4/M6 put the video (x 160-1119, all 720 rows; --window):
  y_mean, y_std   luma (BT.601, studio range 16-235, from the full-range RGB that the DVI output sends)
  snow            mean over source lines of sum |Y[n] - Y[n-1]| over 720 luma samples: the mixer's per-line HF
                  energy (Core gateware/model/bt656.py hf_energy, line_mixer_ref.py decides on it), so the figure
                  has the same definition as the log's snow value. The 960-pixel window is read back at 720 samples
                  (nearest pixel) and runs of equal rows count as one source line (720 rows from 240 or 288)
  black           y_mean < 20 and y_std < 3
  repeated_lines  source lines shown twice in a row (a run of equal rows at least twice the usual run length:
                  the field store's fallback line in BUF); 0 with VINTERP=1, whose rows are blends
  cb, cr, hue, sat  mean chroma in the colour window (--color-window, default the whole 4:3 window); hue in
                  degrees from atan2(Cr - 128, Cb - 128)
Over the series: share of black pictures, snow mean and spread, hue spread (circular, degrees) and Cb/Cr spread
over the non-black pictures, repeated lines in all. JSON to --out, a contact sheet PNG (quarter-size thumbnails,
four per row, in file order) to --sheet. PNGs are read with zlib, as Core gateware/model/oled_ref.py writes them
(8-bit grey, RGB or RGBA, not interlaced). Pure Python: about a second per picture.
"""
import argparse
import json
import math
import statistics
import struct
import sys
import zlib
from pathlib import Path

WINDOW = (160, 0, 960, 720)                         # x, y, w, h: the 4:3 picture in 720p (fb_display.v, M0)


# ---------------------------------------------------------------- PNG

def read_png(path):
    """(width, height, rows): rows are bytes of R G B per pixel."""
    data = Path(path).read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'{path}: not a PNG')
    pos, idat, hdr = 8, b'', None
    while pos < len(data):
        n, tag = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if struct.unpack('>I', data[pos + 8 + n:pos + 12 + n])[0] != zlib.crc32(tag + body) & 0xFFFFFFFF:
            raise ValueError(f'{path}: chunk {tag!r} fails its CRC')
        if tag == b'IHDR':
            hdr = struct.unpack('>IIBBBBB', body)
        elif tag == b'IDAT':
            idat += body
        elif tag == b'IEND':
            break
        pos += 12 + n
    w, h, depth, ctype, _, _, interlace = hdr
    if depth != 8 or interlace or ctype not in (0, 2, 6):
        raise ValueError(f'{path}: only 8-bit grey/RGB/RGBA, not interlaced (depth {depth}, type {ctype})')
    bpp = {0: 1, 2: 3, 6: 4}[ctype]
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b, c = prev[i], prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 0xFF
        elif f != 0:
            raise ValueError(f'{path}: unknown filter {f} in row {y}')
        prev = line
        if bpp == 1:
            rows.append(bytes(v for v in line for _ in range(3)))
        elif bpp == 4:
            rows.append(bytes(v for i, v in enumerate(line) if i % 4 != 3))
        else:
            rows.append(bytes(line))
    return w, h, rows


def write_png(path, w, h, rows):
    raw = b''.join(b'\x00' + bytes(r) for r in rows)

    def chunk(tag, body):
        return struct.pack('>I', len(body)) + tag + body + struct.pack('>I', zlib.crc32(tag + body) & 0xFFFFFFFF)
    Path(path).write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                           + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


# ---------------------------------------------------------------- measures

def ycc(r, g, b):
    """BT.601 studio-range Y, Cb, Cr from full-range RGB (integer, the inverse of Core rtl/ycbcr2rgb.v's job)."""
    return (((66 * r + 129 * g + 25 * b + 128) >> 8) + 16, ((-38 * r - 74 * g + 112 * b + 128) >> 8) + 128,
            ((112 * r - 94 * g - 18 * b + 128) >> 8) + 128)


def hf_energy(luma):
    """sum |Y[n] - Y[n-1]|: the mixer's line HF energy (Core gateware/model/bt656.py, Receiver._record)."""
    return sum(abs(a - b) for a, b in zip(luma[1:], luma[:-1]))


def source_luma(row, x0, w, n=720):
    """n luma samples of one picture row, read back from the w-pixel window starting at x0 (nearest pixel)."""
    out = []
    for i in range(n):
        x = x0 + (i * w + w // 2) // n
        r, g, b = row[3 * x:3 * x + 3]
        out.append(((66 * r + 129 * g + 25 * b + 128) >> 8) + 16)
    return out


def runs(rows, x0, w, tol=0.5):
    """Runs of equal rows (mean absolute difference below tol per byte) as (first row index, length)."""
    out, start = [], 0
    for i in range(1, len(rows) + 1):
        if i == len(rows):
            out.append((start, i - start))
            break
        a, b = rows[i - 1][3 * x0:3 * (x0 + w)], rows[i][3 * x0:3 * (x0 + w)]
        if sum(abs(p - q) for p, q in zip(a, b)) > tol * len(a):
            out.append((start, i - start))
            start = i
    return out


def frame_metrics(w, h, rows, window=WINDOW, color_window=None):
    x0, y0, ww, wh = window
    sel = rows[y0:y0 + wh]
    ys, cbs, crs = [], [], []
    cx, cy, cw, ch = color_window or window
    for y, row in enumerate(sel):
        for x in range(x0, x0 + ww, 2):                  # every other pixel: enough for means and spreads
            r, g, b = row[3 * x:3 * x + 3]
            yy = ((66 * r + 129 * g + 25 * b + 128) >> 8) + 16
            ys.append(yy)
        if cy <= y0 + y < cy + ch:
            for x in range(cx, cx + cw, 2):
                _, cb, cr = ycc(*row[3 * x:3 * x + 3])
                cbs.append(cb)
                crs.append(cr)
    rr = runs(sel, x0, ww)
    lengths = [n for _, n in rr]
    usual = statistics.mode(lengths) if lengths else 1
    repeated = sum(n // usual - 1 for n in lengths if usual and n >= 2 * usual)
    snow = statistics.fmean(hf_energy(source_luma(sel[i], x0, ww)) for i, _ in rr) if rr else 0.0
    y_mean, y_std = statistics.fmean(ys), statistics.pstdev(ys)
    cb, cr = statistics.fmean(cbs), statistics.fmean(crs)
    return {'y_mean': round(y_mean, 2), 'y_std': round(y_std, 2), 'snow': round(snow, 1),
            'black': y_mean < 20 and y_std < 3, 'source_lines': len(rr), 'usual_run': usual,
            'repeated_lines': repeated, 'cb': round(cb, 2), 'cr': round(cr, 2),
            'hue': round(math.degrees(math.atan2(cr - 128, cb - 128)) % 360, 2),
            'sat': round(math.hypot(cb - 128, cr - 128), 2)}


def circ_std(degs):
    """Circular standard deviation in degrees."""
    if len(degs) < 2:
        return 0.0
    s = sum(math.sin(math.radians(d)) for d in degs) / len(degs)
    c = sum(math.cos(math.radians(d)) for d in degs) / len(degs)
    r = min(1.0, math.hypot(s, c))
    return math.degrees(math.sqrt(max(0.0, -2 * math.log(r)))) if r > 0 else 180.0


def series(frames):
    lit = [f for f in frames if not f['black']]
    sd = lambda k: round(statistics.pstdev([f[k] for f in lit]), 2) if len(lit) > 1 else 0.0  # noqa: E731
    return {'pictures': len(frames), 'black_share': round(sum(f['black'] for f in frames) / len(frames), 3),
            'snow_mean': round(statistics.fmean(f['snow'] for f in lit), 1) if lit else None,
            'snow_std': sd('snow'), 'hue_std': round(circ_std([f['hue'] for f in lit]), 2),
            'cb_std': sd('cb'), 'cr_std': sd('cr'), 'repeated_lines': sum(f['repeated_lines'] for f in frames)}


def contact_sheet(path, pictures, cols=4, scale=4):
    tw, th = 1280 // scale, 720 // scale
    n = len(pictures)
    nrows = (n + cols - 1) // cols
    W, H = cols * tw, nrows * th
    canvas = [bytearray(3 * W) for _ in range(H)]
    for k, (w, h, rows) in enumerate(pictures):
        ox, oy = (k % cols) * tw, (k // cols) * th
        for ty in range(min(th, h // scale)):
            src = rows[ty * scale]
            dst = canvas[oy + ty]
            for tx in range(min(tw, w // scale)):
                x = tx * scale
                dst[3 * (ox + tx):3 * (ox + tx) + 3] = src[3 * x:3 * x + 3]
    write_png(path, W, H, canvas)


def m0_bar(i):
    """M0's bar i (Core top/m0_testpattern.v): R = bit 1, G = bit 2, B = bit 0, each 0 or C0h."""
    return (0xC0 if i & 2 else 0, 0xC0 if i & 4 else 0, 0xC0 if i & 1 else 0)


def calibrate(w, h, rows, tol=12):
    """Each of M0's eight bars sampled at its centre over many rows (median: the bouncing square is avoided)."""
    out = []
    for i in range(8):
        xs = range(160 + i * 120 + 40, 160 + i * 120 + 80, 4)
        samples = [rows[y][3 * x:3 * x + 3] for y in range(40, 680, 20) for x in xs]
        med = tuple(int(statistics.median(s[c] for s in samples)) for c in range(3))
        want = m0_bar(i)
        err = max(abs(a - b) for a, b in zip(med, want))
        out.append({'bar': i, 'want': want, 'got': med, 'err': err, 'ok': err <= tol})
    return {'ok': all(b['ok'] for b in out), 'tol': tol, 'bars': out}


def pngs(args):
    files = []
    for a in args:
        p = Path(a)
        files += sorted(p.glob('*.png')) if p.is_dir() else [p]
    return files


def rect(s):
    v = [int(x) for x in s.split(',')]
    if len(v) != 4:
        raise argparse.ArgumentTypeError('x,y,w,h')
    return tuple(v)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    m = sub.add_parser('measure')
    m.add_argument('inputs', nargs='+', help='PNG files or directories of them')
    m.add_argument('--window', type=rect, default=WINDOW)
    m.add_argument('--color-window', type=rect)
    m.add_argument('--out')
    m.add_argument('--sheet')
    c = sub.add_parser('calibrate')
    c.add_argument('png')
    c.add_argument('--tol', type=int, default=12)
    a = ap.parse_args(argv)
    if a.cmd == 'calibrate':
        r = calibrate(*read_png(a.png), tol=a.tol)
        print(json.dumps(r, indent=2))
        return 0 if r['ok'] else 1
    files = pngs(a.inputs)
    if not files:
        ap.error('no PNG files')
    pics, frames = [], []
    for f in files:
        pic = read_png(f)
        pics.append(pic)
        frames.append(dict(file=str(f), **frame_metrics(*pic, window=a.window, color_window=a.color_window)))
    rep = {'window': a.window, 'color_window': a.color_window or a.window, 'series': series(frames), 'frames': frames}
    if a.sheet:
        contact_sheet(a.sheet, pics)
        rep['sheet'] = a.sheet
    text = json.dumps(rep, indent=2)
    if a.out:
        Path(a.out).write_text(text + '\n')
    print(json.dumps(rep['series']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
