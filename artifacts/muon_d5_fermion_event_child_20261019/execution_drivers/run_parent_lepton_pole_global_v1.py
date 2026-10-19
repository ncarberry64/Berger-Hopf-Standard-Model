from pathlib import Path
from hashlib import sha256
import os,sys,json,time
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
from scipy.linalg import qr
ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
WORK=Path(__file__).resolve().parent;OUT=WORK/'PARENT_LEPTON_POLE_GLOBAL_v1'
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_complement_bulk_response import load_groups
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from scripts.evaluate_muon_d5_event_matching import cached,BASE
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_event_normal_source_application import ProvisionalNormalSourceHistory
from bhsm.interface.muon_d5_complement_bulk_response import _generator,_collocation_rule
from bhsm.interface.muon_d5_temporal_bulk_refinement import coefficient_rows,time_evaluation_matrix,_factor_at
from bhsm.interface.muon_d5_corrected_homogeneous_source import corrected_source_factor
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_d5_pole_admissibility import original_n0_pole_indicial,frobenius_regular_seed,pole_boundary_rows
from bhsm.interface.muon_d5_recharted_pole_domain import propagate_recharted_regular_frame,recharted_frame_at,sew_regular_pole_rows
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,a):p.write_text(json.dumps(a,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
def main():
 start=time.monotonic();OUT.mkdir(exist_ok=False)
 prior=ROOT/'artifacts/muon_d5_valid_domain_application_20261019/run_3'
 receipt=json.loads((prior/'core_result.json').read_text());saved=load_groups(prior,receipt['archives'])
 completed,_,cp,_=cached(BASE/'represented_source_core')
 oldsrc=Path('C:/Users/carbe/Downloads/BHSM_D5_TWO_SIDED_EVENT_20261019/PARENT_H_SOURCE_v1/source_application.npz')
 source_saved=load(oldsrc)
 _,hist,pins=inputs();h,hr=recovered_export_history(ROOT,'incoming',*hist['incoming']);pins.update(hr['input_sha256']);pins.update(cp)
 times=saved['times'];D=saved['time_derivative'];n=len(times);source=ProvisionalNormalSourceHistory(h,-.47802575718819384)
 assert np.array_equal(source_saved['source_Xi268_nodes'],np.array([source.source(t)[0] for t in times]))
 op='plus_particle';bi=3;prefix=op+'_block3_';indices=saved[prefix+'indices'];d=len(indices)
 assert np.array_equal(indices,np.array([6,7,22,23,38,39,54,55]))
 epsilon=1e-10;match=float(saved['radial_boundaries'][-1]);bounds=np.geomspace(epsilon,match,37)
 nodes,_,_,_=_collocation_rule(3);stage_r=(bounds[:-1,None]+np.diff(bounds)[:,None]*nodes).ravel()
 probe_r=bounds[:-1]+.413*np.diff(bounds)
 for name in ('muon_d5_pole_admissibility','muon_d5_recharted_pole_domain'):
  owner=ROOT/'src/bhsm/interface'/f'{name}.py';pins[owner.relative_to(ROOT).as_posix()]=pin(owner);(OUT/(name+'_executed.py')).write_bytes(owner.read_bytes())
 pins[str(oldsrc)]=pin(oldsrc);pins[str(prior/'core_result.json')]=pin(prior/'core_result.json');pins[str(Path(__file__))]=pin(Path(__file__))
 (OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
 dump(OUT/'BEFORE.json',dict(input_sha256=pins,cells=36,op=op,indices=indices.tolist(),
  epsilon=epsilon,match_saved_innerstrip=match,physical_admission=False,NEXT_OPERAND='bounded global regular-domain transport, original independent rows, actual h/particular sewing'))
 full=full_d5_localized_lepton_trace();pole=original_n0_pole_indicial(full['gamma5D_particle'],sheet_orientation=1)
 A0=np.kron(np.eye(n),pole['indicial'][np.ix_(indices,indices)]);P=np.kron(np.eye(n),pole['regular_projector'][np.ix_(indices,indices)])
 all_r=np.r_[epsilon,epsilon/2,stage_r];generators=[];firsts=[]
 for start_r in range(0,len(all_r),8):
  rs=all_r[start_r:start_r+8];c,_,_=coefficient_rows(source,times,rs)
  for j,r in enumerate(rs):
   T,R,K,Tx,Rx,Kx=[c[op][key][j][:,indices][:,:,indices] for key in ('time','radial','body','time_source','radial_source','body_source')]
   g,gx=_generator(T,R,K,Tx,Rx,Kx,D);generators.append(g);firsts.append(gx)
  print('COEFFICIENT_RADII',min(start_r+8,len(all_r)),len(all_r),flush=True)
 g,gx=np.array(generators),np.array(firsts)
 write_npz(OUT/'stage_coefficients.npz',dict(radii=all_r,generators=g,generator_sources=gx,A0=A0,P=P))
 seed=frobenius_regular_seed(A0,P,g[0]-A0/epsilon,gx[0],epsilon=epsilon)
 G=(g[2:]-np.eye(n*d)[None]/stage_r[:,None,None]).reshape(36,3,n*d,n*d);Gx=gx[2:].reshape(G.shape)
 app=propagate_recharted_regular_frame(bounds,G,Gx,seed['regular_seed'],seed['regular_seed_source'])
 write_npz(OUT/'frame.npz',dict(**app,**{'seed_'+key:value for key,value in seed.items()}))
 print('FRAME_SAVED',float(np.max(app['pivot_conditions'])),flush=True)
 independent_times=times[0]+np.array([.179,.617,.891])*(times[-1]-times[0]);E=time_evaluation_matrix(times,independent_times);Et=time_evaluation_matrix(times,independent_times,1)
 rows=[];srows=[];termmax=[]
 for start_r in range(0,len(probe_r),8):
  rs=probe_r[start_r:start_r+8];c,_,_=coefficient_rows(source,independent_times,rs)
  for j,r in enumerate(rs):
   v=recharted_frame_at(app,r);k=v['value'].shape[1];ev=lambda a,w:np.einsum('pt,tdk->pdk',w,a.reshape(n,d,k))
   V,Vr,Vt=ev(v['value'],E),ev(v['radial'],E),ev(v['value'],Et)
   Vx,Vrx,Vtx=ev(v['source_value'],E),ev(v['source_radial'],E),ev(v['source_value'],Et)
   T,R,K,Tx,Rx,Kx=[c[op][key][j][:,indices][:,:,indices] for key in ('time','radial','body','time_source','radial_source','body_source')]
   rows.append(R@Vr+T@Vt+K@V);srows.append(R@Vrx+T@Vtx+K@Vx+Rx@Vr+Tx@Vt+Kx@V)
   termmax.append([max(np.max(abs(R@Vr)),np.max(abs(T@Vt)),np.max(abs(K@V))),max(np.max(abs(R@Vrx)),np.max(abs(T@Vtx)),np.max(abs(K@Vx)),np.max(abs(Rx@Vr)),np.max(abs(Tx@Vt)),np.max(abs(Kx@V)))])
 boundary=pole_boundary_rows(app['final_frame'],app['final_frame_source'])
 B,Bx=boundary['boundary'],boundary['boundary_source'];H,Hr,_,_=_factor_at(saved,prefix,[match])[0]
 Hx,Hxr,Z,Zr=corrected_source_factor(source_saved,prefix,[match])[0]
 Q,Qx=completed['wall_plus_complement_basis'],completed['wall_plus_complement_basis_source']
 Wq=np.zeros((n*d,n*366),complex);Wqx=np.zeros_like(Wq)
 for node in range(n):
  Wq[node*d:(node+1)*d,node*366:(node+1)*366]=Q[node,indices]
  Wqx[node*d:(node+1)*d,node*366:(node+1)*366]=Qx[node,indices]
 Vh,Vhx=H@Wq,Hx@Wq+Z@Wqx
 hrows=sew_regular_pole_rows(B,Bx,Vh,Vhx)
 Wa=completed['plus_seed_wall'][:,indices].reshape(n*d,-1);Wax=completed['plus_seed_wall_source'][:,indices].reshape(n*d,-1)
 Va,Vax=H@Wa,Hx@Wa+Z@Wax;arows=sew_regular_pole_rows(B,Bx,Va,Vax)
 Bh,Bhx=hrows['value_rows'],hrows['source_rows'];Ba,Bax=arows['value_rows'],arows['source_rows']
 _,_,piv=qr(Bh,pivoting=True,mode='economic');pivot=piv[:len(Bh)];free=np.setdiff1d(np.arange(n*366),pivot);Hp=Bh[:,pivot];Hpx=Bhx[:,pivot]
 cond=float(np.linalg.cond(Hp));singular=np.linalg.svd(Hp,compute_uv=False)
 affine={}
 if np.isfinite(cond) and cond<1e12:
  a=np.linalg.solve(Hp,-Ba);f=np.linalg.solve(Hp,-Bh[:,free]);ax=np.linalg.solve(Hp,-Bax-Hpx@a);fx=np.linalg.solve(Hp,-Bhx[:,free]-Hpx@f)
  affine=dict(h_pivot_given_particular=a,h_pivot_given_particular_source=ax,h_pivot_given_free_h=f,h_pivot_given_free_h_source=fx,
   pivot_value_rows=Hp@a+Ba,pivot_source_rows=Hpx@a+Hp@ax+Bax,free_h_value_rows=Hp@f+Bh[:,free],free_h_source_rows=Hpx@f+Hp@fx+Bhx[:,free])
 output=dict(times=times,time_derivative=D,indices=indices,independent_times=independent_times,independent_radii=probe_r,
  original_D5_rows=np.array(rows),original_source_rows=np.array(srows),original_term_maxima=np.array(termmax),
  h_value_rows=Bh,h_source_rows=Bhx,particular_value_rows=Ba,particular_source_rows=Bax,
  h_pivot_columns=pivot,remaining_h_columns=free,pivot_singular_values=singular,
  **{'boundary_'+key:value for key,value in boundary.items()},**affine)
 write_npz(OUT/'sewn_application.npz',output)
 report=dict(classification='EXECUTED_BOUNDED_RECHARTED_ORIGINAL_POLE_DOMAIN_AND_SAVED_H_SEWING',
  op=op,indices=indices.tolist(),cells=36,time_nodes=n,regular_amplitudes=40,full_h_coordinates=3660,
  complete_regular_amplitudes_retained=True,transition_count=36,maximum_frame_pivot_condition=float(np.max(app['pivot_conditions'])),
  stage_value_source_max=np.max(app['stage_rows'],axis=0).tolist(),
  independent_original_D5_max=float(np.max(abs(output['original_D5_rows']))),independent_original_source_max=float(np.max(abs(output['original_source_rows']))),
  original_weak_radial_boundary_rows_max=float(np.max(abs(boundary['original_regular_rows']))),
  original_weak_radial_boundary_source_rows_max=float(np.max(abs(boundary['original_regular_source_rows']))),
  h_row_rank_at_explicit_pivot=int(len(Bh)) if affine else None,h_pivot_condition=cond,
  h_row_max=float(np.max(abs(Bh))),particular_row_max=float(np.max(abs(Ba))),
  remaining_h_coordinates=len(free),conditional_h_pivot_executed=bool(affine),
  conditional_pivot_value_max=float(np.max(abs(affine['pivot_value_rows']))) if affine else None,
  conditional_pivot_source_max=float(np.max(abs(affine['pivot_source_rows']))) if affine else None,
  conditional_h_from_particular_max=float(np.max(abs(affine['h_pivot_given_particular']))) if affine else None,
  physical_h_selected=False,independent_delta_h_retained=True,physical_norm_residual=None,physical_admission=False,physical_guard=2e-10,
  source_scope='original Xi plus saved constant proper-normal coefficient; independent free normal-rate/inherited/outer sources remain required',
  regular_seed_scope='first2 Frobenius orders from finite epsilon; no epsilon or continuum enclosure',
  domain_scope='necessary n0 cap-pole regularity; full sigma-normal collar/exterior incidence and physical time faces remain open',
  residual_norm='max absolute original strong matrix component at3 independent times and1 independent rho per36 cells; not physical Cauchy norm',
  amplitude_scope='conditional affine operator in saved particular slots, independent h and all profile/g relations retained, not a state choice',
  elapsed_seconds=time.monotonic()-start,
  NEXT_OPERAND='use actual original residuals and conditioning to decide whether the pole rows may enter the coupled child/event system, retaining full physical time/normal/state errors')
 dump(OUT/'result.json',dict(input_sha256=pins,report=report,arrays={name:pin(OUT/name) for name in ('stage_coefficients.npz','frame.npz','sewn_application.npz')}));print(json.dumps(report,sort_keys=True,indent=2),flush=True)
if __name__=='__main__':main()
