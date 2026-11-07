"""Prepare owned no-V input before the separate first negative model phase."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

positive,out=map(Path,sys.argv[1:])
original=json.loads(positive.read_text())
codes=Path(original['codes']).read_bytes()
assert hashlib.sha256(codes).hexdigest()==original['sha256']
out.mkdir(exist_ok=False)
damaged=bytearray(codes);intervals=[]
for k in range(1050):
    line=k%525+1
    if 1<=line<=19 or 264<=line<=282:
        a,b=round(Fraction(k*12711111,5000)),round(Fraction((k+1)*12711111,5000))
        damaged[a:b]=bytes([13])*188+bytes([22])*(b-a-188)
        intervals.append(dict(global_source_row=k+1,start=a,end=b))
assert len(intervals)==76
path=out/'codes.u8';path.write_bytes(damaged)
manifest=dict(original,kind='negative',node='seed2/cn12/7bit/gated/avg16/no_vertical/first',
              codes=str(path.resolve()),sha256=hashlib.sha256(damaged).hexdigest())
(out/'INPUT.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'MUTATION.json').write_text(json.dumps(dict(parent_sha256=original['sha256'],
    sha256=manifest['sha256'],intervals=intervals,changed_bytes=sum(a!=b for a,b in zip(codes,damaged)),
    sync_width=188,sync_code=13,blank_code=22,active_source_bytes_unchanged=True),indent=2)+'\n')
print('prepared no-V input, 76 vertical intervals only; model not executed',flush=True)
