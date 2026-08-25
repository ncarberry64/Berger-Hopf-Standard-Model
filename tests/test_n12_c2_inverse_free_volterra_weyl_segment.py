from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from bhsm.interface.aether_forward_c2_volterra_enclosure import (  # noqa: E402
    short_segment_transfer_weyl_enclosure,
)
from derive_n12_c2_inverse_free_volterra_weyl_segment import (  # noqa: E402
    build_payload,
)


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_INVERSE_FREE_VOLTERRA_WEYL_SEGMENT.json"
)


def test_c2_segment_payload_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_all_channels_have_free_endpoint_weyl_chart() -> None:
    payload = build_payload()
    for row in payload["channels_at_z_minus_1"].values():
        assert row["chart_margin_lower"] > 0.0
        assert row["transfer_second_order_remainder_upper"] > 0.0
        assert row["endpoint_condition_imposed"] is False
        assert row["terminal_load_imposed"] is False
        assert row["explicit_matrix_inverse_formed"] is False
        assert row["first_parameter_bounds"][
            "Weyl_parameter_Frobenius_upper"
        ] > 0.0


def test_constant_tiny_scalar_segment_has_positive_b_and_symmetric_weyl() -> None:
    row = short_segment_transfer_weyl_enclosure(
        channel="scalar",
        unit_channel_value=3.0,
        spectral_parameter=-1.0,
        log_radius_interval=(-0.01, -0.01),
        proper_log_radius_rate_absolute_upper=0.0,
        proper_duration_interval=(1.0e-6, 1.0e-6),
    )
    entries = row["two_boundary_Weyl_entries"]
    assert row["chart_margin_lower"] > 0.0
    assert entries["M01_equals_M10"][1] < 0.0
    assert entries["M00"][0] > 0.0
    assert entries["M11"][0] > 0.0


def test_launch_edge_is_not_complete_M_C2() -> None:
    payload = build_payload()
    assert payload["claim_boundary"]["launch_edge_physical_endpoint"] is False
    assert payload["claim_boundary"]["complete_M_C2_maximal_response"].startswith(
        "OPEN"
    )
