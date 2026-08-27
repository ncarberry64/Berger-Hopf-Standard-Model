"""Checks for the exact DOP853 bordered-response center first variation."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"
RESPONSE = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_CERTIFICATE.json"
VARIATION = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RESPONSE_FIRST_VARIATION.json"
VARIATION_DATA = VARIATION.with_suffix(".npz")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def keys(payload: dict) -> list[tuple[int, int, int]]:
    return [
        (int(row["interval"]), int(row["subspan"]), int(row["subdivisions"]))
        for row in payload["rows"]
    ]


def test_first_variation_consumes_exact_response_cover() -> None:
    response = load(RESPONSE)
    variation = load(VARIATION)
    assert variation["validation_passed"] is True
    assert keys(variation) == keys(response)
    assert len(variation["rows"]) == 8692
    assert all(row["selected_branch"] == 24 for row in variation["rows"])
    assert all(row["all_center_quantities_finite"] for row in variation["rows"])
    assert variation["identity"] == "D_xi_x=K^-1*(D_xi_rhs-(D_xi_K)*x)"


def test_spectral_comparison_is_residual_conditioned() -> None:
    payload = load(VARIATION)
    for row in payload["rows"]:
        assert row["center_bordered_response_first_variation_residual_upper"] < 1.0e-7
        assert row["spectral_vs_direct_first_variation_discrepancy"] <= row[
            "spectral_vs_direct_comparison_backward_error_upper"
        ]
        assert 0.0 <= row["combined_before_norm_cancellation_ratio"] <= 1.0
    assert payload["summary"][
        "maximum_center_bordered_response_first_variation_2_norm"
    ] == 800.9692587386047
    assert payload["claim_boundary"]["cellwise_response_first_variation_tube"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"


def test_first_variation_vectors_and_hashes_match_disk() -> None:
    payload = load(VARIATION)
    with np.load(VARIATION_DATA) as data:
        assert data["bordered_response_center"].shape == (8692, 62)
        assert data["bordered_response_action_time_first_variation"].shape == (8692, 62)
        assert np.all(np.isfinite(data["bordered_response_center"]))
        assert np.all(np.isfinite(data["bordered_response_action_time_first_variation"]))
    assert normalized_sha256(VARIATION_DATA) == payload["data_SHA256"]
    for relative, expected in payload["inputs"].items():
        assert normalized_sha256(ROOT / relative) == expected
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["FLAGSHIP_READY"] is False
