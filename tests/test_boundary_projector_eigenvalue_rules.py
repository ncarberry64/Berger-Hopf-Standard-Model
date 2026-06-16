import sys
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_projector_algebra import (  # noqa: E402
    ProjectorEigenState,
    electric_charge_from_projector_state,
    hypercharge_from_projector_state,
    physical_projector_charge_table,
    physical_projector_state_registry,
    t3_from_projector_state,
    validate_projector_eigenstate,
)


def test_physical_projector_state_registry_matches_expected_eigenvalues():
    states = physical_projector_state_registry(include_nu_r=True)
    assert states == {
        "nu_L": ProjectorEigenState(0, 1, +1, 1),
        "e_L": ProjectorEigenState(0, 1, -1, 1),
        "u_L": ProjectorEigenState(1, 0, +1, 1),
        "d_L": ProjectorEigenState(1, 0, -1, 1),
        "e_R": ProjectorEigenState(0, 1, -1, 0),
        "u_R": ProjectorEigenState(1, 0, +1, 0),
        "d_R": ProjectorEigenState(1, 0, -1, 0),
        "nu_R": ProjectorEigenState(0, 1, +1, 0),
    }


def test_projector_charge_table_reproduces_sm_diagnostic_rows():
    table = physical_projector_charge_table(include_nu_r=True)
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
    assert table == expected


def test_eigenvalue_validation_rejects_invalid_projector_values():
    valid = ProjectorEigenState(1, 0, -1, 1)
    validate_projector_eigenstate(valid)

    for invalid in [
        ProjectorEigenState(2, 0, -1, 1),
        ProjectorEigenState(1, 2, -1, 1),
        ProjectorEigenState(1, 0, 0, 1),
        ProjectorEigenState(1, 0, -1, 2),
    ]:
        with pytest.raises(ValueError):
            validate_projector_eigenstate(invalid)


def test_charge_helpers_are_fraction_exact():
    state = ProjectorEigenState(1, 0, +1, 0)
    assert t3_from_projector_state(state) == Fraction(0)
    assert hypercharge_from_projector_state(state) == Fraction(4, 3)
    assert electric_charge_from_projector_state(state) == Fraction(2, 3)
