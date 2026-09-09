"""Compose covariance balls through signed stored-map suffixes at 512 bits."""
import numpy as np
from flint import arb,arb_mat,ctx
from bhsm.interface.current_green_midpoint_coordinate_error import (
    PRECISION,_float_upper,_real_binary64,
)
from bhsm.interface.resolved_midpoint_coordinate_error import _exact_matrix
from bhsm.interface.stored_covariance_enclosure import interval_matrix,projected_covariance_upper


def causal_covariance_bounds(local_mid,local_radius,adjacent_mid,adjacent_radius,maps,axes,progress=None,target_nodes=None):
    """Bound longitudinal/transverse quadratic block sums from verified balls.

    Local covariance order is left/cross/right. Adjacent[i] is the previous
    right block times the current left block transpose. Complete a shared
    node before taking norms, preserving cancellation. Form each full signed
    map suffix separately and apply covariance uncertainty only once, avoiding
    repeated propagation of wide independent interval entries.
    """
    lm,lr,am,ar,p,e=[_real_binary64(v,name) for name,v in (
        ('local midpoint',local_mid),('local radius',local_radius),
        ('adjacent midpoint',adjacent_mid),('adjacent radius',adjacent_radius),
        ('maps',maps),('axes',axes))]
    if p.ndim!=3 or min(p.shape)==0 or p.shape[1]!=p.shape[2]:
        raise ValueError('Nonempty square causal maps required')
    count,dimension,_=p.shape
    targets=list(range(1,count+1)) if target_nodes is None else list(target_nodes)
    if (not targets or any(isinstance(n,(bool,np.bool_)) or not isinstance(n,(int,np.integer))
                           or not 1<=n<=count for n in targets)
            or targets!=sorted(set(targets))):
        raise ValueError('Nonempty ordered unique target nodes required')
    if (lm.shape!=(count,3,dimension,dimension) or lr.shape!=lm.shape
            or am.shape!=(count,dimension,dimension) or ar.shape!=am.shape
            or e.shape!=(count+1,dimension) or np.any(lr<0) or np.any(ar<0)):
        raise ValueError('Compatible complete covariance balls and axes required')
    previous=ctx.prec
    ctx.prec=PRECISION
    try:
        exact_maps=[_exact_matrix(v) for v in p]
        local=[[interval_matrix(lm[i,j],lr[i,j]) for j in range(3)] for i in range(count)]
        completed=[]
        for i in range(1,count):
            adjacent=interval_matrix(am[i],ar[i])
            cross=exact_maps[i]*adjacent
            completed.append(exact_maps[i]*local[i-1][2]*exact_maps[i].transpose()
                             +local[i][0]+cross+cross.transpose())
        identity=arb_mat(np.eye(dimension,dtype=int).tolist())
        longitudinal=[0.]+[None]*count
        transverse=[0.]+[None]*count
        for target in targets:
            axis=_exact_matrix(e[target][:,None])
            axis_squared=(axis.transpose()*axis)[0,0]
            suffix=identity
            total_l,total_t=arb(0),arb(0)
            for source in range(target,0,-1):
                gram=suffix.transpose()*suffix
                pulled=suffix.transpose()*axis
                covariances=[local[source-1][1]]
                if source>=2:covariances.append(completed[source-2])
                if source==target:covariances.append(local[target-1][2])
                for covariance in covariances:
                    bound_l,bound_t=projected_covariance_upper(covariance,gram,pulled,axis_squared)
                    total_l+=bound_l;total_t+=bound_t
                if source>1:suffix=suffix*exact_maps[source-1]
            longitudinal[target]=_float_upper(total_l)
            transverse[target]=_float_upper(total_t)
            if progress is not None:progress(target,longitudinal[target],transverse[target])
        return dict(scope='VERIFIED_LOCAL_COVARIANCE_BALLS_THROUGH_EXACT_STORED_CAUSAL_MAPS',
            arithmetic_precision_bits=PRECISION,
            longitudinal_coefficient_upper=longitudinal,transverse_coefficient_upper=transverse,
            maximum_coefficients_upper=[max(longitudinal[n] for n in targets),max(transverse[n] for n in targets)],
            coverage=dict(target_nodes=[int(n) for n in targets],complete=targets==list(range(1,count+1))),
            stored_axis_unit_norm_assumed=False,
            local_covariance_enclosures_require_external_verification=True,
            physical_Hessian_error_enclosed=False,neighborhood_remainder_enclosed=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    finally:
        ctx.prec=previous
