from pathlib import Path
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];LOG=Path(__file__).resolve().parent
name='run_'+sys.argv[1]
argv=[sys.executable,'scripts/evaluate_muon_wick_canonical_inverse.py','--output',
 'artifacts/muon_wick_canonical_inverse_20261011/'+name,'--refinements','16','32','64']
environment={'PYTHONPATH':'src','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
p=subprocess.run(argv,cwd=ROOT,env=dict(os.environ,**environment),capture_output=True)
for label,data in(('stdout',p.stdout),('stderr',p.stderr)):(LOG/(name+'.'+label+'.txt')).write_bytes(data.replace(b'\r\n',b'\n'))
(LOG/(name+'.command.json')).write_text(json.dumps(dict(argv=argv,cwd=str(ROOT),environment_overrides=environment,
 exit_code=p.returncode,stdout_path=name+'.stdout.txt',stderr_path=name+'.stderr.txt'),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(p.stdout.decode('utf8')if p.returncode==0 else p.stderr.decode('utf8'),flush=True)
raise SystemExit(p.returncode)
