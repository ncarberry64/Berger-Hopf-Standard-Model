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
commands=[('tests',[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_birth_area_coupled_endpoint.py'])]
for run in ('run_1','run_2'):
    commands.append((run,[sys.executable,'-m','bhsm.interface.muon_birth_area_coupled_endpoint',
        '--base-directory','artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',
        '--area-response-directory','artifacts/muon_area_endpoint_response_20261011/run_1',
        '--output',f'artifacts/muon_area_coupled_endpoint_20261011/{run}',
        '--gamma','0.0001','--max-iterations','6']))
for name,argv in commands:
    proc=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
    for stream in ('stdout','stderr'):
        (folder/'execution_logs'/f'{name}.{stream}.txt').write_text(getattr(proc,stream),encoding='utf8',newline='\n')
    execution=dict(argv=argv,cwd=str(ROOT),environment_overrides={'PYTHONPATH':'src'},exit_code=proc.returncode,
        stdout_path=f'{name}.stdout.txt',stderr_path=f'{name}.stderr.txt')
    executions.append(execution)
    (folder/'execution_logs'/f'{name}.command.json').write_text(json.dumps(execution,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(execution),flush=True)
    if proc.returncode:raise SystemExit(proc.returncode)
pairs=[]
for filename in ('result.json','application.npz'):
    data=(folder/'run_1'/filename).read_bytes();other=(folder/'run_2'/filename).read_bytes()
    if data!=other:raise ValueError('independent replay differs: '+filename)
    pairs.append(dict(filename=filename,byte_identical=True,bytes=len(data),sha256=sha256(data).hexdigest()))
receipt=dict(executions=executions,pairs=pairs)
(folder/'verification.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(pairs=pairs,verification_sha256=sha256((folder/'verification.json').read_bytes()).hexdigest())),flush=True)
