from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_gate7_current_green_mixed_bilinear_equivalence.py"
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_EQUIVALENCE_AUDIT.json"


def _payload():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_bilinear_centers_reproduce_independent_polarization_seeds() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["maximum_center_absolute_difference"] < 1.0e-8
    assert payload["maximum_center_scaled_difference"] < 1.0e-9
    assert payload["seed_nodes"] == [1, 355, 356, 370]
    assert payload["seed_columns"] == [0, 1, 61]


def test_nonoverlapping_interval_graphs_remain_fail_closed() -> None:
    payload = _payload()
    assert payload["all_component_interval_hulls_overlap"] is False
    assert payload["claim_boundary"][
        "CURRENT_GREEN_MIXED_DIRECT_BILINEAR_OUTWARD_EQUIVALENCE_DERIVED"
    ] is False
    assert payload["claim_boundary"][
        "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS_DERIVED"
    ] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_materializer_declares_all_hashed_inputs() -> None:
    spec = importlib.util.spec_from_file_location("mixed_bilinear_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    payload = _payload()
    assert set(payload["inputs"]) == {
        module._relative(path) for path in module.INPUTS
    }
