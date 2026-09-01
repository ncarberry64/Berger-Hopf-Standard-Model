from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
MAPS = BASE / "BHSM_N12_GATE7_ARB_MAGNUS4_MACRO_MAPS.json"
AFFINE = BASE / "BHSM_N12_GATE7_ARB_MAGNUS4_AFFINE_COMPOSITION.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _assert_provenance(payload: dict[str, object]) -> None:
    for relative, digest in payload["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    assert _sha256(ROOT / payload["data"]) == payload["data_SHA256"]


def test_all_homogeneous_macro_maps_and_global_fundamental_are_outward() -> None:
    payload = json.loads(MAPS.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["identity"]["precision_bits"] == 256
    assert payload["identity"]["macro_maps"] == 47
    assert payload["identity"]["exponential_count"] == 5908
    assert payload["summary"]["maximum_macro_map_component_radius"] < 3.3e-57
    assert payload["summary"]["global_fundamental_component_radius_Frobenius"] < 2.7e-16
    assert payload["claim_boundary"]["finite_global_discrete_fundamental"] == "CERTIFIED"
    assert payload["claim_boundary"]["analytic_Magnus4_remainder"].startswith("OPEN")
    _assert_provenance(payload)
    with np.load(ROOT / payload["data"]) as data:
        assert data["macro_step_map_midpoint"].shape == (47, 73, 73)
        assert data["macro_step_map_component_radius"].shape == (47, 73, 73)
        assert np.all(np.isfinite(data["global_fundamental_component_radius"]))


def test_retained_signed_affine_blocks_compose_globally_without_wrapping() -> None:
    payload = json.loads(AFFINE.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["identity"]["source_precision_bits"] == 256
    assert payload["identity"]["composition_precision_bits"] == 256
    assert payload["identity"]["source_partition"] == "retained-unaligned"
    assert payload["identity"]["macro_blocks"] == 47
    assert payload["identity"]["exponential_count"] == 31019
    assert payload["summary"]["maximum_affine_source_component_radius"] < 9.6e-76
    assert payload["summary"]["maximum_global_response_Euclidean_radius"] < 1.1e-25
    assert payload["summary"]["maximum_reference_quotient_outward_difference"] < 1.6e-18
    assert payload["summary"]["maximum_stored_center_off_tangent_residue"] < 1.7e-21
    assert payload["claim_boundary"]["finite_global_correlated_block_composition"] == "CERTIFIED"
    assert payload["claim_boundary"]["analytic_Magnus4_remainder"].startswith("OPEN")
    assert payload["claim_boundary"]["outward_signed_Y"].startswith("OPEN")
    assert payload["FULL_BHSM_COMPLETE"] is False
    _assert_provenance(payload)
    with np.load(ROOT / payload["data"]) as data:
        assert data["affine_source_midpoint"].shape == (47, 73)
        assert data["global_signed_response_midpoint"].shape == (48, 73)
        assert data["global_signed_response_component_radius"].shape == (48, 73)
        assert data["global_signed_response_Euclidean_radius"][0] == 0.0
        assert np.all(np.isfinite(data["global_signed_response_component_radius"]))
