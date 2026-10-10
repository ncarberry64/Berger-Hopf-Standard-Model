"""Action-bound canonical lepton Hamiltonian and product-factor forms.

The positive-current coefficient is chi=R4**(3/2)*psi.  The retained Lorentz
Euler operator then gives i D_tau chi=H_can chi, with no temporal spin-density
term.  Its spatial/mass/gauge applications below use the actual LR frame and
fixed Y_l.  They extend the already retained product-factor coefficient W;
they do not equate Lorentz evolution with the spectral heat semigroup.

A=D_tau_factor+W_spatial_mass extends the retained separated positive
product factor only after its temporal covariant connection is bound.
The Lorentz Hamiltonian's -i Omega_tau is NOT that connection.  The full
stratified graph, quotient, exterior return and moving-domain jets must
still be bound before the form core is a physical HeatPencil.
No routine in this module heats the Lorentz Euler or a source compression.
"""
from __future__ import annotations

import math

import numpy as np

from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from .muon_intrinsic_lepton_primal import retained_e1_lepton_geometry_coefficients


FACTOR_OWNER = 'ae4_current_c2_factorized_hs_calderon.factorized_product_dirac_hs_weyl_jet'
NATIVE_OWNER = 'ae4_stratified_dirac_zeta_induced_owner.microscopic_owner_contract'
FRAME_ORDER = 'L_L[weak,family,spin2], e_R[family,spin2]'


def _finite(value, name):
    if value is None:
        raise ValueError(f'{name} is required')
    try:
        raw = np.asarray(value)
        if raw.dtype == object and any(type(x).__module__.split('.')[0] == 'flint'
                                       for x in raw.flat):
            raise ValueError(f'{name} needs point coefficients, not interval entries')
        result = np.asarray(value, complex)
    except (TypeError, OverflowError) as error:
        raise ValueError(f'{name} must contain finite point coefficients') from error
    if not np.isfinite(result).all():
        raise ValueError(f'{name} must be finite')
    return result


def _radius(value, count):
    try:
        radius = np.broadcast_to(np.asarray(value, float), (count,))
    except (TypeError, ValueError) as error:
        raise ValueError('R4 needs one positive radius per represented point') from error
    if not np.isfinite(radius).all() or np.any(radius <= 0):
        raise ValueError('R4 needs one positive radius per represented point')
    return radius


def lepton_current_hilbert_representation():
    """Eighteen Weyl components and their canonical positive current Gram.

    This counts the left weak doublet and right charged singlet in all three
    families.  It is a point fiber, not an angular or temporal truncation.
    The neutral left component remains present for a general Higgs doublet.
    """
    rep = retained_higgs_spin_charge_representation()
    gamma = rep['gamma_LR']
    alpha = np.array([gamma[0]@gamma[a] for a in range(1, 4)])
    full_alpha = []
    for item in alpha:
        result = np.zeros((18, 18), complex)
        result[:12, :12] = np.kron(np.eye(6), item[:2, :2])
        result[12:, 12:] = np.kron(np.eye(3), item[2:, 2:])
        full_alpha.append(result)
    gamma5 = np.diag(np.r_[-np.ones(12), np.ones(6)]).astype(complex)
    charge = np.diag(np.r_[np.zeros(6), -np.ones(12)]).astype(complex)
    return dict(alpha=np.array(full_alpha), gamma5=gamma5,
        Gram=np.eye(18, dtype=complex), EM_charge=charge,
        Higgs_EM_charge=np.diag([1., 0.]).astype(complex),
        family_Y=np.asarray(rep['family_yukawa']), frame_order=FRAME_ORDER,
        positive_current='j_normal=psi_dagger psi; chi=R4^(3/2)psi; Haar Gram identity',
        round_spatial_Dhat='-i sigma^a E_a+3/2',
        factor_massless_W='diag(-Dhat_S3,+Dhat_S3)/R4 on the appropriate Weyl copies',
        angular_or_temporal_cutoff_selected=False,
        CAR_state_selected=False, full_stratified_statistics_lift=False)


def fixed_y_higgs_hamiltonian(H):
    """Hermitian LR Hamiltonian mass map for a GENERAL complex H doublet.

    V_(a,f,s;g,t)=H_a Y_(f,g) delta_(s,t).  The reverse vertex is V^dagger.
    Values use the same H units as the represented proper-clock operator.
    No Higgs axis, profile, magnitude or independent Yukawa is selected.
    """
    h = _finite(H, 'H')
    if h.ndim != 2 or h.shape[1] != 2 or not len(h):
        raise ValueError('H needs (points,2) from the coupled scalar map')
    y = lepton_current_hilbert_representation()['family_Y']
    v = np.einsum('pa,fg,st->pafsgt', h, y, np.eye(2)).reshape(len(h), 12, 6)
    result = np.zeros((len(h), 18, 18), complex)
    result[:, :12, 12:] = v
    result[:, 12:, :12] = v.conj().transpose(0, 2, 1)
    return result


def _coefficient_maps(value_map, spatial_derivative_map):
    values = _finite(value_map, 'value_map')
    spatial = _finite(spatial_derivative_map, 'spatial_derivative_map')
    if values.ndim != 3 or values.shape[1] != 18 or not len(values) or not values.shape[2]:
        raise ValueError('value_map needs (points,18,coefficients) in the inherited frame')
    if spatial.shape != (len(values), 3, 18, values.shape[2]):
        raise ValueError('spatial_derivative_map needs (points,3,18,coefficients)')
    return values, spatial


def _gauge_connections(value, count):
    connection = _finite(value, 'gauge_connection')
    if connection.shape != (count, 4, 18, 18):
        raise ValueError('gauge_connection needs (points,4,18,18): proper tau then unit-S3 components')
    scale = max(1., float(np.max(abs(connection))))
    if np.max(abs(connection+connection.conj().transpose(0, 1, 3, 2))) > 2e-12*scale:
        raise ValueError('anti-Hermitian gauge connection is required')
    alpha = lepton_current_hilbert_representation()['alpha']
    # Componentwise [alpha_a,Omega_a]=0 is too weak: i alpha_a would pass
    # despite being a spin matrix.  Internal gauge actions commute with the
    # ENTIRE spin algebra, including in their proper-time component.
    for spin in alpha:
        if np.max(abs(spin@connection-connection@spin)) > 2e-12*scale:
            raise ValueError('gauge connection must act internally; round spin is included separately')
    return connection


def canonical_lepton_hamiltonian_maps(*, value_map, spatial_derivative_map,
        H, R4, gauge_connection):
    """Construct the actual local Hamiltonian application from owned maps.

    H_can=-i alpha^a(E_a+Omega_a)/R4+(3/2)gamma5/R4+M(H)-i Omega_tau.
    E_a are the retained right body derivatives; Omega_a are unit-S3
    connection components, whereas Omega_tau is on the proper physical clock.
    An orthonormal spatial connection is multiplied by R4 before this call.
    The contracted round spin is included exactly once, here.
    R4 is the retained round radius, constant on each spatial slice; its
    temporal values may vary between represented points.  A general
    spatially varying conformal radius needs its own spin/coframe owner.
    """
    values, spatial = _coefficient_maps(value_map, spatial_derivative_map)
    count = len(values)
    r = _radius(R4, count)
    mass = fixed_y_higgs_hamiltonian(H)
    if len(mass) != count:
        raise ValueError('H point count disagrees with represented coefficient maps')
    omega = _gauge_connections(gauge_connection, count)
    rep = lepton_current_hilbert_representation()
    covariant = spatial+np.einsum('paij,pjk->paik', omega[:, 1:], values)
    derivative = -1j*np.einsum('aij,pajk->pik', rep['alpha'], covariant)/r[:, None, None]
    spin = 1.5*rep['gamma5'][None]/r[:, None, None]
    zero_order = spin+mass-1j*omega[:, 0]
    result = derivative+zero_order@values
    return dict(hamiltonian_map=result, spatial_covariant_derivative_map=covariant,
        spatial_mass_hamiltonian_map=derivative+(spin+mass)@values,
        spatial_principal_map=derivative, zero_order=zero_order,
        contracted_round_spin=spin, fixed_Y_H_mass=mass,
        temporal_gauge_potential=-1j*omega[:, 0],
        frame_order=FRAME_ORDER,
        derivative_coordinates='proper physical tau; unit-S3 right body coframe',
        spin_density_rescale='chi=R4^(3/2)psi; temporal3H4/2 spin cancels',
        canonical_evolution_equation='i partial_tau chi=H_can chi',
        represented_spatial_Hermiticity_requires_full_Haar_domain=True,
        stationary_H_or_gauge_selected=False, native_heat_evaluated=False)


def electromagnetic_hamiltonian_source_maps(*, value_map, R4,
        photon_one_form, electromagnetic_coupling, delta_H):
    """Source-affine Hamiltonian insertion at fixed represented geometry.

    Photon components are (proper-tau,unit-S3 coframe).  delta_Omega=-i e Q a;
    delta_H is REQUIRED, even if a proven fixed-field path supplies zero.
    A gauge orbit with charged H_1 must include delta_H=i theta Q_H H.
    Coupled physical normal/source derivatives also require their map/domain
    jets; this local insertion never declares those jets zero.
    """
    values = _finite(value_map, 'value_map')
    if values.ndim != 3 or values.shape[1] != 18 or not len(values):
        raise ValueError('value_map needs (points,18,coefficients)')
    count = len(values)
    r = _radius(R4, count)
    a = _finite(photon_one_form, 'photon_one_form')
    if a.shape != (count, 4) or np.any(a.imag != 0):
        raise ValueError('real photon_one_form needs (points,4) in the stated coframe')
    if isinstance(electromagnetic_coupling, bool):
        raise ValueError('positive electromagnetic coupling required')
    try:
        e = float(electromagnetic_coupling)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError('positive electromagnetic coupling required') from error
    if not math.isfinite(e) or e <= 0:
        raise ValueError('positive electromagnetic coupling required')
    rep = lepton_current_hilbert_representation()
    q = rep['EM_charge']
    mass = fixed_y_higgs_hamiltonian(delta_H)
    if len(mass) != count:
        raise ValueError('delta_H point count disagrees')
    omega = -1j*e*a[:, :, None, None]*q
    insertion = mass-1j*omega[:, 0]
    insertion -= 1j*np.einsum('aij,pajk->pik', rep['alpha'], omega[:, 1:])/r[:, None, None]
    return dict(source_operator=insertion, source_map=insertion@values,
        delta_Omega=omega, delta_mass=mass,
        spatial_mass_source_operator=insertion+1j*omega[:, 0],
        source_equation='Xi_a=-e[Q a_tau+alpha^i Q a_i/R4]+M(delta_H)',
        charge_owner='nu_L=0,e_L=e_R=-1; all three fixed-Y families retained',
        source_affine_fixed_geometry_only=True,
        physical_coupled_source_or_domain_jet_selected=False,
        native_heat_evaluated=False)


def inherited_product_factor_maps(*, proper_time_derivative_map,
        spatial_mass_hamiltonian_map, factor_temporal_connection_map):
    """A=partial_tau+Omega_tau_factor+W_spatial_mass on represented maps.

    The factor temporal connection application is REQUIRED.  It may not
    be inferred from the Lorentz Hamiltonian term -i Omega_tau.  With a
    matched unitary frame it transforms by Omega' = U Omega U^dagger
    -(partial_tau U) U^dagger, so the full factor transforms covariantly.
    This condition proves no analytic continuation or whole native domain.
    A proved temporal-gauge restriction supplies zero together with its
    domain/frame-return map; the function never selects such a gauge.
    """
    derivative = _finite(proper_time_derivative_map, 'proper_time_derivative_map')
    hamiltonian = _finite(spatial_mass_hamiltonian_map, 'spatial_mass_hamiltonian_map')
    connection = _finite(factor_temporal_connection_map, 'factor_temporal_connection_map')
    if (derivative.shape != hamiltonian.shape or derivative.ndim != 3
            or connection.shape != derivative.shape or derivative.shape[1] != 18
            or not len(derivative) or not derivative.shape[2]):
        raise ValueError('matching (points,18,coefficients) time and Hamiltonian maps required')
    return dict(factor_map=derivative+connection+hamiltonian,
        factor_covariant_time_derivative_map=derivative+connection,
        inherited_factor_owner=FACTOR_OWNER,
        derivation='massless round W=diag(-Dhat,+Dhat)/R4; append Hermitian SPATIAL gauge and fixed-YH vertices, with explicitly bound factor temporal covariant derivative',
        Lorentz_temporal_Hamiltonian_automatically_used_as_factor_connection=False,
        factor_temporal_connection_and_native_domain_certified=False,
        physical_time_equals_heat_parameter=False,
        complete_native_operator_domain_closed=False,
        heat_invocation_permitted=False)


def canonical_product_factor_contract():
    """Derive the positive graph relation from the retained scalar factor.

    The matrix W extension uses the canonical Hermitian local Hamiltonian,
    including its owned vertices.  This derivation fixes the formal bulk
    factor and conormal; it does not certify that its whole stratified
    realization has been attached to the current trial maps.
    """
    return dict(
        equations=dict(
            Lorentz_evolution='i partial_tau chi=H_can chi',
            Lorentz_covariant_evolution='i(partial_tau+Omega_tau_L)chi=W_spatial_mass chi; H_can=W_spatial_mass-i Omega_tau_L',
            positive_factor='A=D_tau_factor+W_spatial_mass; D_tau_factor=partial_tau+Omega_tau_factor',
            formal_adjoint='A_dagger=-D_tau_factor+W_spatial_mass on d_tau*dOmega for anti-Hermitian Omega_tau_factor',
            positive_bulk='A_dagger A=-D_tau_factor^2-[D_tau_factor,W_spatial_mass]+W_spatial_mass^2',
            conormal='v=A u=D_tau_factor u+W_spatial_mass u',
            graph='D_tau_factor (u,v)^T=[[-W,I],[-z I,W]] (u,v)^T',
            temporal_gauge_covariance="Omega_factor'=U Omega_factor U_dagger-Udot U_dagger; W'=U W U_dagger; A'=U A U_dagger",
            failed_naive_Lorentz_factor='partial_tau+H_can gains (1+i)Udot U_dagger relative to U A U_dagger and is not gauge covariant',
            scalar_owner_reduction='W=epsilon_b sigma (n+3/2)/R4; exact retained product-Dirac graph',
            boundary_pairing='int (A u)^dagger A v=int u^dagger A_dagger A v+[u^dagger A v]_endpoints',
            gauge_orbit_mass='M(i theta Q_H H)=i theta [Q,M(H)]',
            source_contact='P_vJ=A_v^dagger A_J+A_J^dagger A_v+A^dagger A_vJ+A_vJ^dagger A',
            heat_mixed='Gamma_vJ=STr(Q_c(P) P_vJ+DQ_c(P)[P_J] P_v); Q_c(P)=exp(-c P)/(2 P)',
        ),
        positive_pairing='After chi=R4^(3/2)psi: d_tau*dOmega and current Gram I18',
        component_factor_owner=FACTOR_OWNER, native_owner=NATIVE_OWNER,
        complete_domain_requirements=(
            'same-owner initial/past, reset, child-return and exterior graph on these trials',
            'canonical-stop Friedrichs realization and paired boundary contacts',
            'zero-mode/BRST quotient, statistics supertrace and relative zeta/eta completion',
            'moving pairing/domain/source jets and native c=i/r jets',
        ),
        scalar_owner_reduction_is_full_interacting_domain_certificate=False,
        factor_temporal_native_binding=None,
        Lorentz_to_native_analytic_continuation_automatically_asserted=False,
        heat_invocation_permitted=False,
        uniform_cutoff_or_Pauli_remainder_bound_established=False,
    )


def product_factor_form_jets(*, value_map, factor_map, factor_v, factor_J,
        factor_vJ, proper_time_unnormalized_Haar_weights):
    """Positive factor form and complete source-square contacts on ONE core.

    Weights are d tau*dOmega after chi's density isometry; 2pi^2 belongs in
    them once.  A_vJ is mandatory, including a proved zero for an affine
    fixed-field path.  A†A is formed from A, never from the Lorentz Euler.
    Moving pairing, reset, domain and exterior-return jets are additional
    same-owner applications; this fixed-core operation does not delete them.
    """
    values = _finite(value_map, 'value_map')
    maps = [_finite(x, name) for x, name in (
        (factor_map, 'factor_map'), (factor_v, 'factor_v'),
        (factor_J, 'factor_J'), (factor_vJ, 'factor_vJ'))]
    if (values.ndim != 3 or values.shape[1] != 18 or not len(values)
            or not values.shape[2] or any(x.shape != values.shape for x in maps)):
        raise ValueError('all maps require the same (points,18,coefficients) shape')
    w = _finite(proper_time_unnormalized_Haar_weights, 'proper_time_unnormalized_Haar_weights')
    if w.shape != (len(values),) or np.any(w.imag != 0) or np.any(w.real <= 0):
        raise ValueError('one positive proper-time times unnormalized-Haar weight per point required')
    def pair(a, b):
        return np.einsum('p,pik,pil->kl', w.real, a.conj(), b)
    a, av, aj, avj = maps
    contact = pair(av, aj)+pair(aj, av)
    genuine_mixed = pair(a, avj)+pair(avj, a)
    return dict(M=pair(values, values), K=pair(a, a),
        K_v=pair(av, a)+pair(a, av), K_J=pair(aj, a)+pair(a, aj),
        K_vJ=contact+genuine_mixed, source_square_contact=contact,
        genuine_mixed_first_order_term=genuine_mixed,
        inherited_factor_owner=FACTOR_OWNER, native_owner=NATIVE_OWNER,
        fixed_core_positive_pairing=True,
        Gram_is_statistics_grading=False,
        zero_mode_BRST_quotient_applied=False,
        moving_pairing_domain_and_exterior_jets_included=False,
        complete_native_operator_domain_closed=False,
        heat_invocation_permitted=False)


def retained_e1_source_vertices(electromagnetic_coupling, repository=None):
    """Evaluated E1 photon vertices and fixed-Y Higgs vertex basis.

    Unit one-forms and the four real Higgs coordinate directions describe
    operator coefficients; they are not selected physical source modes or
    a scalar background.  The photon contact is the actual source-square
    coefficient of the canonical Hamiltonian.  Its SPATIAL entries also
    belong to the product factor; the temporal native vertex requires its
    separate covariant-connection binding and is not identified here.
    """
    geom = retained_e1_hamiltonian_coefficients(repository)
    values = np.eye(18, dtype=complex)[None]
    photon = []
    for a in range(4):
        one_form = np.eye(4)[a:a+1]
        photon.append(electromagnetic_hamiltonian_source_maps(
            value_map=values, R4=geom['R4'], photon_one_form=one_form,
            electromagnetic_coupling=electromagnetic_coupling,
            delta_H=np.zeros((1, 2), complex))['source_operator'][0])
    photon = np.asarray(photon)
    higgs_directions = np.array([[1, 0], [1j, 0], [0, 1], [0, 1j]], complex)
    mass = fixed_y_higgs_hamiltonian(higgs_directions)
    contact = np.array([[a.conj().T@b+b.conj().T@a for b in photon]
                        for a in photon])
    return dict(geometry=geom, photon_vertices=photon,
        photon_source_square_contacts=contact, fixed_Y_real_Higgs_vertices=mass,
        contact_kind='CANONICAL_HAMILTONIAN_SOURCE_SQUARE; SPATIAL_COMPONENT_REUSABLE_FOR_PRODUCT_FACTOR',
        native_factor_temporal_photon_vertex=None,
        photon_frame='proper-tau, unit-S3 right coframe theta1,theta2,theta3',
        Higgs_coordinate_order='Re H1, Im H1, Re H2, Im H2',
        fixed_H_photon_partial_derivative=True,
        zero_delta_H_is_fixed_field_derivative_not_stationary_H_zero=True,
        full_physical_photon_lift_or_heat_weighting_evaluated=False)


def retained_e1_hamiltonian_coefficients(repository=None):
    """Actual E1+ principal/spin coefficients; H and gauge are still unknowns.

    This does not insert H=0, a gauge zero, or a chosen scalar profile.
    The principal and spin data are reusable by the coupled producer.
    """
    geom = (retained_e1_lepton_geometry_coefficients() if repository is None
            else retained_e1_lepton_geometry_coefficients(repository))
    rep = lepton_current_hilbert_representation()
    r = geom['R4']
    return dict(N=geom['N'], R4=r,
        H4=geom['operator']['H4'], geometry_source=geom['geometry_source'],
        spatial_principal=-1j*rep['alpha']/r,
        contracted_round_spin=1.5*rep['gamma5']/r,
        positive_current_Gram=rep['Gram'], EM_charge=rep['EM_charge'],
        fixed_Y=rep['family_Y'], frame_order=FRAME_ORDER,
        Higgs_and_gauge_are_coupled_unknowns=True,
        temporal_spin_after_density_rescale='exactly absent; not an H4=0 approximation',
        native_heat_evaluated=False, complete_native=False)
