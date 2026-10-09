"""Coefficient/operator identities; test vectors are iterates, not backgrounds."""
import numpy as np
import pytest

from bhsm.interface.muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from bhsm.interface.muon_intrinsic_lepton_primal import (
    classical_bosonic_body_source, intrinsic_round_dirac_coefficients,
    lepton_fields_from_coefficients, lepton_primal_application,
    lepton_primal_jacobian_application, lepton_weak_euler_rows,
    realify_euler_rows, retained_e1_lepton_geometry_coefficients,
)


def coefficient_fixture():
    """Two smooth scalar trial functions times full Weyl frame components.

    f0=1, f1=t*x0 on unit S3; E_i x0=-x_i in the declared quaternion
    body frame.  Connections in these algebraic tests are held fixed;
    this is not the physical primal gauge/domain selection.
    """
    points, columns = 5, 36
    t = np.linspace(.1, .9, points)
    angle = np.linspace(.2, .7, points)
    axis = np.array([1, 2, -1])/np.sqrt(6)
    x0, xi = np.cos(angle), np.sin(angle)[:, None]*axis
    values = np.stack((np.ones(points), t*x0), axis=1)
    derivatives = np.zeros((points, 4, 2))
    derivatives[:, 0, 1] = x0
    derivatives[:, 1:, 1] = -t[:, None]*xi
    L, e = np.zeros((points, 2, 3, 2, columns)), np.zeros((points, 3, 2, columns))
    DL, De = np.zeros((points, 4, 2, 3, 2, columns)), np.zeros((points, 4, 3, 2, columns))
    column = 0
    for weak in range(2):
        for family in range(3):
            for spin in range(2):
                for mode in range(2):
                    L[:, weak, family, spin, column] = values[:, mode]
                    DL[:, :, weak, family, spin, column] = derivatives[:, :, mode]
                    column += 1
    for family in range(3):
        for spin in range(2):
            for mode in range(2):
                e[:, family, spin, column] = values[:, mode]
                De[:, :, family, spin, column] = derivatives[:, :, mode]
                column += 1
    rng = np.random.default_rng(102011)
    c = .2*(rng.normal(size=columns)+1j*rng.normal(size=columns))
    geometry = intrinsic_round_dirac_coefficients(N=.7, R4=1.2, coordinate_log_R4_rate=.03)
    return dict(coefficients=c, value_map_L=L, value_map_e=e,
                derivative_map_L=DL, derivative_map_e=De,
                H=np.tile([.13+.07j, -.11+.19j], (points, 1)),
                principal_euler_coefficients=geometry['principal_euler_coefficients'],
                contracted_spin=geometry['contracted_spin'],
                spin_placement='CONTRACTED_ZERO_ORDER')


def test_classical_body_zero_is_derived_without_deleting_quantum_loads():
    contract = classical_bosonic_body_source(5)
    np.testing.assert_array_equal(contract['J_H_body'], np.zeros((5, 2)))
    assert contract['quantum_induced_H_load'] is None
    assert contract['quantum_effects_deleted'] is False
    assert contract['numerical_commuting_spinor_iterate_is_body_source'] is False


def test_values_derivatives_and_source_use_one_common_unknown_vector():
    data = coefficient_fixture()
    maps = {key:data[key] for key in ('coefficients', 'value_map_L', 'value_map_e',
                                     'derivative_map_L', 'derivative_map_e')}
    fields = lepton_fields_from_coefficients(**maps)
    np.testing.assert_allclose(fields['L_L'][0, 0, 0, 0],
                               data['value_map_L'][0, 0, 0, 0]@data['coefficients'])
    np.testing.assert_allclose(fields['D_L_L'][0, 0, 0, 0, 0],
                               data['derivative_map_L'][0, 0, 0, 0, 0]@data['coefficients'])
    application = lepton_primal_application(**data)
    assert np.linalg.norm(application['J_H']) > 1e-5
    assert application['J_H_is_classical_bosonic_body'] is False
    assert application['physical_bilinear_expectation_selected'] is False
    assert application['loop_or_native_heat_added'] is False
    zero = lepton_primal_application(**dict(data, coefficients=np.zeros(36)))
    np.testing.assert_array_equal(zero['J_H'], np.zeros((5, 2)))
    np.testing.assert_array_equal(zero['Euler_L'], np.zeros((5, 2, 3, 2)))
    # Zero coefficient iterate does not select a physical classical state.
    assert zero['J_H_is_classical_bosonic_body'] is False


def test_both_weyl_euler_rows_match_retained_four_component_action_signs():
    data = coefficient_fixture()
    app = lepton_primal_application(**data)
    rep = retained_higgs_spin_charge_representation()
    principal = data['principal_euler_coefficients']
    spin = data['contracted_spin']
    Y = rep['family_yukawa']
    full = app['full_fields']
    expected_L = np.zeros_like(app['Euler_L_full'])
    expected_e = np.zeros_like(app['Euler_e_full'])
    for p in range(5):
        for a in range(2):
            for f in range(3):
                expected_L[p, a, f] = sum(principal[mu]@full['DL'][p, mu, a, f]
                                                for mu in range(4))+spin@full['L'][p, a, f]
                expected_L[p, a, f] -= sum(data['H'][p, a]*Y[f, g]*full['e'][p, g]
                                                  for g in range(3))
        for f in range(3):
            expected_e[p, f] = sum(principal[mu]@full['De'][p, mu, f]
                                           for mu in range(4))+spin@full['e'][p, f]
            expected_e[p, f] -= sum(data['H'][p, a].conjugate()*Y[g, f].conjugate()*full['L'][p, a, g]
                                            for g in range(3) for a in range(2))
    np.testing.assert_allclose(app['Euler_L_full'], expected_L, atol=2e-16)
    np.testing.assert_allclose(app['Euler_e_full'], expected_e, atol=2e-16)
    np.testing.assert_allclose(app['Euler_L'], expected_L[..., 2:])
    np.testing.assert_allclose(app['Euler_e'], expected_e[..., :2])
    # Source-owned U has binary64 sqrt(2) rounding, so represented blocks
    # vanish to its rounding precision rather than bitwise.
    np.testing.assert_allclose(expected_L[..., :2], 0, atol=1e-16)
    np.testing.assert_allclose(expected_e[..., 2:], 0, atol=1e-16)
    assert np.linalg.norm(app['spatial_L']) > .01


def test_matter_higgs_jacobian_keeps_hdagger_and_conjugate_source_variation():
    data = coefficient_fixture()
    dc = .17j*data['coefficients']+.03*np.arange(36)
    dH = .12j*data['H']+.07
    result = lepton_primal_jacobian_application(
        **data, delta_coefficients=dc, delta_H=dH)
    step = 2e-6
    plus = lepton_primal_application(**dict(data,
        coefficients=data['coefficients']+step*dc, H=data['H']+step*dH))
    minus = lepton_primal_application(**dict(data,
        coefficients=data['coefficients']-step*dc, H=data['H']-step*dH))
    for key in ('Euler_L', 'Euler_e', 'J_H'):
        np.testing.assert_allclose(result['delta_'+key], (plus[key]-minus[key])/(2*step),
                                   atol=5e-11, rtol=2e-9)
    phase = lepton_primal_jacobian_application(
        **data, delta_coefficients=1j*data['coefficients'], delta_H=np.zeros_like(data['H']))
    # Common matter phase cancels in bar(e)Y†L, even though each field moves.
    np.testing.assert_allclose(phase['delta_J_H'], 0, atol=2e-18)


def test_metric_connection_domain_map_cross_application_differentiates_same_vector():
    data = coefficient_fixture()
    deltas = {name:.13j*data[name] for name in ('value_map_L', 'value_map_e',
                                              'derivative_map_L', 'derivative_map_e')}
    dprincipal, dspin = .09*data['principal_euler_coefficients'], -.11*data['contracted_spin']
    result = lepton_primal_jacobian_application(
        **data, delta_coefficients=np.zeros(36), delta_H=np.zeros_like(data['H']),
        **{'delta_'+name:delta for name, delta in deltas.items()},
        delta_principal_euler_coefficients=dprincipal, delta_contracted_spin=dspin)
    def moved(t):
        return lepton_primal_application(**dict(data,
            **{name:data[name]+t*delta for name, delta in deltas.items()},
            principal_euler_coefficients=data['principal_euler_coefficients']+t*dprincipal,
            contracted_spin=data['contracted_spin']+t*dspin))
    step = 2e-6
    plus, minus = moved(step), moved(-step)
    for key in ('Euler_L', 'Euler_e', 'J_H'):
        np.testing.assert_allclose(result['delta_'+key], (plus[key]-minus[key])/(2*step),
                                   atol=5e-11, rtol=3e-9)


def test_intrinsic_spin_binding_has_temporal_contact_and_signed_angular_term():
    rep = retained_higgs_spin_charge_representation()
    gamma = rep['gamma_LR']
    bound = intrinsic_round_dirac_coefficients(N=.7, R4=1.2, coordinate_log_R4_rate=.03)
    np.testing.assert_allclose(bound['principal_euler_coefficients'][0], 1j*gamma[0]/.7)
    np.testing.assert_allclose(bound['angular_spin'], -1.5j*gamma[1]@gamma[2]@gamma[3]/1.2)
    np.testing.assert_allclose(bound['temporal_spin'], 1.5*.03/.7*1j*gamma[0])
    np.testing.assert_allclose(bound['angular_spin'][2:, :2], np.eye(2)*1.5/1.2)
    np.testing.assert_allclose(bound['angular_spin'][:2, 2:], -np.eye(2)*1.5/1.2)
    actual = retained_e1_lepton_geometry_coefficients()
    assert actual['geometry_source']['branch'] == 24
    assert actual['operator']['physical_matter_field_selected'] is False
    assert actual['operator']['physical_gauge_fluctuation'] is None
    assert actual['full_stationary_base'] is False
    assert np.linalg.norm(actual['operator']['temporal_spin']) > .01


def test_weak_euler_rows_use_owned_complex_pairing_without_extra_two():
    data = coefficient_fixture()
    app = lepton_primal_application(**data)
    testL = np.stack((app['L_L'], 1j*app['L_L']))
    teste = np.stack((app['e_R'], 1j*app['e_R']))
    quad, volume = np.linspace(.02, .08, 5), .69
    rows = lepton_weak_euler_rows(application=app, test_L=testL, test_e=teste,
                                 quadrature=quad, volume_density=volume)
    np.testing.assert_allclose(rows['L'][0], sum(quad[p]*volume*np.vdot(app['L_L'][p], app['Euler_L'][p])
                                                for p in range(5)))
    np.testing.assert_allclose(rows['e'][1], -1j*rows['e'][0])
    np.testing.assert_array_equal(realify_euler_rows(rows),
                                  np.r_[np.r_[rows['L'], rows['e']].real,
                                        np.r_[rows['L'], rows['e']].imag])


def test_spin_placement_and_inconsistent_maps_fail_closed():
    data = coefficient_fixture()
    with pytest.raises(ValueError, match='twice'):
        lepton_primal_application(**dict(data, spin_placement='IN_DERIVATIVE_MAPS'))
    with pytest.raises(ValueError, match='explicitly supplied'):
        lepton_primal_application(**dict(data, contracted_spin=None))
    with pytest.raises(ValueError, match='derivative_map_L'):
        lepton_primal_application(**dict(data, derivative_map_L=data['derivative_map_L'][..., :-1]))
    with pytest.raises(ValueError, match='chirality odd'):
        lepton_primal_application(**dict(data, contracted_spin=np.eye(4)))
