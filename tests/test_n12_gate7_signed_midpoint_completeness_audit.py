from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "midpoint_completeness_audit",
    ROOT / "scripts/audit_n12_gate7_signed_midpoint_completeness.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_retained_diagnostics_show_the_problem_at_every_midpoint():
    result = MODULE.build_payload()
    assert result["validation_passed"]
    assert result[
        "all_retained_midpoints_have_nonzero_longitudinal_and_normal_components"
    ]
    longitudinal = result["midpoint_longitudinal_coordinate_operator_norm"]
    assert longitudinal["nonzero_count"] == 370
    assert longitudinal["maximum"] > 1.0
    assert result["midpoint_normal_operator_norm"]["minimum"] > 0.0
    assert not any(result["claim_boundary"].values())


def test_audit_rejects_changed_source_bytes(tmp_path):
    changed = tmp_path / "changed.npz"
    changed.write_bytes(MODULE.DATA.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        MODULE.build_payload(data_path=changed)


def test_audit_rejects_unvalidated_source(tmp_path):
    source = json.loads(MODULE.SOURCE.read_text())
    source["validation_passed"] = False
    changed = tmp_path / "source.json"
    changed.write_text(json.dumps(source))
    with pytest.raises(ValueError, match="validated source"):
        MODULE.build_payload(source_path=changed)


@pytest.mark.parametrize("invalid", [
    np.ones(369), np.full(370, np.nan), np.full(370, np.inf),
    np.full(370, -1.0),
])
def test_partial_or_invalid_diagnostics_fail_closed(invalid):
    with pytest.raises(ValueError):
        MODULE.summarize_diagnostic(invalid)


def test_counterexample_is_exact_and_not_an_actual_hessian_error():
    witness = MODULE.exact_complement_witness()
    assert witness["arithmetic"] == "EXACT_RATIONAL"
    assert witness["endpoint_axis_dot_input"] == 0
    assert witness["midpoint_axis_component"] == 1
    assert witness["full_quadratic"] == 1
    assert witness["transverse_only_quadratic"] == 0
    assert "NOT_A_BHSM_ACTION_EVALUATION" in witness["scope"]
