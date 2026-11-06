"""First native diagnostic, no model imports and no producer modification."""
import bisect
from collections import Counter
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time

source, packet, out = map(Path,sys.argv[1:])
home = Path(__file__).resolve().parent
out.mkdir(exist_ok=False)
entry_struct = struct.Struct('<BBHIII')
runtime = json.loads((home/'RUNTIME.json').read_text())
tools = {t['name']:t['binary'] for t in runtime['tools']}
codes = (packet/'codes.bin').read_bytes()
model = (packet/'entries.bin').read_bytes()
observed = json.loads((packet/'observations.json').read_text())
geo = json.loads((packet/'source_geometry.json').read_text())
assert len(codes) == 2669333 and max(codes) < 64
assert hashlib.sha256(codes).hexdigest() == observed['codes_sha256']
assert hashlib.sha256(model).hexdigest() == observed['output_sha256']
lut = [f'{n:02x}\n'.encode() for n in range(64)]
hexdata = b''.join(lut[n] for n in codes)
(out/'samples.hex').write_bytes(hexdata)
metadata = dict(schema=1,hardware=False,producer_changed=False,
                codes_sha256=hashlib.sha256(codes).hexdigest(),code_samples=len(codes),
                hex_sha256=hashlib.sha256(hexdata).hexdigest(),native_calls=[])

def save():
    (out/'DIAGNOSTIC.json').write_text(json.dumps(metadata,indent=2)+'\n')

def run(name,command):
    record = dict(name=name,argv=command,cwd=str(out),
                  started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    started = time.monotonic()
    with (out/(name+'.stdout')).open('xb') as stdout, (out/(name+'.stderr')).open('xb') as stderr:
        process = subprocess.Popen(command,cwd=out,stdout=stdout,stderr=stderr)
        f = Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split()
        record['process'] = dict(pid=process.pid,pgrp=int(f[2]),startticks=int(f[19]))
        metadata['native_calls'].append(record)
        save()
        record['returncode'] = process.wait()
    record['elapsed_seconds'] = time.monotonic()-started
    save()
    assert record['returncode'] == 0, name+'_failed'

save()
run('compile',[tools['iverilog'],'-g2012','-I',str(source/'gateware/rtl'),
               '-o','sim.vvp','-s','tb_cvbs_capture',str(home/'tb_cvbs_capture_time.v'),
               str(source/'gateware/rtl/cvbs_capture.v')])
compiled = (out/'sim.vvp').read_text()
names = ['COMB','AVG','WHITE_X8','ACT_START','V_LINES','BOOT_INIT']
params = {}
lines = []
for line in compiled.splitlines():
    match = re.search(r'\.param/\S+ "('+ '|'.join(names) +r')".*[+]?C4<([01]+)>',line)
    if match:
        params.setdefault(match[1],[]).append(int(match[2],2))
        lines.append(line)
expected = dict(COMB=[1],AVG=[8],WHITE_X8=[20],ACT_START=[362],V_LINES=[16],BOOT_INIT=[12])
metadata['compiled_parameters'] = params
metadata['compiled_parameter_lines'] = lines
metadata['compiled_sha256'] = hashlib.sha256((out/'sim.vvp').read_bytes()).hexdigest()
save()
assert params == expected, 'compiled_parameters_differ'
# Relative plusargs avoid the original bench's 128-byte filename limit.
run('simulate',[tools['vvp'],'-n','sim.vvp','+hex=samples.hex','+out=entries.txt',
                '+n='+str(len(codes)),'+lock=lock.txt'])
stdout = (out/'simulate.stdout').read_text()
finished = re.search(r'RESULT samples=(\d+) entries=(\d+)',stdout)
assert finished and int(finished[1]) == len(codes), 'native_did_not_finish'
output = bytearray()
timestamps = []
with (out/'entries.txt').open() as file:
    for index, line in enumerate(file):
        count,text = line.split()
        sample,value = int(count),int(text,16)
        field,number = (value>>51)&1,(value>>41)&0x3ff
        if (value>>52)&1:
            output.extend(entry_struct.pack(1,field,number,(value>>21)&0xfffff,
                                            (value>>17)&15,(value>>1)&0xfff))
        else:
            word_index,data = (value>>32)&0x1ff,value&0xffffffff
            output.extend(entry_struct.pack(0,field,number,word_index,data,0))
            if word_index == 0:
                timestamps.append(dict(sample=sample,entry_index=index,field=field,line=number))
(out/'entries.bin').write_bytes(output)
metadata.update(native_entries=len(output)//16,model_entries=len(model)//16,
                native_sha256=hashlib.sha256(output).hexdigest(),
                model_sha256=hashlib.sha256(model).hexdigest(),model_bit_equal=output==model)
assert int(finished[2]) == metadata['native_entries']
if output != model:
    first = next((n for n,(a,b) in enumerate(zip(output,model)) if a!=b),min(len(output),len(model)))
    metadata['first_difference_byte'] = first
save()
assert metadata['model_bit_equal'], 'model_bit_mismatch'

starts = geo['starts']
groups = Counter()
violations = []
for row in timestamps:
    k = bisect.bisect_right(starts,row['sample'])-1
    assert 0 <= k < len(starts), 'native_time_outside_input'
    line = k%525+1
    active = 20 <= line <= 263 or 283 <= line <= 525
    phase = row['sample']-starts[k]
    row.update(global_source_line=k+1,source_frame=k//525,source_line=line,
               source_half=0 if line<=263 else 1,within_line=phase,source_active=active)
    assert abs(phase-params['ACT_START'][0]) <= 64, 'native_time_attribution_window'
    expected_line = line-(20 if line<=263 else 283)
    row['expected_active_index'] = expected_line
    row['label_offset'] = row['line']-expected_line
    groups[(k//525,row['source_half'],row['field'],row['label_offset'])] += 1
    if not active or row['label_offset'] != 0:
        violations.append(row)
metadata.update(word_rows=timestamps,source_row_identity_met=not violations,
                source_row_violations=len(violations),
                mapping_groups=[dict(frame=f,source_half=h,output_F=of,label_offset=d,rows=n)
                                for (f,h,of,d),n in sorted(groups.items())],
                first_violation=violations[0] if violations else None)
save()
print('native entries',metadata['native_entries'],'model bit equal',metadata['model_bit_equal'],
      'row identity violations',len(violations),flush=True)
assert metadata['source_row_identity_met'], 'source_row_identity'
