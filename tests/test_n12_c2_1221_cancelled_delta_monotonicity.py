from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "certify_n12_c2_1221_cancelled_delta_monotonicity.py"


def test_realized_cover_delta_is_positive_and_descriptor_interval_sharpens() -> None:
    spec = importlib.util.spec_from_file_location("delta_monotonicity", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.build_payload()
    assert payload["validation_passed"] is True
    assert payload["Delta_interval_on_realized_cover"][0] > 0.0
    assert (
        payload["sharpened_correlated_descriptor_interval"][0]
        > payload["independent_wrapped_descriptor_interval_superseded"][0]
    )
    assert payload["adjudication"]["Delta_turning_point_reached"] is False
    assert payload["adjudication"]["event_or_canonical_stop_reached"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False

