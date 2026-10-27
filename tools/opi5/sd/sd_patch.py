"""Write only the changed 4 MiB blocks of a modified image back to a physical disk (Windows Python, elevated).

    py -3 sd_patch.py <PhysicalDrive path> <delta.bin> <delta.json> <log file>

delta.json lists the blocks (offset, length, old_sha256, new_sha256); delta.bin holds old and new data for each
block in that order. For every block: read the disk, require that it still equals the old data (else stop
without writing anything more), write the new data, flush, read it back and require the new hash. Nothing
outside the listed blocks is touched.
"""
import hashlib
import json
import os
import sys
import time

dev, dbin, djson, logpath = sys.argv[1:5]
log = open(logpath, 'a', buffering=1)
plan = json.load(open(djson))
chunks = plan['chunks']
log.write(f'start {time.strftime("%H:%M:%S")} dev={dev} blocks={len(chunks)}\n')
fd = os.open(dev, os.O_RDWR | os.O_BINARY)
ok = 0
try:
    with open(dbin, 'rb') as f:
        for c in chunks:
            off, n = c['offset'], c['length']
            old = f.read(n)
            new = f.read(n)
            assert hashlib.sha256(old).hexdigest() == c['old_sha256'] and hashlib.sha256(new).hexdigest() == c['new_sha256'], 'delta file damaged'
            os.lseek(fd, off, 0)
            cur = os.read(fd, n)
            if cur != old:
                log.write(f'STOP: block at {off} differs from the original copy (disk changed?); nothing more written\n')
                break
            os.lseek(fd, off, 0)
            w = os.write(fd, new)
            os.fsync(fd)
            os.lseek(fd, off, 0)
            back = os.read(fd, n)
            if w != n or back != new:
                log.write(f'STOP: verify failed at {off} (wrote {w}); check the disk before using it\n')
                break
            ok += 1
            log.write(f'ok {off} {n}\n')
finally:
    os.close(fd)
    log.write(f'done {ok}/{len(chunks)} blocks {time.strftime("%H:%M:%S")}\n')
