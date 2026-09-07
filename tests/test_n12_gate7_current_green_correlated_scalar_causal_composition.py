import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_CAUSAL_COMPOSITION.json"


def test_central_scalar_causal_composition_is_finite_and_fail_closed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    assert payload["nodes_composed"] == 371
    assert payload["intervals_composed"] == 370
    assert payload["claim_boundary"][
        "CURRENT_GREEN_CORRELATED_CENTRAL_SCALAR_CAUSAL_COMPOSITION_DERIVED"
    ]
    assert payload["claim_boundary"][
        "CURRENT_GREEN_CENTRAL_SCALAR_RECURSIVE_CAUSAL_ENCLOSURE_DERIVED"
    ]
    assert payload["first_recursive_wrapping_node"] is None
    assert not payload["claim_boundary"][
        "CURRENT_GREEN_EXACT_AXIS_NEIGHBORHOOD_CAUSAL_COMPOSITION_DERIVED"
    ]
    assert not payload["claim_boundary"][
        "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"
    ]


def test_causal_data_covers_reset_through_terminal_node():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    with np.load(ROOT / payload["data"]) as data:
        values = data["causal_central_scalar_curvature_norm_upper"]
        assert values.shape == (371,)
        assert values[0] == 0.0
        assert np.all(np.isfinite(values))
        assert np.all(values >= 0.0)
        assert int(data["precision_bits"]) == 512
    assert hashlib.sha256((ROOT / payload["data"]).read_bytes()).hexdigest().upper() == payload[
        "data_SHA256"
    ]
