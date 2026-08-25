from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_incoming_regularized_terminal_segment import (  # noqa: E402
    build_payload,
)


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_INCOMING_REGULARIZED_TERMINAL_SEGMENT.json"
)


def test_incoming_terminal_segment_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_incoming_sign_orientation_and_nonzero_interval() -> None:
    payload = build_payload()
    ball = payload["terminal_ball"]
    segment = payload["explicit_segment"]
    assert ball["c_psi_interval"][1] < 0.0
    assert ball["b_psi_interval"][0] > 0.0
    assert ball["Delta_interval"][1] < 0.0
    assert ball["minus_Delta_interval"][0] > 0.0
    assert ball["selected_eigenline_gap_lower"] > 0.0
    assert ball["regularized_first_Jacobi_generator_upper"] > 0.0
    assert segment["positive_lambda_end_lower"] > 0.0
    assert segment["physical_u_end_lower"] > 0.0
    assert segment["proper_lookback_duration_interval"][0] > 0.0
    assert segment["physical_history_member_selected"] is False


def test_incoming_chart_does_not_reverse_physical_time() -> None:
    system = build_payload()["exact_regularized_system"]
    assert "backward_from_terminal" in system["state_parameter"]
    assert system["d_proper_lookback_ds"].endswith(">0")
    assert "decreases_to_zero" in system["forward_orientation"]
