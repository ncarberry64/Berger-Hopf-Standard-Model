from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_c2_recenterable_launch_endpoint import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_C2_RECENTERABLE_LAUNCH_ENDPOINT.json"
)


def test_recenterable_endpoint_payload_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_endpoint_tube_closes_without_physical_endpoint_claim() -> None:
    payload = build_payload()
    segment = payload["extended_segment"]
    endpoint = payload["endpoint_recenter"]
    assert segment["proper_time_interval"][0] > 0.0
    assert segment["pole_free_Jacobi_growth_upper"] < 1.001
    assert endpoint["endpoint_tube_radius_upper"] > 0.0
    assert endpoint["outer_ball_total_radius_use"] < endpoint[
        "outer_launch_ball_radius"
    ]
    assert endpoint["predictor_is_physical_endpoint"] is False
    assert payload["claim_boundary"]["physical_encapsulation_endpoint_reached"] is False
