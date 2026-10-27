"""Read-only copy of a physical disk into a sparse image file inside WSL (Windows Python, run elevated).

    py -3 sd_image.py <PhysicalDrive path> <size in bytes> <wsl output path> <log file>

Reads 4 MiB at a time; on a read error it retries that chunk in 4 KiB pieces and writes zeros for the
pieces that still fail, logging their byte offsets (a bad-sector map). Nothing is ever written to the
disk: it is opened read-only. The log gets a progress line per GiB.
"""
import os
import subprocess
import sys
import time

dev, size, out, logpath = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
CH = 4 * 1024 * 1024
SMALL = 4096
log = open(logpath, 'a', buffering=1)
log.write(f'start {time.strftime("%H:%M:%S")} dev={dev} size={size} out={out}\n')
fd = os.open(dev, os.O_RDONLY | os.O_BINARY)
p = subprocess.Popen(['wsl.exe', '-d', 'Ubuntu', '--', 'dd', f'of={out}', 'bs=4M', 'conv=sparse', 'status=none'],
                     stdin=subprocess.PIPE)
pos, bad, t0 = 0, 0, time.time()
try:
    while pos < size:
        n = min(CH, size - pos)
        try:
            os.lseek(fd, pos, 0)
            buf = os.read(fd, n)
            if len(buf) != n:
                raise OSError(f'short read {len(buf)}')
        except OSError:
            parts = bytearray()
            for off in range(0, n, SMALL):
                m = min(SMALL, n - off)
                try:
                    os.lseek(fd, pos + off, 0)
                    piece = os.read(fd, m)
                    if len(piece) != m:
                        raise OSError(f'short read {len(piece)}')
                    parts += piece
                except OSError as e:
                    parts += b'\0' * m
                    bad += 1
                    log.write(f'bad {pos + off} {m} {e}\n')
            buf = bytes(parts)
        p.stdin.write(buf)
        pos += n
        if pos % (256 * CH) == 0 or pos == size:
            dt = time.time() - t0
            log.write(f'progress {pos} {size} {dt:.0f}s {pos / 1e6 / max(dt, 1):.1f}MB/s\n')
finally:
    p.stdin.close()
    rc = p.wait()
    os.close(fd)
    log.write(f'done rc={rc} bytes={pos} bad_pieces={bad} {time.strftime("%H:%M:%S")}\n')
