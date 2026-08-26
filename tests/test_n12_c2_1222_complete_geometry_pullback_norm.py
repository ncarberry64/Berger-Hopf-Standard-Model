from __future__ import annotations

import json
from pathlib import Path

from scripts.derive_n12_c2_1222_complete_geometry_pullback_norm import build_payload


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts" / "flagship_integration" / "BHSM_N12_C2_1222_COMPLETE_GEOMETRY_PULLBACK_NORM.json"


def test_complete_geometry_pullback_norm() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["complete_finite_core_geometry_pullback_norm"] == "CERTIFIED"
    assert payload["claim_boundary"]["signed_finite_core_geometry_covector"] == "OPEN"
    assert len(payload["channels_at_z_minus_1"]) == 3
    for row in payload["channels_at_z_minus_1"].values():
        assert row["complete_geometry_norm_upper"] > 0.0
        assert row["signed_covector_value_evaluated"] is False


def test_stored_complete_geometry_artifact_matches_builder() -> None:
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert stored == build_payload()
