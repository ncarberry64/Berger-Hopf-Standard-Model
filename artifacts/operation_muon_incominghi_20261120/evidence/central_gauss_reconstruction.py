"""Reconstructed original radial central-U1 Maxwell block, not full photon."""
import numpy as np,json,ast,hashlib
from pathlib import Path
from scipy.special import eval_jacobi,gammaln
p=Path(__file__).parent
ns={'__file__':str(p/'exact_radial_known_blocks.py')};exec((p/'exact_radial_known_blocks.py').read_text().split('rec=[]')[0],ns)
cf=ns['cf'];old=ns['old']['coeff'];wall=np.pi/2;alpha=(np.sqrt(45)-3)/2;normalization=.0003208119454588855
f=np.load(p/'reconstructed_radial_frame.npz');ref=np.zeros((2,268));ref[:,:98]=f['reference_states'];projection=f['projection'];norm=float(f['norm']);dw=float(f['wall'])
def radial(rho):
 x=rho/wall;bb=[];dd=[]
 for j in range(2):
  a=2.;b=4+2*alpha;ln=gammaln(j+a+1)+gammaln(j+b+1)-gammaln(j+1)-gammaln(j+a+b+1)-np.log(2*j+a+b+1);v=np.exp(-ln/2)*eval_jacobi(j,a,b,2*x-1);dv=np.exp(-ln/2)*(j+a+b+1)/wall*eval_jacobi(j-1,a+1,b+1,2*x-1) if j else np.zeros_like(x)
  bb.append(x**alpha*(1-x)*v);dd.append((alpha*x**(alpha-1)*(1-x)-x**alpha)/wall*v+x**alpha*(1-x)*dv)
 b0=np.column_stack(bb);d0=np.column_stack(dd);bl=x**alpha;dl=alpha*x**(alpha-1)/wall
 c0=old(ref[0],rho);c1=old(ref[1],rho)
 comp=(c0[:,5]-c1[:,5]-b0@projection-dw*bl)/norm;dc=(c0[:,7]-c1[:,7]-d0@projection-dw*dl)/norm
 return np.column_stack([b0,comp,bl]),np.column_stack([d0,dc,dl])
text=(p/'source_retained_magnetic.py').read_text();tree=ast.parse(text);owned={'np':np,'RADIUS0':(343./5.)**(1/6),'M':np.sqrt(8)*np.c_[np.eye(3),np.zeros(3)]}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='wall_data'],type_ignores=[]),'wall','exec'),owned)
FRAME=np.array([[[0,0,0,1],[0,0,1,0],[0,-1,0,0],[-1,0,0,0]],[[0,0,1,0],[0,0,0,-1],[-1,0,0,0],[0,1,0,0]],[[0,1,0,0],[-1,0,0,0],[0,0,0,1],[0,0,-1,0]]],float)
eps=np.zeros((3,3,3))
for i,j,k in [(0,1,2),(1,2,0),(2,0,1)]:eps[i,j,k]=1;eps[i,k,j]=-1
# curvature maps for field5 x harmonic4, all real, no central commutators.
V=np.zeros((40,20));R=V.copy();T=V.copy();I=np.eye(4)
R[:4,:4]=-I;T[:4,4:8]=I
for i in range(3):
 V[4+4*i:8+4*i,:4]=-FRAME[i].T;T[4+4*i:8+4*i,8+4*i:12+4*i]=I
 V[16+4*i:20+4*i,4:8]=-FRAME[i].T;R[16+4*i:20+4*i,8+4*i:12+4*i]=I
 V[28+4*i:32+4*i,8+4*i:12+4*i]=2*I
 for j,k in np.argwhere(eps[i]):V[28+4*i:32+4*i,8+4*k:12+4*k]+=eps[i,j,k]*FRAME[j].T
ids=np.arange(80).reshape(4,5,4);yy=ids[:,0].ravel();zz=ids[:,1:].ravel()
def weighted(C,c):
 e,r,d,k,sh=c[:5];X=C[:4];Ft=C[4:16];Fr=C[16:28];B=C[28:];F=Ft-sh*Fr
 return np.vstack([k*X,e*F,-e*sh*F-r*Fr,-d*B])
def form(raw,order=192):
 x,w=np.polynomial.legendre.leggauss(order);rho=(x+1)*wall/2;w*=wall/2;bb,dd=radial(rho);cc=cf(raw,rho);K=np.zeros((80,80));B=K.copy();M=K.copy()
 for b,d,c,weight in zip(bb,dd,cc,w*normalization):
  Q=np.hstack([b[j]*V+d[j]*R for j in range(4)]);Qt=np.hstack([b[j]*T for j in range(4)]);K+=weight*Q.T@weighted(Q,c);B+=weight*Q.T@weighted(Qt,c);M+=weight*Qt.T@weighted(Qt,c)
 return K,B,M
records=[];arrays={}
for side in ['incoming','outgoing']:
 history=np.load(p/(side+'_history.npz'))
 for label in ['lo','q000','q001','q002','q003','hi']:
  raw=history[label+'_raw_fields'];rate=history[label+'_raw_coordinate_time_derivative'];K,B,M=form(raw);d=owned['wall_data'](raw);dt=owned['wall_data'](raw.astype(complex)+1j*1e-20*rate);radius=float(d['R4']);rd=dt['R4'].imag/1e-20;s=history[label+'_H_selected_charge_coefficients'][3];sd=history[label+'_H_selected_charge_coordinate_rate'][3]
  wave=np.zeros((4,5,4,3))
  for i,j,k in np.ndindex(3,3,3):wave[3,2+i,3-j,k]+=eps[i,j,k]/4
  W=wave.reshape(80,3)*radius**2*s;Wd=wave.reshape(80,3)*(2*radius*rd*s+radius**2*sd)
  F=K@W+B@Wd;Fd=B@W;H=B.T@W+M@Wd;Hd=M@W
  A=K[np.ix_(yy,yy)];C=K[np.ix_(yy,zz)];D=B[np.ix_(yy,zz)];rhs=np.c_[C,D,F[yy],Fd[yy]];sol=np.linalg.solve(A,rhs);Y,Z,load=sol[:,:64],sol[:,64:128],sol[:,128:]
  Mr=M[np.ix_(zz,zz)]-D.T@Z;fr=np.c_[F[zz],Fd[zz]]-C.T@load;hr=np.c_[H[zz],Hd[zz]]-D.T@load
  eig=np.linalg.eigvalsh((Mr+Mr.T)/2);back=np.linalg.norm(A@sol-rhs,np.inf)/(np.linalg.norm(A,np.inf)*np.linalg.norm(sol,np.inf)+np.linalg.norm(rhs,np.inf))
  # Independent documented central Gauss rate-source identity, all radial columns.
  check=np.zeros((16,3));xm,wm=np.polynomial.legendre.leggauss(192);rho=(xm+1)*wall/2;wm*=wall/2;bas,_=radial(rho);e=cf(raw,rho)[:,0];integ=normalization*bas.T@(wm*e*bas[:,3])
  for j,k in np.ndindex(4,3):check[j*4+3-k,k]=-s*radius**2/2*integ[j]
  error=float(np.max(abs(Fd[yy]-check)))
  prefix=side+'_'+label
  for key,val in dict(K=K,B=B,M=M,Mred=Mr,F=F,Fdot=Fd,H=H,Hdot=Hd,fred=fr,hred=hr).items():arrays[prefix+'_'+key]=val
  records.append(dict(side=side,label=label,Gauss_absolute_residual=float(np.max(abs(A@sol-rhs))),Gauss_backward_error=float(back),central_source_identity_error=error,central_turnon_max=float(np.max(abs(Fd[yy]))),reduced_eigenvalues=eig[:10].tolist(),source_momentum_shift_max=float(np.max(abs(D.T@load)))))
np.savez(p/'central_gauss_reconstruction.npz',**arrays)
out=dict(scope='all4 reconstructed radial columns, central U1 n1 Maxwell component only; algebraic16At elimination not physical boundary quotient',records=records,full_causal_response=False,physical_photon_projection=False,physical_moment=None)
(p/'CENTRAL_GAUSS_RECONSTRUCTION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
