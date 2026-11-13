from hashlib import sha256
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];F=ROOT/'artifacts/muon_area_endpoint_response_20261011';LOG=F/'execution_logs';env=dict(os.environ,PYTHONPATH='src');executions=[]
source=ROOT/'src/bhsm/interface/muon_birth_area_endpoint_response.py';guard=sha256(source.read_bytes()).hexdigest()
commands=[('tests',[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_birth_area_endpoint_response.py'])]
for i in (1,2):commands.append((f'run_{i}',[sys.executable,'-m','bhsm.interface.muon_birth_area_endpoint_response','--base-directory','artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1','--output',f'artifacts/muon_area_endpoint_response_20261011/run_{i}']))
for name,argv in commands:
    r=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
    for label,data in (('stdout',r.stdout),('stderr',r.stderr)):(LOG/(name+'.'+label+'.txt')).write_text(data,encoding='utf8',newline='\n')
    q=dict(argv=argv,cwd=str(ROOT),environment_overrides=dict(PYTHONPATH='src'),exit_code=r.returncode,stdout_path=name+'.stdout.txt',stderr_path=name+'.stderr.txt');executions.append(q)
    (LOG/(name+'.execution.json')).write_text(json.dumps(q,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');print(json.dumps(q,sort_keys=True),flush=True)
    if r.returncode:raise SystemExit(r.returncode)
    if sha256(source.read_bytes()).hexdigest()!=guard:raise RuntimeError('area producer changed')
pairs=[];files={}
for name in ('result.json','application.npz'):
    same=(F/'run_1'/name).read_bytes()==(F/'run_2'/name).read_bytes();pairs.append(dict(filename=name,byte_identical=same))
    if not same:raise RuntimeError('independent area pair differs')
    for i in (1,2):
        p=F/f'run_{i}'/name;b=p.read_bytes();files[p.relative_to(ROOT).as_posix()]=dict(bytes=len(b),sha256=sha256(b).hexdigest())
path=F/'verification.json'
if path.exists():raise FileExistsError('preserve verification')
path.write_text(json.dumps(dict(executions=executions,files=files,independent_replay_pairs=pairs,source_sha256=guard,physical_gamma_or_cutoff_selected=False),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(verification_sha256=sha256(path.read_bytes()).hexdigest(),pairs=pairs),sort_keys=True))
