"""Independent native wire parser and source-time review; no model/DUT imports."""
import bisect
from collections import Counter
import copy
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import tarfile

HOME = Path(__file__).resolve().parent
IDS = ('gated_avg8', 'gated_avg16', 'no_v_avg16')
ENTRY = struct.Struct('<BBHIII')
TIME = struct.Struct('<II')


def read(p):
    return json.loads(Path(p).read_text())


def digest(p):
    p = Path(p)
    return dict(path=str(p.resolve()), size=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def claims(c, expected):
    assert c['node'] == expected['node'], 'node'
    assert c['compiled_parameters'] == expected['compiled_parameters'], 'parameters'
    assert c['output_sha256'] == expected['output_sha256'], 'raw'
    for k in ('image_accepted', 'broader_native_accepted', 'hardware'):
        assert c[k] is False, k


def ended(identity):
    p = Path('/proc') / str(identity['pid']) / 'stat'
    if p.exists():
        fields = p.read_text().rsplit(')', 1)[1].split()
        assert int(fields[19]) != identity['startticks'], 'original_process_still_live'


def inspect():
    cases = {}
    starts = [round(Fraction(k * 12711111, 5000)) for k in range(1051)]
    parent = read(HOME.parent / 'avg83/positive-data/OBSERVATION.json')
    for name in IDS:
        manifest = read(HOME / (name + '.json'))
        directory = HOME / (name + '-data')
        job = read(HOME / (name + '-job/RESULT.json'))
        native = read(directory / 'NATIVE.json')
        assert job['returncode'] == 0 and job['inputs_unchanged'] and not job['signals']
        ended(job['process'])
        assert len(native['calls']) == 2
        for call, role in zip(native['calls'], ('compile', 'simulate')):
            assert call['name'] == role and call['returncode'] == 0
            assert call['process']['pgrp'] == job['process']['pgrp']
            ended(call['process'])
        assert native['node'] == manifest['node']
        codes = Path(manifest['codes']).read_bytes()
        assert len(codes) == manifest['samples'] == 2669333
        assert hashlib.sha256(codes).hexdigest() == manifest['codes_sha256']
        hexdata = (directory / 'samples.hex').read_bytes()
        assert bytes.fromhex(hexdata.decode()) == codes
        assert hashlib.sha256(hexdata).hexdigest() == manifest['hex_sha256']
        parameters = {}
        for line in (directory / 'sim.vvp').read_text().splitlines():
            if '.param/' not in line:
                continue
            m = re.search(r'"(AVG|COMB|WHITE_X8|SW)".*C4<([01]+)>', line)
            if m:
                parameters.setdefault(m[1], []).append(int(m[2], 2))
        expected_params = dict(AVG=[manifest['avg']], COMB=[1], WHITE_X8=[20],
                               SW=[10 if manifest['avg'] == 8 else 11])
        assert parameters == expected_params == native['compiled_parameters']
        complete = re.search(r'RESULT samples=(\d+) entries=(\d+)',
                             (directory / 'simulate.stdout').read_text())
        assert complete and int(complete[1]) == len(codes)
        raw = bytearray()
        times = bytearray()
        first_words = []
        closed = 0
        pending = []
        for index, line in enumerate((directory / 'entries.txt').read_text().splitlines()):
            time_text, encoded = line.split()
            n, word = int(time_text), int(encoded, 16)
            assert word < 1 << 53 and 0 <= n <= len(codes) + 8
            field, row = (word >> 51) & 1, (word >> 41) & 1023
            if word & (1 << 52):
                raw += ENTRY.pack(1, field, row, (word >> 21) & 1048575,
                                  (word >> 17) & 15, (word >> 1) & 4095)
                assert len(pending) == 360 and pending == [(field, row, x) for x in range(360)]
                closed += 1
                pending = []
            else:
                x = (word >> 32) & 511
                raw += ENTRY.pack(0, field, row, x, word & 4294967295, 0)
                times += TIME.pack(index, n)
                pending.append((field, row, x))
                if x == 0:
                    source_row = bisect.bisect_right(starts, n) - 1
                    local = source_row % 525 + 1
                    expected = local - (283 if local > 263 else 20)
                    first_words.append(dict(sample=n, source_global_row=source_row + 1,
                                            output_field=field, output_line=row,
                                            line_offset=row - expected,
                                            first_word_phase=n - starts[source_row]))
        model = Path(manifest['model']).read_bytes()
        assert bytes(raw) == (directory / 'entries.bin').read_bytes() == model
        assert bytes(times) == (directory / 'word_times.bin').read_bytes()
        assert len(raw) // ENTRY.size == int(complete[2]) == native['entries']
        result = dict(node=manifest['node'], compiled_parameters=parameters,
                      entries=len(raw) // ENTRY.size, closed_rows=closed,
                      trailing_words=len(pending), output_sha256=hashlib.sha256(raw).hexdigest(),
                      model_bit_equal=True, image_accepted=False, broader_native_accepted=False,
                      hardware=False, driver_seconds=job['elapsed_seconds'],
                      calls=native['calls'], source_attribution=first_words[:closed])
        if name == 'gated_avg16':
            assert closed == parent['valid_rows'] == 723 and parent['valid_rows_within16'] == 0
            old = parent['source_attribution']
            assert len(old) == closed
            for actual, previous in zip(first_words[:closed], old):
                for key in ('source_global_row', 'output_field', 'output_line', 'line_offset'):
                    assert actual[key] == previous[key], 'source_time_attribution'
            result['label_offsets'] = dict(sorted(Counter(r['line_offset'] for r in first_words[:closed]).items()))
            result['source_line_offsets_nonzero'] = sum(r['line_offset'] != 0 for r in first_words[:closed])
            result['quality_rows_reused_from_identical_model_raw'] = 0
            old_times = list(TIME.iter_unpack((HOME.parent / 'avg83/positive-data/word_times.bin').read_bytes()))
            new_times = list(TIME.iter_unpack(times))
            assert [x[0] for x in new_times] == [x[0] for x in old_times]
            result['native_minus_model_sample_counts'] = dict(sorted(Counter(a[1] - b[1] for a, b in zip(new_times, old_times)).items()))
            assert result['source_line_offsets_nonzero'] == 377
        else:
            assert not raw and not first_words and closed == 0
        cases[name] = result
    closure = read(HOME.parent / 'provenance79/SOURCE_CLOSURE.json')
    source = Path(read(HOME / 'gated_avg8.json')['source'])
    assert subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() == closure['commit']
    assert subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD^{tree}'], text=True).strip() == closure['tree']
    archive = subprocess.check_output(['git', '-C', str(source), 'archive', closure['commit']])
    assert hashlib.sha256(archive).hexdigest() == closure['archive_sha256']
    count = 0
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
        for member in tf:
            if member.isfile():
                assert (source / member.name).read_bytes() == tf.extractfile(member).read()
                count += 1
    assert count == 264
    assert (HOME / 'tb_cvbs_capture_time.v').read_bytes() == (HOME.parent / 'native77/tb_cvbs_capture_time.v').read_bytes()
    return dict(cases=cases, source_files=count, commit=closure['commit'], tree=closure['tree'],
                native_calls=6, semantic_masked_input_negative_caught=True,
                fidelity_only=True, image_accepted=False, hardware=False,
                broader_native_accepted=False, producer_changed=False)


def main():
    mode, output = sys.argv[1:]
    out = Path(output)
    out.mkdir(exist_ok=False)
    result = json.loads(json.dumps(inspect()))
    value = result['cases']['gated_avg16']
    controls = []
    if mode == 'root':
        (out / 'controls').mkdir()
        for name in ('raw', 'parameters', 'node', 'image_accepted', 'broader_native_accepted', 'hardware'):
            damaged = copy.deepcopy(value)
            if name == 'raw':
                raw = bytearray((HOME / 'gated_avg16-data/entries.bin').read_bytes())
                raw[8] ^= 1
                p = out / 'controls/raw.bin'
                p.write_bytes(raw)
                damaged['output_sha256'] = digest(p)['sha256']
            elif name == 'parameters':
                damaged['compiled_parameters']['AVG'] = [8]
            elif name == 'node':
                damaged['node'] = 'foreign/native'
            else:
                damaged[name] = True
            p = out / 'controls' / (name + '.json')
            p.write_text(json.dumps(damaged) + '\n')
            try:
                claims(read(p), value)
            except AssertionError as e:
                assert str(e) == name
                controls.append(dict(name=name, reason=str(e), file=str(p), binding=digest(p)))
            else:
                raise AssertionError('control_not_caught')
            claims(value, value)
        result['controls'] = controls
        (out / 'ROOT_REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        root = read(HOME / 'root-data/ROOT_REVIEW.json')
        controls = root.pop('controls')
        assert result == root
        for control in controls:
            assert digest(control['file']) == control['binding']
            try:
                claims(read(control['file']), value)
            except AssertionError as e:
                assert str(e) == control['reason']
            else:
                raise AssertionError('existing_control_not_caught')
        raw_fault = (HOME / 'root-data/controls/raw.bin').read_bytes()
        original = bytearray((HOME / 'gated_avg16-data/entries.bin').read_bytes())
        original[8] ^= 1
        assert raw_fault == original
        jobs = {}
        for name in (*[i + '-job' for i in IDS], 'root-job'):
            job = read(HOME / name / 'RESULT.json')
            assert job['returncode'] == 0 and job['inputs_unchanged'] and not job['signals']
            ended(job['process'])
            for binding in job['bindings'] + [job['stdout'], job['stderr']]:
                assert digest(binding['path']) == binding
            jobs[name] = {k: job[k] for k in ('returncode', 'elapsed_seconds', 'signals')}
        inventory = [digest(p) for name in (*[i + '-data' for i in IDS], *jobs, 'root-data')
                     for p in sorted((HOME / name).rglob('*')) if p.is_file()]
        (out / 'RAW_INVENTORY.json').write_text(json.dumps(inventory, indent=2) + '\n')
        final = dict(status='FINAL_NATIVE_FIDELITY_REVIEWED_IMAGE_UNACCEPTED', native_calls=6,
                     source_files=264, cases={k: {a: v for a, v in r.items() if a not in ('source_attribution', 'calls')} for k, r in result['cases'].items()},
                     image_accepted=False, hardware=False, broader_native_accepted=False,
                     producer_changed=False, controls_rejected=len(controls), controls_recreated=False,
                     jobs=jobs, raw_files=len(inventory), raw_bytes=sum(p['size'] for p in inventory),
                     publication_pending=True)
        for name in ('FINAL_REVIEW.json', 'PACKAGE_FIDELITY_PREPUBLICATION.json'):
            (out / name).write_text(json.dumps(final, indent=2) + '\n')
    print(mode, 'native fidelity reviewed; image remains unaccepted', flush=True)


if __name__ == '__main__':
    main()
