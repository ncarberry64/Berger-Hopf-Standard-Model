"""Illustrate nodal-plane rigidity for an EXPLICIT auxiliary free scalar action.

This is not an R1/BHSM cosmological evolution calculation. Time units use
R=c_s=1. Requires NumPy/SymPy and writes its receipt beside this source.
"""
from pathlib import Path
import csv
import json
import numpy as np
import sympy as s

I=s.eye(2)
Z=s.zeros(2)
Js=[s.Matrix([[0,0,1,0],[0,0,0,-1],[-1,0,0,0],[0,1,0,0]]),
    s.Matrix([[0,1,0,0],[-1,0,0,0],[0,0,0,1],[0,0,-1,0]])]
A=s.diag(1,-1,0,0)
PiP=s.diag(0,0,1,1)
time=s.symbols('time',real=True)
alpha=s.Rational(36,25)  # a^2=1.2^2
lambda0=s.Integer(8)
lambda2=4+4*alpha
exact=[]
for index,J in enumerate(Js):
    A0=(A+J.T*A*J)/2
    A2=(A-J.T*A*J)/2
    solution=s.cos(s.sqrt(lambda0)*time)*A0+s.cos(s.sqrt(lambda2)*time)*A2
    def L(B):
        return 8*B+4*(alpha-1)*(B-J.T*B*J)/2
    assert (s.diff(solution,time,2)+L(solution)).applyfunc(s.simplify)==s.zeros(4)
    assert solution.subs(time,0)==A
    assert s.diff(solution,time).subs(time,0)==s.zeros(4)
    if index==0:
        expected=(s.cos(s.sqrt(lambda0)*time)-s.cos(s.sqrt(lambda2)*time))/2
        assert (solution*PiP-expected*s.diag(0,0,1,-1)).applyfunc(s.simplify)==s.zeros(4)
        assert s.limit(expected/time**2,time,0)==s.Rational(11,25)
    else:
        assert A0==s.zeros(4)
        assert solution*PiP==s.zeros(4)
    exact.append({'kappa':index,'euler_equation':True,'rest_initial_data':True,
                  'nodal_plane_preserved':bool(index)})

rows=[]
max_euler_residual=0.0
max_leakage_formula_residual=0.0
for kap,J in enumerate(Js):
    j=np.asarray(J,dtype=float)
    a=np.asarray(A,dtype=float)
    pi=np.asarray(PiP,dtype=float)
    a0=(a+j.T@a@j)/2
    a2=(a-j.T@a@j)/2
    w0=np.sqrt(8.)
    w2=np.sqrt(9.76)
    for t in [0.0,0.1,0.2,0.5,1.0]:
        sol=np.cos(w0*t)*a0+np.cos(w2*t)*a2
        acc=-w0*w0*np.cos(w0*t)*a0-w2*w2*np.cos(w2*t)*a2
        lop=8*sol+4*(1.44-1)*(sol-j.T@sol@j)/2
        residual=float(np.max(np.abs(acc+lop)))
        max_euler_residual=max(max_euler_residual,residual)
        leakage=float(np.linalg.norm(sol@pi)/np.linalg.norm(a))
        expected=0.5*abs(np.cos(w0*t)-np.cos(w2*t)) if kap==0 else 0.0
        max_leakage_formula_residual=max(max_leakage_formula_residual,abs(leakage-expected))
        rows.append({'kappa':kap,'time_R_over_cs':t,
                     'relative_nodal_plane_leakage':leakage,
                     'max_euler_residual':residual})
assert max_euler_residual<1e-13
assert max_leakage_formula_residual<1e-14
receipt={
    'status':'PASS',
    'scope':'explicit auxiliary free scalar action on fixed Berger S3; no R1 cosmological extension',
    'parameters':{'a':1.2,'R':1.0,'c_s':1.0,'initial_A':'diag(1,-1,0,0)','initial_velocity':'0'},
    'exact_checks':exact,
    'small_time_leakage_coefficient_kappa0':0.44,
    'max_euler_residual':max_euler_residual,
    'max_leakage_formula_residual':max_leakage_formula_residual,
    'table':rows,
}
base=Path(__file__).parent
(base/'hopf_nodal_rigidity_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
with (base/'hopf_nodal_rigidity_table.csv').open('w',newline='',encoding='utf-8') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(json.dumps(receipt,indent=2))
