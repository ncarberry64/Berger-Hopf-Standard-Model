from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_c2_1064_segment_weyl_coefficient_cotangent import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_1064_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json"
)


def test_full_core_weyl_cotangent_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_one_probe_and_proof_center_boundaries_are_preserved() -> None:
    payload = build_payload()
    boundary = payload["claim_boundary"]
    assert boundary["finite_core_M_C2_at_z_minus_1_on_proof_centers"] == "EVALUATED"
    assert boundary["full_negative_axis_heat_synthesis"] == "OPEN"
    assert boundary["reset_quotient_pullback"] == "OPEN"
    assert boundary["maximal_tail"] == "OPEN"
    assert boundary["zero_source_force"] == "OPEN"
