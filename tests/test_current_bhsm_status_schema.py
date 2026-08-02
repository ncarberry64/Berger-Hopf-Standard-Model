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
        "current_campaign": "v11.0 Canonical crystallization, multiplicative-support Haar action, and physical completion gate",
        "canonical_doctrine_verdict": "BHSM_CANONICAL_RELATIONAL_ENVELOPMENT_ARCHITECTURE_CRYSTALLIZED",
        "canonical_ontology_complete": True,
        "canonical_ontology_is_physical_completion": False,
        "physical_flavor_matrix_derived": False,
        "current_exact_verdict": "BHSM_MULTIPLICATIVE_SUPPORT_HAAR_KINEMATICS_DERIVED_BUT_NORMALIZATION_AND_SUPPORT_WEIGHTS_NOT_ACTION_FIXED",
        "next_exact_object": "ACTION_DERIVED_SUPPORT_REPRESENTATION_FUNCTOR_ON_STRATIFIED_SECTORS_WITH_FIXED_HAAR_SCALE",
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
