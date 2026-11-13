import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json,hashlib
import numpy as np
ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
OUT=Path(__file__).parent/'RAW_WALL_EVENT_v1'
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_event_bundle_incidence import original_event_coefficients,wall_event_incidence
from bhsm.interface.muon_d5_event_formation_constraints import corrected_original_event_source_directions
from bhsm.interface.muon_full_d5_localized_lepton_trace import moving_d5_material_trace_frame,full_d5_localized_lepton_trace
from bhsm.interface.muon_d5_raw_event_trace import colorless_middle_jet,colorless_trace_lift,original_wall_green_checks
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.retained_response.finite_time_response import write_npz
pin=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
def dump(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def mx(a):return float(np.max(abs(a)))
if OUT.exists():raise FileExistsError('preserve prior checkpoint')
OUT.mkdir()
fp=ROOT/'artifacts/muon_d5_event_matching_20261019/formation_core/application.npz'
ap=ROOT/'artifacts/muon_d5_event_matching_20261019/affine_core/application.npz'
jp=ROOT/'artifacts/muon_d5_two_sided_event_20261019/core/JOINT_MAP_SOURCE_v1/application.npz'
hp=ROOT/'artifacts/muon_d5_two_sided_event_20261019/core/PARENT_H_CONSUMER_v1/application.npz'
formation,affine,joint,h=map(load,(fp,ap,jp,hp))
_,hist,pins=inputs();coeff=[];nu=[];histories=[]
for j,(name,side) in enumerate((('incoming','parent'),('outgoing','child'))):
 H,receipt=recovered_export_history(ROOT,name,*hist[name]);pins.update(receipt['input_sha256']);histories.append(H)
 d=corrected_original_event_source_directions(H,formation['provisional_raw_normal_source_correction'][j],side=side)
 d={k:np.concatenate((v,np.zeros_like(v)),axis=-1) for k,v in d.items()}
 d['raw'][:,1]=formation[side+'_raw_normal_columns'][:,1]
 c=original_event_coefficients(H,0.,[WALL],side=side,directions=d);coeff.append(c)
 velocity=c['material_wall_velocity'][0]
 nuframe=moving_d5_material_trace_frame(velocity,c['material_wall_velocity_first'][1,0])
 nu.append(nuframe['spin_boost_first128'])
 # Keep the supplied Xi first separate from the newly evaluated rate port.
 for k,v in list(c.items()):
  if k.endswith('_first') and isinstance(v,np.ndarray):c[k]=v[:1]
wall,wallreport=wall_event_incidence(*coeff)
S=[np.kron(np.eye(3),wall[s+'_spin_boost128']) for s in ('parent','child')]
Sx=[np.kron(np.eye(3),wall[s+'_spin_boost_first128']) for s in ('parent','child')]
N=[np.kron(np.eye(3),a) for a in nu]
C,powers=colorless_trace_lift();P=C@C.T;outside=np.eye(384)-P
f=full_d5_localized_lepton_trace();closure=[]
for a in list(f['gamma5D_self_dual128'])+list(f['unitTr16_gauge_self_dual128']):closure.append(mx(outside@np.kron(np.eye(3),a)@C))
out={'colorless_lift384x96':C,'Higgs_phase_integer_powers96':powers}
for j,side in enumerate(('parent','child')):
 out[side+'_material_spin384']=S[j];out[side+'_material_spin_Xi384']=Sx[j]
 out[side+'_material_spin_normal_rate384']=N[j]
out.update({'wall_'+k:v for k,v in wall.items()})
reports=[]
for i,idx in enumerate(joint['initial_candidate_index']):
 prefix='candidate'+str(int(idx))+'_';_,K,Kx=colorless_middle_jet(joint['known_middle128'][i],joint['known_middle_free_rotation_first128'][i],joint['Higgs_unit_phase'][i])
 out[prefix+'middle96']=K;out[prefix+'middle_free7_first96']=Kx
 out[prefix+'child_raw_left96x384']=C.T@np.linalg.inv(S[1])
 out[prefix+'raw_parent_to_child96_left']=S[1]@C@K@C.T@np.linalg.inv(S[0])
 out[prefix+'child_raw_lift384x96']=S[1]@C
 out[prefix+'child_raw_lift_Xi384x96']=Sx[1]@C
 out[prefix+'child_raw_lift_normal_rate384x96']=N[1]@C
 check=original_wall_green_checks(S[0],S[1],np.kron(np.eye(3),joint['known_middle128'][i]),
  wall['parent_wall_lapse'],wall['child_wall_lapse'],wall['parent_wall_radius'],wall['child_wall_radius'],wall['material_clock_differential'])
 checks={k:mx(check[k]) for k in ('normal_Clifford_rows','time_Clifford_rows','Dirac_bar_rows','density_pullback_row','original_wall_green_rows')}
 details={}
 for label in ('plus_seed','minus_seed','minus_LR','minus_RL','plus_homogeneous','minus_homogeneous'):
  q=affine[label+'_value']
  qx=affine[label+'_source']
  if label.endswith('homogeneous'):
   side=label.split('_')[0];q=h[side+'_h_value'];qx=h[side+'_h_corrected_source']
  else:
   # The active represented-source particular traces are saved in run_1;
   # affine_core Xi is historical. Source selection is corrected below.
   current=load(ROOT/'artifacts/muon_d5_event_matching_20261019/run_1/application.npz')
   for key in (label+'_value',label+'_source'):
    if key in current:
     if key.endswith('_value'):q=current[key]
     else:qx=current[key]
  target=K@C.T@q;targetx=K@C.T@qx
  # ν_parent frame contact is a coordinate effect only; its bulk response
  # is a separate currently uncomputed port, not assigned zero.
  parent_rate=-K@C.T@np.linalg.inv(S[0])@N[0]@q
  out[prefix+label+'_required_child_coordinates96']=target
  out[prefix+label+'_required_child_coordinates_Xi96']=targetx
  out[prefix+label+'_parent_normal_rate_frame_contact96']=parent_rate
  out[prefix+label+'_parent_time_contact96']=K@C.T@affine[label+'_time']
  out[prefix+label+'_parent_radial_fixed_frame_contact96']=K@C.T@affine[label+'_radial_fixed_frame']
  raw=S[1]@C@target;L=C.T@np.linalg.inv(S[1])
  details[label]=dict(columns=q.shape[1],rhs_max=mx(target),rhs_operator_norm2=float(np.linalg.norm(target,2)),
   parent_trace_block_rank=int(np.linalg.matrix_rank(target,tol=1e-12)),
   raw_reconstruction_row_max=mx(L@raw-target),
   known_source_rhs_max=mx(targetx),normal_rate_parent_bulk_response=None)
 reports.append(dict(candidate_index=int(idx),original_wall_checks=checks,channels=details))
for p in (fp,ap,jp,hp,ROOT/'artifacts/muon_d5_event_matching_20261019/run_1/application.npz',ROOT/'src/bhsm/interface/muon_d5_raw_event_trace.py',Path(__file__)):pins[str(p)]=pin(p)
write_npz(OUT/'application.npz',out)
record=dict(classification='EXECUTED_RAW_COLORLESS96_WALL_EVENT_TRACE_OPERATOR_AND_SOURCE',
 parent_head='f9285d08',input_sha256=pins,arrays=dict(sha256=pin(OUT/'application.npz')),
 exact_original_carrier_closure_max=max(closure),candidates=reports,
 row='C96.T Sc^-1 Gamma_child - spin_sign K96 C96.T Sp^-1 Gamma_parent=0',
 source='all Sc/Sp/middle and total base-pullback contacts; independent delta_h coefficient unchanged',
 structural_event_row_rank=96,parent_h_block_rank_at_E1=78,
 remaining_child_wall_color_coordinates=288,parent_h_coordinates_retained=3660,
 supersedes='arbitrary independent full384 Dp/Dc do not occur in raw AE2 point-section law; localized normal traces and coordinate half-densities remain distinct',
 density_rule='rho_child=kappa*rho_parent on the metric-matched wall; raw spinor carries no independently chosen density matrix',
 normal_mode_scope='uR/uL and full normal integrals remain required for localized18 reductions and physical amplitudes, not generic raw384 point traces',
 right_translation='b remains unassigned; represented Y0 scalar coefficients pull back constantly, b has no coefficient action on this restricted family',
 full_gauge_scope='full color288 requires explicit SU3 map and one of three hypercharge roots w^3=uH; no factor assigned',
 spin_sign=None,physical_child_field_selected=False,physical_outer_condition_solved=False,
 full_E1_cap_correspondence=None,full_event_residual=None,physical_admission=False,physical_guard=2e-10,
 error_scope='local wall-corner operator rows only; inherited full-family source/value nonpasses retained; no continuum or physical norm bound',
 NEXT_OPERAND='consume actual96 birth-wall operands through valid child Cauchy characteristic field; retain other288 wall data and remaining physical outer data; derive fullcap incidence independently')
dump(OUT/'result.json',record)
(OUT/'executed_source_owner.py').write_bytes((ROOT/'src/bhsm/interface/muon_d5_raw_event_trace.py').read_bytes())
(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(dict(path=str(OUT),sha256=record['arrays']['sha256'],report=reports),indent=2),flush=True)
