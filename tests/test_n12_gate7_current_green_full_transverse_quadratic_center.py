from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/certify_n12_gate7_current_green_full_transverse_quadratic_center.py"
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER.json"


def _module():
    spec = importlib.util.spec_from_file_location("full_transverse_center", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_complete_center_campaign_is_aggregated_at_512_bits() -> None:
    module = _module()
    payload = _payload()
    assert module.AGGREGATION_PRECISION == 512
    assert payload["aggregation_precision_bits"] == 512
    assert payload["validation_passed"] is True
    assert payload["coverage"] == {
        "endpoint_nodes": "1_THROUGH_370",
        "midpoint_intervals": "0_THROUGH_369",
        "coordinate_dimension": 74,
        "current_Green_complement_dimension": 73,
        "augmented_output_dimension": 99,
    }
    assert payload["validation"][
        "final_shard_aggregation_uses_512_bit_Arb_arithmetic"
    ] is True


def test_aggregate_data_and_center_owner_are_consistent() -> None:
    payload = _payload()
    data_path = ROOT / str(payload["data"])
    assert hashlib.sha256(data_path.read_bytes()).hexdigest().upper() == payload[
        "data_SHA256"
    ]
    with np.load(data_path) as source:
        endpoints = source["endpoint_rows"]
        midpoints = source["midpoint_rows"]
        fields = source["field_names"].tolist()
        endpoint_output = source["endpoint_output_Frobenius_norms"]
        midpoint_output = source["midpoint_output_Frobenius_norms"]
        assert endpoints.shape == (370, len(fields))
        assert midpoints.shape == (370, len(fields))
        assert endpoint_output.shape == (370, 99)
        assert midpoint_output.shape == (370, 99)
        assert source["all_node_output_Frobenius_majorant"].shape == (99,)
        qnorm = np.concatenate(
            (
                endpoints[:, fields.index("quadratic_Frobenius_norm")],
                midpoints[:, fields.index("quadratic_Frobenius_norm")],
            )
        )
    owner = int(np.argmax(qnorm))
    expected_owner = (
        {"kind": "endpoint", "index": owner + 1}
        if owner < 370
        else {"kind": "midpoint", "index": owner - 370}
    )
    assert payload["maximum_center_owner"] == expected_owner
    assert payload["maximum_center_transverse_quadratic_Frobenius_norm"] == qnorm[
        owner
    ]


def test_center_majorant_preserves_the_outward_claim_boundary() -> None:
    payload = _payload()
    boundary = payload["claim_boundary"]
    assert boundary[
        "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_CENTER_OPERATOR_DERIVED"
    ] is True
    assert boundary[
        "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_UNIT_SPHERE_CENTER_MAJORANT_DERIVED"
    ] is True
    assert boundary[
        "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_OUTWARD_REMAINDER_DERIVED"
    ] is False
    assert boundary[
        "CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED"
    ] is False
    assert boundary["CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
