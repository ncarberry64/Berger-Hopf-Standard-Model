from hashlib import sha256
import json
from pathlib import Path
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
folder=Path(__file__).resolve().parents[1];env=dict(os.environ,PYTHONPATH='src');executions=[]
commands=[('sampler_tests',[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_profile_preserving_phase_sample.py'])]
for side in ('incoming','outgoing'):
    phase='artifacts/muon_inherited_finite_normal_phase_20261011/run_1'if side=='outgoing'else'artifacts/muon_finite_normal_phase_20261011/incoming_run_1'
    for run in (1,2):
        name=f'{side}_sample_run_{run}'
        commands.append((name,[sys.executable,'-m','bhsm.interface.muon_profile_preserving_phase_sample',
            '--phase-directory',phase,'--output',f'artifacts/muon_profile_preserving_phase_sample_20261011/{name}']))
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
for side in ('incoming','outgoing'):
    for filename in ('result.json','application.npz'):
        data=(folder/f'{side}_sample_run_1'/filename).read_bytes();other=(folder/f'{side}_sample_run_2'/filename).read_bytes()
        if data!=other:raise ValueError('independent replay differs: '+filename)
        pairs.append(dict(side=side,filename=filename,byte_identical=True,bytes=len(data),sha256=sha256(data).hexdigest()))
(folder/'sample_verification.json').write_text(json.dumps(dict(executions=executions,pairs=pairs),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(pairs=pairs,verification_sha256=sha256((folder/'sample_verification.json').read_bytes()).hexdigest())),flush=True)
