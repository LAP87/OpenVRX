"""Fixed-bin diagnostic from immutable existing Capture entries; no DUT imports."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

ENTRY = struct.Struct('<BBHIII')
SCOPE = dict(model_diagnostic_only=True, causal_proof=False, noisy_image_accepted=False,
             hardware=False, native=False, regenerated_inputs=False,
             noise_input_bytes_available=False, output_timestamps_available=False)
WINDOW = dict(bar_width=90, first=25, last=64, pixels_per_bar=40,
              alignment_search=False, gain_fit=False)


def profile(histogram, bar):
    n = sum(histogram)
    if not n:
        return dict(count=0, histogram=histogram, mean=None, p10=None, p50=None,
                    p90=None, minimum=None, maximum=None, sum=0, squared_error=0,
                    rmse=None, endpoint_count=0)
    total = sum(y*count for y, count in enumerate(histogram))
    error = sum((y-(16+31*bar))**2*count for y, count in enumerate(histogram))

    def percentile(p):
        target, seen = (n*p+99)//100, 0
        for y, count in enumerate(histogram):
            seen += count
            if seen >= target:
                return y

    used = [y for y, count in enumerate(histogram) if count]
    return dict(count=n, histogram=histogram, mean=total/n, p10=percentile(10),
                p50=percentile(50), p90=percentile(90), minimum=min(used),
                maximum=max(used), sum=total, squared_error=error,
                rmse=math.sqrt(error/n), endpoint_count=histogram[1]+histogram[254])


def parse(blob):
    assert len(blob) % ENTRY.size == 0, 'raw_shape'
    hist = {name:[[0]*256 for _ in range(8)] for name in ['all_closed', 'valid_closed']}
    pending = []
    counts = Counter(markers=0, complete_rows=0, valid_rows=0, malformed_rows=0,
                     bad_markers=0, chroma_errors=0, pixels=0, squared_error=0)
    fields, lengths = Counter(), Counter()
    for kind, field, line, index, data, length in ENTRY.iter_unpack(blob):
        assert kind in (0, 1), 'entry_kind'
        if kind == 0:
            pending.append((field, line, index, data))
            continue
        counts['markers'] += 1
        lengths[length] += 1
        counts['bad_markers'] += bool(data)
        shape = len(pending) == 360 and all(w[:3] == (field, line, i) for i,w in enumerate(pending))
        if not shape:
            counts['malformed_rows'] += 1
            pending = []
            continue
        counts['complete_rows'] += 1
        valid = data == 0 and abs(length-1716) <= 2
        if valid:
            counts['valid_rows'] += 1
            fields[field] += 1
        pixels = []
        for f, l, i, word in pending:
            counts['chroma_errors'] += word & 0x00ff00ff != 0x00800080
            pixels.extend(((word >> 8) & 255, word >> 24))
        counts['pixels'] += len(pixels)
        counts['squared_error'] += sum((y-(16+31*(x//90)))**2 for x,y in enumerate(pixels))
        for bar in range(8):
            for y in pixels[bar*90+25:bar*90+65]:
                hist['all_closed'][bar][y] += 1
                if valid:
                    hist['valid_closed'][bar][y] += 1
        pending = []
    counts['trailing_words'] = len(pending)
    metrics = dict(counts, valid_rows_by_field=dict(fields), marker_lengths=dict(lengths),
                   pixel_rmse=math.sqrt(counts['squared_error']/counts['pixels']) if counts['pixels'] else None)
    profiles = {}
    for name, bins in hist.items():
        bars = [profile(h, b) for b,h in enumerate(bins)]
        means = [b['mean'] for b in bars]
        steps = None if means[0] is None else [int(b>a)-int(b<a) for a,b in zip(means,means[1:])]
        profiles[name] = dict(bars=bars, mean_span=None if means[0] is None else means[-1]-means[0],
                              adjacent_mean_step_signs=steps)
    return metrics, profiles


def metadata(c, samples):
    lo, hi = c['clipping_zero'], c['clipping_max']
    assert 0 <= lo <= samples and 0 <= hi <= samples and lo+hi <= samples
    state, previous, locked = False, 0, 0
    for n, next_state in c['lock_trace']:
        assert previous <= n <= samples and isinstance(next_state, bool) and next_state != state
        if state:
            locked += n-previous
        state, previous = next_state, n
    if state:
        locked += samples-previous
    return dict(code_samples=samples, saved_code_endpoint_zero=lo, saved_code_endpoint_max=hi,
                saved_code_endpoint_fraction=(lo+hi)/samples, locked_sample_fraction=locked/samples,
                lock_acquisitions=sum(int(s) for n,s in c['lock_trace']),
                lock_losses=sum(int(not s) for n,s in c['lock_trace']),
                boot_rejects=c['boot_rejects'], original_luma_snr=c['original_luma_snr'],
                original_slicer=c['original_slicer'])


def analyse(selection):
    rows = []
    for node in selection['cases']:
        receipt = json.loads(Path(node['metadata']).read_text())
        c = next(c for c in receipt['cases'] if c['name'] == node['name'])
        blob = Path(node['raw']).read_bytes()
        assert len(blob) == c['raw']['bytes'] and hashlib.sha256(blob).hexdigest() == c['raw']['sha256'], 'raw_identity'
        metrics, profiles = parse(blob)
        assert json.loads(json.dumps(metrics)) == c['metrics'], 'original_metrics'
        rows.append(dict(id=node['id'], cn=receipt['parameters']['cn'], bits=c['bits'],
                         original_metrics=metrics, profiles=profiles,
                         saved_metadata=metadata(c,c['code_samples'])))
    return dict(scope=SCOPE, window=WINDOW, source_commit=selection['source_commit'], cases=rows)


if __name__ == '__main__':
    selection_path, out = map(Path, sys.argv[1:])
    out.mkdir(exist_ok=False)
    result = analyse(json.loads(selection_path.read_text()))
    (out/'PROFILES.json').write_text(json.dumps(result, indent=2)+'\n')
    print('read', len(result['cases']), 'saved cases; no model executed', flush=True)
