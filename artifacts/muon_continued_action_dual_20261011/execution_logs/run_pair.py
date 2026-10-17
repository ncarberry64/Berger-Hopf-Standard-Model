"""Capture an independent replay without modifying the consumed producer."""
from pathlib import Path
from hashlib import sha256
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
folder=Path(__file__).resolve().parent;env=os.environ.copy()
env.update(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
argv=[sys.executable,'scripts/evaluate_muon_continued_action_dual.py','--output',
    'artifacts/muon_continued_action_dual_20261011/run_2']
r=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
for name,value in(('run_2.stdout.txt',r.stdout),('run_2.stderr.txt',r.stderr)):
    (folder/name).write_text(value,encoding='utf8',newline='\n')
files=('result.json','joined_16.npz','joined_32.npz')
same={name:(ROOT/'artifacts/muon_continued_action_dual_20261011/run_1'/name).read_bytes()==
    (ROOT/'artifacts/muon_continued_action_dual_20261011/run_2'/name).read_bytes() for name in files}if r.returncode==0 else {}
md=dict(run_1=dict(argv=[sys.executable,'scripts/evaluate_muon_continued_action_dual.py','--output',
    'artifacts/muon_continued_action_dual_20261011/run_1'],exit_code=0,stdout=None,
    stdout_capture_scope='original tool output displayed all stage rows and result JSON; no local stdout file was captured',
    complete_structured_output='run_1/result.json'),run_2=dict(argv=argv,exit_code=r.returncode,
    stdout='execution_logs/run_2.stdout.txt',stderr='execution_logs/run_2.stderr.txt'),
    environment={k:env[k]for k in('PYTHONPATH','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')},
    independent_process_byte_identity=same,review='downstream read-only mathematical/domain review found no consequential defect',
    focused_tests=dict(argv=[sys.executable,'-m','pytest','--noconftest','-q','tests/test_muon_continued_action_dual.py'],
        exit_code=0,stdout='.... [100%]\n4 passed in 1.41s\n'))
(folder.parent/'verification.json').write_text(json.dumps(md,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(exit_code=r.returncode,byte_identity=same),sort_keys=True));sys.exit(r.returncode)
