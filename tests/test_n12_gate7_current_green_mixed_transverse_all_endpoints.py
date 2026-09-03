from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/certify_n12_gate7_current_green_mixed_transverse_all_endpoints.py"
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS.json"


def _module():
    spec = importlib.util.spec_from_file_location("mixed_all_endpoints", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _payload() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_defined_post_reset_green_axes_are_surveyed() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["total_center_endpoints"] == 371
    assert payload["post_reset_endpoints_with_defined_green_axis"] == 370
    assert payload["excluded_birth_node"] == 0
    assert [row["node"] for row in payload["rows"]] == list(range(1, 371))
    assert payload["precision_bits_node_counts"] == {"192": 290, "512": 80}
    assert payload["measured_192_bit_continuation_CPU_hours"] > 0.0
    assert all(
        row["elapsed_seconds"] is not None
        for row in payload["rows"] if row["precision_bits"] == 192
    )
    assert payload["claim_boundary"][
        "CURRENT_GREEN_MIXED_DIRECT_BILINEAR_ALL_ENDPOINT_CENTERS_MATERIALIZED"
    ] is True
    assert payload["validation"][
        "legacy_512_bit_checkpoint_manifest_is_valid"
    ]
    assert payload["validation"][
        "adaptive_precision_and_worker_benchmark_is_valid"
    ]


def test_reconnaissance_does_not_promote_outward_mixed_authority() -> None:
    payload = _payload()
    assert payload["claim_boundary"][
        "CURRENT_GREEN_MIXED_DIRECT_BILINEAR_OUTWARD_EQUIVALENCE_DERIVED"
    ] is False
    assert payload["claim_boundary"][
        "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS_DERIVED"
    ] is False
    assert payload["claim_boundary"][
        "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"
    ] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_aggregate_arrays_and_owner_are_consistent() -> None:
    payload = _payload()
    data = ROOT / str(payload["data"])
    assert hashlib.sha256(data.read_bytes()).hexdigest().upper() == payload[
        "data_SHA256"
    ]
    with np.load(data) as source:
        assert source["mixed_direct_bilinear_mid"].shape == (370, 99, 74)
        assert source["mixed_direct_bilinear_radius"].shape == (370, 99, 74)
        assert source["post_reset_nodes"].tolist() == list(range(1, 371))
    owner = max(
        payload["rows"], key=lambda row: row["mixed_direct_graph_Frobenius_upper"]
    )
    assert payload["maximum_direct_graph_owner_node"] == owner["node"]
    assert payload["maximum_direct_graph_Frobenius_upper"] == owner[
        "mixed_direct_graph_Frobenius_upper"
    ]
    radius_owner = max(
        payload["rows"], key=lambda row: row["maximum_direct_graph_component_radius"]
    )
    assert payload["maximum_direct_graph_component_radius_owner_node"] == radius_owner[
        "node"
    ]
    assert payload["maximum_direct_graph_component_radius"] == radius_owner[
        "maximum_direct_graph_component_radius"
    ]


def test_materializer_declares_current_hashed_inputs() -> None:
    module = _module()
    payload = _payload()
    assert set(payload["inputs"]) == {
        module._relative(path) for path in module.INPUTS
    }
