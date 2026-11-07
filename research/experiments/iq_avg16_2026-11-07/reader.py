"""Fixed task83 structural/pixel and source-time attribution; no DUT imports."""
import bisect
from collections import Counter
from fractions import Fraction
import struct

ENTRY=struct.Struct('<BBHIII')
TIME=struct.Struct('<II')


def score(raw,times,events,samples):
    timing=dict(TIME.iter_unpack(times))
    assert len(timing)*TIME.size==len(times),'timing_shape'
    assert list(timing)==sorted(timing) and list(timing.values())==sorted(timing.values()),'timing_order'
    starts=[round(Fraction(k*12711111,5000)) for k in range(1051)]
    pending=[];closed=valid=quality=malformed=0;sse=0;words=0
    fields=Counter();offsets=Counter();source_phase=Counter();first_phases=Counter();attribution=[]
    for entry_index,(kind,field,line,index,data,length) in enumerate(ENTRY.iter_unpack(raw)):
        if kind==0:
            assert entry_index in timing and 0<=timing[entry_index]<samples,'word_time'
            words+=1;pending.append((field,line,index,data,timing[entry_index]));continue
        assert kind==1,'entry_kind'
        shape=len(pending)==360 and all(r[:3]==(field,line,i) for i,r in enumerate(pending))
        if not shape:malformed+=1;pending=[];continue
        closed+=1
        pixels=[y for f,l,i,d,n in pending for y in [(d>>8)&255,d>>24]]
        error=sum((y-(16+31*(x//90)))**2 for x,y in enumerate(pixels));sse+=error
        good=data==0 and abs(length-1716)<=2
        if good:
            valid+=1;fields[field]+=1;quality+=int(error<256*720)
        n=pending[0][4];row=bisect.bisect_right(starts,n)-1;local=row%525+1
        active=20<=local<=263 or 283<=local<=525
        half=0 if local<=263 else 1
        expected=local-(20 if half==0 else 283)
        offsets[line-expected]+=1
        source_phase[(row//525,half,field)]+=1
        first_phases[n-starts[row]]+=1
        attribution.append(dict(sample=n,source_global_row=row+1,source_line=local,
                                output_field=field,output_line=line,source_active=active,
                                line_offset=line-expected,first_word_phase=n-starts[row],
                                structurally_valid=good,within16=good and error<256*720))
        pending=[]
    assert words==len(timing),'timing_count'
    arms=[e for e in events if e['kind']=='v_arm']
    eligible=valid>=400 and set(fields)=={0,1} and len(arms)>=1
    return dict(closed_rows=closed,valid_rows=valid,valid_rows_within16=quality,malformed_rows=malformed,
                original_full_row_sse=sse,trailing_words=len(pending),words=words,
                valid_rows_by_field=dict(fields),v_arms=len(arms),negative_eligible=eligible,
                label_offsets=dict(sorted(offsets.items())),first_word_phases=dict(sorted(first_phases.items())),
                source_phase_groups=[dict(frame=f,half=h,output_field=o,rows=count) for (f,h,o),count in sorted(source_phase.items())],
                source_attribution=attribution,quality_accepted=False,native=False,hardware=False)
