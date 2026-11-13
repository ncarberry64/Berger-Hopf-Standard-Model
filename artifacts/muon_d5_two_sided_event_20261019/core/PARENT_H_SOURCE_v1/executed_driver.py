from pathlib import Path
from hashlib import sha256
import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
R=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
W=Path(__file__).resolve().parent;O=W/'PARENT_H_SOURCE_v1'
sys.path[:0]=[str(R/'src'),str(R)]
from scripts.evaluate_muon_d5_complement_bulk_response import load_groups,owners
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from scripts.evaluate_muon_d5_event_matching import cached,BASE
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_temporal_bulk_refinement import coefficient_rows,time_evaluation_matrix,_factor_at
from bhsm.interface.muon_d5_corrected_homogeneous_source import solve_corrected_homogeneous_source,corrected_source_factor
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_bytes((json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())
prior=R/'artifacts/muon_d5_valid_domain_application_20261019/run_3'
core=json.loads((prior/'core_result.json').read_bytes());saved=load_groups(prior,core['archives'])
completed,sr,cp,_=cached(BASE/'represented_source_core')
formation,fr,fp,_=cached(BASE/'formation_core');psi=float(formation['provisional_normal_displacement_source_correction'][0].real)
_,hist,pins=inputs();history,receipt=recovered_export_history(R,'incoming',*hist['incoming']);pins.update(receipt['input_sha256'])
pins.update(cp);pins.update(fp);pins.update(owners())
pins.update({(prior/n).relative_to(R).as_posix():m['sha256'] for n,m in core['archives'].items()})
pins[(prior/'core_result.json').relative_to(R).as_posix()]=pin(prior/'core_result.json')
O.mkdir(exist_ok=True)
if not (O/'source_result.json').exists():
 dump(O/'BEFORE.json',dict(input_sha256=pins,source_psi_parent_E1=psi,
  parent_head='67c113ea5ba2d1558e694a2db02d9e3b245a1e1b',NEXT_OPERAND='compute full retained homogeneous source, never assign physical h'))
 owner=R/'src/bhsm/interface/muon_d5_corrected_homogeneous_source.py'
 (O/'executed_source_owner.py').write_bytes(owner.read_bytes());(O/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
 source,report,newhistory=solve_corrected_homogeneous_source(saved,completed,history,psi)
 write_npz(O/'source_application.npz',source)
 dump(O/'source_result.json',dict(input_sha256=pins,arrays=dict(sha256=pin(O/'source_application.npz')),
  report=report,physical_admission=False))
 print('PARENT_H_SOURCE_SAVED',pin(O/'source_result.json'),flush=True)
else:
 record=json.loads((O/'source_result.json').read_bytes());assert record['input_sha256']==pins
 assert record['arrays']['sha256']==pin(O/'source_application.npz')
 with np.load(O/'source_application.npz',allow_pickle=False) as z:source={k:z[k].copy(order='K') for k in z.files}
 report=record['report']
 from bhsm.interface.muon_d5_event_normal_source_application import ProvisionalNormalSourceHistory
 newhistory=ProvisionalNormalSourceHistory(history,psi)
 print('REUSED_PARENT_H_SOURCE',flush=True)
if (O/'result.json').exists():print('REUSED_PARENT_H_CHECKS',flush=True);raise SystemExit(0)
t=saved['times'];bounds=saved['radial_boundaries'];width=bounds[0]-bounds[-1]
radii=bounds[0]-width*np.array([.043,.319,.947])
pointsets=dict(independent9=np.array([(t[0]+(t[-1]-t[0])*a,r) for a in (.079,.413,.913) for r in radii]),
 old6times=np.array([(a,r) for a in saved['amplitude_times'] for r in radii]))
rows={};checks={}
for name,points in pointsets.items():
 coeffs=[coefficient_rows(newhistory,[time],[rho])[0] for time,rho in points]
 for op in ('plus_particle','plus_conjugate','minus_particle','minus_conjugate'):
  maxima=np.zeros(6)
  for bi in range(int(saved[op+'_block_count'])):
   prefix=op+'_block'+str(bi)+'_';idx=saved[prefix+'indices'];d=len(idx);nd=len(t)*d
   records=[]
   for (time,rho),co in zip(points,coeffs):
    c=co[op];E=time_evaluation_matrix(t,[time])[0];Et=time_evaluation_matrix(t,[time],1)[0]
    H,Hr,Hxo,Hxro=_factor_at(saved,prefix,[rho])[0]
    Hx,Hxr,Z,Zr=corrected_source_factor(source,prefix,[rho])[0]
    ev=lambda a,w:np.einsum('t,tdk->dk',w,a.reshape(len(t),d,nd))
    V,Vr,Vt=ev(H,E),ev(Hr,E),ev(H,Et)
    vx,vrx,vtx=ev(Hx,E),ev(Hxr,E),ev(Hx,Et)
    ox,orx,otx=ev(Hxo,E),ev(Hxro,E),ev(Hxo,Et)
    z,zr,zt=ev(Z,E),ev(Zr,E),ev(Z,Et)
    T,Rr,K,Tx,Rx,Kx=[c[k][0,0][np.ix_(idx,idx)] for k in ('time','radial','body','time_source','radial_source','body_source')]
    vrow=Rr@Vr+T@Vt+K@V;vertex=Rx@Vr+Tx@Vt+Kx@V
    oldrow=Rr@orx+T@otx+K@ox+vertex;newrow=Rr@vrx+T@vtx+K@vx+vertex
    zrow=Rr@zr+T@zt+K@z
    records.append(np.stack((vrow,oldrow,newrow,zrow)))
    maxima=np.maximum(maxima,[np.max(abs(vrow)),np.max(abs(oldrow)),np.max(abs(newrow)),
     np.max(abs(zrow)),np.max(abs(Z-H)),np.max(abs(vertex))])
   rows[name+'_'+prefix+'original_rows']=np.array(records)
  checks[name+'_'+op]=dict(zip(('held_value_max','old_Xi_with_new_coefficients_source_max','corrected_source_max',
   'new_source_initial_data_propagator_max','source_initial_propagator_minus_held_H10_max','source_vertex_max'),maxima.tolist()))
  print(name,op,checks[name+'_'+op],flush=True)
 rows[name+'_points']=points
write_npz(O/'independent_rows.npz',rows)
dump(O/'result.json',dict(input_sha256=pins,source_result_sha256=pin(O/'source_result.json'),
 independent_rows_sha256=pin(O/'independent_rows.npz'),report=report,checks=checks,
 norm='max absolute original strong matrix component on every saved carrier block and cardinal input column at stated points; no physical preparation/Cauchy norm or continuum bound',
 finite_new_source_is_not_exact_derivative_of_old_discrete_value_algorithm=True,
 original_value_and_historical_nonpasses_preserved=True,physical_guard=2e-10,physical_admission=False,
 NEXT_OPERAND='consume corrected Hx and source initial-data propagator Z with actual full wall Q/Qx and joint event/formation h coordinates; do not transfer unit-column arithmetic to physical trace stability'))
print('PARENT_H_CHECKS_SAVED',pin(O/'result.json'),flush=True)
