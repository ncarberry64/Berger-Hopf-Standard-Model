"""Bind an AE2 trace to the new child Cauchy response without choosing a state.

Zero entries in a coordinate-response matrix denote derivatives with respect
to the named coordinates. They never assign zero values to the other birth,
incoming-characteristic, color, profile or homogeneous physical data.
"""
from __future__ import annotations
import numpy as np


def _explicit(a, shape, name):
    a = np.asarray(a, complex)
    if a.shape != shape or not np.isfinite(a).all():
        raise ValueError('explicit finite ' + name + ' of shape ' + str(shape) + ' required')
    return a


def bind_event_birth_data(free_child_data, free_child_source, required_raw,
                         required_source, closed_carrier):
    """Solve only the proved-carrier birth-wall trace equations.

    Child data slots0/1/2 are raw birth values at inner/middle/wall; slots3:8
    are future incoming characteristic data. All unbound coordinates pass
    through. The full source includes the supplied event source, not a
    silently chosen independent state or base-map variation.
    """
    d = np.asarray(free_child_data, complex)
    if d.ndim != 3 or d.shape[:2] != (8, 384):
        raise ValueError('all child birth/characteristic coordinates required')
    dx = _explicit(free_child_source, d.shape, 'independent child data source')
    r = _explicit(required_raw, (384, d.shape[-1]), 'required raw event trace')
    rx = _explicit(required_source, r.shape, 'required raw event source')
    C = np.asarray(closed_carrier, complex)
    if C.ndim != 2 or C.shape[0] != 384 or np.max(abs(C.conj().T @ C-np.eye(C.shape[1]))) > 1e-13:
        raise ValueError('proved closed original carrier lift required')
    P = C @ C.conj().T
    if max(np.max(abs((np.eye(384)-P) @ r)), np.max(abs((np.eye(384)-P) @ rx))) > 1e-12:
        raise ValueError('required event operand escapes the proved carrier')
    result, source = d.copy(), dx.copy()
    result[2] = (np.eye(384)-P) @ d[2] + r
    source[2] = (np.eye(384)-P) @ dx[2] + rx
    return result, source


def event_coordinate_partial(required_raw, required_source):
    """Coordinate derivative of child data; no physical other-data value."""
    r = np.asarray(required_raw, complex)
    rx = _explicit(required_source, r.shape, 'event-coordinate source')
    if r.ndim != 2 or r.shape[0] != 384:
        raise ValueError('full raw event-coordinate columns required')
    data = np.zeros((8, 384, r.shape[1]), complex)
    source = np.zeros_like(data)
    data[2], source[2] = r, rx
    return data, source


def event_jacobi_ports(parent_value, parent_source, parent_time,
                      parent_radial_fixed_frame, child_spin,
                      child_spin_source, carrier, middle,
                      middle_source_columns, *, child_spin_rate_columns):
    """Every local event product and total-base port, in separate arrays.

    q is in the fixed material frame. Its radial off-wall frame derivative
    is an independent contact, so the returned fixed-frame radial port must
    be completed before a nonzero radial event displacement is consumed.
    Child evaluation motion belongs once in total deltaF, outside this
    fixed-wall coordinate application.
    """
    q = np.asarray(parent_value, complex)
    qx, qt, qr = (_explicit(a, q.shape, n) for a, n in (
        (parent_source, 'parent supplied source'), (parent_time, 'parent time gradient'),
        (parent_radial_fixed_frame, 'parent radial fixed-frame gradient')))
    C, S, Sx, K, Kx = map(np.asarray, (carrier, child_spin, child_spin_source,
                                      middle, middle_source_columns))
    n = C.shape[1]
    if q.ndim != 2 or q.shape[0] != 384 or C.shape != (384, n) or K.shape != (n, n) or Kx.shape != (7, n, n):
        raise ValueError('actual parent columns and seven map source factors required')
    _explicit(S, (384,384), 'child material frame')
    _explicit(Sx, S.shape, 'child material frame source')
    Sr = np.asarray(child_spin_rate_columns)
    if Sr.ndim != 3 or Sr.shape[1:] != S.shape:
        raise ValueError('explicit material normal-rate frame coefficients required')
    T = S @ C @ K @ C.conj().T
    return dict(raw_value=T @ q,
        raw_supplied_source=T @ qx+Sx @ C @ K @ C.conj().T @ q,
        raw_independent_state_source_coefficient=T,
        raw_free_map_source=np.einsum('ij,xjk,kl->xil', S@C, Kx, C.conj().T@q, optimize=True),
        raw_child_normal_rate_frame_source=np.einsum('xij,jk,kl->xil', Sr@C, K, C.conj().T@q, optimize=True),
        raw_total_parent_time_pullback=T @ qt,
        raw_total_parent_radial_fixed_frame_pullback=T @ qr,
        radial_material_frame_contact_uncomputed=True,
        total_child_evaluation_added_again=False)


def event_constraint_rank(parent_h, child_left, middle, carrier, *, tolerance=1e-12):
    """Rank of evaluated h block versus the joint trace constraint.

    Independent child birth variables make the rows independent. This
    constrains their relation to h, and does not select parent h alone.
    A numerical rank tolerance is stated; no null vector is called gauge.
    """
    Q, L, K, C = map(np.asarray, (parent_h, child_left, middle, carrier))
    A = K @ C.conj().T @ Q
    singular = np.linalg.svd(A, compute_uv=False)
    left_singular = np.linalg.svd(L, compute_uv=False)
    rank = int(np.sum(singular > tolerance))
    rows = len(A)
    if np.sum(left_singular > tolerance) != rows:
        raise ValueError('independent original child trace row pivot required')
    return dict(parent_h_block=A, parent_h_singular_values=singular,
        numerical_h_block_rank=rank, h_block_kernel_dimension=Q.shape[1]-rank,
        joint_constraint_row_rank=rows, parent_h_selected_rank=0,
        parent_h_coordinates_retained=Q.shape[1],
        child_data_coordinates_per_collar=8*384,
        remaining_joint_coordinates_per_collar=Q.shape[1]+8*384-rows,
        numerical_rank_absolute_tolerance=float(tolerance),
        nullspace_classified_as_gauge=False)
