from pathlib import Path
import importlib.util
import builtins
import json,subprocess
root=Path('/home/lenny/Projekt/DIY_Drone_Lab/projects/OpenVRX-repos')
work=Path(__file__).resolve().parent
src=root/'OpenVRX-Puck/design/rev_a/dekoderkort.py'
s=importlib.util.spec_from_file_location('decoder_audit',src)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.OUT=work/'schematic_current_source'
m.build()
c=builtins.default_circuit
problems=m.design_checks(c)
result={'design_check_problems':problems,'part_count':len(c.parts),'checked_core_submodule':subprocess.check_output(['git','-C',str(root/'OpenVRX-Puck/core'),'rev-parse','HEAD'],text=True).strip(), 'core_led_assignment':next(l.strip() for l in (root/'OpenVRX-Puck/core/gateware/top/m4_dual_mix.v').read_text().splitlines() if 'assign led =' in l), 'header_reset_pin':[int(pin.num) for p in c.parts if p.name=='CONN_1x20' and 'J6' in p.fields['note'] for pin in p.pins if pin.net is not None and pin.net.name=='TVP_RESETB']}
print('SCHEMATIC AUDIT',json.dumps(result),flush=True)
m.OUT.mkdir(parents=True,exist_ok=True)
m.ERC()
m.generate_netlist(file_=str(m.OUT/'dekoderkort.net'))
m.write_reports(c)
(work/'schematic_check_results.json').write_text(json.dumps(result,indent=2))
