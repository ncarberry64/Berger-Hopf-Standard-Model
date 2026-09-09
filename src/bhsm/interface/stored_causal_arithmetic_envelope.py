"""Combine verified stored-input error coefficients without dropping cross terms."""
import numpy as np
from flint import arb,ctx
from bhsm.interface.current_green_midpoint_coordinate_error import (
    PRECISION,_float_upper,_real_binary64,_squared_norm,
)


def fixed_axis_projection_norms(axes):
    """Norms of e.T and I-e e.T, omitting the fixed initial node."""
    values=_real_binary64(axes,'axes')
    if values.ndim!=2 or values.shape[0]<2 or values.shape[1]==0:
        raise ValueError('At least one noninitial finite axis required')
    previous=ctx.prec
    ctx.prec=PRECISION
    try:
        longitudinal,transverse=arb(0),arb(0)
        for axis in values[1:]:
            squared=_squared_norm(axis)
            longitudinal=max(longitudinal,squared.sqrt().upper())
            radial=abs(1-squared).upper()
            transverse=max(transverse,radial,arb(1) if values.shape[1]>1 else arb(0))
        return [_float_upper(longitudinal),_float_upper(transverse)]
    finally:
        ctx.prec=previous


def combine_stored_causal_errors(reconstructed_coefficients,stored_source_errors,map_gain,projection_norms):
    """Lift a reconstructed response plus all source errors to frozen maps.

    C_L,C_T bound e.T z and (I-e e.T)z. Since z=e(e.T z)+(I-e e.T)z exactly,
    ||z|| <= a_L C_L+C_T. For k>=||G DeltaP||<1 and stored-source error E,
    the entire response error is <=(k(a_L C_L+C_T)+E)/(1-k).
    This includes interactions of the map error with every supplied source
    error. The caller must verify all bounds and their common exact operands.
    """
    coefficients,errors,k,projections=[_real_binary64(value,name) for name,value in (
        ('reconstructed coefficients',reconstructed_coefficients),('source errors',stored_source_errors),
        ('map gain',map_gain),('projection norms',projection_norms))]
    if (coefficients.shape!=(2,) or errors.ndim!=1 or k.shape!=() or projections.shape!=(2,)
            or any(np.any(v<0) for v in (coefficients,errors,k,projections)) or float(k)>=1):
        raise ValueError('Nonnegative compatible bounds and map gain below one required')
    previous=ctx.prec
    ctx.prec=PRECISION
    try:
        cl,ct=[arb(float(v)) for v in coefficients]
        al,at=[arb(float(v)) for v in projections]
        gain=arb(float(k))
        source=sum((arb(float(v)) for v in errors),arb(0))
        response=al*cl+ct
        error=(gain*response+source)/(1-gain)
        return dict(scope='VERIFIED_STORED_PULLBACK_AND_CAUSAL_COMPOSITION_ARITHMETIC_ONLY',
            reconstructed_state_coefficient_upper=_float_upper(response),
            combined_stored_source_error_coefficient_upper=_float_upper(source),
            frozen_map_response_error_coefficient_upper=_float_upper(error),
            frozen_map_transverse_quadratic_coefficients_upper=[_float_upper(cl+al*error),_float_upper(ct+at*error)],
            map_source_cross_errors_included=True,stored_axis_unit_norm_assumed=False,
            all_input_bounds_require_external_verification=True,
            physical_Hessian_error_enclosed=False,physical_direction_construction_rounding_enclosed=False,
            kinematic_midpoint_construction_rounding_enclosed=False,neighborhood_remainder_enclosed=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    finally:
        ctx.prec=previous
