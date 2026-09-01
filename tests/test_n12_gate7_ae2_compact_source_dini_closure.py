from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface.action_extension_ae2_compact_source_dini import (
    action_radius_regularity_audit,
    compact_source_dini_trace_norm_bound,
    holonomy_transfer_denominator_audit,
    smooth_compact_source_dini_bound,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_gate7_ae2_compact_source_dini_closure.py"
TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"


def test_bv_trace_norm_bound_is_finite_and_tail_independent() -> None:
    row = compact_source_dini_trace_norm_bound(
        source_interval_length=2.0,
        exp_minus_primitive_abs_upper=3.0,
        weighted_source_endpoint_abs=0.0,
        weighted_source_total_variation=5.0,
    )
    assert row["source_Dini_integral_upper"] == pytest.approx(90.0)
    assert row["far_tail_datum_used"] is False
    assert row["threshold_normalization_supremum_required"] is False


def test_smooth_local_bound_needs_no_tail_class() -> None:
    row = smooth_compact_source_dini_bound(
        superpotential_abs_upper=1.0,
        source_interval_length=0.5,
        source_abs_l1=0.25,
        source_derivative_abs_l1=0.75,
    )
    expected = 0.5 * math.exp(1.0) * (0.75 + 0.5)
    assert row["source_Dini_integral_upper"] == pytest.approx(expected)
    assert row["far_tail_datum_used"] is False


def test_action_audit_does_not_fabricate_global_radius_regularity() -> None:
    row = action_radius_regularity_audit()
    assert not any(row["global_tests_in_increasing_strength"].values())
    assert row["tail_regularization_needed_for_source_Dini"] is False


def test_pi_over_three_common_phase_leaves_transfer_denominator_invariant() -> None:
    row = holonomy_transfer_denominator_audit(math.pi / 3.0)
    assert row["admittance_residual"] < 1.0e-14
    assert row["norm_denominator_residual"] < 1.0e-14
    assert row["common_phase_changes_threshold_denominator"] is False
    assert row["holonomy_regularizes_threshold"] is False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"source_interval_length": 0.0, "exp_minus_primitive_abs_upper": 1.0, "weighted_source_endpoint_abs": 0.0, "weighted_source_total_variation": 1.0},
        {"source_interval_length": 1.0, "exp_minus_primitive_abs_upper": -1.0, "weighted_source_endpoint_abs": 0.0, "weighted_source_total_variation": 1.0},
    ],
)
def test_invalid_bv_inputs_fail(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        compact_source_dini_trace_norm_bound(**kwargs)


def test_artifact_is_validated_and_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["factorization_only_test"]["answer"] == "YES_WITHIN_THE_RETAINED_ADMISSIBLE_CLASS"
    assert payload["frontier_sharpening"]["G7_05_factorized_threshold"].startswith("CLOSED")
    assert payload["claim_boundary"]["angular_sum"] == "OPEN_CURRENT_OWNER"
    assert payload["FULL_BHSM_COMPLETE"] is False
