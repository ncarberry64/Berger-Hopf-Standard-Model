"""Algebraic variation checks; manufactured arrays are never physical primals."""
import numpy as np
import pytest

from bhsm.interface.muon_intrinsic_higgs_weak_action import (
    complexify_doublet, diagonal_kinetic_density, gauge_covariant_variation,
    higgs_action, higgs_boundary_pairing, higgs_boundary_variation,
    higgs_conormal_flux, higgs_explicit_weak_variation,
    higgs_fixed_field_action_two_jet,
    higgs_hessian_application, higgs_metric_action_variation,
    higgs_potential_hessian_application, higgs_potential_real_hessian,
    higgs_supplied_constraint_variation, higgs_weak_residual,
    intrinsic_m4_weight_variation, intrinsic_m4_weights,
    lepton_higgs_source, lepton_higgs_source_variation,
    realified_higgs_weak_jacobian, realify_doublet,
    retained_e1_intrinsic_coefficients,
    retained_higgs_spin_charge_representation,
)


def algebraic_data():
    """Nonstationary complex data for differentiating identities only."""
    rng = np.random.default_rng(201031)
    points = 5
    complex_array = lambda shape: rng.normal(size=shape)+1j*rng.normal(size=shape)
    weights = intrinsic_m4_weights(np.linspace(.7, 1.1, points),
                                  np.linspace(.8, 1.4, points))
    return dict(quadrature=np.linspace(.03, .12, points),
                kinetic_density=diagonal_kinetic_density(weights),
                volume_density=weights['potential'],
                H=.3*complex_array((points, 2)), DH=.2*complex_array((points, 4, 2)),
                J=.15*complex_array((points, 2)), phi=complex_array((points, 2)),
                Dphi=complex_array((points, 4, 2)), lambda_H=.73, nu_squared=.21)


def action_data(data):
    return {key:value for key, value in data.items() if key not in ('phi', 'Dphi')}


def finite_difference(function, epsilon=2e-6):
    return (function(epsilon)-function(-epsilon))/(2*epsilon)


def test_real_chart_is_unscaled_and_real_linear_potential_is_not_complex_linear():
    data = algebraic_data()
    H, h = data['H'], data['phi']
    assert np.array_equal(complexify_doublet(realify_doublet(H)), H)
    kwargs = dict(lambda_H=data['lambda_H'], nu_squared=data['nu_squared'])
    result = higgs_potential_hessian_application(H, h, **kwargs)
    matrix = higgs_potential_real_hessian(H, **kwargs)
    np.testing.assert_allclose(realify_doublet(result),
                               np.einsum('pij,pj->pi', matrix, realify_doublet(h)))
    imaginary = higgs_potential_hessian_application(H, 1j*h, **kwargs)
    assert np.linalg.norm(imaginary-1j*result) > .1


def test_literal_action_derivative_matches_real_weak_residual():
    data = algebraic_data()
    action = action_data(data)
    derivative = finite_difference(lambda t:higgs_action(
        **dict(action, H=data['H']+t*data['phi'], DH=data['DH']+t*data['Dphi'])))
    assert derivative == pytest.approx(higgs_weak_residual(**data), abs=2e-9)


def test_higgs_jacobian_matches_nonlinear_residual_derivative():
    data = algebraic_data()
    h, Dh = .31j*data['phi']+.13*data['H'], -.27j*data['Dphi']
    derivative = finite_difference(lambda t:higgs_weak_residual(
        **dict(data, H=data['H']+t*h, DH=data['DH']+t*Dh)))
    expected = higgs_hessian_application(
        **{key:value for key, value in data.items() if key not in ('DH', 'J')},
        h=h, Dh=Dh)
    assert derivative == pytest.approx(expected, abs=2e-9)


def test_realified_basis_assembly_preserves_symmetry_and_imaginary_directions():
    data = algebraic_data()
    values = np.stack((data['phi'], 1j*data['phi'], data['H']))
    derivatives = np.stack((data['Dphi'], 1j*data['Dphi'], data['DH']))
    matrix = realified_higgs_weak_jacobian(
        **{key:value for key, value in data.items() if key not in ('DH', 'J', 'phi', 'Dphi')},
        test_values=values, test_derivatives=derivatives,
        trial_values=values, trial_derivatives=derivatives)
    np.testing.assert_allclose(matrix, matrix.T, atol=1e-14)
    assert abs(matrix[0, 0]-matrix[1, 1]) > .01


def test_full_explicit_source_retains_measure_frame_source_and_test_transport():
    data = algebraic_data()
    dG = .18*data['kinetic_density']
    dw = -.23*data['volume_density']
    dH, dDH = .12j*data['H'], -.09*data['DH']
    dphi, dDphi = .16*data['phi'], .11j*data['Dphi']
    dJ = .41j*data['J']
    result = higgs_explicit_weak_variation(
        **data, delta_kinetic_density=dG, delta_volume_density=dw, delta_J=dJ,
        delta_DH=dDH, delta_Dphi=dDphi, kinematic_H_lift=dH, test_lift=dphi)
    derivative = finite_difference(lambda t:higgs_weak_residual(**dict(
        data, kinetic_density=data['kinetic_density']+t*dG,
        volume_density=data['volume_density']+t*dw, H=data['H']+t*dH,
        DH=data['DH']+t*dDH, phi=data['phi']+t*dphi,
        Dphi=data['Dphi']+t*dDphi, J=data['J']+t*dJ)))
    assert result == pytest.approx(derivative, abs=2e-9)


def test_induced_field_response_is_hh_and_is_separate_from_partial_source():
    data = algebraic_data()
    h, Dh = .18*data['phi'], -.21j*data['Dphi']
    field_block = higgs_explicit_weak_variation(
        **data, kinematic_H_lift=h, delta_DH=Dh)
    expected = higgs_hessian_application(
        **{key:value for key, value in data.items() if key not in ('DH', 'J')}, h=h, Dh=Dh)
    assert field_block == pytest.approx(expected)
    # At fixed supplied fields no induced response is inserted implicitly.
    assert higgs_explicit_weak_variation(**data) == 0


def test_gauge_cross_application_varies_derivatives_of_field_and_test():
    data = algebraic_data()
    A = np.zeros((5, 4, 2, 2), dtype=complex)
    A[..., 0, 0], A[..., 1, 1] = .17j, -.08j
    A[..., 0, 1], A[..., 1, 0] = .12+.21j, -.12+.21j
    dDH, dDphi = gauge_covariant_variation(A, data['H'], data['phi'])
    result = higgs_explicit_weak_variation(**data, delta_DH=dDH, delta_Dphi=dDphi)
    derivative = finite_difference(lambda t:higgs_weak_residual(
        **dict(data, DH=data['DH']+t*dDH, Dphi=data['Dphi']+t*dDphi)))
    assert result == pytest.approx(derivative, abs=2e-9)
    only_field = higgs_explicit_weak_variation(**data, delta_DH=dDH)
    assert abs(result-only_field) > .01


def test_metric_action_cotangent_and_higgs_cross_block_are_same_action_mixed_derivatives():
    data = algebraic_data()
    dG, dw, dJ = .13*data['kinetic_density'], -.29*data['volume_density'], .32j*data['J']
    kwargs = dict(delta_kinetic_density=dG, delta_volume_density=dw, delta_J=dJ)
    result = higgs_explicit_weak_variation(**data, **kwargs)
    derivative = finite_difference(lambda t:higgs_metric_action_variation(
        **dict(action_data(data), H=data['H']+t*data['phi'],
               DH=data['DH']+t*data['Dphi']), **kwargs))
    assert result == pytest.approx(derivative, abs=2e-9)
    direct = higgs_metric_action_variation(**action_data(data), **kwargs)
    action_derivative = finite_difference(lambda t:higgs_action(**dict(
        action_data(data), kinetic_density=data['kinetic_density']+t*dG,
        volume_density=data['volume_density']+t*dw, J=data['J']+t*dJ)))
    assert direct == pytest.approx(action_derivative, abs=2e-9)


def test_independent_reference_domain_motion_is_kept_once_in_action_and_weak_source():
    data = algebraic_data()
    dquad = -.17*data['quadrature']
    dG, dw = .07*data['kinetic_density'], -.03*data['volume_density']
    kwargs = dict(delta_kinetic_density=dG, delta_volume_density=dw,
                  delta_quadrature=dquad)
    weak = higgs_explicit_weak_variation(**data, **kwargs)
    derivative = finite_difference(lambda t:higgs_weak_residual(**dict(
        data, quadrature=data['quadrature']+t*dquad,
        kinetic_density=data['kinetic_density']+t*dG,
        volume_density=data['volume_density']+t*dw)))
    assert weak == pytest.approx(derivative, abs=2e-9)
    action = higgs_metric_action_variation(**action_data(data), **kwargs)
    derivative = finite_difference(lambda t:higgs_action(**dict(
        action_data(data), quadrature=data['quadrature']+t*dquad,
        kinetic_density=data['kinetic_density']+t*dG,
        volume_density=data['volume_density']+t*dw)))
    assert action == pytest.approx(derivative, abs=2e-9)
    # Same domain Jacobian may instead be assigned to the density tensors.
    fraction = dquad/data['quadrature']
    density_only = higgs_explicit_weak_variation(
        **data, delta_kinetic_density=dG+fraction[:, None, None]*data['kinetic_density'],
        delta_volume_density=dw+fraction*data['volume_density'])
    assert density_only == pytest.approx(weak, abs=1e-14)


def test_lapse_metric_weights_have_owned_independent_derivative_signs():
    N, R, n, r = .7, 1.2, .11, -.23
    result = intrinsic_m4_weight_variation(N, R, delta_log_N=n, delta_log_R4=r)
    for name, value in result.items():
        derivative = finite_difference(lambda t:intrinsic_m4_weights(
            N*np.exp(t*n), R*np.exp(t*r))[name])
        assert value == pytest.approx(derivative, abs=1e-9)
    # The lapse reaction at fixed fields is not a duplicate ADM multiplier row.
    lapse = intrinsic_m4_weight_variation(N, R, delta_log_N=1, delta_log_R4=0)
    assert lapse['time'] < 0 < lapse['spatial']
    assert lapse['potential'] > 0


def test_actual_e1_intrinsic_coefficients_and_normal_weak_check():
    actual = retained_e1_intrinsic_coefficients()
    assert actual['C'] == pytest.approx(1.9180902180140678, abs=2e-15)
    a = actual['normal_first_log_R4_per_unit_amplitude']
    assert a == pytest.approx(.006903452433182276, abs=2e-15)
    assert actual['scalar_primal_evaluated'] is False
    assert actual['stationary_base_established'] is False
    assert actual['source']['branch'] == 24
    data = algebraic_data()
    # Manufactured algebraic inputs check the actual metric coefficients only.
    weights = actual['weights']
    data['kinetic_density'] = diagonal_kinetic_density(weights)
    data['volume_density'] = weights['potential']
    delta = actual['normal_first_weights']
    result = higgs_explicit_weak_variation(
        **data, delta_kinetic_density=diagonal_kinetic_density(delta),
        delta_volume_density=delta['potential'])
    F = (2*data['lambda_H']*(np.sum(np.abs(data['H'])**2, axis=1)
                            -data['nu_squared'])[:, None]*data['H']+data['J'])
    temporal = np.sum(data['Dphi'][:, 0].conj()*data['DH'][:, 0], axis=1)
    spatial = np.sum(data['Dphi'][:, 1:].conj()*data['DH'][:, 1:], axis=(1, 2))
    force = np.sum(data['phi'].conj()*F, axis=1)
    expected = 2*np.real(np.sum(data['quadrature']*a*(
        3*weights['time']*temporal-weights['spatial']*spatial
        -3*weights['potential']*force)))
    assert result == pytest.approx(expected, abs=1e-14)
    omitted_off_shell_measure = 2*np.real(np.sum(data['quadrature']*a*(
        3*weights['time']*temporal-weights['spatial']*spatial)))
    assert abs(result-omitted_off_shell_measure) > 1e-3
    coefficient = actual['polynomial_coefficient_map']
    assert coefficient['quartic_factor_times_lambda_H'] == -weights['potential']
    assert np.shape(coefficient['family_yukawa']) == (3, 3)


def test_actual_dense_metric_normal_first_jet_matches_intrinsic_weight_formula():
    from bhsm.interface.muon_birth_candidate_geometry_action import (
        evaluate_retained_candidate_geometry,
    )
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import metric_normal_two_jet
    geometry = evaluate_retained_candidate_geometry()['geometry']
    jet = metric_normal_two_jet(geometry, normal_value=1,
                               normal_coordinate_time_derivative=.17,
                               normal_unit_s3_gradient=(.3, -.2, .1))
    actual = retained_e1_intrinsic_coefficients()
    np.testing.assert_allclose(jet['kinetic_density'],
                               diagonal_kinetic_density(actual['weights']), atol=1e-15)
    np.testing.assert_allclose(jet['kinetic_density_first'],
                               diagonal_kinetic_density(actual['normal_first_weights']), atol=1e-15)
    assert jet['volume_density_first'] == pytest.approx(actual['normal_first_weights']['potential'])
    assert np.linalg.norm(jet['kinetic_density_second'][0, 1:]) > .01
    data = algebraic_data()
    data['kinetic_density'] = jet['kinetic_density']
    data['volume_density'] = jet['volume_density']
    supplied = higgs_fixed_field_action_two_jet(
        **action_data(data), kinetic_density_first=jet['kinetic_density_first'],
        kinetic_density_second=jet['kinetic_density_second'],
        volume_density_first=jet['volume_density_first'],
        volume_density_second=jet['volume_density_second'])
    expected = higgs_metric_action_variation(
        **action_data(data), delta_kinetic_density=jet['kinetic_density_first'],
        delta_volume_density=jet['volume_density_first'])
    assert supplied['first'] == pytest.approx(expected)
    # Off-diagonal graph contacts are consumed by the action, not discarded.
    diagonal_second = np.diag(np.diag(jet['kinetic_density_second']))
    only_diagonal = higgs_fixed_field_action_two_jet(
        **action_data(data), kinetic_density_first=jet['kinetic_density_first'],
        kinetic_density_second=diagonal_second,
        volume_density_first=jet['volume_density_first'],
        volume_density_second=jet['volume_density_second'])
    assert abs(supplied['second']-only_diagonal['second']) > .001


def test_fixed_field_second_action_jet_retains_all_explicit_product_contacts():
    data = algebraic_data()
    G1, G2 = .13*data['kinetic_density'], -.19*data['kinetic_density']
    w1, w2 = -.23*data['volume_density'], .17*data['volume_density']
    D1, D2 = .31j*data['DH'], -.12*data['DH']
    J1, J2 = .27*data['J'], .14j*data['J']
    q1, q2 = -.09*data['quadrature'], .08*data['quadrature']
    jet = higgs_fixed_field_action_two_jet(
        **action_data(data), kinetic_density_first=G1, kinetic_density_second=G2,
        volume_density_first=w1, volume_density_second=w2,
        DH_first=D1, DH_second=D2, J_first=J1, J_second=J2,
        quadrature_first=q1, quadrature_second=q2)
    action = lambda t:higgs_action(**dict(
        action_data(data), kinetic_density=data['kinetic_density']+t*G1+t*t*G2/2,
        volume_density=data['volume_density']+t*w1+t*t*w2/2,
        DH=data['DH']+t*D1+t*t*D2/2, J=data['J']+t*J1+t*t*J2/2,
        quadrature=data['quadrature']+t*q1+t*t*q2/2))
    assert jet['value'] == pytest.approx(action(0))
    assert jet['first'] == pytest.approx(finite_difference(action), abs=2e-9)
    step = 3e-4
    second = (action(step)-2*action(0)+action(-step))/step**2
    assert jet['second'] == pytest.approx(second, abs=2e-7)


def test_lepton_source_has_owned_yukawa_adjoint_and_explicit_spin_frame():
    rng = np.random.default_rng(141)
    values = lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    L, e, Y = values((3, 2, 3, 4)), values((3, 2, 4)), values((3, 2))
    gamma = np.diag([1, 1, -1, -1]).astype(complex)
    source = lepton_higgs_source(L_L=L, e_R=e, Y_l=Y, gamma0=gamma)
    expected = np.empty((3, 2), complex)
    for p in range(3):
        for a in range(2):
            expected[p, a] = sum(
                e[p, f].conj()@gamma@L[p, a, g]*Y[g, f].conjugate()
                for f in range(2) for g in range(3))
    np.testing.assert_allclose(source, expected, atol=2e-14)


def test_lepton_source_matter_and_frame_cross_jet():
    rng = np.random.default_rng(331)
    values = lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    L, e = values((2, 2, 3, 4)), values((2, 3, 4))
    Y, gamma = values((3, 3)), np.diag([1., 1., -1., -1.])
    dL, de = .13j*L, -.17*e
    dgamma = .09*gamma
    result = lepton_higgs_source_variation(
        L_L=L, e_R=e, Y_l=Y, gamma0=gamma,
        delta_L_L=dL, delta_e_R=de, delta_gamma0=dgamma)
    derivative = finite_difference(lambda t:lepton_higgs_source(
        L_L=L+t*dL, e_R=e+t*de, Y_l=Y, gamma0=gamma+t*dgamma))
    np.testing.assert_allclose(result, derivative, atol=1e-8, rtol=1e-8)


def test_retained_charge_and_lr_spin_binder_has_actual_normalization():
    representation = retained_higgs_spin_charge_representation()
    assert representation['higgs_representation'] == 'H=(1,2)_(1/2)'
    assert representation['higgs_hypercharge_exact'] == '1/2'
    np.testing.assert_array_equal(representation['higgs_hypercharge_generator'], np.eye(2)/2)
    generators = representation['higgs_su2_generators']
    for index in range(3):
        np.testing.assert_allclose(generators[index], generators[index].conj().T, atol=0)
        for other in range(3):
            assert np.trace(generators[index]@generators[other]) == pytest.approx(
                .5 if index == other else 0)
    np.testing.assert_allclose(generators[0]@generators[1]-generators[1]@generators[0],
                               1j*generators[2], atol=0)
    gamma = representation['gamma_LR']
    zero, eye = np.zeros((2, 2)), np.eye(2)
    np.testing.assert_allclose(representation['gamma0_LR'],
                               np.block([[zero, eye], [eye, zero]]), atol=3e-16)
    gamma5 = 1j*gamma[0]@gamma[1]@gamma[2]@gamma[3]
    np.testing.assert_allclose(gamma5, np.diag([-1, -1, 1, 1]), atol=1e-15)
    U = representation['Dirac_to_LR_columns']
    np.testing.assert_allclose(U.conj().T@U, np.eye(4), atol=3e-16)
    assert representation['physical_gauge_connection'] is None
    assert representation['physical_matter_fields'] is None
    assert representation['mechanical_connection_identified_with_weak'] is False
    assert representation['physical_scalar_primal_selected'] is False


def test_lepton_source_is_invariant_under_retained_dirac_to_lr_frame_conversion():
    representation = retained_higgs_spin_charge_representation()
    rng = np.random.default_rng(722)
    values = lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    # Realization-independent basis identity; these are not physical matter fields.
    L_weyl, e_weyl = values((2, 2, 3, 2)), values((2, 3, 2))
    L_lr = np.einsum('si,pagi->pags', representation['left_weyl_embedding_LR'], L_weyl)
    e_lr = np.einsum('si,pfi->pfs', representation['right_weyl_embedding_LR'], e_weyl)
    U = representation['Dirac_to_LR_columns']
    L_dirac, e_dirac = (np.einsum('st,pagt->pags', U, L_lr),
                        np.einsum('st,pft->pfs', U, e_lr))
    common = dict(Y_l=representation['family_yukawa'])
    source_lr = lepton_higgs_source(L_L=L_lr, e_R=e_lr,
                                    gamma0=representation['gamma0_LR'], **common)
    source_dirac = lepton_higgs_source(L_L=L_dirac, e_R=e_dirac,
                                       gamma0=representation['gamma_Dirac'][0], **common)
    np.testing.assert_allclose(source_lr, source_dirac, atol=2e-17)
    assert np.linalg.norm(source_lr) > 1e-4


def test_temporal_integration_by_parts_retains_both_outward_contacts():
    # Polynomial identity with explicit test traces; no physical trace selected.
    nodes, quad = np.polynomial.legendre.leggauss(12)
    t, quad = (nodes+1)/2, quad/2
    H, phi = np.zeros((12, 2), complex), np.zeros((12, 2), complex)
    DH, Dphi = np.zeros((12, 4, 2), complex), np.zeros((12, 4, 2), complex)
    H[:, 0], phi[:, 0] = t*t+1j*t, t+1j*t*t
    DH[:, 0, 0], Dphi[:, 0, 0] = 2*t+1j, 1+2j*t
    wt, ws, w0, lam, nu2 = 1.7, .8, 1.2, .4, .2
    G = np.diag([wt, -ws, -ws, -ws])
    data = dict(quadrature=quad, kinetic_density=G, volume_density=w0,
                H=H, DH=DH, J=np.zeros_like(H), phi=phi, Dphi=Dphi,
                lambda_H=lam, nu_squared=nu2)
    weak = higgs_weak_residual(**data)
    q = np.sum(np.abs(H)**2, axis=1)-nu2
    strong = -w0*(2*lam*q[:, None]*H)
    strong[:, 0] -= 2*wt
    bulk = 2*np.real(np.sum(quad*np.sum(phi.conj()*strong, axis=1)))
    endpoints_DH = np.zeros((2, 4, 2), complex)
    endpoints_DH[:, 0, 0] = [1j, 2+1j]
    stokes = np.zeros((2, 4))
    stokes[:, 0] = [-wt, wt]
    endpoint_phi = np.array([[0, 0], [1+1j, 0]], complex)
    flux = higgs_conormal_flux(endpoints_DH, stokes)
    boundary = higgs_boundary_pairing(boundary_quadrature=np.ones(2),
                                      phi=endpoint_phi, flux=flux)
    assert weak == pytest.approx(bulk+boundary, abs=2e-14)


def test_boundary_measure_conormal_and_test_transport_derivative():
    phi = np.array([[1+.2j, .3j], [-.2j, .7]])
    flux = np.array([[.2-.1j, .4], [.3j, -.6]])
    dphi, dflux = .13j*phi, -.21*flux
    quad, dquad = np.array([.2, .7]), np.array([-.03, .09])
    result = higgs_boundary_variation(
        boundary_quadrature=quad, phi=phi, flux=flux,
        delta_flux=dflux, test_lift=dphi, delta_boundary_quadrature=dquad)
    derivative = finite_difference(lambda t:higgs_boundary_pairing(
        boundary_quadrature=quad+t*dquad, phi=phi+t*dphi, flux=flux+t*dflux))
    assert result == pytest.approx(derivative, abs=1e-10)


def test_constraint_multiplier_contact_is_not_discarded_off_shell():
    result = higgs_supplied_constraint_variation(
        constraint_weak_H=[.2, -.1], delta_constraint_weak_H=[.3, .4],
        multiplier=[.7, -.5], multiplier_variation=[.1, -.2])
    assert result == pytest.approx(.05)
    fixed_multiplier_partial = higgs_supplied_constraint_variation(
        constraint_weak_H=[.2, -.1], delta_constraint_weak_H=[.3, .4],
        multiplier=[.7, -.5], multiplier_variation=[0, 0])
    assert fixed_multiplier_partial == pytest.approx(.01)
    separate_multiplier_response = higgs_supplied_constraint_variation(
        constraint_weak_H=[.2, -.1], delta_constraint_weak_H=[0, 0],
        multiplier=[.7, -.5], multiplier_variation=[.1, -.2])
    assert separate_multiplier_response == pytest.approx(.04)


def test_invalid_connections_shapes_and_nonpositive_stiffness_fail_closed():
    data = algebraic_data()
    with pytest.raises(ValueError, match='anti-Hermitian'):
        gauge_covariant_variation(np.ones((5, 4, 2, 2)), data['H'], data['phi'])
    with pytest.raises(ValueError, match='lambda_H'):
        higgs_action(**dict(action_data(data), lambda_H=0))
    with pytest.raises(ValueError, match='symmetric'):
        bad = data['kinetic_density'].copy()
        bad[:, 0, 1] = .1
        higgs_weak_residual(**dict(data, kinetic_density=bad))
    with pytest.raises(ValueError, match='shape'):
        higgs_weak_residual(**dict(data, H=np.ones((5, 3))))
