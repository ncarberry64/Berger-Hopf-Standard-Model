"""A computational slice of the jointly represented homogeneous birth graph.

The transformation includes both the child round-S3 coordinate chart and
its U2 bundle frame. It is not permission to rotate the child Higgs alone
with a fixed mechanical connection, or to erase physical closed holonomy.
"""
from __future__ import annotations

import numpy as np
from .muon_birth_optimized_two_arm_action import SIZE, FREE, homogeneous_identification


def homogeneous_identification_slice(coefficients):
    """Apply g_old=Sg_new, G_child=U0^dagger to all represented child data.

    U0=central*S and F_B(g)=Sg. Thus F_B*A_child=U0 A_parent U0^-1.
    Pulling the mechanical child connection along the coordinate change
    and applying G_child returns its retained j_i components, including
    their time/radial rates. Zero independent fields stay zero under this
    combined chart/frame change. Both canonical p and Hdot transform;
    p already contains density and Haar J=1 is not applied twice.
    """
    c=np.asarray(coefficients,float)
    if c.shape!=(SIZE,) or not np.isfinite(c).all():
        raise ValueError('finite same-vector225 represented graph required')
    identification=homogeneous_identification(c[220:224]);U=identification['U']
    out=c.copy()
    for start in (200,208,216):
        h=c[start:start+2]+1j*c[start+2:start+4];new=U.conj().T@h
        out[start:start+4]=np.r_[new.real,new.imag]
    out[220:224]=0
    return dict(coefficients=out,free_indices=FREE[(FREE<220)|(FREE>=224)],
        original_identification=identification,
        child_coordinate_change='g_old=S g_new',child_bundle_change=U.conj().T,
        child_fields_transformed=('H','Hdot','canonical p','connection with coordinate pullback'),
        open_graph_computational_slice=True,physical_identification_selected=False,
        physical_closed_holonomy_removed=False,large_gauge_winding=0,
        scope='joint homogeneous equal-radius spatial metric/connection graph; zero independent fields')
