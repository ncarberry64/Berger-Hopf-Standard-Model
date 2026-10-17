"""Geometric second incidence of the owned regular minimal-area action.

Entries are value, x, y, xy derivatives for real parameters. All metric,
embedding and gamma entries are explicit. The output is a coordinate
density relative to the supplied worldvolume chart, not a normalized mode
or an extra copy of an already integrated stratum measure. No background,
FSC value, environment length, projector or physical domain is selected.
"""
from __future__ import annotations

import numpy as np


JET_ORDER = ('value', 'x', 'y', 'xy')
GEOMETRY_OWNER = 'completion.tensor_differential_incidence_v14_69'
SURFACE_OWNER = 'covariant_bubble_interface_mechanics.build_payload.interface_action'


def _real_jet(value, name, shape):
    if value is None:
        raise ValueError(f'explicit {name} jets required, including owned zeros')
    a = np.asarray(value)
    if a.shape != (4,) + shape or not np.isfinite(a).all():
        raise ValueError(f'{name} needs finite shape {(4,) + shape}: {JET_ORDER}')
    if np.iscomplexobj(a) and np.any(a.imag != 0):
        raise ValueError(f'real {name} required; complex germs are not projected')
    return np.asarray(a.real, float)


def _symmetric_jet(value, name, dimension):
    a = _real_jet(value, name, (dimension, dimension))
    if not np.allclose(a, a.swapaxes(-1, -2), atol=1e-13, rtol=1e-13):
        raise ValueError(f'symmetric {name} jets required')
    return a


def _mul(a, b):
    return np.stack((a[0] @ b[0],
        a[1] @ b[0] + a[0] @ b[1],
        a[2] @ b[0] + a[0] @ b[2],
        a[3] @ b[0] + a[1] @ b[2] + a[2] @ b[1] + a[0] @ b[3]))


def _transpose(a):
    return a.swapaxes(-1, -2)


def _inertia(a, name):
    sign, _ = np.linalg.slogdet(a)
    if sign == 0:
        raise ValueError(f'nondegenerate {name} value required')
    eig = np.linalg.eigvalsh(a)
    if np.any(eig == 0):
        raise ValueError(f'nondegenerate {name} value required')
    return (int(np.sum(eig < 0)), int(np.sum(eig > 0)))


def quotient_metric_second_jet(metric8_jet):
    """Return Q=A-B solve(C,B.T), including ALL mixed second contacts.

    The fixed owned splitting has horizontal dimension five and vertical
    dimension three. An invertible C and a nondegenerate G are required;
    no Euclidean signature is imposed on G or its horizontal quotient.
    """
    G = _symmetric_jet(metric8_jet, 'M8 metric', 8)
    inertia8 = _inertia(G[0], 'M8 metric')
    A, B, C = G[:, :5, :5], G[:, :5, 5:], G[:, 5:, 5:]
    inertiaC = _inertia(C[0], 'vertical metric')
    rhs = _transpose(B)
    # Differentiate C X=B.T. No explicit inverse or new whitening is used.
    X0 = np.linalg.solve(C[0], rhs[0])
    Xx = np.linalg.solve(C[0], rhs[1] - C[1] @ X0)
    Xy = np.linalg.solve(C[0], rhs[2] - C[2] @ X0)
    Xxy = np.linalg.solve(C[0], rhs[3] - C[3] @ X0
                         - C[1] @ Xy - C[2] @ Xx)
    X = np.stack((X0, Xx, Xy, Xxy))
    Q = A - _mul(B, X)
    return dict(quotient_metric_jet=Q, solved_vertical_B_transpose_jet=X,
                metric8_signature=inertia8, vertical_signature=inertiaC,
                quotient_signature=_inertia(Q[0], 'horizontal quotient'))


def induced_metric_second_jet(*, quotient5_jet, tangent_inclusion_jet):
    """Return h=T.T Q T with every moving tangent-frame/embedding jet.

    T jets must come from the actual embedding when this is applied to a
    physical carrier. The evaluator does not infer them from a fixed seam.
    """
    Q = _symmetric_jet(quotient5_jet, 'M5 quotient', 5)
    T = _real_jet(tangent_inclusion_jet, 'M4 tangent inclusion', (5, 4))
    h = _mul(_mul(_transpose(T), Q), T)
    return dict(induced_metric_jet=h,
                induced_signature=_inertia(h[0], 'induced worldvolume metric'))


def signed_area_action_second_jet(*, induced_metric_jet, gamma_jet):
    """Return -gamma sqrt(abs(det h)) as a local coordinate-density jet.

    Signature is fixed on a sufficiently small neighborhood of a supplied
    nondegenerate base. Gamma jets include their owned environmental scale
    contacts. They are not identified with microscopic cutoff jets.
    """
    h = _symmetric_jet(induced_metric_jet, 'induced metric', 4)
    gamma = _real_jet(gamma_jet, 'surface coefficient', ())
    signature = _inertia(h[0], 'induced worldvolume metric')
    _, logdet = np.linalg.slogdet(h[0])
    density0 = np.exp(logdet / 2)
    hx = np.linalg.solve(h[0], h[1])
    hy = np.linalg.solve(h[0], h[2])
    hxy = np.linalg.solve(h[0], h[3])
    lx, ly = np.trace(hx) / 2, np.trace(hy) / 2
    density = density0 * np.array((1., lx, ly,
        np.trace(hxy) / 2 + lx * ly - np.trace(hx @ hy) / 2))
    action = -np.array((gamma[0] * density[0],
        gamma[1] * density[0] + gamma[0] * density[1],
        gamma[2] * density[0] + gamma[0] * density[2],
        gamma[3] * density[0] + gamma[1] * density[2]
        + gamma[2] * density[1] + gamma[0] * density[3]))
    covector = -gamma[0] * density0 * np.linalg.solve(h[0], np.eye(4)) / 2
    if not np.isfinite(density).all() or not np.isfinite(action).all():
        raise ValueError('surface density is outside the numerical range')
    return dict(worldvolume_density_jet=density, signed_area_action_jet=action,
                induced_metric_covector_density=covector,
                gamma_covector_density=-density0, induced_signature=signature)


def surface_incidence_second_jet(*, metric8_jet, tangent_inclusion_jet, gamma_jet):
    """Compose the owned quotient, moving incidence and signed area law.

    Covectors at value use tr(Lambda dG) / Frobenius(T_covector,dT).
    They include the supplied coordinate density exactly once. A physical
    fibre disintegration, chart integral, constraints, corners or Schur
    reduction must use their existing action-owned measures separately.
    """
    G = _symmetric_jet(metric8_jet, 'M8 metric', 8)
    T = _real_jet(tangent_inclusion_jet, 'M4 tangent inclusion', (5, 4))
    quotient = quotient_metric_second_jet(G)
    Q = quotient['quotient_metric_jet']
    induced = induced_metric_second_jet(quotient5_jet=Q, tangent_inclusion_jet=T)
    area = signed_area_action_second_jet(
        induced_metric_jet=induced['induced_metric_jet'], gamma_jet=gamma_jet)
    lam_h = area['induced_metric_covector_density']
    lam_Q = T[0] @ lam_h @ T[0].T
    right = quotient['solved_vertical_B_transpose_jet'][0].T  # B C^-1
    cross = -lam_Q @ right
    lam_G = np.block([[lam_Q, cross], [cross.T, right.T @ lam_Q @ right]])
    lam_T = 2 * Q[0] @ T[0] @ lam_h
    return dict(jet_order=JET_ORDER, **quotient, **area,
        induced_metric_jet=induced['induced_metric_jet'],
        quotient_metric_covector_density=lam_Q,
        metric8_covector_density=lam_G,
        tangent_inclusion_covector_density=lam_T,
        measure_scope='local worldvolume coordinate density; no extra L2/fibre normalization',
        derivative_scope='explicit real value/x/y/xy G8, T and gamma jets',
        physical_carrier_selected=False, physical_surface_coefficient_selected=False,
        microscopic_operator_or_outgoing_domain_selected=False,
        physical_full_derivative_passed=False, coupled_matching_corrections=0)
