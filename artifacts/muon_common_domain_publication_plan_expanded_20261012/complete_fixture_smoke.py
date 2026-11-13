"""Copy missing compact regression fixtures only; never regenerate science."""
from pathlib import Path
from hashlib import sha256
import argparse,json,os,re,shutil,subprocess,time

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent


def missing_names(log):
    names=set()
    for name in re.findall(r"No such file or directory: '([^']+)'",log):
        name=name.replace('\\','/')
        while '//'in name:name=name.replace('//','/')
        if '/artifacts/'in name:names.add('artifacts/'+name.split('/artifacts/',1)[1])
    return names


def execute(scratch,last_log,max_rounds,prefix):
    scratch=Path(scratch).resolve()
    if not scratch.is_dir()or scratch==ROOT or ROOT in scratch.parents:
        raise ValueError('existing external isolated regression scratch required')
    if not re.fullmatch(r'[A-Za-z0-9_]+',prefix):raise ValueError('literal simple diagnostic prefix required')
    log=(ROOT/last_log).read_text();history=[]
    for number in range(3,3+max_rounds):
        cp=OUT/f'{prefix}copy_round_{number}.json'
        lp=OUT/f'{prefix}smoke_round_{number}.log'
        rp=OUT/f'{prefix}smoke_round_{number}.json'
        if any(p.exists()for p in(cp,lp,rp)):
            raise FileExistsError('preserve all earlier diagnostic files; use a fresh prefix')
        names=missing_names(log)
        if not names:raise ValueError('remaining failure is not a missing compact fixture')
        names|={(Path(name).parent/'result.json').as_posix()for name in list(names)
                 if(ROOT/Path(name).parent/'result.json').is_file()}
        rows=[]
        for name in sorted(names):
            source=(ROOT/name).resolve();target=(scratch/name).resolve()
            if ROOT not in source.parents or scratch not in target.parents or not source.is_file():
                raise ValueError('fixture path absent or escaped the intended tree: '+name)
            b=source.read_bytes()
            if len(b)>=10*1024**2:raise ValueError('report oversized fixture before copying: '+name)
            if target.is_file()and target.read_bytes()!=b:raise ValueError('preserve conflicting scratch bytes: '+name)
            fresh=not target.is_file()
            if fresh:target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
            rows.append(dict(path=name,bytes=len(b),sha256=sha256(b).hexdigest(),newly_copied=fresh))
        cp.write_text(json.dumps(dict(files=rows,destination=str(scratch)),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        tests=sorted(set(re.findall(r'(?:FAILED|ERROR) (tests/[^ :]+\.py)::',log)))
        if not tests:raise ValueError('no original failed test-file restriction found')
        argv=['C:/Python314/python.exe','-m','pytest','--noconftest','-q',*tests]
        env=os.environ.copy();env.update(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        start=time.time();p=subprocess.run(argv,cwd=scratch,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        lp.write_bytes(p.stdout);log=p.stdout.decode(errors='replace')
        receipt=dict(argv=argv,working_directory=str(scratch),environment={k:env[k]for k in('PYTHONPATH','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')},
            exit_code=p.returncode,elapsed_seconds=time.time()-start,stdout_log=lp.relative_to(ROOT).as_posix(),
            stdout_sha256=sha256(p.stdout).hexdigest(),subset_of_previously_failed_unchanged_tests=True,
            full_numerical_producer_regeneration_proved=False)
        rp.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        history.append(dict(round=number,copy_receipt=cp.relative_to(ROOT).as_posix(),test_receipt=rp.relative_to(ROOT).as_posix()))
        print(json.dumps(dict(round=number,exit_code=p.returncode,added_bytes=sum(r['bytes']for r in rows if r['newly_copied']),
            last_lines=log.splitlines()[-4:])),flush=True)
        if p.returncode==0:break
    else:raise ValueError('fixture attempts exhausted; preserve all diagnostics')
    hp=OUT/f'{prefix}completion_history.json'
    if hp.exists():raise FileExistsError('preserve previous diagnostic history')
    hp.write_text(json.dumps(dict(history=history),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scratch',type=Path,required=True);p.add_argument('--last-log',type=Path,required=True)
    p.add_argument('--max-rounds',type=int,default=6)
    p.add_argument('--prefix',required=True)
    a=p.parse_args();execute(a.scratch,a.last_log,a.max_rounds,a.prefix)
