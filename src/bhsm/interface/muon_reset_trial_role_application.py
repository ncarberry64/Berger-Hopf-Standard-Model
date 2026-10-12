"""Role/source audit of supplied trials on the original reset equations.

Trace and algebraic compatibility are distinct from natural temporal
traction/energy.  This module evaluates the supplied directions; it does
not solve a physical lift or force natural responses to vanish.
"""
from __future__ import annotations
import numpy as np


RESET_ROLES = {
    'kinematic_trace': ('gauge_trace', 'Higgs_trace',
                        'moving_geometric_trace', 'normal_position_trace'),
    'bulk_algebraic_compatibility': ('incoming_constraints', 'child_constraints'),
    'natural_response': ('incoming_energy', 'child_energy', 'gauge_temporal_dual',
                         'Higgs_temporal_dual', 'common_attachment_temporal_dual',
                         'common_normal_temporal_dual'),
}


def reset_role_indices(groups):
    """Keep every original row, with no Ward row or natural force deletion."""
    result = {}
    for role, names in RESET_ROLES.items():
        values = []
        for name in names:
            item = groups[name]
            values.extend(item['indices'] if isinstance(item, dict) else item)
        result[role] = np.asarray(values, int)
    if sorted(np.concatenate(list(result.values())).tolist()) != list(range(226)):
        raise ValueError('all original reset row groups required exactly once')
    return result


def reset_trial_role_application(jacobian, lifts, groups, *, source_rows=None):
    """Compute R_z delta_z+R_s, preserving its source and response roles.

    A supplied source must be an actual matching coefficient/source jet.
    Omitting it evaluates the fixed-source trial only; it assigns no
    physical missing coefficient zero.  Natural entries are readouts,
    rather than prohibited domain variations or selected mode equations.
    """
    J = np.asarray(jacobian, complex); z = np.asarray(lifts, complex)
    if J.shape != (226, 504) or z.ndim != 2 or z.shape[0] != 504:
        raise ValueError('all original226 rows and original504 trial required')
    sourced = source_rows is not None
    s = np.zeros((226, z.shape[1]), complex) if not sourced else np.asarray(source_rows, complex)
    if s.shape != (226, z.shape[1]) or not np.isfinite(s).all():
        raise ValueError('same actual source jet and coefficient ordering required')
    bare = J @ z; total = bare+s; ids = reset_role_indices(groups)
    summary = {}
    for role, rows in ids.items():
        summary[role] = dict(indices=rows.tolist(),
            max_abs_by_coefficient=np.max(abs(total[rows]), axis=0).tolist(),
            norm_by_coefficient=np.linalg.norm(total[rows], axis=0).tolist())
    return dict(original226_fixed_source_rows=bare, original226_source_rows=s,
                original226_total_rows=total, role_indices=ids, roles=summary,
                explicit_source_supplied=sourced,
                natural_response_is_not_forced_zero=True)


def reset_algebraic_duplicate_application(jacobian, hessian, groups, scales, lifts,
                                          *, gradient_source=None):
    """Audit identical reset/bulk Ly equations before any KKT composition.

    The 80 reset Ly rows are the same original bulk algebraic equations,
    scaled by the declared geometry weights.  Their source jets must be
    carried with those same scales, not imposed as additional independent
    Jacobi borders.  A true phase solve may retain named frame reactions.
    """
    J = np.asarray(jacobian, complex); H = np.asarray(hessian, complex)
    D = np.asarray(lifts, complex); scale = np.asarray(scales, float)
    y = np.r_[np.arange(212, 252), np.arange(464, 504)]
    ids = reset_role_indices(groups)['bulk_algebraic_compatibility']
    if J.shape != (226, 504) or H.shape != (504, 504) or scale.shape != (80,):
        raise ValueError('full same-action Hessian/Jacobian and declared80 scales required')
    source = np.zeros(504, complex) if gradient_source is None else np.asarray(gradient_source, complex)
    if source.shape != (504,):
        raise ValueError('explicit original504 gradient source required')
    rows = H[y] @ D + source[y, None]
    return dict(reset_algebraic_indices=ids, original_algebraic_indices=y,
        declared_scales=scale, duplicate_Jacobian_defect=J[ids]-scale[:, None]*H[y],
        original_bulk_algebraic_trial_rows=rows,
        scaled_reset_algebraic_trial_rows=scale[:, None]*rows,
        explicit_reset_algebraic_source_rows=scale*source[y],
        duplicated_bulk_rows_must_not_be_added_as_independent_borders=True)


def canonical_variational_constitutive_rows(hessian, master_lift, momentum, gradient_source):
    """Literal full292 constitutive compatibility for independently supplied data.

    delta_p = H_v,* delta_z + g_v,s; 0 = H_y,* delta_z+g_y,s.
    The velocity/y phase operator is D=[Lvv Lvy; Lyv Lyy].  No Euclidean
    minimum-norm state choice or frozen frequency relation is introduced.
    Evolution subsequently uses delta_x_dot=delta_v and
    delta_p_dot=H_x,*delta_z+g_x,s, with actual reference/domain motion.
    """
    H = np.asarray(hessian, complex); z = np.asarray(master_lift, complex)
    p = np.asarray(momentum, complex); g = np.asarray(gradient_source, complex)
    if H.shape != (504, 504) or z.shape != (504,) or p.shape != (212,) or g.shape != (504,):
        raise ValueError('full joint x/v/y, actual canonical momentum and gradient source required')
    x = np.r_[np.arange(106), np.arange(252, 358)]; v = x+106
    y = np.r_[np.arange(212, 252), np.arange(464, 504)]; phase = np.r_[v, y]
    rhs = np.r_[p-H[np.ix_(v, x)]@z[x]-g[v], -H[np.ix_(y, x)]@z[x]-g[y]]
    return dict(phase_Hessian=H[np.ix_(phase, phase)], phase_rhs=rhs,
        original292_constitutive_rows=np.r_[H[v]@z+g[v]-p, H[y]@z+g[y]],
        original212_position_rate=z[v], original212_momentum_rate=H[x]@z+g[x])
