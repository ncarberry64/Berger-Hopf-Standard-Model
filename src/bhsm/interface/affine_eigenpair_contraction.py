"""Weighted Banach bounds after signed action contractions on an affine tube."""
import numpy as np
from flint import arb
from bhsm.interface.physical_arb_inputs import preserve_ball
from bhsm.interface.direct_physical_neighborhood import exact_radius
from bhsm.interface.current_green_midpoint_coordinate_error import _float_upper


def _balls(values):
    a=np.asarray(values,dtype=object)
    result=np.array([preserve_ball(v) for v in a.flat],dtype=object).reshape(a.shape)
    if not all(v.is_finite() for v in result.flat):
        raise ValueError('finite interval operands required')
    return result


def affine_row_bounds(signed_derivatives,rL,rT):
    """Bound common L plus a Euclidean transverse ball after signed contraction.

    Column zero is the complete longitudinal action contraction. Every remaining
    column is a complete transverse contraction, with all contributions summed
    before taking absolute values. This routine does not establish those facts.
    """
    d=_balls(signed_derivatives)
    if d.ndim!=2 or not d.shape[0] or d.shape[1]<2:
        raise ValueError('longitudinal and complete transverse derivative columns required')
    rL,rT=exact_radius(rL),exact_radius(rT)
    return np.array([(rL*abs(row[0]).upper()+rT*sum((abs(v).upper()**2 for v in row[1:]),arb(0)).upper().sqrt()).upper()
                     for row in d],dtype=object)


def nonlinear_eigenpair_variation(preconditioner,radii):
    """Bound the p/lambda dependence of I-R*D(Hp-lambda*p,(p^Tp-1)/2).

    The factor two includes both the variable-lambda diagonal block and the
    variable-vector last column. The last row contributes the squared radii.
    """
    R,r=_balls(preconditioner),_balls(radii)
    if r.ndim!=1 or r.size<2 or R.shape!=(r.size,r.size):
        raise ValueError('square preconditioner and matching eigenpair radii required')
    if not all(v>0 and v.rad().is_zero() for v in r):
        raise ValueError('exact positive eigenpair proposal radii required')
    squared=sum((v*v for v in r[:-1]),arb(0))
    return np.array([(2*r[-1]*sum((abs(a).upper()*b for a,b in zip(row[:-1],r[:-1])),arb(0))
                      +abs(row[-1]).upper()*squared).upper() for row in R],dtype=object)


def certify_rows(residual_bounds,center_defect,preconditioner,radii,state_variation):
    """Check uniform self-inclusion and contraction from caller-owned bounds.

    center_defect encloses I-R*J at the fixed center. state_variation already
    includes the proposed vector radii, through a signed third-action leg.
    Passing these inequalities alone does not bind an action, domain or index.
    """
    Y,D,R,r,S=map(_balls,(residual_bounds,center_defect,preconditioner,radii,state_variation))
    if r.ndim!=1 or r.size<2 or Y.shape!=r.shape or S.shape!=r.shape or D.shape!=(r.size,r.size):
        raise ValueError('matching complete row operands required')
    if not all(v>=0 for a in (Y,S) for v in a):
        raise ValueError('nonnegative residual and state-variation bounds required')
    nonlinear=nonlinear_eigenpair_variation(R,r)
    variation=np.array([(sum((abs(a).upper()*b for a,b in zip(row,r)),arb(0))+s+n).upper()
                        for row,s,n in zip(D,S,nonlinear)],dtype=object)
    rows=[]
    for i in range(r.size):
        margin=(r[i]-Y[i].upper()-variation[i]).lower()
        contraction_margin=(r[i]-variation[i]).lower()
        rows.append(dict(coordinate=i,strict_inclusion=bool(margin>0),strict_contraction=bool(contraction_margin>0),
            inclusion_margin_lower_rational=str(margin.fmpq()),
            contraction_margin_lower_rational=str(contraction_margin.fmpq()),
            image_radius_ratio_upper=_float_upper((Y[i].upper()+variation[i])/r[i]),
            weighted_contraction_upper=_float_upper(variation[i]/r[i])))
    return variation,dict(rows=rows,validation_passed=all(x['strict_inclusion'] and x['strict_contraction'] for x in rows),
        maximum_image_radius_ratio_upper=max(x['image_radius_ratio_upper'] for x in rows),
        weighted_contraction_upper=max(x['weighted_contraction_upper'] for x in rows),
        action_domain_bound=False,physical_spectral_index_verified=False,FULL_BHSM_COMPLETE=False)


def grow_failed_coordinates(residual_bounds,variation_bounds,radii):
    """Deterministic proposal update; never change a physical domain radius."""
    Y,V,r=map(_balls,(residual_bounds,variation_bounds,radii))
    if r.ndim!=1 or Y.shape!=r.shape or V.shape!=r.shape or not r.size:
        raise ValueError('matching nonempty row bounds required')
    if not all(v>=0 for a in (Y,V) for v in a) or not all(v>0 and v.rad().is_zero() for v in r):
        raise ValueError('nonnegative bounds and exact positive radii required')
    result=r.copy();changed=[]
    for i in range(r.size):
        image=(Y[i]+V[i]).upper()
        if not image<r[i]:
            result[i]=(3*image/2).upper();changed.append(i)
    return result,changed
