from hashlib import sha256
import json,os,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];folder=Path(__file__).resolve().parents[1]
env=dict(os.environ,PYTHONPATH='src');executions=[]
commands=[('tests',[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_common_normal_boundary_form.py'])]
for family in ('base','area'):
    source='artifacts/muon_finite_normal_boundary_action_20261011'if family=='base'else'artifacts/muon_area_coupled_endpoint_20261011'
    for run in (1,2):
        ip=source+('/incoming_run_1'if family=='base'else'/incoming_boundary_run_1')
        op=source+('/outgoing_run_1'if family=='base'else'/outgoing_boundary_run_1')
        name=f'{family}_run_{run}'
        commands.append((name,[sys.executable,'-m','bhsm.interface.muon_common_normal_boundary_form','--incoming-boundary',ip,
            '--child-boundary',op,'--output',f'artifacts/muon_common_normal_boundary_form_20261011/{name}']))
for name,argv in commands:
    proc=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
    for stream in ('stdout','stderr'):(folder/'execution_logs'/f'{name}.{stream}.txt').write_text(getattr(proc,stream),encoding='utf8',newline='\n')
    md=dict(argv=argv,cwd=str(ROOT),environment_overrides={'PYTHONPATH':'src'},exit_code=proc.returncode,stdout_path=f'{name}.stdout.txt',stderr_path=f'{name}.stderr.txt')
    executions.append(md);(folder/'execution_logs'/f'{name}.command.json').write_text(json.dumps(md,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(md),flush=True)
    if proc.returncode:raise SystemExit(proc.returncode)
pairs=[]
for family in ('base','area'):
    for filename in ('result.json','application.npz'):
        data=(folder/f'{family}_run_1'/filename).read_bytes()
        if data!=(folder/f'{family}_run_2'/filename).read_bytes():raise ValueError('independent application replay differs')
        pairs.append(dict(family=family,filename=filename,byte_identical=True,bytes=len(data),sha256=sha256(data).hexdigest()))
(folder/'verification.json').write_text(json.dumps(dict(executions=executions,pairs=pairs),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(pairs=pairs),sort_keys=True))
