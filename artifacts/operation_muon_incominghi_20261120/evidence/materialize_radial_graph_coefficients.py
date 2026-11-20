"""Original material Maxwell radial geometry + n1 source jets on saved raw268.
No field/Cauchy/native solution or physical-mode selection.
"""
import numpy as np,json
from pathlib import Path
p=Path(__file__).parent;r0=(343./5.)**(1/6);WALL=np.pi/2
def sinrem(x):
 out=np.sin(x)-x;mask=np.abs(x)<.1
 if np.any(mask):
  y=x[mask];term=-y**3/6;ss=term.copy()
  for n in range(2,12):
   term *= -y*y/((2*n)*(2*n+1));ss+=term
  out[mask]=ss
 return out
names=['electric','radial','angular','electric_radial','shift','lambda','lambda_tau','lambda_rho','angular_shear_per_grad_xi']
def coeff(raw,rho,s=None,sd=None):
 q=raw[:37];v=raw[37:74];m=raw[74:98];s=raw[98] if s is None else s;sd=raw[99] if sd is None else sd
 cs=r0*np.exp(q[0]+q[1:13]@((-1.)**np.arange(1,13))+q[13:25]@((-1.)**np.arange(12)))
 lc=v[0]+v[1:13]@((-1.)**np.arange(1,13))+v[13:25]@((-1.)**np.arange(12));ks=np.arange(1,13);js=np.arange(12)
 kshape=-1/(16*cs);wall=np.pi/4+s/cs;wd=(sd-lc*s)/cs;jac=2*wall/WALL;chi=rho*wall/WALL
 ck=np.cos(4*chi[:,None]*ks);cj=np.cos(4*chi[:,None]*js);sk=np.sin(4*chi[:,None]*ks);sj=np.sin(4*chi[:,None]*js);win=np.sin(2*chi)**2;wp=2*np.sin(4*chi)
 u=ck@q[1:13];w=win*(cj@q[13:25]);bb=win*(cj@q[25:37]);up=(-4*ks*sk)@q[1:13];bp=(wp[:,None]*cj-4*js*win[:,None]*sj)@q[25:37]
 rad=r0*np.exp(q[0]);C=rad*np.exp(u+w);A=rad*np.exp(u+bb)*np.cos(chi);B=rad*np.exp(u-bb)*np.sin(chi);N=np.exp(ck@m[:12]);beta=np.sin(4*chi)*(cj@m[12:]);LF=np.sqrt(A*A+B*B);R=A*B/LF
 la=v[0]+ck@v[1:13]+win*(cj@v[25:37]);lb=v[0]+ck@v[1:13]-win*(cj@v[25:37]);ap=up+bp-np.tan(chi);bprime=up-bp+1/np.tan(chi)
 delta=-.5*sinrem(4*chi)/np.pi+s*kshape*(52*sinrem(2*chi)-14*sinrem(6*chi)-2*sinrem(10*chi))/np.pi+.5*s*s*kshape*kshape*(982*sinrem(4*chi)-256*sinrem(8*chi)-140*sinrem(12*chi)-12.5*sinrem(16*chi))/np.pi
 common=2*np.pi**4*LF**5*(4*delta*(1-delta));Cr=C/2;adv=2*rho/WALL*wd;lam=A*A/LF**2;lr=lam*(1-lam)*(ap-bprime);lt=2*lam*(1-lam)*(la-lb)
 return np.stack([jac*common*Cr*R/N,common*N*R/(Cr*jac),jac*common*N*Cr/R,common*R**3/(N*Cr*jac),(2*beta+adv)/jac,lam,lt+adv*lr,jac*lr,rho/(cs*wall)],axis=-1)
records=[]
for side in ['incoming','outgoing']:
 z=np.load(p/(side+'_lo.npz'));raw=z['raw'];xx,ww=np.polynomial.legendre.leggauss(192);rho=(xx+1)*WALL/2;weights=ww*WALL/2
 base=coeff(raw,rho);ds=coeff(raw,rho,s=raw[98]+1e-20j).imag/1e-20;dv=coeff(raw,rho,sd=raw[99]+1e-20j).imag/1e-20
 e,r,d,k=base[:,0],base[:,1],base[:,2],base[:,3];rel=np.max(abs(k-e*r/d)/np.maximum(1,abs(k)))
 jetid=ds[:,3]-(ds[:,0]*r/d+e*ds[:,1]/d-e*r*ds[:,2]/d**2)
 assert np.all(base[:,:4]>0) and rel<1e-12 and np.max(abs(jetid)/np.maximum(1,abs(ds[:,3])))<1e-11
 h=1e-4
 def centered(h):return (coeff(raw,rho,s=raw[98]+h)-coeff(raw,rho,s=raw[98]-h))/(2*h)
 fd=(4*centered(h/2)-centered(h))/3;defect=np.max(abs(fd-ds)/np.maximum(1,abs(ds)))
 assert defect<1e-6
 np.savez(p/(side+'_radial_graph_coefficients.npz'),rho=rho,quadrature=weights,coefficients=base,normal_position_first=ds,normal_velocity_first=dv,names=np.array(names),raw=raw,rawdot=z['rawdot'])
 records.append(dict(side=side,radial_nodes=192,positive_base_densities=True,metric_identity_relative_defect=float(rel),metric_identity_first_relative_defect=float(np.max(abs(jetid)/np.maximum(1,abs(ds[:,3])))),independent_shape_difference_scaled_defect=float(defect),normal_velocity_nonzero_columns=[names[i] for i in range(9) if np.any(dv[:,i])],radial_shape_first_max=float(abs(ds).max()),source_interval='first actual retained sample only',physical_causal_solution=False))
out=dict(scope='original anchored material geometry192 radial nodes, same supplied source chart and exact first shape/rate jets; source-response polynomial used within its retained two-jet scope',records=records)
(p/'RADIAL_GRAPH_COEFFICIENTS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
