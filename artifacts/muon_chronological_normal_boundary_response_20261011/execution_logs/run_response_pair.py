from pathlib import Path
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
base=ROOT/'artifacts/muon_chronological_normal_boundary_response_20261011'
env=os.environ.copy();env['PYTHONPATH']='src'
run=int(sys.argv[1])
for side in ('incoming','outgoing'):
 for steps in (1,2,4):
  name=f'{side}_{steps}steps_run_{run}'
  phase=f'artifacts/muon_parent_gauge_geometry_correction_20261010/attached_phase_{side}_{steps}steps_run_1'
  if steps>1:phase+='_stage_package'
  argv=[sys.executable,'-m','bhsm.interface.muon_birth_chronological_normal_boundary_response','--phase-directory',phase,'--output',str(base/name)]
  result=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True)
  log=base/'execution_logs';log.mkdir(parents=True,exist_ok=True)
  (log/(name+'.stdout.txt')).write_text(result.stdout,encoding='utf8',newline='\n')
  (log/(name+'.stderr.txt')).write_text(result.stderr,encoding='utf8',newline='\n')
  receipt=dict(argv=argv,environment={'PYTHONPATH':'src'},exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr)
  (log/(name+'.execution.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
  print(json.dumps(dict(name=name,exit_code=result.returncode)),flush=True)
  if result.returncode:raise SystemExit(result.returncode)
