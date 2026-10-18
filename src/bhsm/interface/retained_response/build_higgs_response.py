"""Original Higgs n1 wall response on exported provisional fields.

No physical collider/native/exterior solution is asserted. Maxwell coefficients
and saved causal maps are reused. Scalar initials and all wall ports are free.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
import sys,json,hashlib,io,zipfile
import numpy as np
from scipy.linalg import solve,lu_factor,lu_solve
from numpy.polynomial import Polynomial

ROOT=Path(__file__).resolve().parents[4]/'artifacts/muon_retained_response_20261018'
from .retained_magnetic_application import wall_data,FRAME,rule8,rule24

LAM=1.1663774240217167e-5*125.11**2/np.sqrt(2)
NU2=4.0
C_ORBIT=1/(2*np.pi**2)


def maxabs(a):return float(np.max(np.abs(a))) if np.size(a) else 0.
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save_npz(path,data):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp')
 with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for k,v in sorted(data.items()):
   b=io.BytesIO();np.lib.format.write_array(b,np.asarray(v),allow_pickle=False)
   n=zipfile.ZipInfo(k+'.npy',(1980,1,1,0,0,0));n.compress_type=zipfile.ZIP_DEFLATED;z.writestr(n,b.getvalue())
 tmp.replace(p)

def generators():
 pauli=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
 gc=np.concatenate((-1j*pauli/(2*np.sqrt(2)),(-.5j*np.eye(2)/np.sqrt(10/3))[None]))
 return gc,np.array([np.block([[a.real,-a.imag],[a.imag,a.real]]) for a in gc])


def maps(points):
 """q=(Hreal4*n1harm4, wallfields4*internal4*n1harm4)."""
 p=len(points);Y=2*points;DY=2*np.einsum('aij,pj->pai',FRAME,points)
 H=np.zeros((p,4,80));dH=np.zeros((p,4,4,80));G=np.zeros((p,4,4,80))
 for i in range(4):
  for h in range(4):
   H[:,i,i*4+h]=Y[:,h]
   dH[:,1:,i,i*4+h]=DY[:,:,h]
 for f,c,h in np.ndindex(4,4,4):G[:,f,c,16+(f*4+c)*4+h]=Y[:,h]
 rate=np.zeros_like(dH);rate[:,0]=H
 return H,dH,G,rate


def higgs_blocks(raw,rawdot=None,lam=LAM,nu2=NU2,rule=rule8):
 """Hessian of one signed original scalar action, in physical time."""
 d=wall_data(raw);h=raw[260:264];hd=raw[264:268]
 _,gr=generators();omega=np.einsum('fc,cij->fij',d['connection'][[0,2,3,4]],gr)
 weights=np.array([d['R4']**3/d['lapse']]+[-d['lapse']*d['R4']]*3)
 wv=d['lapse']*d['R4']**3
 DH=np.einsum('fij,j->fi',omega,h);DH[0]+=hd
 points,w=rule();V,D,G,Rate=maps(points)
 J=D+np.einsum('fij,pjk->pfik',omega,V)+np.einsum('pfck,cij,j->pfik',G,gr,h)
 # DH dot delta2(A H) includes both gauge/scalar placements.
 cross=np.einsum('p,f,fi,pfck,cij,pjl->kl',w,weights,DH,G,gr,V)
 pot=4*lam*((h@h-nu2)*np.eye(4)+2*np.outer(h,h))
 M=2*C_ORBIT*np.einsum('p,f,pfik,pfil->kl',w,weights,Rate,Rate)
 B=2*C_ORBIT*np.einsum('p,f,pfik,pfil->kl',w,weights,J,Rate)
 K=2*C_ORBIT*(np.einsum('p,f,pfik,pfil->kl',w,weights,J,J)+cross+cross.T)-C_ORBIT*wv*np.einsum('p,pik,ij,pjl->kl',w,V,pot,V)
 # Homogeneous first covectors used to check moving neutral generator contacts.
 gauge_grad=np.empty((4,4));scalar_grad=-C_ORBIT*wv*4*lam*(h@h-nu2)*h
 scalar_momentum=2*C_ORBIT*weights[0]*DH[0]
 for f in range(4):
  gauge_grad[f]=2*C_ORBIT*weights[f]*np.einsum('i,cij,j->c',DH[f],gr,h)
  scalar_grad+=2*C_ORBIT*weights[f]*omega[f].T@DH[f]
 return dict(M=M,B=B,K=K,wall=d,weights=weights,wv=wv,base_H=h.copy(),base_Hdot=hd.copy(),
             gauge_grad=gauge_grad,scalar_grad=scalar_grad,scalar_momentum=scalar_momentum,
             symmetry=max(maxabs(M-M.T),maxabs(K-K.T)))


def literal_action(raw,q,qd,lam=LAM,nu2=NU2,rule=rule24):
 """Independent complex-doublet evaluation of the original scalar density."""
 d=wall_data(raw);x,w=rule();Y=2*x;DY=2*np.einsum('aij,pj->pai',FRAME,x)
 hh=raw[260:264][None]+np.einsum('ph,ih->pi',Y,q[:16].reshape(4,4))
 ht=raw[264:268][None]+np.einsum('ph,ih->pi',Y,qd[:16].reshape(4,4))
 deriv=np.einsum('pah,ih->pai',DY,q[:16].reshape(4,4))
 H=hh[:,:2]+1j*hh[:,2:];Ht=ht[:,:2]+1j*ht[:,2:]
 Hs=deriv[:,:,:2]+1j*deriv[:,:,2:]
 gg=d['connection'][[0,2,3,4]][None]+np.einsum('ph,fch->pfc',Y,q[16:].reshape(4,4,4))
 gc,_=generators();O=np.einsum('pfc,cij->pfij',gg,gc)
 Dt=Ht+np.einsum('pij,pj->pi',O[:,0],H)
 Ds=Hs+np.einsum('paij,pj->pai',O[:,1:],H)
 norm=np.einsum('pi,pi->p',H.conj(),H).real
 vals=d['R4']**3/d['lapse']*np.sum(abs(Dt)**2,axis=1)-d['lapse']*d['R4']*np.sum(abs(Ds)**2,axis=(1,2))-d['lapse']*d['R4']**3*lam*(norm-nu2)**2
 return float(C_ORBIT*w@vals)


def gauss_table():
 c,b=np.polynomial.legendre.leggauss(4);c=(c+1)/2;b=b/2;A=np.empty((4,4))
 for j in range(4):
  p=Polynomial.fromroots(np.delete(c,j));p=p/p(c[j]);ii=p.integ();A[:,j]=ii(c)-ii(0)
 return c,b,A


def prepare(side,inputs,maxwell=None,*,nu2=NU2,lam=LAM):
 meta=json.loads((inputs/'metadata.json').read_text());T=meta['sides'][side]['duration']
 labels=['lo','q000','q001','q002','q003','hi']
 s0=dict(np.load(inputs/f'{side}_lo.npz'));b0=higgs_blocks(s0['raw'],nu2=nu2,lam=lam)
 mass=float(b0['M'][0,0]);J=np.eye(80);J[:16,:16]/=np.sqrt(mass);J[16:32,16:32]/=T
 records={};nd=134;n=32
 for lab in labels:
  ss=dict(np.load(inputs/f'{side}_{lab}.npz'));tau=meta['sides'][side]['samples'][lab]['tau'];h=higgs_blocks(ss['raw'],nu2=nu2,lam=lam)
  M=J.T@h['M']@J;B=T*J.T@h['B']@J;K=T*T*J.T@h['K']@J
  G=np.zeros((64,nd));Gd=np.zeros_like(G);G[:,:64]=np.eye(64);G[:,64:128]=tau*np.eye(64);Gd[:,64:128]=np.eye(64)
  # Same exact source traces used by the saved Maxwell response.
  W=ss['Wg'];Wd=T*ss['Wgdot'];G[:,128:131]=W;G[:,131:]=tau*W;Gd[:,128:131]=Wd;Gd[:,131:]=W+tau*Wd
  mx,bx,kx=M[:16,:16],B[:16,:16],K[:16,:16]
  hh=B[16:,:16].T@G+M[:16,16:]@Gd
  ff=K[:16,16:]@G+B[:16,16:]@Gd
  sol=solve(mx,np.c_[bx.T,np.eye(16),hh],assume_a='pos');neg=-sol[:,:16];iv=sol[:,16:32];src=-sol[:,32:]
  F=np.block([[neg,iv],[kx+bx@neg,bx@iv]]);force=np.vstack((src,ff+bx@src))
  records[lab]=dict(M=M,B=B,K=K,G=G,Gd=Gd,F=F,force=force,original=h)
 return dict(records=records,T=T,J=J,scalar_whitening=np.sqrt(mass),side=side)


def solve_response(data):
 c,b,A=gauss_table();n=32;nd=134;N=n+nd;pts=[data['records'][f'q{i:03d}'] for i in range(4)]
 mat=np.zeros((4*n,4*n));rhs=np.zeros((4*n,N))
 for i in range(4):
  rhs[i*n:(i+1)*n,:n]=np.eye(n)
  for j in range(4):
   mat[i*n:(i+1)*n,j*n:(j+1)*n]=-A[i,j]*pts[j]['F'];rhs[i*n:(i+1)*n,n:]+=A[i,j]*pts[j]['force']
  mat[i*n:(i+1)*n,i*n:(i+1)*n]+=np.eye(n)
 z=solve(mat,rhs).reshape(4,n,N);rates=np.array([r['F']@zz+np.c_[np.zeros((n,n)),r['force']] for r,zz in zip(pts,z)])
 initial=np.c_[np.eye(n),np.zeros((n,nd))];final=initial+np.einsum('i,ijk->jk',b,rates)
 responses={};Wwall=np.zeros((nd,N));recs={}
 for i,lab in enumerate(['lo','q000','q001','q002','q003','hi']):
  r=data['records'][lab];zz=initial if lab=='lo' else final if lab=='hi' else z[i-1]
  zd=r['F']@zz+np.c_[np.zeros((n,n)),r['force']]
  q=np.vstack((zz[:16],np.c_[np.zeros((64,n)),r['G']]));qd=np.vstack((zd[:16],np.c_[np.zeros((64,n)),r['Gd']]))
  grad=r['K']@q+r['B']@qd;mom=r['M']@qd+r['B'].T@q
  recs[lab]=dict(q=q,qd=qd,grad=grad,mom=mom)
  if lab.startswith('q'):Wwall+=b[i-1]*(r['G'].T@grad[16:]+r['Gd'].T@mom[16:])
 endpoint=data['records']['hi']['G'].T@recs['hi']['mom'][16:]-data['records']['lo']['G'].T@recs['lo']['mom'][16:]
 Jsym=np.block([[np.zeros((16,16)),np.eye(16)],[-np.eye(16),np.zeros((16,16))]])
 FF=final[:,n:];green=Wwall[:,n:]-Wwall[:,n:].T+FF.T@Jsym@FF
 return dict(stages=z,rates=rates,initial=initial,final=final,wall=Wwall,wall_endpoint=endpoint,wall_euler=Wwall-endpoint,recs=recs,
             stage_residual=maxabs(mat@z.reshape(4*n,N)-rhs),green=maxabs(green),symplectic=maxabs(final[:,:n].T@Jsym@final[:,:n]-Jsym))


def direct_original(data):
 """Independently assemble the original scalar momentum and Euler stage equations."""
 c,b,A=gauss_table();n=16;ni=32;nd=134;N=ni+nd;mat=np.zeros((4*2*n,4*2*n));rhs=np.zeros((4*2*n,N));pts=[data['records'][f'q{i:03d}'] for i in range(4)]
 for i,r in enumerate(pts):
  ix=slice(i*32,i*32+16);ip=slice(i*32+16,(i+1)*32);ci=ix;cv=ip
  mat[ix,ci]=np.eye(n);rhs[ix,:n]=np.eye(n)
  mat[ip,ci]=r['B'][:n,:n].T;mat[ip,cv]=r['M'][:n,:n];rhs[ip,n:ni]=np.eye(n)
  rhs[ip,ni:]=-r['B'][n:,:n].T@r['G']-r['M'][:n,n:]@r['Gd']
  for j,rj in enumerate(pts):
   jx=slice(j*32,j*32+16);jv=slice(j*32+16,(j+1)*32)
   mat[ix,jv]-=A[i,j]*np.eye(n)
   mat[ip,jx]-=A[i,j]*rj['K'][:n,:n];mat[ip,jv]-=A[i,j]*rj['B'][:n,:n]
   rhs[ip,ni:]+=A[i,j]*(rj['K'][:n,n:]@rj['G']+rj['B'][:n,n:]@rj['Gd'])
 uv=solve(mat,rhs).reshape(4,32,N);Z=[];dZ=[]
 for r,z in zip(pts,uv):
  q=np.vstack((z[:n],np.c_[np.zeros((64,32)),r['G']]));qd=np.vstack((z[n:],np.c_[np.zeros((64,32)),r['Gd']]))
  mom=r['M']@qd+r['B'].T@q;grad=r['K']@q+r['B']@qd
  Z.append(np.vstack((z[:n],mom[:n])));dZ.append(np.vstack((z[n:],grad[:n])))
 final=np.c_[np.eye(32),np.zeros((32,134))]+np.einsum('i,ijk->jk',b,np.array(dZ))
 return dict(stages=np.array(Z),final=final,residual=maxabs(mat@uv.reshape(128,N)-rhs))


def charge_derivative(h,dh):
 h=np.asarray(h);dh=np.asarray(dh);a,b,c,d=h;aa,bb,cc,dd=dh;norm=h@h;dn=2*h@dh
 num=np.array([2*(a*b+c*d),2*(a*d-c*b),a*a+c*c-b*b-d*d])
 deriv=np.array([2*(aa*b+a*bb+cc*d+c*dd),2*(aa*d+a*dd-cc*b-c*bb),2*(a*aa+c*cc-b*bb-d*dd)])
 return np.r_[-np.sqrt(2)*(deriv/norm-num*dn/norm**2),0.]


def original_gauge_checks(raw,blocks):
 """Exact n1 gauge directions and residual contacts in original Higgs action."""
 d=blocks['wall'];H=raw[260:264];Hd=raw[264:268];_,gr=generators();x,w=rule8();Y=2*x;DY=2*np.einsum('aij,pj->pai',FRAME,x)
 eps=np.zeros((3,3,3));eps[0,1,2]=eps[1,2,0]=eps[2,0,1]=1;eps[0,2,1]=eps[2,1,0]=eps[1,0,2]=-1
 A=d['connection'][[0,2,3,4]];basegrad=blocks['gauge_grad'];hgrad=blocks['scalar_grad'];hp=blocks['scalar_momentum'];K,B,M=blocks['K'],blocks['B'],blocks['M']
 # All 80 value tests and 16 scalar-rate tests.
 err=0.;firstmax=0.;same=0.
 for c,harm in np.ndindex(4,4):
  alp=np.eye(4)[c];op=gr[c];t=np.zeros(80);td=np.zeros(80)
  t[:16].reshape(4,4)[:,harm]=-op@H;td[:16].reshape(4,4)[:,harm]=-op@Hd
  tg=t[16:].reshape(4,4,4)
  for f in range(4):
   if c<3:tg[f,:3,harm]=np.cross(A[f,:3],alp[:3])/np.sqrt(2)
   if f>0:
    # E_f Y_harm=sum_l FRAME[f-1,harm,l]Y_l
    tg[f,c,:]+=FRAME[f-1,harm,:]
  first=np.r_[t@K+td@B.T,(t@B+td@M)[:16]];contact=np.zeros(96)
  # Products of equal harmonics have unit Haar pairing.
  for ri in range(4):
   contact[ri*4+harm]=hgrad@(-op[:,ri]);contact[80+ri*4+harm]=hp@(-op[:,ri])
  for f,ci in np.ndindex(4,4):
   com=np.zeros(4)
   if ci<3 and c<3:com[:3]=np.cross(np.eye(3)[ci],np.eye(3)[c])/np.sqrt(2)
   contact[16+(f*4+ci)*4+harm]=basegrad[f]@com
  err=max(err,maxabs(first+contact));firstmax=max(firstmax,maxabs(first))
 return dict(off_shell_gauge_identity=err,uncompleted_gauge_test_max=firstmax)


def aligned_checks(raw,blocks,W):
 """Do not assign the neutral line a Higgs holding force by freezing Q_H."""
 x,w=rule8();Y=2*x;H=raw[260:264];A=blocks['wall'];_,gr=generators();s=A['charge'];norm=s@s
 Wg=W[16:] if W.shape[0]==80 else W
 Wvalues=np.einsum('ph,fcha->pfca',Y,Wg.reshape(4,4,4,3));wave=np.einsum('pfca,c->pfa',Wvalues,s)/norm
 cross=blocks['K'][:16,16:]@Wg
 contact=np.zeros((16,3))
 for r,harm in np.ndindex(4,4):
  ds=charge_derivative(H,np.eye(4)[r])
  contact[r*4+harm]=np.einsum('p,fc,c,pfa,p->a',w,blocks['gauge_grad'],ds,wave,Y[:,harm])
 return dict(neutral_generator_annihilation=maxabs(np.einsum('c,cij,j->i',s,gr,H)),
             neutral_gauge_self_hessian=maxabs(Wg.T@blocks['K'][16:,16:]@Wg),
             fixed_axis_scalar_cross=maxabs(cross),moving_axis_gradient_contact=maxabs(contact),
             complete_aligned_Higgs_cross=maxabs(cross+contact),fixed_axis_cross_array=cross,contact_array=contact)


def combine_saved(maxwell,scalar):
 """Add only the intrinsic Higgs wall action; do not impose a wall law."""
 nm,nh,nd=408,32,134;N=nm+nh+nd
 final=np.zeros((nm+nh,N));final[:nm,:nm]=maxwell['initial_to_final'];final[:nm,nm+nh:]=maxwell['trace_and_probe_to_final']
 final[nm:,nm:nm+nh]=scalar['final'][:,:nh];final[nm:,nm+nh:]=scalar['final'][:,nh:]
 wall=np.zeros((nd,N));wall[:,:nm]=maxwell['weak_wall_from_initial'];wall[:,nm:nm+nh]=scalar['wall'][:,:nh];wall[:,nm+nh:]=maxwell['weak_wall_from_trace_and_probe']+scalar['wall'][:,nh:]
 endpoint=np.zeros_like(wall);endpoint[:,:nm]=maxwell['wall_temporal_endpoint'][:,:nm];endpoint[:,nm+nh:]=maxwell['wall_temporal_endpoint'][:,nm:]+scalar['wall_endpoint'][:,nh:];endpoint[:,nm:nm+nh]=scalar['wall_endpoint'][:,:nh]
 symp=lambda n:np.block([[np.zeros((n,n)),np.eye(n)],[-np.eye(n),np.zeros((n,n))]])
 J=np.zeros((nm+nh,nm+nh));J[:nm,:nm]=symp(204);J[nm:,nm:]=symp(16)
 response=final[:,nm+nh:];green=wall[:,nm+nh:]-wall[:,nm+nh:].T+response.T@J@response
 return dict(final=final,weak_wall=wall,wall_temporal_endpoint=endpoint,wall_euler=wall-endpoint,green=maxabs(green))


def nu2_sensitivity(data,sol):
 """Differentiate the actual inherited nu2 slot, holding other supplied fields fixed.

 This is an explicit parameter partial at nu2=4, not the physical coupled
 energy-scale/background/domain derivative.
 """
 _,b,A=gauss_table();n,nd,N=32,134,166;ns=4;mat=np.zeros((128,128));dmat=np.zeros_like(mat);Fs=[]
 for lab in ['q000','q001','q002','q003']:
  r=data['records'][lab];DK0=np.zeros((80,80));DK0[:16,:16]=4*C_ORBIT*r['original']['wv']*LAM*np.eye(16)
  DK=data['T']**2*data['J'].T@DK0@data['J'];dF=np.zeros((n,n));dF[16:,:16]=DK[:16,:16];Fs.append(dF)
 for i in range(4):
  for j in range(4):
   r=data['records'][f'q{j:03d}'];mat[i*n:(i+1)*n,j*n:(j+1)*n]=-A[i,j]*r['F'];dmat[i*n:(i+1)*n,j*n:(j+1)*n]=-A[i,j]*Fs[j]
  mat[i*n:(i+1)*n,i*n:(i+1)*n]+=np.eye(n)
 dZ=solve(mat,-dmat@sol['stages'].reshape(128,N)).reshape(4,n,N)
 dRates=np.array([f@z+data['records'][f'q{i:03d}']['F']@dz for i,(f,z,dz) in enumerate(zip(Fs,sol['stages'],dZ))])
 dFinal=np.einsum('i,ijk->jk',b,dRates);dWall=np.zeros((nd,N))
 for i in range(4):
  r=data['records'][f'q{i:03d}'];dx=dZ[i,:16];dv=dRates[i,:16]
  grad=r['K'][16:,:16]@dx+r['B'][16:,:16]@dv
  mom=r['B'][:16,16:].T@dx+r['M'][16:,:16]@dv
  dWall+=b[i]*(r['G'].T@grad+r['Gd'].T@mom)
 return dict(final=dFinal,wall=dWall,stages=dZ,implicit_equation_residual=maxabs(mat@dZ.reshape(128,N)+dmat@sol['stages'].reshape(128,N)))
