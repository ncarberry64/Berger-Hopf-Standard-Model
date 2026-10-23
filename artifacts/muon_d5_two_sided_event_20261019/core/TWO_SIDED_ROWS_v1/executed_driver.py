from pathlib import Path
from hashlib import sha256
import json,sys,os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
R=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');W=Path(__file__).resolve().parent;O=W/'TWO_SIDED_ROWS_v1'
sys.path[:0]=[str(R/'src'),str(R)]
from bhsm.interface.muon_d5_two_sided_constraint_rows import assemble_two_sided_rows
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(p.read_bytes()).hexdigest()
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
assert not O.exists();O.mkdir();pins={}
sources=[]
for name in ('CONSTRAINT_TWOJET_APPEND_v1','JOINT_MAP_SOURCE_v1','HIGGS_TEMPORAL_v1'):
 p=W/name/'application.npz';sources.append(load(p));pins[str(p)]=pin(p)
owner=R/'src/bhsm/interface/muon_d5_two_sided_constraint_rows.py';pins[owner.relative_to(R).as_posix()]=pin(owner)
(O/'BEFORE.json').write_text(json.dumps(dict(input_sha256=pins),indent=2)+'\n')
(O/'executed_source_owner.py').write_bytes(owner.read_bytes());(O/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
arrays,report=assemble_two_sided_rows(*sources);write_npz(O/'application.npz',arrays)
(O/'result.json').write_bytes((json.dumps(dict(input_sha256=pins,arrays=dict(sha256=pin(O/'application.npz')),
 report=report,NEXT_OPERAND='consume the complete child/seam and physical outer/normal/formation action, including pending Higgs/time multiplier Hessians, without selecting numerical kernel coordinates as a physical state'),sort_keys=True,indent=2)+'\n').encode())
print('TWO_SIDED_ROWS_SAVED',pin(O/'result.json'),report,flush=True)
