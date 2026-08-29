from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_CAUSAL_Y_Z1_Z2_MARGIN_BUDGET_AUDIT.json"
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_causal_proxy_budget_vanishes_at_reset_and_has_margin_headroom() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["outward_signed_Y"] == "OPEN_INTERVAL_AUTHORITY"
    assert payload["claim_boundary"]["outward_PROP16_Z1"] == "OPEN_INTERVAL_AUTHORITY"
    assert payload["claim_boundary"]["shifted_scalar_first_hit"] == "OPEN"
    assert payload["summary"]["certified_proxy_inflation_factor_lower"] > 200.0
    assert payload["summary"]["maximum_combined_state_proxy_radius"] < 7.3e-13
    for relative, digest in payload["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    assert _sha256(ROOT / payload["data"]) == payload["data_SHA256"]

    with np.load(ROOT / payload["data"]) as data:
        total = data["combined_state_proxy_radius"]
        y_radius = data["causal_signed_Y_proxy_radius"]
        z1_radius = data["causal_PROP_Z1_proxy_radius"]
        z2_radius = data["interpolated_causal_Z2_radius"]
        assert total.shape == y_radius.shape == z1_radius.shape == z2_radius.shape == (371,)
        assert total[0] == y_radius[0] == z1_radius[0] == z2_radius[0] == 0.0
        assert np.all(np.diff(y_radius) >= 0.0)
        assert np.all(np.diff(z1_radius) >= 0.0)


def test_prop32_replay_keeps_the_claim_boundary_numerical() -> None:
    path = ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_PROP32_AUDIT.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["artifact"].endswith("PROP32_AUDIT")
    assert payload["identity"]["propagator_substeps_per_quarter_cell"] == 32
    assert payload["claim_boundary"]["outward_interval_Y_and_Z1"] == "OPEN"
    assert payload["validation"]["not_relabelled_as_interval_propagator_authority"] is True

