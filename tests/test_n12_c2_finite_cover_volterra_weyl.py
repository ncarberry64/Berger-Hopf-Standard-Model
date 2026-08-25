from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_c2_finite_cover_volterra_weyl import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_C2_FINITE_COVER_VOLTERRA_WEYL.json"
)


def test_finite_cover_weyl_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_finite_cover_response_is_inverse_free_and_unloaded() -> None:
    payload = build_payload()
    assert payload["finite_history_response"]["segment_count"] == 98
    assert payload["finite_history_response"]["proper_duration_interval"][0] > 0.0
    for channel in payload["channels_at_z_minus_1"].values():
        assert channel["chart_margin_lower"] > 0.0
        assert channel["terminal_load_imposed"] is False
        assert channel["explicit_matrix_inverse_formed"] is False
