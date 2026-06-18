import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_finite_boundary_algebra import (  # noqa: E402
    BoundaryAlgebraState,
    electric_charge_from_boundary_algebra_state,
    electric_charge_simplified,
    hypercharge_from_boundary_algebra_state,
    physical_boundary_algebra_charge_table,
    physical_boundary_algebra_state_registry,
    projector_eigenvalues_from_state,
    t3_from_boundary_algebra_state,
)


def test_physical_registry_reproduces_charge_hypercharge_rows():
    table = physical_boundary_algebra_charge_table(include_nu_r=True)
    expected = {
        "nu_L": {"T3": Fraction(1, 2), "Y": Fraction(-1), "Q": Fraction(0)},
        "e_L": {"T3": Fraction(-1, 2), "Y": Fraction(-1), "Q": Fraction(-1)},
        "u_L": {"T3": Fraction(1, 2), "Y": Fraction(1, 3), "Q": Fraction(2, 3)},
        "d_L": {"T3": Fraction(-1, 2), "Y": Fraction(1, 3), "Q": Fraction(-1, 3)},
        "nu_R": {"T3": Fraction(0), "Y": Fraction(0), "Q": Fraction(0)},
        "e_R": {"T3": Fraction(0), "Y": Fraction(-2), "Q": Fraction(-1)},
        "u_R": {"T3": Fraction(0), "Y": Fraction(4, 3), "Q": Fraction(2, 3)},
        "d_R": {"T3": Fraction(0), "Y": Fraction(-2, 3), "Q": Fraction(-1, 3)},
    }
    for field, expected_row in expected.items():
        assert table[field]["T3"] == expected_row["T3"]
        assert table[field]["Y"] == expected_row["Y"]
        assert table[field]["Q"] == expected_row["Q"]


def test_simplified_charge_equals_full_charge_for_physical_registry():
    for state in physical_boundary_algebra_state_registry(include_nu_r=True).values():
        values = projector_eigenvalues_from_state(state)
        assert electric_charge_from_boundary_algebra_state(state) == electric_charge_simplified(
            values["C"], values["sigma"]
        )


def test_weak_activity_changes_t3_and_y_not_q():
    active = BoundaryAlgebraState("M3_C", "M2_active", "upper")
    inactive = BoundaryAlgebraState("M3_C", "C_sigma_plus")

    assert t3_from_boundary_algebra_state(active) == Fraction(1, 2)
    assert t3_from_boundary_algebra_state(inactive) == Fraction(0)
    assert hypercharge_from_boundary_algebra_state(active) == Fraction(1, 3)
    assert hypercharge_from_boundary_algebra_state(inactive) == Fraction(4, 3)
    assert electric_charge_from_boundary_algebra_state(active) == electric_charge_from_boundary_algebra_state(inactive)


def test_simplified_charge_table():
    assert electric_charge_simplified(0, +1) == Fraction(0)
    assert electric_charge_simplified(0, -1) == Fraction(-1)
    assert electric_charge_simplified(1, +1) == Fraction(2, 3)
    assert electric_charge_simplified(1, -1) == Fraction(-1, 3)
