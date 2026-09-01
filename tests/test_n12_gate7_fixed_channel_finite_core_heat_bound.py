from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.linalg import eigh

from bhsm.interface.aether_forward_c2_finite_core_descriptor import (
    assemble_finite_core_descriptor,
)
from bhsm.interface.forward_finite_endpoint_heat_force import (
    finite_core_heat_trace_log_upper_bound,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_FIXED_CHANNEL_FINITE_CORE_HEAT_BOUND.json"


def _dense(diagonal: np.ndarray, off: np.ndarray) -> np.ndarray:
    return np.diag(diagonal) + np.diag(off, 1) + np.diag(off, -1)


def test_log_bound_encloses_small_scalar_descriptor_trace() -> None:
    duration = np.asarray([0.2, 0.25])
    descriptor = assemble_finite_core_descriptor(
        log_radii=np.asarray([0.0, 0.02, 0.01]),
        proper_durations=duration,
        channel="scalar",
        unit_channel_value=3.0,
    )
    eigenvalues = eigh(
        _dense(descriptor["K_diagonal"], descriptor["K_off_diagonal"]),
        _dense(descriptor["M_diagonal"], descriptor["M_off_diagonal"]),
        eigvals_only=True,
    )
    actual_log = float(np.log(np.sum(np.exp(-eigenvalues))))
    bound = finite_core_heat_trace_log_upper_bound(
        dimension=descriptor["dimension"],
        proper_duration_upper=float(np.sum(duration)),
        scalar_potential_lower=float(np.min(descriptor["element_coefficient"])),
    )
    assert actual_log <= bound["log_heat_trace_upper_bound"] + 1.0e-12
    assert bound["heat_trace_upper_bound_prefactor"] == descriptor["dimension"]
    assert bound["heat_trace_upper_bound_expression"].startswith("2*exp(")
    assert bound["explicit_matrix_inverse_formed"] is False


def test_log_bound_encloses_small_factorized_descriptor_trace() -> None:
    x = np.asarray([0.0, 0.02, 0.01])
    duration = np.asarray([0.2, 0.25])
    descriptor = assemble_finite_core_descriptor(
        log_radii=x,
        proper_durations=duration,
        channel="product_Dirac",
        unit_channel_value=1.5,
        chirality=1,
    )
    eigenvalues = eigh(
        _dense(descriptor["K_diagonal"], descriptor["K_off_diagonal"]),
        _dense(descriptor["M_diagonal"], descriptor["M_off_diagonal"]),
        eigvals_only=True,
    )
    actual_log = float(np.log(np.sum(np.exp(-eigenvalues))))
    bound = finite_core_heat_trace_log_upper_bound(
        dimension=descriptor["dimension"],
        proper_duration_upper=float(np.sum(duration)),
        factorization_coefficient_upper=1.5 * float(np.exp(-np.min(x))),
    )
    assert actual_log <= bound["log_heat_trace_upper_bound"] + 1.0e-12


def test_fixed_channel_certificate_is_scoped_and_valid() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["stored_fixed_channel_finite_core_increment"] == "CERTIFIED_SUPPRESSED"
    assert payload["claim_boundary"]["actual_joint_graded_heat_trace"] == "OPEN"
    assert payload["claim_boundary"]["maximal_tail_beyond_1222"] == "OPEN"
    assert payload["increment_1064_to_1222"]["three_channel_absolute_sum_exact_bound_expression"].startswith("3*(1064*exp(")
    assert payload["increment_1064_to_1222"]["three_channel_absolute_sum_log_upper"] < -1.0e50
