from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from certify_n12_c2_refined_reset_root_center import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.json"
)


def test_refined_root_payload_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_refined_radii_ball_closes() -> None:
    theorem = build_payload()["refined_radii_theorem"]
    assert theorem["radii_polynomial_at_certified_radius"] < 0.0
    assert theorem["contraction_at_certified_radius"] < 1.0
    assert 0.0 < theorem["a_posteriori_root_distance_upper"] < 1.0e-14


def test_recenter_is_proof_coordinate_not_selector() -> None:
    payload = build_payload()
    assert payload["claim_boundary"]["physical_reset_family_member_selected"] is False
    assert payload["proof_coordinate_Newton_step"]["role"].endswith(
        "NOT_A_PHYSICAL_SELECTOR"
    )
