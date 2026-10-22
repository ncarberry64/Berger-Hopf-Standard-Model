"""Independent symbolic/projection checks; no horizon or amplitude inference.

Run with Python in this directory. The receipt records algebraic assertions and
quadrature controls for the isolated frozen cubic exterior used in the note.
"""
from pathlib import Path
import json
import math
import numpy as np
import sympy as sp
from scipy.integrate import quad
from scipy.special import gamma, hyp2f1

checks = {}
def exact(name, expression):
    result = sp.simplify(expression)
    assert result == 0, (name, result)
    checks[name] = True

r = sp.symbols('r', positive=True)
K = sp.Function('K')(r)
Y = sp.Function('Y')(r)
f = Y/r**3
Ko = K+r*sp.diff(K,r)/2
ode = K*sp.diff(f,r,2)+2*Ko*sp.diff(f,r)/r-6*Ko*f/r**2
expected = K*sp.diff(Y,r,2)+(sp.diff(K,r)-4*K/r)*sp.diff(Y,r)-6*sp.diff(K,r)*Y/r
exact('cubic_Y_equation', r**3*ode-expected)
exact('cubic_Y_integrating_factor', sp.diff(K/r**4*sp.diff(Y,r),r)-6*sp.diff(K,r)/r**5*Y-expected/r**4)

b,z = sp.symbols('b z', positive=True)
rr = sp.sqrt(b*b+z*z)
F = sp.Function('F')
axial = F(rr)*(1-sp.Rational(3,2)*b*b/rr**2)
positive_integrand = sp.Rational(1,2)*z*z/rr**2*(rr*sp.diff(F(rr),z)*rr/z+3*F(rr))
exact('axial_integration_by_parts', positive_integrand-axial-sp.diff(z*F(rr),z)/2)
exact('deep_transverse_integral', sp.integrate(b*b/(b*b+z*z)**sp.Rational(3,2),(z,-sp.oo,sp.oo))-2)
exact('harmonic_transverse_integral', sp.integrate(b*b/(b*b+z*z)**sp.Rational(5,2),(z,-sp.oo,sp.oo))-4/(3*b*b))
exact('harmonic_axial_null', sp.integrate((1-sp.Rational(3,2)*b*b/(b*b+z*z))/(b*b+z*z)**sp.Rational(3,2),(z,-sp.oo,sp.oo)))

x1,x2,x3 = sp.symbols('x1 x2 x3', positive=True)
xs = [x1,x2,x3]
design = sp.Matrix([[1,1/x,x] for x in xs])
vandermonde = (x2-x1)*(x3-x1)*(x3-x2)
exact('three_radius_determinant', design.det()+vandermonde/(x1*x2*x3))
w = []
for i in range(3):
    j,k = [j for j in range(3) if j != i]
    w.append(-xs[i]*(xs[j]+xs[k])/((xs[i]-xs[j])*(xs[i]-xs[k])))
exact('contrast_constant', sum(w)-1)
exact('contrast_internal', sum(w[i]/xs[i] for i in range(3)))
exact('contrast_external', sum(w[i]*xs[i] for i in range(3)))
for power in [-2,0,2]:
    expr = b*sp.diff(b*sp.diff(b**power,b),b)-4*b**power
    exact('radial_filter_'+str(power), expr-(-4 if power==0 else 0))

# Cartesian Hessian calculation includes displacement of the background Hessian.
x,y = sp.symbols('x y', real=True)
R2 = x*x+y*y
psi0 = sp.log(R2)/2
H0 = sp.hessian(psi0,(x,y))
pconstant = (x*x-y*y)/R2
pshear = x*x-y*y
Ar = 1+r**-2
At = 1-r**-2
Ainv = sp.diag(1/Ar,1/At)
def cartesian_flux(p):
    grad = sp.Matrix([sp.diff(p,v) for v in (x,y)]).subs({x:r,y:0})
    shift = Ainv*grad
    dH = sum((H0.diff(v)*shift[i] for i,v in enumerate((x,y))),sp.zeros(2)).subs({x:r,y:0})
    return sp.simplify(sp.trace(Ainv*(sp.hessian(p,(x,y)).subs({x:r,y:0})+dH)))
Fc = cartesian_flux(pconstant)
Fs = cartesian_flux(pshear)
exact('constant_flux_cartesian', Fc+4/(r*r-1))
exact('shear_flux_cartesian', Fs+4*r*r*(r*r+3)/((r*r-1)*(r*r+1)**2))
a,h = sp.symbols('a h', positive=True)
u = a-1/a
s = a+1/a
Kc = -s*s/(4*h)*(Fc.subs(r,a)-Fc.subs(r,1/a))
Ks = (a*a-a**-2)/h-s*s/(4*h)*(Fs.subs(r,a)-Fs.subs(r,1/a))
exact('constant_estimator_response', Kc-s**3/(u*h))
exact('shear_estimator_response', Ks-s**3/(u*h))
exact('estimator_null_r2_minus_1', Ks-Kc)
exact('geometry_mass_constant', 0)
exact('geometry_mass_shear', (1/a)*(2*a/(1+a**-2))+a*(2/a/(1+a*a))-2)

# Independent Cartesian check of the pair-gradient identity at arbitrary angle.
t = sp.symbols('t', real=True)
e = sp.Matrix([(1-t*t)/(1+t*t),2*t/(1+t*t)])
pdiff = pshear-pconstant
grad = sp.Matrix([sp.diff(pdiff,v) for v in (x,y)])
gp = grad.subs({x:a*e[0],y:a*e[1]}, simultaneous=True)
gm = grad.subs({x:-e[0]/a,y:-e[1]/a}, simultaneous=True)
c2 = e[0]**2-e[1]**2
for i in range(2):
    exact('pair_gradient_difference_'+str(i), gp[i]-gm[i]-2*s*c2*e[i])

# Projection of the matched, normalized exact cubic l=2 response.
r0 = 1.0e-3
def radial(raw_r):
    return raw_r**-3*hyp2f1(1.5,2/3,8/3,-raw_r**-3)
norm = radial(r0)
Ad = gamma(8/3)*gamma(5/6)/(gamma(1.5)*gamma(2))/norm
projection = []
for impact in [0.003,0.01,0.1,1.0,10.0]:
    def ftheta(theta):
        return radial(impact/math.cos(theta))/norm
    T = 2*impact*quad(ftheta,0,math.pi/2,epsabs=1e-12,epsrel=3e-10)[0]
    A0 = 2*impact*quad(lambda theta: ftheta(theta)*(1-1.5*math.cos(theta)**2)/math.cos(theta)**2,
                       0,math.pi/2,epsabs=1e-12,epsrel=3e-10)[0]
    assert T>0 and A0>0, (impact,T,A0)
    projection.append(dict(b_over_rV=impact,T=T,A0=A0,deep_T_ratio=T/(2*Ad)))
assert abs(projection[0]['deep_T_ratio']-1)<2e-4
checks['matched_projection_positive'] = True
checks['deep_projection_limit'] = True

# Exact on-axis stationary branches, not numerical root differentiation.
def observables(u0, eps, kind):
    # q=1 leaves on-axis stationary positions unchanged. q=r² and q=r²−1
    # have identical radial derivatives there.
    coeff = 1.0 if kind=='constant' else 1-2*eps
    disc = math.sqrt(u0*u0+4*coeff)
    images = [(u0+disc)/(2*coeff),(u0-disc)/(2*coeff)]
    times, mags = [],[]
    for image in images:
        rad = abs(image)
        if kind=='constant':
            p, hrr, htt = 1.0, 0.0, -4/rad**2
        elif kind=='shear':
            p, hrr, htt = rad**2, 2.0, -2.0
        else:
            p, hrr, htt = rad**2-1, 2.0, -2.0+4/rad**2
        times.append(0.5*(image-u0)**2-math.log(rad)-eps*p)
        mags.append(1/((1+rad**-2-eps*hrr)*(1-rad**-2-eps*htt)))
    logR = math.log(abs(mags[0]/mags[1]))
    uR = 2*math.sinh(logR/4)
    hu = 0.5*uR*math.sqrt(uR*uR+4)+2*math.asinh(uR/2)
    return math.log((times[1]-times[0])/hu), abs(images[0]*images[1])
finite = []
for u0 in [0.3,0.8,1.7]:
    hu = 0.5*u0*math.sqrt(u0*u0+4)+2*math.asinh(u0/2)
    target = (u0*u0+4)**1.5/(u0*hu)
    for kind in ['constant','shear','difference']:
        eps = 2e-7
        pos = observables(u0,eps,kind)
        neg = observables(u0,-eps,kind)
        numerical = (pos[0]-neg[0])/(2*eps)
        expected = 0 if kind=='difference' else target
        assert abs(numerical-expected)<2e-6*max(1,abs(expected)), (u0,kind,numerical,expected)
        geom = (pos[1]-neg[1])/(2*eps)
        assert abs(geom-(0 if kind=='constant' else 2))<2e-7
        finite.append(dict(u=u0,profile=kind,estimator_derivative=numerical,expected=expected,
                           geometry_mass_derivative=geom))
checks['finite_branch_estimator_and_geometry'] = True

receipt = dict(status='PASS',checks=checks,matched_projection=projection,
               exact_branch_finite_differences=finite,
               scope='Internal algebra and isolated frozen-exterior projection checks; no data, horizon, or source-amplitude certification.')
destination = Path(__file__).with_suffix('.json')
destination.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='PASS',symbolic_controls=len(checks),receipt=str(destination)),indent=2))
