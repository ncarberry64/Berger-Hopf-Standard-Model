import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_admissible_closure_spectrum import (  # noqa: E402
    admissible_closure_pass,
    closure_sector_registry,
    endomorphism_algebra_for_dim,
    finite_algebra_blocks_from_spectrum,
    finite_boundary_algebra_bridge,
    minimality_audit,
)


def test_endomorphism_algebras_for_admissible_dimensions():
    assert endomorphism_algebra_for_dim(1) == "C"
    assert endomorphism_algebra_for_dim(2) == "M2(C)"
    assert endomorphism_algebra_for_dim(3) == "M3(C)"
    with pytest.raises(ValueError):
        endomorphism_algebra_for_dim(0)


def test_registry_and_minimality_audit():
    registry = closure_sector_registry()
    assert sorted(sector.dimension for sector in registry.values()) == [1, 2, 3]
    assert all(admissible_closure_pass(sector.dimension) for sector in registry.values())

    audit = minimality_audit()
    assert audit["required_dimensions_present"] is True
    assert audit["all_required_dimensions_admissible"] is True
    assert audit["finite_algebra_bridge_confirmed"] is True
    assert audit["unique_first_principles_derivation"] is False
    assert audit["full_hessian_proof_complete"] is False


def test_finite_algebra_bridge_recovers_previous_blocks():
    assert finite_algebra_blocks_from_spectrum() == {
        "End(C^1)": "C",
        "End(C^2)": "M2(C)",
        "End(C^3)": "M3(C)",
    }
    bridge = finite_boundary_algebra_bridge()
    assert bridge["A_channel"] == "C_ell direct_sum M3(C)_C"
    assert bridge["A_weak"] == "M2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}"


def test_closure_spectrum_bridge_doc():
    text = (ROOT / "theory" / "closure_spectrum_to_finite_algebra_bridge.md").read_text()
    assert "D_adm = {1,2,3}" in text
    assert "End(C^1) = C" in text
    assert "End(C^2) = M2(C)" in text
    assert "End(C^3) = M3(C)" in text
    assert "A_channel = C_ell direct_sum M3(C)_C" in text
