from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_sm_derivation_gate import sm_input_dependency_registry  # noqa: E402


REQUIRED_OBJECTS = {
    "B",
    "L",
    "T3",
    "Y",
    "Q",
    "SU(3)_c",
    "SU(2)_L",
    "U(1)_Y",
    "fermion chirality",
    "left/right multiplets",
    "color triplet/singlet split",
    "weak doublet/singlet split",
    "Higgs doublet",
    "Yukawa coupling layer",
    "CKM",
    "PMNS",
    "anomaly cancellation",
}


def test_sm_input_dependency_registry_has_required_objects() -> None:
    rows = sm_input_dependency_registry()
    objects = {row["object"] for row in rows}
    assert REQUIRED_OBJECTS <= objects
    for row in rows:
        assert row["uses_sm_input"] is True
        assert row["input_type"]
        assert row["replacement_needed_for_full_derivation"]
        assert row["candidate_bhsm_primitive"]
        assert row["risk_if_unreplaced"]


def test_dependency_audit_markdown_contains_required_conclusion() -> None:
    text = (ROOT / "theory" / "sm_input_dependency_audit.md").read_text(
        encoding="utf-8"
    )
    assert "The strongest current BHSM layer is downstream" in text
    assert "moving B, L, T3, chirality, color, weak isospin, and hypercharge" in text
    for obj in REQUIRED_OBJECTS:
        assert obj in text
