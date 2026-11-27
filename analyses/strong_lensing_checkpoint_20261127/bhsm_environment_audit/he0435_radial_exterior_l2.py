"""Finite same-star transparent match, using isolated Sluse-group scalar as incident exterior."""
import contextlib,io,json,math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp, solve_bvp, quad
from scipy.interpolate import CubicSpline
with contextlib.redirect_stdout(io.StringIO()):
 from he0435_joint_field_control import m,positions,names,d1,w1,bg,L,speed,xrad
p=Path(__file__).parent
cfg=json.loads((p/'he0435_group_direction.json').read_text())
axis=np.r_[cfg['unit_E_N'],0.]
d=67.1*xrad*d1/L
b,C,lam=m.b,m.C,bg.LAMBDA
rmin,rmax=1e-7/L,100/L
ts=np.linspace(np.log(rmin),np.log(rmax),1400)
def coef(t):
 x=np.exp(t); r=x*L
 mu,n=m.sphere(r/m.a)
 S=np.sqrt(1+(m.rv/r)**3*mu)
 return C*S,.5*(n-3)*(1-1/S**2)
v=np.array([coef(t) for t in ts])
A=CubicSpline(ts,v[:,0]); ell=CubicSpline(ts,v[:,1])
def ric(t,y):
 e=ell(t); q=y[0]
 return [6*(1+e/2)-q*(q+1+e),q]
vdec=solve_ivp(ric,(ts[-1],ts[0]),[-3,0],rtol=3e-11,atol=5e-11,dense_output=True)
assert vdec.success
e=ell(ts[0]); q0=(-1-e+np.sqrt((1+e)**2+24*(1+e/2)))/2
uinc=solve_ivp(ric,(ts[0],ts[-1]),[q0,0],rtol=3e-11,atol=5e-11,dense_output=True)
assert uinc.success
mu,weight=leggauss(120)
P2=(3*mu**2-1)/2

def run(rb,sigma):
 gamma=2*(sigma/speed)**2
 K=16*b*gamma/(lam*C*C)
 pref=-b*gamma/C
 def g_scalar(x):
  rr=np.sqrt(np.maximum(0.,x*x+d*d-2*x*d*mu))
  sq=np.sqrt(rr*rr+K)
  val=pref*(rr/(sq+rr)+np.arcsinh(rr/np.sqrt(K)))
  der0=2*pref/(sq+rr)
  ds=(x-d*mu)/rr
  derivative=der0*ds
  second=der0*(d*d*(1-mu*mu)/rr**3-ds*ds/sq)
  return tuple((5/2)*np.sum(weight*P2*t) for t in [val,derivative,second])
 def source_l2(x):
  den=x*x+d*d-2*x*d*mu
  return -(5/2)*b*gamma*np.sum(weight*P2/den)
 x=rb/L; t0=np.log(x)
 inc,dinc,ddinc=g_scalar(x)
 gv=vdec.sol(t0)[0]; gu=uinc.sol(t0)[0]
 td=np.linspace(ts[0],t0,500)
 fsource=CubicSpline(td,[source_l2(np.exp(t)) for t in td])
 def eq(t,y):
  e=ell(t); rhs=np.exp(2*t)*fsource(t)/(A(t)*inc)
  return [y[1],rhs-(1+e)*y[1]+6*(1+e/2)*y[0]]
 # f_out = g_inc + c * v_dec, so L_* f_out = L_* g_inc for x>=x_b;
 # no artificial sheet: same A(r_b) times exact matched derivative.
 second=x*dinc/inc-gv
 def bc(L,R):return [L[1]-q0*L[0],R[1]-gv*R[0]-second]
 sol=solve_bvp(eq,bc,td,np.zeros((2,len(td))),tol=1e-9,max_nodes=8000)
 assert sol.success
 fin,fdot=inc*sol.sol(t0)
 exterior_c=fin-inc
 def ext(r):
  t=np.log(r); giv,gid,_=g_scalar(r)
  yd=vdec.sol(t); amp=exterior_c*np.exp(yd[1]-vdec.sol(t0)[1])
  return giv+amp,gid+yd[0]*amp/r
 h,hp=ext(x)
 rel_val=abs(h-fin)/abs(inc)
 rel_flux=abs(A(t0)*(hp-fdot/x))/(abs(A(t0)*dinc))
 assert rel_val<1e-12 and rel_flux<1e-8
 # Compare fixed inner observation window across exterior launch radii.
 rcut=.015/L
 def slope_2d(xyz):
  r=np.linalg.norm(xyz); unit=xyz/r; u=axis@unit; P=.5*(3*u*u-1)
  f,fp=inc*sol.sol(np.log(r)); fp/=r
  return (fp*P*unit+(3*u*f/r)*(axis-u*unit))[:2]
 rays=[]
 for n in names:
  xx=(positions[n]-positions['G'])*xrad*d1/L
  zmax=np.sqrt(rcut**2-xx@xx)
  j=[-2*b*w1*quad(lambda z:slope_2d(np.r_[xx,z])[k],0,zmax,epsabs=1e-13,epsrel=2e-9)[0]/xrad for k in [0,1]]
  rays.append(j)
 rays=np.array(rays)
 f6,df6=inc*sol.sol(np.log(.006/L)); g6,_,_=g_scalar(.006/L)
 root_a=A(t0); root_e=ell(t0)
 outer_source=root_a*(ddinc+(2+root_e)/x*dinc-6*(1+root_e/2)*inc/x**2)
 actual_source=source_l2(x)
 return dict(sigma_kms=sigma,launch_kpc=rb*1000,a_boundary_over_C=float(A(t0)/C), outer_incident_drive_over_exact_l2_group_density=float(outer_source/actual_source),interior_6kpc_to_isolated_quad=float(f6/g6),pointwise_matched_over_fixed_Dirichlet_at_launch=float(fin/inc),quad_flux_relative_mismatch=float(rel_flux),quad_value_relative_mismatch=float(rel_val),regular_slope=float(gu),decaying_slope=float(gv),max_pairwise_l2_inner15_mas=1000*float(np.max(np.linalg.norm(rays[:,None]-rays,axis=2))))

out=dict(scope='Radial stellar operator with exact l=2 projection of group volume source inside the launch boundary, group scalar isolated incident shape and radial-stellar decaying correction outside. Exterior forcing is by construction Lstar[g_inc], not a nonlinear self-consistent 3D calculation. Fixed 15kpc LOS window (not full sky readout), no timing, no adjusted amplitudes. Cross-launch variation is sensitivity to the prescribed external drive, not mismatch or numerical tolerance.',stellar_rV_Mpc=m.rv,group_projected_sep_Mpc=d*L,runs=[run(r,s) for r in [.02,.04,.08,.12] for s in [370,470,570]])
(p/'he0435_radial_exterior_l2.json').write_text(json.dumps(out,indent=2)+'\n')
for a in out['runs']:
 if a['sigma_kms']==470: print(a)
