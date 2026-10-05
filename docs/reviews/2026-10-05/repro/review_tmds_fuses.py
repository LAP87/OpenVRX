"""Review: compare the IOB configuration fuses of the four TMDS output pairs between the
project's own bitstreams (gateware/build/<top>.fs, built with gateware/build.sh):
    m0_testpattern   no single-ended output in bank 5
    m4_dual_mix      RESETB (LVCMOS33 output) on pin 25, bank 5, next to the TMDS clock pair 33/34
    m6_puck_proto    the same pin plan
Method as in gateware/tools/test_lvds_bank_inputs.py: only fuses that belong to an IOBA/IOBB
attribute are compared (routing excluded).
"""
import json
import os
import sys
from pathlib import Path

CORE = Path(os.environ.get('OPENVRX_CORE', Path.home() / 'openvrx-review' / 'OpenVRX-Core'))
BUILD = CORE / 'gateware' / 'build'
TOPS = ('m0_testpattern', 'm4_dual_mix', 'm6_puck_proto')


def main():
    from apycula import chipdb
    from apycula.bslib import read_bitstream
    db = chipdb.load_chipdb(os.path.join(os.path.dirname(chipdb.__file__), 'GW2A-18C.msgpack.xz'))
    bm = {t: chipdb.tile_bitmap(db, read_bitstream(str(BUILD / f'{t}.fs'))[0]) for t in TOPS}
    cells = next(iter(json.load(open(BUILD / 'm0_testpattern.pnr.json'))['modules'].values()))['cells']
    tiles = {}
    for n, c in cells.items():
        bel = c.get('attributes', {}).get('NEXTPNR_BEL', '')
        if 'IOB' in bel and 'tmds' in n:
            x, y = bel.split('/')[0][1:].split('Y')
            tiles.setdefault((int(y), int(x)), []).append(n)
    for rc, names in sorted(tiles.items()):
        ttyp = db[rc].ttyp
        mask = {f for tbl in ('IOBA', 'IOBB') for fuses in db.longval[ttyp][tbl].values()
                for f in fuses if isinstance(f, tuple)}
        on = {t: {(r, c) for r, line in enumerate(bm[t][rc]) for c, v in enumerate(line) if v} & mask for t in TOPS}
        label = sorted(names)[0].split('_OBUF')[0].split('_TLVDS')[0]
        ref = on['m0_testpattern']
        print(f'tile {rc} ({label} pair): IOB fuses set m0={len(ref)}', end='')
        for t in TOPS[1:]:
            print(f'  {t}={len(on[t])} (only in m0: {sorted(ref - on[t])}, only in {t}: {sorted(on[t] - ref)})', end='')
        print()


if __name__ == '__main__':
    sys.exit(main())
