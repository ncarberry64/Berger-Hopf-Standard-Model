"""Fixed-position Jackpot companion: conditional R1 same-plane examples and direct-vector control."""
from pathlib import Path
from contextlib import redirect_stdout
import sys,io,json,math
import numpy as np
from scipy.integrate import cumulative_trapezoid,quad
from scipy.interpolate import CubicSpline,RectBivariateSpline
from itertools import product
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
P=Path(__file__).resolve().parent
sys.path[:0]=[str(P.parent/'bhsm_environment_audit'),str(P.parent/'bhsm_environment_audit'/'pinned_extra')]
with redirect_stdout(io.StringIO()):
 import he0435_joint_projected as h
 import s3_stellar_transfer as j
from r1_background_geometry import D,cfs,G,speed,L,xrad,bg
mesh,mat=h.mesh,h.mat
b,C,lam=j.b,j.C,bg.LAMBDA
axis=np.array([-1.,-1.])/np.sqrt(2) # southwest direction; not precise companion astrometry
sep=40.*xrad*j.dl
class Body:
 def __init__(self, label, mass=0, core=.010):
  self.kind=label;self.core=core
  if label=='star':
   self.M=10**np.array(j.masses['Salpeter'])*G/speed**2
   self.mt=sum(self.M)
  else:self.mt=mass*G/speed**2
  r=np.r_[0,np.geomspace(1e-8,1e3,14000)]
  g=self.grad(r)
  self.p=CubicSpline(r,cumulative_trapezoid(g,r,initial=0)-np.trapezoid(g,r))
 def mass(self,r):
  if self.kind=='neighbor':return self.mt*(r/np.hypot(r,self.core))**3
  a,t=j.scales.T
  y=np.asarray(r)[...,None]
  return np.sum(self.M*(2/np.pi)*(t*np.arctan(y/t)-a*np.arctan(y/a))/(t-a),axis=-1)
 def source(self,r):
  if self.kind=='neighbor':return -3*b*L**2*self.mt*self.core**2/np.hypot(r,self.core)**5
  a,t=j.scales.T
  y=np.asarray(r)[...,None]
  return -b*L**2*np.sum(2*self.M/np.pi/(t-a)*(1/(a*a+y*y)-1/(t*t+y*y)),axis=-1)
 def grad(self,r):
  r=np.asarray(r); x=np.where(r>0,r,1.)
  M=self.mass(x); S=np.sqrt(1+16*b*L**2*M/(lam*C*C*x**3))
  return np.where(r>0,-2*b*L**2*M/(C*x*x*(1+S)),0.)

def solve(N,box,Astar,Agroup):
 case='joint'
 r=mesh(0,box,N,[0],[ [.006],[6.] ])
 z=mesh(-box,box,2*N-1,[0,sep],[ [.006,Agroup.core],[6.,1.8] ])
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
 if True: # same single-domain joint equation as HE 0435
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
 assert out['converged'] and ell>0, out
 return RectBivariateSpline(r,z,Uf.reshape(shape)),out
def compare(N,B,mc):
 star,env=Body('star'),Body('neighbor',mc)
 F,out=solve(N,B,star,env)
 normal=np.r_[-axis[1],axis[0]]
 def calc(th,length):
  xyz=th*j.dl*xrad
  u,t=xyz@normal,xyz@axis
  def g(l,k,which):
   r=np.hypot(u,l)
   z=[t,t-sep]
   if which:
    if k==0:return F.ev(r,t,dy=1)
    return F.ev(r,t,dx=1)*u/r
   p,q=np.hypot(z,r)
   h0,h1=star.grad(p)/p,env.grad(q)/q
   return h0*z[0]+h1*z[1] if k==0 else (h0+h1)*u
  iso,joint=[-2*b/L**2*j.weight/xrad*sum(v*quad(lambda l:g(l,k,i),0,length,limit=400,epsabs=1e-8)[0] for k,v in enumerate([axis,normal])) for i in [False,True]]
  y=xyz-sep*axis
  base=j.ray(th,star.M)[0]
  ordinary=4*env.mt*j.weight/xrad*y/(y@y+env.core**2)
  return np.stack([th-base,ordinary,iso,joint])
 rows={}
 for l in [.30,.6,1.0]:
  ca,cb=[calc(t,l) for t in j.theta]
  v,ordinary,iso,joint=ca-cb
  rows[str(l)]=dict(star_gap=float(np.linalg.norm(v)),ordinary_deflection_delta=ordinary.tolist(),
                    GR_gap=float(np.linalg.norm(v-ordinary)),isolated_R1_gap=float(np.linalg.norm(v-ordinary-iso)),
                    joint_R1_gap=float(np.linalg.norm(v-ordinary-joint)),joint_minus_isolated_mas=float(1000*np.linalg.norm(joint-iso)))
 return out|{'companion_mass_solar':mc,'assumed_core_kpc':1000*env.core,'projection':rows}
def direct_geometry():
 # Pure ordinary one-plane test, includes fixed Plummer scale; varying only mass.
 # Range of PAs is an illustrative sampling of the southwest quadrant, not
 # a satellite-position error or a joint prior.
 star=Body('star')
 def line(th,pa):
  V=np.array([np.sin(pa),np.cos(pa)])*sep; y=th*j.dl*xrad-V
  return 4*(1e12*G/speed**2)*j.weight/xrad*y/(y@y+.01**2)
 aa,bb=[th-j.ray(th,star.M)[0] for th in j.theta]
 v=aa-bb
 rows=[]
 # Upper bound on differential per unit mass for ANY PA at radius 40 arcsec:
 # Plummer map has Jacobian norm <= 1/(|x|^2+core^2) <= 1/|x|^2 along the A-B chord.
 radial_min=(40-max(np.linalg.norm(j.theta,axis=1)))*j.dl*xrad
 max_shift=4*(1e12*G/speed**2)*j.weight/xrad*np.linalg.norm(j.theta[0]-j.theta[1])*j.dl*xrad/radial_min**2
 for pa in [180,195,210,225,240,255,270]:
  a,b=[line(th,np.deg2rad(pa)) for th in j.theta];u=a-b
  m=max(0.,v@u/(u@u))
  rows.append(dict(PA_deg=pa,differential_mas_per_1e12_Msun=1000*np.linalg.norm(u),
                  diagnostic_best_mass_solar=m*1e12,minimum_remaining_arcsec=np.linalg.norm(v-m*u)))
 assert all(row['differential_mas_per_1e12_Msun']/1000<=max_shift for row in rows)
 return {'sampled_position_angles':rows,'mass_lower_bound_for_any_angle_solar':np.linalg.norm(v)/max_shift*1e12,
         'upper_shift_arcsec_per_1e12':max_shift,'projected_separation_kpc':sep*1000}
if __name__=='__main__':
 out={'scope':'Fixed 40 arcsec nominal south-west companion at main redshift (conditional), R1 axisymmetric field; no s1/s2 masses, morphology, lens-derived mass or free coupling. No claim of measured companion mass or line-of-sight separation. Positive-mass fit is an ordinary geometric diagnostic only.',
      'single_companion_geometry':direct_geometry(),'runs':[compare(n,B,m) for n,B,m in [(100,1.4,1e11),(130,1.7,1e11),(100,1.4,1e12),(130,1.7,1e12)]]}
 (P/'observed_jackpot.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
