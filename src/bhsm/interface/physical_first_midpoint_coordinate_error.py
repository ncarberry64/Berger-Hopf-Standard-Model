"""Propagate physical endpoint DF error balls through midpoint coordinates."""
import numpy as np
from flint import arb,arb_mat,ctx
from bhsm.interface import stored_midpoint_kinematic_error as kinematic


def _ball(mid,radius):
    return arb_mat([[arb(float(m),float(r)) for m,r in zip(a,b)] for a,b in zip(mid,radius)])


def combine_coordinate_errors(basis,base_mid,base_radius,endpoint_mid,endpoint_radius,
                              step,retained_dimension):
    """Enclose base error + S^-1 h/8 [DF_error_left,-DF_error_right].

    The base and endpoint balls are caller-certified. In particular, a fixed
    initial endpoint must be supplied as an exact zero ball by the consumer.
    """
    s,b,br,d,dr=[kinematic.resolved._real_binary64(v,n) for v,n in (
        (basis,'basis'),(base_mid,'base midpoint'),(base_radius,'base radius'),
        (endpoint_mid,'endpoint midpoint'),(endpoint_radius,'endpoint radius'))]
    h=kinematic.resolved._real_binary64(step,'step')
    if (s.ndim!=2 or s.shape[0]==0 or s.shape[0]!=s.shape[1]
            or d.ndim!=3 or d.shape[:2]!=(2,s.shape[0]) or d.shape[2]==0 or dr.shape!=d.shape
            or b.shape!=(s.shape[0],2*d.shape[2]) or br.shape!=b.shape
            or np.any(br<0) or np.any(dr<0) or h.shape!=() or float(h)<=0
            or type(retained_dimension) is not int or not 0<retained_dimension<s.shape[0]):
        raise ValueError('compatible finite nonnegative coordinate/DF balls required')
    previous=ctx.prec;ctx.prec=kinematic.resolved.PRECISION
    try:
        exact=kinematic.resolved._exact_matrix(s);inverse=exact.inv()
        identity=arb_mat(np.eye(s.shape[0],dtype=int).tolist())
        residual=identity-exact*inverse
        upper=max(sum(abs(residual[i,j]) for j in range(s.shape[0])).upper() for i in range(s.shape[0]))
        if not (upper.is_finite() and upper<1):raise RuntimeError('stored basis inverse could not be certified')
        left,right=_ball(d[0],dr[0]),_ball(d[1],dr[1])
        delta=arb_mat([[left[i,j] for j in range(d.shape[2])]+[-right[i,j] for j in range(d.shape[2])]
                       for i in range(s.shape[0])])*(arb(float(h))/8)
        first_error=inverse*delta;combined=_ball(b,br)+first_error
        arrays={}
        for name,matrix in (('first_derivative_coordinate_error',first_error),('combined_coordinate_error',combined)):
            arrays[name+'_mid'],arrays[name+'_radius']=kinematic._export(matrix)
        return arrays,dict(scope='PHYSICAL_FIRST_DERIVATIVE_AND_STORED_CONSTRUCTION_COORDINATE_ERROR',
            precision_bits=kinematic.resolved.PRECISION,
            inverse_residual_infinity_upper=kinematic.resolved._float_upper(upper),
            first_derivative_coordinate_error=kinematic._norms(first_error,retained_dimension),
            combined_coordinate_error=kinematic._norms(combined,retained_dimension),
            base_and_endpoint_balls_require_certificates=True,physical_frame_error_enclosed=False,
            neighborhood_remainder_enclosed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    finally:ctx.prec=previous
