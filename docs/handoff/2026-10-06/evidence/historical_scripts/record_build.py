#!/usr/bin/env python3
"""Capture build inputs, then archive outputs against the accepted Core commit.

Run with Core's venv. `prepare <top>` must precede its build. After tests,
builds and the Core commit: `archive`. Prior snapshots are never replaced.
This records internal timing only; it does not establish board I/O margins.
"""
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORE = ROOT / 'OpenVRX-Core'
TOPS = ('m0_testpattern', 'm3_probe', 'm4_dual_mix', 'm6_puck_proto')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=CORE)


def prepare(top):
    assert top in TOPS
    target = HERE / f'{top}.inputs.json'
    assert not target.exists(), f'input snapshot already exists: {target}'
    gw = CORE / 'gateware'
    paths = [gw / 'build.sh', CORE / 'requirements.txt', gw / 'top' / f'{top}.v',
             gw / 'boards/tangnano20k.cst']
    paths += sorted(p for p in (gw / 'rtl').iterdir() if p.suffix in ('.v', '.vh'))
    paths += [p for p in (gw / 'boards' / f'{top}.cst', gw / 'boards' / f'{top}.sdc') if p.exists()]
    data = dict(top=top, command=f'gateware/build.sh {top}',
                freq_mhz=os.environ.get('FREQ_MHZ', '75'), pull=os.environ.get('PULL'),
                inputs={str(p.relative_to(CORE)): sha(p) for p in paths},
                tools={name: version(name) for name in
                       ('yowasp-yosys', 'yowasp-nextpnr-himbaechel-gowin',
                        'apycula', 'cocotb', 'pytest', 'skidl')})
    assert data['pull'] is None and data['freq_mhz'] == '75'
    target.write_text(json.dumps(data, indent=2) + '\n')
    shutil.copy2(gw / 'build.sh', HERE / f'{top}.executed.build.sh')
    print(f'captured {top}: {len(paths)} source/config files')


def archive():
    commit = git('rev-parse', 'HEAD').decode().strip()
    assert not git('status', '--porcelain').strip(), 'Core must be committed before archiving'
    destination = ROOT / 'private/bitstreams' / f'2026-10-05_{commit[:12]}'
    assert not destination.exists(), f'archive already exists: {destination}'
    entries = []
    for top in TOPS:
        data = json.loads((HERE / f'{top}.inputs.json').read_text())
        script = HERE / f'{top}.executed.build.sh'
        expected_script = data['inputs'].pop('gateware/build.sh')
        assert sha(script) == expected_script, f'wrong executed build script: {top}'
        committed_script = git('show', f'{commit}:gateware/build.sh')
        divider = b'# nextpnr prints the clock table twice:'
        assert divider in script.read_bytes() and divider in committed_script
        assert script.read_bytes().split(divider)[0] == committed_script.split(divider)[0], 'commands through packing changed'
        data['build_script'] = dict(at_run_sha256=expected_script,
                                   at_commit_sha256=hashlib.sha256(committed_script).hexdigest(),
                                   commands_through_packing_identical=True,
                                   snapshot=script.name)
        # M4 packed successfully before the old summary pipeline received
        # SIGPIPE. The corrected summary was separately executed on its log.
        data['command_exit_code'] = 141 if top == 'm4_dual_mix' else 0
        if top == 'm4_dual_mix':
            assert json.loads((HERE / 'summary_exit_check.json').read_text())[top]['returncode'] == 0
            data['summary_after_fix_exit_code'] = 0
            data['exit_explanation'] = 'SIGPIPE in old summary after successful synthesis, routing and packing'
        for rel, expected in data['inputs'].items():
            assert sha(CORE / rel) == expected, f'build input changed: {rel}'
            blob = git('show', f'{commit}:{rel}')
            assert hashlib.sha256(blob).hexdigest() == expected, f'uncommitted build input: {rel}'
        out = CORE / 'gateware/build'
        log = (out / f'{top}.pnr.log').read_text()
        clocks = {}
        for match in re.finditer(r"Max frequency for clock\s+'([^']+)': ([0-9.]+) MHz \((PASS|FAIL) at ([0-9.]+) MHz\)", log):
            name, fmax, result, required = match.groups()
            clocks[name] = dict(fmax_mhz=float(fmax), required_mhz=float(required), result=result)
        assert clocks and all(c['result'] == 'PASS' for c in clocks.values()), f'final clock constraint failed: {top}'
        utilisation = {}
        for name in ('LUT4', 'DFF', 'BSRAM'):
            match = re.search(rf'\b{name}:\s+(\d+)/\s*(\d+)\s+(\d+)%', log)
            assert match, f'no {name} utilisation: {top}'
            utilisation[name] = dict(used=int(match[1]), available=int(match[2]), percent=int(match[3]))
        files = [out / f'{top}{suffix}' for suffix in ('.fs', '.pnr.log', '.yosys.log', '.stat.txt', '.cst')]
        files.append(script)
        sdc = out / f'{top}.sdc'
        if sdc.exists():
            files.append(sdc)
        assert all(p.is_file() for p in files)
        data.update(commit=commit, final_clocks=clocks, utilisation=utilisation,
                    outputs={p.name: sha(p) for p in files})
        entries.append((data, files))
    destination.mkdir()
    for data, files in entries:
        for p in files:
            shutil.copy2(p, destination / p.name)
        (destination / f"{data['top']}.inputs.json").write_text(json.dumps(data, indent=2) + '\n')
    manifest = dict(core_commit=commit, hardware_tested=False, internal_timing_only=True,
                    m3_m4_m6_board_revision='3923; verify actual board before connecting modules',
                    builds=[data for data, _ in entries])
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (HERE / 'build_evidence.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for data, _ in entries:
        print(data['top'], data['utilisation'], data['final_clocks'])
    print(f'archived: {destination}')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'prepare':
        prepare(sys.argv[2])
    elif sys.argv[1:] == ['archive']:
        archive()
    else:
        raise SystemExit('usage: record_build.py prepare <top> | archive')
