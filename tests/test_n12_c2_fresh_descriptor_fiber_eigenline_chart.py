import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "flagship_integration"
    / "BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART.json"
)


def test_fresh_descriptor_fiber_chart_is_certified():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    radius = payload["radius_derivation"]
    assert payload["validation_passed"] is True
    assert payload["center"]["selected_branch"] == 24
    assert radius["selected_fresh_chart_radius"] > radius["incoming_endpoint_tube_upper"]
    assert radius["selected_chart_bounds"]["eigenline_gap_lower"] > 0.0
    assert payload["chart_semantics"]["arbitrary_normal_motion_allowed"] is False
    assert payload["chart_semantics"]["proof_chart_boundary_is_physical_stop"] is False
    assert payload["hindsight"]["obstruction_physical"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    with np.load(ROOT / payload["data"]) as data:
        assert data["selected_vector_derivative_action"].shape == (61, 98)
        assert data["fixed_descriptor_tangent_basis"].shape == (98, 97)
