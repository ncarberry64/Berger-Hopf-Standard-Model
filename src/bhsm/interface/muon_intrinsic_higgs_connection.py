"""Owned mechanical Sp1 application on the intrinsic Higgs doublet.

The adopted common-A lepton action represents jmath by -i sigma_weak.
The Higgs is the same fundamental Sp1 representation.  This applies that
background to a supplied common coframe; it does not select a Higgs field,
an Abelian connection, independent gauge fluctuations, or a temporal lift.

The scalar density wS=lapse*R4 contracts unit-S3 derivatives.  Its connection
coefficient is therefore R4 times the physical orthonormal coefficient:
lambda_geom-1 on incoming parent sigma1, or lambda_geom on an explicitly
identified child sigma0 patch.  Radius motion must not be inserted twice.
"""
from __future__ import annotations

import numpy as np

from .bhsm_standard_model_gauge_vertices import su2_fundamental_generators


PARENT_PATCH = 'parent_sigma1'
CHILD_PATCH = 'child_sigma0'
CHILD_PATCH_OWNER = 'muon_owned_connection_application.apply_saved_child_profiles'


def _real(value, name):
    if value is None:
        raise ValueError(f'explicit {name} required')
    raw = np.asarray(value)
    if np.iscomplexobj(raw) and np.any(raw.imag != 0):
        raise ValueError(f'real {name} required')
    result = np.asarray(value, dtype=float)
    if not np.isfinite(result).all():
        raise ValueError(f'finite {name} required')
    return result


def _rotation_jet(rotation, first, second):
    values = [_real(x, name) for x, name in (
        (rotation, 'Ad SO3 coframe transport'),
        (first, 'Ad transport first jet'),
        (second, 'Ad transport second jet'))]
    if any(x.shape[-2:] != (3, 3) for x in values):
        raise ValueError('Ad transport jets need (...,3,3)')
    try:
        R, R1, R2 = np.broadcast_arrays(*values)
    except ValueError as error:
        raise ValueError('Ad transport jets must have a common shape') from error
    transpose = lambda x: np.swapaxes(x, -1, -2)
    I = np.eye(3)
    # These are representation consistency checks, not physical error bounds.
    if not np.allclose(transpose(R)@R, I, rtol=0, atol=1e-12) or not np.allclose(
            np.linalg.det(R), 1, rtol=0, atol=1e-12):
        raise ValueError('orientation-preserving orthogonal Ad transport required')
    if not np.allclose(transpose(R1)@R+transpose(R)@R1, 0, rtol=0, atol=1e-11):
        raise ValueError('first Ad jet must be tangent to SO3')
    if not np.allclose(transpose(R2)@R+2*transpose(R1)@R1+transpose(R)@R2,
                       0, rtol=0, atol=1e-11):
        raise ValueError('second Ad jet must preserve the SO3 two-jet')
    return R, R1, R2


def mechanical_higgs_connection_two_jet(*, radius, radius_first, radius_second,
                                       lambda_geom, lambda_first, lambda_second,
                                       rotation, rotation_first, rotation_second,
                                       patch=PARENT_PATCH, child_patch_owner=None):
    """Return spatial anti-Hermitian background coefficients and normal jets.

    All derivatives are in the caller's one common normal chart.  An identity
    rotation with zero jets may describe fixed body coordinates, but must be
    supplied explicitly; it is not inferred as a physical angular mode.
    The child formula is enabled only with its retained patch owner named.
    No time-component zero is appended to these three spatial coefficients.
    """
    if patch == PARENT_PATCH:
        offset = 1.
        coefficient_owner = 'muon_owned_connection_application.regular_parent_background_prefactor'
    elif patch == CHILD_PATCH and child_patch_owner == CHILD_PATCH_OWNER:
        offset = 0.
        coefficient_owner = CHILD_PATCH_OWNER
    else:
        raise ValueError('owned parent sigma1 or explicitly owned child sigma0 patch required')
    scalar = [_real(x, name) for x, name in (
        (radius, 'R4'), (radius_first, 'R4 first jet'),
        (radius_second, 'R4 second jet'), (lambda_geom, 'lambda_geom'),
        (lambda_first, 'lambda first jet'), (lambda_second, 'lambda second jet'))]
    R, R1, R2 = _rotation_jet(rotation, rotation_first, rotation_second)
    try:
        shape = np.broadcast_shapes(*(x.shape for x in scalar), R.shape[:-2])
    except ValueError as error:
        raise ValueError('geometry and coframe jets must have a common point shape') from error
    r, r1, r2, lam, l1, l2 = [np.broadcast_to(x, shape) for x in scalar]
    R, R1, R2 = [np.broadcast_to(x, shape+(3, 3)) for x in (R, R1, R2)]
    if np.any(r <= 0) or np.any((lam < 0)|(lam > 1)):
        raise ValueError('positive R4 and geometric lambda in [0,1] required')
    k = lam-offset
    c = k/r
    c1 = l1/r-k*r1/r**2
    c2 = l2/r-2*l1*r1/r**2-k*r2/r**2+2*k*r1**2/r**3
    # -2i*(sigma/2) is the already-owned jmath=-i sigma representation.
    generators = -2j*np.asarray(su2_fundamental_generators())
    def combine(a, a1, a2):
        return (
            np.einsum('...ad,dij->...aij', a[..., None, None]*R, generators),
            np.einsum('...ad,dij->...aij', a1[..., None, None]*R+a[..., None, None]*R1,
                      generators),
            np.einsum('...ad,dij->...aij', a2[..., None, None]*R
                      +2*a1[..., None, None]*R1+a[..., None, None]*R2, generators))
    unit = combine(k, l1, l2)
    physical = combine(c, c1, c2)
    if not all(np.isfinite(x).all() for x in (*unit, *physical)):
        raise ValueError('finite mechanical connection two-jet required')
    return dict(
        unit_s3_connection=unit[0], unit_s3_connection_first=unit[1],
        unit_s3_connection_second=unit[2],
        orthonormal_connection=physical[0], orthonormal_connection_first=physical[1],
        orthonormal_connection_second=physical[2],
        unit_s3_coefficient=k, unit_s3_coefficient_first=l1, unit_s3_coefficient_second=l2,
        orthonormal_coefficient=c, orthonormal_coefficient_first=c1,
        orthonormal_coefficient_second=c2,
        derivative_convention='partial normal two-jet at fixed field coordinates',
        density_convention='wS=lapse*R4 contracts unit-S3 derivatives',
        patch=patch, coefficient_owner=coefficient_owner,
        representation_owner='muon_owned_connection_application.mechanical_background_action',
        generator_owner='bhsm_standard_model_gauge_vertices.su2_fundamental_generators',
        higgs_bundle_owner='aether_hybrid_standard_model_bundle_v15_53.chiral_bundle_contract',
        temporal_connection=None, independent_u1_connection=None,
        independent_gauge_fluctuation=None, physical_scalar_primal_selected=False,
        full_gauge_connection_claimed=False, stationarity_claimed=False)


def mechanical_higgs_connection_from_weight_jet(weights, *, rotation,
                                                rotation_first, rotation_second,
                                                normal_index=None, patch=PARENT_PATCH,
                                                child_patch_owner=None):
    """Consume the retained intrinsic-M4 geometric Jet without rerunning it.

    The default index is its owned normal source coordinate s.  Supplied
    coframe jets must use that same index; no angular transport is inferred.
    """
    index = weights['source_indices'][0] if normal_index is None else normal_index
    if not isinstance(index, (int, np.integer)) or isinstance(index, (bool, np.bool_)):
        raise ValueError('integer normal jet index required')
    r, lam = weights['R4'], weights['mechanical_connection_lambda']
    if index < 0 or index >= len(r.gradient) or index >= len(lam.gradient):
        raise ValueError('normal index outside supplied geometry jet')
    return mechanical_higgs_connection_two_jet(
        radius=r.value, radius_first=r.gradient[index], radius_second=r.hessian[index, index],
        lambda_geom=lam.value, lambda_first=lam.gradient[index],
        lambda_second=lam.hessian[index, index], rotation=rotation,
        rotation_first=rotation_first, rotation_second=rotation_second,
        patch=patch, child_patch_owner=child_patch_owner)


def apply_fixed_field_connection_two_jet(connection, *, H, phi):
    """Apply only this background spatial insertion to fixed doublets.

    Values and first/second jets are A_H H and A_H phi in unit-S3 derivatives.
    They must be added to the corresponding ordinary derivative and other
    owned gauge terms.  Induced h belongs in the coupled Jacobian, not here.
    """
    arrays = [np.asarray(connection[k], dtype=complex) for k in (
        'unit_s3_connection', 'unit_s3_connection_first', 'unit_s3_connection_second')]
    if any(x.shape[-3:] != (3, 2, 2) for x in arrays) or any(
            x.shape != arrays[0].shape or not np.isfinite(x).all() for x in arrays):
        raise ValueError('finite common-shape spatial connection two-jet required')
    shape = arrays[0].shape[:-3]+(2,)
    def field(x, name):
        if x is None:
            raise ValueError(f'explicit fixed {name} required')
        value = np.asarray(x, dtype=complex)
        if value.shape != shape or not np.isfinite(value).all():
            raise ValueError(f'finite {name} doublet on connection points required')
        return value
    h, test = field(H, 'H'), field(phi, 'phi')
    def apply(A, value):
        return np.einsum('...aij,...j->...ai', A, value)
    return dict(spatial_DH_background=apply(arrays[0], h),
                delta_spatial_DH=apply(arrays[1], h),
                second_spatial_DH=apply(arrays[2], h),
                spatial_Dphi_background=apply(arrays[0], test),
                delta_spatial_Dphi=apply(arrays[1], test),
                second_spatial_Dphi=apply(arrays[2], test),
                derivative_convention='unit-S3 spatial; explicit connection jet at fixed H and phi',
                full_DH_claimed=False, induced_H_response_included=False)
