"""Original endpoint response of supplied corrected two-term arm directions.

The complete joint Hessian already contains inherited parent feedback.
Only explicit action-parameter sources are added to that joint derivative.
Natural endpoint tractions are readouts, not constraints imposed in bulk.
"""
from __future__ import annotations
import numpy as np
from flint import acb, ctx
from .muon_stored_admission_correction import _matrix, _mid, _upper
from .muon_coupled_phase_trace_projection import coupled_phase_trace_projection
from .muon_reset_trial_role_application import reset_role_indices
from .aether_full_reset_action_jacobian import (
    _attachment_jacobian_at_order, _symmetric_power,
)


def endpoint_formal_area_offset(application, offset, normalization_coordinates):
    """Evaluate the exact polynomial area offset and re-solve its phase port.

    This is a formal source-derivative control around the held coefficient;
    a signed offset is not a selected positive physical tension. All
    non-port endpoint rows are affine in the action's area coefficient.
    The phase port is recomputed from D+offset*D_gamma before inversion.
    """
    a = application; g = a['action']; p = a['projection']; phase = np.r_[
        g['velocity_indices'], g['algebraic_indices']]
    z = complex(offset)
    D = p['phase_Hessian'] + z*g['area_Hessian_per_gamma'][np.ix_(phase, phase)]
    theta = np.r_[g['temporal_cotangent'] + z*g['area_temporal_cotangent_per_gamma'],
                  np.zeros(80, complex)]
    fresh = coupled_phase_trace_projection(D, p['trace_map'], p['named_frames'],
        theta, p['common_trace_map'])
    rows = a['residual'] + z*a['area_parameter_source']
    ai = a['groups']['common_attachment_temporal_dual']
    ni = a['groups']['common_normal_temporal_dual']
    B = _attachment_jacobian_at_order(12, normalization_coordinates)
    rows[ai] = _symmetric_power(B@B.T, .5)@fresh['common_trace_cotangent'][:2]
    rows[ni] = fresh['common_trace_cotangent'][2]
    return dict(residual=rows, projection=fresh,
        formal_area_offset=z, physical_tension_selected=False)


def corrected_birth_endpoint_source(application, jacobian, direction_high,
        direction_low, position_trace_map, *, parameter_amplitude=0,
        precision_bits=192):
    """Apply original226 and both signed temporal duals without rounding away low terms.

    ``jacobian`` is the supplied same-point full endpoint derivative. Its
    third-action production error remains outside the stored arithmetic.
    ``position_trace_map`` maps original504 to both actual attachment2 and
    proper-normal1 displacements, in parent3/child3 order.
    """
    a = application; g = a['action']; H = np.asarray(g['hessian'], complex)
    Hp = np.asarray(g['parent']['hessian'], complex)
    J = np.asarray(jacobian, complex); dh = np.asarray(direction_high, complex)
    dl = np.asarray(direction_low, complex); T = np.asarray(position_trace_map, complex)
    if (H.shape != (504, 504) or Hp.shape != (252, 252) or J.shape != (226, 504)
            or dh.shape != (504,) or dl.shape != dh.shape or T.shape != (6, 504)
            or not all(np.isfinite(x).all() for x in (H, Hp, J, dh, dl, T))):
        raise ValueError('same full original504/226 endpoint and both actual position trace maps required')
    z = complex(parameter_amplitude)
    if not np.isfinite(z): raise ValueError('finite explicit parameter direction required')
    roles = reset_role_indices(a['groups'])
    old = ctx.prec; ctx.prec = precision_bits
    try:
        dd = _matrix(dh)+_matrix(dl); zz = acb(z.real, z.imag)
        gamma = _matrix(a['area_parameter_source'])
        rows = _matrix(J)*dd + gamma*zz
        master = _matrix(H)*dd + _matrix(g['area_gradient_per_gamma'])*zz
        own = _matrix(Hp)*_matrix(dh[:252])+_matrix(Hp)*_matrix(dl[:252])
        own += _matrix(g['area_gradient_per_gamma'][:252])*zz
        # Keep the unrounded products in the decomposition and port signs.
        own_v = type(own)([[own[i, 0]] for i in range(106, 212)])
        pi_pair = type(master)([[master[i, 0]] for i in g['velocity_indices']])
        theta = type(master)([[2*own_v[i, 0]-pi_pair[i, 0]] for i in range(106)]
                             + [[-pi_pair[i, 0]] for i in range(106, 212)])
        theta_direct = _matrix(g['temporal_cotangent_first'])*dd + _matrix(
            g['area_temporal_cotangent_per_gamma'])*zz
        trace = _matrix(T)*dd
        high = _mid(rows)[:, 0]; low = _mid(rows-_matrix(high))[:, 0]
        th = _mid(theta)[:, 0]; tl = _mid(theta-_matrix(th))[:, 0]
        wh = _mid(own_v)[:, 0]; wl = _mid(own_v-_matrix(wh))[:, 0]
        jh = _mid(pi_pair)[:, 0]; jl = _mid(pi_pair-_matrix(jh))[:, 0]
        trh = _mid(trace)[:, 0]; trl = _mid(trace-_matrix(trh))[:, 0]
        records = {}
        for name, ids in roles.items():
            if not isinstance(ids, np.ndarray): continue
            block = type(rows)([[rows[i, 0]] for i in ids])
            records[name+'_stored_rows_upper'] = _upper(block)
        return dict(arrays=dict(original504_direction_high=dh, original504_direction_low=dl,
            original226_response_high=high, original226_response_low=low,
            original226_state_response_high=_mid(_matrix(J)*dd)[:, 0],
            original226_direct_parameter_source=np.asarray(a['area_parameter_source'])*z,
            temporal_dual_response_high=th, temporal_dual_response_low=tl,
            own_parent_Pi_response_high=wh, own_parent_Pi_response_low=wl,
            joint_Pi_response_high=jh, joint_Pi_response_low=jl,
            both_attachment_and_proper_normal_displacements_high=trh,
            both_attachment_and_proper_normal_displacements_low=trl,
            actual_position_trace_map=T,
            proper_normal_displacement_parent=np.array(trh[2]+trl[2]),
            proper_normal_displacement_child=np.array(trh[5]+trl[5])),
            original226_stored_response_upper=_upper(rows),
            temporal_dual_decomposition_difference_upper=_upper(theta-theta_direct),
            role_response_uppers=records, parameter_amplitude=z,
            precision_bits=precision_bits, inherited_feedback_count=1,
            child_reconstituted_source_gradient_not_appended_to_joint_action=True,
            normal_natural_force_not_forced_zero=True,
            reset_endpoint_not_continuous_bulk_load=True,
            analytic_direction_or_dual_conjugated=False,
            physical_mode_first_hit_or_pole_selected=False,
            arithmetic_scope='exact stored binary H/J/source and two-term direction only; upstream endpoint third-action and physical source/domain errors excluded')
    finally:
        ctx.prec = old
