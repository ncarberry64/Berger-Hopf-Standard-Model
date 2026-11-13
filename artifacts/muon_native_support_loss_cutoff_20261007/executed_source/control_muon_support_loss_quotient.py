"""Independent analytic branch control; not a BHSM event or operator."""
from __future__ import annotations
import numpy as np
import sympy as sp

from bhsm.interface.muon_native_support_loss_cutoff import (
    quadratic_form_branch_jets,cutoff_from_total_contractions,
)


def control_expressions():
    x,y,t = sp.symbols('x y t', real=True)
    # The prescribed surface is a CHAIN-RULE CONTROL only; no physical event
    # is selected by it. The forms and line include both explicit and t motion.
    surface = sp.Rational(3,10)*x-sp.Rational(1,5)*y+sp.Rational(3,20)*x*y
    p = sp.Matrix([1+x/5+3*y/10+t/7+x*y/10,
                   sp.Rational(1,10)+2*x/5-y/5-t/9+x*y/4])
    R = sp.Matrix([[4+x/5+t/3,1+x/10-y/8],[1+x/10-y/8,3+y/4-t/6+x*y/7]])
    I = sp.Matrix([[2-y/8+t/5,sp.Rational(1,10)+x/9],[sp.Rational(1,10)+x/9,sp.Rational(3,2)+x/7+t/4-x*y/6]])
    return x,y,surface,p.subs(t,surface),R.subs(t,surface),I.subs(t,surface)


def execute_control():
    x,y,surface,p,R,I = control_expressions()
    zero={x:0,y:0}
    def jet(f):
        return [np.array(g.subs(zero),dtype=float) for g in (f,sp.diff(f,x),sp.diff(f,y),sp.diff(f,x,y))]
    pv,px,py,pxy = [z.reshape(-1) for z in jet(p)]
    R0,Rx,Ry,Rxy = jet(R);I0,Ix,Iy,Ixy = jet(I)
    r = quadratic_form_branch_jets(R0,pv,K_x=Rx,K_y=Ry,K_xy=Rxy,psi_x=px,psi_y=py,psi_xy=pxy)
    i = quadratic_form_branch_jets(I0,pv,K_x=Ix,K_y=Iy,K_xy=Ixy,psi_x=px,psi_y=py,psi_xy=pxy)
    c = cutoff_from_total_contractions(r,i)
    exactr=(p.T*R*p)[0];exacti=(p.T*I*p)[0];exact=exacti/exactr
    direct=dict(value=float(exact.subs(zero)),x=float(sp.diff(exact,x).subs(zero)),
                y=float(sp.diff(exact,y).subs(zero)),xy=float(sp.diff(exact,x,y).subs(zero)))
    evaluate=sp.lambdify((x,y),exact,'numpy')
    fd=[]
    for h in (1e-3,5e-4,2.5e-4):
        value=(evaluate(h,h)-evaluate(h,-h)-evaluate(-h,h)+evaluate(-h,-h))/(4*h*h)
        fd.append(dict(step=h,c_xy=float(value),absolute_error=float(abs(value-c['c_xy']))))
    def scalar(j):return {k:float(complex(j[k]).real) for k in ('value','x','y','xy')}
    report=dict(classification='SUPPLIED_ARITHMETIC_BRANCH_CONTROL__NO_PHYSICAL_SUPPORT_LOSS',
        r=scalar(r),i=scalar(i),c={k:float(complex(c[k]).real) for k in ('c','c_x','c_y','c_xy')},
        independent_symbolic=direct,finite_differences=fd,
        mode_not_assumed_R_eigenvector=True,total_event_motion_included_once=True,
        second_embedding_terms_retained=True,
        max_symbolic_difference=max(float(abs(c[k]-direct[j])) for k,j in (('c','value'),('c_x','x'),('c_y','y'),('c_xy','xy'))),
        error_scope='binary64 consistency and exact symbolic identity; no rigorous FD remainder, continuum or physical error bound')
    arrays=dict(R=R0,R_x=Rx,R_y=Ry,R_xy=Rxy,I=I0,I_x=Ix,I_y=Iy,I_xy=Ixy,
                psi=pv,psi_x=px,psi_y=py,psi_xy=pxy)
    return report,arrays
