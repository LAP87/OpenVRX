#!/usr/bin/env python3
"""Read-only OpenVRX review probes. All generated files stay under this script's directory.
Run with the OpenVRX shared venv; optional first argument is the workspace root.
These probes expose missing invariants; they do not modify the RTL or its tests.
"""
from pathlib import Path
import importlib.util
import sys
import json
import collections
import subprocess

ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path('/home/lenny/Projekt/DIY_Drone_Lab/projects/OpenVRX-repos')
CORE = ROOT / 'OpenVRX-Core'
WORK = Path(__file__).resolve().parent

def module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

results={}
latency=module('audit_latency', CORE/'tests/latency/analyze_latency.py')
pairs=latency.pair_delays([10.,12.],[16.],4.,6.,2.)
results['latency_edge_reuse']={'pairs':[[float(x) for x in row] for row in pairs], 'screen_edge_reused':len(set(b for a,b,d in pairs))!=len(pairs)}
print('LATENCY',results['latency_edge_reuse'],flush=True)

m=module('audit_mixer',CORE/'gateware/sim/test_mixer.py')
# Positive control is the exact existing compact test stimulus.
a,b=m.stream('a',1),m.stream('b',2)
ref=m.model(a,b)
dec,out,end=m.run_sim(a,b,WORK/'mixer_control')
assert dec==ref.trace and out==ref.out and end[0]==0
results['mixer_positive_control']={'decisions':len(dec),'words':len(out),'matches_reference':True}
print('MIXER CONTROL',results['mixer_positive_control'],flush=True)

# The existing suite uses only 2 VBI lines. Use 20 without changing RTL or the model.
m.VBI=20
a=m.stream('a',1,{0:60,1:20,2:20,3:20,4:20})
b=m.stream('b',2,{0:0,1:24,2:24,3:24,4:24})
ref=m.model(a,b)
dec,out,end=m.run_sim(a,b,WORK/'mixer_vbi20')
diffs=[i for i,(r,e) in enumerate(zip(dec,ref.trace)) if r!=e]
results['mixer_vbi20']={'rtl_decisions':len(dec),'model_decisions':len(ref.trace),'different_decisions':len(diffs),'overflow':end[0], 'first_difference':{'index':diffs[0],'rtl':dec[diffs[0]],'model':ref.trace[diffs[0]]} if diffs else None}
print('MIXER VBI20',results['mixer_vbi20'],flush=True)
assert diffs, 'The selected stimulus must expose a model/RTL mismatch'

# One clean channel and one declared unlocked, with B 5 line periods behind A.
m.LINES=24;m.VBI=20;m.FIELDS=3
m.START_B=m.START_A+5*1716*m.T_A
a,b=m.stream('a',1),m.stream('b',2)
dec,out,end=m.run_sim(a,b,WORK/'mixer_bad_b_lag5',[f'-Ptb_mixer.START_B={m.START_B}','-Ptb_mixer.EXT_B=1'])
shown=[(u,p,f,l) for u,p,f,l in dec if u]
bad_shown=sum(bool(u&2) for u,p,f,l in shown)
starts=1+sum(f!=pf or l<pl for (_,_,pf,pl),(_,_,f,l) in zip(shown,shown[1:]))
backwards=sum(f==pf and l<pl for (_,_,pf,pl),(_,_,f,l) in zip(shown,shown[1:]))
results['mixer_bad_b_lag5']={'fields_in_stimulus':m.FIELDS,'unlocked_b_lines_shown':bad_shown,'output_lines':len(shown),'field_starts_seen_by_backend_rule':starts,'backwards_line_steps_in_same_field':backwards,'overflow':end[0]}
print('MIXER UNLOCKED B LAG5',results['mixer_bad_b_lag5'],flush=True)
assert bad_shown>0 and backwards>0

# F never toggles: 240p/288p-like frame boundaries still have VBI.
a0=m.stream('a',1)
bt=m.bt656
mapped=bytearray(a0)
for i in range(len(mapped)-3):
    if mapped[i:i+3]==bytes([255,0,0]) and mapped[i+3] in bt.XY_TABLE:
        entry=bt.XY_TABLE[mapped[i+3]]
        if entry[3]!='bad':mapped[i+3]=bt.xy(1,entry[1],entry[2])
records=m.records_with_times(bytes(mapped),m.START_A,m.T_A)
line_numbers=[r.line_in_field for t,r in records]
results['constant_f']={'frames_in_stimulus':m.FIELDS,'last_line_number':line_numbers[-1], 'line_number_restarts':sum(b<a for a,b in zip(line_numbers,line_numbers[1:]))}
print('CONSTANT F MODEL',results['constant_f'],flush=True)

(WORK/'reproduction_results.json').write_text(json.dumps(results,indent=2))
