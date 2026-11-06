"""Observe unchanged clean Capture; input and output must match task75."""
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

source, previous, output = map(Path, sys.argv[1:])
sys.path.insert(0,str(source/'gateware/model'))
import iq_demod_ref as iq
import iq_capture_ref as adapter

output.mkdir(exist_ok=False)
started = time.monotonic()
old = json.loads(previous.read_text())
bypass = next(c for c in old['cases'] if c['name']=='bypass')
video,starts,info = iq.composite_ire(iq.cv.bars,1050,first_line=1)
video = iq.lowpass(video,4.2e6)
video_hash = hashlib.sha256(video.astype('<f8').tobytes()).hexdigest()
assert video_hash == old['source_video_sha256']
codes = adapter.video_codes(video)
code_hash = hashlib.sha256(codes.tobytes()).hexdigest()
assert code_hash == bypass['codes_sha256']
(output/'codes.bin').write_bytes(codes.tobytes())
(output/'source_geometry.json').write_text(json.dumps(dict(starts=starts.tolist(),
    active=[bool(a) for s,a in info],source_lines=1050,first_line=1,samples=len(codes)),indent=2)+'\n')

capture = iq.cv.Capture(comb=True,avg=8,white_x8=20,boot_check=True)
watch = ('locked','boot_slice','field','countdown','numbered','line_no','levels_fresh','boot_rejects')
def state():
    return {name:getattr(capture,name) for name in watch}
def context():
    return dict(last_start=capture.last_start,cur_edge=capture.cur_edge,
                pulse_start=capture.pulse_start,pulse_width=capture.pulse_width,
                sync=capture.sync,blank=capture.blank,pos=capture.pos)
states = [dict(sample=-1,state=state(),context=context())]
words,markers = [],[]
last_state = state()
seen = 0
for sample, code in enumerate(codes):
    before_start = capture.last_start
    capture.step(int(code))
    now = state()
    if now != last_state:
        states.append(dict(sample=sample,state=now,context=context()))
        last_state = now
    total = len(capture.entries)
    if total != seen:
        for index in range(seen,total):
            entry = capture.entries[index]
            if entry[0]=='word' and entry[3]==0:
                words.append(dict(sample=sample,entry_index=index,field=entry[1],line=entry[2],
                                  last_start=capture.last_start,edge=capture.cur_edge,
                                  countdown=capture.countdown))
            elif entry[0]=='marker':
                markers.append(dict(sample=sample,entry_index=index,field=entry[1],line=entry[2],
                                    ending_start=before_start,next_start=capture.last_start,
                                    hf=entry[3],bad=entry[4],length=entry[5]))
        seen = total
adapter.write_entries(output/'entries.bin',capture.entries)
actual = (output/'entries.bin').read_bytes()
receipt = dict(source_video_sha256=video_hash,codes_sha256=code_hash,code_samples=len(codes),
               output_sha256=hashlib.sha256(actual).hexdigest(),output_bytes=len(actual),
               output_matches_task75=hashlib.sha256(actual).hexdigest()==bypass['raw']['sha256'],
               word_rows=words,markers=markers,states=states,
               runtime=dict(python=sys.version,prefix=sys.prefix,numpy=np.__version__),
               elapsed_seconds=time.monotonic()-started,producer_changed=False,hardware=False)
(output/'observations.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert receipt['output_matches_task75'], 'observer must not alter task75 output'
print('Exact input/output identity; word starts',len(words),'markers',len(markers),
      'state changes',len(states),'seconds',receipt['elapsed_seconds'])
