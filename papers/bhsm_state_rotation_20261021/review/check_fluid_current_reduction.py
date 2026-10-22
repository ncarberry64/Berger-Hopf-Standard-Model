"""Exact independent current elimination/source pairing in a local ADM frame.

This does not certify every term of the covariant KGB metric expansion.
"""
from pathlib import Path
import json
import sympy as s

h,a,chi,v,sp=s.symbols('h a chi v sp',real=True,nonzero=True)
# A single orthonormal gradient direction suffices by polarization.
L=h*(a*a*(sp+chi/a**2)**2/2-sp*v)
solution=s.solve(s.diff(L,sp),sp)[0]
expected=(v-chi)/a**2
assert s.simplify(solution-expected)==0
assert s.simplify(L.subs(sp,solution)-h*(-v*v/2+chi*v)/a**2)==0

# Current source: J0 conserved, mu may depend on time.
t=s.symbols('t',real=True)
J0=s.symbols('J0',real=True,nonzero=True)
D,mu,vel=[s.Function(name)(t) for name in ['D','mu','vel']]
original=-J0*D*s.diff(mu*vel,t)
boundary=s.diff(-J0*D*mu*vel,t)
canonical=J0*mu*vel*s.diff(D,t)
assert s.simplify(original-boundary-canonical)==0
p,rho,alpha,z,di=s.symbols('p rho alpha z di',real=True)
fluid=9*p*z*z/2+3*p*alpha*z-(rho+p)*alpha*di
gravity=-9*p*z*z/2+3*rho*alpha*z
assert s.expand(fluid+gravity+(rho+p)*alpha*(di-3*z))==0
receipt={'status':'PASS','spatial_current_algebraic_elimination':True,
         'temporal_source_pairing_with_variable_mu':True,'total_background_tadpole_sum':True,
         'claim':'exact finite fluid/current identities, not full covariant metric certification'}
(Path(__file__).with_suffix('.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
