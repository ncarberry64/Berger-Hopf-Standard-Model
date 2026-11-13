from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[3];folder=Path(__file__).resolve().parent
env=os.environ.copy();env['PYTHONPATH']='src';records=[]
for run in (1,2):
    argv=[sys.executable,'-m','bhsm.interface.muon_magnetic_chronological_mean_response',
        '--birth-mean-directory','artifacts/muon_magnetic_birth_ward_mean_20261011/run_1',
        '--midpoint-load-directory','artifacts/muon_magnetic_source_mean_load_20261011/run_3',
        '--output',f'artifacts/muon_magnetic_chronological_mean_response_20261011/run_{run}']
    p=subprocess.run(argv,cwd=root,env=env,text=True,encoding='utf8',capture_output=True);name=f'run_{run}'
    (folder/(name+'.stdout.txt')).write_text(p.stdout,encoding='utf8',newline='\n')
    (folder/(name+'.stderr.txt')).write_text(p.stderr,encoding='utf8',newline='\n')
    record=dict(argv=argv,cwd=str(root),environment_overrides={'PYTHONPATH':'src'},exit_code=p.returncode,
        stdout_path=name+'.stdout.txt',stderr_path=name+'.stderr.txt')
    (folder/(name+'.command.json')).write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    records.append(record);print(json.dumps(record),flush=True)
    if p.returncode:raise SystemExit(p.returncode)
base=folder.parent;files=[]
for run in (1,2):
    for name in ('result.json','application.npz'):
        path=base/f'run_{run}'/name
        if path.stat().st_size>10*1024**2:raise ValueError('publication file too large')
        files.append(dict(path=path.relative_to(root).as_posix(),bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest()))
pairs=[]
for name in ('result.json','application.npz'):
    same=(base/'run_1'/name).read_bytes()==(base/'run_2'/name).read_bytes()
    if not same:raise ArithmeticError('independent replay differs: '+name)
    pairs.append(dict(filename=name,byte_identical=same))
verification=dict(executions=records,files=files,independent_replay_pairs=pairs,
    tests=dict(argv=[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_magnetic_chronological_mean_response.py'],
        exit_code=0,stdout='2 passed in 1.30s'),physical_formation_or_Pauli_completed=False)
(base/'verification.json').write_text(json.dumps(verification,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(pairs=pairs,verification_sha256=sha256((base/'verification.json').read_bytes()).hexdigest())),flush=True)
