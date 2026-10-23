"""Serial ports from WSL without pyserial (stdlib termios only).

Linux raises DTR and RTS when a tty is opened (cdc_acm and ftdi_sio both do it in the open call) and, with HUPCL
set, drops both in one request when the last handle closes. Nothing here touches the modem lines after the open:
there is no ioctl(TIOCMSET/TIOCMBIS/TIOCMBIC) in this file, so the lines stay as the driver left them.
"""
import os
import termios
import time
from datetime import datetime, timezone

BAUDS = {9600: termios.B9600, 57600: termios.B57600, 115200: termios.B115200, 230400: termios.B230400,
         460800: termios.B460800, 921600: termios.B921600, 1000000: termios.B1000000}


def open_port(path, baud=115200, write=False):
    """Raw 8N1 at `baud`, reads return after 0.2 s with whatever arrived."""
    if baud not in BAUDS:
        raise ValueError(f'unsupported baud rate {baud} (have {sorted(BAUDS)})')
    fd = os.open(path, (os.O_RDWR if write else os.O_RDONLY) | os.O_NOCTTY)
    attrs = termios.tcgetattr(fd)
    attrs[0] = 0                                        # iflag: no translation, no flow control
    attrs[1] = 0                                        # oflag: raw
    attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL | (attrs[2] & termios.HUPCL)
    attrs[3] = 0                                        # lflag: no echo, not canonical
    attrs[4] = attrs[5] = BAUDS[baud]
    attrs[6][termios.VMIN] = 0
    attrs[6][termios.VTIME] = 2
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    return fd


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


def read_lines(fd, seconds, on_line, stop=None):
    """Call on_line(timestamp, text) for every complete line within `seconds`; stop early when stop() is true.

    The timestamp is the host's arrival time. Over usbipd the board's lines arrive in bursts, sometimes half a
    minute late: it orders lines, it does not time the board.
    """
    end = time.monotonic() + seconds
    buf = b''
    while time.monotonic() < end:
        chunk = os.read(fd, 4096)
        if not chunk:
            if stop is not None and stop():
                break
            continue
        buf += chunk
        while b'\n' in buf:
            raw, buf = buf.split(b'\n', 1)
            on_line(now_iso(), raw.decode('ascii', 'replace').rstrip('\r'))
        if stop is not None and stop():
            break
    return buf
