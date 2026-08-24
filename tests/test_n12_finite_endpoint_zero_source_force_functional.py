from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from bhsm.interface.forward_finite_endpoint_heat_force import (
    direct_sum_heat_value_and_force,
    heat_regulator_value_and_force,
)
from scripts.derive_n12_finite_endpoint_zero_source_force_functional import (
    basis_covariance_witness,
    build_payload,
    finite_difference_witness,
    historical_operator_level_witness,
    reset_fiber_geometry_variation_witness,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_finite_endpoint_zero_source_force_functional.py"
TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
)


def test_exact_force_matches_noncommuting_finite_difference() -> None:
    assert finite_difference_witness()["absolute_residual"] < 1.0e-10


def test_force_is_basis_covariant() -> None:
    assert max(basis_covariance_witness().values()) < 1.0e-12


def test_historical_engine_matches_only_at_shared_operator_level() -> None:
    assert historical_operator_level_witness()["maximum_force_residual"] < 1.0e-12


def test_reset_fiber_does_not_hold_geometry_fixed() -> None:
    witness = reset_fiber_geometry_variation_witness()
    assert witness["fixed_event_child_fiber_dimension"] == 67
    assert witness["child_q_variation_rank_on_fiber"] == 33
    assert witness[
        "child_q_variation_rank_after_any_one_dimensional_time_quotient_lower"
    ] == 32
    assert witness["boundary_log_R4_covector_projection_norm"] > 0.18
    assert witness["unit_fiber_direction_constraint_residual"] < 1.0e-10


def test_direct_sum_coefficients_are_applied_exactly() -> None:
    operator = np.diag([1.5, 2.0])
    jet = np.diag([0.2, -0.1])
    single = heat_regulator_value_and_force(operator, {"h": jet})
    result = direct_sum_heat_value_and_force([
        {"operator": operator, "geometry_jets": {"h": jet}, "coefficient": 3.0},
        {"operator": operator, "geometry_jets": {"h": jet}, "coefficient": -1.0},
    ])
    assert result["Gamma_heat"] == pytest.approx(2.0 * single["Gamma_heat"])
    assert result["forces"]["h"] == pytest.approx(2.0 * single["forces"]["h"])


def test_nonpositive_or_nonhermitian_operator_is_rejected() -> None:
    with pytest.raises(ValueError, match="strictly positive"):
        heat_regulator_value_and_force(np.diag([0.0, 1.0]), {})
    with pytest.raises(ValueError, match="Hermitian"):
        heat_regulator_value_and_force(np.asarray([[2.0, 1.0], [0.0, 2.0]]), {})


def test_current_value_is_not_fabricated_and_artifact_is_deterministic() -> None:
    payload = build_payload()
    audit = payload["current_realization_audit"]
    assert audit["therefore_current_force_value_or_sign_evaluated"] is False
    assert payload["historical_transfer_boundary"]["periodic_force_value_promoted"] is False
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
    assert json.loads(TARGET.read_text(encoding="utf-8"))["validation_passed"] is True
