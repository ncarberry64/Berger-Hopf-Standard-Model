"""Exact and random checks of the stationary-nodal great-circle Hopf bound.

Requires NumPy and SymPy. Writes a receipt beside this file and does not modify
any inherited research source. See hopf_nodal_bound.md for assumptions/proof.
"""
from pathlib import Path
import json
import numpy as np
import sympy as s

u,v = s.symbols('u v', real=True)
j12,j13,j14,j23,j24,j34 = s.symbols('j12 j13 j14 j23 j24 j34', real=True)
Jgeneric=s.Matrix([[0,j12,j13,j14],[-j12,0,j23,j24],[-j13,-j23,0,j34],[-j14,-j24,-j34,0]])
A=s.Matrix([[u,v,0,0],[v,-u,0,0],[0,0,0,0],[0,0,0,0]])
norm2=s.trace(A*A)
assert s.expand(s.trace(A*Jgeneric.T*A*Jgeneric)+j12**2*norm2)==0

# An exact rational family spans kappa in [0,1], including both endpoints.
t,alpha = s.symbols('t alpha', real=True)
kappa=2*t/(1+t*t)
q=(1-t*t)/(1+t*t)
J=s.Matrix([[0,kappa,q,0],[-kappa,0,0,-q],[-q,0,0,kappa],[0,q,-kappa,0]])
assert (J.T*J-s.eye(4)).applyfunc(s.simplify)==s.zeros(4)
assert (J*J+s.eye(4)).applyfunc(s.simplify)==s.zeros(4)
A0=(A+J.T*A*J)/2
A2=(A-J.T*A*J)/2
assert (A0*J-J*A0).applyfunc(s.simplify)==s.zeros(4)
assert (A2*J+J*A2).applyfunc(s.simplify)==s.zeros(4)
assert s.simplify(s.trace(A2*A2)/norm2-(1+kappa*kappa)/2)==0
assert s.simplify(s.trace(A0*A2))==0

# Verify the differential operator directly, rather than calling spectral code.
x=s.Matrix(s.symbols('x0:4', real=True))
def K(f):
    return s.expand(sum((J*x)[i]*s.diff(f,x[i]) for i in range(4)))
F=(x.T*A*x)[0]
F2=(x.T*A2*x)[0]
assert s.simplify(K(K(F))+4*F2)==0
operator_matrix=8*A+4*(alpha-1)*A2
rayleigh=s.trace(A*operator_matrix)/norm2
assert s.simplify(rayleigh-(8+2*(alpha-1)*(1+kappa*kappa)))==0
assert s.simplify(s.diff(rayleigh,alpha)-2*(1+kappa*kappa))==0

# General J obtained by orthogonal conjugation covers both complex orientations.
rng=np.random.default_rng(20261021)
Jstandard=np.array([[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]],dtype=float)
residuals={key:0.0 for key in ['trace_identity','charged_fraction','sector_orthogonality','rayleigh','complex_structure','nodal_support']}
minimum_fraction=1.0
maximum_fraction=0.0
orientation_counts={'positive':0,'negative':0}
for index in range(258):
    if index<2:
        k=float(index)
        z=float(np.sqrt(1-k*k))
        j=np.array([[0,k,z,0],[-k,0,0,-z],[-z,0,0,k],[0,z,-k,0]],dtype=float)
    else:
        o,_=np.linalg.qr(rng.normal(size=(4,4)))
        if index%2:
            o[:,0]*=-1
        j=o@Jstandard@o.T
    # Pfaffian is +1 or -1 and records both orientation classes.
    pf=j[0,1]*j[2,3]-j[0,2]*j[1,3]+j[0,3]*j[1,2]
    orientation_counts['positive' if pf>0 else 'negative']+=1
    c=rng.normal(size=2)
    c/=np.linalg.norm(c)
    a=np.array([[c[0],c[1],0,0],[c[1],-c[0],0,0],[0,0,0,0],[0,0,0,0]])
    n=float(np.sum(a*a))
    a0=(a+j.T@a@j)/2
    a2=(a-j.T@a@j)/2
    kap=abs(float(j[0,1]))
    f2=float(np.sum(a2*a2)/n)
    minimum_fraction=min(minimum_fraction,f2)
    maximum_fraction=max(maximum_fraction,f2)
    residuals['trace_identity']=max(residuals['trace_identity'],abs(float(np.trace(a@j.T@a@j))+kap*kap*n))
    residuals['charged_fraction']=max(residuals['charged_fraction'],abs(f2-(1+kap*kap)/2))
    residuals['sector_orthogonality']=max(residuals['sector_orthogonality'],abs(float(np.sum(a0*a2)))/n)
    residuals['complex_structure']=max(residuals['complex_structure'],float(np.max(np.abs(j@j+np.eye(4)))))
    # Multiple inverse-fibre scales, including a<1 and the exact round limit.
    for inverse_fibre_scale in [0.4,1.0,1.157054135733433,2.3]:
        alpha_value=inverse_fibre_scale**2
        lmat=8*a+4*(alpha_value-1)*a2
        actual=float(np.sum(a*lmat)/n)
        expected=8+4*(alpha_value-1)*(1+kap*kap)/2
        residuals['rayleigh']=max(residuals['rayleigh'],abs(actual-expected))
    for chi in [0.0,0.31,1.2,2.7]:
        point=np.array([0,0,np.cos(chi),np.sin(chi)])
        residuals['nodal_support']=max(residuals['nodal_support'],float(np.linalg.norm(a@point)))
assert all(value<3e-13 for value in residuals.values()),residuals
assert abs(minimum_fraction-0.5)<1e-14 and abs(maximum_fraction-1)<1e-14
assert all(orientation_counts.values())
receipt={
    'status':'PASS',
    'scope':'stationary-nodal GREAT CIRCLE scalar geometry; not a squashed-spacetime optical prediction',
    'exact_checks':{
        'generic_skew_J_trace_identity':True,
        'orthogonal_complex_family':True,
        'charged_fraction':'(1+kappa**2)/2',
        'charged_fraction_range':[0.5,1.0],
        'Hopf_differential_operator_K2F_equals_minus4F2':True,
        'Rayleigh_quotient_times_R2':'8+2*(a**2-1)*(1+kappa**2)',
        'd_Rayleigh_d_a2_times_R2':'2*(1+kappa**2)',
        'susceptibility_range_times_R2':[2.0,4.0],
    },
    'numerical_checks':{
        'seed':20261021,'samples':258,'inverse_fibre_scales':[0.4,1.0,1.157054135733433,2.3],
        'complex_orientation_counts':orientation_counts,
        'minimum_charged_fraction':minimum_fraction,'maximum_charged_fraction':maximum_fraction,
        'maximum_absolute_residuals':residuals,
    },
}
target=Path(__file__).with_name('hopf_nodal_bound_receipt.json')
target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
