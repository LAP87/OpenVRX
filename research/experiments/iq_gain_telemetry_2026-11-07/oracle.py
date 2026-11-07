"""Integer arithmetic for recorded telemetry and fixed-map diagnostics, no DUT imports."""
import struct

TRACE=struct.Struct('<IiHHHHHHB')
ENTRY=struct.Struct('<BBHIII')
FIXED_GAIN=1246
SCOPE=dict(observed_model_only=True,causal_proof=False,quality_accepted=False,
           native=False,hardware=False,producer_changed=False)


def y_value(a,b,blank,gain):
    delta=a+b-2*blank
    magnitude=abs(delta)*gain//256
    return max(1,min(254,16+(magnitude if delta>=0 else -magnitude)))


def values(record,codes,clean):
    n,partner,field,line,x,blank,sync,gain,y=record
    assert 0<=n<len(codes)==len(clean) and (partner==-1 or 0<=partner<n),'sample_bounds'
    assert field in (0,1) and 0<=x<720 and 0<=blank<64 and 0<=sync<64,'telemetry_shape'
    d=max(0,min(127,2*(blank-sync)))
    expected_gain=0 if d<2 else min(4095,(219*256*8*2+20*d)//(40*d))
    assert gain==expected_gain,'telemetry_gain'
    previous=n if partner<0 else partner
    assert y==y_value(codes[n],codes[previous],blank,gain),'pixel_value'
    noisy_fixed=y_value(codes[n],codes[previous],22,FIXED_GAIN)
    clean_fixed=y_value(clean[n],clean[previous],22,FIXED_GAIN)
    a,b=noisy_fixed-clean_fixed,y-noisy_fixed
    assert a+b==y-clean_fixed
    return a,b,y-clean_fixed


def empty():
    return dict(count=0,sum_a=0,sum_b=0,a2=0,b2=0,ab=0,residual2=0)


def add(moment,a,b,residual):
    moment['count']+=1
    moment['sum_a']+=a;moment['sum_b']+=b
    moment['a2']+=a*a;moment['b2']+=b*b;moment['ab']+=a*b
    moment['residual2']+=residual*residual


def check(moment):
    assert moment['residual2']==moment['a2']+moment['b2']+2*moment['ab'],'cross_identity'
    assert moment['a2']>=0 and moment['b2']>=0 and moment['ab']**2<=moment['a2']*moment['b2'],'moment_bounds'


def inspect(codes,clean,trace_blob,entry_blob):
    records=list(TRACE.iter_unpack(trace_blob))
    moments={name:empty() for name in ['all_emitted','valid_closed','valid_closed_centers']}
    for r in records:
        add(moments['all_emitted'],*values(r,codes,clean))
    pending=[];offset=0;closed=valid=quality=malformed=0;sse=0
    for kind,field,line,index,data,length in ENTRY.iter_unpack(entry_blob):
        if kind==0:
            pair=records[offset:offset+2];offset+=2
            assert len(pair)==2 and pair[0][2:5]==(field,line,2*index) and pair[1][2:5]==(field,line,2*index+1),'trace_word_link'
            assert data==((pair[1][8]<<24)|(128<<16)|(pair[0][8]<<8)|128),'word_value'
            pending.extend(pair)
            continue
        assert kind==1,'entry_kind'
        shape=len(pending)==720 and all(r[2:5]==(field,line,x) for x,r in enumerate(pending))
        if not shape:
            malformed+=1;pending=[];continue
        closed+=1
        row_sse=sum((r[8]-(16+31*(r[4]//90)))**2 for r in pending)
        sse+=row_sse
        if data==0 and abs(length-1716)<=2:
            valid+=1;quality+=int(row_sse<256*720)
            for r in pending:
                triple=values(r,codes,clean)
                add(moments['valid_closed'],*triple)
                if 25<=r[4]%90<=64:add(moments['valid_closed_centers'],*triple)
        pending=[]
    assert offset==len(records),'trace_length'
    for m in moments.values():check(m)
    return dict(scope=SCOPE,moments=moments,emitted_pixels=len(records),closed_rows=closed,
                valid_rows=valid,valid_rows_within16=quality,malformed_rows=malformed,
                original_full_row_sse=sse,trailing_pixels=len(pending))
