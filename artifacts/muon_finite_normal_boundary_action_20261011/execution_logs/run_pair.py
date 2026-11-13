from hashlib import sha256
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];folder=Path(__file__).resolve().parents[1]
env=dict(os.environ,PYTHONPATH='src');executions=[]
commands=[('tests',[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_birth_finite_normal_boundary_action.py'])]
for side,source in (('incoming','muon_finite_normal_phase_20261011/incoming_run_1'),('outgoing','muon_inherited_finite_normal_phase_20261011/run_1')):
    for i in (1,2):
        name=f'{side}_run_{i}'
        commands.append((name,[sys.executable,'-m','bhsm.interface.muon_birth_finite_normal_boundary_action',
            '--phase-directory','artifacts/'+source,'--output',f'artifacts/muon_finite_normal_boundary_action_20261011/{name}']))
for name,argv in commands:
    proc=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
    for stream in ('stdout','stderr'):(folder/'execution_logs'/f'{name}.{stream}.txt').write_text(getattr(proc,stream),encoding='utf8',newline='\n')
    item=dict(argv=argv,cwd=str(ROOT),environment_overrides={'PYTHONPATH':'src'},exit_code=proc.returncode,
        stdout_path=f'{name}.stdout.txt',stderr_path=f'{name}.stderr.txt');executions.append(item)
    (folder/'execution_logs'/f'{name}.command.json').write_text(json.dumps(item,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(item),flush=True)
    if proc.returncode:raise SystemExit(proc.returncode)
pairs=[]
for side in ('incoming','outgoing'):
    for filename in ('result.json','application.npz'):
        data=(folder/f'{side}_run_1'/filename).read_bytes();other=(folder/f'{side}_run_2'/filename).read_bytes()
        if data!=other:raise ValueError('independent run differs')
        pairs.append(dict(side=side,filename=filename,byte_identical=True,bytes=len(data),sha256=sha256(data).hexdigest()))
receipt=dict(executions=executions,pairs=pairs)
(folder/'verification.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(pairs=pairs,verification_sha256=sha256((folder/'verification.json').read_bytes()).hexdigest())),flush=True)
