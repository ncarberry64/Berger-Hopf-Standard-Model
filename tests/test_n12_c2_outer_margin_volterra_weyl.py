from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_c2_outer_margin_volterra_weyl import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_C2_OUTER_MARGIN_VOLTERRA_WEYL.json"
)


def test_extended_weyl_payload_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_extended_channels_are_inverse_free_and_open_ended() -> None:
    payload = build_payload()
    for row in payload["channels_at_z_minus_1"].values():
        assert row["chart_margin_lower"] > 0.0
        assert row["terminal_load_imposed"] is False
        assert row["explicit_matrix_inverse_formed"] is False
    assert payload["claim_boundary"]["physical_encapsulation_endpoint_reached"] is False
