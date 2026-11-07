"""One new passive state observation of saved gated codes, no producer mutation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

source,packet,out=map(Path,sys.argv[1:])
out.mkdir(exist_ok=False)
codes=(packet/'source-data/gated.codes.u8').read_bytes()
original=json.loads((packet/'gated-data/OBSERVATION.json').read_text())
assert hashlib.sha256(codes).hexdigest()==original['codes_sha256']
assert original['emitted_pixels']==0
spec=importlib.util.spec_from_file_location('frozen_capture',source/'gateware/model/cvbs_capture_ref.py')
cv=importlib.util.module_from_spec(spec);spec.loader.exec_module(cv)
c=cv.Capture(comb=True,avg=8,white_x8=20,boot_check=True)
FIELDS=('locked','levels_fresh','sync','blank','boot_slice','low_run','high_run',
        'in_pulse','pulse_start','pulse_width','last_start','pos','cur_edge','pend_edge',
        'pulse_was_eq','pulse_was_broad','pend_eq','pend_broad','seen_normal','countdown',
        'numbered','cur_active','active_decided','field','line_no','miss','hp','pred','have_start')
ix={name:i for i,name in enumerate(FIELDS)}


def snapshot():
    return [getattr(c,name) for name in FIELDS]


before=snapshot();initial=before.copy();events=pulses=0
with (out/'events.jsonl').open('x') as stream,(out/'pulses.jsonl').open('x') as pulse_stream:
    for n,sample in enumerate(codes):
        ws=c.win_sum
        level=(before[2]+before[3])>>1 if before[1] else before[4]
        low=ws<level*8
        c.step(int(sample))
        after=snapshot()
        reasons=[]
        if before[7]!=after[7]:reasons.append('pulse_start' if after[7] else 'pulse_end')
        if after[7] and before[9]<140<=after[9]:reasons.append('T_EQ')
        if after[7] and before[9]<600<=after[9]:reasons.append('T_BROAD')
        if before[10]!=after[10] or (not before[28] and after[28]):reasons.append('line_start')
        if not before[22] and after[22]:reasons.append('ACT_CHECK')
        if before[1:5]!=after[1:5]:reasons.append('levels')
        if before[14:18]!=after[14:18]:reasons.append('line_class')
        if before[18]!=after[18]:reasons.append('seen_normal')
        if before[19]!=after[19]:reasons.append('countdown')
        if before[20:22]!=after[20:22]:reasons.append('active_state')
        if before[23]!=after[23]:reasons.append('field_flip')
        if before[0]!=after[0]:reasons.append('lock')
        if reasons:
            stream.write(json.dumps(dict(n=n,reasons=reasons,registered_sum=ws,
                                         slice_level=level,low=low,before=before,after=after))+'\n')
            events+=1
        if before[7] and not after[7]:
            pulse_stream.write(json.dumps(dict(start=after[8],end=n,width=after[9]))+'\n')
            pulses+=1
        before=after
entry=struct.Struct('<BBHIII');output=bytearray()
for item in c.entries:
    if item[0]=='word':
        _,field,line,index,data=item;output.extend(entry.pack(0,field,line,index,data,0))
    else:
        _,field,line,hf,bad,length=item;output.extend(entry.pack(1,field,line,hf,bad,length))
(out/'entries.bin').write_bytes(output)
metadata=dict(fields=FIELDS,initial=initial,final=before,events=events,pulses=pulses,samples=len(codes),
              code_sha256=hashlib.sha256(codes).hexdigest(),output_sha256=hashlib.sha256(output).hexdigest(),
              original_output_sha256=hashlib.sha256((packet/'gated-data/entries.bin').read_bytes()).hexdigest(),
              entries=len(c.entries),lock_trace=c.lock_trace,
              original_lock_equal=c.lock_trace==original['lock_trace'],
              output_equal=bytes(output)==(packet/'gated-data/entries.bin').read_bytes(),
              model_evaluations=1,source_generated=False,producer_changed=False,native=False,hardware=False,
              runtime=dict(python=sys.version,prefix=sys.prefix))
(out/'OBSERVATION.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps({k:metadata[k] for k in ['events','pulses','entries','original_lock_equal','output_equal']}),flush=True)
assert metadata['original_lock_equal'] and metadata['output_equal'],'original_equivalence'
