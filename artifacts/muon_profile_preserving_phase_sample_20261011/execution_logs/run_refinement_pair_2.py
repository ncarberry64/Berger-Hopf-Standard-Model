from hashlib import sha256
import json
from pathlib import Path
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
folder=Path(__file__).resolve().parents[1]
env=dict(os.environ,PYTHONPATH='src')
executions=[]
for side in ('outgoing','incoming'):
    for steps in (2,4):
        name=f'{side}_{steps}steps_run_2'
        module='muon_birth_inherited_finite_normal_phase'if side=='outgoing'else'muon_birth_finite_normal_phase'
        argv=[sys.executable,'-m','bhsm.interface.'+module,
            '--base-directory','artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',
            '--output',f'artifacts/muon_profile_preserving_phase_sample_20261011/{name}',
            '--span='+('1e-5'if side=='outgoing'else'-1e-5'),'--steps',str(steps),'--max-iterations','12']
        if side=='incoming':argv.extend(['--side','incoming'])
        proc=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
        for stream in ('stdout','stderr'):
            (folder/'execution_logs'/f'{name}.{stream}.txt').write_text(getattr(proc,stream),encoding='utf8',newline='\n')
        execution=dict(argv=argv,cwd=str(ROOT),environment_overrides={'PYTHONPATH':'src'},exit_code=proc.returncode,
            stdout_path=f'{name}.stdout.txt',stderr_path=f'{name}.stderr.txt')
        executions.append(execution)
        (folder/'execution_logs'/f'{name}.command.json').write_text(json.dumps(execution,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        print(json.dumps(execution),flush=True)
        if proc.returncode:raise SystemExit(proc.returncode)
(folder/'refinement_verification_run_2.json').write_text(json.dumps(dict(executions=executions),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(verification_sha256=sha256((folder/'refinement_verification_run_2.json').read_bytes()).hexdigest())),flush=True)
