from pathlib import Path
import json, os, subprocess, sys

ROOT=Path(__file__).resolve().parents[3]
folder=Path(__file__).resolve().parents[1]
env=dict(os.environ,PYTHONPATH='src')
executions=[]
for index in (1,2):
    name=f'run_{index}'
    argv=[sys.executable,'-m','bhsm.interface.muon_positive_area_endpoint_response',
        '--base-directory','artifacts/muon_area_coupled_endpoint_20261011/gamma_0p11_run_1',
        '--output',f'artifacts/muon_positive_area_endpoint_response_20261011/{name}']
    p=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
    for stream in ('stdout','stderr'):
        (folder/'execution_logs'/f'{name}.{stream}.txt').write_text(getattr(p,stream),encoding='utf8',newline='\n')
    md=dict(argv=argv,cwd=str(ROOT),environment_overrides={'PYTHONPATH':'src'},exit_code=p.returncode,
        stdout_path=f'execution_logs/{name}.stdout.txt',stderr_path=f'execution_logs/{name}.stderr.txt')
    executions.append(md)
    (folder/'execution_logs'/f'{name}.command.json').write_text(json.dumps(md,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(md),flush=True)
    if p.returncode:raise SystemExit(p.returncode)
(folder/'verification.json').write_text(json.dumps(dict(executions=executions),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
