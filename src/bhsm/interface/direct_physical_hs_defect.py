"""Fixed-preconditioner local defects from direct physical HS derivatives."""
import numpy as np
from flint import arb_mat, ctx
from bhsm.interface import direct_physical_hs_jacobian as hs


def local_defect_blocks(left_df, midpoint_df, right_df, step,
                        trial_left, trial_right, test, frozen_left, frozen_right,
                        *, initial_endpoint_fixed=False, precision=512):
    """Enclose C, DL, DR in v_next = -C*v_prev + DL*u_prev + DR*u_next.

    C = R^-1 T L E0, DL = R^-1 T (L-Dr0) E0,
    DR = I-R^-1 T Dr1 E1. Fixed frames and frozen L/R are supplied by the
    caller; physical frame derivatives and quotient identification are not
    established by this algebra. A fixed initial endpoint contributes no DL.
    """
    if type(initial_endpoint_fixed) is not bool:
        raise ValueError('explicit boolean initial endpoint condition required')
    if type(precision) is not int or precision<64:
        raise ValueError('at least 64 bits of arithmetic precision required')
    previous=ctx.prec;ctx.prec=precision
    try:
        blocks=hs.physical_hs_blocks(left_df,midpoint_df,right_df,step,precision=precision)
        l=hs._matrix(frozen_left)
        r=hs._matrix(frozen_right)
        n=blocks['residual_left'].nrows()
        if l.nrows()!=n or l.ncols()!=n:raise ValueError('matching ambient frozen left block required')
        c=hs.fixed_frame_pullback(l,trial_left,test,r,precision=precision)
        dl=hs.fixed_frame_pullback(l-blocks['residual_left'],trial_left,test,r,precision=precision)
        new_right=hs.fixed_frame_pullback(blocks['residual_right'],trial_right,test,r,precision=precision)
        k=r.nrows()
        if any(m.nrows()!=k or m.ncols()!=k for m in (c,dl,new_right)):
            raise ValueError('square reduced local blocks required')
        dr=arb_mat(np.eye(k,dtype=int).tolist())-new_right
        if initial_endpoint_fixed:dl=arb_mat(k,k)
        return dict(C=c,DL=dl,DR=dr)
    finally:ctx.prec=previous
