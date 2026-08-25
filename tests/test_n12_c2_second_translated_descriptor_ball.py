from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_c2_second_translated_descriptor_ball import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_SECOND_TRANSLATED_DESCRIPTOR_BALL.json"
)


def test_second_translated_descriptor_ball_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_second_translated_ball_preserves_canonical_margins() -> None:
    payload = build_payload()
    ball = payload["translated_ball"]
    assert ball["derived_local_radius"] > 0.0
    assert ball["hard_self_consistency"] < 0.5
    assert ball["Delta_interval"][0] > 0.0
    assert ball["lapse_interval"][0] > 0.0
    assert ball["D_tau_log_R4_interval"][0] > 0.0
    assert ball["selected_line_gap_lower"] > 0.0
    assert ball["Legendre_event_lower"] > 0.0
    assert payload["adjudication"]["outcome"] == (
        "REGULAR_FORWARD_CONTINUATION_AVAILABLE"
    )
