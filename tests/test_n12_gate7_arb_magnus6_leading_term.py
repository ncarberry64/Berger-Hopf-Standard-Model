from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
MAPS = BASE / "BHSM_N12_GATE7_ARB_MAGNUS6_MACRO_MAPS.json"
AFFINE = BASE / "BHSM_N12_GATE7_ARB_MAGNUS6_AFFINE_COMPOSITION.json"
AUDIT = BASE / "BHSM_N12_GATE7_ARB_MAGNUS6_LEADING_TERM_AUDIT.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _assert_provenance(payload: dict[str, object]) -> None:
    for relative, digest in payload["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    assert _sha256(ROOT / payload["data"]) == payload["data_SHA256"]


def test_magnus6_maps_and_affine_source_blocks_are_outward() -> None:
    maps = json.loads(MAPS.read_text(encoding="utf-8"))
    affine = json.loads(AFFINE.read_text(encoding="utf-8"))
    assert maps["validation_passed"] is True
    assert maps["identity"]["Magnus_order"] == 6
    assert maps["identity"]["precision_bits"] == 256
    assert maps["identity"]["exponential_count"] == 5908
    assert maps["summary"]["maximum_macro_map_component_radius"] < 3.9e-57
    assert affine["validation_passed"] is True
    assert affine["identity"]["Magnus_order"] == 6
    assert affine["identity"]["exponential_count"] == 31019
    assert affine["summary"]["maximum_affine_source_component_radius"] < 1.2e-75
    assert affine["summary"]["maximum_global_response_Euclidean_radius"] < 1.2e-25
    _assert_provenance(maps)
    _assert_provenance(affine)


def test_finite_omega5_shift_is_certified_without_promoting_higher_tail() -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["summary"]["maximum_finite_Omega5_augmented_outward_shift"] < 5.8e-20
    assert payload["summary"]["maximum_combined_evaluation_radius"] < 2.3e-25
    assert payload["summary"]["finite_Omega5_shift_cone_reserve_factor"] > 9.0e6
    assert payload["claim_boundary"]["finite_Omega5_augmented_operator"] == "CERTIFIED"
    assert payload["claim_boundary"]["Omega7_and_higher_analytic_remainder"].startswith("OPEN")
    assert payload["claim_boundary"]["outward_signed_Y"].startswith("OPEN")
    assert payload["FULL_BHSM_COMPLETE"] is False
    _assert_provenance(payload)
    with np.load(ROOT / payload["data"]) as data:
        assert data["Magnus6_minus_Magnus4_outward_2_norm"].shape == (48,)
        assert np.all(np.isfinite(data["combined_outward_evaluation_radius"]))
