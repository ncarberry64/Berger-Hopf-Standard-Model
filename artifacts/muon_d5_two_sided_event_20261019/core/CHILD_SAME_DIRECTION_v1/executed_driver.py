import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
import sys,json
import numpy as np
ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');OUT=Path(__file__).parent/'CHILD_SAME_DIRECTION_v1'
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_child_same_direction_application import evaluate_child_same_direction
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
OUT.mkdir(exist_ok=False)
_,histories,pins=inputs();history,receipt=recovered_export_history(ROOT,'outgoing',*histories['outgoing']);pins.update(receipt['input_sha256'])
folder=ROOT/'artifacts/muon_d5_valid_domain_application_20261019/domain_core'
record=json.loads((folder/'result.json').read_bytes())
if pin(folder/'arrays.npz')!=record['arrays']['sha256']:raise ValueError('saved child domain/source bytes changed')
with np.load(folder/'arrays.npz',allow_pickle=False) as z:cached={k:z[k].copy(order='K') for k in z.files}
formation=ROOT/'artifacts/muon_d5_event_matching_20261019/formation_core/application.npz'
with np.load(formation,allow_pickle=False) as z:psi=float(z['provisional_normal_displacement_source_correction'][1].real)
if psi!=17.98966013686085:raise ValueError('executed child normal pivot identity changed')
for p in (folder/'result.json',folder/'arrays.npz',formation,ROOT/'src/bhsm/interface/muon_d5_child_same_direction_application.py'):
 pins[p.relative_to(ROOT).as_posix()]=pin(p)
pins[str(Path(__file__))]=pin(__file__)
dump(OUT/'BEFORE.json',dict(input_sha256=pins,parent_head='67c113ea',child_normal_psi_E1=psi,
 child_normal_rate=None,value_and_prescribed_Xi_cache_reused=True,
 equation='child Xi_corrected=Xi_prescribed+Bnormal*psi_E1+nu_child*Bnormal_rate; nu_child remains free'))
arrays,report=evaluate_child_same_direction(history,cached,psi)
write_npz(OUT/'application.npz',arrays)
owner=ROOT/'src/bhsm/interface/muon_d5_child_same_direction_application.py'
(OUT/'executed_source_owner.py').write_bytes(owner.read_bytes())
(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
dump(OUT/'result.json',dict(input_sha256=pins,report=report,arrays=dict(sha256=pin(OUT/'application.npz'),bytes=(OUT/'application.npz').stat().st_size),
 executed_owner_sha256=pin(OUT/'executed_source_owner.py'),executed_driver_sha256=pin(OUT/'executed_driver.py'),
 NEXT_OPERAND='consume both corrected history sources with original event/base/bundle and formation equations; retain free normal rate, inherited sources, outer data and physical mode'))
print(json.dumps(dict(stage='CHILD_SAME_DIRECTION_SAVED',sha256=pin(OUT/'result.json'),report=report)),flush=True)
