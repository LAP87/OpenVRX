"""One first native case. Coordinator success is evidence capture, not image acceptance."""
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time

case_path,out=map(Path,sys.argv[1:])
case=json.loads(case_path.read_text())
home=Path(__file__).resolve().parent
runtime=json.loads((home/'RUNTIME.json').read_text())
tools={t['name']:t['binary'] for t in runtime['tools']}
assert case['avg'] in (8,16) and case['samples']==2669333
out.mkdir(exist_ok=False)
assert os.getpgrp()==os.getpid(),'driver_session'
os.link(case['hex'],out/'samples.hex')
record=dict(node=case['node'],avg_requested=case['avg'],calls=[],image_accepted=False,
            hardware=False,source_changed=False)


def identity(pid):
    f=Path(f'/proc/{pid}/stat')
    if not f.exists():return None
    v=f.read_text().rsplit(')',1)[1].split()
    return dict(pid=pid,pgrp=int(v[2]),startticks=int(v[19]))


def save():
    (out/'NATIVE.json').write_text(json.dumps(record,indent=2)+'\n')


def run(name,argv):
    with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:
        began=time.monotonic()
        p=subprocess.Popen(argv,cwd=out,stdout=stdout,stderr=stderr)
        owned=identity(p.pid)
        item=dict(name=name,argv=argv,process=owned)
        record['calls'].append(item)
        # Never leave a live child on a Python bookkeeping exception. Compiler
        # and VVP inherit this session, so the outer ownership-checked timeout
        # also reaches them. This helper sends no signals of its own.
        try:
            assert owned and owned['pgrp']==os.getpgrp(),'child_group'
            save()
        finally:
            rc=p.wait()
        item.update(returncode=rc,elapsed_seconds=time.monotonic()-began)
        save()
        assert rc==0,name+'_failed'


save()
source=Path(case['source'])
run('compile',[tools['iverilog'],'-g2012','-I',str(source/'gateware/rtl'),
               '-DCVBS_AVG='+str(case['avg']),'-DCVBS_COMB=1','-DCVBS_WHITE_X8=20',
               '-s','tb_cvbs_capture','-o','sim.vvp',str(home/'tb_cvbs_capture_time.v'),
               str(source/'gateware/rtl/cvbs_capture.v')])
parameters={}
for line in (out/'sim.vvp').read_text().splitlines():
    m=re.search(r'\.param/\S+ "(AVG|COMB|WHITE_X8|SW)".*[+]?C4<([01]+)>',line)
    if m:parameters.setdefault(m[1],[]).append(int(m[2],2))
record['compiled_parameters']=parameters
record['compiled_sha256']=hashlib.sha256((out/'sim.vvp').read_bytes()).hexdigest()
save()
assert parameters.get('AVG')==[case['avg']] and parameters.get('COMB')==[1] and parameters.get('WHITE_X8')==[20],'compiled_parameters'
run('simulate',[tools['vvp'],'-n','sim.vvp','+hex=samples.hex','+out=entries.txt',
                '+lock=lock.txt','+n='+str(case['samples'])])
stdout=(out/'simulate.stdout').read_text()
finish=re.search(r'RESULT samples=(\d+) entries=(\d+)',stdout)
assert finish and int(finish[1])==case['samples'],'completion'
entry=struct.Struct('<BBHIII');timing=struct.Struct('<II')
raw=bytearray();times=bytearray();entry_count=0
for index,line in enumerate((out/'entries.txt').read_text().splitlines()):
    n,text=line.split();n=int(n);word=int(text,16)
    field,number=(word>>51)&1,(word>>41)&1023
    if (word>>52)&1:
        raw.extend(entry.pack(1,field,number,(word>>21)&0xfffff,(word>>17)&15,(word>>1)&0xfff))
    else:
        raw.extend(entry.pack(0,field,number,(word>>32)&511,word&0xffffffff,0))
        times.extend(timing.pack(index,n))
    entry_count+=1
(out/'entries.bin').write_bytes(raw);(out/'word_times.bin').write_bytes(times)
model=Path(case['model']).read_bytes()
record.update(samples=case['samples'],entries=entry_count,
              output_sha256=hashlib.sha256(raw).hexdigest(),model_sha256=hashlib.sha256(model).hexdigest(),
              model_bit_equal=bytes(raw)==model,code_sha256=hashlib.sha256(Path(case['codes']).read_bytes()).hexdigest(),
              hex_sha256=hashlib.sha256((out/'samples.hex').read_bytes()).hexdigest(),
              native_calls=len(record['calls']))
save()
assert int(finish[2])==entry_count,'entry_count'
assert record['code_sha256']==case['codes_sha256'] and record['hex_sha256']==case['hex_sha256'],'input_identity'
assert record['model_bit_equal'],'model_bit_mismatch'
print(case['node'],'native/model bytes equal;',entry_count,'entries; image unaccepted',flush=True)
