import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RECORD = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_MACRO_MAPS.json"
MAGNUS8 = BASE / "BHSM_N12_GATE7_ARB_MAGNUS8_MACRO_MAPS.npz"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_exact_affine_macro_map_certificate() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    assert record["validation_passed"] is True
    assert record["summary"]["macro_count"] == 47
    assert record["summary"]["substep_count"] == 5908
    assert record["summary"]["maximum_interaction_beta_upper"] < 0.022
    assert record["summary"]["maximum_local_exact_flow_error_upper"] < 1e-70
    assert record["summary"]["maximum_macro_map_component_radius"] < 1e-50
    assert (
        record["summary"][
            "global_exact_affine_fundamental_component_radius_Frobenius"
        ] < 3e-15
    )
    assert record["claim_boundary"]["homogeneous_exact_affine_macro_maps"] == (
        "CERTIFIED"
    )
    assert record["claim_boundary"]["signed_source_quadrature_Y"] == (
        "OPEN_INTERVAL_AUTHORITY"
    )
    assert record["FULL_BHSM_COMPLETE"] is False


def test_exact_affine_data_provenance_and_magnus8_crosscheck() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    data = ROOT / record["data"]
    assert _sha256(data) == record["data_SHA256"]
    for relative, digest in record["inputs"].items():
        assert _sha256(ROOT / relative) == digest
    with np.load(data) as exact, np.load(MAGNUS8) as magnus:
        exact_macro = exact["macro_step_map_midpoint"]
        magnus_macro = magnus["macro_step_map_midpoint"]
        assert exact_macro.shape == (47, 73, 73)
        assert np.array_equal(exact_macro, magnus_macro)
        exact_global = exact["global_exact_affine_fundamental_midpoint"]
        magnus_global = magnus["global_fundamental_midpoint"]
        assert np.array_equal(exact_global, magnus_global)
        outward = (
            np.linalg.norm(
                exact["global_exact_affine_fundamental_component_radius"]
            )
            + np.linalg.norm(magnus["global_fundamental_component_radius"])
        )
        assert outward < 3.21e-15
