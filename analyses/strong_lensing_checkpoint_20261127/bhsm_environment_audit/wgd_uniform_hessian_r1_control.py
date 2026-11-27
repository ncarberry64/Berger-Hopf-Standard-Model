"""Conditional upper envelope: isotropic environmental Hessian shifts only C in local R1."""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import quad
p=Path(__file__).resolve().parent
owned=p.parent/'wgd_frozen_transfer/wgd_frozen_transfer.py'
ns={'__file__':str(owned)}
exec(compile(owned.read_text().split('\nruns={}',1)[0],str(owned),'exec'),ns)
w=json.loads(owned.with_suffix('.json').read_text())
crit=w['Einstein_radius_conditional_screen'][0]['ratio_at_source_redshift']['0.777']['circular_critical_Msun']
x=ns['d_l']*1.30*ns['xrad']/ns['a']
b=ns['b']; C=ns['C']; G=ns['G'];c=ns['speed']; L=ns['L']; a=ns['a'];lam=ns['bg'].LAMBDA
rows=[]
for logM in (11.57,11.82):
 M=10**logM
 k=16*b*G*M/c**2*L**2/(lam*a**3)
 def bend(Ceff):
  def integrand(theta):
   z=np.cos(theta); r=x/z
   mu,_=ns['sersic'](r)
   den=Ceff+np.sqrt(Ceff*Ceff+k*mu/r**3)
   return mu*b*b/den*z
  return quad(integrand,0,np.pi/2,epsabs=2e-13,epsrel=2e-10)[0]
 f,cap=bend(C),bend(0)
 assert 0 < bend(2*C) < f < cap
 rows.append({'logM':logM,'native_increment_over_circular_critical':M*f/crit,
              'uniform_hessian_passive_Ceff_ge_0_cap_over_circular_critical':M*cap/crit,
              'cap_to_native_ratio':cap/f})
out={'scope':'Isotropic environmental Hessian h I only, Ceff=C−8h/λ, unchanged b/λ, subtract environment own lensing. Upper comparison extends local Ceff>=0 formula formally to infinity; not a claim for real anisotropic, negative kinetic, global or arbitrary physical environment. The Ceff=0 limit is an algebraic cap, not an admitted physical environment.',
 'rows':rows}
(p/'wgd_uniform_hessian_r1_control.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
