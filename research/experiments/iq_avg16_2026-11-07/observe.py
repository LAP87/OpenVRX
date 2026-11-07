"""One first source-defined AVG16 experiment; defaults and producer remain unchanged."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from reader import ENTRY,TIME,score

source,manifest_path,out=map(Path,sys.argv[1:])
manifest=json.loads(manifest_path.read_text())
assert manifest['parameters']==dict(avg=16,comb=True,white_x8=20,boot_check=True),'parameters'
codes=Path(manifest['codes']).read_bytes()
assert len(codes)==manifest['size'] and hashlib.sha256(codes).hexdigest()==manifest['sha256'],'codes_identity'
out.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('frozen_capture',source/'gateware/model/cvbs_capture_ref.py')
cv=importlib.util.module_from_spec(spec);spec.loader.exec_module(cv)
c=cv.Capture(comb=True,avg=16,white_x8=20,boot_check=True)
assert c.avg==len(c.window)==16 and c.comb and c.boot_check
actual=dict(avg=c.avg,window_length=len(c.window),comb=c.comb,boot_check=c.boot_check,white_x8=20)
events=[];emitted=0
with (out/'entries.bin').open('xb') as raw,(out/'word_times.bin').open('xb') as timing:
    for n,code in enumerate(codes):
        field,active=c.field,c.cur_active
        c.step(int(code))
        if c.field!=field:
            events.append(dict(kind='v_arm',sample=n,field=c.field,countdown=c.countdown,
                               pulse_start=c.pulse_start,cur_edge=c.cur_edge))
        if c.cur_active!=active:
            events.append(dict(kind='active',sample=n,value=c.cur_active,line=c.cur_line,field=c.cur_field))
        for entry_index in range(emitted,len(c.entries)):
            item=c.entries[entry_index]
            if item[0]=='word':
                _,f,l,i,d=item;raw.write(ENTRY.pack(0,f,l,i,d,0));timing.write(TIME.pack(entry_index,n))
            else:
                _,f,l,hf,bad,length=item;raw.write(ENTRY.pack(1,f,l,hf,bad,length))
        emitted=len(c.entries)
(out/'events.json').write_text(json.dumps(events,indent=2)+'\n')
result=score((out/'entries.bin').read_bytes(),(out/'word_times.bin').read_bytes(),events,len(codes))
result.update(node=manifest['node'],kind=manifest['kind'],parameters=actual,
              codes_sha256=hashlib.sha256(codes).hexdigest(),lock_trace=c.lock_trace,
              final_countdown=c.countdown,runtime=dict(python=sys.version,prefix=sys.prefix),
              source_generated=False,producer_changed=False)
(out/'OBSERVATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['node','closed_rows','valid_rows','valid_rows_within16','v_arms','negative_eligible']}),flush=True)
if manifest['kind']=='negative':
    assert result['words']==0 and result['v_arms']==0,'masked_vertical_not_caught'
