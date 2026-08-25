from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_c2_pole_free_outer_margin_extension import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION.json"
)


def test_outer_margin_extension_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_pole_free_extension_is_longer_and_recenterable() -> None:
    payload = build_payload()
    ball = payload["improved_launch_ball"]
    segment = payload["extended_segment"]
    endpoint = payload["endpoint_recenter"]
    assert ball["pole_free_R_upper"] < ball["superseded_crude_R_upper"]
    assert ball["Delta_interval"][0] > 0.0
    assert segment["proper_time_interval"][0] > 0.0
    assert segment["Jacobi_growth_upper"] < 2.0
    assert endpoint["outer_ball_total_radius_use"] < ball["outer_action_radius"]
    assert endpoint["predictor_is_physical_endpoint"] is False
