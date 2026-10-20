import array, fcntl, hashlib, json, os, pathlib, re, select, struct, termios, time
P=pathlib.Path(__file__).resolve().parent
# Read-only data capture on the SAME running FPGA image; no programming or DUT restart.
# Follow-up hypothesis: effective board clock/UART bit time differs from nominal.
# Bound to at most six host receive settings, six seconds each; no DUT writes.
# A valid line establishes readable transport only, not the cause of rate mismatch.
port='/dev/serial/by-id/usb-SIPEED_USB_Debugger_2025030317-if01-port0'
fd=os.open(port,os.O_RDONLY|os.O_NOCTTY|os.O_NONBLOCK)
results=[]
try:
    fcntl.ioctl(fd,termios.TIOCEXCL)
    for baud in (102400,100000,108000,120000,128000,96000):
        a=termios.tcgetattr(fd); a[0]=0; a[1]=0; a[2]=termios.CLOCAL|termios.CREAD|termios.CS8; a[3]=0; a[4]=termios.B115200; a[5]=termios.B115200; a[6][termios.VMIN]=0; a[6][termios.VTIME]=0
        termios.tcsetattr(fd,termios.TCSANOW,a)
        buf=bytearray(44); fcntl.ioctl(fd,0x802c542a,buf,True)
        fields=list(struct.unpack('=IIIIB19BII',buf)); fields[2]=(fields[2]&~0x100f)|0x1000; fields[-2]=baud; fields[-1]=baud
        fcntl.ioctl(fd,0x402c542b,struct.pack('=IIIIB19BII',*fields))
        actual=bytearray(44); fcntl.ioctl(fd,0x802c542a,actual,True)
        termios.tcflush(fd,termios.TCIFLUSH)
        raw=bytearray(); end=time.monotonic()+6
        with (P/('baud_'+str(baud)+'.raw')).open('xb') as f:
            while time.monotonic()<end:
                if select.select([fd],[],[],.1)[0]:
                    data=os.read(fd,65536); f.write(data); raw.extend(data)
        rows=[x.decode() for x in re.findall(rb'M rs=[0-9A-F] pass=[0-9A-F]{4} err=[0-9A-F]{8} bits=[0-9A-F]{32} pos=[0-9A-F]{8}\r\n',raw)]
        r={'requested_baud':baud,'termios2_hex':actual.hex(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'valid_rows':rows}
        results.append(r); print(json.dumps({'baud':baud,'bytes':len(raw),'valid_rows':rows[:4]}),flush=True)
        if rows: break
finally: os.close(fd)
with (P/'CLOCK_BAUD_DIAGNOSTIC.json').open('x') as f: json.dump({'hypothesis_source':'https://wiki.sipeed.com/hardware/en/tang/tang-nano-20k/nano-20k.html','same_running_bitstream':True,'reprogrammed':False,'serial_transmit_bytes':0,'results':results},f,indent=2)
