from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "artifacts/n12_continuum_majorant_effectiveness"
    / "BHSM_N12_REGULAR_POLE_SOURCE_RESTRICTION.json"
)


def test_regular_pole_source_restriction_localizes_exact_open_transfer() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["validation_passed"] is True
    assert payload["exact_source_support"][
        "direct_projection_onto_Berger_anisotropy_v_Euler_covector"
    ] == 0.0
    assert payload["category_3_positive_duration_collapse_sequence_constructed"] is False
    assert payload["M_star_certified"] is False
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["retained_indirect_transfer"]["finite_rows_are_the_proof"] is False
    assert payload["retained_indirect_transfer"][
        "maximum_sampled_q_v_action_fraction"
    ] < 4.0e-4
    assert payload["retained_indirect_transfer"][
        "maximum_sampled_velocity_v_action_fraction"
    ] < 1.3e-3
