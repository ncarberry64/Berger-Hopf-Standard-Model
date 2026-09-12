"""Use a proved coupled eigenpair contraction for multiple physical RHS columns."""
import numpy as np
from flint import arb,arb_mat
from bhsm.interface.affine_eigenpair_contraction import _balls
from bhsm.interface.weighted_response_enclosure import enclose_response


def enclose_columns(preconditioner,rhs,weights,defect_row_bounds):
    """Enclose K^-1 rhs where K=J diag(I,-1) on the already proved family.

    The caller owns the proof that R, weights and defect bounds refer to this
    same J. A zero center needs only R*rhs; no inverse of an independent-entry
    matrix hull is asserted. The final coordinate changes sign on return.
    """
    R,b,r,V=map(_balls,(preconditioner,rhs,weights,defect_row_bounds))
    if (R.ndim!=2 or R.shape[0]!=R.shape[1] or not R.shape[0]
            or b.ndim!=2 or b.shape[0]!=R.shape[0] or not b.shape[1]
            or r.shape!=(R.shape[0],) or V.shape!=r.shape):
        raise ValueError('complete compatible preconditioner, RHS and contraction bounds required')
    if not all(v.rad().is_zero() for v in R.flat):
        raise ValueError('fixed exact preconditioner required')
    residual=arb_mat(R.shape[0],R.shape[1],list(R.flat))*arb_mat(b.shape[0],b.shape[1],list(b.flat))
    residual=np.array(residual.entries(),dtype=object).reshape(b.shape)
    result=np.empty_like(b);proofs=[]
    for column in range(b.shape[1]):
        result[:,column],proof=enclose_response(np.full(r.shape,arb(0)),residual[:,column],r,V)
        result[-1,column]=-result[-1,column]
        proofs.append(proof)
    return result,residual,proofs
