"""Regression guards for the DOP853 bordered response variation tube."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_STOP_DOP853_BORDERED_RESPONSE_SECOND_VARIATION.json"


def test_complete_cellwise_response_variation_tube() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["mesh"]["response_cells"] == 8692
    assert payload["claim_boundary"]["correlated_Y_Z1_Z2"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert all(row["selected_branch"] == 24 for row in payload["rows"])
    assert "self_consistent_second_variation_denominator_positive_everywhere" in payload["validation"]
    assert len(payload["scalar_denominator_owner_cells"]) == payload["summary"]["scalar_denominator_owner_cells"]
    assert payload["first_variation_validation_passed"] is True
    assert payload["claim_boundary"]["cellwise_response_first_variation_tube"] == "CERTIFIED_FINITE"
    assert all(
        math.isfinite(row["certified_first_variation_2_norm_upper"])
        for row in payload["rows"]
    )
    if payload["validation_passed"]:
        assert payload["claim_boundary"]["cellwise_response_second_variation_tube"] == "CERTIFIED_FINITE"
        assert all(
            math.isfinite(row["certified_first_variation_2_norm_upper"])
            and math.isfinite(row["uniform_second_variation_2_norm_upper"])
            for row in payload["rows"]
        )
    else:
        assert payload["scalar_denominator_owner_cells"]
        assert all(
            row["uniform_second_variation_2_norm_upper"] is None
            for row in payload["rows"]
            if not row["self_consistent_denominator_closed"]
        )


def test_source_ontology_and_inverse_boundary_are_preserved() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    validation = payload["validation"]
    assert validation["only_external_Cauchy_birth_source_zero"] is True
    assert validation["no_internal_seam_response_zeroed_or_double_counted"] is True
    assert validation["no_full_kinetic_Dirac_or_history_inverse_used"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
