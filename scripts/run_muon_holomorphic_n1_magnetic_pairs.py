"""Record exact subprocess evidence for the four signed magnetic pair replays."""
from pathlib import Path
from hashlib import sha256
import argparse,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]


def run(base,source):
    base=ROOT/base
    env=os.environ.copy();env.update(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4')
    commands=[]
    # Outgoing operands feed the independent D3S consumer first.
    for side in ('outgoing','incoming'):
        for case in ('normal_basis','area_source'):
            for attempt in (1,2):
                name=f'{side}_{case}_run_{attempt}';out=base/name
                if out.exists()or any((base/(name+s)).exists()for s in('.stdout.txt','.stderr.txt','.execution.json')):
                    raise FileExistsError('preserve all earlier exact source pair evidence')
                argv=[sys.executable,'scripts/evaluate_muon_holomorphic_n1_magnetic_action.py','--source-folder',str(source).replace('\\','/'),
                    '--side',side,'--case',case,'--output',out.relative_to(ROOT).as_posix()]
                commands.append((name,argv))
    base.mkdir(exist_ok=True,parents=True)
    for name,argv in commands:
        print(json.dumps(dict(stage='signed_magnetic_pair_dispatch',folder=name,argv=argv)),flush=True)
        p=subprocess.run(argv,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout=base/(name+'.stdout.txt');stderr=base/(name+'.stderr.txt')
        stdout.write_bytes(p.stdout);stderr.write_bytes(p.stderr)
        rec=dict(argv=argv,cwd=str(ROOT),environment={k:env[k]for k in('PYTHONPATH','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')},
            exit_code=p.returncode,stdout_sha256=sha256(p.stdout).hexdigest(),stderr_sha256=sha256(p.stderr).hexdigest(),
            stdout_bytes=len(p.stdout),stderr_bytes=len(p.stderr),execution_subprocess_binary_capture=True)
        (base/(name+'.execution.json')).write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        print(p.stdout.decode('utf8',errors='replace'),end='',flush=True)
        if p.returncode:
            print(p.stderr.decode('utf8',errors='replace'),end='',flush=True);raise SystemExit(p.returncode)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True)
    p.add_argument('--source-folder',type=Path,required=True);a=p.parse_args();run(a.base,a.source_folder)
