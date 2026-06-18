from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_sm_derivation_gate import boundary_primitive_registry  # noqa: E402


ALLOWED_PRIMITIVE_STATUSES = {
    "candidate_primitive",
    "operationally_tested",
    "needs_derivation",
    "speculative",
    "forbidden_as_claim",
}


def test_boundary_primitives_are_cataloged_with_guarded_statuses() -> None:
    rows = boundary_primitive_registry()
    primitives = {row["primitive"] for row in rows}
    assert "Hopf fiber winding" in primitives
    assert "Berger base winding" in primitives
    assert "chirality from boundary orientation/asymmetry" in primitives
    assert "color from active three-channel internal degeneracy" in primitives
    assert "weak isospin from two-state boundary interface orientation" in primitives
    assert "hypercharge from admissible boundary phase closure" in primitives
    assert "gauge group from automorphism/action algebra of admissible boundary channels" in primitives
    for row in rows:
        assert row["status"] in ALLOWED_PRIMITIVE_STATUSES


def test_boundary_primitives_doc_is_roadmap_not_derivation_claim() -> None:
    text = (
        ROOT / "theory" / "bhsm_boundary_primitives_for_sm_derivation.md"
    ).read_text(encoding="utf-8")
    assert "roadmap, not a derivation claim" in text
    assert "No primitive in this file is promoted to full gauge-group derivation." in text
    assert "needs_derivation" in text
