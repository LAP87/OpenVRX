"""First isolated nominal Capture observation with passive line-buffer origin tags."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from oracle import ENTRY, TRACE, OPTIONS, active, geometry, lane_code

source, out = map(Path, sys.argv[1:])
out.mkdir(exist_ok=False)
spec = importlib.util.spec_from_file_location('frozen_capture', source/'gateware/model/cvbs_capture_ref.py')
cv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cv)
assert (cv.AVG, cv.ACT_START, cv.WHITE_X8_STD) == (8, 362, 20)
starts = geometry()
codes = bytearray([20])*starts[-1]
source_patterns = []
for k in range(1050):
    line = k % 525+1
    begin, end = starts[k:k+2]
    half = round((begin+end)/2)
    if 1 <= line <= 3 or 7 <= line <= 9 or 264 <= line <= 265 or 270 <= line <= 271:
        pulses = [(begin, 92), (half, 92)]
    elif 4 <= line <= 6 or 267 <= line <= 268:
        pulses = [(begin, 1083), (half, 1083)]
    elif line == 263:
        pulses = [(begin, 188), (half, 92)]
    elif line == 266:
        pulses = [(begin, 92), (half, 1083)]
    elif line == 269:
        pulses = [(begin, 1083), (half, 92)]
    elif line == 272:
        pulses = [(begin, 92)]
    else:
        pulses = [(begin, 188)]
    for a, width in pulses:
        codes[a:min(a+width, end)] = bytes([4])*min(width, end-a)
    if active(line):
        pattern = [lane_code(k, lane) for lane in range(8)]
        source_patterns.append(pattern)
        # Rectangular source lanes, no IQ, analogue low-pass, or colour burst.
        for p in range(362, 2495):
            lane = min(7, (p-362)*8//2133)
            codes[begin+p] = pattern[lane]
assert len(set(map(tuple, source_patterns))) == len(source_patterns)
(out/'codes.bin').write_bytes(codes)


class Origins(list):
    def __init__(self, owner):
        super().__init__([0]*4096)
        self.origins = [-1]*4096
        self.owner = owner

    def __setitem__(self, p, value):
        super().__setitem__(p, value)
        self.origins[p] = self.owner.n

    def __getitem__(self, p):
        value = super().__getitem__(p)
        observed['partner'] = self.origins[p]
        return value


capture = cv.Capture(comb=True, avg=8, white_x8=20, boot_check=True)
observed = {}
capture.prev_line, capture.cur_line_buf = Origins(capture), Origins(capture)
emitted = 0
pending = None
with (out/'trace.bin').open('xb') as trace, (out/'entries.bin').open('xb') as raw:
    for n, sample in enumerate(codes):
        before = capture.y_count
        observed.clear()
        capture.step(int(sample))
        if capture.y_count == before+1:
            pixel = (n, observed.get('partner', -1))
            if capture.y_count % 2:
                pending = pixel
            else:
                word = capture.entries[-1]
                assert word[0] == 'word' and pending is not None
                _, field, line, index, data = word
                trace.write(TRACE.pack(*pending, *pixel, data, field, line, index, 0))
                pending = None
        for entry in capture.entries[emitted:]:
            if entry[0] == 'word':
                _, field, line, index, data = entry
                raw.write(ENTRY.pack(0, field, line, index, data, 0))
            else:
                _, field, line, hf, bad, length = entry
                raw.write(ENTRY.pack(1, field, line, hf, bad, length))
        emitted = len(capture.entries)
metadata = dict(options=OPTIONS, source_commit='031bba053943ee04ce303ae75b5e701746169c97',
                codes_sha256=hashlib.sha256(codes).hexdigest(), source_patterns=len(source_patterns),
                unique_source_patterns=len(set(map(tuple, source_patterns))),
                entries=len(capture.entries), lock_trace=capture.lock_trace,
                observed_only=True, producer_changed=False, hardware=False, native=False)
(out/'RESULT.json').write_text(json.dumps(metadata, indent=2)+'\n')
print(json.dumps(metadata), flush=True)
