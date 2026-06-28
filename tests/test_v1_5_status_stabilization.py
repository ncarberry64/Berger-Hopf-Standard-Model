from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bhsm.interface.neutrino_closure_status import (
    ACTION_DERIVED_RESPONSE_CONE_STATUS,
    DIMENSIONFUL_EV_GEV_MASS_CLOSURE_STATUS,
    DIMENSIONLESS_PROPAGATION_CLOSURE_STATUS,
    MEASUREMENT_SUPPORTED_ADMISSIBLE_POSITIVITY_STATUS,
    NEUTRAL_SPECTRAL_MASS_THEOREM_STATUS,
    REMAINING_MISSING_OBJECTS,
    build_v1_5_status_stabilization_report,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/BHSM_v1_5_status_stabilization_report.json"
FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_status_stabilization_preserves_the_five_part_split() -> None:
    report = build_v1_5_status_stabilization_report()
    assert report.dimensionless_propagation_closure_status == DIMENSIONLESS_PROPAGATION_CLOSURE_STATUS
    assert report.neutral_spectral_mass_theorem_status == NEUTRAL_SPECTRAL_MASS_THEOREM_STATUS
    assert (
        report.measurement_supported_admissible_positivity_status
        == MEASUREMENT_SUPPORTED_ADMISSIBLE_POSITIVITY_STATUS
    )
    assert report.action_derived_response_cone_status == ACTION_DERIVED_RESPONSE_CONE_STATUS
    assert report.dimensionful_ev_gev_mass_closure_status == DIMENSIONFUL_EV_GEV_MASS_CLOSURE_STATUS
    assert report.remaining_missing_objects == REMAINING_MISSING_OBJECTS
    assert report.physical_mass_emitted is False
    assert report.raw_neutral_kernel_psd_claimed is False
    assert report.complete_neutral_action_claimed is False


def test_status_artifact_is_parseable_and_fail_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload == build_v1_5_status_stabilization_report().to_dict()
    assert payload["stack_merged"] is True
    assert payload["merge_path"] == "aggregate_integration_branch_from_main"
    assert payload["public_base_branch"] == "main"
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False
    assert payload["empirical_inputs_used"] is False
    assert payload["external_review_ready"] is True


def test_frozen_prediction_hashes_remain_exact() -> None:
    for path, expected in FROZEN_HASHES.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
