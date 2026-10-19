"""Actual parent characteristic/initial-face rows, using completed operands."""
from pathlib import Path
from hashlib import sha256
import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
from scipy.linalg import qr
ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');WORK=Path(__file__).resolve().parent
OUT=WORK/'PARENT_CHARACTERISTIC_v1';sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_complement_bulk_response import load_groups
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from scripts.evaluate_muon_d5_event_matching import cached,BASE
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_temporal_bulk_refinement import _factor_at,time_evaluation_matrix
from bhsm.interface.muon_d5_corrected_homogeneous_source import corrected_source_factor
from bhsm.interface.muon_d5_child_characteristic_field import characteristic_bases
from bhsm.interface.muon_holomorphic_normal_geometry import RADIUS0
def pin(p):return sha256(p.read_bytes()).hexdigest()
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
def dump(p,a):p.write_text(json.dumps(a,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
 OUT.mkdir(exist_ok=False)
 gp=WORK/'PARENT_LEPTON_POLE_GLOBAL_v1/stage_coefficients.npz';stage=load(gp)
 prior=ROOT/'artifacts/muon_d5_valid_domain_application_20261019/run_3';receipt=json.loads((prior/'core_result.json').read_text());saved=load_groups(prior,receipt['archives'])
 completed,_,pins,_=cached(BASE/'represented_source_core')
 sp=Path('C:/Users/carbe/Downloads/BHSM_D5_TWO_SIDED_EVENT_20261019/PARENT_H_SOURCE_v1/source_application.npz');source=load(sp)
 _,hist,hpins=inputs();pins.update(hpins);h,hr=recovered_export_history(ROOT,'incoming',*hist['incoming']);pins.update(hr['input_sha256'])
 owner=ROOT/'src/bhsm/interface/muon_d5_child_characteristic_field.py';pins[owner.relative_to(ROOT).as_posix()]=pin(owner)
 pins[str(gp)]=pin(gp);pins[str(sp)]=pin(sp);pins[str(Path(__file__))]=pin(Path(__file__))
 (OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes());(OUT/'executed_characteristic_owner.py').write_bytes(owner.read_bytes())
 dump(OUT/'BEFORE.json',dict(input_sha256=pins,equation='incoming characteristic and actual earliest-time Cauchy rows; no incoming datum assigned',
  muon_family_index=1,NEXT_OPERAND='evaluate exact PinQ/Pina and initial-face field/source coefficients from completed responses'))
 times=saved['times'];D=saved['time_derivative'];n=len(times);indices=saved['plus_particle_block3_indices'];d=len(indices)
 (Qin,_),(Qout,_)=characteristic_bases('particle',1,indices) # returned inner then outer
 outer=Qout;Pin=outer@outer.conj().T;Pout=Qin@Qin.conj().T
 C=np.kron(np.eye(n),outer.conj().T)
 characteristic=[];first=[];checks=[]
 for G,Gx in zip(stage['generators'],stage['generator_sources']):
  per=[];perx=[]
  for i in range(n):
   j=(i+1)%n
   A=G[i*d:(i+1)*d,j*d:(j+1)*d]/D[i,j]
   Ax=Gx[i*d:(i+1)*d,j*d:(j+1)*d]/D[i,j]
   inv=np.linalg.inv(A);V=-inv;Vx=inv@Ax@inv
   m=np.trace(V)/d;W=V-m*np.eye(d);speed=np.sqrt(np.trace(W@W)/d)
   mx=np.trace(Vx)/d;speedx=np.trace(W@(Vx-mx*np.eye(d)))/(d*speed)
   per.append([m-speed,m+speed]);perx.append([mx-speedx,mx+speedx])
   checks.append([np.max(abs(V@outer-(m-speed)*outer)),np.max(abs(V@Qin-(m+speed)*Qin)),np.max(abs(V-V.conj().T))])
  characteristic.append(per);first.append(perx)
 characteristic=np.array(characteristic);first=np.array(first)
 # A conservative algebraic envelope over the entire held affine history
 # and0<=rho<=WALL, not merely a finite sample maximum.
 endpoints=np.array([h.value(times[0])[0],h.value(times[-1])[0]]).real;u=np.max(abs(endpoints),axis=0)
 logCmin=np.log(float(RADIUS0))+np.min(endpoints[:,0])-sum(u[1:25]);Cmin=np.exp(logCmin)
 smax=u[98];wallmin=np.pi/4-smax/Cmin
 lcmax=u[37]+sum(u[38:62]);drmax=(u[99]+lcmax*smax)/Cmin
 zmax=(sum(u[86:98])+drmax)*np.pi/(2*wallmin)
 Nmax=np.exp(sum(u[74:86]));Crhomin=Cmin*wallmin/(np.pi/2)
 vmax=zmax+Nmax/Crhomin;dt=times[-1]-times[0];radial_reach=vmax*dt
 # Original MUON family, not electron-family sewing. The same exact64
 # fundamental is repeated across families by the action.
 family=1;rows=128*family+indices
 Wq=np.zeros((n*d,n*366),complex);Wqx=np.zeros_like(Wq)
 for i in range(n):
  Wq[i*d:(i+1)*d,i*366:(i+1)*366]=completed['wall_plus_complement_basis'][i,rows]
  Wqx[i*d:(i+1)*d,i*366:(i+1)*366]=completed['wall_plus_complement_basis_source'][i,rows]
 Wa=completed['plus_seed_wall'][:,rows].reshape(n*d,-1);Wax=completed['plus_seed_wall_source'][:,rows].reshape(n*d,-1)
 A,Ax=C@Wq,C@Wqx;B,Bx=C@Wa,C@Wax
 _,_,pivot=qr(A,pivoting=True,mode='economic');pivot=pivot[:len(A)];free=np.setdiff1d(np.arange(3660),pivot)
 P,Px=A[:,pivot],Ax[:,pivot];inv=np.linalg.inv(P)
 ha=-inv@B;hf=-inv@A[:,free];hc=inv
 hax=-inv@(Bx+Px@ha);hfx=-inv@(Ax[:,free]+Px@hf);hcx=-inv@Px@hc
 # Evaluate the actual earliest-time trace at three points of the saved
 # strip. This is a finite restriction of the full Cauchy-face equation.
 radii=np.linspace(saved['radial_boundaries'][0],saved['radial_boundaries'][-1],3)
 Et0=np.kron(time_evaluation_matrix(times,[times[0]]),np.eye(d));Ett0=np.kron(time_evaluation_matrix(times,[times[0]],1),np.eye(d))
 init={name:[] for name in ('h','h_source','particular','particular_source','h_time','h_radial','particular_time','particular_radial')}
 for r in radii:
  H,Hr,_,_=_factor_at(saved,'plus_particle_block3_',[r])[0]
  Hx,Hxr,Z,Zr=corrected_source_factor(source,'plus_particle_block3_',[r])[0]
  V,Vx=H@Wq,Hx@Wq+Z@Wqx;U,Ux=H@Wa,Hx@Wa+Z@Wax
  for name,value in dict(h=Et0@V,h_source=Et0@Vx,particular=Et0@U,particular_source=Et0@Ux,
   h_time=Ett0@V,h_radial=Et0@Hr@Wq,particular_time=Ett0@U,particular_radial=Et0@Hr@Wa).items():init[name].append(value)
 arrays=dict(block_indices=indices,muon_family_index=np.array(1),times=times,radial_probe=radii,
  original_speed=characteristic,original_speed_source=first,characteristic_checks=np.array(checks),
  incoming_projector=Pin,outgoing_projector=Pout,incoming_trace_rows=C,
  incoming_h=A,incoming_h_source=Ax,incoming_particular=B,incoming_particular_source=Bx,
  h_pivot_columns=pivot,remaining_h_columns=free,h_pivot_from_particular=ha,h_pivot_from_particular_source=hax,
  h_pivot_from_incoming_datum=hc,h_pivot_from_incoming_datum_source=hcx,
  h_pivot_from_free_h=hf,h_pivot_from_free_h_source=hfx,
  original_particular_pivot_rows=P@ha+B,original_particular_pivot_source_rows=Px@ha+P@hax+Bx,
  original_incoming_datum_pivot_rows=P@hc-np.eye(len(P)),
  **{'initial_'+key:np.array(value) for key,value in init.items()})
 write_npz(OUT/'application.npz',arrays)
 report=dict(classification='EXECUTED_ORIGINAL_PARENT_CHARACTERISTIC_AND_INITIAL_FACE_COEFFICIENTS',
  principal_equation='T^-1 R=epsilon (N/C_rho) Gamma0 Gamma4−zeta I',
  principal_source='Vx=A^-1 Ax A^-1 from original G_ij=−R^-1 T D_ij, with i!=j; body coefficients are not substituted',
  original_characteristic_eigen_row_max=float(np.max(abs(arrays['characteristic_checks'][:,:2]))),
  characteristic_Hermitian_max=float(np.max(abs(arrays['characteristic_checks'][:,2]))),
  evaluated_speed_min=float(np.min(characteristic.real)),evaluated_speed_max=float(np.max(characteristic.real)),
  speed_source_max=float(np.max(abs(first))),positive_wall_chart_lower_bound=float(wallmin),
  algebraic_affine_history_speed_upper_bound=float(vmax),parent_time_span=float(dt),
  algebraic_backward_radial_reach_upper_bound=float(radial_reach),pole_distance_at_saved_strip=float(saved['radial_boundaries'][-1]),
  cone_scope='algebraic triangle bounds on exact held affine/trigonometric coefficient formulas, binary64 evaluation not interval rounding enclosure; large gap to pole',
  incoming_characteristic_count_per64=32,leptonweak8_incoming_count_per_time=4,
  muon_family_index=1,incoming_h_rows=40,explicit_h_pivot_rank=40,h_pivot_condition=float(np.linalg.cond(P)),
  remaining_h_coordinates=len(free),all_h_and_independent_delta_h_retained=True,
  h_pivot_from_particular_max=float(np.max(abs(ha))),particular_reconstruction_max=float(np.max(abs(P@ha+B))),
  particular_source_reconstruction_max=float(np.max(abs(Px@ha+P@hax+Bx))),
  incoming_datum_assigned=False,zero_incoming_condition_imposed=False,physical_h_or_state_selected=False,
  initial_face_equation='Gamma_Cauchy(t0) Phi_parent(g,h)=Psi_prepared(t0) on the actual parent cap/Cauchy incidence; independent incoming characteristic law at timelike faces',
  initial_face_scope='three evaluated strip restrictions and their original time/radial/source coefficients; not the complete physical Cauchy section',
  preparation_equation='Psi_prepared(t0)=Gamma_Cauchy(t0) U_y(t0,tprep) Omega_- P_as f_as, with the adopted same-action dressed stationary-past comparison and physical Cauchy incidence',
  selector_adjudication_reopened=False,past_comparison_or_wave_operator_evaluated_here=False,
  pair_conversion_scope='beam four-mode preparation and interacting occupation are not replaced by a one-particle muon-family propagation or nonzero odd expectation',
  preserved_parent_bulk_source_nonpasses=True,source_scope='declared corrected-Xi coefficient only; independent normal-rate, event/time-face/frame/state variations remain explicit',
  physical_norm_residual=None,physical_admission=False,physical_guard=2e-10,
  NEXT_OPERAND='consume actual same-action prepared Cauchy sections and the interacting boundary/correlation data in these initial/incoming rows, jointly with the executed child event/corner equations; do not use rejected global pole h correction')
 dump(OUT/'result.json',dict(input_sha256=pins,arrays=dict(sha256=pin(OUT/'application.npz')),report=report));print(json.dumps(report,sort_keys=True,indent=2),flush=True)
if __name__=='__main__':
 from bhsm.interface.retained_response.finite_time_response import write_npz
 main()
