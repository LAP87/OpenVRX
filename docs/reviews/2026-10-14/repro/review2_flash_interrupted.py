"""FL-1: after a power loss in the middle of a sector erase (or a record program), the start scan
can load a record that was never written. Model: Core model/flash_store_ref.py (scan(), the
same acceptance as rtl/flash_store.v: magic A5h and CRC-8, newest seq mod 2^16); the first image
the model gets wrong is then run through the RTL (sim/test_flash_store.py's run(): the RTL with
sim/spi_flash_model.v) to show that the RTL loads it too.

Interruption model (an assumption: XTX publishes no behaviour for it, and its data sheet was not
readable): an interrupted erase leaves every 0 bit of the sector at 1 with probability p,
independently; an interrupted program leaves every bit that should go from 1 to 0 at 1 with
probability q. Erasing only sets bits and programming only clears them, so both errors are
one-directional.

Erase: the image just before the 513th save. Sector 0 holds seq 1..256, sector 1 seq 257..512;
the save erases sector 0 and power fails during that erase. The right load is seq 512.
Program: sector 1 holds seq 257..356 in slots 256..355; power fails while seq 357 goes into slot
356. A right load is seq 356, or 357 with the payload that was being written.

A wrong load is counted with numpy (the valid records of the damaged area and their seq) and
every wrong image is confirmed with ref.scan(); so is every 200th image.

Usage: OPENVRX_CORE=/path/to/OpenVRX-Core python review2_flash_interrupted.py [trials]
"""
import os
import random
import sys
from pathlib import Path

import numpy as np

CORE = Path(os.environ.get('OPENVRX_CORE', '.')).resolve()
sys.path.insert(0, str(CORE / 'gateware' / 'model'))
sys.path.insert(0, str(CORE / 'gateware' / 'sim'))
import flash_store_ref as ref  # noqa: E402

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
CRC_TABLE = np.array([ref.crc8([i]) for i in range(256)], dtype=np.uint8)


def crc_rows(recs):
    """CRC-8 over bytes 0..14 of each row (n x 16 uint8)."""
    c = np.zeros(recs.shape[0], dtype=np.uint8)
    for i in range(15):
        c = CRC_TABLE[c ^ recs[:, i]]
    return c


def newer(a, b):
    d = (a - b) & 0xFFFF
    return (d > 0) & (d < 0x8000)


def pick(valid, seqs):
    """The record scan() takes: in slot order, a valid record replaces the best one so far when its
    seq is newer (the comparison mod 2^16 is not transitive, so the order matters)."""
    best = None
    for s in np.flatnonzero(valid):
        q = int(seqs[s])
        if best is None or newer(q, best[1]):
            best = (int(s), q)
    return best


def settings(rng):
    """A random valid setting: band 0..5, channel 0..7, mode 0..2, RSSI ranges."""
    mn_a, mn_b = rng.randrange(0, 8000), rng.randrange(0, 8000)
    return ref.payload(rng.randrange(6), rng.randrange(8), rng.randrange(3), rng.randrange(2), rng.randrange(2),
                       mn_a, mn_a + rng.randrange(400, 20000), mn_b, mn_b + rng.randrange(400, 20000))


def band(pay):
    return pay[0] >> 5


def erase_campaign(rng, nrng):
    print('Interrupted erase of sector 0 (sector 1 holds the newest record, seq 512):')
    print('    p  | wrong load | band 6 or 7 | example of a wrong seq')
    base = bytearray(b'\xff' * 8192)
    for s in range(512):
        base[16 * s:16 * s + 16] = ref.record(s + 1, settings(rng))
    sec0 = np.frombuffer(bytes(base[:4096]), dtype=np.uint8)
    zeros = np.unpackbits(~sec0)                        # 1 where a bit is 0
    sec1 = np.frombuffer(bytes(base[4096:]), dtype=np.uint8).reshape(256, 16)
    seqs1 = sec1[:, 1].astype(np.int64) << 8 | sec1[:, 2]
    first, checked = None, 0
    after = {'erase sector 1 (the one with the newest real record)': 0,
             'program into the half-erased sector 0 without erasing it': 0, 'other': 0}
    for p in (0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9):
        wrong = bad_band = 0
        example = None
        for t in range(TRIALS):
            flip = zeros & (nrng.random(zeros.size) < p)
            dam = (sec0 | np.packbits(flip)).astype(np.uint8)
            recs = dam.reshape(256, 16)
            ok = (recs[:, 0] == 0xA5) & (crc_rows(recs) == recs[:, 15])
            seqs = recs[:, 1].astype(np.int64) << 8 | recs[:, 2]
            best = pick(np.concatenate([ok, np.ones(256, bool)]), np.concatenate([seqs, seqs1]))
            predicted_wrong = best[1] != 512 or best[0] != 511
            if predicted_wrong or t % 200 == 0:
                mem = dam.tobytes() + bytes(base[4096:])
                pay, seq, nxt, erase = ref.scan(mem)
                checked += 1
                is_wrong = seq != 512 or pay != bytes(base[16 * 511 + 3:16 * 511 + 13])
                assert is_wrong == predicted_wrong, 'the vectorised count disagrees with ref.scan()'
                if is_wrong:
                    if erase and nxt >= 256:
                        after['erase sector 1 (the one with the newest real record)'] += 1
                    elif not erase and nxt < 256:
                        after['program into the half-erased sector 0 without erasing it'] += 1
                    else:
                        after['other'] += 1
                    wrong += 1
                    bad_band += band(pay) > 5
                    example = example if example is not None else seq
                    if first is None:
                        first = (p, mem, pay, seq)
        print(f'  {p:4.2f} | {wrong / TRIALS:9.2%} | {bad_band / TRIALS:10.2%} | {example}')
    print(f'  ({checked} images confirmed with ref.scan())')
    print('  The next save after a wrong load (ref.scan: next slot, erase first):')
    for k, v in after.items():
        print(f'    {k}: {v}')
    return first


def program_campaign(rng, nrng):
    print('Interrupted program of seq 357 into slot 356 (newest complete record: seq 356):')
    print('    q  | wrong load')
    base = bytearray(b'\xff' * 8192)
    for s in range(256, 356):
        base[16 * s:16 * s + 16] = ref.record(s + 1, settings(rng))
    for q in (0.02, 0.1, 0.3, 0.5, 0.7, 0.9):
        wrong = 0
        for t in range(TRIALS):
            pay_new = settings(rng)
            rec = np.frombuffer(ref.record(357, pay_new), dtype=np.uint8)
            want0 = np.unpackbits(~rec)                 # bits to be cleared
            left = want0 & (nrng.random(128) < q)       # ... still 1
            got = (rec | np.packbits(left)).astype(np.uint8)
            valid = got[0] == 0xA5 and crc_rows(got.reshape(1, 16))[0] == got[15]
            seq = int(got[1]) << 8 | int(got[2])
            # slots 256..355 hold 257..356 in order, so the scan ends on 356 unless slot 356 is a
            # valid record newer than 356
            predicted_wrong = bool(valid and newer(seq, 356) and not (seq == 357 and got[3:13].tobytes() == pay_new))
            if predicted_wrong or t % 200 == 0:
                mem = bytes(base[:16 * 356]) + got.tobytes() + bytes(base[16 * 357:])
                pay, s2, _, _ = ref.scan(mem)
                right = s2 == 356 or (s2 == 357 and pay == pay_new)
                assert (not right) == predicted_wrong, 'the vectorised count disagrees with ref.scan()'
                wrong += not right
        print(f'  {q:4.2f} | {wrong / TRIALS:9.3%}')


def main():
    rng, nrng = random.Random(14), np.random.default_rng(14)
    first = erase_campaign(rng, nrng)
    program_campaign(rng, nrng)
    if first is None:
        print('FL-1 NOT reproduced')
        return 1
    p, mem, pay, seq = first
    import test_flash_store as tf  # noqa: E402
    loads, end, out, ready = tf.run('review2_flash_interrupted', mem, [], end_ms=300)
    print(f'RTL on the first wrong image (p = {p}): loads {[(l.hex(), s) for l, s in loads]}; '
          f'model loads {pay.hex()} seq {seq} (band {band(pay)})')
    ok = loads == [(pay, seq)]
    print('FL-1 reproduced on the RTL' if ok else 'RTL differs from the model')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
