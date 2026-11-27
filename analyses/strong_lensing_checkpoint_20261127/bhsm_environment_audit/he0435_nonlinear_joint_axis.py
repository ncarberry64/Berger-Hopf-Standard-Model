"""Single-domain axisymmetric nonlinear frozen-R1 solver, independently sourced photometric/star plus kinematic group proxies."""
from pathlib import Path
import argparse,contextlib,io,json,math
from functools import lru_cache
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from scipy.integrate import cumulative_trapezoid,quad
from scipy.interpolate import CubicSpline,RectBivariateSpline
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
 from he0435_joint_field_control import m,positions,names,d1,w1,bg,L,speed,xrad,G
p=Path(__file__).parent
cfg=json.loads((p/'he0435_group_direction.json').read_text())
axis=np.array(cfg['unit_E_N'])
sep=67.1*xrad*d1
b,C,lam=m.b,m.C,bg.LAMBDA
gamma=2*(470/speed)**2
main_mass=m.m
r200=.761

class Obj:
 def __init__(self,kind):
  self.kind=kind
  if kind in ['main','sersic']: self.mt=main_mass
  elif kind=='group': self.mt=gamma*np.pi/2*(r200-.025)
  else: raise ValueError(kind)
  if kind=='sersic':
   core=.0005
   pg=np.r_[0,np.geomspace(1e-9,4.,2400)]
   dx=np.hypot(pg,core)
   def den(r):
    u,n=m.sphere(r/m.a)
    return u*n/r**3
   prof=np.array([den(r) for r in dx])
   norm=np.trapezoid(prof*pg*pg,pg)
   self.norm=norm
   self.rho=CubicSpline(pg,prof/norm,extrapolate=False)
   self.enclosed=CubicSpline(pg,cumulative_trapezoid(prof/norm*pg*pg,pg,initial=0),extrapolate=False)
  RS=np.r_[0,np.geomspace(1e-9,1000,6500)]
  numer=self.grad(RS)
  self.p=CubicSpline(RS, cumulative_trapezoid(numer,RS,initial=0)-np.trapezoid(numer,RS), extrapolate=True)
 def mass(self,r):
  if self.kind=='main': return self.mt*(r/np.hypot(r,m.a))**3
  if self.kind=='sersic': return self.mt*self.enclosed(np.minimum(r,4.))
  return gamma*(r200*np.arctan(r/r200)-.025*np.arctan(r/.025))
 def source(self,r):
  if self.kind=='main':return -3*b*L**2*self.mt*m.a**2/np.hypot(r,m.a)**5
  if self.kind=='sersic': return -b*L**2*self.mt*self.rho(np.minimum(r,4.))
  return -b*L**2*gamma*(1/(r**2+.025**2)-1/(r**2+r200**2))
 def grad(self,r):
  a=np.asarray(r); x=np.where(a>0,a,1.); M=self.mass(x); S=np.sqrt(1+16*b*L**2*M/(lam*C**2*x**3))
  return np.where(a>0,-2*b*L**2*M/(C*x*x*(1+S)),0.)
Astar,Agroup=Obj('main'),Obj('group')

def mesh(lo,hi,n,centers,dens):
 x=np.linspace(lo,hi,40001);u=(x-lo)/(hi-lo)
 for c,s,w in zip(centers,*dens):u+=w/np.pi*(np.arctan((x-c)/s)-np.arctan((lo-c)/s))
 return np.interp(np.linspace(0,u[-1],n),u,x)
def mat(x,order,axis=False):
 n=len(x); q=sp.lil_matrix((n,n))
 for i in range(1,n-1):
  h=x[i]-x[i-1]; H=x[i+1]-x[i]
  q[i,i-1:i+2]=[-H/(h*(h+H)),(H-h)/(h*H),h/(H*(h+H))] if order==1 else [2/(h*(h+H)),-2/(h*H),2/(H*(h+H))]
 if axis and order==2: q[0,0:2]=[-2/x[1]**2,2/x[1]**2]
 return q.tocsr()

def run(N,box,case='joint'):
 r=mesh(0,box,N,[0],[ [.006],[6.] ])
 z=mesh(-box,box,2*N-1,[0,sep],[ [.006,.04],[6.,1.3] ])
 R,Z=np.meshgrid(r,z,indexing='ij')
 shape=R.shape
 rr=np.hypot(R,Z);rg=np.hypot(R,Z-sep)
 ir,iz=sp.eye(len(r),format='csr'),sp.eye(len(z),format='csr')
 r1=mat(r,1,True); r2=mat(r,2,True); z1=mat(z,1); z2=mat(z,2)
 az=sp.kron(ir,z2,format='csr'); ar=sp.kron(r2,iz,format='csr'); ax=sp.kron(r1,z1,format='csr')
 pcoef=sp.diags(np.where(r>0,1/np.where(r>0,r,1),0))@r1
 pcoef=pcoef.tolil();pcoef[0,:]=r2[0,:]
 ap=sp.kron(pcoef.tocsr(),iz,format='csr')
 mask=np.ones(shape,dtype=bool); mask[-1,:]=mask[:,0]=mask[:,-1]=False
 ids=np.flatnonzero(mask.ravel())
 AR,AZ,AP,AX=[X[ids,:].tocsr() for X in [ar,az,ap,ax]]
 QR,QZ,QP,QX=[X[:,ids].tocsr() for X in [AR,AZ,AP,AX]]
 if case=='main':
  u=Astar.p(rr); J=Astar.source(rr); gref=u.copy()
 else:
  u=Astar.p(rr)+Agroup.p(rg); J=Astar.source(rr)+Agroup.source(rg); gref=u.copy()
  # One jointly screened angular-average far field around the total mass centroid.
  # Smooth bulk initial guess fades to its common boundary, never independent output fields.
  com=sep*Agroup.mt/(Astar.mt+Agroup.mt)
  rr0=np.hypot(R,Z-com)
  RS=np.geomspace(.000001,1000,6500)
  M=Astar.mass(RS)+Agroup.mass(RS)
  S=np.sqrt(1+16*b*L**2*M/(lam*C**2*RS**3))
  dg=-2*b*L**2*M/(C*RS**2*(1+S)); inte=cumulative_trapezoid(dg,RS,initial=0); inte-=inte[-1]
  boundary=CubicSpline(RS,inte)(rr0)
  ta=np.clip((np.maximum(R,np.abs(Z))-(.55*box))/(.45*box),0,1)
  mix=ta*ta*(3-2*ta)
  u=u*(1-mix)+mix*boundary
 gauge=u[0,np.argmin(abs(z))]
 u-=gauge
 Uf=u.ravel().copy(); source=J.ravel()[ids]
 scale=np.maximum(1.,abs(source)); target=2e-7
 def sample(u):
  a,d,c,e=[X@u for X in [AR,AZ,AP,AX]]
  residue=C*(a+d+c)-(4/lam)*(a*d+a*c+d*c-e*e)-source
  diagR=C-(4/lam)*(d+c);diagZ=C-(4/lam)*(a+c);diagP=C-(4/lam)*(a+d)
  cross=(4/lam)*e
  ell=min(np.min(diagP),np.min(.5*(diagR+diagZ-np.hypot(diagR-diagZ,2*cross))))
  return residue,ell,(diagR,diagZ,diagP,2*cross)
 def norm(v):return np.max(abs(v)/scale)
 start=sample(Uf)
 trace=[]
 for it in range(45):
  re,ell,der=sample(Uf); err=norm(re)
  trace.append([err,float(ell)])
  if err<target:break
  DR,DZ,DP,DX=der
  Jac=sum(sp.diags(d)@q for d,q in zip([DR,DZ,DP,DX],[QR,QZ,QP,QX]))
  du=spsolve(Jac.tocsc(),-re)
  accepted=False
  for k in range(24):
   step=.5**k; v=Uf.copy();v[ids]+=step*du
   e2,A2,_=sample(v)
   if A2>0 and norm(e2)<err*(1-1e-4*step):
    Uf=v;accepted=True;break
  if not accepted: break
 re,ell,_=sample(Uf)
 out=dict(Nr=N,Nz=len(z),box_Mpc=box,case=case,central_dr_kpc=r[1]*1000,central_dz_kpc=(z[np.searchsorted(z,0)+1]-z[np.searchsorted(z,0)])*1000,iterations=len(trace)-1,converged=bool(norm(re)<target),last_max_scaled_residual=float(norm(re)),absolute_residual=float(np.max(abs(re))),minimum_principal_eigenvalue=float(ell),newton_trace=trace)
 if case=='main':
  check=(rr>.002)&(rr<.035)
  spl=RectBivariateSpline(r,z,Uf.reshape(shape))
  pts=np.array([.003,.006,.012,.024]); j=spl.ev(pts,np.zeros_like(pts),dx=1)
  out['spherical_exact_grad_rel_errors']=(j/Astar.grad(pts)-1).tolist()
  diff=(Uf.reshape(shape)-gref)[check]
  out['spherical_exact_inner_potential_relative_rms']=float(np.linalg.norm(diff-diff.mean())/np.linalg.norm(gref[check]-gref[check].mean()))
 else:
  S=RectBivariateSpline(r,z,Uf.reshape(shape))
  trans=np.array([-axis[1],axis[0]])
  wins={}
  for cutoff in [.08,.30,.80]:
   pairs=[]
   for k in names:
    v=(positions[k]-positions['G'])*xrad*d1
    zz=v@axis; uu=v@trans
    def grads(l,j):
     R0=np.hypot(uu,l); rr=math.hypot(R0,zz); rg=math.hypot(R0,zz-sep)
     if j==0:
      return S.ev(R0,zz,dy=1)-Astar.grad(rr)*zz/rr-Agroup.grad(rg)*(zz-sep)/rg
     return (S.ev(R0,zz,dx=1)-Astar.grad(rr)*R0/rr-Agroup.grad(rg)*R0/rg)*uu/R0
    ang=-2*b*w1/L**2/xrad*np.array([quad(lambda l:grads(l,j),0,cutoff,epsabs=1e-6,epsrel=1e-5,limit=160)[0] for j in [0,1]])
    pairs.append(ang)
   pairs=np.array(pairs)
   wins[str(cutoff)]={'joint_minus_isolated_stacks_pair_mas':1000*float(np.max(np.linalg.norm(pairs[:,None]-pairs,axis=2))), 'each_ray_axis_trans_arcsec':pairs.tolist()}
  out['LOS_half_length_Mpc']=wins
 return out
if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('--runs',nargs='+',default=['main:68:1.5','joint:68:1.5','joint:90:1.5','joint:90:2.25'])
 parser.add_argument('--main-profile',choices=['main','sersic'],default='main')
 args=parser.parse_args();rs=[]
 Astar=Obj(args.main_profile)
 for q in args.runs:
  ca,n,B=q.split(':'); val=run(int(n),float(B),ca);rs.append(val)
  print(json.dumps({k:v for k,v in val.items() if k!='newton_trace'}),flush=True)
  (p/f'he0435_nonlinear_joint_axis_{args.main_profile}.json').write_text(json.dumps(dict(scope='Axisymmetric, no-interface, nonlinear static PDE in full single box with smooth spherical photometrically normalized main (Plummer or core-regularized Sérsic) and cored finite isothermal group proxies (25-kpc unmeasured guard, truncation .761 Mpc from velocity-dispersion proxy). Single common monopole boundary; actual environment density and nonspherical stellar profile unresolved. Observed ray positions evaluated without time-delay or fit.',stellar_profile=args.main_profile,stellar_cored_sersic_retained_pre_normalized_stellar_mass_fraction=getattr(Astar,"norm",None),group_sep_Mpc=sep,group_sigma_kms=470,group_cutoff_Mpc=r200,group_core_Mpc=.025,runs=rs),indent=2)+'\n')
