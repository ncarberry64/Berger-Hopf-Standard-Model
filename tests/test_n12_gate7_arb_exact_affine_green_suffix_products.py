from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
SUFFIX = BASE / "BHSM_N12_GATE7_ARB_EXACT_AFFINE_GREEN_SUFFIX_PRODUCTS.json"
SUFFIX_DATA = SUFFIX.with_suffix(".npz")
BOOTSTRAP = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_SIGNED_CAUSAL_VECTOR_BOOTSTRAP.json"
CAUSAL = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_CAUSAL_VECTOR_CERTIFICATE.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_all_correlated_arb_suffix_products_close() -> None:
    payload = _load(SUFFIX)
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    summary = payload["summary"]
    assert summary["suffix_product_count"] == 1128
    assert summary["maximum_suffix_product_Frobenius_upper"] < 1.0e4
    assert summary["maximum_suffix_product_export_radius_Frobenius"] < 1.0e-10


def test_suffix_array_is_strictly_causal_and_finite() -> None:
    with np.load(SUFFIX_DATA) as source:
        upper = np.asarray(source["suffix_product_Frobenius_upper"])
        radius = np.asarray(source["suffix_product_export_radius_Frobenius"])
    assert upper.shape == (48, 48)
    assert np.count_nonzero(upper) == 1128
    assert np.allclose(np.triu(upper), 0.0, atol=0.0, rtol=0.0)
    assert np.all(np.isfinite(upper))
    assert np.all(radius >= 0.0)


def test_suffix_code_provenance_is_current() -> None:
    payload = _load(SUFFIX)
    relative = "scripts/certify_n12_gate7_arb_exact_affine_green_suffix_products.py"
    assert payload["inputs"][relative] == _sha256(ROOT / relative)


def test_correlated_suffix_replay_closes_exact_center_radius_only() -> None:
    bootstrap = _load(BOOTSTRAP)
    causal = _load(CAUSAL)
    assert bootstrap["validation_passed"] is True
    assert bootstrap["summary"]["maximum_exact_carrier_source_radius"] < 1.0e-20
    assert bootstrap["summary"]["maximum_outward_causal_Green_norm"] < 2.0e4
    assert causal["validation_passed"] is True
    assert causal["summary"]["maximum_exact_total_center_radius"] < 1.0e-12
    boundary = causal["claim_boundary"]
    assert boundary["exact_action_center_causal_vector_radius"] == "DERIVED_CENTER_ONLY"
    assert boundary["outward_exact_affine_Green_suffix_products"] == "CERTIFIED"
    assert boundary["outward_signed_nonlinear_source_remainder"] == "OPEN"
    assert boundary["outward_D5_curvature_remainder"] == "OPEN"
    assert boundary["causal_interval_vector_radius"] == "OPEN"
    assert boundary["FULL_BHSM_COMPLETE"] is False
