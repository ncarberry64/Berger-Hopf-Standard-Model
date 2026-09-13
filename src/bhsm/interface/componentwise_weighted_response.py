"""Recover component bounds from a proved weighted Neumann enclosure."""
import numpy as np
from flint import arb,fmpq
from bhsm.interface.affine_eigenpair_contraction import _balls
from bhsm.interface.weighted_response_enclosure import enclose_response


def enclose_response_rows(center,preconditioned_residual,weights,defect_row_bounds):
    """Use |error_i| <= |residual_i| + V_i*||error||_weights.

    The caller owns exactly the same family and residual bindings as for the
    original enclosure. This adds no action or eigenpair assumptions.
    """
    _,proof=enclose_response(center,preconditioned_residual,weights,defect_row_bounds)
    z,e,r,V=map(_balls,(center,preconditioned_residual,weights,defect_row_bounds))
    scale=arb(fmpq(proof['weighted_error_upper_rational']))
    radii=np.array([min((abs(ee).upper()+vv*scale).upper(),(rr*scale).upper())
                    for ee,rr,vv in zip(e,r,V,strict=True)],dtype=object)
    result=np.array([zz+arb(0,rad) for zz,rad in zip(z,radii,strict=True)],dtype=object)
    proof=dict(proof,componentwise_residual_plus_defect_bound=True,
               component_radii_upper_rational=[str(v.fmpq()) for v in radii])
    return result,proof
