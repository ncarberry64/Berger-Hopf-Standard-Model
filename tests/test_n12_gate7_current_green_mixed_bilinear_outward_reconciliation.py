from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/certify_n12_gate7_current_green_mixed_bilinear_outward_reconciliation.py"
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_OUTWARD_RECONCILIATION.json"


def _module():
    spec = importlib.util.spec_from_file_location("mixed_outward", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_common_hull_helper_contains_both_directed_inputs() -> None:
    module = _module()
    left_mid = np.asarray([1.0, -3.0, 1.0e10])
    left_radius = np.asarray([1.0e-16, 4.0e-16, 2.0e-7])
    right_mid = np.asarray([1.0 + 1.0e-12, -3.0 - 1.0e-9, 1.0e10 + 1.0e-3])
    right_radius = np.asarray([2.0e-16, 2.0e-16, 3.0e-7])
    midpoint, radius = module._hull(
        left_mid, left_radius, right_mid, right_radius,
    )
    assert module._contains(midpoint, radius, left_mid, left_radius)
    assert module._contains(midpoint, radius, right_mid, right_radius)


def test_exact_identity_and_common_outward_graph_are_reconciled() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["seed_nodes"] == [1, 355, 356, 370]
    assert payload["seed_columns_reconciled_per_node"] == 74
    assert payload["owner_polarization_precision_bits"] == 512
    assert payload["maximum_seed_center_absolute_difference"] < 1.0e-8
    assert payload["maximum_seed_center_scaled_difference"] < 1.0e-9
    assert (
        payload[
            "maximum_owner_leading_direction_center_absolute_difference"
        ]
        < 1.0e-8
    )
    assert (
        payload[
            "maximum_owner_leading_direction_center_scaled_difference"
        ]
        < 1.0e-9
    )
    assert payload["claim_boundary"][
        "CURRENT_GREEN_MIXED_DIRECT_BILINEAR_OUTWARD_EQUIVALENCE_DERIVED"
    ] is True
    assert payload["claim_boundary"][
        "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS_DERIVED"
    ] is True


def test_promotion_stops_before_midpoints_and_two_radius_theorem() -> None:
    payload = _payload()
    assert payload["claim_boundary"][
        "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_MIDPOINTS_DERIVED"
    ] is False
    assert payload["claim_boundary"][
        "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"
    ] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_persisted_common_hulls_contain_both_graphs() -> None:
    payload = _payload()
    data = ROOT / str(payload["data"])
    assert hashlib.sha256(data.read_bytes()).hexdigest().upper() == payload[
        "data_SHA256"
    ]
    with np.load(data) as source:
        for prefix in ("seed", "owner"):
            hull_mid = source[f"{prefix}_common_hull_mid"]
            hull_radius = source[f"{prefix}_common_hull_radius"]
            for route in ("direct", "polarization"):
                mid = source[f"{prefix}_{route}_mid"]
                radius = source[f"{prefix}_{route}_radius"]
                assert np.all(np.abs(mid - hull_mid) + radius <= hull_radius)


def test_materializer_declares_current_hashed_inputs() -> None:
    module = _module()
    payload = _payload()
    assert set(payload["inputs"]) == {
        module._relative(path) for path in module.INPUTS
    }
