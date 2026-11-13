import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
import sys,json,numpy as np
ROOT=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');BASE=Path(r'C:/Users/carbe/Downloads/BHSM_D5_TWO_SIDED_EVENT_20261019')
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from bhsm.interface.muon_d5_child_higgs_seam_source_application import consume_child_higgs_seam
from bhsm.interface.retained_response.finite_time_response import write_npz
OUT=BASE/'CHILD_HIGGS_SEAM_v1';OUT.mkdir(exist_ok=False)
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
paths=dict(endpoint=ROOT/'artifacts/muon_formed_event_domain_application_20261019/run_2/formed_event_domain_application.npz',affine=ROOT/'artifacts/muon_d5_event_matching_20261019/affine_core/application.npz',joint=BASE/'JOINT_MAP_SOURCE_v1/application.npz',parent_h=BASE/'PARENT_H_CONSUMER_v1/application.npz')
owner=ROOT/'src/bhsm/interface/muon_d5_child_higgs_seam_source_application.py';pins={str(p):pin(p) for p in [*paths.values(),owner]}
dump(OUT/'BEFORE.json',dict(input_sha256=pins,physical_event_D_maps=None,physical_guard=2e-10,equation='execute once-only intrinsic Higgs source and retain full ordered event-map factors; normalized numerical contractions are formal coefficients only'))
data={}
for key,path in paths.items():
 with np.load(path,allow_pickle=False) as z:data[key]={k:z[k].copy(order='K') for k in z.files}
arrays,report=consume_child_higgs_seam(**data)
write_npz(OUT/'application.npz',arrays)
(OUT/'executed_source_owner.py').write_bytes(owner.read_bytes())
# The executing stdin script is saved by its caller before this invocation.
dump(OUT/'result.json',dict(input_sha256=pins,report=report,arrays=dict(sha256=pin(OUT/'application.npz'),bytes=(OUT/'application.npz').stat().st_size),executed_owner_sha256=pin(OUT/'executed_source_owner.py')))
print(json.dumps(dict(saved=str(OUT),result_sha256=pin(OUT/'result.json'),report=report)),flush=True)
