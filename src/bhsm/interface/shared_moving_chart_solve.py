"""Pointwise residual correction using an already certified moving inverse.

The moving preconditioner is a numerical representation. Physical derivatives
come from the defining K z=b equation, not derivatives of Taylor enclosures.
"""
from flint import arb
from bhsm.interface.shared_action_taylor import Taylor
from bhsm.interface.shared_implicit_response_jet import matvec, _domain


def solve(rhs, apply_operator, moving_preconditioner, weights, defect_upper):
    d=_domain(list(rhs));n=len(rhs);w=list(weights);q=arb(defect_upper)
    R=moving_preconditioner
    if (len(R)!=n or any(len(row)!=n for row in R) or len(w)!=n
            or any(not x>0 or not x.rad().is_zero() for x in w)
            or not 0<=q<1):
        raise ValueError('complete moving inverse, positive exact weights and certified q<1 required')
    if any(not isinstance(v,Taylor) or v.domain is not d for row in R for v in row):
        raise ValueError('moving inverse must retain the same parameter namespace')
    proposal=matvec(R,rhs)
    predictor=[d.affine(v.c.mid(),[a.mid() for a in v.a.entries()]) for v in proposal]
    applied=apply_operator(predictor)
    if len(applied)!=n or _domain(list(applied)) is not d:
        raise ValueError('complete same-domain physical operator required')
    residual=matvec(R,[b-a for b,a in zip(rhs,applied,strict=True)])
    eta=max((v.support()/wi).upper() for v,wi in zip(residual,w,strict=True))
    correction=(eta/(1-q)).upper()
    return [Taylor(d,p.c,p.a,(wi*correction).upper()) for p,wi in zip(predictor,w,strict=True)],dict(
        weighted_residual_upper=eta,weighted_correction_upper=correction,
        certified_domain_defect_upper=q,preconditioned_residual=residual)
