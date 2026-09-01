from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_c2_translated_pole_free_segment import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT.json"
)


def test_translated_pole_free_segment_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_second_segment_closes_without_a_stop_or_selector() -> None:
    payload = build_payload()
    segment = payload["translated_segment"]
    endpoint = payload["endpoint_recenter"]
    assert segment["signed_lambda_step"] > 0.0
    assert segment["proper_time_increment_interval"][0] > 0.0
    assert segment["Jacobi_growth_upper"] <= 2.0
    assert (
        endpoint["root_relative_path_plus_tube_upper"]
        < endpoint["translated_ball_radius"]
    )
    assert payload["adjudication"]["outcome"] == (
        "REGULAR_FORWARD_CONTINUATION_AVAILABLE"
    )
    assert endpoint["predictor_is_physical_endpoint"] is False
