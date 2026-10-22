"""Independent first-order estimator proof checks and on-axis polynomial tests.

No general nonlinear lens solver is implemented here. Finite tests use the
exact polynomial stationary equation for even radial powers, and continue
only the two reference primary roots. All inputs are synthetic.
"""
from pathlib import Path
import json
from math import asinh, cos, log, sin, sinh, sqrt
import numpy as np
import sympy as s

r,u=s.symbols('r u',positive=True)
ar=1+r**-2
at=1-r**-2
def symbolic_F(q):
    qp=s.diff(q,r)
    return s.factor(s.diff(q,r,2)/ar+(qp/r-4*q/r**2)/at+
                    2*qp/(r**3*ar)*(1/ar-1/at))
F2=symbolic_F(r*r)
Fm2=symbolic_F(r**-2)
F0=symbolic_F(s.Integer(1))
assert s.factor(F2+4*r*r*(r*r+3)/((r*r-1)*(r*r+1)**2))==0
assert s.factor(Fm2+4*(3*r*r+1)/(r*r*(r*r-1)*(r*r+1)**2))==0
# Use u=r-1/r, sqrt(u²+4)=r+1/r on the r=r+>1 branch.
ur=r-1/r
sr=r+1/r
assert s.factor(F2-F2.subs(r,1/r)+16/(ur*sr))==0
assert s.factor(Fm2-Fm2.subs(r,1/r)+4*(ur**4+6*ur**2+4)/(ur*sr))==0
assert s.factor(F0-F0.subs(r,1/r)+4*sr/ur)==0
# Multiply K_q by h, avoiding any branch simplification of logarithms.
Kh2=s.factor(r*r-r**-2-sr**2*(F2-F2.subs(r,1/r))/4)
Khm2=s.factor(r**-2-r*r-sr**2*(Fm2-Fm2.subs(r,1/r))/4)
Kh0=s.factor(-sr**2*(F0-F0.subs(r,1/r))/4)
assert s.factor(Kh2-sr**3/ur)==0
assert s.factor(Khm2-(ur*ur+1)*sr**3/ur)==0
assert s.factor(Kh0-Kh2)==0

def h(un):
    return un*sqrt(un*un+4)/2+2*asinh(un/2)

def radial_values(coeffs,radius):
    q=sum(c*radius**k for k,c in coeffs.items())
    qp=sum(k*c*radius**(k-1) for k,c in coeffs.items())
    qpp=sum(k*(k-1)*c*radius**(k-2) for k,c in coeffs.items())
    return q,qp,qpp

def quad_cartesian(coeffs,x):
    radius=float(np.linalg.norm(x))
    er=x/radius
    et=np.array([-er[1],er[0]])
    c2=er[0]**2-er[1]**2
    s2=2*er[0]*er[1]
    q,qp,qpp=radial_values(coeffs,radius)
    grad=qp*c2*er-2*q*s2/radius*et
    local=np.array([[qpp*c2,-2*(qp/radius-q/radius**2)*s2],
                    [-2*(qp/radius-q/radius**2)*s2,(qp/radius-4*q/radius**2)*c2]])
    basis=np.column_stack((er,et))
    return q*c2,grad,basis@local@basis.T

def generic_first_variation(un,angle,potential):
    n=np.array([cos(angle),sin(angle)])
    xp=(un+sqrt(un*un+4))/2
    xs=[xp,-1/xp]
    items=[]
    for signed_radius in xs:
        x=signed_radius*n
        radius=float(np.linalg.norm(x))
        H0=np.eye(2)/radius**2-2*np.outer(x,x)/radius**4
        A=np.eye(2)-H0
        p,grad,Hp=potential(x)
        dx=np.linalg.solve(A,grad)
        dot=float(x@dx)
        DH=(-2*dot*np.eye(2)/radius**4
            -2*(np.outer(dx,x)+np.outer(x,dx))/radius**4
            +8*dot*np.outer(x,x)/radius**6)
        dA=-Hp-DH
        dlogmu=-float(np.trace(np.linalg.solve(A,dA)))
        items.append({'p':float(p),'dx':dx,'dlogmu':dlogmu})
    ddelay=items[0]['p']-items[1]['p']
    dlogR=items[0]['dlogmu']-items[1]['dlogmu']
    response=ddelay/h(un)-(un*un+4)/(4*h(un))*dlogR
    return response,ddelay,dlogR,items

def scalar_F(coeffs,radius):
    q,qp,qpp=radial_values(coeffs,radius)
    radial=1+1/radius**2
    tangent=1-1/radius**2
    return qpp/radial+(qp/radius-4*q/radius**2)/tangent+2*qp/(radius**3*radial)*(1/radial-1/tangent)

def scalar_K(coeffs,un):
    xp=(un+sqrt(un*un+4))/2
    xm=1/xp
    return ((radial_values(coeffs,xp)[0]-radial_values(coeffs,xm)[0])/h(un)
            -(un*un+4)/(4*h(un))*(scalar_F(coeffs,xp)-scalar_F(coeffs,xm)))

profiles={'compact':{-2:1.0},'external_r2':{2:1.0},'angular_constant':{0:1.0},
          'null_r2_minus1':{2:1.0,0:-1.0},'quartic':{4:1.0},
          'mixed':{-2:.03,0:.17,2:.12,4:.015}}
maximum_cartesian_scalar_difference=0.0
for coeffs in profiles.values():
    for un in [.4,.8,1.6,2.0]:
        for angle in [.0,.17,.42,.9]:
            actual=generic_first_variation(un,angle,lambda x:quad_cartesian(coeffs,x))[0]
            expected=cos(2*angle)*scalar_K(coeffs,un)
            maximum_cartesian_scalar_difference=max(maximum_cartesian_scalar_difference,abs(actual-expected)/(1+abs(expected)))
assert maximum_cartesian_scalar_difference<1e-12

# Structural controls use generic Cartesian variations, not the quad formula.
def controls(name,x):
    radius=float(np.linalg.norm(x))
    if name=='constant': return 1.,np.zeros(2),np.zeros((2,2))
    if name=='uniform_deflection': return float(np.array([.3,-.2])@x),np.array([.3,-.2]),np.zeros((2,2))
    if name=='isotropic_convergence': return radius**2/2,x,np.eye(2)
    if name=='fractional_mass':
        return log(radius),x/radius**2,np.eye(2)/radius**2-2*np.outer(x,x)/radius**4
    raise ValueError(name)
control_residuals={}
for name in ['constant','uniform_deflection','isotropic_convergence','fractional_mass']:
    target=1.0 if name=='fractional_mass' else 0.0
    errors=[]
    for un in [.4,.8,1.6,2.0]:
        for angle in [.1,.7,1.3]:
            response=generic_first_variation(un,angle,lambda x:controls(name,x))[0]
            errors.append(abs(response-target))
    control_residuals[name]=max(errors)
assert max(control_residuals.values())<2e-13

def polynomial_primary_pair(coeffs,un,epsilon):
    # Multiply the on-axis stationary equation by x^3:
    # x^4-u*x^3-x^2-epsilon*sum_k k*c_k*x^(k+2)=0.
    powers={4:1.0,3:-un,2:-1.0}
    for k,c in coeffs.items():
        if k: powers[k+2]=powers.get(k+2,0.0)-epsilon*k*c
    degree=max(k for k,v in powers.items() if v!=0)
    poly=[powers.get(k,0.0) for k in range(degree,-1,-1)]
    roots=np.roots(poly)
    real=[float(z.real) for z in roots if abs(z.imag)<1e-8 and abs(z.real)>1e-12]
    reference_plus=(un+sqrt(un*un+4))/2
    selected=[min(real,key=lambda z:abs(z-reference_plus)),min(real,key=lambda z:abs(z+1/reference_plus))]
    assert selected[0]>0 and selected[1]<0
    result=[]
    maximum_residual=0.0
    for x in selected:
        radius=abs(x)
        qv,qp,qpp=radial_values(coeffs,radius)
        stationary=x-un-1/x-epsilon*np.sign(x)*qp
        maximum_residual=max(maximum_residual,abs(stationary))
        determinant=(1+1/radius**2-epsilon*qpp)*(1-1/radius**2-epsilon*(qp/radius-4*qv/radius**2))
        mu=1/determinant
        tau=.5*(x-un)**2-log(radius)-epsilon*qv
        result.append((x,mu,tau))
    assert result[0][1]>0 and result[1][1]<0 and result[0][1]>abs(result[1][1])
    delay=result[1][2]-result[0][2]
    ratio=abs(result[0][1]/result[1][1])
    inferred_u=2*sinh(log(ratio)/4)
    logmass=log(delay/h(inferred_u))
    values=np.array([result[0][0],result[1][0],log(abs(result[0][1])),log(abs(result[1][1])),delay,logmass])
    return values,maximum_residual

maximum_polynomial_stationary_residual=0.0
maximum_fine_derivative_error=0.0
maximum_extrapolated_derivative_error=0.0
polynomial_checks=[]
for name,coeffs in profiles.items():
    for un in [.4,.8,1.6,2.0]:
        response,ddelay,_,items=generic_first_variation(un,0.0,lambda x:quad_cartesian(coeffs,x))
        expected=np.array([items[0]['dx'][0],items[1]['dx'][0],items[0]['dlogmu'],items[1]['dlogmu'],ddelay,response])
        ds=[]
        for step in [1e-5,5e-6]:
            vp,rp=polynomial_primary_pair(coeffs,un,step)
            vm,rm=polynomial_primary_pair(coeffs,un,-step)
            maximum_polynomial_stationary_residual=max(maximum_polynomial_stationary_residual,rp,rm)
            ds.append((vp-vm)/(2*step))
        extrapolated=(4*ds[1]-ds[0])/3
        fine_error=float(np.max(np.abs(ds[1]-expected)/(1+np.abs(expected))))
        extrapolated_error=float(np.max(np.abs(extrapolated-expected)/(1+np.abs(expected))))
        maximum_fine_derivative_error=max(maximum_fine_derivative_error,fine_error)
        maximum_extrapolated_derivative_error=max(maximum_extrapolated_derivative_error,extrapolated_error)
        polynomial_checks.append({'profile':name,'u':un,'analytic_dlogM':response,'extrapolated_dlogM':float(extrapolated[-1]),'maximum_scaled_derivative_error':extrapolated_error})
assert maximum_polynomial_stationary_residual<2e-12
assert maximum_extrapolated_derivative_error<2e-7

# The nontrivial null is only first order: quantify one finite quadratic effect.
null_value=polynomial_primary_pair(profiles['null_r2_minus1'],1.0,.001)[0][-1]
assert abs(scalar_K(profiles['null_r2_minus1'],1.0))<1e-13
assert abs(null_value)>1e-7
receipt={
    'status':'PASS',
    'scope':'first variation of two continued primary thin-lens images; synthetic on-axis polynomial checks',
    'symbolic_checks':{'compact_F':True,'external_F':True,'compact_K':'(u**2+1)*Kstar','external_r2_K':'Kstar','angular_constant_K':'Kstar','first_order_null_r2_minus1':True},
    'maximum_cartesian_scalar_scaled_difference':maximum_cartesian_scalar_difference,
    'structural_control_absolute_residuals':control_residuals,
    'polynomial_stationary_equation_maximum_absolute_residual':maximum_polynomial_stationary_residual,
    'polynomial_fine_central_derivative_maximum_scaled_error':maximum_fine_derivative_error,
    'polynomial_extrapolated_derivative_maximum_scaled_error':maximum_extrapolated_derivative_error,
    'finite_null_profile_example':{'u':1.0,'epsilon':.001,'log_Mapp_over_M':float(null_value),'interpretation':'nonzero quadratic departure; not an exact finite invariant'},
    'polynomial_checks':polynomial_checks,
}
target=Path(__file__).with_name('perturbed_mass_estimator_receipt.json')
target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
