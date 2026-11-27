"""Finite local Dirichlet control: observed group and main R1 mixed static operator."""
from pathlib import Path
import contextlib,io,json,math
from scipy.integrate import solve_ivp,quad,solve_bvp
from scipy.interpolate import CubicSpline
import numpy as np
from numpy.polynomial.legendre import legval,legder,leggauss
with contextlib.redirect_stdout(io.StringIO()):
 from he0435_joint_field_control import m,z1,positions,names,d1,w1,bg,L,speed,xrad
p=Path(__file__).parent
b,C=m.b,m.C
lam=bg.LAMBDA
gsep=67.1
groups=370.,470.,570.
# Astrometric group PA supplied by primary centroid; read override, otherwise report axis-aligned illustrative projection only.
cfgpath=p/'he0435_group_direction.json'
cfg=json.loads(cfgpath.read_text()) if cfgpath.exists() else None
axis=np.array(cfg['unit_E_N'] if cfg else (1.,0.)); axis=axis/np.linalg.norm(axis)
Xg=gsep*xrad*d1/L
g3=np.r_[axis,0.]
I=np.eye(3)
def coeff(logr):
 x=np.exp(logr); r=x*L
 mu,n=m.sphere(r/m.a)
 S=np.sqrt(1+(m.rv/r)**3*mu)
 deriv=.5*(n-3)*(1-1/S**2)
 return C*S,deriv
ln=np.linspace(np.log(1e-7/L),np.log(.125/L),600)
vals=np.array([coeff(a) for a in ln])
ar_s=CubicSpline(ln,vals[:,0]); dl_s=CubicSpline(ln,vals[:,1]); rlo=ln[0]
def aro(x):return ar_s(np.log(x))
qgamma=(-1-dl_s(rlo)+np.sqrt((1+dl_s(rlo))**2+24*(1+dl_s(rlo)/2)))/2
def rhs(t,y):
 loga=dl_s(t); gamma=y[0]
 return [6*(1+loga/2)-gamma*(gamma+1+loga),gamma]
res=solve_ivp(rhs,(rlo,ln[-1]),[qgamma,0.],rtol=2e-10,atol=2e-11,dense_output=True)
assert res.success
def run(r_b,sigma):
 xb=r_b/L
 gamma=2*(sigma/speed)**2 # mass length m_g/L=gamma*x_g for ideal SIS.
 Sg=np.sqrt(1+16*b*gamma/(lam*C*C*Xg**2))
 grad=-2*b*gamma/(Xg*C*(1+Sg))
 HgR=-grad/(Xg*Sg)
 HgT=grad/Xg
 J=-b*gamma/Xg**2
 # l=0 true local source. l=2 group asymptotic shape data is local Taylor Dirichlet.
 # l=1 constant group acceleration removed simultaneously for all centered rays.
 obsquad=(HgR-HgT)*xb**2/3
 v_b=res.sol(np.log(xb))[1]
 def fl(r):
  y=res.sol(np.log(r)); f=obsquad*np.exp(y[1]-v_b)
  return f,y[0]*f/r
 def Hess(l,r,f,fp,fpp,mu):
  ec=np.eye(l+1)[l]
  P=legval(mu,ec); Pd=legval(mu,legder(ec)); Pdd=legval(mu,legder(ec,2))
  Hrr=fpp*P
  T=fp*P/r
  Htt=T+f/r**2*((1-mu*mu)*Pdd-mu*Pd)
  Hpp=T-f/r**2*mu*Pd
  Hrt=-(fp/r-f/r**2)*Pd*np.sqrt(1-mu*mu)
  return np.array([Hrr,Htt,Hpp,Hrt])
 def h1(r,mu):
  ar=aro(r); dl=dl_s(np.log(r)); f,fp=fl(r); fpp=6*(1+dl/2)*f/r**2-(2+dl)*fp/r
  u=J*r/(3*ar); up=(1-dl)*u/r
  return Hess(0,r,0.,u,up,mu)+Hess(2,r,f,fp,fpp,mu)
 def nonlin(H):
  a,d,c,e=H
  return (2/lam)*((a+d+c)**2-a*a-d*d-c*c-2*e*e)
 def change(r,mu):
  H=h1(r,mu)
  a,d,c,e=H
  evals=np.linalg.eigvalsh(np.array([[a,e,0],[e,d,0],[0,0,c]]))
  delta=(4/lam)*(np.sum(evals)-evals)
  amin=aro(r)*min(1,1+dl_s(np.log(r))/2)
  return np.max(abs(delta))/amin
 def actual_perturb_solution():
  # With fixed Dirichlet data one explicit Newton/Picard residual correction.
  # RHS is the exact omitted quadratic evaluated at the linear solution.
  rs=np.linspace(rlo,np.log(xb),501)
  u,w=leggauss(8)
  scales=abs(obsquad)
  Q=np.array([nonlin(h1(np.exp(t),u)) for t in rs])
  corr=[]
  for l in [0,2,4]:
   P=legval(u,np.eye(l+1)[l])
   rhs=CubicSpline(rs,(2*l+1)/2*(Q@(w*P)))
   pwr=(-1-dl_s(rlo)+np.sqrt((1+dl_s(rlo))**2+4*l*(l+1)*(1+dl_s(rlo)/2)))/2
   def eq(t,y,l=l,rhs=rhs):
    d=dl_s(t); F=np.exp(2*t)*rhs(t)/(ar_s(t)*scales)
    return np.stack((y[1],F-(1+d)*y[1]+l*(l+1)*(1+d/2)*y[0]))
   bc=lambda L,R,pwr=pwr:np.array([L[1]-pwr*L[0],R[0]])
   sol=solve_bvp(eq,bc,rs,np.zeros((2,len(rs))),tol=2e-8,max_nodes=5000)
   assert sol.success
   corr.append((l,sol,eq))
  def q_update(r,mu):
   t=np.log(r); H=h1(r,mu); dh=np.zeros_like(H); fs=[]
   for l,sol,eq in corr:
    f,d=sol.sol(t); dd=eq(t,np.array([f,d]))[1]
    dh+=Hess(l,r,scales*f,scales*d/r,scales*(dd-d)/r**2,mu)
    fs.append(f)
   return abs((nonlin(H+dh)-nonlin(H))/J), float(np.linalg.norm(dh)/np.linalg.norm(H)), max(abs(v) for v in fs)
  samples=[q_update(v,u) for v in np.geomspace(.001*xb,xb,70) for u in np.linspace(0,1,41)]
  def cg(x):
   r=np.linalg.norm(x); nh=x/r; mu=nh@g3; total=np.zeros(3)
   for l,sol,eq in corr:
    f,d=sol.sol(np.log(r)); ec=np.eye(l+1)[l]
    total+=scales/r*(d*legval(mu,ec)*nh+f*legval(mu,legder(ec))*(g3-mu*nh))
   return total[:2]
  R=[]
  for k in names:
   q=(positions[k]-positions['G'])*xrad*d1/L
   zmax=np.sqrt(xb*xb-q@q)
   raw=[quad(lambda zz:cg(np.r_[q,zz])[j],0,zmax,epsabs=2e-13,epsrel=2e-9)[0] for j in [0,1]]
   R.append(-2*b*w1*np.array(raw)/xrad)
  R=np.array(R)
  return dict(post_update_quadratic_residual_over_J_grid_max=max(x[0] for x in samples), hessian_update_rel_grid_max=max(x[1] for x in samples), max_each_mode_correction_potential_over_l2_boundary=max(x[2] for x in samples),pairwise_nonlinear_correction_mas=1000*float(np.max(np.linalg.norm(R[:,None]-R,axis=2))),correction_rays_arcsec=R.tolist())

 def grad_perp(x):
  r=np.linalg.norm(x); nh=x/r; mu=nh@g3; P=(3*mu*mu-1)/2
  f,fp=fl(r)
  u=J*r/(3*aro(r))
  h= (u+fp*P)*nh + (3*mu*f/r)*(g3-mu*nh)
  iso=HgT*x+(HgR-HgT)*(x@g3)*g3
  return h[:2],iso[:2]
 A=[]
 for k in names:
  q=(positions[k]-positions['G'])*xrad*d1/L
  zmax=np.sqrt(xb*xb-q@q)
  vals=[quad(lambda zz:grad_perp(np.r_[q,zz])[i][j],0,zmax,epsabs=2e-13,epsrel=2e-9)[0] for i in [0,1] for j in [0,1]]
  vals=-2*b*w1*np.array(vals).reshape(2,2)/xrad
  A.append(dict(image=k,group_scalar_joint_inner_reduced_deflection_arcsec=vals[0].tolist(),group_scalar_isolated_Taylor_inner_deflection_arcsec=vals[1].tolist(),nonstack_difference=(vals[0]-vals[1]).tolist()))
 d=np.array([a['nonstack_difference'] for a in A])
 j=np.array([a['group_scalar_joint_inner_reduced_deflection_arcsec'] for a in A])
 second=actual_perturb_solution() if sigma==470 else None
 if second:
  j1=j+np.array(second['correction_rays_arcsec'])
  dd=d+np.array(second['correction_rays_arcsec'])
  second['max_pairwise_inner_group_scalar_joint_after_correction_mas']=1000*float(np.max(np.linalg.norm(j1[:,None]-j1,axis=2)))
  second['max_pairwise_nonstack_delta_after_correction_mas']=1000*float(np.max(np.linalg.norm(dd[:,None]-dd,axis=2)))
 return dict(radius_kpc=r_b*1000,group_sigma_kms=sigma,S_group_at_foreground=Sg,ratio_Rmatch_over_group_separation=xb/Xg,mono_group_delta_RHS=J,Hg_radial_tangent=[HgR,HgT],grid_max_ignored_nonlinear_RHS_fraction=max(abs(nonlin(h1(v,u))/J) for v in np.geomspace(.001*xb,xb,70) for u in np.linspace(0,1,41)), grid_max_change_principal_over_min_ellipticity=max(change(v,u) for v in np.geomspace(.001*xb,xb,70) for u in np.linspace(0,1,41)),one_step=second,quad_log_derivative_at_match=float(res.sol(np.log(xb))[0]),max_pairwise_nonstack_delta_mas=1000*float(np.max(np.linalg.norm(d[:,None]-d,axis=2))),max_pairwise_inner_group_scalar_joint_mas=1000*float(np.max(np.linalg.norm(j[:,None]-j,axis=2))),rays=A)
out=dict(scope='Finite local static Dirichlet interior response only. Isothermal spherical dynamical group control; group leading Taylor density monopole plus scalar tidal boundary. No validated outer matching/physical shell, no fitted or timing inputs, no full-field inference. Finite LOS over matching ball only, not launched through rear G1.',galaxy_group_sep_Mpc=Xg*L,group_astrometric_inputs=cfg,axis_used=axis.tolist(),runs=[run(r,s) for r in [.02,.04,.08] for s in groups])
(p/'he0435_local_group_joint_response.json').write_text(json.dumps(out,indent=2)+'\n')
for q in out['runs']:print(q['radius_kpc'],q['group_sigma_kms'],q['S_group_at_foreground'],q['max_pairwise_nonstack_delta_mas'],q['max_pairwise_inner_group_scalar_joint_mas'],q['grid_max_ignored_nonlinear_RHS_fraction'])
