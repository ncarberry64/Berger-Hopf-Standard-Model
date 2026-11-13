"""Literal boundary/source Green identity on the reached canonical cells.

All 67 tests, both endpoint terms, full source gradient, stored action
asymmetry and the original named-frame reaction are kept independently.
This is an action/source contraction, not an exterior boundary selector.
"""
import numpy as np
from flint import acb,ctx
from .muon_stored_admission_correction import _matrix,_mid,_upper
from .muon_stored_fiber_canonical_tangent import _rows,_split


def canonical_green_source_cell(H,step,initial_u,initial_u_low,final_u,final_u_low,
        initial_v,initial_v_low,final_v,final_v_low,stage_u,stage_u_low,
        stage_v,stage_v_low,source_v,reaction_u,reaction_v,*,precision_bits=192):
    """W_final-W_initial=h*(u.T g+u.T(H-H.T)v+frame work).

    W=u_x.T v_Pi-u_Pi.T v_x. No transpose is inferred from a Hilbert
    inner product, and a stored nonsymmetric H is not symmetrized.
    """
    n=len(initial_u)//2;H=np.asarray(H,complex);h=complex(step)
    if n<1 or H.shape[0]<=2*n or h==0:raise ValueError('same complete canonical action cell required')
    old=ctx.prec;ctx.prec=int(precision_bits)
    try:
        pair=lambda a,b:_matrix(a)+_matrix(b)
        a=pair(initial_u,initial_u_low);b=pair(initial_v,initial_v_low)
        c=pair(final_u,final_u_low);d=pair(final_v,final_v_low)
        U=pair(stage_u,stage_u_low);V=pair(stage_v,stage_v_low);G=_matrix(source_v)
        HH=_matrix(H);ru=_matrix(reaction_u);rv=_matrix(reaction_v)
        W=lambda x,y:_rows(x,0,n).transpose()*_rows(y,n,2*n)-_rows(x,n,2*n).transpose()*_rows(y,0,n)
        first,last=W(a,b),W(c,d);clock=acb(h.real,h.imag)
        source=clock*U.transpose()*G
        asymmetry=clock*U.transpose()*(HH-HH.transpose())*V
        frames=clock*(_rows(U,n,len(H)).transpose()*rv-ru.transpose()*_rows(V,n,len(H)))
        boundary=last-first;rows=boundary-source-asymmetry-frames
        bh,bl=_split(boundary)
        return dict(initial_boundary_pairing=_mid(first),final_boundary_pairing=_mid(last),
            boundary_increment_high=bh,boundary_increment_low=bl,
            full_source_work=_mid(source),literal_action_asymmetry_work=_mid(asymmetry),
            named_frame_work=_mid(frames),green_identity_rows=_mid(rows),
            green_identity_upper=_upper(rows),source_work_upper=_upper(source),
            action_asymmetry_work_upper=_upper(asymmetry),named_frame_work_upper=_upper(frames),
            complete_source_and_both_natural_faces_retained=True)
    finally:ctx.prec=old
