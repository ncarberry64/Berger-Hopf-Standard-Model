from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_FROZEN_DECIMAL_GAUSS8_CENTER.json"
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_frozen_decimal_gauss8_center_has_one_counted_descriptor_split() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["identity"]["source_terms_added"] == 0
    assert payload["identity"]["internal_descriptor_term_double_counted"] is False
    assert payload["claim_boundary"]["Decimal_Gauss8_linear_center"] == "FROZEN"
    assert payload["claim_boundary"][
        "continuous_preterminal_margin_and_interval_Newton"
    ] == "OPEN"
    summary = payload["summary"]
    assert summary["maximum_descriptor_cross_order_increment"] < 2.0e-16
    assert summary["last_complete_node_descriptor_margin"] > 1.5e-12
    assert 0.0 < summary["linearized_later_stop_time_shift"] < summary[
        "remaining_terminal_dense_cell_time"
    ]
    for relative, digest in payload["inputs"].items():
        assert _sha256(ROOT / relative) == digest

    with np.load(ROOT / payload["data"]) as data:
        corrected = data["corrected_augmented_action_values"]
        state = data["state_correction_profile"]
        direct = data["direct_descriptor_correction_profile"]
        descriptor = data["descriptor_correction_profile"]
        assert corrected.shape == (371, 99)
        assert state.shape == (371, 98)
        assert direct.shape == descriptor.shape == (371,)
        assert np.all(corrected[:-1, -1] > 0.0)

