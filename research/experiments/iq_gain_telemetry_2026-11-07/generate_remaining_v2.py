"""First seed2 IQ source; save actual arrays before any Capture invocation."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

source,out=map(Path,sys.argv[1:3])
out.mkdir(exist_ok=False)
sys.path.insert(0,str(source/'gateware/model'))
import iq_demod_ref as iq

meta=dict(status='GENERATING',seed=2,cn=12,bits=7,lines=1050,first_line=1,
          fs=40e6,deviation=2.8,channel_bw=12e6,video_bw=4.2e6,
          source_commit='031bba053943ee04ce303ae75b5e701746169c97',files={},paths={},
          runtime=dict(python=sys.version,prefix=sys.prefix,numpy=np.__version__),
          capture_executed=False,native=False,hardware=False)


def save():
    (out/'SOURCE.json').write_text(json.dumps(meta,indent=2)+'\n')


def array(name,values,dtype):
    data=np.asarray(values,dtype=dtype).tobytes()
    (out/name).write_bytes(data)
    record=dict(file=name,size=len(data),sha256=hashlib.sha256(data).hexdigest(),dtype=dtype)
    meta['files'][name]=record
    save()
    return record


save()
clean,starts,info=iq.composite_ire(iq.cv.bars,1050,first_line=1)
array('source.ire.f64',clean,'<f8')
video=iq.lowpass(clean,4.2e6)
array('source.filtered.f64',video,'<f8')
array('source.clean.codes.u8',np.clip(np.rint(22+0.22*video),0,63),'<u1')
base=iq.lowpass(iq.fm_modulate(video,2.8),6e6,taps=95)
base=iq.lowpass(iq.add_noise(base,12,12e6,np.random.default_rng(2)),6e6,taps=95)
quantized=iq.quantise_iq(base,7)
pairs=np.column_stack((np.rint(quantized.real*64),np.rint(quantized.imag*64))).astype('<i2')
iq_record=array('iq.pairs.i16',pairs,'<i2')
old=json.loads(Path(sys.argv[3]).read_text())
old_sha=next(c['iq_sha256'] for c in old['cases'] if c['name']=='adjacent7')
assert iq_record['sha256']!=old_sha,'new_seed_matches_old_iq'
meta['old_seed1_iq_sha256']=old_sha
# Both discriminators consume a reconstruction of these actual saved bytes.
saved=np.fromfile(out/'iq.pairs.i16',dtype='<i2').reshape(-1,2)
z=saved[:,0].astype(float)/64+1j*saved[:,1].astype(float)/64
assert np.array_equal(z,quantized)
for name in ['adjacent','gated']:
    demod=iq.fm_demodulate(z,2.8) if name=='adjacent' else iq.fm_demodulate_pll(z,7,2.8)
    raw=array(name+'.demod.f64',demod,'<f8')
    filtered=iq.lowpass(demod,4.2e6)
    filt=array(name+'.filtered.f64',filtered,'<f8')
    codes=array(name+'.codes.u8',np.clip(np.rint(22+0.22*filtered),0,63),'<u1')
    meta['paths'][name]=dict(node='seed2/cn12/7bit/'+name,iq_sha256=iq_record['sha256'],
                             code_sha256=codes['sha256'],samples=len(filtered),
                             codes_file=codes['file'])
    save()
meta['samples']=len(video)
meta['status']='SOURCE_COMPLETE_NO_CAPTURE'
save()
print('new seed2 arrays saved; both paths used saved IQ; no Capture executed',flush=True)
