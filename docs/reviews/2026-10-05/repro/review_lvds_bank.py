"""Review experiment: does a single-ended OUTPUT in bank 5 (RESETB on pin 25 in M4/M6)
change how Apicula packs the true-LVDS TMDS clock pair on pins 33/34?

Same method as gateware/tools/test_lvds_bank_inputs.py (IOB configuration fuses of a
tile, routing excluded), but that test only has inputs in bank 5. Here:
    base : LVDS output on 33/34 + LVCMOS33 inputs on 27..30          (like M0-M2)
    out25: the same + an LVCMOS33 output on pin 25                   (like M4/M6)
    ctrl : the same + an LVCMOS33 output on pin 72 (bank 1, control)
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

CORE = Path(os.environ.get('OPENVRX_CORE', Path.home() / 'openvrx-review' / 'OpenVRX-Core'))   # a checkout of OpenVRX-Core with .venv
BIN = CORE / '.venv' / 'bin'

SRC = '''
module base (input wire clk, input wire [3:0] din, output wire [1:0] led, output wire tmds_clk_p, tmds_clk_n);
    reg [23:0] c; always @(posedge clk) c <= c + 1'b1;
    reg [3:0] q; always @(posedge clk) q <= din;
    assign led = {^q, c[23]};
    TLVDS_OBUF ob (.I(c[3]), .O(tmds_clk_p), .OB(tmds_clk_n));
endmodule
module without (input wire clk, input wire [3:0] din, output wire [1:0] led, output wire tmds_clk_p, tmds_clk_n,
                output wire extra);
    reg [23:0] c; always @(posedge clk) c <= c + 1'b1;
    reg [3:0] q; always @(posedge clk) q <= din;
    assign led = {^q, c[23]};
    assign extra = c[20];
    TLVDS_OBUF ob (.I(c[3]), .O(tmds_clk_p), .OB(tmds_clk_n));
endmodule
'''
COMMON = ('IO_LOC "clk" 4;\nIO_LOC "led[0]" 15;\nIO_LOC "led[1]" 16;\n'
          + ''.join(f'IO_LOC "din[{i}]" {27 + i};\nIO_PORT "din[{i}]" IO_TYPE=LVCMOS33 PULL_MODE=NONE;\n' for i in range(4))
          + 'IO_LOC "tmds_clk_p" 33;\nIO_PORT "tmds_clk_p" IO_TYPE=LVDS25 PULL_MODE=NONE;\n'
            'IO_LOC "tmds_clk_n" 34;\nIO_PORT "tmds_clk_n" IO_TYPE=LVDS25 PULL_MODE=NONE;\n')


def build(tmp, top, name, cst_text):
    env = dict(os.environ, TMPDIR=str(tmp))
    (tmp / f'{name}.cst').write_text(cst_text)
    def run(*a):
        r = subprocess.run(a, cwd=tmp, env=env, capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(f'{Path(a[0]).name} failed for {name}: ' + (r.stderr or r.stdout)[-700:])
    run(str(BIN / 'yowasp-yosys'), '-q', '-p', f'read_verilog probe.v; synth_gowin -top {top} -family gw2a -json {name}.json')
    run(str(BIN / 'yowasp-nextpnr-himbaechel-gowin'), '--json', f'{name}.json', '--write', f'{name}.pnr.json',
        '--device', 'GW2AR-LV18QN88C8/I7', '--vopt', 'family=GW2A-18C', '--vopt', f'cst={name}.cst', '--quiet')
    run(str(BIN / 'gowin_pack'), '-c', '-d', 'GW2A-18C', '-o', f'{name}.fs', f'{name}.pnr.json')
    return tmp / f'{name}.fs', tmp / f'{name}.pnr.json'


def main():
    from apycula import chipdb
    from apycula.bslib import read_bitstream
    tmp = Path(tempfile.mkdtemp(prefix='review_lvds_', dir=str(CORE / 'gateware' / 'sim' / 'build')))
    (tmp / 'probe.v').write_text(SRC)
    fs = {}
    fs['base'] = build(tmp, 'base', 'base', COMMON)
    fs['out25'] = build(tmp, 'without', 'out25', COMMON + 'IO_LOC "extra" 25;\nIO_PORT "extra" IO_TYPE=LVCMOS33 PULL_MODE=NONE;\n')
    try:        # control: the same extra output in another bank (pin 72, bank 1)
        fs['ctrl'] = build(tmp, 'without', 'ctrl', COMMON + 'IO_LOC "extra" 72;\nIO_PORT "extra" IO_TYPE=LVCMOS33 PULL_MODE=NONE;\n')
    except RuntimeError as e:
        print('control build failed:', e)
        fs['ctrl'] = fs['base']
    db = chipdb.load_chipdb(os.path.join(os.path.dirname(chipdb.__file__), 'GW2A-18C.msgpack.xz'))
    bm = {k: chipdb.tile_bitmap(db, read_bitstream(str(v[0]))[0]) for k, v in fs.items()}

    # where did the pads land? (taken from the `out25` design)
    def bels(pnr):
        cells = next(iter(json.load(open(pnr))['modules'].values()))['cells']
        out = {}
        for n, c in cells.items():
            bel = c.get('attributes', {}).get('NEXTPNR_BEL', '')
            if 'IOB' in bel:
                out[n] = (c['type'], bel)
        return out
    b25 = bels(fs['out25'][1])
    for n, (t, bel) in sorted(b25.items()):
        print(f'   cell {n:28s} {t:12s} {bel}')

    def tile_of(bel):
        x, y = bel.split('/')[0][1:].split('Y')
        return (int(y), int(x))

    tiles = {}
    for n, (t, bel) in b25.items():
        if 'tmds' in n or t.startswith('TLVDS'):
            tiles['TMDS clock pair (33/34)'] = tile_of(bel)
        elif 'din' in n:
            tiles.setdefault(f'input tile {tile_of(bel)}', tile_of(bel))

    def iob_fuses(which, rc):
        ttyp = db[rc].ttyp
        mask = {f for tbl in ('IOBA', 'IOBB') for fuses in db.longval[ttyp][tbl].values()
                for f in fuses if isinstance(f, tuple)}
        return {(r, c) for r, line in enumerate(bm[which][rc]) for c, v in enumerate(line) if v} & mask

    verdict = {}
    for label, rc in sorted(tiles.items()):
        base, o25, octl = (iob_fuses(k, rc) for k in ('base', 'out25', 'ctrl'))
        print(f'{label} tile {rc}: fuses set base={len(base)} out25={len(o25)} ctrl={len(octl)}')
        print(f'   out25 vs base: only out25 {sorted(o25 - base)}  only base {sorted(base - o25)}')
        print(f'   ctrl  vs base: only ctrl  {sorted(octl - base)}  only base {sorted(base - octl)}')
        verdict[label] = (o25 != base, octl != base)
    # decode which attributes those fuses belong to, for the TMDS pair
    rc = tiles['TMDS clock pair (33/34)']
    ttyp = db[rc].ttyp
    base, o25 = iob_fuses('base', rc), iob_fuses('out25', rc)
    changed = (o25 ^ base)
    if changed:
        from apycula import attrids
        inv = {}
        for tblname in ('IOBA', 'IOBB'):
            for key, fuses in db.longval[ttyp][tblname].items():
                hit = [f for f in fuses if isinstance(f, tuple) and f in changed]
                if hit:
                    names = []
                    for k in key:
                        if isinstance(k, int) and k:
                            nm = [a for a, v in attrids.iob_attrids.items() if v == abs(k)] or \
                                 [a for a, v in attrids.iob_attrvals.items() if v == abs(k)]
                            names.append((k, nm[:3]))
                    inv.setdefault(tblname, []).append((key, hit))
        for tblname, rows in inv.items():
            print(f'   {tblname}: {len(rows)} attribute rows touch the changed fuses, e.g. {rows[:6]}')
    print()
    for label, (d25, d17) in sorted(verdict.items()):
        print(f'VERDICT {label}: output on pin 25 changes its IOB fuses: {d25}; output on pin 72 (other bank): {d17}')


if __name__ == '__main__':
    sys.exit(main())
