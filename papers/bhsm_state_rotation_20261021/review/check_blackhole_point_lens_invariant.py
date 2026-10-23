"""Independent branch-aware checks of point-lens delay/flux motion cancellation.

Synthetic dimensionless tests only. No observations or inferred physical
couplings. Requires NumPy and SymPy; writes its receipt and CSV beside source.
"""
from pathlib import Path
import csv
import json
from math import asinh, cos, log, sin, sinh, sqrt, pi
import numpy as np
import sympy as s

# Symbolic proof starts from the stationary image x+=q, x-=-1/q.
q=s.symbols('q',positive=True)
u=s.symbols('u',positive=True)
y=q-1/q
tauplus=s.Rational(1,2)*(q-y)**2-s.log(q)
tauminus=s.Rational(1,2)*(-1/q-y)**2+s.log(q)
assert s.simplify(tauminus-tauplus-(q*q-q**-2)/2-2*s.log(q))==0
muplus=1/(1-q**-4)
muminus=1/(1-q**4)
assert s.simplify(-muplus/muminus-q**4)==0
h_expr=u*s.sqrt(u*u+4)/2+2*s.asinh(u/2)
assert s.simplify(s.diff(h_expr,u)-s.sqrt(u*u+4))==0
assert s.simplify(s.diff(4*s.asinh(u/2),u)-4/s.sqrt(u*u+4))==0

def h(u):
    return u*sqrt(u*u+4)/2+2*asinh(u/2)

def apparent_mass_ratio(delay,ratio):
    inferred_u=2*sinh(log(ratio)/4)
    return delay/h(inferred_u)

def full_point_images(source):
    source=np.asarray(source,dtype=float)
    un=float(np.linalg.norm(source))
    direction=source/un
    xp=(un+sqrt(un*un+4))/2
    xm=-1/xp
    out=[]
    for signed_x in (xp,xm):
        x=signed_x*direction
        r2=float(x@x)
        residual=x-source-x/r2
        jac=(1-1/r2)*np.eye(2)+2*np.outer(x,x)/r2**2
        mu=1/float(np.linalg.det(jac))
        tau=float((x-source)@(x-source))/2-log(sqrt(r2))
        out.append((x,mu,tau,float(np.linalg.norm(residual))))
    assert out[0][1]>0 and out[1][1]<0
    assert out[0][1]>abs(out[1][1])
    delay=out[1][2]-out[0][2]
    assert delay>0
    ratio=abs(out[0][1]/out[1][1])
    return delay,ratio,max(o[3] for o in out)

maximum_mass_error=0.0
maximum_stationary_residual=0.0
trajectory_counts={}
for name in ['straight','curved','parallax_like']:
    count=0
    for epoch in np.linspace(-1,1,81):
        if name=='straight':
            position=(epoch,.3)
        elif name=='curved':
            position=((.6+.2*epoch)*cos(2*epoch),(.6+.2*epoch)*sin(2*epoch))
        else:
            position=(.2+.5*epoch+.08*cos(2*pi*epoch),.4+.06*sin(2*pi*epoch))
        delay,ratio,residual=full_point_images(position)
        maximum_mass_error=max(maximum_mass_error,abs(apparent_mass_ratio(delay,ratio)-1))
        maximum_stationary_residual=max(maximum_stationary_residual,residual)
        count+=1
    trajectory_counts[name]=count

rows=[]
convergence_error=0.0
shear_values=[]
for kappa in [.1,.3]:
    lam=1-kappa
    for un in [.5,1.,2.]:
        xp=(un+sqrt(un*un+4*lam))/(2*lam)
        xm=(un-sqrt(un*un+4*lam))/(2*lam)
        def tau(x): return .5*(x-un)**2-log(abs(x))-.5*kappa*x*x
        def mu(x): return 1/(lam*lam-1/x**4)
        delay=tau(xm)-tau(xp)
        ratio=abs(mu(xp)/mu(xm))
        massratio=apparent_mass_ratio(delay,ratio)
        convergence_error=max(convergence_error,abs(massratio-1))
        rows.append({'model':'isotropic_convergence','coefficient':kappa,'u':un,'flux_ratio':ratio,'delay_in_4GM1plusz_over_c3':delay,'M_app_over_M':massratio})

for gamma in [.05,.1]:
    for un in [.5,1.,2.]:
        assert un>2*gamma/sqrt(1+gamma)  # exactly two images, no off-axis pair
        lam=1-gamma
        xp=(un+sqrt(un*un+4*lam))/(2*lam)
        xm=(un-sqrt(un*un+4*lam))/(2*lam)
        def tau(x): return .5*(x-un)**2-log(abs(x))-.5*gamma*x*x
        def mu(x): return 1/((1-gamma+1/x**2)*(1+gamma-1/x**2))
        assert mu(xp)>0 and mu(xm)<0 and mu(xp)>abs(mu(xm))
        delay=tau(xm)-tau(xp)
        ratio=abs(mu(xp)/mu(xm))
        assert delay>0 and ratio>1
        massratio=apparent_mass_ratio(delay,ratio)
        shear_values.append(massratio)
        rows.append({'model':'external_shear_on_axis','coefficient':gamma,'u':un,'flux_ratio':ratio,'delay_in_4GM1plusz_over_c3':delay,'M_app_over_M':massratio})

# The first-order formula cancels a displacement to quadratic accuracy.
linear_checks=[]
for un in [.2,.5,1.,2.]:
    du=1e-5
    coefficient=(un*un+4)/(4*h(un))
    dlogdelay=log(h(un+du)/h(un))
    dlogratio=4*(asinh((un+du)/2)-asinh(un/2))
    residual=dlogdelay-coefficient*dlogratio
    linear_checks.append({'u':un,'du':du,'linear_residual':residual,'absolute_residual_over_du2':abs(residual)/du**2})

assert maximum_mass_error<2e-13
assert maximum_stationary_residual<1e-13
assert convergence_error<1e-13
assert max(abs(x['linear_residual']) for x in linear_checks)<2e-8
assert max(shear_values)-min(shear_values)>.5
receipt={
    'status':'PASS',
    'scope':'standard point-lens identity and quasistatic synthetic alignment control; no observational claim',
    'symbolic_checks':{'fermat_delay_identity':True,'signed_flux_ratio_identity':True,'h_derivative':True,'log_flux_ratio_derivative':True},
    'synthetic_trajectory_sample_counts':trajectory_counts,
    'maximum_absolute_Mapp_over_M_error':maximum_mass_error,
    'maximum_stationary_equation_residual':maximum_stationary_residual,
    'maximum_isotropic_convergence_Mapp_error':convergence_error,
    'linear_perturbation_checks':linear_checks,
    'macro_counterexamples':rows,
}
base=Path(__file__).parent
(base/'blackhole_point_lens_invariant_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
with (base/'blackhole_point_lens_invariant_table.csv').open('w',newline='',encoding='utf-8') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(json.dumps(receipt,indent=2))
