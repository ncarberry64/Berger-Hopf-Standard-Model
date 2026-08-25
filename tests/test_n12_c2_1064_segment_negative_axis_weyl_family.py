from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_c2_1064_segment_negative_axis_weyl_family import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_1064_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json"
)


def test_negative_axis_family_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_sampled_impedances_positive_and_paired_remainder_retained() -> None:
    payload = build_payload()
    for row in payload["sampled_crosschecks"]:
        assert all(
            channel["all_backward_impedances_positive"]
            for channel in row["channels"].values()
        )
        assert Decimal(
            row["paired_product_Dirac_uniform_log_R4_remainder_decimal"]
        ) != 0


def test_force_and_tail_boundaries_remain_open() -> None:
    boundary = build_payload()["claim_boundary"]
    assert boundary[
        "finite_core_complete_negative_real_axis_spectral_parameter_coverage"
    ] == "DERIVED_EXECUTABLE"
    assert boundary["joint_AE2_seam"].startswith("OPEN")
    assert boundary["heat_minus_zeta_force"] == "OPEN"
    assert boundary["maximal_tail"] == "OPEN"
