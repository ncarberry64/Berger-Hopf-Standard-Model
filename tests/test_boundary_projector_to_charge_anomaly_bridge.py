import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_projector_algebra import (  # noqa: E402
    ProjectorEigenState,
    anomaly_closure_bridge_confirmed,
    electric_charge_from_projector_state,
    hypercharge_from_projector_state,
    physical_projector_charge_table,
    t3_from_projector_state,
)
from candidate_boundary_integer_primitives import (  # noqa: E402
    electric_charge_from_integer_primitives,
    hypercharge_from_integer_primitives,
    t3_from_integer_primitives,
)


def test_projector_charge_bridge_matches_integer_primitive_bridge():
    for field, row in physical_projector_charge_table(include_nu_r=True).items():
        states = {
            "nu_L": (0, 1, +1, 1),
            "e_L": (0, 1, -1, 1),
            "u_L": (1, 0, +1, 1),
            "d_L": (1, 0, -1, 1),
            "nu_R": (0, 1, +1, 0),
            "e_R": (0, 1, -1, 0),
            "u_R": (1, 0, +1, 0),
            "d_R": (1, 0, -1, 0),
        }
        C, ell, sigma, w = states[field]
        assert row["T3"] == t3_from_integer_primitives(sigma, w)
        assert row["Y"] == hypercharge_from_integer_primitives(C, ell, sigma, w)
        assert row["Q"] == electric_charge_from_integer_primitives(C, ell, sigma, w)


def test_anomaly_closure_bridge_confirmed_is_diagnostic_true():
    assert anomaly_closure_bridge_confirmed() is True


def test_weak_interface_activity_changes_t3_and_y_but_preserves_q():
    left = ProjectorEigenState(1, 0, +1, 1)
    right = ProjectorEigenState(1, 0, +1, 0)

    assert t3_from_projector_state(left) == Fraction(1, 2)
    assert t3_from_projector_state(right) == Fraction(0)
    assert hypercharge_from_projector_state(left) == Fraction(1, 3)
    assert hypercharge_from_projector_state(right) == Fraction(4, 3)
    assert electric_charge_from_projector_state(left) == electric_charge_from_projector_state(right)
