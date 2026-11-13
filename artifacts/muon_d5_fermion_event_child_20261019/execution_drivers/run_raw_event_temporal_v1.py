import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json,hashlib
import numpy as np
ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');WORK=Path(__file__).parent
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from bhsm.interface.muon_d5_raw_event_temporal_ports import temporal_map_source_ports,material_velocity_source_from_spin,normal_rate_clock_ports
from bhsm.interface.retained_response.finite_time_response import write_npz
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
pin=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
oldp=ROOT/'artifacts/muon_d5_two_sided_event_20261019/core/HIGGS_TEMPORAL_v1/application.npz'
jp=ROOT/'artifacts/muon_d5_two_sided_event_20261019/core/JOINT_MAP_SOURCE_v1/application.npz'
rp=WORK/'RAW_WALL_EVENT_v1/application.npz';a,j,r=map(load,(oldp,jp,rp))
OUT=WORK/'RAW_EVENT_TEMPORAL_v1';OUT.mkdir(exist_ok=False)
k=complex(r['wall_material_clock_differential']);p=r['wall_parent_material_velocity'];c=r['wall_child_material_velocity']
px=material_velocity_source_from_spin(r['parent_material_spin384'],r['parent_material_spin_normal_rate384'],p)
cx=material_velocity_source_from_spin(r['child_material_spin384'],r['child_material_spin_normal_rate384'],c)
knu=normal_rate_clock_ports(k,p,c,px,cx)
out=dict(normal_rate_clock_differential_ports=knu,parent_normal_rate_velocity=np.array(px),child_normal_rate_velocity=np.array(cx))
reports=[]
for i,idx in enumerate(j['initial_candidate_index']):
 pref='candidate'+str(int(idx))+'_';U=j['Higgs_middle'][i]
 ports=temporal_map_source_ports(a['parent_temporal_connection'],a['child_temporal_connection'],k,U)
 out.update({pref+n:v for n,v in ports.items()})
 out[pref+'normal_rate_temporal_first']=knu[:,None,None]*(U@a['parent_temporal_connection'])[None]
 out[pref+'supplied_Xi_temporal_first_particular']=j['temporal_bundle_time_first_particular'][i]
 reports.append(dict(candidate_index=int(idx),free7_original_row_max=float(np.max(abs(ports['original_rows']))),
    free7_temporal_first_max=float(np.max(abs(ports['temporal_first']))),normal_rate_temporal_first_max=float(np.max(abs(out[pref+'normal_rate_temporal_first'])))))
write_npz(OUT/'application.npz',out)
owner=ROOT/'src/bhsm/interface/muon_d5_raw_event_temporal_ports.py'
record=dict(classification='EXECUTED_FINAL_MAP_LOCAL_E1_HIGGS_TEMPORAL_SOURCE_PORTS',
 input_sha256={str(p):pin(p) for p in (oldp,jp,rp,owner,Path(__file__))},arrays=dict(sha256=pin(OUT/'application.npz')),
 candidates=reports,original_equation='U_t=-A_c0 U+kappa U A_p0; deltaU_t=-A_c0 deltaU+kappa deltaU A_p0+delta_kappa U A_p0 for these ports',
 zero_provenance='free7 compensating rawfield supports168:180,260:264; normal rate supports99. Original d5_trial_stage_coefficients adds mechanical changes only to spatial components2:, so all direct deltaA0 ports are identically0',
 normal_rate_clock_ports_real_imag=[[float(v.real),float(v.imag)] for v in knu],
 domain='local one-sided E1 jet only; child future incoming history is not the event extension',
 full_Spin_reset_temporal_derivative=None,physical_map_selected=False,complete_physical_derivative=False,
 physical_admission=False,physical_guard=2e-10,NEXT_OPERAND='retain these localE1 gauge ports in actual raw event Jacobi contacts; derive remaining Spin/base/normal and boundary-history data through their original equations')
(OUT/'result.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf-8')
(OUT/'executed_source_owner.py').write_bytes(owner.read_bytes());(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(record,sort_keys=True,indent=2))
