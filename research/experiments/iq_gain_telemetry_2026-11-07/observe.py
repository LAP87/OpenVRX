"""One first path observation: passive origins, levels and gain; no producer edits."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from oracle import ENTRY,TRACE,inspect

source,packet,name,out=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3],Path(sys.argv[4])
assert name in ('adjacent','gated')
out.mkdir(exist_ok=False)
metadata=json.loads((packet/'SOURCE.json').read_text())
assert metadata['status']=='SOURCE_COMPLETE_NO_CAPTURE' and metadata['seed']==2
for f in metadata['files'].values():
    data=(packet/f['file']).read_bytes()
    assert len(data)==f['size'] and hashlib.sha256(data).hexdigest()==f['sha256']
codes=(packet/(name+'.codes.u8')).read_bytes()
clean=(packet/'source.clean.codes.u8').read_bytes()
assert len(codes)==len(clean)==metadata['samples']
spec=importlib.util.spec_from_file_location('frozen_capture',source/'gateware/model/cvbs_capture_ref.py')
cv=importlib.util.module_from_spec(spec);spec.loader.exec_module(cv)
capture=cv.Capture(comb=True,avg=8,white_x8=20,boot_check=True)
observed={}


class Origins(list):
    def __init__(self):
        super().__init__([0]*4096);self.origins=[-1]*4096
    def __setitem__(self,p,value):
        super().__setitem__(p,value);self.origins[p]=capture.n
    def __getitem__(self,p):
        value=super().__getitem__(p);observed['partner']=self.origins[p];return value


capture.prev_line,capture.cur_line_buf=Origins(),Origins()
emitted=0
with (out/'trace.bin').open('xb') as trace,(out/'entries.bin').open('xb') as raw:
    for n,sample in enumerate(codes):
        before=capture.y_count;observed.clear();capture.step(int(sample))
        if capture.y_count==before+1:
            y=capture.y_pending if capture.y_count%2 else capture.entries[-1][4]>>24
            d=max(0,min(127,2*(capture.blank-capture.sync)))
            trace.write(TRACE.pack(n,observed.get('partner',-1),capture.cur_field,capture.cur_line,
                                   capture.y_count-1,capture.blank,capture.sync,capture.gain[d],y))
        for entry in capture.entries[emitted:]:
            if entry[0]=='word':
                _,field,line,index,data=entry;raw.write(ENTRY.pack(0,field,line,index,data,0))
            else:
                _,field,line,hf,bad,length=entry;raw.write(ENTRY.pack(1,field,line,hf,bad,length))
        emitted=len(capture.entries)
result=inspect(codes,clean,(out/'trace.bin').read_bytes(),(out/'entries.bin').read_bytes())
result.update(node=metadata['paths'][name]['node'],iq_sha256=metadata['files']['iq.pairs.i16']['sha256'],
              codes_sha256=hashlib.sha256(codes).hexdigest(),lock_trace=capture.lock_trace,
              runtime=dict(python=sys.version,prefix=sys.prefix))
(out/'OBSERVATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['node','emitted_pixels','closed_rows','valid_rows','valid_rows_within16','moments']}),flush=True)
