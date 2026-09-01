from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_c2_accumulated_translated_volterra_weyl import (  # noqa: E402
    build_payload,
)


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_ACCUMULATED_TRANSLATED_VOLTERRA_WEYL.json"
)


def test_accumulated_translated_weyl_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_accumulated_response_is_inverse_free_and_unloaded() -> None:
    payload = build_payload()
    assert payload["accumulated_history"]["segment_count"] == 2
    assert payload["accumulated_history"]["proper_duration_interval"][0] > 0.0
    for channel in payload["channels_at_z_minus_1"].values():
        assert channel["chart_margin_lower"] > 0.0
        assert channel["terminal_load_imposed"] is False
        assert channel["explicit_matrix_inverse_formed"] is False
