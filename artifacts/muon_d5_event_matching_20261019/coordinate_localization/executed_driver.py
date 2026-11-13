import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json
from hashlib import sha256
import numpy as np
ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');BASE=Path(__file__).parent
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_complement_bulk_response import load_groups
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history,original_d5_coefficient_callback,original_strong_rows
from bhsm.interface.muon_d5_event_normal_source_application import ProvisionalNormalSourceHistory,evaluate_event_normal_source
from bhsm.interface.muon_d5_temporal_bulk_refinement import time_evaluation_matrix,nodal_derivative
from bhsm.interface.muon_d5_complement_bulk_response import _collocation_rule
from bhsm.interface.retained_response.finite_time_response import write_npz
OUT=BASE/'SOURCE_COORDINATE_LOCALIZATION_v2';OUT.mkdir(exist_ok=False)
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
old=ROOT/'artifacts/muon_d5_valid_domain_application_20261019/run_3';core=json.loads((old/'core_result.json').read_bytes());saved=load_groups(old,core['archives'])
sourcepath=BASE/'SOURCE_CONSISTENT_RHS2_v1/source_application.npz'
with np.load(sourcepath,allow_pickle=False) as z:source={k:z[k].copy(order='K') for k in z.files}
_,histories,pins=inputs();history,receipt=recovered_export_history(ROOT,'incoming',*histories['incoming'])
newhistory=ProvisionalNormalSourceHistory(history,complex(source['provisional_constant_psi_E1']))
t=source['times'];bounds=source['radial_boundaries'];q=int(source['radial_order']);cn,polys,integral,A=_collocation_rule(q)
P=time_evaluation_matrix(t,t);Dt=time_evaluation_matrix(t,t,1);D=nodal_derivative(t)
stages=[(step,j,left+(right-left)*cn[j]) for step,(left,right) in enumerate(zip(bounds[:-1],bounds[1:])) for j in range(q)]
chosen=[stages[k] for k in (0,4,9)];reports={};out={}
for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
 coef=original_d5_coefficient_callback(lambda ti:(newhistory.value(ti)[0],newhistory.source(ti)[0]),sheet_orientation=1 if label.startswith('plus_') else -1,gauge_basis_evaluate=newhistory.gauge_basis)
 entries=[];chartentries=[];discreteentries=[];thetaerrors=[];sourceerrors=[]
 for si,j,rho in chosen:
  rho=float(rho);h=bounds[si+1]-bounds[si];theta=(rho-bounds[si])/h
  thetaerrors.append(theta-cn[j]);shape=(len(t),384,108)
  chart={key:np.zeros(shape,complex) for key in ('source','time_source','radial_source')}
  discrete={key:np.zeros(shape,complex) for key in chart}
  for branch_index,branch in enumerate(('particle','conjugate')):
   op=label.split('_')[0]+'_'+branch
   for bi in range(int(source[op+'_block_count'])):
    prefix=label+'_'+op+'_block'+str(bi)+'_';indices=source[prefix+'indices'];d=len(indices)
    initial=source[prefix+'source_initial'][si];slopes=source[prefix+'source_slopes'][si]
    V=initial+h*np.einsum('q,qdk->dk',integral(cn[j]),slopes)
    Vr=np.einsum('q,qdk->dk',np.array([p(cn[j]) for p in polys]),slopes)
    for family in range(3):
     sl=slice(family*108,(family+1)*108);rows=(2*family+branch_index)*64+indices
     a=V[:,sl].reshape(len(t),d,108);ar=Vr[:,sl].reshape(len(t),d,108)
     for key,w,b in (('source',P,a),('time_source',Dt,a),('radial_source',P,ar)):
      chart[key][:,rows]=(w@b.reshape(len(t),-1)).reshape(len(t),d,108)
     discrete['source'][:,rows]=a;discrete['radial_source'][:,rows]=ar
     discrete['time_source'][:,rows]=(D@a.reshape(len(t),-1)).reshape(len(t),d,108)
  rounded={key:a[0] for key,a in evaluate_event_normal_source(source,label,t,[rho]).items()}
  ri=int(np.argmin(abs(saved['radial_nodes']-rho)))
  if abs(saved['radial_nodes'][ri]-rho)>np.spacing(rho):raise ValueError('original saved stage identity required')
  value={key:saved[label+'_'+key][ri] for key in ('value','time','radial')}
  sourceerrors.append(max(float(np.max(abs(rounded[key]-chart[key]))) for key in chart))
  for ti,time in enumerate(t):
   c=coef(float(time),rho)
   def rows(sourcefields):return original_strong_rows({**{key:a[ti] for key,a in value.items()},**{key:a[ti] for key,a in sourcefields.items()}},c)['strong_source']
   entries.append(rows(rounded));chartentries.append(rows(chart));discreteentries.append(rows(discrete))
 tag=label+'_'
 out[tag+'original_rounded_rho_source_rows']=np.array(entries)
 out[tag+'exact_Gauss_coordinate_source_rows']=np.array(chartentries)
 out[tag+'exact_Gauss_and_discrete_D_source_rows']=np.array(discreteentries)
 reports[label]=dict(original_rounded_rho_source_max=float(np.max(abs(out[tag+'original_rounded_rho_source_rows']))),
  exact_Gauss_coordinate_arithmetic_diagnostic_max=float(np.max(abs(out[tag+'exact_Gauss_coordinate_source_rows']))),
  exact_Gauss_and_discrete_D_arithmetic_diagnostic_max=float(np.max(abs(out[tag+'exact_Gauss_and_discrete_D_source_rows']))),
  rho_inverse_theta_minus_original_Gauss_theta_max=float(np.max(np.abs(thetaerrors))),
  source_polynomial_derivative_roundtrip_difference_max=max(sourceerrors))
out['chosen_radial_step_Gaussindex_rho']=np.array(chosen)
write_npz(OUT/'arrays.npz',out)
record=dict(classification='FINITE_SOURCE_COORDINATE_ROUNDTRIP_LOCALIZATION',report=reports,
 input_sha256={str(sourcepath):pin(sourcepath),str(old/'core_result.json'):pin(old/'core_result.json'),str(Path(__file__)):pin(__file__)},
 time_interpolation_node_identity_defect_max=float(np.max(abs(P-np.eye(len(t))))),
 time_polynomial_derivative_minus_discrete_D_max=float(np.max(abs(Dt-D))),
 original_time_nodes=t.tolist(),physical_admission=False,continuum_error_bound=False,
 diagnostic_scope='Exact Gauss-chart evaluation and discrete-D rows isolate arithmetic; they are NOT original rounded-physical-rho probe passes and do not remove the recorded original-coordinate nonpasses',
 arrays=dict(sha256=pin(OUT/'arrays.npz'),bytes=(OUT/'arrays.npz').stat().st_size))
(OUT/'result.json').write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n')
print(json.dumps(record),flush=True)
