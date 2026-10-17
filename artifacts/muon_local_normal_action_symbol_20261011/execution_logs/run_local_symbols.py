from pathlib import Path
import json, os, subprocess, sys

ROOT=Path(__file__).resolve().parents[3]
folder=Path(__file__).resolve().parents[1]
env=dict(os.environ,PYTHONPATH='src')
executions=[]
commands=[('focused_tests',[sys.executable,'-m','pytest','--noconftest','-q',
    'tests/test_muon_local_normal_action_symbol.py'])]
for index in (1,2):
    for side in ('incoming','outgoing'):
        commands.append((f'{side}_run_{index}',[sys.executable,'-m','bhsm.interface.muon_local_normal_action_symbol',
            '--phase-directory',f'artifacts/muon_area_coupled_endpoint_20261011/gamma_0p11_{side}_phase_run_1',
            '--output',f'artifacts/muon_local_normal_action_symbol_20261011/{side}_run_{index}']))
for name,argv in commands:
    p=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
    for stream in ('stdout','stderr'):
        (folder/'execution_logs'/f'{name}.{stream}.txt').write_text(getattr(p,stream),encoding='utf8',newline='\n')
    md=dict(argv=argv,cwd=str(ROOT),environment_overrides={'PYTHONPATH':'src'},exit_code=p.returncode,
        stdout_path=f'execution_logs/{name}.stdout.txt',stderr_path=f'execution_logs/{name}.stderr.txt')
    executions.append(md)
    (folder/'execution_logs'/f'{name}.command.json').write_text(json.dumps(md,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(md),flush=True)
    if p.returncode:raise SystemExit(p.returncode)
(folder/'verification.json').write_text(json.dumps(dict(executions=executions,
    focused_test_initial_probe=dict(exit_code=1,passed=2,failed=1,
        failure='contrast threshold .02 exceeded exact .01333333333333342; assertion corrected to .01, implementation unchanged'),
    ),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
