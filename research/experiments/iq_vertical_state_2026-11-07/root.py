"""Read existing state/raw only; independent slicer/deglitch and vertical predicates."""
from array import array
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

home=Path(__file__).resolve().parent
out=Path(sys.argv[1]);out.mkdir(exist_ok=False)
source=Path(sys.argv[2]);parent=home.parent/'telemetry81'
meta=json.loads((home/'observe-data/OBSERVATION.json').read_text())
original=json.loads((parent/'gated-data/OBSERVATION.json').read_text())
events=[json.loads(l) for l in (home/'observe-data/events.jsonl').read_text().splitlines()]
pulses=[json.loads(l) for l in (home/'observe-data/pulses.jsonl').read_text().splitlines()]
codes=(parent/'source-data/gated.codes.u8').read_bytes()
assert hashlib.sha256(codes).hexdigest()==meta['code_sha256']==original['codes_sha256']
fields=meta['fields'];ix={v:i for i,v in enumerate(fields)}
assert len(fields)==29 and len(ix)==29


def get(state,name):return state[ix[name]]


def equivalence(m,blob):
    assert m['entries']==0 and blob==b'' and m['output_equal'] is True,'output_equivalence'
    assert m['output_sha256']==m['original_output_sha256']==hashlib.sha256(blob).hexdigest(),'output_equivalence'
    assert m['lock_trace']==original['lock_trace'] and all(type(n) is int and type(s) is bool for n,s in m['lock_trace']),'lock_equivalence'


equivalence(meta,(home/'observe-data/entries.bin').read_bytes())
assert meta['original_lock_equal'] is False  # preserve the failed in-memory tuple/list comparator
assert meta['model_evaluations']==1 and not meta['source_generated'] and not meta['producer_changed']
initial=meta['initial'];state_levels=initial[1:5]
assert state_levels==[False,4,20,12]
by_n={e['n']:e for e in events};assert len(by_n)==len(events)==meta['events']
assert [e['n'] for e in events]==sorted(by_n)
low_run=high_run=width=start=rolling=0;inside=False;computed=[]
crossings=[]
for n,sample in enumerate(codes):
    level=(state_levels[1]+state_levels[2])//2 if state_levels[0] else state_levels[3]
    low=rolling<8*level
    event=by_n.get(n)
    if event:
        assert event['registered_sum']==rolling and event['slice_level']==level and event['low'] is low,'registered_slicer'
        assert [get(event['before'],k) for k in ['low_run','high_run','in_pulse','pulse_start','pulse_width']]==[low_run,high_run,inside,start,width],'pulse_before'
        assert event['before'][1:5]==state_levels,'level_continuity'
    low_run=min(3,low_run+1) if low else 0
    high_run=0 if low else min(3,high_run+1)
    was_inside=inside;old_width=width
    if not inside and low_run==3:
        inside=True;start=n-2;width=3
        assert event and 'pulse_start' in event['reasons'],'missing_pulse_start'
    elif inside:
        if high_run==3:
            inside=False;computed.append(dict(start=start,end=n,width=width))
            assert event and 'pulse_end' in event['reasons'],'missing_pulse_end'
        else:width+=1
    if inside and old_width<600<=width:
        assert event and 'T_BROAD' in event['reasons'],'missing_broad_crossing'
        crossings.append(event)
    if inside and old_width<140<=width:
        assert event and 'T_EQ' in event['reasons'],'missing_eq_crossing'
    if event:
        assert [get(event['after'],k) for k in ['low_run','high_run','in_pulse','pulse_start','pulse_width']]==[low_run,high_run,inside,start,width],'pulse_after'
        state_levels=event['after'][1:5]
    rolling+=sample-(codes[n-8] if n>=8 else 0)
assert computed==pulses and len(pulses)==meta['pulses'],'pulse_width'
assert [get(meta['final'],k) for k in ['low_run','high_run','in_pulse','pulse_start','pulse_width']]==[low_run,high_run,inside,start,width],'pulse_final'


def vertical(sequence):
    countdown=-1;field=0;numbered=False;active=False;seen=True
    arms=checks=active_checks=0
    for e in sequence:
        before,after=e['before'],e['after']
        assert get(before,'countdown')==countdown,'countdown'
        assert get(before,'field')==field,'field_continuity'
        assert get(before,'numbered') is numbered and get(before,'cur_active') is active,'active_continuity'
        assert get(before,'seen_normal') is seen,'seen_normal'
        if 'line_start' in e['reasons']:active=False
        if get(after,'field')!=field:
            assert seen and get(after,'field')==(field^1) and get(after,'in_pulse') and get(after,'pulse_width')>=600 and get(after,'pulse_start')==get(after,'cur_edge') and get(after,'pulse_was_broad'),'v_arm'
            field^=1;countdown=16;seen=False;arms+=1
        if 'ACT_CHECK' in e['reasons']:
            assert get(after,'pos')==300 and not get(before,'active_decided') and get(after,'active_decided'),'act_check'
            if not e['low'] and not get(after,'pulse_was_eq'):seen=True
            if countdown>0:
                countdown-=1;active=countdown==0
                if active:numbered=True
            elif countdown==0 and numbered:
                active=not get(after,'pulse_was_eq') and not e['low']
            else:active=False
            checks+=1;active_checks+=int(active)
        assert get(after,'countdown')==countdown,'countdown'
        assert get(after,'numbered') is numbered and get(after,'cur_active') is active,'active_state'
        assert get(after,'seen_normal') is seen,'seen_normal'
    assert [countdown,field,numbered,active]==[get(meta['final'],k) for k in ['countdown','field','numbered','cur_active']]
    return dict(v_arms=arms,act_checks=checks,active_checks=active_checks,final_countdown=countdown)


vertical_result=vertical(events)
qualified_current={get(e['after'],'pulse_start') for e in events if get(e['after'],'in_pulse') and get(e['after'],'pulse_width')>=600 and get(e['after'],'pulse_start')==get(e['after'],'cur_edge') and get(e['after'],'pulse_was_broad')}
qualified_pending={get(e['after'],'pulse_start') for e in events if get(e['after'],'in_pulse') and get(e['after'],'pulse_width')>=600 and get(e['after'],'pulse_start')==get(e['after'],'pend_edge') and get(e['after'],'pend_broad')}
source_meta=json.loads((parent/'source-data/SOURCE.json').read_text())
wave_bytes=(parent/'source-data/source.ire.f64').read_bytes()
assert hashlib.sha256(wave_bytes).hexdigest()==source_meta['files']['source.ire.f64']['sha256']
wave=array('d');wave.frombytes(wave_bytes)
if sys.byteorder!='little':wave.byteswap()
source_broads=[];begin=None
for n,value in enumerate(wave):
    if value==-40.0:
        if begin is None:begin=n
    elif begin is not None:
        if n-begin>=600:source_broads.append((begin,n))
        begin=None
if begin is not None and len(wave)-begin>=600:source_broads.append((begin,len(wave)))
windows=[]
for a,b in source_broads:
    overlapping=[p for p in pulses if p['start']<b and p['end']>=a]
    windows.append(dict(start=a,end=b,longest_detected_width=max((p['width'] for p in overlapping),default=0),
                        fragment_count=len(overlapping)))
if vertical_result['v_arms']==0 and vertical_result['final_countdown']==-1:
    cause='broad_pulses_not_qualified_as_line_pulses' if crossings and not qualified_current and not qualified_pending else 'no_vertical_arm_condition_established'
else:cause='limited_trace_no_unique_zero_output_explanation'
summary=dict(cause=cause,case_only=True,global_or_hardware_cause=False,**vertical_result,
             completed_pulses=len(pulses),broad_crossings=len(crossings),maximum_pulse_width=max(p['width'] for p in pulses),
             qualified_current_broads=len(qualified_current),qualified_pending_broads=len(qualified_pending),
             crossing_contexts=[dict(n=e['n'],pulse_start=get(e['after'],'pulse_start'),
                                    cur_edge=get(e['after'],'cur_edge'),pend_edge=get(e['after'],'pend_edge'),
                                    width=get(e['after'],'pulse_width'),seen_normal=get(e['after'],'seen_normal')) for e in crossings],
             synthetic_source_broad_windows=windows)


def claim(value):assert value==summary,'cause'


claim(summary);controls=[];directory=out/'controls';directory.mkdir()
damaged=copy.deepcopy(pulses);damaged[0]['width']+=1
f=directory/'pulse_width.json';f.write_text(json.dumps(damaged)+'\n')
try:assert json.loads(f.read_text())==computed,'pulse_width'
except AssertionError as exc:controls.append(dict(name='pulse_width',file=f.name,reason=str(exc)))
else:raise AssertionError('fault_not_caught')
for name in ['v_arm','countdown']:
    damaged=copy.deepcopy(events)
    damaged[0]['after'][ix['field' if name=='v_arm' else 'countdown']]=1 if name=='v_arm' else 0
    f=directory/(name+'.json');f.write_text(json.dumps(damaged)+'\n')
    try:vertical(json.loads(f.read_text()))
    except AssertionError as exc:
        assert str(exc)==name;controls.append(dict(name=name,file=f.name,reason=str(exc)))
    else:raise AssertionError('fault_not_caught')
for name in ['output','lock']:
    damaged=copy.deepcopy(meta)
    if name=='output':damaged['entries']=1
    else:damaged['lock_trace'][0][0]+=1
    f=directory/(name+'.json');f.write_text(json.dumps(damaged)+'\n')
    try:equivalence(json.loads(f.read_text()),b'')
    except AssertionError as exc:
        assert str(exc)==('output_equivalence' if name=='output' else 'lock_equivalence')
        controls.append(dict(name=name,file=f.name,reason=str(exc)))
    else:raise AssertionError('fault_not_caught')
for name in ['false_cause','native','hardware']:
    damaged=copy.deepcopy(summary)
    damaged['cause']='all_receivers_fail' if name=='false_cause' else summary['cause']
    if name!='false_cause':damaged[name]=True
    f=directory/(name+'.json');f.write_text(json.dumps(damaged)+'\n')
    try:claim(json.loads(f.read_text()))
    except AssertionError as exc:
        assert str(exc)=='cause';controls.append(dict(name=name,file=f.name,reason=str(exc)))
    else:raise AssertionError('fault_not_caught')
claim(summary);vertical(events);equivalence(meta,b'')
closure=json.loads((home.parent/'provenance79/SOURCE_CLOSURE.json').read_text())
archive=subprocess.check_output(['git','-C',str(source),'archive',closure['commit']])
assert hashlib.sha256(archive).hexdigest()==closure['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
    for member in tf:
        if member.isfile():assert (source/member.name).read_bytes()==tf.extractfile(member).read()
job=json.loads((home/'observe-job/RESULT.json').read_text())
assert job['returncode']==1 and job['signals']==[] and job['inputs_unchanged']
assert not Path('/proc/'+str(job['process']['pid'])).exists()
for b in job['bindings']:
    f=Path(b['path']);assert f.stat().st_size==b['size'] and hashlib.sha256(f.read_bytes()).hexdigest()==b['sha256']
result=dict(status='ROOT_REVIEWED_EXISTING_STATE_TRACE',summary=summary,controls=controls,
            original_equivalence_canonical=True,original_failed_comparator_preserved=True,
            model_evaluations=1,model_retry=False,new_source_generated=False,
            native=False,hardware=False,producer_changed=False,source_files=len(closure['files']))
(out/'ROOT_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(summary),flush=True)
