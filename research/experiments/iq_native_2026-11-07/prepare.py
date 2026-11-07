"""Prepare owned native inputs and current tool-version receipts; no HDL simulation."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import datetime

source,home=map(Path,sys.argv[1:])
assert not (home/'RUNTIME.json').exists() and not (home/'inputs').exists()
selection=json.loads((home/'TASK_SELECTION.json').read_text())
for b in selection['dependencies']:
    f=Path(b['path']);assert f.stat().st_size==b['size'] and hashlib.sha256(f.read_bytes()).hexdigest()==b['sha256']
old=json.loads((home.parent/'native77/RUNTIME.json').read_text())
result=dict(python=sys.version,executable=sys.executable,prefix=sys.prefix,tools=[],
            observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),compile_or_simulation=False)
for item in old['tools']:
    binary=Path(item['binary']);assert hashlib.sha256(binary.read_bytes()).hexdigest()==item['sha256']
    argv=[str(binary),'-V'];r=subprocess.run(argv,capture_output=True,text=True)
    (home/(item['name']+'.version.stdout')).write_text(r.stdout)
    (home/(item['name']+'.version.stderr')).write_text(r.stderr)
    result['tools'].append(dict(name=item['name'],binary=str(binary),argv=argv,rc=r.returncode,
                               size=binary.stat().st_size,sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                               version_line=(r.stdout+r.stderr).splitlines()[0]))
    (home/'RUNTIME.json').write_text(json.dumps(result,indent=2)+'\n')
    assert r.returncode==0 and '12.0' in result['tools'][-1]['version_line']
shutil.copyfile(home.parent/'native77/tb_cvbs_capture_time.v',home/'tb_cvbs_capture_time.v')
folder=home/'inputs';folder.mkdir()
normal=home.parent/'telemetry81/source-data/gated.codes.u8'
masked=home.parent/'avg83/negative-input/codes.u8'
hexes={}
lut=[f'{value:02x}\n'.encode() for value in range(64)]
for name,path in [('normal',normal),('no_v',masked)]:
    codes=path.read_bytes();assert len(codes)==2669333 and max(codes)<64
    text=b''.join(lut[value] for value in codes)
    f=folder/(name+'.hex');f.write_bytes(text)
    hexes[name]=(str(f),hashlib.sha256(text).hexdigest())
cases=[('gated_avg8',8,normal,home.parent/'telemetry81/gated-data/entries.bin','normal'),
       ('gated_avg16',16,normal,home.parent/'avg83/positive-data/entries.bin','normal'),
       ('no_v_avg16',16,masked,home.parent/'avg83/negative-data/entries.bin','no_v')]
for name,avg,codes,model,key in cases:
    case=dict(node='seed2/gated/rtl/'+name+'/first',id=name,avg=avg,source=str(source),
              codes=str(codes),codes_sha256=hashlib.sha256(codes.read_bytes()).hexdigest(),
              hex=hexes[key][0],hex_sha256=hexes[key][1],samples=2669333,
              model=str(model),model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
              image_accepted=False,hardware=False)
    (home/(name+'.json')).write_text(json.dumps(case,indent=2)+'\n')
(home/'PREPARATION.json').write_text(json.dumps(dict(status='PREPARED_NO_NATIVE_EXECUTED',
    cases=[c[0] for c in cases],bench_identical_to_native77=True,source_changed=False,
    cost_review='native77 same sample count30.014s; three separately started cases max120s each/360total, no expansion',
    runtime_probes=len(result['tools']),native_compile_calls=0,native_simulation_calls=0),indent=2)+'\n')
print('current tool receipts and exact owned hex inputs prepared; no compile/simulation',flush=True)
