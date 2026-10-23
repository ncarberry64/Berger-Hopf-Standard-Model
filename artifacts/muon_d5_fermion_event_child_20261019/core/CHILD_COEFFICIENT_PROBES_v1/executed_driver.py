import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
import sys,json,ast,numpy as np
ROOT=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');BASE=Path(__file__).parent;OUT=BASE/'CHILD_COEFFICIENT_PROBES_v1';OUT.mkdir(exist_ok=False)
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_child_characteristic_field import original_child_cell_coefficients
from bhsm.interface.retained_response.finite_time_response import write_npz

def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
_,hist,pins=inputs();history,receipt=recovered_export_history(ROOT,'outgoing',*hist['outgoing']);pins.update(receipt['input_sha256'])
OLD=Path(r'C:/Users/carbe/Downloads/BHSM_D5_TWO_SIDED_EVENT_20261019');jp=OLD/'JOINT_MAP_SOURCE_v1/application.npz';joint=load(jp)
C=BASE/'CHILD_CELL_v2';record=json.loads((C/'core_result.json').read_bytes());meta=load(C/'metadata.npz');times=meta['times'];radii=meta['radii']
tp=times[-1]*np.array([.137,.419,.863]);rp=radii[0]+(radii[-1]-radii[0])*np.array([.083,.377,.911])
owner=ROOT/'src/bhsm/interface/muon_d5_child_characteristic_field.py'
for p in (jp,C/'core_result.json',C/'metadata.npz',owner):pins[str(p)]=pin(p)
# Explicit mathematical callback compatibility: only the solver changed.
def function_bytes(p,name):
 text=Path(p).read_text(encoding='utf-8');tree=ast.parse(text)
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
 return '\n'.join(text.splitlines()[node.lineno-1:node.end_lineno]).encode()
functions=('child_source_names','original_child_cell_coefficients')
proof={n:dict(old_sha256=sha256(function_bytes(BASE/'CHILD_CELL_v1/executed_source_owner.py',n)).hexdigest(),current_sha256=sha256(function_bytes(owner,n)).hexdigest()) for n in functions}
if any(v['old_sha256']!=v['current_sha256'] for v in proof.values()):raise ValueError('original callback changed')
dump(OUT/'BEFORE.json',dict(input_sha256=pins,original_callback_source_compatibility=proof,equation='original inherited child T,R,K and17source jets at same9 independentpoints; missing cache materialized once for actual v2event-consumed field check',no_field_or_ancestor_solve=True))
coeff,aux=original_child_cell_coefficients(history,tp,rp,joint,17.98966013686085)
archives={}
for label,c in coeff.items():
 for bi in range(int(meta[label+'_block_count'])):
  name=label+'_block'+str(bi);old=load(C/(name+'.npz'));idx=old[name+'_indices']
  arrays={name+'_indices':idx}
  for k,a in c.items():arrays[name+'_original_coefficient_'+k]=a[...,idx,:][...,idx]
  path=OUT/(name+'.npz');write_npz(path,arrays);archives[path.name]=dict(sha256=pin(path),bytes=path.stat().st_size)
write_npz(OUT/'metadata.npz',dict(times=tp,radii=rp,original_metrics=aux['metrics'],original_raw_source_columns=aux['raw_source_columns']));archives['metadata.npz']=dict(sha256=pin(OUT/'metadata.npz'),bytes=(OUT/'metadata.npz').stat().st_size)
(OUT/'executed_source_owner.py').write_bytes(owner.read_bytes());(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
dump(OUT/'result.json',dict(input_sha256=pins,archives=archives,source_names=aux['source_names'],original_callback_source_compatibility=proof,original_operator_and_source_callback=True,field_or_ancestor_precision_replayed=False,physical_admission=False,physical_guard=2e-10))
print(json.dumps(dict(stage='CHILD_ORIGINAL_PROBE_COEFFICIENTS_SAVED',sha256=pin(OUT/'result.json'),archives=len(archives))),flush=True)
