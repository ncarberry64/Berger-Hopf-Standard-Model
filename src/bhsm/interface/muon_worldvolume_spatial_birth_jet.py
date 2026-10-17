"""Spatial same-E1 birth-map jets of the owned worldvolume transport IVP.

No physical history, initial identification or outgoing domain is selected.
Spatial map jets do not supply moving-endpoint clock or energy/field jets.
"""
from __future__ import annotations

import numpy as np

from .muon_intrinsic_worldvolume_scalar_transport import (
    unit_s3_material_frame, worldvolume_scalar_transport_ivp,
)
from .gauge_connection_reset_bundle_lift_adjudication import (
    induced_connection_transport,
)


def _real(value, name):
    array = np.asarray(value)
    if np.iscomplexobj(array) and np.any(array.imag != 0):
        raise ValueError(f'real {name} required; complex germs are not projected')
    result = np.asarray(array.real if np.iscomplexobj(array) else array, float)
    if not np.isfinite(result).all():
        raise ValueError(f'finite {name} required')
    return result


def spatial_birth_map_one_jet(*, coefficients, times, parent_label_points,
        initial_material_points, initial_bundle_transport, initial_jacobian,
        initial_material_point_spatial_derivatives,
        initial_bundle_transport_spatial_derivatives,
        initial_jacobian_spatial_derivatives, evaluator, rtol, atol):
    """Apply the same IVP to three explicit initial-label spatial seeds.

    Spatial derivatives are E_i on the declared parent label S3 chart. The
    initial dF, dU and dJ are required, including when their owned values are
    zero. The evaluator must supply all coefficient/spatial jets for its
    literal zero coefficient direction. This is not an E/B derivative.
    """
    labels = _real(parent_label_points, 'parent label points')
    unit_s3_material_frame(labels)
    q0 = _real(initial_material_points, 'initial material points')
    coefficients = _real(coefficients, 'coefficient vector')
    times = _real(times, 'physical times')
    initial_jacobian = _real(initial_jacobian, 'initial material Jacobian')
    p = len(labels)
    if q0.shape != (p, 4):
        raise ValueError('one explicit initial material point per parent label')
    shapes = ((p, 3, 4), (p, 3, 2, 2), (p, 3))
    seeds = []
    for value, shape, name in zip((initial_material_point_spatial_derivatives,
            initial_bundle_transport_spatial_derivatives,
            initial_jacobian_spatial_derivatives), shapes, ('dF0', 'dU0', 'dJ0')):
        if value is None:
            raise ValueError(f'explicit {name} required; omission is not zero')
        a = np.asarray(value)
        if a.shape != shape or not np.isfinite(a).all():
            raise ValueError(f'finite {name} with shape {shape} required')
        seeds.append(a)
    seeds[0] = _real(seeds[0], 'initial spatial material derivative')
    seeds[2] = _real(seeds[2], 'initial spatial Jacobian derivative')
    initial_body = np.einsum('pra,pir->pai', unit_s3_material_frame(q0), seeds[0])
    if np.any(np.linalg.matrix_rank(initial_body) != 3):
        raise ValueError('nonsingular initial geometric identification required')
    common = dict(coefficients=coefficients, times=times,
        initial_material_points=q0, initial_bundle_transport=initial_bundle_transport,
        initial_jacobian=initial_jacobian, evaluator=evaluator, rtol=rtol, atol=atol)
    base = worldvolume_scalar_transport_ivp(**common)
    variations = []
    differences = []
    for axis in range(3):
        tangent = worldvolume_scalar_transport_ivp(**common,
            coefficient_variation=np.zeros_like(np.asarray(coefficients, float)),
            initial_material_points_variation=seeds[0][:, axis],
            initial_bundle_transport_variation=seeds[1][:, axis],
            initial_jacobian_variation=seeds[2][:, axis])
        variations.append(tangent)
        differences.append(max(float(np.max(abs(tangent[k]-base[k]))) for k in
            ('material_points', 'bundle_transport', 'haar_jacobian')))
    dF = np.stack([x['material_points_variation'] for x in variations], axis=2)
    dU = np.stack([x['bundle_transport_variation'] for x in variations], axis=2)
    dJ = np.stack([x['haar_jacobian_variation'] for x in variations], axis=2)
    frames = np.stack([unit_s3_material_frame(q) for q in base['material_points']])
    # M[time,point,child_body_axis,parent_label_axis].
    M = np.einsum('tpra,tpir->tpai', frames, dF)
    determinant = np.linalg.det(M)
    return dict(base=base, material_point_spatial_derivatives=dF,
        bundle_transport_spatial_derivatives=dU,
        haar_jacobian_spatial_derivatives=dJ,
        spatial_tangent_map=M,
        geometric_jacobian=determinant,
        jacobian_consistency_defect=float(np.max(abs(determinant-base['haar_jacobian']))),
        independent_base_agreement=max(differences),
        derivative_scope='parent-label spatial j1 only; no physical E/B/outgoing derivative',
        physical_primal_selected=False, outgoing_boundary_selected=False)


def affine_birth_connection(*, parent_connection, bundle_transport,
                            spatial_tangent_map, bundle_spatial_derivatives):
    """Construct the child spatial connection required by local incidence.

    M^b_i A_child,b=U A_parent,i U^dagger-(E_i U)U^dagger in anti-Hermitian convention.
    This equation is a birth incidence; it is not inferred as an interior
    consequence of Wilson-line parallel transport.
    """
    A, U, dU = map(np.asarray, (parent_connection, bundle_transport,
        bundle_spatial_derivatives))
    M = _real(spatial_tangent_map, 'spatial tangent map')
    p = len(U)
    if A.shape != (p, 3, 2, 2) or dU.shape != A.shape or M.shape != (p, 3, 3):
        raise ValueError('spatial connection and one-jet shape mismatch')
    if U.shape != (p, 2, 2) or not all(np.isfinite(x).all() for x in (A,U,M,dU)):
        raise ValueError('finite U2 spatial connection data required')
    if not np.allclose(A+A.conj().swapaxes(-1,-2), 0, atol=1e-10, rtol=0):
        raise ValueError('anti-Hermitian parent spatial connection required')
    if not np.allclose(U.conj().swapaxes(-1,-2)@U, np.eye(2), atol=1e-10, rtol=0):
        raise ValueError('unitary bundle transport required')
    if not np.allclose(dU.conj().swapaxes(-1,-2)@U[:,None]
            +U.conj().swapaxes(-1,-2)[:,None]@dU, 0, atol=1e-10, rtol=0):
        raise ValueError('spatial bundle derivative must be tangent to U2')
    if np.any(np.linalg.matrix_rank(M) != 3):
        raise ValueError('nonsingular spatial tangent map required')
    # Thin batch adapter of the existing owned affine connection evaluator.
    return np.stack([induced_connection_transport(a, m, u, du)
        for a, m, u, du in zip(A, M, U, dU)])
