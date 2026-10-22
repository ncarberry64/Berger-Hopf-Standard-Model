"""Finite product release checks, with the independent protocol preserved."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'validation';out.mkdir(exist_ok=True)
stages=[['-m','pytest','-q','tests'],['tests/calibrate_product.py'],['tests/check_finite_harmonic_degeneracy.py']]
receipts=[]
for i,args in enumerate(stages):
    print('Stage '+str(i+1)+': '+' '.join(args),flush=True)
    run=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True)
    (out/f'stage_{i+1}.txt').write_text(run.stdout+run.stderr,encoding='utf8')
    receipts.append({'command':args,'returncode':run.returncode})
    if run.returncode:
        print(run.stdout+run.stderr);raise SystemExit(run.returncode)
hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'bhtracker').rglob('*.py')) if '__pycache__' not in p.parts}
(out/'product_replay_receipt.json').write_text(json.dumps({'status':'ALL_PRODUCT_STAGES_PASSED','stages':receipts,'code_sha256':hashes},indent=2)+'\n')
print('ALL_PRODUCT_STAGES_PASSED')
