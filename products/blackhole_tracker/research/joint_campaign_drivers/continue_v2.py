import sys,json,time
from pathlib import Path
sys.path.insert(0,'product')
from bhtracker.joint_mass_v2 import fit_joint
p=Path(__file__).resolve().parent;name=sys.argv[1];f=json.loads((p/name).read_text());states=[row['internal_state'] for row in f['all_starts'] if 'internal_state' in row]
r=fit_joint(f['dataset_input'],initial_states=states,max_nfev=1800,**f['model_options']);r['continuation_of']=name
(p/(Path(name).stem+'_CONTINUED.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'numerical_convergence':r.get('numerical_convergence'),'parameters':r.get('parameters')}))
