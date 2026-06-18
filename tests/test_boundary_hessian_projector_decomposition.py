import sys
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_action_hessian import (  # noqa: E402
    candidate_hessian_eigenvalues,
    closure_dimension_from_projector,
    finite_algebra_block_from_projector,
    hessian_projector_registry,
    stability_hierarchy_passes,
)


def test_hessian_projector_registry_and_blocks():
    registry = hessian_projector_registry()
    assert set(registry) == {"P_ref", "P_orient", "P_cyclic", "P_excess"}
    assert closure_dimension_from_projector("P_ref") == "1"
    assert finite_algebra_block_from_projector("P_ref") == "C"
    assert closure_dimension_from_projector("P_orient") == "2"
    assert finite_algebra_block_from_projector("P_orient") == "M2(C)"
    assert closure_dimension_from_projector("P_cyclic") == "3"
    assert finite_algebra_block_from_projector("P_cyclic") == "M3(C)"
    assert closure_dimension_from_projector("P_excess") == ">=4"
    assert finite_algebra_block_from_projector("P_excess") == "higher/composite"


def test_hessian_eigenvalue_hierarchy():
    values = candidate_hessian_eigenvalues(gap=10)
    assert values["P_ref"].eigenvalue == Fraction(0)
    assert values["P_orient"].eigenvalue == Fraction(1)
    assert values["P_cyclic"].eigenvalue == Fraction(1)
    assert values["P_excess"].eigenvalue == Fraction(10)
    assert stability_hierarchy_passes(gap=10)
    with pytest.raises(ValueError):
        candidate_hessian_eigenvalues(gap=1)


def test_hessian_decomposition_doc():
    text = (ROOT / "theory" / "boundary_hessian_projector_decomposition.md").read_text()
    assert "P_ref + P_orient + P_cyclic + P_excess = I" in text
    assert "mu_excess >= gap" in text
    assert "not the full Hessian proof" in text
