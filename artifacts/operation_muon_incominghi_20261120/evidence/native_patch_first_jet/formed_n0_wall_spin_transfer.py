from pathlib import Path
import sys,json,numpy as np
from scipy.linalg import null_space
p=Path(__file__).resolve().parents[1];sys.path.insert(0,str(p))
from source_retained_magnetic import wall_data
a=np.load(p/'native_n0_coupled_static.npz');K=a['K84'];L=a['lift84x20'];J=a['boundary20'];D=a['Dirichlet_trial_return20']
raw=np.load(p/'incoming_history.npz')['hi_raw_fields'];w=wall_data(raw);h=raw[260:264];Q=w['charge'];q=Q/np.linalg.norm(Q);n=w['lapse'];r=w['R4']
ops=np.load(p/'incoming_spin_operators.npz');H=ops['H_coordinate_time'][-1,:6,:6]
cur=np.load(p/'independent_review/native_spin_odd_current.npz');rho=cur['incoming_density_difference6'];y=ops['family_yukawa'][1];v=[]
for s in np.eye(4):
 c=s[:2]+1j*s[2:];Y=y*np.kron(c[:,None],np.eye(2));v.append(np.block([[np.zeros((4,4)),Y],[Y.conj().T,np.zeros((2,2))]]))
dH=np.array(v)*n
g=np.r_[n/r*cur['incoming_spin_odd_internal_spatial3x4'].ravel(),np.einsum('aij,ji->a',dH,rho).real]
pauli=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex); Gens=np.zeros((4,6,6),complex); alpha=np.zeros((3,6,6),complex)
for k in range(3):
 Gens[k,:4,:4]=-1j*np.kron(pauli[k]/2,np.eye(2))/np.sqrt(2); alpha[k,:4,:4]=-np.kron(np.eye(2),pauli[k]); alpha[k,4:,4:]=pauli[k]
Gens[3]=-1j*np.diag([-.5]*4+[-1.]*2)/np.sqrt(10/3)
gaugeV=(-1j*n/r*np.einsum('aij,kjl->akil',alpha,Gens)).reshape(12,6,6)
pair=np.load(p/'independent_review/n0_spin_pair_audit.npz')['incoming_approximate_n0_spin_pair'][:6]
def tracked_gap(Hmat):
 eig,U=np.linalg.eigh(Hmat)
 idx=np.argmax(abs(pair.conj().T@U)**2,axis=1)
 assert len(set(idx))==2
 return eig[idx[1]]-eig[idx[0]]
A=D[4:,4:]; sv=np.linalg.svd(A,compute_uv=False)
records={}
for key,e0 in [('central',[0,0,0,1]),('H_aligned',q)]:
 e=np.zeros(16);e[8:12]=e0
 V=null_space(e[None]);T=e-V@np.linalg.solve(V.T@A@V,V.T@A@e);R=A@T
 z=np.linalg.solve(A,e);chi=e@z;tau=g@z;G=g@T
 op=np.einsum('a,aij->ij',T,np.r_[gaugeV,dH]); FD={str(eps):float((tracked_gap(H+eps*op)-tracked_gap(H-eps*op))/(2*eps)) for eps in [1e-6,1e-7,1e-8]}; assert abs(FD['1e-06']-G)<1e-7; records[key]=dict(finite_difference_eigen_gap=FD,chi=float(chi),held_trace_spin_transfer=float(G),force_spin_transfer=float(tau),held_trace_induced_H_norm=float(np.linalg.norm(T[12:])),held_trace_direct_only=float(g@e),held_trace_Higgs_contact=float(g[12:]@T[12:]),required_exterior_zero=float(-1/chi),full_complement_reaction_norm=float(np.linalg.norm(V.T@R)),rankone_transfer_consistency=float(abs(G*chi-tau)),interior_residual=float(np.linalg.norm((K@L@np.r_[np.zeros(4),T])[a['interior64']])))
np.savez(Path(__file__).with_suffix('.npz'),action_A=A,spin_gap_covector=g)
out=dict(scope='actual incoming-hi frozen n0 conditional static formed-spin-pair differential; wall temporal trace held, all other spatial/scalar complement free under interior action; force and trace comparisons do not assign an actual exterior or physical pole',n0_lapse=float(n),R4=float(r),eigenvalues=np.linalg.eigvalsh(H).tolist(),A_singular_range=[float(sv[-1]),float(sv[0])],spin_gap_covector=g.tolist(),records=records)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
