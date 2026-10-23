"""Consume the raw AE2 wall trace in the actual corrected child field."""
from pathlib import Path
from hashlib import sha256
import json,sys,os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
R=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
W=Path(__file__).resolve().parent;O=W/'EVENT_CHILD_v1'
sys.path[:0]=[str(R/'src'),str(R)]
from bhsm.interface.muon_d5_child_characteristic_field import apply_child_cell_field
from bhsm.interface.muon_d5_event_child_cauchy_coupling import event_coordinate_partial,event_constraint_rank
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_bytes((json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
assert not O.exists();O.mkdir()
raw=load(W/'RAW_WALL_EVENT_v1/application.npz')
core=json.loads((W/'CHILD_CELL_v2/core_result.json').read_bytes());app={};pins={}
for name,meta in core['archives'].items():
 p=W/'CHILD_CELL_v2'/name;assert pin(p)==meta['sha256'];app.update(load(p));pins[str(p)]=pin(p)
for p in (W/'RAW_WALL_EVENT_v1/application.npz',W/'RAW_WALL_EVENT_v1/result.json',W/'CHILD_CELL_v2/core_result.json',
 R/'src/bhsm/interface/muon_d5_child_characteristic_field.py',R/'src/bhsm/interface/muon_d5_event_child_cauchy_coupling.py'):
 pins[str(p)]=pin(p)
old=R/'artifacts/muon_d5_two_sided_event_20261019/core/PARENT_H_CONSUMER_v1/application.npz';parent_h=load(old);pins[str(old)]=pin(old)
dump(O/'BEFORE.json',dict(input_sha256=pins,parent_h_coordinates=3660,unbound_child_data_per_collar=2976,
 event_scope='proved96 raw wall-carrier equations only; no wholecap incidence or chosen initial state',physical_admission=False))
(O/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
(O/'executed_source_owner.py').write_bytes((R/'src/bhsm/interface/muon_d5_event_child_cauchy_coupling.py').read_bytes())
C=raw['colorless_lift384x96'];S=raw['child_material_spin384'];Sx=raw['child_material_spin_Xi384'];Sn=raw['child_material_spin_normal_rate384']
tmax=float(app['times'][-1]);rin,rout=float(app['radii'][0]),float(app['radii'][-1])
tp=tmax*np.array([.137,.419,.863]);rp=rin+(rout-rin)*np.array([.083,.377,.911])
out=dict(independent_times=tp,independent_radii=rp,child_times=app['times'],child_radii=app['radii'],colorless_lift=C)
reports=[];archives={}
for ci,candidate in enumerate((2,3)):
 prefix='candidate'+str(candidate)+'_';K=raw[prefix+'middle96'];Kx=raw[prefix+'middle_free7_first96']
 L=raw[prefix+'child_raw_left96x384'];lift=raw[prefix+'child_raw_lift384x96'];liftx=raw[prefix+'child_raw_lift_Xi384x96']
 for label in ('plus_seed','minus_seed','minus_LR','minus_RL','plus_homogeneous','minus_homogeneous'):
  tag=prefix+label+'_';side=label.split('_')[0];slot=8*ci
  target=raw[tag+'required_child_coordinates96'];targetx=raw[tag+'required_child_coordinates_Xi96']
  full=lift@target;fullx=liftx@target+lift@targetx
  active=np.flatnonzero(np.any((full!=0)|(fullx!=0),axis=0))
  data,datas=event_coordinate_partial(full[:,active],fullx[:,active])
  field=apply_child_cell_field(app,side,data,datas,source_slot=slot,times=tp,radii=rp)
  corner=apply_child_cell_field(app,side,data,datas,source_slot=slot,times=[0.],radii=[rout])
  event=L@corner['value'][0,0]-target[:,active]
  leftx=-L@Sx@np.linalg.inv(S)
  eventx=leftx@corner['value'][0,0]+L@corner['source'][0,0]-targetx[:,active]
  arrays=dict(original_parent_column_indices=active,original_parent_column_count=np.array(full.shape[1]),
   child_birth_wall_data=full[:,active],child_birth_wall_data_Xi=fullx[:,active],
   original_event_value_rows=event,original_event_supplied_source_rows=eventx,
   **{'child_'+k:v for k,v in field.items()})
  # Every uncomputed independent child datum stays in the original response.
  # These are coefficient derivatives, never zero selections of physical data.
  qproj=np.linalg.solve(K,target)
  free_raw=np.einsum('ij,xjk,kl->xil',lift,Kx,qproj,optimize=True)
  for j in range(7):
   _,dx=event_coordinate_partial(full[:,active],free_raw[j][:,active])
   f=apply_child_cell_field(app,side,data,dx,source_slot=slot+1+j,times=tp,radii=rp)
   arrays['child_free_map'+str(j)+'_source']=f['source']
   arrays['child_free_map'+str(j)+'_time_source']=f['time_source'];arrays['child_free_map'+str(j)+'_radial_source']=f['radial_source']
  nr=Sn@C@target[:,active];_,dx=event_coordinate_partial(full[:,active],nr)
  fn=apply_child_cell_field(app,side,data,dx,source_slot=16,times=tp,radii=rp)
  for k in ('source','time_source','radial_source'):arrays['child_normal_rate_'+k]=fn[k]
  for name in ('parent_time_contact96','parent_radial_fixed_frame_contact96','parent_normal_rate_frame_contact96'):
   # Complete TOTAL base/source contacts remain in these original full-column
   # arrays; a missing radial-frame/parent-nu field response is not zero.
   arrays[name]=raw[tag+name]
  if 'homogeneous' in label:
   rank=event_constraint_rank(parent_h[side+'_h_value'],L,K,C)
   arrays['event_parent_h_block']=rank.pop('parent_h_block');arrays['event_parent_h_singular_values']=rank.pop('parent_h_singular_values')
  else:rank=None
  path=O/(prefix+label+'.npz');write_npz(path,arrays);archives[path.name]=dict(sha256=pin(path),bytes=path.stat().st_size)
  row=dict(candidate=candidate,label=label,source_slot=slot,original_parent_columns=full.shape[1],active_event_columns=len(active),
   event_value_max=float(np.max(abs(event))),event_supplied_source_max=float(np.max(abs(eventx))),
   child_field_value_max=float(np.max(abs(field['value']))),child_field_source_max=float(np.max(abs(field['source']))),
   event_h_rank=rank,physical_state_selected=False,physical_admission=False)
  reports.append(row);print(json.dumps(row),flush=True)
write_npz(O/'metadata.npz',out);archives['metadata.npz']=dict(sha256=pin(O/'metadata.npz'),bytes=(O/'metadata.npz').stat().st_size)
dump(O/'result.json',dict(input_sha256=pins,archives=archives,reports=reports,
 classification='EXECUTED_AE2_COLORLESS96_EVENT_BINDING_IN_ORIGINAL_CHILD_FIELD_FAMILY',
 field_equation='child T Phi_t+R Phi_r+K Phi=0 on the declared future Cauchy cell, with original outgoing-characteristic equations and explicit incoming/birth data',
 event_equation='C96.T Sc^-1 Gamma_child=spin_sign K96 C96.T q_parent',
 event_source='both corrected supplied directions, all7 map-source responses and child normal-rate source; independent delta h and total deltaF ports retained',
 joint_event_complex_rank_per_collar=96,child_data_remaining_per_collar=2976,parent_h_retained=3660,
 remaining_joint_complex_coordinates_per_collar=6636,remaining_bosonic_compatibility_coordinates=538,
 parent_h_selected_by_event_rank=0,full_formation_Hessian=None,physical_outer_residual=None,
 all_unbound_data='original child response H_free d_free retained; no coordinate assigned zero as a physical state',
 amplitude_rule='a_R,a_LR,a_RL remain tied to the same physical g and independent normal profiles; saved columns are coordinate derivatives only',
 global_spin_sign=None,spin_sign_rule='stored coefficient representative +; exact - response is its negative by linearity, neither chosen physically',
 fullcap_incidence=None,color288_map=None,local_normal_integrals=None,
 independent_original_child_checks=None,parent_original_checks='saved residual operators retained; physical Rpart*a+Rh*h remains uncomputed until actual data are determined',
 error_scope='finite coordinate responses and event rows; no continuum, exterior, full physical Cauchy norm or trace-stability bound',
 physical_guard=2e-10,physical_admission=False,
 NEXT_OPERAND='apply original differential/source operators to these actual event-driven child combinations, including retained incoming boundary rows; consume demonstrated pole/outer constraints on parent h and retain all unresolved state/profile/domain data'))
print('EVENT_CHILD_CORE_SAVED',pin(O/'result.json'),flush=True)
