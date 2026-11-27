import datetime, fcntl, hashlib, json, os, pathlib, select, subprocess, sys, termios, time
P=pathlib.Path(__file__).resolve().parent
top=sys.argv[1]
assert top in ('m2u_uart27','m2u_uart64')
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def write(name,value):
    with (P/(top+'_'+name)).open('x') as f:json.dump(value,f,indent=2)
c=json.loads((P/'CONTRACT.json').read_text())
q=json.loads((P/(top+'_QUOTA.json')).read_text())
assert q['api']['ordinaryUsageAllowed'] is True and 0<=time.time()-q['observed_epoch']<=60
bit=P/'bitstreams'/(top+'.fs')
assert sha(bit)==c['tops'][top]['bitstream_sha256']
for name,record in c['source_bindings'].items():assert sha(P/'source'/name)==record['sha256'],name
lock=open('/home/owner/openvrx-review/build.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
fd=os.open(c['port'],os.O_RDONLY|os.O_NOCTTY|os.O_NONBLOCK)
try:
    fcntl.ioctl(fd,termios.TIOCEXCL)
    a=termios.tcgetattr(fd);a[0]=0;a[1]=0;a[2]=termios.CLOCAL|termios.CREAD|termios.CS8;a[3]=0;a[4]=termios.B115200;a[5]=termios.B115200;a[6][termios.VMIN]=0;a[6][termios.VTIME]=0
    termios.tcsetattr(fd,termios.TCSANOW,a)
    # Save, rather than silently discard, bytes queued before this image is loaded.
    previous=bytearray();end=time.monotonic()+1
    while time.monotonic()<end:
        if select.select([fd],[],[],.1)[0]:previous.extend(os.read(fd,65536))
    (P/(top+'_before.raw')).open('xb').write(previous)
    argv=['/usr/bin/openFPGALoader','-b',c['board'],'--ftdi-serial',c['debugger_serial'],'-m',str(bit)]
    start={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':argv,'bitstream_sha256':sha(bit),'contract_sha256':sha(P/'CONTRACT.json'),'helper_sha256':sha(pathlib.Path(__file__)),'quota_sha256':sha(P/(top+'_QUOTA.json')),'port':c['port'],'real_port':os.path.realpath(c['port']),'termios_after':termios.tcgetattr(fd)[:6],'capture_seconds':c['capture_seconds'],'serial_payload_bytes_written':0}
    with (P/(top+'_program.stdout')).open('xb') as out,(P/(top+'_program.stderr')).open('xb') as err:
        child=subprocess.Popen(argv,stdout=out,stderr=err,start_new_session=True)
        fields=pathlib.Path('/proc/'+str(child.pid)+'/stat').read_text().rsplit(')',1)[1].split()
        start['process']={'pid':child.pid,'pgid':int(fields[2]),'startticks':int(fields[19])};write('START.json',start)
        rc=child.wait()
    write('PROGRAM_RESULT.json',{'rc':rc,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    assert rc==0
    raw=bytearray();end=time.monotonic()+c['capture_seconds']
    with (P/(top+'.raw')).open('xb') as f:
        while time.monotonic()<end:
            if select.select([fd],[],[],min(.1,max(0,end-time.monotonic())))[0]:
                data=os.read(fd,65536);f.write(data);f.flush();raw.extend(data)
finally:
    os.close(fd);fcntl.flock(lock,fcntl.LOCK_UN)
expected=bytes.fromhex(c['expected_line_hex'])
lines=bytes(raw).split(b'\n');complete=lines[:-1]
valid=sum(line+b'\n'==expected for line in complete)
bad=[{'index':i,'hex':line.hex()} for i,line in enumerate(complete) if line+b'\n'!=expected]
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'valid_exact_lines':valid,'complete_lines':len(complete),'unmatched_complete_lines':bad,'trailing_partial_hex':lines[-1].hex(),'first_164_bytes_hex':bytes(raw[:164]).hex(),'first_164_bytes_repr':repr(bytes(raw[:164])),'sdram_test':False}
write('RESULT.json',r)
print(json.dumps({'top':top,'bytes':len(raw),'valid_exact_lines':valid,'complete_lines':len(complete),'bad_complete_lines':len(bad),'first_164_bytes_repr':r['first_164_bytes_repr']}))
