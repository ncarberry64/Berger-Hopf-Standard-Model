from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_c2_finite_translated_descriptor_cover import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_FINITE_TRANSLATED_DESCRIPTOR_COVER.json"
)


def test_finite_translated_descriptor_cover_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_cover_rows_are_forward_regular_and_not_physical_endpoints() -> None:
    payload = build_payload()
    rows = payload["cover"]["rows"]
    assert rows
    for row in rows:
        assert row["signed_lambda_step"] > 0.0
        assert row["proper_time_increment_interval"][0] > 0.0
        assert row["proof_center_branch"] == 24
        assert (
            row["root_relative_path_plus_tube_upper"]
            < row["translated_ball_total_radius"]
        )
        assert row["predictor_is_physical_endpoint"] is False
    assert payload["cover"]["exhaustion_is_canonical_stop"] is False
