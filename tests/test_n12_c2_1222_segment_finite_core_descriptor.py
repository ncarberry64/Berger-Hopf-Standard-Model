import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"


def test_1222_segment_exact_fiber_finite_core() -> None:
    payload = json.loads((
        BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["coefficient_path"]["segment_count"] == 1222
    assert payload["coefficient_path"]["node_count"] == 1223
    assert max(payload["coefficient_path"]["chronological_join_action_norm_residuals"]) == 0.0
    assert payload["endpoint_event_child_partition"]["far_core_edge_is_physical_endpoint"] is False
    assert payload["adjudication"]["finite_event_or_canonical_stop"] == "NOT_REACHED"
    with np.load(BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz") as data:
        assert data["C2_proof_center_nodes"].shape == (1223, 98)
        assert data["segment_proper_duration_interval"].shape == (1222, 2)
        assert np.all(data["segment_proper_duration_interval"][:, 0] > 0.0)
