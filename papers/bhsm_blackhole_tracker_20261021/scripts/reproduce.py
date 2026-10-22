"""Offline scientific replay; does not edit the preserved starting papers."""
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
for entry in manifest['files']:
    assert hashlib.sha256((VENDOR/entry['path']).read_bytes()).hexdigest()==entry['sha256']
stages=['review/check_compact_multipole_specialfunction.py',
        'review/check_blackhole_point_lens_invariant.py',
        'review/check_perturbed_mass_estimator.py',
        'review/check_projection_identifiability.py',
        'review/check_radial_response_provider.py',
        'code/tracker_response.py',
        'review/check_tracker_response.py',
        'scripts/numerical_table.py','scripts/make_figures.py']
logs=ROOT/'results/replay';logs.mkdir(exist_ok=True)
env=os.environ.copy();env['OPENBLAS_NUM_THREADS']='1';env['OMP_NUM_THREADS']='1'
receipts=[]
for stage in stages:
    print('Running '+stage,flush=True)
    done=subprocess.run([sys.executable,str(ROOT/stage)],cwd=ROOT,env=env,capture_output=True,text=True)
    (logs/(Path(stage).stem+'.txt')).write_text(done.stdout+done.stderr,encoding='utf8')
    receipts.append({'stage':stage,'returncode':done.returncode})
    if done.returncode:
        print(done.stdout+done.stderr);raise SystemExit(done.returncode)
import numpy,scipy,sympy,matplotlib,mpmath
j={'status':'ALL_NINE_STAGES_PASSED','python':platform.python_version(),
   'numpy':numpy.__version__,'scipy':scipy.__version__,'sympy':sympy.__version__,
   'matplotlib':matplotlib.__version__,'mpmath':mpmath.__version__,
   'pinned_provider_files_verified':len(manifest['files']),
   'provider_source_commit':manifest['source_commit'],'observations_used':False,'stages':receipts}
(ROOT/'results/replay_receipt.json').write_text(json.dumps(j,indent=2)+'\n',encoding='utf8')
print(json.dumps(j,indent=2))
