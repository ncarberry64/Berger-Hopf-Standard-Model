from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
FOLDER=ROOT/'artifacts/muon_finite_normal_phase_20261011'
LOG=FOLDER/'execution_logs'
env=dict(os.environ,PYTHONPATH='src')
executions=[]
def execute(argv,name):
    r=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
    (LOG/(name+'.stdout.txt')).write_text(r.stdout,encoding='utf8',newline='\n')
    (LOG/(name+'.stderr.txt')).write_text(r.stderr,encoding='utf8',newline='\n')
    receipt=dict(argv=argv,cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src'),exit_code=r.returncode,
        stdout_path=name+'.stdout.txt',stderr_path=name+'.stderr.txt')
    (LOG/(name+'.execution.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    executions.append(receipt);print(json.dumps(receipt,sort_keys=True),flush=True)
    if r.returncode:raise SystemExit(r.returncode)

source=ROOT/'src/bhsm/interface/muon_birth_finite_normal_phase.py'
guard=sha256(source.read_bytes()).hexdigest()
execute([sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_birth_finite_normal_phase.py'],'tests')
for side in ('incoming','outgoing'):
    for run in (1,2):
        name=f'{side}_run_{run}'
        execute([sys.executable,'-m','bhsm.interface.muon_birth_finite_normal_phase',
            '--base-directory','artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',
            '--output','artifacts/muon_finite_normal_phase_20261011/'+name,'--side',side,
            '--span='+('-1e-5' if side=='incoming' else '1e-5'),'--steps','1'],name)
        if sha256(source.read_bytes()).hexdigest()!=guard:raise RuntimeError('phase source changed')
pairs=[];files={}
for side in ('incoming','outgoing'):
    for filename in ('result.json','application.npz'):
        same=(FOLDER/(side+'_run_1')/filename).read_bytes()==(FOLDER/(side+'_run_2')/filename).read_bytes()
        pairs.append(dict(side=side,filename=filename,byte_identical=same))
        if not same:raise RuntimeError('independent phase pair differs')
        for run in (1,2):
            p=FOLDER/(side+f'_run_{run}')/filename;b=p.read_bytes()
            files[p.relative_to(ROOT).as_posix()]=dict(bytes=len(b),sha256=sha256(b).hexdigest())
receipt=dict(executions=executions,files=files,independent_replay_pairs=pairs,
    phase_source_sha256=guard,physical_cutoff_or_Pauli_completed=False,
    finite_outer_face_not_identified_with_E0=True)
path=FOLDER/'verification.json'
if path.exists():raise FileExistsError('preserve verification')
path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(verification_sha256=sha256(path.read_bytes()).hexdigest(),pairs=pairs),sort_keys=True))
