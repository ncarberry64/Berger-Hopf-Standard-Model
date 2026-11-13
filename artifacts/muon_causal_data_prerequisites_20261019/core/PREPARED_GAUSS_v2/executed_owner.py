"""Adopted charge moments in the original gauge-covariant weak Gauss law.

This evaluates a necessary dressing contraction, not a local packet or a
selected incoming characteristic state.  The physical centroids are imposed
preparation targets.  The independent Gaussian second moment belongs to the
declared reference envelopes until a dressed packet calculation checks it.
All boundary, inherited-state and other-source terms remain in the law.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
import numpy as np
from numpy.polynomial.hermite import hermgauss

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
from .muon_primal_electromagnetic_source import higgs_aligned_charge


BENCHMARK = 'BHSM_NEW_COLLIDER_ELECTRON_POSITRON_TO_MUON_ANTIMUON_V1'
GAUSS_LAW = (
    'Flux[lambda]-Bulk[D_i lambda]+J_other[lambda]+J_pair[lambda]=0; '
    'K[lambda]:=Bulk[D_i lambda]-Flux[lambda]-J_other[lambda]=J_pair[lambda]'
)


def _finite_real(value, shape, name):
    raw = np.asarray(value)
    if raw.shape != shape or not np.isrealobj(raw) or not np.isfinite(raw).all():
        raise ValueError('finite real '+name+' with shape '+str(shape)+' required')
    return raw.astype(float)


def _annihilators4():
    # Same bit order as the retained exact preparation; no continuum state
    # or independent gauge CCR representation is selected by this algebra.
    operators = np.zeros((4, 16, 16), complex)
    for mode in range(4):
        for state in range(16):
            if state & (1 << mode):
                operators[mode, state ^ (1 << mode), state] = (
                    -1 if (state & ((1 << mode)-1)).bit_count() % 2 else 1)
    return operators


def prepared_charge_moments(preparation, pair_density):
    """Execute exact pair counts and the adopted physical centroid target.

    Hermite integration evaluates only the specified independent scalar
    reference NUMBER-POSITION probability envelope. Its spatial complement
    defect is retained. This is not the variance of a full relativistic
    local charge: anomalous U-dagger Q X3 V, continuum/complement and matched
    reference contractions have not been evaluated. Spectral/dressing
    preservation of the scalar distribution is also not established.
    """
    if preparation.get('extends_benchmark') != BENCHMARK:
        raise ValueError('the unchanged adopted collider preparation is required')
    frame, packets = preparation['frame_and_geometry'], preparation['packets']
    spin = preparation['spin_state']
    if not spin['exact_pair_statistics_required'] or spin['quasifree_replacement_from_one_body_covariance_allowed']:
        raise ValueError('exact prepared pair statistics must remain explicit')
    density = np.asarray(pair_density, complex)
    if density.shape != (16, 16) or not np.isfinite(density).all():
        raise ValueError('retained exact pair density16 required')
    exact = np.zeros((16, 16), complex)
    for s in range(2):
        for t in range(2):
            index = (1 << s) | (1 << (2+t))
            exact[index, index] = .25
    if not np.array_equal(density, exact):
        raise ValueError('do not replace the exact one-electron/one-positron mixture')
    operators = _annihilators4()
    number = np.array([a.conj().T@a for a in operators])
    ne, np_ = number[0]+number[1], number[2]+number[3]
    mean = lambda a: np.trace(density@a).real
    pair_counts = np.array([mean(ne), mean(np_), mean(ne@ne), mean(np_@np_), mean(ne@np_)])
    centers = frame['initial_packet_centers_fm']
    ze, zp = float(centers['electron'][2]), float(centers['positron'][2])
    sigma = float(packets['reference_probability_rms_width_each_axis_fm'][2])
    dipole = -ze*ne+zp*np_
    q = -ne+np_
    dipole_mean = float(mean(dipole))
    compressed_second = float(mean(dipole@dipole))
    # Tensor-product species coefficients before required field dressing are
    # explicit in the authoritative preparation.  No independence of the
    # subsequent interacting/dressed physical state is inferred.
    declared_product = 'factor before required field dressing' in packets['coherence']
    if not declared_product or packets['envelope'] != 'isotropic Gaussian coherent packet for each incoming species':
        raise ValueError('the reference Gaussian product assumption was not declared')
    nodes, weights = hermgauss(3)
    positions_e, positions_p = ze+np.sqrt(2)*sigma*nodes, zp+np.sqrt(2)*sigma*nodes
    product_weights = weights[:, None]*weights[None, :]/np.pi
    relative = -positions_e[:, None]+positions_p[None, :]
    gaussian_mean = float(np.sum(product_weights*relative))
    gaussian_second = float(np.sum(product_weights*relative**2))
    reference_variance = 2*sigma*sigma
    reference_second = dipole_mean*dipole_mean+reference_variance
    # Parse h,c,e from the adopted independent unit constants.  This is a
    # conversion, not the missing physical G_F scale equation.
    with localcontext() as context:
        context.prec = 65
        constants = preparation['calibration_and_units']
        h = Decimal(constants['h_J_s']['value'])
        c = Decimal(constants['c_m_per_s']['value'])
        electric = Decimal(constants['e_C']['value'])
        # Decimal pi is explicit solely for the exact h/(2*pi) conversion.
        pi = Decimal('3.1415926535897932384626433832795028841971693993751058209749445923078')
        hbar_c_GeV_fm = h*c/(2*pi*electric)*Decimal(10)**6
    return dict(pair_density16=density.copy(), particle_number_operators=np.array([ne, np_]),
        pair_number_moments=pair_counts, charge_operator16=q,
        compressed_dipole_operator_fm16=dipole,
        required_physical_charge_mean=float(mean(q)),
        required_physical_dipole_mean_fm=dipole_mean,
        exact_pair_charge_variance=float(mean(q@q)-mean(q)**2),
        reference_envelope_variance_fm_squared=reference_variance,
        reference_envelope_second_moment_fm_squared=reference_second,
        compressed_dipole_second_moment_fm_squared=compressed_second,
        spatial_compression_defect_fm_squared=reference_second-compressed_second,
        Gaussian_quadrature_mean_fm=gaussian_mean,
        Gaussian_quadrature_second_moment_fm_squared=gaussian_second,
        Gaussian_mean_identity_error=abs(gaussian_mean-dipole_mean),
        Gaussian_second_identity_error=abs(gaussian_second-reference_second),
        hbar_c_GeV_fm_decimal=str(hbar_c_GeV_fm),
        hbar_c_GeV_fm=float(hbar_c_GeV_fm),
        achieved_physical_sections_or_moments=None,
        achieved_J_pair_lambda1=None,
        required_dipole_kind='mandatory adopted physical centroid/source target; not an achieved packet moment',
        reference_second_moment_kind='independent scalar reference number-position operator only',
        physical_local_charge_variance=None,
        reference_second_moment_is_a_dressed_physical_result=False)


def _collect(jets):
    return dict(value=np.array([a.value for a in jets]),
        gradient=np.array([a.gradient for a in jets]),
        hessian=np.array([a.hessian for a in jets]))


def charge_test_twojet(theta, gradient, hessian):
    """s(H), [A_i,s]/R and all same151 coefficient derivatives.

    For lambda=X3*s(H),
      D_i lambda=(e_i X3)*s+X3*(E_i s+[A_i,s])/R.
    E_i s=0 only on this saved homogeneous angular comparison component.
    The physical collider coordinate/normal extension is not assigned.
    """
    t = _finite_real(theta, (22,), 'same comparison theta22')
    g = _finite_real(gradient, (22, 151), 'theta gradient')
    h = _finite_real(hessian, (22, 151, 151), 'theta Hessian')
    if min(t[:2]) <= 0 or np.sum(t[18:]**2) <= 0:
        raise ValueError('positive actual radius/lapse and nonzero actual H required')
    jets = [Jet(a, b, c) for a, b, c in zip(t, g, h)]
    a, b, c, d = jets[18:22]
    norm = a*a+b*b+c*c+d*d
    bloch = [2*(a*b+c*d)/norm, 2*(a*d-b*c)/norm,
             (a*a+c*c-b*b-d*d)/norm]
    s = [-np.sqrt(2)*v for v in bloch]+[Jet.constant(np.sqrt(10/3), 151)]
    gauge = [jets[2:6]]+[jets[6+4*i:10+4*i] for i in range(3)]
    def bracket(left, right):
        return [(left[1]*right[2]-left[2]*right[1])/np.sqrt(2),
                (left[2]*right[0]-left[0]*right[2])/np.sqrt(2),
                (left[0]*right[1]-left[1]*right[0])/np.sqrt(2),
                Jet.constant(0., 151)]
    spatial = [v/jets[0] for field in gauge[1:] for v in bracket(field, s)]
    temporal = [v/jets[1] for v in bracket(gauge[0], s)]
    alignment = higgs_aligned_charge(t[18:20]+1j*t[20:22], np.zeros(2, complex))
    G = lepton_unit_trace_gauge_representation()['generators']
    sv = np.array([z.value for z in s])
    Q = np.einsum('c,cij->ij', sv, 1j*G)
    # The material At action cotangent is -N*dH/dAt=iG.  Retain the
    # induced physical lapse; substituting ambient lapse is not permitted.
    hamiltonian_At_vertex = -1j*G/t[1]
    action_At_vertex = -t[1]*hamiltonian_At_vertex
    mass = fixed_y_higgs_hamiltonian((t[18:20]+1j*t[20:22])[None])[0]
    return dict(charge_test=_collect(s),
        proper_spatial_covariant_charge_derivative=_collect(spatial),
        proper_stationary_temporal_covariant_charge_derivative=_collect(temporal),
        physical_charge18=Q,original_At_action_vertices=action_At_vertex,
        charge_reconstruction_error=float(np.max(abs(Q-alignment['charge']))),
        At_lapse_cancellation_error=float(np.max(abs(action_At_vertex-1j*G))),
        charge_mass_commutator_error=float(np.max(abs(Q@mass-mass@Q))),
        charge_spectrum=np.linalg.eigvalsh(Q),
        spatial_covariant_derivative_nonzero=bool(np.max(np.abs([z.value for z in spatial]))>0),
        angular_H_derivative_zero_scope='saved constant-angular comparison only',
        original_Gauss_sign=GAUSS_LAW,
        ambient_lapse_substituted=False,extra_e_or_family_multiplicity_inserted=False,
        physical_collider_coordinate_or_dressing_selected=False)


def physical_unit_moment_twojet(moments, log_energy_unit):
    """Provisional chart values, with exact e-derivatives and physical e free.

    L_chart=L_fm*exp(e)/(hbar*c in GeV fm).  This evaluates at the pinned
    initializer only.  It neither solves nor changes G_F exp(2e)=c_F.
    """
    e = float(log_energy_unit)
    if not np.isfinite(e):
        raise ValueError('finite pinned log-unit initializer required')
    ej = Jet.affine(e, np.eye(151)[150])
    conversion = ej.exp()/moments['hbar_c_GeV_fm']
    dipole = moments['required_physical_dipole_mean_fm']*conversion
    variance = moments['reference_envelope_variance_fm_squared']*conversion**2
    second = moments['reference_envelope_second_moment_fm_squared']*conversion**2
    return dict(required_dipole_chart=_collect([dipole]),
        reference_variance_chart=_collect([variance]),
        reference_second_moment_chart=_collect([second]),
        scale_is_initializer_only=True,physical_scale_equation_solved=False,
        exact_total_derivative='D d=d D e; D2 d=d[(D e)^2+D2 e]; D v=2v D e; D2 v=v[4(D e)^2+2D2 e]')


def required_dressing_contractions(moments):
    """Consume the moment in the actual Gauss relation, leaving its summands.

    K_1 has one mandatory target from the preparation. Its achieved value
    is not allocated among unknown terms or inferred from a classical
    residual. The operator identities require a frozen-background real
    test, a common self-adjoint domain and the operator Gauss constraint.
    Their physical variance operand is not the scalar number-position
    envelope variance: local anomalous/reference terms remain explicit.
    """
    d = moments['required_physical_dipole_mean_fm']
    v = moments['reference_envelope_variance_fm_squared']
    return dict(equation=GAUSS_LAW,
        test0='lambda_0=s(H)', test1='lambda_1=X3*s(H)',
        required_K0=moments['required_physical_charge_mean'], required_K1_fm=d,
        algebraic_target_substitution_Gauss_row_fm=-d+d,
        target_kind='required adopted source moment; physical evaluation not performed',
        achieved_J_pair_lambda1=None, achieved_K1=None,
        flux_covariant_bulk_other_source_summands='individually unevaluated, none assigned zero',
        conditional_operator_identity='For fixed real test and common self-adjoint F,D: (F+D)Psi=0, F=Flux-Bulk+J_other => <F>=-<D>, Var(F)=Var(D), Cov_sym(F,D)=-Var(D)',
        physical_Var_D=None, physical_Var_F=None, physical_Cov_FD=None,
        reference_number_position_variance_fm_squared=v,
        full_charge_variance_missing='anomalous U-dagger Q X3 V, spatial complement, matched inherited-state and other connected contractions',
        quantum_H_inside_test_ordering_constructed=False,
        quantum_dressing_or_reference_correlation_evaluated=False,
        achieved_complete_Gauss_residual=None,
        local_parent_incoming40_or_packet_selected=False,
        physical_admission=False,physical_guard=2e-10)
