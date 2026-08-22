from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "artifacts/n12_continuum_majorant_effectiveness"


def _load(name: str) -> dict:
    return json.loads((TARGET / name).read_text(encoding="utf-8"))


def test_continuum_majorant_checkpoint_fails_closed() -> None:
    ownership = _load("BHSM_N12_CONTINUUM_MAJORANT_OWNERSHIP_AUDIT.json")
    localization = _load("BHSM_N12_EFFECTIVE_INVERSE_LOCALIZATION.json")
    history = _load("BHSM_N12_POSITIVE_DURATION_CALDERON_HISTORY.json")
    manifest = _load("BHSM_N12_CONTINUUM_MAJORANT_CHECKPOINT_MANIFEST.json")

    assert ownership["validation_passed"] is True
    assert ownership["radii_polynomial_rigorously_evaluable"] is False
    assert ownership["constants"]["C_r"]["status"] == (
        "CLOSED_EXPLICIT_RETAINED_ACTION_CONSTANT"
    )
    assert ownership["constants"]["C_r"][
        "explicit_validated_upper_bound"
    ] > 0.0
    assert ownership["constants"]["K"][
        "explicit_positive_duration_continuum_inverse_bound"
    ] is None
    assert localization["validation_passed"] is True
    assert localization["BHSM_interpretation"][
        "qualitative_closed_range_invalidated"
    ] is False
    assert history["validation_passed"] is True
    assert history["measurement"][
        "is_a_rigorous_positive_duration_observation_lower_bound"
    ] is False
    assert manifest["claims"]["principal_high_tail_bound_is_the_full_inverse_K"] is False
    assert manifest["claims"]["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert manifest["claims"]["FULL_BHSM_COMPLETE"] is False
