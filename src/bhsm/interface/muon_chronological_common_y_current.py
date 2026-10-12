"""Coupled GG/GH/HG/HH current coefficients on one unchanged field action.

This uses two completed family responses to the SAME original K, without
another inverse.  The pure gauge source is checked exactly; the scalar
source scales by the retained fixed Yukawa.  All field/H/Gauss/frame rows
remain in the responses, including both coupled mixed placements.
"""
from __future__ import annotations
import numpy as np


def common_y_current_chunk(y_middle,y_light,middle,light,*,scalar_rows):
    """Recover source-affine responses and contract all four source orders.

    u_H=(u_m-u_e)/(Y_m-Y_e), u_G=(Y_m*u_e-Y_e*u_m)/(Y_m-Y_e),
    and independently p_H,p_G from literal transpose responses.
    C(Y)=C_GG+Y*(C_GH+C_HG)+Y^2*C_HH.
    The inferred response difference is binary64, with its amplification
    exported.  This algebraic protected GG cancellation is not a solve or
    physical-overlap certificate.
    """
    ys=np.asarray([y_middle,y_light])
    if ys.dtype.kind not in 'fiu' or ys.shape!=(2,) or not np.isfinite(ys).all():
        raise ValueError('two explicit finite REAL fixed Yukawa coefficients required')
    ym,ye=map(float,ys)
    if ym<=0 or ye<=0 or ym==ye:raise ValueError('distinct nonzero fixed family Yukawas required')
    names=('original_literal_right_current_source','original_literal_left_transpose_source',
           'original_current_response','original_transpose_current_adjoint')
    ma,ea=({k:np.asarray(a[k],complex)for k in names}for a in(middle,light))
    shape=ma[names[0]].shape
    rows=np.asarray(scalar_rows)
    if (len(shape)!=3 or rows.ndim!=1 or rows.dtype.kind not in 'iu'
        or len(np.unique(rows))!=len(rows) or np.any(rows<0) or np.any(rows>=shape[1])
        or not len(rows) or any(x.shape!=shape or not np.isfinite(x).all()for a in(ma,ea)for x in a.values())):
        raise ValueError('all common original rows and explicit scalar-coordinate incidence required')
    gauge=np.ones(shape[1],bool);gauge[rows]=False
    for k in names[:2]:
        if not np.array_equal(ma[k][:,gauge],ea[k][:,gauge]):
            raise ValueError('pure gauge/frame source is not identical on this common action')
    sources=[];unit_defect=0.;unit_scale=0.
    for k in names[:2]:
        g=ma[k].copy();g[:,rows]=0
        h=np.zeros_like(g);h[:,rows]=ma[k][:,rows]/ym
        d=ea[k][:,rows]/ye-h[:,rows]
        unit_defect=max(unit_defect,float(np.max(abs(d))))
        unit_scale=max(unit_scale,float(np.max(abs(h))))
        sources.append((g,h))
    if unit_defect>64*np.finfo(float).eps*max(unit_scale,np.finfo(float).tiny):
        raise ValueError('scalar current is not the same retained fixed-Y unit vertex')
    rg,rh=sources[0];lg,lh=sources[1];dy=ym-ye
    uh=(ma[names[2]]-ea[names[2]])/dy
    ug=(ym*ea[names[2]]-ye*ma[names[2]])/dy
    ph=(ma[names[3]]-ea[names[3]])/dy
    pg=(ym*ea[names[3]]-ye*ma[names[3]])/dy
    flat=lambda a:a.reshape(-1,shape[2])
    ordered=np.array([flat(l).T@flat(u)for l,u in((lg,ug),(lg,uh),(lh,ug),(lh,uh))])
    transpose=np.array([flat(p).T@flat(r)for p,r in((pg,rg),(pg,rh),(ph,rg),(ph,rh))])
    coef=np.array([ordered[0],ordered[1]+ordered[2],ordered[3]])
    tcoef=np.array([transpose[0],transpose[1]+transpose[2],transpose[3]])
    evaluate=lambda y,c:c[0]+y*c[1]+y*y*c[2]
    direct=np.array([flat(a[names[1]]).T@flat(a[names[2]])for a in(ma,ea)])
    reconstructed=np.array([evaluate(y,coef)for y in(ym,ye)])
    paired=dy*(coef[1]+(ym+ye)*coef[2])
    return dict(ordered_GG_GH_HG_HH=ordered,independent_transpose_ordered_GG_GH_HG_HH=transpose,
                source_current_Y_coefficients=coef,independent_transpose_Y_coefficients=tcoef,
                direct_family_current=direct,reconstructed_family_current=reconstructed,
                source_polynomial_paired_current=paired,
                independent_family_binary_difference=direct[0]-direct[1],
                scalar_unit_source_reconstruction_max=unit_defect,
                scalar_unit_source_scale=unit_scale,
                gauge_source_identical=True,GG_paired_coefficient_is_algebraic_zero=True,
                inferred_response_difference_amplification=1/abs(dy),
                source_coefficient_or_current_vertex_conjugated=False,
                new_inverse_or_family_normalization_used=False,
                physical_graded_loop_overlap_or_Pauli_subtraction_identified=False)
