import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_common_domain_charge_source_clock import (
    corrected_source_clock_higgs_first, charge_clock_direction_effect)
from bhsm.interface.muon_common_domain_charge_transport import (
    holomorphic_charge_first, source_clock_higgs_first)
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES


def generators():
    i = FAMILY_INDICES[1]
    return lepton_unit_trace_gauge_representation()['generators'][:, i][:, :, i]


def test_source_cell_clock_matches_literal_nonconstant_lapse_curve_and_charge_direction():
    N = 1.2+.13j; k = .3-.09j
    base = np.array([.12+.03j, -.07+.04j, .03j, .02-.01j])
    nodal = np.array([.02j, .04, -.01+.01j, .03])
    h = np.array([.9+.04j, .12-.02j, .06j, .03])
    field_rate = 1j*N*nodal
    result = corrected_source_clock_higgs_first(base+field_rate, field_rate, 0, 0, 1, N)
    eps = 2e-6
    # The branch solves N(z) dz/dtau=-i; nodal field is linear in tau.
    def curve(tau):
        z = (np.sqrt(N*N-2j*k*tau)-N)/k
        return h+base*z+nodal*tau
    np.testing.assert_allclose(result['H_source_clock_first'],
                               (curve(eps)-curve(-eps))/(2*eps), rtol=2e-9, atol=3e-11)
    G = generators()
    exact = holomorphic_charge_first(h, result['H_source_clock_first'], G)['charge_first']
    finite = (holomorphic_charge_first(curve(eps), np.zeros(4), G)['charge']-
              holomorphic_charge_first(curve(-eps), np.zeros(4), G)['charge'])/(2*eps)
    np.testing.assert_allclose(exact, finite, rtol=3e-9, atol=4e-11)
    old = source_clock_higgs_first(base+field_rate, field_rate, 0, 1, N)
    assert np.linalg.norm(result['H_source_clock_first']-old) > .05


def test_both_connector_legs_preserve_original_clock_and_independent_nodal_motion():
    base = np.array([.3+.1j, .2j, -.1+.04j, .02])
    nodal = np.array([.02j, -.03, .04+.02j, .01])
    slope = .03-.02j; w = .2+.4j; N = 1.1-.07j
    field_rate = 1j*N/w*nodal
    for part in (1, 2):
        result = corrected_source_clock_higgs_first(base+field_rate, field_rate, part, slope, w, N)
        np.testing.assert_array_equal(result['H_source_clock_first'],
                                     source_clock_higgs_first(base+field_rate, field_rate, slope, w, N))
        np.testing.assert_allclose(result['H_source_clock_first'], (slope*base+nodal)/w, atol=8e-17)
    constant = corrected_source_clock_higgs_first(base+field_rate, field_rate, 2, 0, w, N)
    np.testing.assert_allclose(constant['H_source_clock_first'], nodal/w, atol=8e-17)


def test_complete_analytic_source_directions_and_nonzero_charge_neutral_returns_are_kept():
    h = np.array([.9+.02j, .1-.03j, .07j, .03])
    dh = np.array([.1j, .02+.04j, -.03, .06])
    q = holomorphic_charge_first(h, dh, generators())
    rng = np.random.default_rng(805)
    F = expm(.04*(rng.normal(size=(6, 6))+1j*rng.normal(size=(6, 6))))
    L = np.linalg.solve(F.T, np.eye(6))
    result = charge_clock_direction_effect(q['charge'], q['charge_first'], F, L)
    for j in range(6):
        expected = np.linalg.solve(F, q['charge_first']@F[:, j])
        np.testing.assert_allclose(result['source_direction_clock_correction'][:, j], expected, atol=4e-17)
    np.testing.assert_allclose(result['analytic_dual_direction_difference'], 0, atol=7e-17)
    np.testing.assert_allclose(result['charged_to_charged_clock_correction'], 0, atol=9e-17)
    np.testing.assert_allclose(result['neutral_to_neutral_clock_correction'], 0, atol=9e-17)
    assert np.linalg.norm(result['charged_to_neutral_clock_correction']) > .05
    assert np.linalg.norm(result['neutral_to_charged_clock_correction']) > .01
