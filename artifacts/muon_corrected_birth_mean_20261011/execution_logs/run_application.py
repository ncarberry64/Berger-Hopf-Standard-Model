"""Capture original, independent corrected moving-birth mean production."""
from pathlib import Path
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];LOG=Path(__file__).resolve().parent
name='run_'+sys.argv[1]
argv=[sys.executable,'scripts/evaluate_muon_corrected_birth_mean.py','--output',
      'artifacts/muon_corrected_birth_mean_20261011/'+name]
p=subprocess.run(argv,cwd=ROOT,env=dict(os.environ,PYTHONPATH='src'),capture_output=True)
for label,data in (('stdout',p.stdout),('stderr',p.stderr)):
    (LOG/(name+'.'+label+'.txt')).write_bytes(data.replace(b'\r\n',b'\n'))
r=dict(argv=argv,cwd=str(ROOT),environment_overrides={'PYTHONPATH':'src'},exit_code=p.returncode,
       stdout_path=name+'.stdout.txt',stderr_path=name+'.stderr.txt')
(LOG/(name+'.command.json')).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(p.stdout.decode('utf8')if p.returncode==0 else p.stderr.decode('utf8'),flush=True)
raise SystemExit(p.returncode)
