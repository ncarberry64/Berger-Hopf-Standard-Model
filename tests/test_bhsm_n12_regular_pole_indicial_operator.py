from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "artifacts/n12_continuum_majorant_effectiveness"
    / "BHSM_N12_REGULAR_POLE_INDICIAL_OPERATOR.json"
)


def test_regular_pole_indicial_correction_fails_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["validation_passed"] is True
    assert payload["M_star_certified"] is False
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["logarithmic_normal_form"][
        "essential_spectrum_contains_zero"
    ] is True
    assert payload["reclassification"][
        "pointwise_matrix_gap_sqrt29_minus5_invalidated"
    ] is False
    assert payload["reclassification"][
        "uniform_static_M_star_exists_by_the_old_Neumann_split"
    ] is False
    assert payload["reclassification"]["BHSM_continuum_child_disproved"] is False
    assert payload["reclassification"][
        "pure_v_Weyl_sequence_proved_to_satisfy_the_full_mixed_constraints"
    ] is False
    assert payload["reclassification"][
        "full_positive_duration_mixed_operator_proved_to_have_zero_essential_spectrum"
    ] is False

    rows = payload["explicit_Weyl_sequence"]["rows"]
    residuals = [
        row["normalized_indicial_residual_before_positive_coefficient"]
        for row in rows
    ]
    assert all(left > right for left, right in zip(residuals, residuals[1:]))
    ratios = [left / right for left, right in zip(residuals, residuals[1:])]
    assert all(1.9 < ratio < 2.1 for ratio in ratios)
