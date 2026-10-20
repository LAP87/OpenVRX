import datetime, fcntl, hashlib, json, os, pathlib, re, select, sys, termios, time
P=pathlib.Path(__file__).resolve().parent
name=sys.argv[1]
assert name in ('baseline','inject','released')
port='/dev/serial/by-id/usb-SIPEED_USB_Debugger_2025030317-if01-port0'
start={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'port':port,'real_port':os.path.realpath(port),'seconds':20,'baud':115200,'format':'8N1','serial_write_bytes':0,'helper_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
with (P/(name+'_START.json')).open('x') as f: json.dump(start,f,indent=2)
fd=os.open(port,os.O_RDONLY|os.O_NOCTTY|os.O_NONBLOCK)
try:
    fcntl.ioctl(fd,termios.TIOCEXCL)
    a=termios.tcgetattr(fd); a[0]=0; a[1]=0; a[2]=termios.CLOCAL|termios.CREAD|termios.CS8; a[3]=0; a[4]=termios.B115200; a[5]=termios.B115200; a[6][termios.VMIN]=0; a[6][termios.VTIME]=0
    termios.tcsetattr(fd,termios.TCSANOW,a)
    raw=bytearray(); end=time.monotonic()+20
    with (P/(name+'.raw')).open('xb') as f:
        while time.monotonic()<end:
            if select.select([fd],[],[],min(.25,max(0,end-time.monotonic())))[0]:
                data=os.read(fd,65536)
                f.write(data); f.flush(); raw.extend(data)
finally: os.close(fd)
lines=bytes(raw).split(b'\n')
rx=re.compile(rb'M rs=([0-9A-Fa-f]) pass=([0-9A-Fa-f]{4}) err=([0-9A-Fa-f]{8}) bits=([0-9A-Fa-f]{32}) pos=([0-9A-Fa-f]{8})\r?')
rows=[]; unmatched=[]
for i,line in enumerate(lines[:-1]):
    m=rx.fullmatch(line)
    if m: rows.append(dict(zip(('rs','pass','err','bits','pos'),(x.decode() for x in m.groups()))))
    else: unmatched.append({'index':i,'hex':line.hex()})
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'rows':rows,'unmatched_complete_lines':unmatched,'trailing_partial_hex':lines[-1].hex()}
with (P/(name+'_RESULT.json')).open('x') as f: json.dump(result,f,indent=2)
summary={}
for row in rows: summary.setdefault(row['rs'],{}).setdefault(row['err'],0); summary[row['rs']][row['err']]+=1
print(json.dumps({'name':name,'rows':len(rows),'by_sample_and_error':summary,'unmatched_complete_lines':len(unmatched)}))
