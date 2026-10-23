"""Parser for the M3 probe line (Core gateware/top/m3_probe.v, BRINGUP.md section 3).

    A sclk 27000064 tog FF hi FF len 1716-1716 ln 14565 fld 060 xe 0000 i2c 5C st 000E ri 00
    A sclk 00000000 no SCLK                                             i2c -- st ---- ri 00

parse(line) returns a dict or None. None means the line is not a probe line or was damaged on the way:
every field is checked for its fixed width and alphabet, so one lost or changed byte is caught.
"""
import re

_HEX2 = r'[0-9A-F]{2}'
_OK = re.compile(
    r'^(?P<ch>[AB]) sclk (?P<sclk>\d{8}) tog (?P<tog>' + _HEX2 + r') hi (?P<hi>' + _HEX2 + r') '
    r'len (?P<len>\d{4}-\d{4}|-{9}) ln (?P<ln>\d{5}) fld (?P<fld>\d{3}) xe (?P<xe>\d{4}) '
    r'i2c (?P<i2c>5C|5D|NA|--) st (?P<st>[0-9A-F]{4}|-{4}) ri (?P<ri>' + _HEX2 + r')$')
_DEAD = re.compile(
    r'^(?P<ch>[AB]) sclk (?P<sclk>\d{8}) no SCLK {44} '
    r'i2c (?P<i2c>5C|5D|NA|--) st (?P<st>[0-9A-F]{4}|-{4}) ri (?P<ri>' + _HEX2 + r')$')


def status_bits(st):
    """Decode 89h/88h (st = 0x8988 as one 16-bit value) the way BRINGUP.md section 3 reads them."""
    r88, r89 = st & 0xFF, st >> 8
    return {'h_lock': bool(r88 & 0x02), 'v_lock': bool(r88 & 0x04), 'color_lock': bool(r88 & 0x08),
            'lost_since_read': bool(r88 & 0x10), 'field_50hz': bool(r88 & 0x20), 'pal_switch': bool(r88 & 0x40),
            'vcr': bool(r88 & 0x01), 'peak_white': bool(r88 & 0x80), 'weak_signal': bool(r89 & 0x40)}


def parse(line):
    line = line.rstrip('\r\n')
    m = _OK.match(line)
    dead = False
    if not m:
        m = _DEAD.match(line)
        dead = True
        if not m:
            return None
    g = m.groupdict()
    rec = {'ch': g['ch'], 'sclk': int(g['sclk']), 'sclk_ok': not dead, 'i2c': g['i2c'],
           'addr': g['i2c'] if g['i2c'] in ('5C', '5D') else None,
           'st': None if g['st'] == '----' else int(g['st'], 16), 'ri': int(g['ri'], 16)}
    if not dead:
        rec.update(tog=int(g['tog'], 16), hi=int(g['hi'], 16), ln=int(g['ln']), fld=int(g['fld']), xe=int(g['xe']))
        if g['len'].startswith('-'):
            rec.update(len_min=None, len_max=None)
        else:
            lo, hi = g['len'].split('-')
            rec.update(len_min=int(lo), len_max=int(hi))
    if rec['st'] is not None:
        rec.update(status_bits(rec['st']))
        rec['locked'] = rec['h_lock'] and rec['v_lock']
    else:
        rec['locked'] = None
    return rec
