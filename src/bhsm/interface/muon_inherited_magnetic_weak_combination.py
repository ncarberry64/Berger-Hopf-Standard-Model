"""Literal signed weak action and returns of an inherited magnetic source.

This is the prescribed-source classical application on its declared fixed
coordinate interval, not the positive native mean or a physical Pauli fit.
"""
from __future__ import annotations
import numpy as np
from .muon_holomorphic_n1_magnetic_quadratic_action import signed_magnetic_quadratic_source_motion


def literal_face_work(face):
    """q.T Pi and its two independent analytic response placements."""
    q, p = (np.asarray(face[n], complex) for n in ('total_field', 'canonical_momentum'))
    dq, dp = (np.asarray(face[n], complex) for n in ('total_field_first', 'canonical_momentum_first'))
    if q.ndim != 2 or p.shape != q.shape or dq.ndim != 3 or dq.shape[1:] != q.shape or dp.shape != dq.shape:
        raise ValueError('same complete face and literal source-first columns required')
    left = np.einsum('kfa,fb->kab', dq, p, optimize=True)
    right = np.einsum('fa,kfb->kab', q, dp, optimize=True)
    return dict(value=q.T @ p, left_first=left, right_first=right, first=left+right)


def combine_inherited_magnetic_weak_action(forms, forms_first, points, initial_face, final_face,
                                          corner_left, corner_right, constraint):
    """Combine original bulk, prescribed-wall work and ALL temporal returns.

    For the signed quadratic action, 2L = q.T E + d(q.T Pi)/dt,
    E = force - Pi_dot.  A coefficient corner contributes the LEFT minus
    RIGHT face. Free canonical momentum continuity does not remove wall
    source work. Point and face derivatives use a literal transpose; no
    Hilbert adjoint, real-part projection, or physical pole is inserted.

    `scale` already includes the owned -i coordinate-time pullback. Its
    value is held in this supplied-direction application. Coefficient,
    source, pairing/density/coframe variations are in forms_first; endpoint
    and domain selection require a separate physical matching application.
    """
    C = np.asarray(constraint, complex)
    scale = np.asarray(points['scale'], complex)
    values = {}
    def append(name, value):
        values.setdefault(name, []).append(value)
    for i, cell in enumerate(points['cell']):
        j = int(cell)
        q, qt, dq, dqt = (points[n][i] for n in
            ('total_field', 'total_coordinate_rate', 'total_field_first', 'total_coordinate_rate_first'))
        a = signed_magnetic_quadratic_source_motion(forms[j], forms_first[j], q, qt, dq, dqt)
        for name, v in a.items():
            append(name, v)
        p = points['canonical_momentum'][i]
        force = points['original_action_force'][i]
        e = points['original_unbordered_Euler_rows'][i]
        de = (points['original_first_reconstructed_rows'][i]
              + np.einsum('fc,kcs->kfs', C.T, points['wall_and_frame_reactions_first'][i]))
        source = .5 * q.T @ e
        source_left = .5 * np.einsum('kfa,fb->kab', dq, e, optimize=True)
        source_right = .5 * np.einsum('fa,kfb->kab', q, de, optimize=True)
        append('wall_force_work', source)
        append('wall_force_work_left_first', source_left)
        append('wall_force_work_right_first', source_right)
        append('wall_force_work_first', source_left+source_right)
        # This independent point identity does not use a cancellation to
        # define the computed bulk action or its coefficient/source jets.
        append('point_action_identity_defect', a['base_total']-.5*(q.T@force+qt.T@p))
    arrays = {name:np.array(v) for name, v in values.items()}
    integrated = {name:np.einsum('q,q...->...', scale, v, optimize=True) for name,v in arrays.items()}
    first, last, left, right = map(literal_face_work, (initial_face, final_face, corner_left, corner_right))
    endpoint = -.5j * (last['value']-first['value'])
    endpoint_first = -.5j * (last['first']-first['first'])
    corner = -.5j * (left['value']-right['value'])
    corner_first = -.5j * (left['first']-right['first'])
    returned = endpoint + corner + integrated['wall_force_work']
    returned_first = endpoint_first + corner_first + integrated['wall_force_work_first']
    return dict(points=arrays, integrated=integrated,
        temporal_endpoint_return=endpoint, temporal_endpoint_return_first=endpoint_first,
        coefficient_corner_return=corner, coefficient_corner_return_first=corner_first,
        complete_weak_return=returned, complete_weak_return_first=returned_first,
        original_bulk_minus_complete_weak_return=integrated['base_total']-returned,
        original_bulk_first_minus_complete_weak_return_first=integrated['total_first_total']-returned_first,
        initial_face_work=first, final_face_work=last, corner_left_work=left, corner_right_work=right,
        quantum_native_mean_insertions_overlap_or_Pauli_completed=False)
