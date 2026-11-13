"""Record focused FD control and repeated actual U_B applications."""
from pathlib import Path
from hashlib import sha256
import json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'artifacts/muon_inherited_magnetic_pure_trace_20261012'


def main():
    env=os.environ.copy();env.update(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4');BASE.mkdir(exist_ok=True)
    def run(args,stem):
        logs=[BASE/(stem+s)for s in('.stdout.txt','.stderr.txt','.execution.json')]
        if any(p.exists()for p in logs):raise FileExistsError('preserve actual execution records')
        start=time.time();r=subprocess.run([sys.executable,*args],cwd=ROOT,env=env,capture_output=True)
        logs[0].write_bytes(r.stdout);logs[1].write_bytes(r.stderr)
        record=dict(argv=[sys.executable,*args],cwd=str(ROOT),environment={k:env[k]for k in('PYTHONPATH','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')},
            exit_code=r.returncode,elapsed_seconds=time.time()-start,stdout_sha256=sha256(r.stdout).hexdigest(),stderr_sha256=sha256(r.stderr).hexdigest())
        logs[2].write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        print(json.dumps(dict(stem=stem,**record)),flush=True)
        if r.returncode:raise SystemExit(r.returncode)
    run(['-m','pytest','--noconftest','-q','tests/test_muon_inherited_magnetic_pure_trace.py'],'focused_tests_run_1')
    for k in(1,2):run(['scripts/evaluate_muon_inherited_magnetic_pure_trace.py','--source-folder',
        'artifacts/muon_holomorphic_magnetic_inherited_cauchy_20261012/run_1','--output',(BASE/f'run_{k}').relative_to(ROOT).as_posix()],f'run_{k}')


if __name__=='__main__':main()
