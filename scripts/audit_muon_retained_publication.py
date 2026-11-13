"""Save the required publication audit outputs without rewriting global ledgers."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
CHECKS={
    'status':['tools/audit_bhsm_status.py'],
    'forbidden_claims':['tools/audit_forbidden_claims.py'],
    'frozen_integrity':['tools/audit_frozen_prediction_integrity.py'],
    'precision':['tools/verify_precision.py'],
    'public_readiness':['tools/audit_public_readiness.py','--format','json'],
    'covariant_interface':['scripts/audit_covariant_bubble_interface_mechanics.py'],
    'museum_check':['tools/materialize_museum_science.py','--check'],
}

def main(output):
    output.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'src')
    def run(item):
        name,args=item
        try:
            process=subprocess.run([sys.executable,'-B',*args],cwd=ROOT,env=env,
                                   capture_output=True,timeout=600)
            log=process.stdout+process.stderr;code=process.returncode
        except subprocess.TimeoutExpired as error:
            log=(error.stdout or b'')+(error.stderr or b'')+b'\nAUDIT TIMEOUT\n';code=124
        (output/(name+'.log')).write_bytes(log)
        result=dict(arguments=args,exit_code=code,log_sha256=hashlib.sha256(log).hexdigest())
        print(json.dumps(dict(check=name,**result)),flush=True)
        return name,result
    with ThreadPoolExecutor(max_workers=5) as pool:
        results=dict(pool.map(run,CHECKS.items()))
    (output/'results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    return int(any(r['exit_code'] for r in results.values()))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    raise SystemExit(main(p.parse_args().output))
