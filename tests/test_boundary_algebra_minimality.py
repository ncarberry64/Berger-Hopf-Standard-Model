import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_automorphism_closure import (  # noqa: E402
    finite_boundary_algebra_descriptor,
    minimality_audit,
    minimality_requirements,
)


def test_minimality_requirements_are_supplied():
    audit = minimality_audit()
    assert audit["diagnostic_requirements_met"] is True
    assert audit["unique_first_principles_derivation"] is False
    assert set(audit["requirements"]) == set(minimality_requirements())
    assert all(row["supplied"] for row in audit["requirements"].values())


def test_finite_boundary_algebra_descriptor_preserves_previous_gate():
    descriptor = finite_boundary_algebra_descriptor()
    assert descriptor["A_channel"] == "C_ell direct_sum M3(C)_C"
    assert descriptor["A_weak"] == "M2(C)_{w=1} direct_sum C_{sigma=+} direct_sum C_{sigma=-}"
    assert descriptor["P_C"] == "central projection onto M3(C)_C"
    assert descriptor["P_ell"] == "central projection onto C_ell"
    assert descriptor["P_w"] == "central projection onto M2(C)_{w=1}"
    assert descriptor["S_sigma"] == "Z2 orientation grading on weak-interface orientation space"


def test_minimality_document_lists_required_blocks():
    text = (ROOT / "theory" / "boundary_algebra_minimality_audit.md").read_text()
    for item in [
        "single-channel closure",
        "three-channel active closure",
        "active two-orientation interface",
        "inactive upper orientation",
        "inactive lower orientation",
    ]:
        assert item in text
    assert "not yet uniquely derived from first-principles Berger-Hopf geometry" in text
