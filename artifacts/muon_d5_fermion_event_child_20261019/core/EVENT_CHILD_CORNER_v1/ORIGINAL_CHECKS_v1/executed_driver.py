from pathlib import Path
from hashlib import sha256
import json,sys,os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
R=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');W=Path(__file__).resolve().parent;O=W/'EVENT_CHILD_CORNER_v1/ORIGINAL_CHECKS_v1'
sys.path[:0]=[str(R/'src'),str(R)]
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_bytes((json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
assert not O.exists();O.mkdir();pr=json.loads((W/'CHILD_COEFFICIENT_PROBES_v1/result.json').read_bytes());probes={};pins={}
for name,meta in pr['archives'].items():
 p=W/'CHILD_COEFFICIENT_PROBES_v1'/name;assert pin(p)==meta['sha256'];probes.update(load(p));pins[str(p)]=pin(p)
er=json.loads((W/'EVENT_CHILD_CORNER_v1/result.json').read_bytes());pins[str(W/'EVENT_CHILD_CORNER_v1/result.json')]=pin(W/'EVENT_CHILD_CORNER_v1/result.json')
dump(O/'BEFORE.json',dict(input_sha256=pins,scope='original child differential/source application on actual event-driven coordinate coefficients, not selected physical data'))
reports=[];archives={}
for row in er['reports']:
 name='candidate'+str(row['candidate'])+'_'+row['label']+'.npz';p=W/'EVENT_CHILD_v1'/name;assert pin(p)==er['archives'][name]['sha256'];a=load(p)
 v,vt,vr=(a['child_'+k] for k in ('value','time','radial'))
 residual=np.zeros_like(v);sources=np.zeros((9,*v.shape),complex);side=row['label'].split('_')[0];slot=row['source_slot']
 for family in range(3):
  for b,branch in enumerate(('particle','conjugate')):
   label=side+'_'+branch
   for block in range(13):
    prefix=label+'_block'+str(block)+'_';idx=probes[prefix+'indices'];rows=(2*family+b)*64+idx
    T,Q,K=(probes[prefix+'original_coefficient_'+k] for k in ('time','radial','body'))
    Tx,Qx,Kx=(probes[prefix+'original_coefficient_'+k] for k in ('time_source','radial_source','body_source'))
    residual[:,:,rows]=T@vt[:,:,rows]+Q@vr[:,:,rows]+K@v[:,:,rows]
    for j,direction in enumerate([slot,*range(slot+1,slot+8),16]):
     stem='child_' if j==0 else ('child_free_map'+str(j-1)+'_' if j<8 else 'child_normal_rate_')
     vx,vtx,vrx=(a[stem+k] for k in ('source','time_source','radial_source'))
     r=Tx[direction]@vt[:,:,rows]+Qx[direction]@vr[:,:,rows]+Kx[direction]@v[:,:,rows]
     r+=T@vtx[:,:,rows]+Q@vrx[:,:,rows]+K@vx[:,:,rows]
     sources[j,:,:,rows]=r.transpose(2,0,1,3)
 arrays=dict(original_value_rows=residual,original_supplied_source_rows=sources[0],
  original_value_max_by_point=np.max(abs(residual),axis=(-2,-1)),
  original_source_max_by_direction_point=np.max(abs(sources),axis=(-2,-1)),
  original_source_Frobenius_by_direction_point=np.linalg.norm(sources,axis=(-2,-1)),
  original_parent_column_indices=a['original_parent_column_indices'])
 dest=O/name;write_npz(dest,arrays);archives[name]=dict(sha256=pin(dest),bytes=dest.stat().st_size)
 r=dict(candidate=row['candidate'],label=row['label'],columns=len(a['original_parent_column_indices']),
  independent_original_value_max=float(np.max(abs(residual))),independent_original_source_max=float(np.max(abs(sources[0]))),
  all9_source_direction_maxima=np.max(abs(sources),axis=(1,2,3,4)).tolist())
 reports.append(r);print(json.dumps(r),flush=True)
dump(O/'result.json',dict(input_sha256=pins,archives=archives,reports=reports,
 norm='maximum absolute coordinate component of original strong D5 at3x3 independent future points across stated actual event-input coefficient columns; not physical Cauchy norm',
 source_directions=['supplied Xi','map0','map1','map2','map3','map4','map5','map6','child_nu'],
 physical_admission=False,physical_guard=2e-10,physical_combination='Phi_event_h h+Phi_event_R a_R+Phi_event_LR a_LR+Phi_event_RL a_RL+Phi_free d_free; all physical amplitudes unassigned',
 parent_residual_operator_scope='saved particular and full3660-h original residual operators reused at9 independent points and6 original times; they remain source/value nonpasses and require actual data/stability for a physical bound',
 NEXT_OPERAND='use these consumed source/value errors and the actual corner/outer equations to target justified corrections; retain independent incoming and time-face data'))
print('ACTUAL_EVENT_CHILD_ORIGINAL_CHECKS_SAVED',pin(O/'result.json'),flush=True)
