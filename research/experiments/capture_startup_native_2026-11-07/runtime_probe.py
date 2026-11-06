"""One runtime inspection, no project imports or compile/simulation."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

source, output = map(Path,sys.argv[1:])
assert not output.exists()
result = dict(python=sys.version,executable=sys.executable,prefix=sys.prefix,
              packages={p:importlib.metadata.version(p) for p in ['pytest','numpy','cocotb']},tools=[])
for tool in ['iverilog','vvp']:
    binary = (source/'.tools/iverilog/bin'/tool).resolve()
    command = [str(binary),'-V']
    run = subprocess.run(command,capture_output=True,text=True)
    result['tools'].append(dict(name=tool,binary=str(binary),argv=command,rc=run.returncode,
                               size=binary.stat().st_size,sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                               stdout=run.stdout,stderr=run.stderr))
    output.write_text(json.dumps(result,indent=2)+'\n')
    assert run.returncode == 0
print(result['python'].splitlines()[0],result['prefix'])
for tool in result['tools']:
    print(tool['name'],(tool['stdout']+tool['stderr']).splitlines()[0],tool['rc'])
