"""Preserve endpoint affine directions in an actual HS midpoint outer domain."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls
from bhsm.interface.direct_physical_neighborhood import exact_radius,unweight_box


def midpoint_domain(left,right,left_frame,right_frame,left_axis,right_axis,
                    left_rate,right_rate,step,weights,longitudinal_radii,transverse_radii):
    """Enclose (zL+zR)/2+h*(F(zL)-F(zR))/8 as an affine product domain.

    The caller must supply uniform rates on the entire two endpoint tubes.
    Independent rate remainder intervals enlarge that domain conservatively;
    a center-only rate cannot be substituted. No unit-axis assumption is made.
    """
    a,b,EL,ER,eL,eR,fL,fR,w=map(_balls,(left,right,left_frame,right_frame,left_axis,right_axis,left_rate,right_rate,weights))
    if (a.ndim!=1 or a.size<2 or b.shape!=a.shape or fL.shape!=a.shape or fR.shape!=a.shape
            or w.shape!=(a.size-1,) or EL.ndim!=2 or EL.shape[0]!=a.size or not EL.shape[1]
            or ER.shape!=EL.shape or eL.shape!=(EL.shape[1],) or eR.shape!=eL.shape):
        raise ValueError('complete matching endpoint, field and affine operands required')
    if not all(v>0 and v.rad().is_zero() for v in w):
        raise ValueError('positive exact state weights required')
    h=exact_radius(step)
    if not h>0:raise ValueError('positive exact HS step required')
    if len(longitudinal_radii)!=2 or len(transverse_radii)!=2:
        raise ValueError('separate radii for both endpoints required')
    rL=[exact_radius(v) for v in longitudinal_radii]
    rT=[exact_radius(v) for v in transverse_radii]
    fLc=np.array([v.mid() for v in fL],dtype=object)
    fRc=np.array([v.mid() for v in fR],dtype=object)
    center_ball=unweight_box((a+b)/2+h*(fLc-fRc)/8,w)
    center=np.array([v.mid() for v in center_ball],dtype=object)
    error=center_ball-center+unweight_box(h*((fL-fLc)-(fR-fRc))/8,w)
    box_radii=np.array([abs(v).upper() for v in error],dtype=object)
    T=[np.stack([unweight_box(E[:,j]/2,w) for j in range(E.shape[1])],axis=1) for E in (EL,ER)]
    U=[matrix@axis for matrix,axis in zip(T,(eL,eR),strict=True)]
    box=np.full((a.size,a.size),arb(0),dtype=object)
    for i,r in enumerate(box_radii):box[i,i]=r
    directions=np.column_stack((U[0],U[1],T[0],T[1],box))
    k=EL.shape[1]
    groups=[dict(start=0,stop=1,norm='interval',radius=rL[0]),
            dict(start=1,stop=2,norm='interval',radius=rL[1]),
            dict(start=2,stop=2+k,norm='euclidean',radius=rT[0]),
            dict(start=2+k,stop=2+2*k,norm='euclidean',radius=rT[1]),
            dict(start=2+2*k,stop=2+2*k+a.size,norm='box',radius=arb(1))]
    hull_radii=group_row_bounds(directions,groups)
    hull=np.array([v+arb(0,r) for v,r in zip(center,hull_radii,strict=True)],dtype=object)
    return dict(raw_center=center,raw_directions=directions,raw_segment_hull=hull,
                raw_rate_remainder_radii=box_radii,groups=groups)


def group_row_bounds(derivatives,groups):
    """Bound signed directional derivatives on the complete product domain."""
    d=_balls(derivatives)
    if d.ndim!=2 or not all(d.shape):raise ValueError('complete derivative matrix required')
    result=np.full(d.shape[0],arb(0),dtype=object);next_column=0
    for group in groups:
        start,stop,norm=group['start'],group['stop'],group['norm']
        if type(start) is not int or type(stop) is not int or start!=next_column or not start<stop<=d.shape[1]:
            raise ValueError('ordered disjoint groups must cover every direction')
        radius=exact_radius(group['radius'])
        if norm not in ('interval','euclidean','box') or (norm=='interval' and stop-start!=1):
            raise ValueError('explicit interval, Euclidean-ball or box group required')
        for i,row in enumerate(d[:,start:stop]):
            if norm=='euclidean':bound=sum((abs(v).upper()**2 for v in row),arb(0)).upper().sqrt()
            else:bound=sum((abs(v).upper() for v in row),arb(0))
            result[i]+=radius*bound
        next_column=stop
    if next_column!=d.shape[1]:raise ValueError('all directions must be included')
    return np.array([v.upper() for v in result],dtype=object)
