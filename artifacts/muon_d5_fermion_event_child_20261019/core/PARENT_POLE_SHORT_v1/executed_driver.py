from pathlib import Path
from hashlib import sha256
import os,sys,json,time
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
WORK=Path(__file__).resolve().parent;OUT=WORK/'PARENT_POLE_SHORT_v1'
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_complement_bulk_response import load_groups
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_event_normal_source_application import ProvisionalNormalSourceHistory
from bhsm.interface.muon_d5_complement_bulk_response import _generator,_collocation_rule
from bhsm.interface.muon_d5_temporal_bulk_refinement import coefficient_rows,time_evaluation_matrix
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_d5_pole_admissibility import (
 original_n0_pole_indicial,frobenius_regular_seed,propagate_regular_frame,regular_frame_at,pole_boundary_rows)
from bhsm.interface.retained_response.finite_time_response import write_npz

def pin(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,a):p.write_text(json.dumps(a,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def main():
 OUT.mkdir(exist_ok=False);start=time.monotonic()
 prior=ROOT/'artifacts/muon_d5_valid_domain_application_20261019/run_3'
 receipt=json.loads((prior/'core_result.json').read_text());saved=load_groups(prior,receipt['archives'])
 _,hist,pins=inputs();h,hr=recovered_export_history(ROOT,'incoming',*hist['incoming']);pins.update(hr['input_sha256'])
 times=saved['times'];D=saved['time_derivative'];n=len(times);psi=-.47802575718819384
 source=ProvisionalNormalSourceHistory(h,psi)
 op='plus_particle';index=saved[op+'_block0_indices'];d=len(index)
 owner=ROOT/'src/bhsm/interface/muon_d5_pole_admissibility.py'
 pins[owner.relative_to(ROOT).as_posix()]=pin(owner)
 pins[str(prior/'core_result.json')]=pin(prior/'core_result.json')
 pins[str(Path(__file__))]=pin(Path(__file__))
 dump(OUT/'BEFORE.json',dict(input_sha256=pins,op=op,carrier_indices=index.tolist(),
  epsilon=1e-10,radial_end=8e-10,normal_source_psi=psi,
  equation='original regular Frobenius frame n0 D5, not selected amplitudes or full pole-to-wall map',
  NEXT_OPERAND='execute short outward Frobenius trial before any full pole transport'))
 (OUT/'executed_source_owner.py').write_bytes(owner.read_bytes());(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
 full=full_d5_localized_lepton_trace();pole=original_n0_pole_indicial(full['gamma5D_particle'],sheet_orientation=1)
 A0=np.kron(np.eye(n),pole['indicial'][np.ix_(index,index)])
 P=np.kron(np.eye(n),pole['regular_projector'][np.ix_(index,index)])
 epsilon=1e-10;bounds=epsilon*2.**np.arange(4);nodes,_,_,_=_collocation_rule(3)
 stage_r=bounds[:-1,None]+np.diff(bounds)[:,None]*nodes
 probe_r=bounds[:-1]+.413*np.diff(bounds)
 all_r=np.r_[epsilon,epsilon/2,epsilon/4,stage_r.ravel(),probe_r]
 coefficients,mu,mux=coefficient_rows(source,times,all_r)
 generators=[];generatorx=[]
 for j,r in enumerate(all_r):
  T,R,K,Tx,Rx,Kx=[coefficients[op][k][j][:,index][:,:,index] for k in (
   'time','radial','body','time_source','radial_source','body_source')]
  g,gx=_generator(T,R,K,Tx,Rx,Kx,D);generators.append(g);generatorx.append(gx)
 g,gx=np.array(generators),np.array(generatorx)
 seed=frobenius_regular_seed(A0,P,g[0]-A0/epsilon,gx[0],epsilon=epsilon)
 count=stage_r.size
 gs=(g[3:3+count]-np.eye(n*d)[None]/stage_r.ravel()[:,None,None]).reshape(3,3,n*d,n*d)
 gxs=gx[3:3+count].reshape(gs.shape)
 app=propagate_regular_frame(bounds,gs,gxs,seed['regular_seed'],seed['regular_seed_source'])
 rows=[];srows=[];fields=[];fieldxs=[]
 independent_times=np.array([times[0]+.179*(times[-1]-times[0]),times[0]+.617*(times[-1]-times[0]),times[0]+.891*(times[-1]-times[0])])
 ic,_,_=coefficient_rows(source,independent_times,probe_r)
 E=time_evaluation_matrix(times,independent_times);Et=time_evaluation_matrix(times,independent_times,1)
 for ri,r in enumerate(probe_r):
  v=regular_frame_at(app,r);k=v['value'].shape[1]
  ev=lambda a,w:np.einsum('pt,tdk->pdk',w,a.reshape(n,d,k))
  V,Vr,Vt=ev(v['value'],E),ev(v['radial'],E),ev(v['value'],Et)
  Vx,Vrx,Vtx=ev(v['source_value'],E),ev(v['source_radial'],E),ev(v['source_value'],Et)
  T,R,K,Tx,Rx,Kx=[ic[op][key][ri][:,index][:,:,index] for key in (
   'time','radial','body','time_source','radial_source','body_source')]
  rows.append(R@Vr+T@Vt+K@V)
  srows.append(R@Vrx+T@Vtx+K@Vx+Rx@Vr+Tx@Vt+Kx@V)
  fields.append(V);fieldxs.append(Vx)
 boundary=pole_boundary_rows(app['regularized_final'],app['regularized_source_final'])
 arrays=dict(times=times,time_derivative=D,block_indices=index,leading_indicial=A0,
  regular_projector=P,leading_radius_probes=all_r[:3],
  original_indicial_probe_rows=np.array([r*a-A0 for r,a in zip(all_r[:3],g[:3])]),
  original_source_indicial_probe_rows=np.array([r*a for r,a in zip(all_r[:3],gx[:3])]),
  original_volume_density=mu[:3],independent_times=independent_times,independent_radii=probe_r,
  independent_original_D5_rows=np.array(rows),independent_original_source_rows=np.array(srows),
  independent_field_frames=np.array(fields),independent_field_source_frames=np.array(fieldxs),
  **{'seed_'+k:v for k,v in seed.items()},**app,**boundary)
 write_npz(OUT/'application.npz',arrays)
 report=dict(classification='EXECUTED_ORIGINAL_N0_POLE_FROBENIUS_SHORT_OUTWARD_FRAME',
  op=op,original_carrier_indices=index.tolist(),time_nodes=n,full_block_dimension=n*d,
  regular_amplitude_dimension=seed['regular_seed'].shape[1],regular_exponent=1,singular_exponent=-2,
  finite_Cauchy_condition='rho^3 norm: exponent−2 logarithmically divergent, exponent+1 integrable',
  indicial_source_exact_zero=True,
  indicial_probe_rows_max=[float(np.max(abs(a))) for a in arrays['original_indicial_probe_rows']],
  indicial_source_probe_max=[float(np.max(abs(a))) for a in arrays['original_source_indicial_probe_rows']],
  first_recursion_max=float(np.max(abs(seed['original_first_recursion_rows']))),
  first_source_recursion_max=float(np.max(abs(seed['original_first_source_recursion_rows']))),
  stage_rows_max=np.max(app['stage_rows'],axis=0).tolist(),
  independent_original_D5_max=float(np.max(abs(rows))),independent_original_source_max=float(np.max(abs(srows))),
  regular_boundary_value_max=float(np.max(abs(boundary['original_regular_rows']))),
  regular_boundary_source_max=float(np.max(abs(boundary['original_regular_source_rows']))),
  regular_boundary_pivot_condition=float(boundary['pivot_condition']),
  normalization_or_physical_amplitude_selected=False,physical_h_or_delta_h_selected=False,
  free_normal_rate_source='independent column remains required; not included in this particular corrected-Xi short trial',
  time_faces='all10 regular seed time coordinates retained; no initial/final physical data assigned',
  domain_scope='genuine cap-pole necessary n0 finite-Cauchy condition; incidence of each full normal collar/exterior remains separate',
  source_scope='original Xi plus saved provisional constant proper-normal correction only; no full physical derivative',
  cutoff_scope='numerical epsilon start with first two Frobenius orders, no cutoff-error enclosure',
  saved_strip_sewn=False,full_pole_to_strip_transport=False,continuum_bound=False,physical_admission=False,physical_guard=2e-10,
  elapsed_seconds=time.monotonic()-start,
  NEXT_OPERAND='inspect exact original coefficient/source indicial and independent errors before full pole-to-saved-strip regular-domain transport with all blocks and free time/source data')
 dump(OUT/'result.json',dict(input_sha256=pins,arrays=dict(sha256=pin(OUT/'application.npz')),
  report=report));print(json.dumps(report,sort_keys=True,indent=2),flush=True)

if __name__=='__main__':main()
