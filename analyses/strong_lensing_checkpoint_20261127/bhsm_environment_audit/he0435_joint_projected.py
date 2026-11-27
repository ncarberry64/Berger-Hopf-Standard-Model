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
 from he0435_joint_field_control import m,positions,names,d1,w1,bg,L,speed,xrad,G,d2,d12,w2,theta_g,g_photo
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
  def deflections(t,cutoff):
   zz=t*d1@axis; uu=t*d1@trans
   def gradients(l,j,typ):
    R0=np.hypot(uu,l); rr=math.hypot(R0,zz); rg=math.hypot(R0,zz-sep)
    if typ=='joint':
     return S.ev(R0,zz,dy=1) if j==0 else S.ev(R0,zz,dx=1)*uu/R0
    if j==0:return Astar.grad(rr)*zz/rr+Agroup.grad(rg)*(zz-sep)/rg
    return (Astar.grad(rr)/rr+Agroup.grad(rg)/rg)*uu
   vec=[axis,trans]
   return {typ:sum(-2*b/L**2*vec[j]*quad(lambda l:gradients(l,j,typ),0,cutoff,epsabs=1e-7,epsrel=2e-6,limit=400)[0] for j in (0,1)) for typ in ('joint','isolated')}
  def newton(t):
   x=t*d1
   R=np.linalg.norm(x)
   # Project spherical density without re-using the uncored light profile.
   def ext(th):
    c=math.cos(th); r=R/c
    return Astar.rho(min(r,4.))*R**3*math.sin(th)*c**-4*(c*c/(1+math.sin(th)))
   mcyl=Astar.mt*(Astar.enclosed(R)+quad(ext,0,math.pi/2,epsabs=2e-9,epsrel=5e-7)[0])
   y=x-sep*axis; r=np.linalg.norm(y)
   # Analytic cylindrical mass for difference of two softened isothermal profiles.
   Mgroup=math.pi*gamma/2*r*r*(1/(math.hypot(.025,r)+.025)-1/(math.hypot(r200,r)+r200))
   return 4*mcyl/R**2*x+4*Mgroup/r**2*y
  th=[(positions[k]-positions['G'])*xrad for k in names]+[theta_g]
  ordinary=np.array([newton(t) for t in th])
  def pair(A):return float(np.max(np.linalg.norm(A[:,None]-A,axis=2)))
  def readout(aa,on2):
   rays=[]; rear=[]
   for i,t in enumerate(th[:-1]):
    x2=d2*(t-theta_g)-d12*(aa[i]-aa[-1])
    a2,_=g_photo.apply(x2,on2)
    rays.append((t-w1*aa[i]-w2*a2)/xrad)
    rear.append(np.linalg.norm(x2)*1000)
   return np.array(rays),rear
  wins={}
  base,base_rear=readout(ordinary,False)
  for cutoff in [.08,.30,.80,1.25]:
   graph=[deflections(t,cutoff) for t in th]
   joint=np.array([g['joint'] for g in graph]); iso=np.array([g['isolated'] for g in graph])
   bj,rj=readout(ordinary+joint,True); bi,ri=readout(ordinary+iso,True)
   diff=bj-bi; angle=w1*(joint-iso)/xrad
   def rms(v):return float(np.sqrt(np.mean(np.sum((v-v.mean(axis=0))**2,axis=1))))
   wins[str(cutoff)]=dict(ordinary_common_source_RMS_arcsec=rms(base),isolated_R1_common_source_RMS_arcsec=rms(bi),joint_R1_common_source_RMS_arcsec=rms(bj),ordinary_max_source_disagreement_arcsec=pair(base),joint_max_source_disagreement_arcsec=pair(bj),joint_vs_ordinary_pairwise_differential_source_shift_mas=1000*pair(bj-base),joint_minus_isolated_foreground_pairwise_deflection_microarcsec=1e6*pair(angle[:-1]),joint_minus_isolated_after_G1_pairwise_source_shift_microarcsec=1e6*pair(diff),rear_propagation_increment_on_that_differential_microarcsec=1e6*pair(diff+angle[:-1]),ordinary_sources_arcsec=base.tolist(),joint_sources_arcsec=bj.tolist(),isolated_sources_arcsec=bi.tolist(),joint_G1_impacts_kpc=rj)
  out['LOS_half_length_Mpc']=wins
  print(N,box,out['converged'],wins['0.8'],flush=True)
 return out
if __name__=='__main__':
 Astar=Obj('sersic')
 runs=[run(n,B) for n,B in [(68,1.5),(90,1.5),(90,2.25),(115,1.5),(115,2.25)]]
 (p/'he0435_joint_projected.json').write_text(json.dumps(dict(scope='Observed-ray, fixed-input two-screen calculation. Foreground scalar terms integrated over identical finite sightlines, ordinary fields full thin-lens projection.',runs=runs),indent=2)+'\n')
