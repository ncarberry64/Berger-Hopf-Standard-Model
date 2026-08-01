from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_current_bhsm_status_json_schema() -> None:
    status = json.loads((ROOT / "docs" / "current_bhsm_status.json").read_text())
    assert status == {
        "status": "Full BHSM v1.0 Candidate",
        "candidate_architecture_complete": True,
        "full_bhsm_proven": False,
        "standard_model_fully_derived": False,
        "replacement_goal": "derive the Standard Model as the low-energy effective limit of BHSM",
        "local_sm_layer_status": "preserved infrared layer until derived",
        "mass_numerical_closure": False,
        "dark_matter_solved": False,
        "particle_dark_matter_disproven": False,
        "collective_curvature_layer": "connected topographic-gravity extension candidate",
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "current_campaign": "v10.4 Stratified-core spacetime-support action gate",
        "physical_flavor_matrix_derived": False,
        "current_exact_verdict": "BHSM_MULTIPLE_INEQUIVALENT_SUPPORT_ACTIONS_REMAIN_AFTER_AUTHOR_EXTENSION_SELECTION",
        "next_exact_object": "ACTION_PRINCIPLE_FIXING_Z_UPSILON_U_UPSILON_AND_SUPPORT_COUPLINGS",
    }


def test_current_status_markdown_contains_required_public_safe_wording() -> None:
    text = (ROOT / "docs" / "current_bhsm_status.md").read_text(encoding="utf-8")
    required = (
        "Full BHSM v1.0 Candidate is a repo-audited completion framework, "
        "not yet a completed replacement of the Standard Model."
    )
    assert required in text
    assert "replacement by derivation" in text
    assert "preserved infrared layer" in text
