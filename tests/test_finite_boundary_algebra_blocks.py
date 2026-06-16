import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_finite_boundary_algebra import (  # noqa: E402
    BoundaryAlgebraState,
    C_from_channel_block,
    channel_multiplicity_from_block,
    ell_from_channel_block,
    projector_eigenvalues_from_state,
    sigma_from_weak_block,
    validate_boundary_algebra_state,
    w_from_weak_block,
)


def test_channel_block_mappings():
    assert C_from_channel_block("C_ell") == 0
    assert ell_from_channel_block("C_ell") == 1
    assert channel_multiplicity_from_block("C_ell") == 1

    assert C_from_channel_block("M3_C") == 1
    assert ell_from_channel_block("M3_C") == 0
    assert channel_multiplicity_from_block("M3_C") == 3


def test_weak_block_mappings():
    assert w_from_weak_block("M2_active") == 1
    assert sigma_from_weak_block("M2_active", "upper") == +1
    assert sigma_from_weak_block("M2_active", "lower") == -1
    assert w_from_weak_block("C_sigma_plus") == 0
    assert sigma_from_weak_block("C_sigma_plus") == +1
    assert w_from_weak_block("C_sigma_minus") == 0
    assert sigma_from_weak_block("C_sigma_minus") == -1


def test_projector_eigenvalues_from_state():
    assert projector_eigenvalues_from_state(BoundaryAlgebraState("M3_C", "M2_active", "upper")) == {
        "C": 1,
        "ell": 0,
        "w": 1,
        "sigma": 1,
    }


def test_invalid_block_or_orientation_combinations_raise():
    invalid_states = [
        BoundaryAlgebraState("bad", "M2_active", "upper"),
        BoundaryAlgebraState("C_ell", "bad", None),
        BoundaryAlgebraState("C_ell", "M2_active", None),
        BoundaryAlgebraState("C_ell", "M2_active", "sideways"),
        BoundaryAlgebraState("C_ell", "C_sigma_plus", "upper"),
    ]
    for state in invalid_states:
        with pytest.raises(ValueError):
            validate_boundary_algebra_state(state)
