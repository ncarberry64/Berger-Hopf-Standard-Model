from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface.action_extension_ae2_angular_dini_uniformity import (
    angular_uniformity_requirement,
    exponential_radius_angular_counterexample,
    integrable_optical_tail_dini_coefficient_lower,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_gate7_ae2_angular_dini_uniformity.py"
TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"


def test_integrable_optical_tail_lower_bound_grows_exponentially() -> None:
    low = integrable_optical_tail_dini_coefficient_lower(
        angular_eigenvalue=3.0,
        reciprocal_radius_integral=1.0,
        initial_reciprocal_radius_upper=1.0,
        initial_interval_length=0.25,
        positive_source_reciprocal_integral=0.2,
    )
    high = integrable_optical_tail_dini_coefficient_lower(
        angular_eigenvalue=7.0,
        reciprocal_radius_integral=1.0,
        initial_reciprocal_radius_upper=1.0,
        initial_interval_length=0.25,
        positive_source_reciprocal_integral=0.2,
    )
    assert high["log_threshold_coefficient_lower"] - low["log_threshold_coefficient_lower"] == pytest.approx(8.0)
    assert low["fixed_channel_source_Dini_finite"] is True


def test_exponential_radius_is_a_smooth_nonpower_angular_counterexample() -> None:
    row = exponential_radius_angular_counterexample(10)
    assert row["radius_history"] == "R4(tau)=exp(tau)"
    assert row["log_radius_derivative"] == 1.0
    assert row["reciprocal_radius_integral"] == 1.0
    assert row["minimum_successive_log_term_increment"] > 2.0
    assert row["absolute_angular_source_Dini_sum_finite"] is False
    assert row["fixed_channel_source_Dini_finite_for_every_level"] is True


def test_optical_completeness_is_necessary_but_not_overclaimed_sufficient() -> None:
    row = angular_uniformity_requirement()
    assert row["finite_optical_length_excluded_by_angular_finiteness"] is True
    assert row["necessary_geometric_exclusion"].endswith("=infinity")
    assert row["optical_completeness_alone_proved_sufficient"] is False


def test_invalid_angular_inputs_fail() -> None:
    with pytest.raises(ValueError):
        integrable_optical_tail_dini_coefficient_lower(
            angular_eigenvalue=1.0,
            reciprocal_radius_integral=1.0,
            initial_reciprocal_radius_upper=1.0,
            initial_interval_length=0.25,
            positive_source_reciprocal_integral=0.2,
        )
    with pytest.raises(ValueError):
        exponential_radius_angular_counterexample(1)


def test_artifact_is_validated_and_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["fixed_channel_source_Dini"] == "CLOSED_DO_NOT_REOPEN"
    assert payload["adjudication"]["arbitrary_positive_tail_angular_sum"] == "FALSE"
    assert payload["frontier_sharpening"]["G7_07_angular_tail"] == "OPEN_CURRENT_OWNER"
    assert payload["FULL_BHSM_COMPLETE"] is False
