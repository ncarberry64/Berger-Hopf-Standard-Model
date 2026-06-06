from math import isclose, pi

from gauge_couplings import coupling_screens, gauge_coupling_screen


def test_supplied_coupling_screen_values():
    values = coupling_screens()

    assert isclose(values["alpha_1"], 1 / (6 * pi**2))
    assert isclose(values["alpha_2"], 2 / (6 * pi**2))
    assert isclose(values["alpha_3"], 7 / (6 * pi**2))
    assert isclose(values["sin2_theta_w"], 3 / 13)
    assert isclose(values["alpha_em_inv_mew"], 13 * pi**2)


def test_coupling_screen_is_close_to_reference_values():
    screen = gauge_coupling_screen()

    assert screen.status == "screened"
    assert screen.relative_error["sin2_theta_w"] < 0.005
    assert screen.relative_error["alpha_em_inv_mew"] < 0.01
    assert screen.relative_error["alpha_3"] < 0.01

