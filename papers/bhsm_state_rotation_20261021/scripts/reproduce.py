"""Offline reproducibility entry point. Never edits the inherited paper."""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
VENDOR=ROOT.parent/'bhsm_angular_lensing_20261021/code/vendor_original'
manifest=json.loads((VENDOR/'SOURCE_MANIFEST.json').read_text())
for f in manifest['files']:
    assert hashlib.sha256((VENDOR/f['path']).read_bytes()).hexdigest()==f['sha256']
stages=['review/check_hopf_nodal_bound.py','review/check_hopf_nodal_rigidity.py',
        'review/check_fluid_current_reduction.py',
        'code/rotation_response.py','review/independent_rotation_check.py',
        'review/check_response_results.py','scripts/make_figures.py']
env=os.environ.copy();env['OPENBLAS_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1'
logs=ROOT/'results/replay';logs.mkdir(exist_ok=True)
receipts=[]
for stage in stages:
    print('Running '+stage,flush=True)
    result=subprocess.run([sys.executable,str(ROOT/stage)],cwd=ROOT,env=env,
                          capture_output=True,text=True)
    (logs/(Path(stage).stem+'.txt')).write_text(result.stdout+result.stderr,encoding='utf8')
    receipts.append({'stage':stage,'returncode':result.returncode})
    if result.returncode:
        print(result.stdout+result.stderr);raise SystemExit(result.returncode)
import numpy,scipy,matplotlib,sympy
receipt={'status':'ALL_SEVEN_STAGES_PASSED','python':platform.python_version(),
         'numpy':numpy.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__,
         'sympy':sympy.__version__,'source_commit':manifest['source_commit'],
         'vendor_hashes_verified':len(manifest['files']),'observations_used':False,'stages':receipts}
(ROOT/'results/replay_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print(json.dumps(receipt,indent=2))
