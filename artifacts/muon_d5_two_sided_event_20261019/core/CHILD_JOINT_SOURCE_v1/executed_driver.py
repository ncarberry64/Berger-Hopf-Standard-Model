import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
import sys,json,numpy as np
ROOT=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');BASE=Path(__file__).parent;OUT=BASE/'CHILD_JOINT_SOURCE_v1'
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_child_joint_source_application import append_joint_child_source
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
OUT.mkdir(exist_ok=False)
_,hist,pins=inputs();history,receipt=recovered_export_history(ROOT,'outgoing',*hist['outgoing']);pins.update(receipt['input_sha256'])
paths=dict(child=BASE/'CHILD_SAME_DIRECTION_v1/application.npz',previous=BASE/'CHILD_SPATIAL_SOURCE_v1/application.npz',spatial=BASE/'SPATIAL_BUNDLE_v2/application.npz',joint=BASE/'JOINT_MAP_SOURCE_v1/application.npz')
owner=ROOT/'src/bhsm/interface/muon_d5_child_joint_source_application.py'
for p in (*paths.values(),owner):pins[str(p)]=pin(p)
data={}
for key,path in paths.items():
 with np.load(path,allow_pickle=False) as z:data[key]={k:z[k].copy(order='K') for k in z.files}
dump(OUT/'BEFORE.json',dict(input_sha256=pins,equation='final-joint source = completed normal + old spatial source + actual original callback applied only to exact new spatial source increment',held='cached value and birth/chart; prescribed inherited jets; both free normal-rate coefficients',physical_guard=2e-10))
arrays,report=append_joint_child_source(history,**data)
write_npz(OUT/'application.npz',arrays)
(OUT/'executed_source_owner.py').write_bytes(owner.read_bytes());(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
dump(OUT/'result.json',dict(input_sha256=pins,report=report,arrays=dict(sha256=pin(OUT/'application.npz'),bytes=(OUT/'application.npz').stat().st_size),executed_owner_sha256=pin(OUT/'executed_source_owner.py'),executed_driver_sha256=pin(OUT/'executed_driver.py')))
print(json.dumps(dict(saved=str(OUT),result_sha256=pin(OUT/'result.json'),report=report)),flush=True)
