"""Uneliminated AE3.1 lepton Euler applications on one coefficient vector.

These are the coefficient applications of the retained Grassmann field
equations, not a commuting spinor background, an LSZ insertion, a CAR state
or an extra determinant.  A solver supplies its represented domain and
covariant derivative maps; values and derivatives are never independent
profiles.  Numerical coefficients can test/represent the Euler operators
without assigning a physical fermion bilinear expectation.
"""
from __future__ import annotations

import numpy as np

from .muon_birth_candidate_geometry_action import ROOT, evaluate_retained_candidate_geometry
from .muon_intrinsic_higgs_weak_action import (
    lepton_higgs_source, lepton_higgs_source_variation,
    retained_higgs_spin_charge_representation,
)


def classical_bosonic_body_source(points):
    """Derived zero of this local Grassmann bilinear's classical body.

    The geometric attachment explicitly keeps fermion_background zero
    classically and determinant backreaction quantum.  Odd Grassmann
    variables have zero body; their bilinear has zero commuting body.
    This does not evaluate/delete an induced quantum Higgs load or replace
    the full sourced microscopic action by its classical body.
    """
    from .aether_diagonal_sp1_m4_attachment_v15_50 import action_ownership_ledger
    if type(points) is not int or points < 1:
        raise ValueError('positive number of represented points required')
    owner = action_ownership_ledger()
    if owner['fermion_background'] != 'zero_classically;_determinant_backreaction_quantum':
        raise ValueError('retained classical fermion-body convention changed')
    return dict(J_H_body=np.zeros((points, 2), complex),
                classification='DERIVED_CLASSICAL_BODY_ZERO_OF_LOCAL_GRASSMANN_YUKAWA_SOURCE',
                owner='aether_diagonal_sp1_m4_attachment_v15_50.action_ownership_ledger',
                equation='body(bar(e_R) Y_l^dagger L_L)=0',
                scope='Local uneliminated classical bosonic body only',
                quantum_induced_H_load=None,
                quantum_effects_deleted=False,
                numerical_commuting_spinor_iterate_is_body_source=False)


def _finite(value, name, *, real=False):
    result = np.asarray(value, dtype=float if real else complex)
    if not np.isfinite(result).all():
        raise ValueError(f'{name} must be finite')
    return result


def _maps(coefficients, value_map_L, value_map_e, derivative_map_L, derivative_map_e):
    c = _finite(coefficients, 'coefficients')
    L, e = _finite(value_map_L, 'value_map_L'), _finite(value_map_e, 'value_map_e')
    DL, De = (_finite(derivative_map_L, 'derivative_map_L'),
              _finite(derivative_map_e, 'derivative_map_e'))
    if c.ndim != 1 or len(c) == 0:
        raise ValueError('coefficients must be a nonempty common complex vector')
    if L.ndim != 5 or L.shape[1] != 2 or L.shape[3:] != (2, len(c)) or len(L) == 0:
        raise ValueError('value_map_L needs (points,2,families,2,coefficients)')
    points, families = L.shape[0], L.shape[2]
    if e.shape != (points, families, 2, len(c)):
        raise ValueError('value_map_e needs (points,families,2,coefficients)')
    if DL.shape != (points, 4, 2, families, 2, len(c)):
        raise ValueError('derivative_map_L shape disagrees with the common coefficient map')
    if De.shape != (points, 4, families, 2, len(c)):
        raise ValueError('derivative_map_e shape disagrees with the common coefficient map')
    return c, L, e, DL, De


def lepton_fields_from_coefficients(*, coefficients, value_map_L, value_map_e,
                                   derivative_map_L, derivative_map_e):
    """Apply one represented vector to both values and covariant derivatives.

    Derivative maps carry the caller's gauge/spin/domain connections in the
    declared coordinates.  Their construction is a represented operator
    application, not independent supplied spinor profiles.
    """
    c, L, e, DL, De = _maps(coefficients, value_map_L, value_map_e,
                            derivative_map_L, derivative_map_e)
    return dict(L_L=np.einsum('pafsk,k->pafs', L, c),
                e_R=np.einsum('pfsk,k->pfs', e, c),
                D_L_L=np.einsum('pmafsk,k->pmafs', DL, c),
                D_e_R=np.einsum('pmfsk,k->pmfs', De, c))


def intrinsic_round_dirac_coefficients(*, N, R4, coordinate_log_R4_rate):
    """Retained round-S3 coframe principal and contracted spin operators.

    Coordinate t and unit-S3 body derivatives are used.  The connection
    owner has S_S3=-3i gamma1 gamma2 gamma3/2, and the temporal spin term
    3 H4 i gamma0/2 with H4=(partial_t log R4)/N.  These geometric terms
    belong in the derivative maps OR this contracted term, once.  Other
    gauge/connection applications are not selected by this binder.
    """
    N, r, rate = np.broadcast_arrays(_finite(N, 'N', real=True),
                                     _finite(R4, 'R4', real=True),
                                     _finite(coordinate_log_R4_rate, 'coordinate_log_R4_rate', real=True))
    if np.any(N <= 0) or np.any(r <= 0):
        raise ValueError('positive intrinsic lapse and radius required')
    representation = retained_higgs_spin_charge_representation()
    gamma = representation['gamma_LR']
    factors = np.stack((1/N, 1/r, 1/r, 1/r), axis=-1)
    principal = 1j*factors[..., :, None, None]*gamma
    angular_unit = -1.5j*gamma[1]@gamma[2]@gamma[3]
    temporal = (1.5*rate/N)[..., None, None]*(1j*gamma[0])
    angular = angular_unit/r[..., None, None]
    return dict(principal_euler_coefficients=principal,
                contracted_spin=temporal+angular,
                temporal_spin=temporal, angular_spin=angular,
                H4=rate/N, angular_spin_unit=angular_unit,
                signature='+---', derivative_coordinates='coordinate t and unit-S3 body derivatives',
                spin_placement='CONTRACTED_ZERO_ORDER',
                connection_owners=(
                    'muon_parent_source_contact.cut_metric_dirac_actions',
                    'muon_wall_input_attachment.intrinsic_reference_rows'),
                physical_gauge_fluctuation=None,
                physical_matter_field_selected=False)


def retained_e1_lepton_geometry_coefficients(repository=ROOT):
    """Evaluate coframe/spin coefficients from the retained actual E1+ state."""
    candidate = evaluate_retained_candidate_geometry(repository)
    g = candidate['geometry']
    lam = g['lambda_geom']
    rates = g['coordinate_time_log_rates']
    log_rate = (1-lam)*rates['A']+lam*rates['B']
    return dict(geometry_source=candidate['source'], N=g['N'], R4=g['R4'],
                coordinate_log_R4_rate=log_rate,
                operator=intrinsic_round_dirac_coefficients(
                    N=g['N'], R4=g['R4'], coordinate_log_R4_rate=log_rate),
                classification='EVALUATED_RETAINED_E1_PLUS_GEOMETRIC_LEPTON_COEFFICIENTS',
                full_stationary_base=False)


def _operators(points, principal_euler_coefficients, contracted_spin, spin_placement):
    principal = _finite(principal_euler_coefficients, 'principal_euler_coefficients')
    try:
        principal = np.broadcast_to(principal, (points, 4, 4, 4))
    except ValueError as error:
        raise ValueError('principal_euler_coefficients need (4,4,4) or (points,4,4,4)') from error
    if spin_placement == 'IN_DERIVATIVE_MAPS':
        if contracted_spin is not None:
            raise ValueError('spin cannot be supplied twice: it is already in derivative maps')
        spin = np.zeros((points, 4, 4), complex)
    elif spin_placement == 'CONTRACTED_ZERO_ORDER':
        if contracted_spin is None:
            raise ValueError('contracted spin operator must be explicitly supplied')
        try:
            spin = np.broadcast_to(_finite(contracted_spin, 'contracted_spin'), (points, 4, 4))
        except ValueError as error:
            raise ValueError('contracted_spin needs (4,4) or (points,4,4)') from error
    else:
        raise ValueError('declare spin_placement as IN_DERIVATIVE_MAPS or CONTRACTED_ZERO_ORDER')
    # A slash operator is chirality odd; the scalar LR vertices are separate.
    for name, value in (('principal', principal), ('contracted_spin', spin)):
        if np.max(np.abs(value[..., :2, :2])) > 1e-12 or np.max(np.abs(value[..., 2:, 2:])) > 1e-12:
            raise ValueError(f'{name} must be chirality odd in the retained LR frame')
    return principal, spin


def _embed(fields, representation):
    left, right = representation['left_weyl_embedding_LR'], representation['right_weyl_embedding_LR']
    return dict(L=np.einsum('si,pafi->pafs', left, fields['L_L']),
                e=np.einsum('si,pfi->pfs', right, fields['e_R']),
                DL=np.einsum('si,pmafi->pmafs', left, fields['D_L_L']),
                De=np.einsum('si,pmfi->pmfs', right, fields['D_e_R']))


def _euler(fields4, H, principal, spin, Y, representation):
    L, e, DL, De = (fields4[key] for key in ('L', 'e', 'DL', 'De'))
    temporal_L = np.einsum('pst,paft->pafs', principal[:, 0], DL[:, 0])
    spatial_L = np.einsum('pmst,pmaft->pafs', principal[:, 1:], DL[:, 1:])
    temporal_e = np.einsum('pst,pft->pfs', principal[:, 0], De[:, 0])
    spatial_e = np.einsum('pmst,pmft->pfs', principal[:, 1:], De[:, 1:])
    spin_L, spin_e = (np.einsum('pst,paft->pafs', spin, L),
                       np.einsum('pst,pft->pfs', spin, e))
    vertex_L = np.einsum('pa,fg,pgs->pafs', H, Y, e)
    vertex_e = np.einsum('pa,gf,pags->pfs', H.conj(), Y.conj(), L)
    EL4 = temporal_L+spatial_L+spin_L-vertex_L
    Ee4 = temporal_e+spatial_e+spin_e-vertex_e
    right, left = representation['right_weyl_embedding_LR'], representation['left_weyl_embedding_LR']
    return dict(Euler_L=np.einsum('si,pafs->pafi', right.conj(), EL4),
                Euler_e=np.einsum('si,pfs->pfi', left.conj(), Ee4),
                Euler_L_full=EL4, Euler_e_full=Ee4,
                temporal_L=temporal_L, spatial_L=spatial_L, spin_L=spin_L,
                temporal_e=temporal_e, spatial_e=spatial_e, spin_e=spin_e,
                Yukawa_L=vertex_L, Yukawa_e=vertex_e)


def lepton_primal_application(*, coefficients, value_map_L, value_map_e,
                             derivative_map_L, derivative_map_e, H,
                             principal_euler_coefficients, contracted_spin,
                             spin_placement):
    """Both owned Weyl Euler equations and J_H from the same unknowns.

    No independent linear Grassmann load occurs in this literal S4_lH
    term.  Such a load must have its separate owner before being added.
    Boundary/matching equations and any effective contribution are separate
    applications of the same problem, not inferred from an LSZ mode here.
    """
    fields = lepton_fields_from_coefficients(
        coefficients=coefficients, value_map_L=value_map_L, value_map_e=value_map_e,
        derivative_map_L=derivative_map_L, derivative_map_e=derivative_map_e)
    points, _, families, _ = fields['L_L'].shape
    if families != 3:
        raise ValueError('retained Y_l has three family coordinates')
    H = _finite(H, 'H')
    if H.shape != (points, 2):
        raise ValueError('H needs (points,2) from the scalar coefficient map')
    representation = retained_higgs_spin_charge_representation()
    principal, spin = _operators(points, principal_euler_coefficients, contracted_spin, spin_placement)
    full = _embed(fields, representation)
    source = lepton_higgs_source(L_L=full['L'], e_R=full['e'],
                                Y_l=representation['family_yukawa'],
                                gamma0=representation['gamma0_LR'])
    return dict(**fields, **_euler(full, H, principal, spin,
                                  representation['family_yukawa'], representation),
                J_H=source, full_fields=full,
                source_representation='FORMAL_BILINEAR_COEFFICIENT_APPLICATION_OF_UNELIMINATED_GRASSMANN_ACTION',
                J_H_is_classical_bosonic_body=False,
                physical_bilinear_expectation_selected=False,
                loop_or_native_heat_added=False)


def _map_jet(value, delta, name):
    if delta is None:
        return np.zeros_like(value)
    result = _finite(delta, name)
    if result.shape != value.shape:
        raise ValueError(f'{name} shape disagrees with its base map')
    return result


def lepton_primal_jacobian_application(*, coefficients, delta_coefficients,
                                      value_map_L, value_map_e,
                                      derivative_map_L, derivative_map_e, H, delta_H,
                                      principal_euler_coefficients, contracted_spin,
                                      spin_placement,
                                      delta_value_map_L=None, delta_value_map_e=None,
                                      delta_derivative_map_L=None, delta_derivative_map_e=None,
                                      delta_principal_euler_coefficients=None,
                                      delta_contracted_spin=None, delta_gamma0_LR=None):
    """Real-linear matter/H/metric/frame cross application on one vector.

    Operator-map jets implement the prescribed geometry/gauge/domain
    dependence.  Missing optional jets hold those mathematical inputs fixed;
    they do not certify a physical zero.  J_H keeps both conjugate matter
    variation and the supplied adjoint-frame variation.
    """
    c, L, e, DL, De = _maps(coefficients, value_map_L, value_map_e,
                            derivative_map_L, derivative_map_e)
    dc = _finite(delta_coefficients, 'delta_coefficients')
    if dc.shape != c.shape:
        raise ValueError('delta_coefficients shape disagrees')
    base_fields = lepton_fields_from_coefficients(
        coefficients=c, value_map_L=L, value_map_e=e, derivative_map_L=DL, derivative_map_e=De)
    delta_fields = lepton_fields_from_coefficients(
        coefficients=dc, value_map_L=L, value_map_e=e, derivative_map_L=DL, derivative_map_e=De)
    moved_fields = lepton_fields_from_coefficients(
        coefficients=c, value_map_L=_map_jet(L, delta_value_map_L, 'delta_value_map_L'),
        value_map_e=_map_jet(e, delta_value_map_e, 'delta_value_map_e'),
        derivative_map_L=_map_jet(DL, delta_derivative_map_L, 'delta_derivative_map_L'),
        derivative_map_e=_map_jet(De, delta_derivative_map_e, 'delta_derivative_map_e'))
    delta_fields = {key:delta_fields[key]+moved_fields[key] for key in delta_fields}
    points = len(L)
    H, dH = _finite(H, 'H'), _finite(delta_H, 'delta_H')
    if H.shape != (points, 2) or dH.shape != H.shape:
        raise ValueError('H/delta_H need matching (points,2) arrays')
    representation = retained_higgs_spin_charge_representation()
    Y = representation['family_yukawa']
    principal, spin = _operators(points, principal_euler_coefficients, contracted_spin, spin_placement)
    dprincipal = np.zeros_like(principal) if delta_principal_euler_coefficients is None else _finite(
        delta_principal_euler_coefficients, 'delta_principal_euler_coefficients')
    try:
        dprincipal = np.broadcast_to(dprincipal, principal.shape)
    except ValueError as error:
        raise ValueError('delta_principal_euler_coefficients shape disagrees') from error
    dspin = np.zeros_like(spin) if delta_contracted_spin is None else _finite(
        delta_contracted_spin, 'delta_contracted_spin')
    try:
        dspin = np.broadcast_to(dspin, spin.shape)
    except ValueError as error:
        raise ValueError('delta_contracted_spin shape disagrees') from error
    if spin_placement == 'IN_DERIVATIVE_MAPS' and delta_contracted_spin is not None:
        raise ValueError('spin jet cannot be supplied twice')
    full, dfull = _embed(base_fields, representation), _embed(delta_fields, representation)
    # Euler is linear in fermions/operators, bilinear in the Higgs vertices.
    varied_fields = _euler(dfull, H, principal, spin, Y, representation)
    varied_operator = _euler(full, dH, dprincipal, dspin, Y, representation)
    dJ = lepton_higgs_source_variation(
        L_L=full['L'], e_R=full['e'], Y_l=Y, gamma0=representation['gamma0_LR'],
        delta_L_L=dfull['L'], delta_e_R=dfull['e'], delta_gamma0=delta_gamma0_LR)
    return dict(delta_Euler_L=varied_fields['Euler_L']+varied_operator['Euler_L'],
                delta_Euler_e=varied_fields['Euler_e']+varied_operator['Euler_e'],
                delta_J_H=dJ, delta_fields=delta_fields,
                physical_bilinear_expectation_selected=False)


def lepton_weak_euler_rows(*, application, test_L, test_e, quadrature, volume_density):
    """Complex left-Euler covectors in the supplied intrinsic-M4 pairing.

    These are variations with respect to independent barred Grassmann
    variables.  No bosonic 2 Re factor is inserted in the complex Euler
    operator.  A real-coordinate solver may separately realify its rows.
    """
    EL, Ee = application['Euler_L'], application['Euler_e']
    tests_L, tests_e = _finite(test_L, 'test_L'), _finite(test_e, 'test_e')
    if tests_L.ndim != 5 or tests_L.shape[1:] != EL.shape:
        raise ValueError('test_L needs (tests,points,2,families,2)')
    if tests_e.ndim != 4 or tests_e.shape[1:] != Ee.shape:
        raise ValueError('test_e needs (tests,points,families,2)')
    quad = _finite(quadrature, 'quadrature', real=True)
    volume = _finite(volume_density, 'volume_density', real=True)
    try:
        weight = np.broadcast_to(quad, (len(EL),))*np.broadcast_to(volume, (len(EL),))
    except ValueError as error:
        raise ValueError('quadrature and volume_density need scalar or point arrays') from error
    if np.any(quad < 0) or np.any(volume <= 0):
        raise ValueError('nonnegative quadrature and positive volume required')
    return dict(L=np.einsum('p,kpafs,pafs->k', weight, tests_L.conj(), EL),
                e=np.einsum('p,kpfs,pfs->k', weight, tests_e.conj(), Ee))


def realify_euler_rows(rows):
    """Real/imaginary equations of the same complex Euler covectors."""
    value = np.concatenate((np.asarray(rows['L']).ravel(), np.asarray(rows['e']).ravel()))
    return np.r_[value.real, value.imag]
