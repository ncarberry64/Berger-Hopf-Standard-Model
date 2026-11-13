"""Second endpoint/time-family contacts on a supplied joint action germ.

The original reset traces are temporal endpoint conditions.  Their time
jets do not impose persistent parent/child bulk glue or a new action load.
The total derivative follows the supplied canonical vector field and the
recorded reference-only affine clock; it is not a selected physical mode.
"""
from __future__ import annotations
import numpy as np
from .muon_holomorphic_two_arm_reset import holomorphic_moving_trace
from .muon_complex_normal_trace_motion import proper_normal_trace_motion


def endpoint_trace_first_germ(raw_pair,raw_rate,master_lift,one_lift,normalizer):
    raw=np.asarray(raw_pair,complex);rate=np.asarray(raw_rate,complex)
    R=np.asarray(master_lift,complex);P=np.asarray(one_lift,complex);norm=np.asarray(normalizer)
    if raw.shape!=(2,268)or rate.shape!=raw.shape or R.shape!=(536,504)or P.shape!=(268,252)or norm.shape!=(4,4):
        raise ValueError('same full pair, original lifts and declared reset normalization required')
    C=np.zeros((4,504),complex);Ct=np.zeros_like(C);value=np.zeros(4,complex)
    N=np.zeros((2,504),complex);Nt=np.zeros_like(N);lapse=np.zeros(2,complex);lt=np.zeros(2,complex)
    xi=np.r_[np.arange(106),np.arange(252,358)]
    for arm,sign in((0,-1),(1,1)):
        tr=holomorphic_moving_trace(raw[arm]);r=arm*268+np.arange(100)
        C+=sign*tr['first']@R[r];value+=sign*tr['value']
        Ct+=sign*np.einsum('aij,j,ik->ak',tr['second'],rate[arm,:100],R[r],optimize=True)
        proper=proper_normal_trace_motion(raw[arm],P,rate[arm]);ids=xi[arm*106:(arm+1)*106]
        N[arm,ids]=proper['trace'][-1];Nt[arm,ids]=proper['trace_coordinate_time_first'][-1]
        lapse[arm]=proper['lapse'];lt[arm]=proper['lapse_coordinate_time_first']
    return dict(moving_geometric_trace_value=norm@value,moving_geometric_trace=norm@C,
        moving_geometric_trace_time_first=norm@Ct,proper_normal_rows=N,proper_normal_rows_time_first=Nt,
        induced_lapses=lapse,induced_lapse_time_first=lt)


def endpoint_second_from_first_germs(plus,minus,plus_rate,minus_rate,*,normalized_step,rate_magnitude):
    """Differentiate actual first germs, including derivative of their rate.

    plus/minus rates are recomputed by the original canonical DAE with
    actual reference clock at each displaced point. This retains base
    acceleration/jerk and source-clock motion once. The centered result is
    a numerical directional diagnostic, without a derivative enclosure.
    """
    h=float(normalized_step);m=float(rate_magnitude)
    if h<=0 or m<=0:raise ValueError('positive declared step and original rate normalization required')
    factor=m/(2*h)
    return dict(moving_geometric_trace_time_second=factor*(plus['moving_geometric_trace_time_first']-minus['moving_geometric_trace_time_first']),
        proper_normal_rows_time_second=factor*(plus['proper_normal_rows_time_first']-minus['proper_normal_rows_time_first']),
        induced_lapse_time_second=factor*(plus['induced_lapse_time_first']-minus['induced_lapse_time_first']),
        original_master_coordinate_rate_time_first=factor*(np.asarray(plus_rate)-np.asarray(minus_rate)),
        physical_clock_step=h/m,normalized_step=h,rate_magnitude=m,
        actual_rate_recomputed_in_both_first_germs=True,
        temporal_endpoint_condition_not_promoted_to_bulk_glue=True)
