from fractions import Fraction

from hypercharge import derive_hypercharges, hypercharge_screen, yukawa_invariance_residuals


def test_hypercharge_derivation_matches_sm_left_weyl_values():
    charges = derive_hypercharges()

    assert charges == {
        "Q": Fraction(1, 6),
        "u_c": Fraction(-2, 3),
        "d_c": Fraction(1, 3),
        "L": Fraction(-1, 2),
        "e_c": Fraction(1, 1),
        "H": Fraction(1, 2),
    }


def test_yukawa_invariance_residuals_vanish():
    residuals = yukawa_invariance_residuals(derive_hypercharges())

    assert residuals == {
        "up": 0,
        "down": 0,
        "charged_lepton": 0,
    }


def test_hypercharge_screen_reports_required_fields():
    screen = hypercharge_screen()

    assert screen.status == "conditional"
    assert screen.assumptions
    assert "Q" in screen.outputs
    assert isinstance(screen.relative_error, dict)

