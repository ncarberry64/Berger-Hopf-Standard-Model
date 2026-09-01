from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_c2_regularized_launch_segment import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_REGULARIZED_LAUNCH_SEGMENT.json"
)


def test_regularized_launch_payload_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_launch_is_explicit_positive_and_endpoint_free() -> None:
    payload = build_payload()
    segment = payload["explicit_segment"]
    launch = payload["launch_ball"]
    assert launch["Delta_interval"][0] > 0.0
    assert launch["selected_eigenline_gap_lower"] > 0.0
    assert launch["regularized_first_Jacobi_generator_upper"] > 0.0
    assert segment["signed_lambda_end_lower"] > 0.0
    assert segment["physical_u_end_lower"] > 0.0
    assert segment["coordinate_time_interval"][0] > 0.0
    assert segment["proper_time_interval"][0] > 0.0
    assert segment["future_endpoint_selected"] is False


def test_state_and_time_coordinates_are_not_conflated() -> None:
    system = build_payload()["exact_regularized_system"]
    assert system["state_parameter"] == "s=lambda_event>=0"
    assert system["physical_readout"] == "u=s^2"
    assert "psi/c_psi" in system["birth_limit"]
