import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
import sys,json,numpy as np
ROOT=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');BASE=Path(__file__).parent;CELL=BASE/'CHILD_CELL_v2';OUT=BASE/'CHILD_CORNER_v1';OUT.mkdir(exist_ok=False)
sys.path[:0]=[str(ROOT/'src')]
from bhsm.interface.muon_d5_child_corner_compatibility import build_child_corner_compatibility
from bhsm.interface.retained_response.finite_time_response import write_npz

def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
r=json.loads((CELL/'core_result.json').read_bytes());app={};pins={str(CELL/'core_result.json'):pin(CELL/'core_result.json')}
for filename,receipt in r['archives'].items():
 path=CELL/filename
 if pin(path)!=receipt['sha256']:raise ValueError('saved child field identity changed')
 pins[str(path)]=pin(path)
 with np.load(path,allow_pickle=False) as z:app.update({k:z[k].copy(order='K') for k in z.files})
owner=ROOT/'src/bhsm/interface/muon_d5_child_corner_compatibility.py';baseowner=ROOT/'src/bhsm/interface/muon_d5_child_characteristic_field.py'
for p in (owner,baseowner):pins[str(p)]=pin(p)
dump(OUT/'BEFORE.json',dict(input_sha256=pins,equation='both radial-face incoming evolution equations at original birtht0; eliminate ONLY firstfuture incoming trace slot3 with allotherdata retained',physical_data_or_h_selected=False,physical_guard=2e-10))
arrays,report=build_child_corner_compatibility(app)
write_npz(OUT/'application.npz',arrays)
(OUT/'executed_source_owner.py').write_bytes(owner.read_bytes());(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
dump(OUT/'result.json',dict(input_sha256=pins,report=report,arrays=dict(sha256=pin(OUT/'application.npz'),bytes=(OUT/'application.npz').stat().st_size),executed_owner_sha256=pin(OUT/'executed_source_owner.py'),executed_driver_sha256=pin(OUT/'executed_driver.py')))
print(json.dumps(dict(stage='CHILD_CORNER_ORIGINAL_GERM_SAVED',sha256=pin(OUT/'result.json'),array_sha256=pin(OUT/'application.npz'),max_pivot_condition=max(a['pivot_condition2'] for a in report['blocks'].values()),max_exact_kernel_rows=max(a['exact_kernel_original_row_max'] for a in report['blocks'].values()),max_exact_source_kernel_rows=max(a['exact_kernel_source_original_row_max'] for a in report['blocks'].values()))),flush=True)
