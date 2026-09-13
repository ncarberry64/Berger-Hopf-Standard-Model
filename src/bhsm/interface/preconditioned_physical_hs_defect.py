"""Equivalent local HS algebra with fixed preconditioning performed first."""
import numpy as np
from flint import arb,arb_mat,ctx
from bhsm.interface import direct_physical_hs_jacobian as hs


def local_defect_blocks(left_df,midpoint_df,right_df,step,trial_left,trial_right,
                        test,frozen_left,frozen_right,*,initial_endpoint_fixed=False,
                        association='preconditioned_chain',precision=512):
    """Enclose the unchanged frozen C/DL/DR with explicit product association.

    Input domains, branch validity and physical quotient claims remain owned
    by the caller. No midpoint or radius of an uncertain input is discarded.
    """
    if association not in ('solve_first','preconditioned_chain','combined_endpoint_coefficient'):
        raise ValueError('explicit supported HS product association required')
    if type(initial_endpoint_fixed) is not bool:raise ValueError('explicit initial endpoint condition required')
    if type(precision) is not int or precision<64:raise ValueError('at least 64 bits of precision required')
    previous=ctx.prec;ctx.prec=precision
    try:
        a,m,b,e0,e1,t,l,r=map(hs._matrix,(left_df,midpoint_df,right_df,trial_left,trial_right,test,frozen_left,frozen_right))
        n=a.nrows();k=r.nrows();h=arb(step)
        if (any(x.nrows()!=n or x.ncols()!=n for x in (a,m,b,l))
                or any(x.nrows()!=n or x.ncols()!=k for x in (e0,e1))
                or t.nrows()!=k or t.ncols()!=n or r.ncols()!=k):
            raise ValueError('complete compatible physical derivatives and frozen frames required')
        if not h.is_finite() or not h.rad().is_zero() or not h>0:raise ValueError('positive exact step required')
        try:p=r.solve(t)
        except (ValueError,ZeroDivisionError) as error:raise ArithmeticError('fixed right preconditioner unresolved') from error
        identity=arb_mat(np.eye(n,dtype=int).tolist());reduced_identity=arb_mat(np.eye(k,dtype=int).tolist())
        c=p*l*e0
        if association=='solve_first':
            blocks=hs.physical_hs_blocks(a,m,b,h,precision=precision)
            dl=p*(l-blocks['residual_left'])*e0
            dr=reduced_identity-p*blocks['residual_right']*e1
        else:
            pm=p*m;ae=a*e0;be=b*e1
            fixed_left=p*(l+identity)*e0
            if association=='preconditioned_chain':
                dl=fixed_left+(p*ae)*(h/6)+(pm*(e0/2+ae*(h/8)))*(2*h/3)
                dr=reduced_identity-p*e1+(p*be)*(h/6)+(pm*(e1/2-be*(h/8)))*(2*h/3)
            else:
                dl=fixed_left+(pm*e0)*(h/3)+(p*(h/6)+pm*(h*h/12))*ae
                dr=reduced_identity-p*e1+(pm*e1)*(h/3)+(p*(h/6)-pm*(h*h/12))*be
        if initial_endpoint_fixed:dl=arb_mat(k,k)
        result=dict(C=c,DL=dl,DR=dr)
        if not all(v.is_finite() for matrix in result.values() for v in matrix.entries()):
            raise ArithmeticError('finite preconditioned physical HS blocks required')
        return result
    finally:ctx.prec=previous
