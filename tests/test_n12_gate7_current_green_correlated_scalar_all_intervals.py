import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS.json"
HIGH_PRECISION_ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS_512BIT.json"


def test_all_correlated_scalar_intervals_are_finite_and_fail_closed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    assert payload["intervals_certified"] == 370
    assert payload["claim_boundary"]["CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS_DERIVED"]
    assert not payload["claim_boundary"][
        "CURRENT_GREEN_AXIS_NEIGHBORHOOD_MIXED_TRANSVERSE_BOUND_DERIVED"
    ]
    assert not payload["claim_boundary"][
        "CURRENT_CENTER_GREEN_CAUSAL_TWO_RADIUS_CERTIFICATE_DERIVED"
    ]


def test_global_data_preserves_finite_curvatures_and_axis_errors():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    with np.load(ROOT / payload["data"]) as data:
        for name in ("intrinsic", "incidence", "total", "local_hs"):
            values = data[f"{name}_norm_upper"]
            assert values.shape == (370,)
            assert np.all(np.isfinite(values))
        errors = data["axis_error_upper"]
        assert errors.shape == (371,)
        assert errors[0] == 0.0
        assert np.all(np.isfinite(errors[1:]))
        assert np.all(errors[1:] > 0.0)
        assert int(data["precision_bits"]) == 384
        assert data["local_hs_arb"].shape == (370, 99)


def test_512_bit_operand_repeats_the_same_scalar_without_model_changes():
    payload = json.loads(HIGH_PRECISION_ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    assert payload["intervals_certified"] == 370
    assert payload["claim_boundary"][
        "CURRENT_GREEN_CORRELATED_SCALAR_ALL_INTERVALS_DERIVED"
    ]
    with np.load(ROOT / payload["data"]) as data:
        assert int(data["precision_bits"]) == 512
        assert data["local_hs_arb"].shape == (370, 99)
    assert hashlib.sha256((ROOT / payload["data"]).read_bytes()).hexdigest().upper() == payload[
        "data_SHA256"
    ]


def test_interval355_reproduces_the_correlation_reconciliation_seed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation"][
        "interval355_seed_sharply_enclosed_after_exact_Arb_shard_transport"
    ]
