# CERN-OHL-S-2.0; exported from the accepted private motion trace reader.
# Checks existing M0 traces only; it does not launch a simulator or touch hardware.
import gzip
import json
import pathlib
import sys

def inspect(raw, variant):
    lines=raw.decode().splitlines()
    assert lines.count('MOTION_END 5000')==1
    assert lines[-1].endswith('tb_motion.v:18: $finish called at 150000000 (1ps)')
    assert lines[-2]=='MOTION_END 5000'
    rows=[tuple(map(int,x.split()[1:])) for x in lines if x.startswith('T ')]
    holds=[tuple(map(int,x.split()[1:])) for x in lines if x.startswith('H ')]
    assert len(lines)==10002 and len(rows)==len(holds)==5000 and rows==holds
    x=y=100;dx=dy=1;expected=[]
    for i in range(5000):
        x+=3 if dx else -3;y+=2 if dy else -2
        if x>=1216:x=1216;dx=0
        elif x<=0:x=0;dx=1
        if y>=656:y=656;dy=0
        elif y<=0:y=0;dy=1
        expected.append((i,x,y,dx,dy))
    bad=next((r for r in rows if not(0<=r[1]<=1216 and 0<=r[2]<=656)),None)
    if variant=='original':
        assert bad==(777,2046,344,1,1)
        assert all(row[1] in (1,2046) for row in rows[777:])
        assert rows!=expected
    else:
        assert bad is None and rows==expected
        assert all(sum(row[col]==edge for row in rows)>=5 for col,edge in ((1,0),(1,1216),(2,0),(2,656)))
    return {'frames':5000,'holds':5000,'first_out_of_bounds':bad,'model_match':rows==expected,'edge_hits':{str((col,edge)):sum(row[col]==edge for row in rows) for col,edge in ((1,0),(1,1216),(2,0),(2,656))}}

if __name__ == '__main__':
    variant, filename = sys.argv[1:]
    if variant not in ('original', 'candidate'):
        raise SystemExit('variant must be original or candidate')
    p = pathlib.Path(filename)
    raw = gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes()
    print(json.dumps(inspect(raw, variant), indent=2))
