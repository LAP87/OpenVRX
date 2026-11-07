"""Independent source-byte arithmetic and observed-dependency checks, no DUT imports."""
import bisect
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

TRACE = struct.Struct('<IiIiIHHHH')
ENTRY = struct.Struct('<BBHIII')
OPTIONS = dict(lines=1050, sync=4, blank=20, white=60, comb=1, avg=8,
               white_x8=20, boot_check=True, gain=701, hardware=False, native=False)


def rounded_ratio(n, d):
    q, r = divmod(n, d)
    return q + int(2*r > d or (2*r == d and q % 2))


def geometry():
    return [rounded_ratio(k*12711111, 5000) for k in range(1051)]


def active(line):
    return 20 <= line <= 263 or 283 <= line <= 525


def lane_code(global_row, lane):
    value = ((global_row+1)*0x9e3779b1 + (lane+1)*0x85ebca77) & 0xffffffff
    value ^= value >> 16
    value = (value*0x7feb352d) & 0xffffffff
    value ^= value >> 15
    return 22 + value % 35


def check_record(record, codes, starts, options):
    assert options == OPTIONS, 'options'
    n0, p0, n1, p1, data, field, line, index, reserved = record
    assert reserved == 0 and 0 <= index < 360, 'record_shape'
    assert data & 0x00ff00ff == 0x00800080, 'chroma'
    assert 2 <= n1-n0 <= 3, 'sample_spacing'
    for n, partner, actual in [(n0, p0, (data >> 8) & 255),
                               (n1, p1, data >> 24)]:
        assert 0 <= n < len(codes), 'sample_bounds'
        row = bisect.bisect_right(starts, n)-1
        source_line = row % 525+1
        assert active(source_line), 'current_source_row'
        half = int(source_line >= 283)
        assert field == 1-half, 'field_label'
        assert line == source_line-(283 if half else 20), 'line_label'
        if partner < 0:
            assert source_line in (20, 283), 'missing_comb_partner'
            other = codes[n]
        else:
            assert 0 <= partner < n, 'partner_bounds'
            prev_row = bisect.bisect_right(starts, partner)-1
            assert prev_row == row-1, 'comb_source_row'
            assert active(prev_row % 525+1), 'comb_source_active'
            assert abs((n-starts[row])-(partner-starts[prev_row])) <= 3, 'comb_position'
            other = codes[partner]
        delta = codes[n]+other-40
        magnitude = abs(delta)*701//256
        expected = max(1, min(254, 16+(magnitude if delta >= 0 else -magnitude)))
        assert actual == expected, 'pixel_value'
    return True


def validate_packet(folder):
    folder = Path(folder)
    metadata = json.loads((folder/'RESULT.json').read_text())
    options = metadata['options']
    assert options == OPTIONS, 'options'
    codes = (folder/'codes.bin').read_bytes()
    assert hashlib.sha256(codes).hexdigest() == metadata['codes_sha256'], 'codes_identity'
    starts = geometry()
    assert len(codes) == starts[-1] and max(codes) < 64, 'source_shape'
    trace = (folder/'trace.bin').read_bytes()
    raw = (folder/'entries.bin').read_bytes()
    assert len(trace) % TRACE.size == len(raw) % ENTRY.size == 0
    counts, frames, phases = Counter(), Counter(), Counter()
    pending = []
    offset = 0
    unequal = partners = 0
    for kind, field, line, index, data, length in ENTRY.iter_unpack(raw):
        if kind == 0:
            record = TRACE.unpack_from(trace, offset)
            offset += TRACE.size
            check_record(record, codes, starts, options)
            assert record[4:8] == (data, field, line, index), 'trace_word_link'
            assert index == len(pending), 'word_order'
            pending.append(record)
            for n, p in [(record[0], record[1]), (record[2], record[3])]:
                counts['pixels'] += 1
                if p >= 0:
                    partners += 1
                    unequal += int(codes[n] != codes[p])
            continue
        assert kind == 1 and len(pending) == 360, 'closed_row_shape'
        assert all(r[5:7] == (field, line) for r in pending), 'marker_identity'
        assert data == 0 and abs(length-1716) <= 2, 'marker_validity'
        row = bisect.bisect_right(starts, pending[0][0])-1
        frames[row//525] += 1
        phases[field] += 1
        counts['closed_rows'] += 1
        pending = []
    assert offset == len(trace), 'trace_length'
    assert counts['closed_rows'] > 400 and set(frames) == {0, 1} and set(phases) == {0, 1}
    assert unequal*4 >= partners*3, 'nontrivial_partners'
    counts.update(partner_pixels=partners, unequal_partner_pixels=unequal,
                  trailing_words=len(pending), word_records=len(trace)//TRACE.size)
    return dict(counts=counts, rows_by_source_frame=frames, rows_by_output_field=phases)
