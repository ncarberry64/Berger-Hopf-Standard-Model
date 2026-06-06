from math import isclose, pi

from higgs_scale import electroweak_scale_candidate, epsilon_alpha, higgs_scale_screen, hopf_lift_mass


def test_epsilon_alpha_formula():
    alpha_inv = 137.035999084

    assert isclose(epsilon_alpha(alpha_inv), alpha_inv / (12 * pi**2) - 1)


def test_electroweak_scale_candidate_screen():
    v = electroweak_scale_candidate()
    screen = higgs_scale_screen()

    assert screen.status == "screened"
    assert isclose(screen.outputs["v_gev"], v)
    assert screen.relative_error["v_gev"] < 0.01
    assert isclose(screen.outputs["m_lift_gev"], hopf_lift_mass(v))

