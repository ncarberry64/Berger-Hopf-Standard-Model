from pathlib import Path
import numpy as np,json
from source_action_magnetic_kernel import FieldJet,curvature,curvature_first,curvature_second
from source_integrated_source import _basis_jet,flatten_curvature,weighted_curvature
import source_build_higgs_response as hg
p=Path(__file__).parent;ns={'__file__':str(p/'central_gauss_reconstruction.py')};exec((p/'central_gauss_reconstruction.py').read_text().split('records=[]')[0],ns)
raw=np.load(p/'incoming_history.npz')['hi_raw_fields'];records=[]
def maps0(points):
 n=len(points);H=np.zeros((n,4,20));H[:,:,:4]=np.eye(4);D=np.zeros((n,4,4,20));G=np.zeros((n,4,4,20));G[:,:,:,4:]=np.eye(16).reshape(4,4,16);Rate=D.copy();Rate[:,0]=H;return H,D,G,Rate
hg.maps=maps0;hblock=hg.higgs_blocks(raw);KH=hblock['K']
for order in (192,384):
 x,w=np.polynomial.legendre.leggauss(order);rho=(x+1)*ns['wall']/2;w*=ns['wall']/2*ns['normalization'];bas,dr=ns['radial'](rho);cc=ns['cf'](raw,rho)
 g=np.einsum('rj,jfc->rfc',bas,raw[100:180].reshape(4,5,4));gt=np.einsum('rj,jfc->rfc',bas,raw[180:260].reshape(4,5,4));gr=np.einsum('rj,jfc->rfc',dr,raw[100:180].reshape(4,5,4));MM=np.sqrt(8)*np.c_[np.eye(3),np.zeros(3)]
 g[:,2:]+=(cc[:,5]-1)[:,None,None]*MM;gt[:,2:]+=cc[:,6,None,None]*MM;gr[:,2:]+=cc[:,7,None,None]*MM
 base=FieldJet(g[:,None],gt[:,None],gr[:,None],np.zeros((order,1,3,5,4)))
 def bjet(kind='value'):
  z=_basis_jet(kind);return FieldJet(*(np.broadcast_to(getattr(z,k),(order,)+getattr(z,k).shape).copy() for k in ('value','time','radial','angular')))
 V=flatten_curvature(curvature_first(base,bjet())).real
 R=flatten_curvature(curvature_first(base,bjet('radial'))).real
 T=flatten_curvature(curvature_first(base,bjet('time'))).real
 # radial basis x coefficient20
 Q=np.concatenate([bas[:,j,None,None]*V+dr[:,j,None,None]*R for j in range(4)],axis=1)
 # weighted_curvature expects density broadcast along directions
 QT=np.concatenate([bas[:,j,None,None]*T for j in range(4)],axis=1)
 WT=weighted_curvature(QT,cc[:,None,:5]).real
 MB=np.einsum('r,rai,rbi->ab',w,QT,WT);BB=np.einsum('r,rai,rbi->ab',w,Q,WT)
 W=weighted_curvature(Q,cc[:,None,:5]).real
 K=np.einsum('r,rai,rbi->ab',w,Q,W)
 I=np.eye(20).reshape(20,5,4);zz=np.zeros_like(I);u=FieldJet(I[:,None],zz[:,None],zz[:,None],np.zeros((20,1,3,5,4)));v=FieldJet(I[None],zz[None],zz[None],np.zeros((1,20,3,5,4)))
 C=flatten_curvature(curvature_second(u,v)).real;F=flatten_curvature(curvature(base))[:,0].real;WF=weighted_curvature(F,cc[:,:5]).real;contact=np.einsum('ri,abi->rab',WF,C)
 K+=np.einsum('r,rj,rk,rab->jakb',w,bas,bas,contact).reshape(80,80)
 full=np.zeros((84,84));full[:80,:80]=K;wall=np.arange(80).reshape(4,5,4)[3,[0,2,3,4]].ravel();S=np.zeros((20,84));S[:4,80:]=np.eye(4);S[4+np.arange(16),wall]=1;full+=S.T@KH@S
 mass=np.zeros((84,84));mass[:80,:80]=MB;mass+=S.T@hblock['M']@S;bmix=np.zeros((84,84));bmix[:80,:80]=BB;bmix+=S.T@hblock['B']@S
 b=np.r_[wall,np.arange(80,84)];ii=np.setdiff1d(np.arange(84),b);A=full[np.ix_(ii,ii)];Cib=full[np.ix_(ii,b)];U,sv,Vt=np.linalg.svd(A);tol=sv[0]*1e-11;keep=sv>tol;Ai=(Vt[keep].T/sv[keep])@U[:,keep].T;Y=-Ai@Cib;Lift=np.zeros((84,20));Lift[b]=np.eye(20);Lift[ii]=Y;res=A@Y+Cib;D=Lift.T@full@Lift
 records.append(dict(order=order,interior_rank=int(keep.sum()),interior_dimension=len(ii),singular_values=sv.tolist(),interior_trace_compatibility_residual=float(np.linalg.norm(res)),interior_trace_rhs_norm=float(np.linalg.norm(Cib)),null_to_wall_norm=float(np.linalg.norm(U[:,~keep].T@Cib)),reduced_symmetry=float(np.linalg.norm(D-D.T)),reduced_eigenvalues=np.linalg.eigvalsh(D).tolist(),central_bulk_replay=float(np.max(abs(K[np.ix_([11,31,51,71],[11,31,51,71])]-np.load(p/'native_n0_central_radial_return.npz')['K4'])))))
 np.savez(p/'native_n0_coupled_static.npz',K80=K,B80=BB,M80=MB,KH20=KH,K84=full,B84=bmix,M84=mass,interior64=ii,boundary20=b,lift84x20=Lift,Dirichlet_trial_return20=D,interior_singular_values=sv)
out=dict(scope='incoming hi static n0 Maxwell plus Higgs action on retained four radial trial profiles; formal interior least-norm solve audited for compatibility; no exterior/free-wall or physical moment imposed',records=records);(p/'native_n0_coupled_static.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
