from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_c2_log_descriptor_multiple_shooting.py"


def _module():
    spec = importlib.util.spec_from_file_location("log_descriptor_shooting", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_log_descriptor_chart_is_exact_and_forward() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    witness = payload["core_formula_witness"]
    assert witness["signed_descriptor"] > 0.0
    assert witness["Delta"] > 0.0
    assert witness["proper_time_density_d_tau_d_log_s"] > 0.0
    assert np.isclose(
        witness["norm_reduction_factor"], witness["signed_descriptor"],
        rtol=1.0e-14, atol=0.0,
    )


def test_reconnaissance_stop_is_not_promoted() -> None:
    payload = _module().build_payload()
    assert payload["reconnaissance_boundary"]["promoted_to_certified_stop"] is False
    assert payload["claim_boundary"]["reset_to_capture_or_stop_certificate"] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["chord_03_authorized"] is False
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
