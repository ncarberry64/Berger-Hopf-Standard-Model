from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
MAPS = BASE / "BHSM_N12_GATE7_ARB_MAGNUS8_MACRO_MAPS.json"
AFFINE = BASE / "BHSM_N12_GATE7_ARB_MAGNUS8_AFFINE_COMPOSITION.json"
AUDIT = BASE / "BHSM_N12_GATE7_ARB_MAGNUS8_LEADING_TERM_AUDIT.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _assert_provenance(payload: dict[str, object]) -> None:
    for relative, digest in payload["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    assert _sha256(ROOT / payload["data"]) == payload["data_SHA256"]


def test_magnus8_maps_and_affine_source_blocks_are_outward() -> None:
    maps = json.loads(MAPS.read_text(encoding="utf-8"))
    affine = json.loads(AFFINE.read_text(encoding="utf-8"))
    assert maps["validation_passed"] is True
    assert maps["identity"]["Magnus_order"] == 8
    assert maps["identity"]["precision_bits"] == 256
    assert maps["summary"]["maximum_macro_map_component_radius"] < 4.5e-57
    assert affine["validation_passed"] is True
    assert affine["identity"]["Magnus_order"] == 8
    assert affine["identity"]["exponential_count"] == 31019
    assert affine["summary"]["maximum_affine_source_component_radius"] < 1.4e-75
    assert affine["summary"]["maximum_global_response_Euclidean_radius"] < 1.4e-25
    _assert_provenance(maps)
    _assert_provenance(affine)


def test_finite_omega7_has_an_outward_bound_not_an_exact_zero_claim() -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["summary"]["maximum_finite_Omega7_augmented_outward_bound"] < 2.5e-25
    assert payload["summary"]["maximum_stored_midpoint_difference"] == 0.0
    assert payload["summary"]["finite_Omega7_bound_cone_reserve_factor"] > 1.0e12
    assert payload["claim_boundary"]["finite_Omega7_augmented_operator"].startswith("CERTIFIED")
    assert payload["claim_boundary"]["Omega9_and_higher_analytic_remainder"].startswith("OPEN")
    assert payload["claim_boundary"]["outward_signed_Y"].startswith("OPEN")
    assert payload["FULL_BHSM_COMPLETE"] is False
    _assert_provenance(payload)
    with np.load(ROOT / payload["data"]) as data:
        assert data["Magnus8_minus_Magnus6_outward_2_norm"].shape == (48,)
        assert np.all(np.isfinite(data["combined_outward_evaluation_radius"]))
