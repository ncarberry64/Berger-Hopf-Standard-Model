"""Capture actual focused control and two executions without replacing outputs."""
from pathlib import Path
from hashlib import sha256
import json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/muon_holomorphic_n3_magnetic_return_20261012'


def main():
    env=os.environ.copy();env.update(PYTHONPATH='src;scripts;tests',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4')
    BASE.mkdir(exist_ok=True)
    def execute(args,stem):
        logs=[Path(str(stem)+s)for s in('.stdout.txt','.stderr.txt','.execution.json')]
        if any(p.exists()for p in logs):raise FileExistsError('preserve actual execution evidence')
        start=time.time();r=subprocess.run([sys.executable,*args],cwd=ROOT,env=env,capture_output=True)
        logs[0].write_bytes(r.stdout);logs[1].write_bytes(r.stderr)
        record=dict(argv=[sys.executable,*args],cwd=str(ROOT),environment={k:env[k]for k in('PYTHONPATH','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')},
            exit_code=r.returncode,elapsed_seconds=time.time()-start,
            stdout_sha256=sha256(r.stdout).hexdigest(),stderr_sha256=sha256(r.stderr).hexdigest())
        logs[2].write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        print(json.dumps(dict(stem=stem.relative_to(ROOT).as_posix(),**record)),flush=True)
        if r.returncode:raise SystemExit(r.returncode)
    execute(['-m','pytest','--noconftest','-q','tests/test_muon_holomorphic_n3_magnetic_return.py'],BASE/'focused_tests_run_1')
    for k in (1,2):
        folder=BASE/f'outgoing_normal_basis_run_{k}'
        execute(['scripts/evaluate_muon_holomorphic_n3_magnetic_return.py','--source-folder',
            'artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_normal_basis_run_1','--output',folder.relative_to(ROOT).as_posix()],folder)


if __name__=='__main__':main()
