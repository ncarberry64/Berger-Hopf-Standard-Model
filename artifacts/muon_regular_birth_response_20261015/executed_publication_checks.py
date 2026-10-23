"""Execute the repository's five publication audits and preserve full logs."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
import json
import os
import subprocess

repo=Path(r'C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001')
out=repo/'artifacts/muon_regular_birth_response_20261015/publication_checks'
out.mkdir(exist_ok=False)
env=os.environ.copy()
env['PYTHONPATH']=str(repo/'src')
checks=[
    ('status',['tools/audit_bhsm_status.py']),
    ('forbidden_claims',['tools/audit_forbidden_claims.py']),
    ('frozen_integrity',['tools/audit_frozen_prediction_integrity.py']),
    ('precision',['tools/verify_precision.py']),
    ('public_readiness',['tools/audit_public_readiness.py','--format','json']),
]


def run(check):
    name,args=check
    result=subprocess.run([r'C:\Python314\python.exe',*args],cwd=repo,env=env,
                          capture_output=True,timeout=600)
    log=result.stdout+result.stderr
    (out/f'{name}.log').write_bytes(log)
    return name,dict(arguments=args,exit_code=result.returncode,
        log_sha256=sha256(log).hexdigest(),log_bytes=len(log))


results={}
with ThreadPoolExecutor(max_workers=5) as pool:
    for future in as_completed([pool.submit(run,check) for check in checks]):
        name,result=future.result()
        results[name]=result
        print(json.dumps(dict(check=name,**result)),flush=True)
(out/'results.json').write_text(json.dumps(results,sort_keys=True,indent=2)+'\n',
                               encoding='utf-8',newline='\n')
