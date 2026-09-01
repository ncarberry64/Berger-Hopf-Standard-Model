from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from bhsm.interface.constraint_projected_replacement_saddle import (
    bordered_kkt_correction,
    constraint_tangent_basis,
    kkt_force_decomposition,
    linearized_tangent_correction,
    projected_force,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_constraint_projected_replacement_saddle.py"
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json"
)


def _payload() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_tangent_basis_and_projected_force_are_exact_for_simple_constraint() -> None:
    jacobian = np.asarray([[1.0, 1.0, 0.0]])
    basis = constraint_tangent_basis(jacobian)
    assert basis.shape == (3, 2)
    assert np.linalg.norm(jacobian @ basis) < 1.0e-14
    force = np.asarray([1.0, 1.0, 3.0])
    result = projected_force(force, jacobian)
    assert result["tangent_norm"] == pytest.approx(3.0)
    assert np.linalg.norm(result["normal_component"] - [1.0, 1.0, 0.0]) < 1.0e-14


def test_nonzero_normal_force_is_only_a_multiplier_shift() -> None:
    jacobian = np.asarray([[1.0, -2.0, 0.5], [0.0, 1.0, 1.0]])
    multiplier = np.asarray([0.7, -0.2])
    force = jacobian.T @ multiplier
    result = kkt_force_decomposition(force, jacobian)
    assert result["ambient_norm"] > 0.0
    assert result["tangent_norm"] < 1.0e-14
    assert result["normal_absorption_residual_norm"] < 1.0e-14
    assert result["shifted_force_minus_tangent_residual_norm"] < 1.0e-14


def test_complex_adjoint_convention_is_respected() -> None:
    jacobian = np.asarray([[1.0 + 1.0j, 2.0 - 0.5j, -0.3j]])
    multiplier = np.asarray([0.8 - 0.2j])
    force = jacobian.conj().T @ multiplier
    result = kkt_force_decomposition(force, jacobian)
    assert result["tangent_norm"] < 1.0e-13
    assert result["normal_absorption_residual_norm"] < 1.0e-13


def test_linearized_correction_solves_projected_newton_equation() -> None:
    jacobian = np.asarray([[1.0, 0.0, 1.0]])
    hessian = np.diag([2.0, 3.0, 4.0])
    force = np.asarray([0.2, -0.7, 1.1])
    result = linearized_tangent_correction(hessian, force, jacobian)
    assert result["positive_definite_on_tangent"] is True
    assert result["center_eigenvalue_count"] == 0
    assert result["projected_linearized_residual_norm"] < 1.0e-14


def test_bordered_and_nullspace_corrections_agree_without_hessian_inverse() -> None:
    jacobian = np.asarray([[1.0, 0.0, 1.0], [0.0, 1.0, -1.0]])
    hessian = np.asarray(
        [[2.0, 0.2, 0.0], [0.2, 3.0, -0.1], [0.0, -0.1, 4.0]]
    )
    force = np.asarray([0.2, -0.7, 1.1])
    quotient = linearized_tangent_correction(hessian, force, jacobian)
    bordered = bordered_kkt_correction(hessian, force, jacobian)
    assert np.linalg.norm(
        quotient["ambient_correction"] - bordered["ambient_correction"]
    ) < 1.0e-14
    assert bordered["stationarity_residual_norm"] < 1.0e-14
    assert bordered["constraint_residual_norm"] < 1.0e-14


def test_linearized_correction_rejects_center_or_nonhermitian_hessian() -> None:
    jacobian = np.asarray([[1.0, 0.0, 0.0]])
    with pytest.raises(np.linalg.LinAlgError, match="not certified invertible"):
        linearized_tangent_correction(
            np.diag([1.0, 0.0, 2.0]), np.ones(3), jacobian
        )
    with pytest.raises(ValueError, match="Hermitian"):
        linearized_tangent_correction(
            np.asarray([[1.0, 0.0, 0.0], [0.0, 1.0, 2.0], [0.0, 0.0, 1.0]]),
            np.ones(3),
            jacobian,
        )


def test_actual_n12_reset_fiber_adjudication_is_conservative() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    witness = payload["actual_N12_reset_witness"]
    assert witness["raw_constraint_tangent_dimension"] == 67
    assert payload["existing_quotient_audit"][
        "after_existing_whole_system_time_quotient_dimension"
    ] == 66
    assert payload["existing_quotient_audit"][
        "raw_nullspace_crosscheck_is_final_physical_quotient"
    ] is False
    assert payload["existing_quotient_audit"][
        "common_scale_center_removed_as_exact_gauge"
    ] is False
    assert witness["boundary_log_R4_covector_tangent_projection_norm"] > 0.18
    assert payload["claim_boundary"][
        "constraint_tangent_force_criterion"
    ] == "DERIVED"
    assert payload["claim_boundary"]["actual_projected_force_value"] == "OPEN"
    assert payload["claim_boundary"]["same_action_saddle"] == (
        "OPEN_COUPLED_TO_FORCE"
    )
    assert payload["FULL_BHSM_COMPLETE"] is False
