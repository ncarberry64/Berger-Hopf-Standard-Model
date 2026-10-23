"""Original normal-flow incidence at the actual temporal birth corner.

The local normal chart is used only at its regular wall point. It is
not continued through a polar/characteristic set or through child t<0.
"""
from __future__ import annotations
import numpy as np

from .muon_sigma_normal_collar_transport import sigma_geometry_point
from .muon_holomorphic_d5_trace_action import (
    d5_sigma_foliation_eta, d5_sigma_normal_flow_germ,
)
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from .muon_parent_retarded_hypercharge import WALL


def birth_corner_incidence(raw, raw_coordinate_rate):
    """Evaluate the boundary of the admissible future normal-coordinate wedge.

    If X(q,s) is inward normal flow with X(q,0)=(q,WALL),
      X^t=q-n^t s+O(s²).
    Its birth curve X^t(q_birth(s),s)=0 has
      q_birth'=n^t,
      q_birth''=(partial_t n^t)n^t-(partial_rho n^t)n^rho.
    Positive q_birth' excludes the q=0 inward ray from child t>=0.
    This establishes a local domain incidence, not the physical reset map.
    """
    x, dx = np.asarray(raw, float), np.asarray(raw_coordinate_rate, float)
    if x.shape != (268,) or dx.shape != (268,) or not np.isfinite(np.r_[x, dx]).all():
        raise ValueError('actual finite birth raw268 and its own time direction required')
    c = sigma_geometry_point(x, dx, WALL)
    f = full_d5_localized_lepton_trace()
    n = d5_sigma_foliation_eta(c, gamma=f['gamma5D_particle'],
        carrier_count=1, angular_count=1, sheet_orientation=1)
    flow = d5_sigma_normal_flow_germ(c, n, coordinate_time_first_slot=0)
    v = flow['sigma_flow_coordinate_velocity'][0]
    vt = flow['sigma_flow_coordinate_velocity_time'][0]
    vr = flow['sigma_flow_coordinate_velocity_radial'][0]
    v, vt, vr = [np.real_if_close(a) for a in (v, vt, vr)]
    if any(np.iscomplexobj(a) for a in (v, vt, vr)):
        raise ValueError('this future-domain incidence requires its real branch')
    qb1 = float(v[0]); qb2 = float(vt[0]*v[0]-vr[0]*v[1])
    # Original differentiated implicit-level equation, before cancellation.
    inward = -v
    t_ss = float(vt[0]*v[0]+vr[0]*v[1])
    t_qs = float(-vt[0])
    row1 = -v[0]+qb1
    row2 = qb2+2*t_qs*qb1+t_ss
    arrays = dict(outward_coordinate_velocity2=v,
        outward_coordinate_velocity_time2=vt,
        outward_coordinate_velocity_radial2=vr,
        inward_coordinate_velocity2=inward,
        normal_birth_curve_first=np.array(qb1),
        normal_birth_curve_second=np.array(qb2),
        original_implicit_birth_curve_rows=np.array([row1, row2]))
    report = dict(outward_time_component=float(v[0]),
        outward_material_radial_component=float(v[1]),
        normal_birth_curve_first=qb1, normal_birth_curve_second=qb2,
        original_implicit_birth_curve_max=float(max(abs(row1), abs(row2))),
        child_birth_ray_enters_future_domain=bool(inward[0] >= 0),
        correct_future_normal_domain='q >= q_birth(s), not all q>=0,s>=0',
        global_normal_chart_claimed=False,
        child_prebirth_polynomial_extension_used=False,
        physical_event_reset_or_Goursat_data_assigned=False)
    return arrays, report
