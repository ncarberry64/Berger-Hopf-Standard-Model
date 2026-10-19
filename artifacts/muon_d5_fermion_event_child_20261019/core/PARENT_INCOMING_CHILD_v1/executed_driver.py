"""Consume the actual parent incoming-characteristic equations in child fields."""
from pathlib import Path
from hashlib import sha256
import json,sys,os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
R=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');W=Path(__file__).resolve().parent;O=W/'PARENT_INCOMING_CHILD_v1'
sys.path[:0]=[str(R/'src'),str(R)]
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_bytes((json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
assert not O.exists();O.mkdir();path=W/'PARENT_CHARACTERISTIC_v1/application.npz';c=load(path);pins={str(path):pin(path)}
cp,cf=c['h_pivot_columns'],c['remaining_h_columns'];Ha,Hd,Hf=(c[k] for k in ('h_pivot_from_particular','h_pivot_from_incoming_datum','h_pivot_from_free_h'))
Hax,Hdx,Hfx=(c[k+'_source'] for k in ('h_pivot_from_particular','h_pivot_from_incoming_datum','h_pivot_from_free_h'))
Ah,Aa,Ahx,Aax=(c[k] for k in ('incoming_h','incoming_particular','incoming_h_source','incoming_particular_source'))
equations=dict(incoming_particular_value_rows=Ah[:,cp]@Ha+Aa,
 incoming_datum_value_rows=Ah[:,cp]@Hd-np.eye(40),incoming_free_value_rows=Ah[:,cp]@Hf+Ah[:,cf],
 incoming_particular_source_rows=Ahx[:,cp]@Ha+Ah[:,cp]@Hax+Aax,
 incoming_datum_source_rows=Ahx[:,cp]@Hd+Ah[:,cp]@Hdx,
 incoming_free_source_rows=Ahx[:,cp]@Hf+Ah[:,cp]@Hfx+Ahx[:,cf])
dump(O/'BEFORE.json',dict(input_sha256=pins,muon_family=1,physical_incoming_datum=None,
 original_equation='incoming_h h+incoming_particular a_R=d_in40',parent_data_dimension=3660,
 net_dimension_after='3620 free_h +40 free_d_in',physical_admission=False))
(O/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
out=dict(h_pivot_columns=cp,remaining_h_columns=cf,**equations);archives={};reports=[]
for candidate in (2,3):
 for side in ('plus','minus'):
  name='candidate'+str(candidate)+'_'+side+'_homogeneous.npz';fp=W/'EVENT_CHILD_CORNER_v1'/name
  rp=W/'EVENT_CHILD_CORNER_v1/ORIGINAL_CHECKS_v2'/name
  a,e=load(fp),load(rp);pins[str(fp)]=pin(fp);pins[str(rp)]=pin(rp)
  idx=a['original_parent_column_indices'];position={int(k):j for j,k in enumerate(idx)}
  def pivot_coeff(F):
   # The full original h count and exact sparse index binding are retained.
   # Missing entries are proved zero COEFFICIENTS, never physical data.
   P=np.zeros((*F.shape[:-1],40),complex)
   for j,k in enumerate(cp):
    if int(k) in position:P[...,j]=F[...,position[int(k)]]
   return P
  arrays=dict(original_h_active_columns=idx,original_h_column_count=np.array(3660),h_pivot_columns=cp,
   retained_original_child_h_file=np.frombuffer(str(fp).encode(),dtype=np.uint8))
  for field in ('value','time','radial'):
   F=pivot_coeff(a['child_'+field]);X=pivot_coeff(a['child_'+('source' if field=='value' else field+'_source')])
   arrays[field+'_h_pivot_coefficient']=F
   arrays[field+'_incoming_datum_coefficient']=F@Hd
   arrays[field+'_a_R_additive_coefficient']=F@Ha
   arrays[field+'_incoming_datum_source_coefficient']=X@Hd+F@Hdx
   arrays[field+'_a_R_additive_source_coefficient']=X@Ha+F@Hax
  V=pivot_coeff(e['original_value_rows']);X=pivot_coeff(e['original_supplied_source_rows'])
  arrays.update(original_child_incoming_value_rows=V@Hd,
   original_child_incoming_source_rows=X@Hd+V@Hdx,
   original_child_a_R_additive_value_rows=V@Ha,
   original_child_a_R_additive_source_rows=X@Ha+V@Hax)
  for j in range(7):arrays['free_map'+str(j)+'_incoming_source']=pivot_coeff(a['child_free_map'+str(j)+'_source'])@Hd
  arrays['child_normal_rate_incoming_source']=pivot_coeff(a['child_normal_rate_source'])@Hd
  dest=O/name;write_npz(dest,arrays);archives[name]=dict(sha256=pin(dest),bytes=dest.stat().st_size)
  r=dict(candidate=candidate,side=side,incoming_coordinates=40,remaining_h=3620,
   nonnull_child_incoming_response_max=float(np.max(abs(arrays['value_incoming_datum_coefficient']))),
   nonnull_child_incoming_source_max=float(np.max(abs(arrays['value_incoming_datum_source_coefficient']))),
   original_child_incoming_value_max=float(np.max(abs(arrays['original_child_incoming_value_rows']))),
   original_child_incoming_source_max=float(np.max(abs(arrays['original_child_incoming_source_rows']))),
   source_rule='F_hXi H_d+F_h H_dXi, plus F_d delta_d_in; independent state/map/time/source ports remain',
   physical_data_selected=False,physical_admission=False)
  reports.append(r);print(json.dumps(r),flush=True)
write_npz(O/'equations.npz',out);archives['equations.npz']=dict(sha256=pin(O/'equations.npz'),bytes=(O/'equations.npz').stat().st_size)
dump(O/'result.json',dict(input_sha256=pins,archives=archives,reports=reports,
 classification='EXECUTED_PARENT_INCOMING_CHARACTERISTIC_PIVOTS_IN_COUPLED_CHILD_FIELD',
 equation='A_h h+A_a a_R=d_in40',equation_value_max=max(float(np.max(abs(v))) for k,v in equations.items() if 'value' in k),
 equation_source_max=max(float(np.max(abs(v))) for k,v in equations.items() if 'source' in k),
 value_field_rule='Phi_child=F_hfree h_free+F_d d_in+(F_a_R+DeltaF_a_R) a_R+F_LR a_LR+F_RL a_RL+F_child_free z_free',
 free_field_rule='F_hfree=F_h_original[...,remaining_h]+F_h_pivot H_free; no dense h columns dropped',
 all_coefficient_sources_retained=True,physical_d_in=None,physical_h_selected=False,
 parent_free_coordinates=3660,parent_free_scope='3620 h +40 independent incoming data; no reduction in total physical input dimension',
 bosonic_kernel=538,fullcap_incidence=None,complete_formation_Hessian=None,
 original_parent_bulk_source_nonpasses_reused=True,original_child_bulk_source_nonpasses=True,
 local_native_accounting_changed=False,physical_guard=2e-10,physical_admission=False,
 NEXT_OPERAND='evaluate physical incoming/Cauchy data from the adopted prepared interacting state, then apply the retained joint event/corner/formation equations and check their actual field/error combinations'))
print('PARENT_INCOMING_CHILD_SAVED',pin(O/'result.json'),flush=True)
