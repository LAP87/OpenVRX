#!/usr/bin/env python3
"""Verify two real schematic exports; date is the only ignored netlist value."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PUCK = HERE.parents[2] / 'OpenVRX-Puck'
OUT = PUCK / 'design/rev_a/out'


def canonical(path):
    return re.sub(r'\(date "[^"]*"\)', '(date "GENERATED")', path.read_text()).encode()


def generate(name):
    result = subprocess.run([sys.executable, 'design/rev_a/dekoderkort.py'], cwd=PUCK,
                            capture_output=True, text=True)
    log = result.stdout + result.stderr
    (HERE / name).write_text(log)
    assert result.returncode == 0, log
    assert 'No errors or warnings found while running ERC' in log
    assert '110 parts, 83 nets' in log and 'design checks passed' in log
    assert 'Random tag' not in log
    return log


generate('puck_generate.log')
files = sorted(OUT.glob('dekoderkort*'))
first = HERE / 'puck_export_first_lf'
first.mkdir()
for path in files:
    shutil.copy2(path, first / path.name)
before = {p.name: hashlib.sha256(canonical(p)).hexdigest() for p in files}
generate('puck_generate_repeat.log')
after = {p.name: hashlib.sha256(canonical(p)).hexdigest() for p in files}
assert before == after, (before, after)
assert '/home/owner/' not in (OUT / 'dekoderkort.net').read_text()
assert b'\r\n' not in (OUT / 'dekoderkort_bom.csv').read_bytes()
report = (OUT / 'dekoderkort_kopplingar.md').read_text()
assert '- 18 18: TVP_RESETB' in report and '- 10 10: TVP_RESETB' not in report
evidence = dict(core_commit=subprocess.check_output(['git', '-C', 'core', 'rev-parse', 'HEAD'], cwd=PUCK, text=True).strip(),
                parts=110, connected_nets=83, erc_errors=0, erc_warnings=0,
                repeat_identical_except_date=True, canonical_sha256=before,
                sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                random_tag_warnings=0,
                netlist_warnings='empty root tag required by KiCad; footprint libraries unavailable')
(HERE / 'puck_export_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
print('ERC 0 errors/0 warnings. Repeated exports match except date; J6-18 RESETB and LF CSV confirmed.')
