from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface.action_extension_ae2_factorized_source_measure import (
    endpoint_threshold_dichotomy,
    exact_constant_resonance_coefficient,
    resonant_transfer_majorant,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_gate7_ae2_factorized_source_measure_reduction.py"
TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json"


def test_exact_constant_transfer_derivative_recovers_prior_coefficient() -> None:
    exact = exact_constant_resonance_coefficient(2.0, 0.75)
    assert exact["first_form_weight_over_k_squared_limit"] == pytest.approx(6.552579915052088)
    assert exact["cumulative_measure_over_Lambda_to_three_halves_limit"] == pytest.approx(6.552579915052088 / 3.0)


def test_majorant_is_superlinear_and_dominates_exact_model() -> None:
    exact = exact_constant_resonance_coefficient(2.0, 0.75)
    bound = resonant_transfer_majorant(2.0, 0.75, 1.0, exact["threshold_delta_normalization_squared"])
    assert bound["source_measure_excess_exponent"] == 0.5
    assert bound["first_form_weight_over_k_squared_upper"] >= exact["first_form_weight_over_k_squared_limit"]


def test_endpoint_dichotomy_only_leaves_infinite_normalization() -> None:
    finite = endpoint_threshold_dichotomy(finite_regular_or_canonical_stop=True, infinite_end_threshold_normalization_bound_available=False)
    infinite = endpoint_threshold_dichotomy(finite_regular_or_canonical_stop=False, infinite_end_threshold_normalization_bound_available=False)
    assert finite["remaining_input"] is None
    assert infinite["remaining_input"] == "FINITE_UNIFORM_NEAR_THRESHOLD_SUM_OF_SQUARED_GENERALIZED_EIGENSTATE_NORMALIZATIONS"
    assert not infinite["strict_gap_required"]
    assert not infinite["full_operator_norm_limiting_absorption_required"]


def test_invalid_majorant_inputs_fail() -> None:
    with pytest.raises(ValueError):
        resonant_transfer_majorant(-1.0, 1.0, 1.0, 1.0)


def test_artifact_is_validated_and_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["abstract_factorized_transfer_to_source_measure_theorem"] == "CLOSED"
    assert payload["claim_boundary"]["actual_N12_infinite_end_threshold_normalization"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
