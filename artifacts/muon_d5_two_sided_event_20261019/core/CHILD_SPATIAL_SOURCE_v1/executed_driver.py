import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
import sys,json
import numpy as np
ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');BASE=Path(__file__).parent;OUT=BASE/'CHILD_SPATIAL_SOURCE_v1'
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_child_spatial_source_application import evaluate_child_spatial_source
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
OUT.mkdir(exist_ok=False)
_,hist,pins=inputs();history,receipt=recovered_export_history(ROOT,'outgoing',*hist['outgoing']);pins.update(receipt['input_sha256'])
child_folder=BASE/'CHILD_SAME_DIRECTION_v1';child_record=json.loads((child_folder/'result.json').read_bytes())
if pin(child_folder/'application.npz')!=child_record['arrays']['sha256']:raise ValueError('completed corrected child source changed')
with np.load(child_folder/'application.npz',allow_pickle=False) as z:child={k:z[k].copy(order='K') for k in z.files}
bundle_folder=BASE/'SPATIAL_BUNDLE_v2';bundle_record=json.loads((bundle_folder/'result.json').read_bytes())
if pin(bundle_folder/'application.npz')!=bundle_record['arrays_sha256']:raise ValueError('executed spatial constraint source changed')
with np.load(bundle_folder/'application.npz',allow_pickle=False) as z:bundle={k:z[k].copy(order='K') for k in z.files}
owner=ROOT/'src/bhsm/interface/muon_d5_child_spatial_source_application.py'
for p in (child_folder/'result.json',child_folder/'application.npz',bundle_folder/'result.json',bundle_folder/'application.npz',owner):pins[str(p)]=pin(p)
dump(OUT/'BEFORE.json',dict(input_sha256=pins,parent_head='67c113ea',candidate_indices=[2,3],
 equation='child source candidate_j=corrected prescribed+normal source + equation-derived own-wall-gauge source_j +sixfree rotation coefficients',
 child_free_normal_rate=None,normal_chart_recomputed=False))
arrays,report=evaluate_child_spatial_source(history,child,bundle['child_raw_field_source_corrections'],bundle['child_raw_field_free_rotation_coefficients'])
write_npz(OUT/'application.npz',arrays)
(OUT/'executed_source_owner.py').write_bytes(owner.read_bytes());(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
dump(OUT/'result.json',dict(input_sha256=pins,report=report,arrays=dict(sha256=pin(OUT/'application.npz'),bytes=(OUT/'application.npz').stat().st_size),
 executed_owner_sha256=pin(OUT/'executed_source_owner.py'),executed_driver_sha256=pin(OUT/'executed_driver.py'),
 NEXT_OPERAND='consume both value-compatible orientation source families and allfree rotation/normal-rate coordinates in joint event and outer/formation equations; no physical map selected'))
print(json.dumps(dict(stage='CHILD_SPATIAL_SOURCE_SAVED',sha256=pin(OUT/'result.json'),report=report)),flush=True)
