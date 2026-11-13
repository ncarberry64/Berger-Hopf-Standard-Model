import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
import sys,json,numpy as np
ROOT=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');BASE=Path(__file__).parent;CELL=BASE/'CHILD_CELL_v2';OUT=CELL/'ORIGINAL_ROWS_v1';OUT.mkdir(exist_ok=False)
sys.path[:0]=[str(ROOT/'src')]
from bhsm.interface.retained_response.finite_time_response import write_npz

def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
record=json.loads((CELL/'core_result.json').read_bytes());meta=load(CELL/'metadata.npz');Dt=meta['time_derivative'];Dr=meta['radial_derivative']
dump(OUT/'BEFORE.json',dict(core_result_sha256=pin(CELL/'core_result.json'),equation='reconstruct original T Phi_t+R Phi_r+K Phi from saved field polynomial and saved original coefficients; project outgoing with Qout^dagger T^-1, source includes inverse-time vertex',no_solve_or_callback_replayed=True))
archives={};reports={}
for filename,receipt in record['archives'].items():
 if filename=='metadata.npz':continue
 a=load(CELL/filename);prefix=filename.removesuffix('.npz')+'_';H=a[prefix+'response'];X=a[prefix+'response_source'];d=H.shape[-2];nt,nr=H.shape[:2];half=d//2
 T,R,K=(a[prefix+'original_coefficient_'+k] for k in ('time','radial','body'))
 Tx,Rx,Kx=(a[prefix+'original_coefficient_'+k+'_source'] for k in ('time','radial','body'))
 Ht=np.einsum('ij,jrab->irab',Dt,H);Hr=np.einsum('rs,isab->irab',Dr,H)
 Xt=np.einsum('ij,xjrab->xirab',Dt,X);Xr=np.einsum('rs,xisab->xirab',Dr,X)
 L=T@Ht+R@Hr+K@H;Lx=Tx@Ht[None]+Rx@Hr[None]+Kx@H[None]+T[None]@Xt+R[None]@Xr+K[None]@X
 TI=np.linalg.inv(T);TIx=-TI[None]@Tx@TI[None]
 inner=a[prefix+'incoming_inner_basis'];outer=a[prefix+'incoming_outer_basis']
 birth=[];birthx=[];incoming=[];incomingx=[];outgoing=[];outgoingx=[];held=[];heldx=[]
 for r in range(nr):
  E=np.zeros((d,H.shape[-1]),complex);E[:,r*d:(r+1)*d]=np.eye(d);birth.append(H[0,r]-E);birthx.append(X[:,0,r])
 for i in range(1,nt):
  for r,Qin,Qout,face in ((0,inner,outer,0),(nr-1,outer,inner,1)):
   E=np.zeros((half,H.shape[-1]),complex);j=(nr+i-1)*d+face*half;E[:,j:j+half]=np.eye(half)
   incoming.append(Qin.conj().T@H[i,r]-E);incomingx.append(Qin.conj().T@X[:,i,r])
   outgoing.append(Qout.conj().T@TI[i,r]@L[i,r]);outgoingx.append(Qout.conj().T@(TI[i,r]@Lx[:,i,r]+TIx[:,i,r]@L[i,r]))
   held.append(Qin.conj().T@TI[i,r]@L[i,r]);heldx.append(Qin.conj().T@(TI[i,r]@Lx[:,i,r]+TIx[:,i,r]@L[i,r]))
 arrays=dict(original_full_D5_rows=L,original_full_D5_source_rows=Lx,
  original_birth_trace_rows=np.array(birth),original_birth_trace_source_rows=np.array(birthx),
  original_incoming_characteristic_trace_rows=np.array(incoming),original_incoming_characteristic_trace_source_rows=np.array(incomingx),
  original_outgoing_evolution_PDE_rows=np.array(outgoing),original_outgoing_evolution_PDE_source_rows=np.array(outgoingx),
  retained_incoming_evolution_PDE_rows=np.array(held),retained_incoming_evolution_PDE_source_rows=np.array(heldx))
 path=OUT/filename;write_npz(path,arrays);archives[filename]=dict(sha256=pin(path),bytes=path.stat().st_size)
 maximum=lambda a:float(np.max(abs(np.asarray(a))))
 reports[prefix[:-1]]=dict(birth_trace_max=maximum(birth),birth_trace_source_max=maximum(birthx),incoming_trace_max=maximum(incoming),incoming_trace_source_max=maximum(incomingx),solved_interior_original_PDE_max=maximum(L[1:,1:-1]),solved_interior_original_PDE_source_max=maximum(Lx[:,1:,1:-1]),solved_outgoing_evolution_PDE_max=maximum(outgoing),solved_outgoing_evolution_PDE_source_max=maximum(outgoingx),retained_incoming_evolution_PDE_max=maximum(held),retained_incoming_evolution_PDE_source_max=maximum(heldx),full_original_PDE_max=maximum(L),full_original_PDE_source_max=maximum(Lx))
(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
dump(OUT/'result.json',dict(core_result_sha256=pin(CELL/'core_result.json'),archives=archives,blocks=reports,physical_data_selected=False,physical_admission=False,physical_guard=2e-10,norm='maxabs original coordinate component over all stated nodal unit-data columns; outgoing covectors explicitly T^-1; no continuum or physical-data bound'))
summary={k:max(v[k] for v in reports.values()) for k in next(iter(reports.values()))}
print(json.dumps(dict(stage='CHILD_ORIGINAL_NODE_ROW_LOCALIZATION_SAVED',sha256=pin(OUT/'result.json'),summary=summary)),flush=True)
