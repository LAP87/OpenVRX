#!/usr/bin/env python3
"""Raw bytes from a serial port for a while, to a file (WSL, stdlib only): for bitstreams whose UART output has
no parser in bench.py, such as the M7 digital-input probe (Core gateware/top/m7_digin_probe.v).

    uart_raw.py /dev/ttyUSB1 8 out.txt [baud]
"""
import os
import sys
import termios
import time

BAUDS = {115200: termios.B115200, 230400: termios.B230400, 460800: termios.B460800, 921600: termios.B921600}


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    port, seconds, out = argv[1], float(argv[2]), argv[3]
    baud = BAUDS[int(argv[4])] if len(argv) > 4 else termios.B115200
    fd = os.open(port, os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = a[1] = a[3] = 0
    a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    a[4] = a[5] = baud
    a[6][termios.VMIN] = 0
    a[6][termios.VTIME] = 1
    termios.tcsetattr(fd, termios.TCSANOW, a)
    termios.tcflush(fd, termios.TCIFLUSH)
    end = time.time() + seconds
    n = 0
    with open(out, 'wb') as f:
        while time.time() < end:
            try:
                b = os.read(fd, 4096)
            except BlockingIOError:
                b = b''
            if b:
                f.write(b)
                n += len(b)
            else:
                time.sleep(0.02)
    os.close(fd)
    print(f'{n} bytes in {seconds:g} s -> {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
