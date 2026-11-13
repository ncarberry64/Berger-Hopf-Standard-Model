"""Record the exact independent continued-domain heat application command."""
from pathlib import Path
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
number=int(sys.argv[1]);base=Path(__file__).resolve().parent
argv=['C:/Python314/python.exe','scripts/evaluate_muon_continued_current_boundary_heat.py',
      '--output',f'artifacts/muon_continued_current_boundary_heat_20261011/run_{number}',
      '--refinements','16','32','--cutoff-probe','1.0329133712274834e-11']
environment=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
p=subprocess.run(argv,cwd=ROOT,env={**os.environ,**environment},capture_output=True,text=True)
for label,value in (('stdout',p.stdout),('stderr',p.stderr)):
    (base/f'run_{number}.{label}.txt').write_text(value,encoding='utf8',newline='\n')
(base/f'run_{number}.command.json').write_text(json.dumps(dict(argv=argv,cwd=str(ROOT),
    environment=environment,exit_code=p.returncode),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(p.stdout);print(p.stderr,file=sys.stderr);sys.exit(p.returncode)
